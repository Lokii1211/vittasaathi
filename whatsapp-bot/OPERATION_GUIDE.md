# MoneyViya WhatsApp Bot - Complete Operation Guide

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR PHONE                            │
│               (WhatsApp Linked Device)                   │
└───────────────────────┬─────────────────────────────────┘
                        │ WhatsApp Web Protocol
                        ▼
┌─────────────────────────────────────────────────────────┐
│              NODE.JS WHATSAPP BOT                        │
│            (whatsapp-bot/index.js)                       │
│                                                          │
│  • Receives all WhatsApp messages                        │
│  • Uses Baileys library (WhatsApp Web)                   │
│  • Runs on your LOCAL computer                           │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP POST /api/message
                        ▼
┌─────────────────────────────────────────────────────────┐
│              MoneyViya BACKEND                         │
│           (Hosted on Render.com)                         │
│                                                          │
│  • AI-powered message understanding                      │
│  • Financial tracking & analytics                        │
│  • PDF report generation                                 │
│  • User management & onboarding                          │
└─────────────────────────────────────────────────────────┘
```

## 🚀 How to Start the Bot

### Prerequisites
- Node.js installed (v18+)
- WhatsApp account on your phone
- Internet connection

### Step 1: Open PowerShell
Press `Win + R`, type `powershell`, press Enter

### Step 2: Navigate to bot folder
```powershell
cd C:\Users\dell\Desktop\MoneyViya\whatsapp-bot
```

### Step 3: Start the bot
```powershell
npm start
```

### Step 4: Scan QR Code (First time only)
1. A QR code will appear in the terminal
2. Open WhatsApp on your phone
3. Go to **Settings** → **Linked Devices** → **Link a Device**
4. Scan the QR code

### Step 5: Done! 🎉
You'll see:
```
✅ CONNECTED TO WHATSAPP SUCCESSFULLY!
📞 Bot is ready to receive messages
🔗 Backend: https://MoneyViya-1.onrender.com
```

## 🔄 How to Restart the Bot

### If bot is running:
1. Press `Ctrl + C` to stop
2. Run `npm start` again

### If bot won't connect:
1. Stop the bot (`Ctrl + C`)
2. Delete session: 
   ```powershell
   Remove-Item -Recurse -Force auth_info
   ```
3. Start again: `npm start`
4. Scan QR code again

## 📱 Keeping Bot Running 24/7

### Option 1: Keep PowerShell Open
Just don't close the PowerShell window. Bot stays running.

### Option 2: Use PM2 (Process Manager)
```powershell
# Install PM2
npm install -g pm2

# Start bot with PM2
cd C:\Users\dell\Desktop\MoneyViya\whatsapp-bot
pm2 start index.js --name MoneyViya-bot

# View logs
pm2 logs MoneyViya-bot

# Stop bot
pm2 stop MoneyViya-bot

# Restart bot
pm2 restart MoneyViya-bot
```

## 🔧 Troubleshooting

### ❌ "Connection closed. Reconnecting: true" loop
- Your phone might be offline
- WhatsApp Web might be disconnected
- **Fix:** Delete `auth_info` folder and restart

### ❌ "Error processing your request"
- Backend (Render) might be sleeping
- **Fix:** Wait 30-60 seconds, try again

### ❌ QR code not showing
- Session already exists
- **Fix:** Delete `auth_info` folder and restart

### ❌ Messages not being sent
- Check if backend URL is correct in index.js
- Make sure Render deployment is complete

## 📝 Bot Features

### Onboarding (New Users)
- Language selection (English, Hindi, Tamil, etc.)
- Name collection
- Profession detection
- Income input (supports 25k, 25000, 2 lakh formats)
- Financial goal setting

### Financial Tracking
- "spent 100 on food" → Records expense
- "earned 5000" → Records income
- "balance" → Shows financial summary
- "report" → Generates summary

### AI Understanding
- Natural language processing
- Multi-language support
- Voice message transcription (with OpenAI)

## 🔐 Environment Variables

The bot uses these environment variables (optional):
```
BACKEND_URL=https://MoneyViya-1.onrender.com
```

To set custom backend:
```powershell
$env:BACKEND_URL = "http://localhost:8000"
npm start
```

## 📊 Dashboard Access

Web dashboard: https://MoneyViya-1.onrender.com/dashboard

## 🗂️ File Structure

```
whatsapp-bot/
├── index.js          # Main bot code
├── package.json      # Dependencies
├── auth_info/        # WhatsApp session (auto-created)
│   └── creds.json    # Login credentials
└── README.md         # This guide
```

## ⚠️ Important Notes

1. **Don't share auth_info folder** - Contains your WhatsApp session
2. **Keep phone connected** - Bot uses WhatsApp Web, phone must be online
3. **One account per bot** - Can't run multiple bots on same WhatsApp
4. **Don't spam** - WhatsApp may ban accounts that send too many messages

## 🆚 Comparison: This vs Twilio

| Feature | Twilio | This Bot |
|---------|--------|----------|
| Cost | $0.005/msg | FREE |
| Limit | 50/day (sandbox) | UNLIMITED |
| Setup | Easy | Medium |
| Reliability | Very High | Good |
| Works Offline | Yes | No (phone needed) |

## 📞 Support

- Check logs in terminal for errors
- Reset by deleting auth_info folder
- Restart bot if not responding

