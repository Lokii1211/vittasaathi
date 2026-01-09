/**
 * VittaSaathi WhatsApp Bot v2
 * Uses Baileys library for WhatsApp Web integration
 * Fixed QR code display
 */

const { default: makeWASocket, DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const pino = require('pino');
const axios = require('axios');
const qrcode = require('qrcode-terminal');
const fs = require('fs');

// Configuration
const CONFIG = {
    BACKEND_URL: process.env.BACKEND_URL || 'https://vittasaathi-1.onrender.com',
    AUTH_FOLDER: './auth_info'
};

// Simple logger
const logger = pino({ level: 'warn' });

let reconnectAttempts = 0;
const MAX_RECONNECT = 5;

/**
 * Send message to VittaSaathi backend
 */
async function processMessage(phone, message) {
    try {
        console.log(`📤 Processing: ${message.substring(0, 50)}...`);

        const response = await axios.post(
            `${CONFIG.BACKEND_URL}/api/message`,
            new URLSearchParams({
                From: `whatsapp:+${phone}`,
                Body: message
            }),
            {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                timeout: 60000
            }
        );

        if (response.data?.reply) {
            return response.data.reply;
        }
        return null;
    } catch (error) {
        console.error('❌ Backend error:', error.message);
        return '❌ Error processing your request. Please try again.';
    }
}

/**
 * Start WhatsApp Bot
 */
async function startBot() {
    console.log('\n🚀 Starting VittaSaathi WhatsApp Bot...\n');

    // Clear old auth if too many reconnects
    if (reconnectAttempts >= MAX_RECONNECT) {
        console.log('🔄 Too many reconnects. Clearing session...');
        if (fs.existsSync(CONFIG.AUTH_FOLDER)) {
            fs.rmSync(CONFIG.AUTH_FOLDER, { recursive: true });
        }
        reconnectAttempts = 0;
    }

    // Create auth folder
    if (!fs.existsSync(CONFIG.AUTH_FOLDER)) {
        fs.mkdirSync(CONFIG.AUTH_FOLDER, { recursive: true });
    }

    // Get latest version
    const { version } = await fetchLatestBaileysVersion();
    console.log(`📱 Using Baileys version: ${version.join('.')}\n`);

    // Load auth state
    const { state, saveCreds } = await useMultiFileAuthState(CONFIG.AUTH_FOLDER);

    // Create socket
    const sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: true,  // Enable built-in QR printing
        logger: logger,
        browser: ['VittaSaathi Bot', 'Chrome', '120.0.0'],
        connectTimeoutMs: 60000,
        defaultQueryTimeoutMs: 60000,
        keepAliveIntervalMs: 25000,
        emitOwnEvents: false,
        markOnlineOnConnect: true
    });

    // Connection updates
    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        // Show QR code (backup method)
        if (qr) {
            console.log('\n' + '='.repeat(50));
            console.log('📱 SCAN THIS QR CODE WITH WHATSAPP:');
            console.log('='.repeat(50) + '\n');
            qrcode.generate(qr, { small: true });
            console.log('\n' + '='.repeat(50));
            console.log('Go to WhatsApp → Settings → Linked Devices → Link');
            console.log('='.repeat(50) + '\n');
        }

        if (connection === 'close') {
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut;

            console.log(`🔌 Disconnected. Code: ${statusCode}. Reconnecting: ${shouldReconnect}`);

            if (shouldReconnect && reconnectAttempts < MAX_RECONNECT) {
                reconnectAttempts++;
                console.log(`⏳ Reconnect attempt ${reconnectAttempts}/${MAX_RECONNECT}...`);
                setTimeout(startBot, 3000);
            } else if (statusCode === DisconnectReason.loggedOut) {
                console.log('\n❌ Logged out from WhatsApp.');
                console.log('Delete the auth_info folder and restart.\n');
                process.exit(0);
            }
        }
        else if (connection === 'open') {
            reconnectAttempts = 0;
            console.log('\n' + '='.repeat(50));
            console.log('✅ CONNECTED TO WHATSAPP SUCCESSFULLY!');
            console.log('='.repeat(50));
            console.log(`📞 Bot is ready to receive messages`);
            console.log(`🔗 Backend: ${CONFIG.BACKEND_URL}`);
            console.log('='.repeat(50) + '\n');
        }
    });

    // Save credentials
    sock.ev.on('creds.update', saveCreds);

    // Handle messages
    sock.ev.on('messages.upsert', async ({ messages, type }) => {
        if (type !== 'notify') return;

        for (const message of messages) {
            try {
                // Skip own messages and broadcasts
                if (message.key.fromMe) continue;
                if (message.key.remoteJid === 'status@broadcast') continue;

                const jid = message.key.remoteJid;
                const phone = jid.split('@')[0].split(':')[0];

                // Extract message text
                let text = '';
                const msg = message.message;

                if (!msg) continue;

                if (msg.conversation) {
                    text = msg.conversation;
                } else if (msg.extendedTextMessage?.text) {
                    text = msg.extendedTextMessage.text;
                } else if (msg.imageMessage?.caption) {
                    text = msg.imageMessage.caption || '[Image]';
                } else if (msg.audioMessage) {
                    text = '[Voice message]';
                }

                if (!text) continue;

                console.log(`\n📩 From +${phone}: ${text.substring(0, 100)}`);

                // Process and reply
                const reply = await processMessage(phone, text);

                if (reply) {
                    await sock.sendMessage(jid, { text: reply });
                    console.log(`📤 Replied: ${reply.substring(0, 50)}...`);
                }

            } catch (err) {
                console.error('Message error:', err.message);
            }
        }
    });
}

// Main
console.log('╔══════════════════════════════════════════════════╗');
console.log('║      VittaSaathi WhatsApp Bot v2.0               ║');
console.log('║      Personal Financial Advisor                  ║');
console.log('╚══════════════════════════════════════════════════╝');

startBot().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
});
