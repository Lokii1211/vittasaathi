/**
 * MoneyView WhatsApp Bot v3.1
 * ===========================
 * - Handles both @s.whatsapp.net and @lid formats
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
        bot: 'MoneyView WhatsApp Bot v3.1',
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

        // Format phone number
        let cleanPhone = phone.toString().replace(/[^0-9]/g, '');
        if (!cleanPhone.startsWith('91') && cleanPhone.length === 10) {
            cleanPhone = '91' + cleanPhone;
        }

        const jid = cleanPhone + '@s.whatsapp.net';

        await sock.sendMessage(jid, { text: message });
        console.log(`[n8n → WhatsApp] Sent to ${cleanPhone}`);

        res.json({ success: true, sent_to: cleanPhone });
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
 * Extract clean phone number from JID
 * Handles both @s.whatsapp.net and @lid formats
 */
function extractPhone(jid) {
    if (!jid) return null;

    // Remove @s.whatsapp.net or @lid suffix
    let phone = jid.replace(/@s\.whatsapp\.net$/, '').replace(/@lid$/, '');

    // Remove any non-digit characters
    phone = phone.replace(/[^0-9]/g, '');

    // If it's a LID (long ID), try to extract the actual phone
    // LIDs are internal WhatsApp IDs, we need to use the device's linked phone
    if (phone.length > 15) {
        console.log(`[Note] LID detected: ${jid}. Using stored phone if available.`);
        // For LIDs, we'll use the phone as-is for now
        // The actual phone should be extracted from the message context
    }

    // Ensure it starts with country code
    if (phone.length === 10) {
        phone = '91' + phone;
    }

    return phone;
}

/**
 * Process message through n8n or directly to Railway
 */
async function processMessage(phone, message, senderName) {
    try {
        console.log(`[Processing] ${phone}: "${message.substring(0, 50)}..."`);

        // Try n8n webhook first
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
            console.log(`[n8n] Not available (${n8nError.message}), using Railway...`);
        }

        // Fallback: Direct to MoneyView API
        try {
            const response = await axios.post(MONEYVIEW_ENDPOINT, {
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
        } catch (railwayError) {
            console.error(`[Railway Error]`, railwayError.message);
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
║     💰 MoneyView WhatsApp Bot v3.1                    ║
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
        browser: ['MoneyView', 'Chrome', '120.0.0'],
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
            console.log('📤 User → Baileys → n8n → MoneyView API → Reply');
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

            // Extract phone - handle both formats
            let phone = extractPhone(jid);

            // For LID format, try to get the actual sender's phone
            if (jid.endsWith('@lid')) {
                // Use participant if available (for business accounts)
                const participant = msg.key.participant;
                if (participant) {
                    phone = extractPhone(participant);
                } else {
                    // Try to use the pushName as fallback context
                    console.log(`[LID] Using extracted phone: ${phone} for ${senderName}`);
                }
            }

            console.log(`\n[User → Bot] ${senderName} (${jid}): ${messageContent}`);
            console.log(`[Phone] Extracted: ${phone}`);

            // Process message
            const reply = await processMessage(phone, messageContent, senderName);

            // Send reply
            if (reply) {
                await sendMessage(jid, reply);
            }
        }
    });
}

// Start
console.log('\n🚀 Starting MoneyView WhatsApp Bot...\n');
startBot().catch(err => console.error('Startup error:', err));
