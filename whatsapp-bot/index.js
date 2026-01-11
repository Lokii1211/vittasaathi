/**
 * VittaSaathi WhatsApp Bot v3.0
 * Fixed session handling and QR code display
 */

const { default: makeWASocket, DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const pino = require('pino');
const axios = require('axios');
const qrcode = require('qrcode-terminal');
const fs = require('fs');

// Configuration
const CONFIG = {
    BACKEND_URL: process.env.BACKEND_URL || 'https://moneyviya.up.railway.app',
    AUTH_FOLDER: './auth_info'
};

const logger = pino({ level: 'silent' });

let sock = null;
let reconnectAttempts = 0;
const MAX_RECONNECT = 3;

/**
 * Send message to MoneyViya backend
 */
async function processMessage(phone, message) {
    try {
        console.log(`📤 Processing: ${message.substring(0, 50)}...`);

        // Use the dedicated Baileys webhook
        const response = await axios.post(
            `${CONFIG.BACKEND_URL}/webhook/baileys`,
            {
                phone: `+${phone}`,
                message: message
            },
            {
                headers: { 'Content-Type': 'application/json' },
                timeout: 60000
            }
        );

        if (response.data?.reply) {
            return response.data.reply;
        }
        return null;
    } catch (error) {
        console.error('❌ Backend error:', error.message);
        // Fallback: don't reply if backend fails
        return null;
    }
}

/**
 * Start WhatsApp Bot
 */
async function startBot() {
    console.log('\n🚀 Starting VittaSaathi WhatsApp Bot...\n');

    // Create auth folder
    if (!fs.existsSync(CONFIG.AUTH_FOLDER)) {
        fs.mkdirSync(CONFIG.AUTH_FOLDER, { recursive: true });
    }

    // Get latest version
    const { version } = await fetchLatestBaileysVersion();
    console.log(`📱 Using Baileys version: ${version.join('.')}\n`);

    // Load auth state
    const { state, saveCreds } = await useMultiFileAuthState(CONFIG.AUTH_FOLDER);

    // Create socket - FIXED: removed deprecated option
    sock = makeWASocket({
        version,
        auth: state,
        logger: logger,
        browser: ['VittaSaathi', 'Chrome', '120.0.0'],
        connectTimeoutMs: 60000,
        defaultQueryTimeoutMs: 60000,
        keepAliveIntervalMs: 30000,
        markOnlineOnConnect: false,
        syncFullHistory: false
    });

    // Connection updates
    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        // Show QR code
        if (qr) {
            console.log('\n' + '='.repeat(50));
            console.log('📱 SCAN THIS QR CODE WITH WHATSAPP:');
            console.log('='.repeat(50) + '\n');
            qrcode.generate(qr, { small: true });
            console.log('\n' + '='.repeat(50));
            console.log('WhatsApp → Settings → Linked Devices → Link');
            console.log('='.repeat(50) + '\n');
        }

        if (connection === 'close') {
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            const shouldReconnect = statusCode !== DisconnectReason.loggedOut &&
                statusCode !== 440; // Don't reconnect on conflict

            console.log(`🔌 Disconnected. Code: ${statusCode}`);

            if (statusCode === 440) {
                console.log('\n⚠️ Session conflict detected!');
                console.log('Clearing session and restarting...\n');
                // Clear auth and restart
                if (fs.existsSync(CONFIG.AUTH_FOLDER)) {
                    fs.rmSync(CONFIG.AUTH_FOLDER, { recursive: true });
                }
                reconnectAttempts = 0;
                setTimeout(startBot, 3000);
            } else if (statusCode === DisconnectReason.loggedOut) {
                console.log('\n❌ Logged out. Scan QR code again.\n');
                if (fs.existsSync(CONFIG.AUTH_FOLDER)) {
                    fs.rmSync(CONFIG.AUTH_FOLDER, { recursive: true });
                }
                setTimeout(startBot, 2000);
            } else if (shouldReconnect && reconnectAttempts < MAX_RECONNECT) {
                reconnectAttempts++;
                console.log(`⏳ Reconnecting... (${reconnectAttempts}/${MAX_RECONNECT})`);
                setTimeout(startBot, 5000);
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
                if (message.key.fromMe) continue;
                if (message.key.remoteJid === 'status@broadcast') continue;

                const jid = message.key.remoteJid;
                const phone = jid.split('@')[0].split(':')[0];

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

                const reply = await processMessage(phone, text);

                if (reply && sock) {
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
console.log('║      VittaSaathi WhatsApp Bot v3.0               ║');
console.log('║      Personal Financial Advisor                  ║');
console.log('╚══════════════════════════════════════════════════╝');

startBot().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
});

// Handle process termination
process.on('SIGINT', () => {
    console.log('\n👋 Shutting down bot...');
    process.exit(0);
});
