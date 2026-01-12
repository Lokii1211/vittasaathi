# VittaSaathi n8n Workflow Guide

## 📋 Complete Workflow Overview

The `vittasaathi_complete_workflow.json` provides a comprehensive n8n workflow that handles:

1. **WhatsApp Message Processing**
2. **Morning Reminders (6 AM)**
3. **Evening Summaries (8 PM)**
4. **Weekly Reports (Sunday 10 AM)**
5. **Custom Reminders**

---

## 🔧 Prerequisites

### 1. Environment Variables in n8n

Set these in n8n Credentials/Settings:

```
WHATSAPP_ACCESS_TOKEN=your_meta_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
```

### 2. Railway API Endpoints

Your Railway server needs these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/whatsapp/process` | POST | Process incoming messages |
| `/api/v2/users/active` | GET | Get all active users |
| `/api/v2/reminders/pending` | GET | Get pending reminders |
| `/api/v2/reports/weekly/generate` | POST | Generate weekly reports |

---

## 📊 Workflow Components

### 1. WhatsApp Webhook Handler
- **Trigger**: Incoming WhatsApp messages
- **Flow**: 
  ```
  Webhook → Extract Data → Process with AI → Send Reply → Respond OK
  ```

### 2. Morning Motivation (6 AM IST)
- **Trigger**: Cron `0 6 * * *`
- **Flow**:
  ```
  6 AM Trigger → Get Users → Generate Message (by language) → Send
  ```
- **Multilingual**: Messages in EN, HI, TA, TE

### 3. Evening Summary (8 PM IST)
- **Trigger**: Cron `0 20 * * *`
- **Flow**:
  ```
  8 PM Trigger → Get Users → Calculate Today's Data → Send Summary
  ```

### 4. Weekly Report (Sunday 10 AM)
- **Trigger**: Cron `0 10 * * 0`
- **Flow**:
  ```
  Sunday 10 AM → Generate Reports → Loop Users → Send Reports
  ```

### 5. Hourly Reminder Check
- **Trigger**: Every hour
- **Flow**:
  ```
  Hourly Trigger → Get Pending Reminders → Send Each
  ```

---

## 🚀 How to Import

### Step 1: Open n8n
Go to your n8n instance (e.g., `http://localhost:5678`)

### Step 2: Import Workflow
1. Click "Workflows" → "Import from File"
2. Select `vittasaathi_complete_workflow.json`
3. Click "Import"

### Step 3: Configure Credentials
1. Click on each HTTP Request node
2. Update URLs if your Railway URL is different
3. Add WhatsApp API credentials

### Step 4: Set Webhook URL
Copy the webhook URL from n8n and set it in Meta WhatsApp Business:
```
https://your-n8n-instance.com/webhook/whatsapp-webhook
```

### Step 5: Activate Workflow
Toggle the workflow to "Active"

---

## 🌍 Multilingual Support

The workflow automatically sends messages in the user's preferred language:

| Language | Code | Example Morning Message |
|----------|------|------------------------|
| English | `en` | "Good Morning, John!" |
| Hindi | `hi` | "सुप्रभात, राज!" |
| Tamil | `ta` | "காலை வணக்கம், குமார்!" |
| Telugu | `te` | "శుభోదయం, రాజు!" |

---

## ⏰ Timezone Note

The cron times are in **IST (Indian Standard Time)**. n8n will run based on your server timezone.

For IST:
- 6 AM IST = `0 6 * * *`
- 8 PM IST = `0 20 * * *`
- Sunday 10 AM IST = `0 10 * * 0`

---

## 📱 Testing

### Test Webhook Manually
```bash
curl -X POST https://your-n8n.com/webhook/whatsapp-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "919003360494",
            "text": {"body": "Hello"}
          }],
          "contacts": [{
            "profile": {"name": "Test User"}
          }]
        }
      }]
    }]
  }'
```

### Test Manual Execution
1. Open the workflow
2. Click "Execute Workflow"
3. Check each node's output

---

## 🔒 Security

1. **Never expose credentials** in the workflow JSON
2. **Use n8n Credentials** for storing API tokens
3. **Enable authentication** on your n8n instance

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Webhook not receiving | Check Meta webhook URL configuration |
| Messages not sending | Verify WhatsApp API token is valid |
| Wrong timezone | Update cron expressions for your TZ |
| SSL errors | Ensure your n8n has valid HTTPS |

---

## 📞 Support

For issues, check:
1. n8n execution logs
2. Railway server logs at `/health`
3. WhatsApp Business API status

---

*VittaSaathi - Your AI Financial Advisor* 🎯💰
