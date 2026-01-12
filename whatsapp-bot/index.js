/**
 * MoneyViya WhatsApp Bot v3.2
 * ===========================
 * - Uses JID/LID directly as user ID (no phone extraction needed)
 * - Sends all messages to n8n for processing
 * - Fallback to Railway API
 * - HTTP endpoint for n8n scheduled messages
 */

const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const pino = require('pino');
const axios = require('axios');
const express = require('express');

// Configuration
const N8N_WEBHOOK_URL = process.env.N8N_WEBHOOK_URL || 'http://localhost:5678/webhook/moneyview-webhook';
const RAILWAY_API_URL = process.env.RAILWAY_API_URL || 'https://moneyviya.up.railway.app';
const MONEYVIEW_ENDPOINT = `${RAILWAY_API_URL}/api/moneyview/process`;
const HTTP_PORT = process.env.BOT_PORT || 3001;

// Connection state
let sock;
let isConnected = false;

// Express app for n8n to send messages
const app = express();
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        connected: isConnected,
        bot: 'MoneyViya WhatsApp Bot v3.2',
        n8n_webhook: N8N_WEBHOOK_URL,
        railway_api: RAILWAY_API_URL
    });
});

// Send message endpoint (called by n8n)
app.post('/send', async (req, res) => {
    try {
        const { phone, message } = req.body;

        if (!phone || !message) {
            return res.status(400).json({ error: 'Phone and message required' });
        }

        if (!isConnected || !sock) {
            return res.status(503).json({ error: 'Bot not connected to WhatsApp' });
        }

        // Format JID - handle both phone numbers and LIDs
        let jid;
        if (phone.includes('@')) {
            jid = phone; // Already a JID
        } else {
            // It's a phone number, format it
            let cleanPhone = phone.toString().replace(/[^0-9]/g, '');
            if (!cleanPhone.startsWith('91') && cleanPhone.length === 10) {
                cleanPhone = '91' + cleanPhone;
            }
            jid = cleanPhone + '@s.whatsapp.net';
        }

        await sock.sendMessage(jid, { text: message });
        console.log(`[n8n → WhatsApp] Sent to ${jid}`);

        res.json({ success: true, sent_to: jid });
    } catch (error) {
        console.error('[Send Error]', error.message);
        res.status(500).json({ error: error.message });
    }
});

// Start HTTP server
app.listen(HTTP_PORT, () => {
    console.log(`\n📡 HTTP API: http://localhost:${HTTP_PORT}`);
    console.log(`   POST /send - Send message to user`);
    console.log(`   GET /health - Check bot status`);
});

/**
 * Get user ID from JID
 * For LID format, we use the LID directly
 * For phone format, we extract the phone number
 */
function getUserId(jid) {
    if (!jid) return null;

    // Remove suffix to get the core ID
    const userId = jid.replace(/@s\.whatsapp\.net$/, '').replace(/@lid$/, '');
    return userId;
}

/**
 * Process message through n8n or directly to Railway
 */
async function processMessage(userId, message, senderName, originalJid) {
    try {
        console.log(`[Processing] ${userId}: "${message.substring(0, 50)}..."`);

        // Try n8n webhook first
        try {
            const response = await axios.post(N8N_WEBHOOK_URL, {
                phone: userId,
                message: message,
                sender_name: senderName,
                jid: originalJid
            }, {
                headers: { 'Content-Type': 'application/json' },
                timeout: 30000
            });

            if (response.data && response.data.reply) {
                console.log(`[n8n] Got reply`);
                return response.data.reply;
            }
        } catch (n8nError) {
            console.log(`[n8n] Not available (${n8nError.message}), trying Railway...`);
        }

        // Fallback: Direct to MoneyViya API
        try {
            const response = await axios.post(MONEYVIEW_ENDPOINT, {
                phone: userId,
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
        } catch (railwayError) {
            console.error(`[Railway Error]`, railwayError.response?.status, railwayError.message);

            // Return a helpful error message
            if (railwayError.response?.status === 404) {
                return "⚠️ Sorry, there's a connection issue. The team is fixing it. Please try again soon!";
            }
        }

        return null;
    } catch (error) {
        console.error(`[Process Error]`, error.message);
        return "⚠️ Sorry, I'm having trouble. Please try again in a moment.";
    }
}

/**
 * Send WhatsApp message
 */
async function sendMessage(jid, text) {
    try {
        await sock.sendMessage(jid, { text: text });
        console.log(`[WhatsApp → User] Sent to ${jid}`);
    } catch (error) {
        console.error(`[Send Error]`, error.message);
    }
}

/**
 * Start WhatsApp bot
 */
async function startBot() {
    const { state, saveCreds } = await useMultiFileAuthState('./auth_info');
    const { version } = await fetchLatestBaileysVersion();

    console.log(`
╔═══════════════════════════════════════════════════════╗
║     💰 MoneyViya WhatsApp Bot v3.2                    ║
║     Personal Financial Manager & Advisor              ║
╠═══════════════════════════════════════════════════════╣
║  n8n:     ${N8N_WEBHOOK_URL.substring(0, 43).padEnd(43)}║
║  Railway: ${RAILWAY_API_URL.substring(0, 43).padEnd(43)}║
╚═══════════════════════════════════════════════════════╝
    `);

    sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: false,
        logger: pino({ level: 'silent' }),
        browser: ['MoneyViya', 'Chrome', '120.0.0'],
    });

    // Connection events
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
            console.log('📤 User → Baileys → n8n → MoneyViya API → Reply');
            console.log('📥 n8n Scheduled → Baileys → User');
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
        }
    });

    // Save credentials
    sock.ev.on('creds.update', saveCreds);

    // Handle incoming messages
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        if (type !== 'notify') return;

        for (const msg of messages) {
            // Skip self and broadcast
            if (!msg.message || msg.key.fromMe) continue;
            if (msg.key.remoteJid === 'status@broadcast') continue;

            // Skip group messages
            if (msg.key.remoteJid.endsWith('@g.us')) continue;

            // Extract message text
            const messageContent = msg.message.conversation
                || msg.message.extendedTextMessage?.text
                || msg.message.imageMessage?.caption
                || msg.message.videoMessage?.caption
                || '';

            if (!messageContent) continue;

            // Get sender info
            const jid = msg.key.remoteJid;
            const senderName = msg.pushName || 'Friend';

            // Get user ID (either phone number or LID)
            const userId = getUserId(jid);

            console.log(`\n[User → Bot] ${senderName} (${jid}): ${messageContent}`);

            // Process message
            const reply = await processMessage(userId, messageContent, senderName, jid);

            // Send reply
            if (reply) {
                await sendMessage(jid, reply);
            }
        }
    });
}

// Start
console.log('\n🚀 Starting MoneyViya WhatsApp Bot...\n');
startBot().catch(err => console.error('Startup error:', err));
