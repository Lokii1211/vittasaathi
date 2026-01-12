/**
 * MoneyViya WhatsApp Bot v3.0
 * - Sends all messages to n8n webhook for processing
 * - n8n handles: onboarding, expenses, income, reports, etc.
 * - Provides HTTP API for n8n to send scheduled messages
 */

const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const pino = require('pino');
const axios = require('axios');
const express = require('express');

// Configuration - IMPORTANT: Update these!
const N8N_WEBHOOK_URL = process.env.N8N_WEBHOOK_URL || 'http://localhost:5678/webhook/whatsapp-message';
const HTTP_PORT = process.env.BOT_PORT || 3001;

// Fallback to Railway if n8n not available
const RAILWAY_API_URL = process.env.RAILWAY_API_URL || 'https://moneyviya.up.railway.app';
const RAILWAY_ENDPOINT = `${RAILWAY_API_URL}/api/v2/whatsapp/process`;

// Store for connection
let sock;
let isConnected = false;

// Express app for n8n to send messages
const app = express();
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        connected: isConnected,
        bot: 'MoneyViya WhatsApp Bot v3.0',
        n8n_webhook: N8N_WEBHOOK_URL
    });
});

// Send message endpoint (called by n8n scheduled messages)
app.post('/send', async (req, res) => {
    try {
        const { phone, message } = req.body;

        if (!phone || !message) {
            return res.status(400).json({ error: 'Phone and message required' });
        }

        if (!isConnected || !sock) {
            return res.status(503).json({ error: 'Bot not connected' });
        }

        // Format phone number
        let cleanPhone = phone.toString().replace(/[^0-9]/g, '');
        if (!cleanPhone.startsWith('91') && cleanPhone.length === 10) {
            cleanPhone = '91' + cleanPhone;
        }

        const jid = cleanPhone + '@s.whatsapp.net';

        await sock.sendMessage(jid, { text: message });
        console.log(`[n8n] Sent message to ${cleanPhone}`);

        res.json({ success: true, sent_to: cleanPhone });
    } catch (error) {
        console.error('[n8n] Error sending:', error.message);
        res.status(500).json({ error: error.message });
    }
});

// Start HTTP server
app.listen(HTTP_PORT, () => {
    console.log(`\n📡 HTTP API running on port ${HTTP_PORT}`);
    console.log(`   POST http://localhost:${HTTP_PORT}/send`);
});

async function processMessage(phone, message, senderName) {
    try {
        console.log(`[Processing] ${phone} -> "${message.substring(0, 50)}..."`);

        // Try n8n first
        try {
            const response = await axios.post(N8N_WEBHOOK_URL, {
                phone: phone,
                message: message,
                sender_name: senderName
            }, {
                headers: { 'Content-Type': 'application/json' },
                timeout: 30000
            });

            if (response.data && response.data.reply) {
                console.log(`[n8n] Got reply`);
                return response.data.reply;
            }
        } catch (n8nError) {
            console.log(`[n8n] Not available, trying Railway...`);
        }

        // Fallback to Railway
        const response = await axios.post(RAILWAY_ENDPOINT, {
            phone: phone,
            message: message,
            sender_name: senderName
        }, {
            headers: { 'Content-Type': 'application/json' },
            timeout: 30000
        });

        if (response.data && response.data.reply) {
            console.log(`[Railway] Got reply`);
            return response.data.reply;
        }

        return null;
    } catch (error) {
        console.error(`[Error]`, error.message);
        return "⚠️ Sorry, I'm having trouble. Please try again.";
    }
}

async function sendMessage(jid, text) {
    try {
        await sock.sendMessage(jid, { text: text });
        console.log(`[Sent] to ${jid}`);
    } catch (error) {
        console.error(`[Send Error]`, error.message);
    }
}

async function startBot() {
    const { state, saveCreds } = await useMultiFileAuthState('./auth_info');
    const { version } = await fetchLatestBaileysVersion();

    console.log(`
╔═══════════════════════════════════════════════════╗
║     💰 MoneyViya WhatsApp Bot v3.0                ║
║     n8n Workflow Integration                       ║
╠═══════════════════════════════════════════════════╣
║  n8n: ${N8N_WEBHOOK_URL.substring(0, 45).padEnd(45)}║
║  Fallback: Railway API                             ║
╚═══════════════════════════════════════════════════╝
    `);

    sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: false,
        logger: pino({ level: 'silent' }),
        browser: ['MoneyViya', 'Chrome', '120.0.0'],
    });

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            console.log('\n📱 Scan this QR code with WhatsApp:\n');
            qrcode.generate(qr, { small: true });
        }

        if (connection === 'close') {
            isConnected = false;
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('[Connection] Closed. Reconnecting:', shouldReconnect);

            if (shouldReconnect) {
                setTimeout(startBot, 5000);
            }
        } else if (connection === 'open') {
            isConnected = true;
            console.log('\n✅ Connected to WhatsApp!\n');
            console.log('🔄 Messages go to: n8n → Railway API');
            console.log('📤 n8n sends scheduled messages via: localhost:' + HTTP_PORT);
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
        }
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        if (type !== 'notify') return;

        for (const msg of messages) {
            if (!msg.message || msg.key.fromMe) continue;
            if (msg.key.remoteJid === 'status@broadcast') continue;

            const messageContent = msg.message.conversation
                || msg.message.extendedTextMessage?.text
                || msg.message.imageMessage?.caption
                || msg.message.videoMessage?.caption
                || '';

            if (!messageContent) continue;

            const jid = msg.key.remoteJid;
            const phone = jid.replace('@s.whatsapp.net', '');
            const senderName = msg.pushName || 'Friend';

            console.log(`\n[Received] ${senderName} (${phone}): ${messageContent}`);

            const reply = await processMessage(phone, messageContent, senderName);

            if (reply) {
                await sendMessage(jid, reply);
            }
        }
    });
}

console.log('Starting MoneyViya WhatsApp Bot v3.0...\n');
startBot().catch(err => console.error('Startup error:', err));
