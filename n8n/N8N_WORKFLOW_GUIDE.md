# MoneyView - n8n Workflow Guide

## Overview

MoneyView uses n8n to automate:
- Message processing from WhatsApp
- Scheduled morning briefings (6 AM)
- Market analysis (9 AM)
- Evening check-ins (8 PM)
- Weekly reports (Sunday)
- Monthly reports (1st of month)

## Workflow File

📁 `n8n/workflows/moneyview_complete_workflow.json`

## Setup Steps

### 1. Import Workflow
1. Open n8n dashboard
2. Go to **Workflows** → **Import from File**
3. Select `moneyview_complete_workflow.json`
4. Click **Import**

### 2. Get Webhook URL
After import, click on "Receive WhatsApp Message" node.
Copy the webhook URL (e.g., `http://localhost:5678/webhook/moneyview-webhook`)

### 3. Update Baileys Bot
Edit `whatsapp-bot/index.js`:
```javascript
const N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/moneyview-webhook';
```

### 4. Start Services

**Start Baileys Bot:**
```bash
cd whatsapp-bot
npm install
npm start
```

**Ensure Railway is deployed with MoneyView API**

### 5. Activate Workflow
Toggle the workflow to **Active** in n8n.

## Workflow Flow

```
┌─────────────────────────────────────────────────────┐
│                  MESSAGE FLOW                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  User WhatsApp → Baileys Bot → n8n Webhook         │
│                        ↓                            │
│            Process via Railway API                  │
│                        ↓                            │
│               Prepare Reply                         │
│                        ↓                            │
│           Send back to Baileys → User              │
│                                                     │
├─────────────────────────────────────────────────────┤
│                SCHEDULED MESSAGES                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  6 AM  → Morning Briefing                          │
│  9 AM  → Market Analysis                           │
│  8 PM  → Evening Check-in                          │
│  Sunday → Weekly Report                            │
│  1st   → Monthly Report                            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## API Endpoints Used

| Endpoint | Description |
|----------|-------------|
| `POST /api/moneyview/process` | Process WhatsApp message |
| `GET /api/moneyview/morning-briefing` | Get morning messages |
| `GET /api/moneyview/market-analysis` | Get market updates |
| `GET /api/moneyview/evening-checkin` | Get evening messages |
| `POST /api/moneyview/weekly-reports` | Generate weekly reports |
| `POST /api/moneyview/monthly-reports` | Generate monthly reports |

## Troubleshooting

**Messages not processing?**
- Check n8n workflow is active
- Verify webhook URL in Baileys bot
- Check Railway API is running

**Scheduled messages not sending?**
- Verify n8n is running 24/7
- Check Baileys bot is connected
- Verify `localhost:3001` is accessible

---

*MoneyView - Your Personal Finance Partner* 💰
