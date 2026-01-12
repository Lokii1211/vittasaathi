/**
 * VittaSaathi WhatsApp Bot v2.0
 * Forwards all messages to Railway API for processing
 */

const { default: makeWASocket, useMultiFileAuthState, DisconnectReason, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const qrcode = require('qrcode-terminal');
const pino = require('pino');
const axios = require('axios');

// Configuration
const RAILWAY_API_URL = process.env.RAILWAY_API_URL || 'https://moneyviya.up.railway.app';
const API_ENDPOINT = `${RAILWAY_API_URL}/api/v2/whatsapp/process`;

// Logger
const logger = pino({ level: 'info' });

// Store for connection
let sock;

async function processMessageViaAPI(phone, message, senderName) {
    try {
        console.log(`[API] Sending to Railway: ${phone} -> "${message.substring(0, 50)}..."`);

        const response = await axios.post(API_ENDPOINT, {
            phone: phone,
            message: message,
            sender_name: senderName
        }, {
            headers: { 'Content-Type': 'application/json' },
            timeout: 30000 // 30 second timeout
        });

        if (response.data && response.data.reply) {
            console.log(`[API] Got reply from Railway`);
            return response.data.reply;
        } else {
            console.log(`[API] No reply in response:`, response.data);
            return null;
        }
    } catch (error) {
        console.error(`[API] Error calling Railway:`, error.message);

        // Fallback error message
        return "⚠️ Sorry, I'm having trouble connecting to the server. Please try again in a moment.";
    }
}

async function sendMessage(jid, text) {
    try {
        await sock.sendMessage(jid, { text: text });
        console.log(`[Send] Message sent to ${jid}`);
    } catch (error) {
        console.error(`[Send] Error sending message:`, error.message);
    }
}

async function startBot() {
    const { state, saveCreds } = await useMultiFileAuthState('./auth_info');
    const { version } = await fetchLatestBaileysVersion();

    console.log(`
╔════════════════════════════════════════════════╗
║     VittaSaathi WhatsApp Bot v2.0              ║
║     Railway API Integration                     ║
╠════════════════════════════════════════════════╣
║  API: ${RAILWAY_API_URL.substring(0, 40).padEnd(40)}║
╚════════════════════════════════════════════════╝
    `);

    sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: false,
        logger: pino({ level: 'silent' }),
        browser: ['VittaSaathi', 'Chrome', '120.0.0'],
    });

    // Handle connection events
    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            console.log('\n📱 Scan this QR code with WhatsApp:\n');
            qrcode.generate(qr, { small: true });
        }

        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            console.log('[Connection] Closed. Reconnecting:', shouldReconnect);

            if (shouldReconnect) {
                setTimeout(startBot, 5000);
            }
        } else if (connection === 'open') {
            console.log('\n✅ Connected to WhatsApp!\n');
            console.log('📡 All messages will be forwarded to Railway API');
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');
        }
    });

    // Save credentials when updated
    sock.ev.on('creds.update', saveCreds);

    // Handle incoming messages
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        if (type !== 'notify') return;

        for (const msg of messages) {
            // Skip if no message content or from self
            if (!msg.message || msg.key.fromMe) continue;

            // Skip status broadcasts
            if (msg.key.remoteJid === 'status@broadcast') continue;

            // Extract message text
            const messageContent = msg.message.conversation
                || msg.message.extendedTextMessage?.text
                || msg.message.imageMessage?.caption
                || msg.message.videoMessage?.caption
                || '';

            if (!messageContent) continue;

            // Extract sender info
            const jid = msg.key.remoteJid;
            const phone = jid.replace('@s.whatsapp.net', '');
            const senderName = msg.pushName || 'Friend';

            console.log(`\n[Received] ${senderName} (${phone}): ${messageContent}`);

            // Process via Railway API
            const reply = await processMessageViaAPI(phone, messageContent, senderName);

            if (reply) {
                await sendMessage(jid, reply);
            }
        }
    });
}

// Start the bot
console.log('Starting VittaSaathi WhatsApp Bot...\n');
startBot().catch(err => console.error('Startup error:', err));
