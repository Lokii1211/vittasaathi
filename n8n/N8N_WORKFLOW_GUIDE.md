# MoneyViya n8n Workflow Guide (Baileys Bot)

## 📋 Overview

The `moneyviya_baileys_workflow.json` provides n8n automation for MoneyViya using your local Baileys WhatsApp bot.

### Features:
- ☀️ **Morning Reminders** (6 AM) - Daily motivation & budget info
- 🌙 **Evening Summaries** (8 PM) - Today's income/expense summary
- 📊 **Weekly Reports** (Sunday 10 AM) - Full week financial report
- 🔔 **Hourly Reminders** - Bill due date alerts

All messages are in the user's selected language (EN, HI, TA, TE).

---

## 🔧 Architecture

```
┌─────────────┐      ┌─────────────┐      ┌───────────────┐
│    n8n      │─────▶│ Baileys Bot │─────▶│   WhatsApp    │
│  (Scheduler)│      │  (Local)    │      │   (User)      │
└─────────────┘      └─────────────┘      └───────────────┘
      │                    ▲
      │                    │
      ▼                    │
┌─────────────┐            │
│  Railway    │────────────┘
│  API        │  (Get user data)
└─────────────┘
```

---

## 🚀 Setup Steps

### Step 1: Update Baileys Bot

In `whatsapp-bot/`, run:
```bash
npm install
```

This installs Express for the HTTP API.

### Step 2: Start Baileys Bot

```bash
cd whatsapp-bot
npm start
```

The bot now runs:
- **WhatsApp Connection** on Baileys protocol
- **HTTP API** on port 3001 for n8n

### Step 3: Import n8n Workflow

1. Open n8n (http://localhost:5678)
2. Import → File → `moneyviya_baileys_workflow.json`
3. Activate the workflow

### Step 4: Configure n8n Endpoints

Update the HTTP Request nodes if needed:
- **Railway API**: `https://moneyviya.up.railway.app`
- **Baileys API**: `http://localhost:3001` (or your bot's IP)

---

## 📡 Baileys Bot HTTP API

Your local bot exposes these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check bot status |
| `/send` | POST | Send a WhatsApp message |

### Send Message Example:
```bash
curl -X POST http://localhost:3001/send \
  -H "Content-Type: application/json" \
  -d '{"phone": "919003360494", "message": "Hello from n8n!"}'
```

---

## ⏰ Scheduled Messages

### Morning (6 AM IST)
```
☀️ *Good Morning, {name}!*

📊 Today's Plan:
💰 Daily Budget: ₹{budget}
🎯 Savings Target: ₹{target}

💪 Today is going to be a great day!
```

### Evening (8 PM IST)
```
🌙 *{name}, Today's Summary*

💵 Income: ₹{income}
💸 Expenses: ₹{expenses}
💰 Net: ₹{savings}

👏 Great job! You saved money!
```

### Weekly (Sunday 10 AM)
```
📊 *{name} Weekly Report*

💵 Total Income: ₹X,XXX
💸 Total Expenses: ₹X,XXX
💰 Net Savings: ₹X,XXX

🎉 Great week! Keep it up!
```

---

## 🌍 Multilingual

Messages automatically use the user's language:

| Language | Code |
|----------|------|
| English | `en` |
| Hindi | `hi` |
| Tamil | `ta` |
| Telugu | `te` |

---

## 🔒 Security Notes

1. The Baileys bot runs **locally** on your machine
2. n8n should be on the **same network** as the bot
3. Or expose via **ngrok/tunnel** if n8n is cloud-hosted

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot not connected | Check if Baileys bot is running |
| n8n can't reach bot | Verify IP/port is correct |
| Messages not sending | Check Railway API is up at `/health` |
| Wrong language | User may need to select language again (send `reset`) |

---

## 📞 Local Development

To test manually:

```bash
# Check bot health
curl http://localhost:3001/health

# Send test message
curl -X POST http://localhost:3001/send \
  -H "Content-Type: application/json" \
  -d '{"phone": "919003360494", "message": "Test from n8n! 🎉"}'
```

---

*MoneyViya - Your AI Financial Advisor* 💰
