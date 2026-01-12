# MoneyViya 💰

**Your Personal AI Financial Manager & Advisor**

MoneyViya is an AI-powered WhatsApp bot that helps you manage your finances, track expenses, achieve goals, and grow wealth.

---

## ✨ Features

### 💬 Natural Conversation
- No menus or numbered options
- Just chat naturally: "Spent 500 on food", "Earned 10000"
- Available in English, Hindi, Tamil, Telugu, Kannada

### 📊 Complete Financial Tracking
- Track income and expenses with categories
- Daily budget management
- Real-time balance summaries

### 🎯 Multi-Goal Management
- Add unlimited financial goals
- Track progress with percentages
- Get motivated to achieve targets

### 📈 Stock Market Analysis
- Daily market updates at 9 AM
- NIFTY, SENSEX, Bank Nifty
- Personalized investment recommendations

### ⏰ Smart Reminders
- **6 AM**: Morning briefing with yesterday's summary
- **9 AM**: Market analysis and investment tips
- **8 PM**: Evening check-in to close the day
- **Sunday**: Weekly report with % comparisons
- **1st of Month**: Monthly detailed report

### 🌐 Live Dashboard
- Web-based dashboard synced with WhatsApp
- View transactions, goals, reports
- Real-time updates

---

## 🚀 Quick Start

### 1. Start Baileys Bot
```bash
cd whatsapp-bot
npm install
npm start
```
Scan QR code with WhatsApp.

### 2. Import n8n Workflow
Import `n8n/workflows/MoneyViya_complete_workflow.json`

### 3. Deploy API (Railway)
```bash
git push
```
Railway auto-deploys the MoneyViya API.

### 4. Start Chatting!
Send "Hi" to the WhatsApp bot.

---

## 📁 Project Structure

```
MoneyViya/
├── agents/
│   └── MoneyViya_agent.py    # AI Financial Agent
├── services/
│   └── stock_market_service.py # Market Analysis
├── MoneyViya_api.py          # API Endpoints
├── app.py                     # FastAPI Main
├── n8n/
│   └── workflows/
│       └── MoneyViya_complete_workflow.json
├── whatsapp-bot/
│   ├── index.js              # Baileys Bot
│   └── package.json
├── static/
│   └── index.html            # Web Dashboard
└── requirements.txt
```

---

## 💬 Example Conversation

```
User: Hi
MoneyViya: 👋 Welcome to MoneyViya!
           Which language do you prefer?
           (Just type: English, Hindi, Tamil...)

User: English
MoneyViya: Perfect! What's your name?

User: Lokesh
MoneyViya: Nice to meet you, Lokesh! What do you do?

User: I'm a freelancer
MoneyViya: Great! What's your monthly income?

... [Complete onboarding] ...

User: Spent 500 on lunch
MoneyViya: ✅ Expense Logged!
           💸 ₹500 on Food
           💰 Budget Left: ₹833
           
User: Balance
MoneyViya: 📊 Lokesh's Summary
           💵 Income: ₹0
           💸 Spent: ₹500
           💰 Remaining: ₹833
```

---

## 🔧 Configuration

### Environment Variables
```
OPENAI_API_KEY=sk-xxx          # For AI responses
ALPHA_VANTAGE_API_KEY=xxx      # For market data
```

### Baileys Bot
```javascript
// whatsapp-bot/index.js
const N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/MoneyViya-webhook';
const RAILWAY_API_URL = 'https://your-app.up.railway.app';
```

---

## 📞 Support

Built with ❤️ for the n8n AI Agents Hackathon 2025

---

*MoneyViya - Your Personal Finance Partner* 💰
