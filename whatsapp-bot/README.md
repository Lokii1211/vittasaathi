# VittaSaathi WhatsApp Bot (Node.js)

This is a simple WhatsApp bot using Baileys library that connects to the VittaSaathi Python backend.

## Features
- ✅ No Docker required
- ✅ Unlimited messages (FREE)
- ✅ QR code authentication (like WhatsApp Web)
- ✅ Forwards all messages to VittaSaathi backend
- ✅ Supports text, images, voice messages

## Quick Start

### 1. Install dependencies
```bash
cd whatsapp-bot
npm install
```

### 2. Start the bot
```bash
npm start
```

### 3. Scan QR Code
- A QR code will appear in the terminal
- Open WhatsApp on your phone
- Go to Settings → Linked Devices → Link a Device
- Scan the QR code

### 4. Done!
The bot will now forward all messages to VittaSaathi backend.

## Configuration

Edit `index.js` to change:
- `BACKEND_URL` - URL of VittaSaathi API (default: http://localhost:8000)

For production (Render), change to:
```javascript
BACKEND_URL: 'https://vittasaathi-1.onrender.com'
```

## Running with Python Backend

### Terminal 1: Start Python backend
```bash
cd c:\Users\dell\Desktop\vittasaathi
python -m uvicorn app:app --reload --port 8000
```

### Terminal 2: Start WhatsApp bot
```bash
cd c:\Users\dell\Desktop\vittasaathi\whatsapp-bot
npm start
```

## Session Storage

The bot stores WhatsApp session in the `auth_info` folder.
- Don't delete this folder or you'll need to re-scan QR code
- To logout, delete the `auth_info` folder

## Troubleshooting

**QR code not showing?**
- Session might already exist. Delete `auth_info` folder and restart.

**Messages not being processed?**
- Make sure Python backend is running
- Check the BACKEND_URL is correct

**Connection keeps dropping?**
- Your phone might be offline
- WhatsApp might have logged you out
