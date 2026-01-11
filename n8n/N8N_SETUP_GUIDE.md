# 🔄 MoneyViya n8n Setup - Simple Import Guide

> **All workflows are ready to import! Just follow these steps.**

---

## ⚡ Quick Setup (5 Minutes)

### Step 1: Add Twilio Credentials in n8n

1. Open n8n: **http://localhost:5678**
2. Click **Settings** (⚙️ gear icon) → **Credentials**
3. Click **+ Add Credential** → Search "**Twilio**"
4. Enter your credentials:
   ```
   Credential Name: Twilio account
   Account SID: [Your Account SID from Twilio Console]
   Auth Token: [Your Auth Token from Twilio Console]
   ```
5. Click **Save**

---

### Step 2: Import Workflows (One by One)

For each workflow file, do these steps:

1. In n8n, click **Workflows** (left sidebar)
2. Click **+ Add Workflow** button
3. Click the **⋮** (three dots) menu → **Import from File**
4. Navigate to: `c:\Users\dell\Desktop\MoneyViya\n8n\workflows\`
5. Select the workflow file
6. Click **Save** → **Activate** (toggle switch)

---

## 📁 Workflows to Import

| # | File | Purpose | Schedule |
|---|------|---------|----------|
| 1 | `whatsapp_main_workflow.json` | Main WhatsApp handler | Always on |
| 2 | `daily_summary_workflow.json` | Morning summary | 8 AM daily |
| 3 | `bill_reminder_workflow.json` | Bill reminders | 9 AM daily |
| 4 | `fraud_alert_workflow.json` | Fraud detection | Webhook triggered |
| 5 | `monthly_report_workflow.json` | Monthly reports | 1st of month |

---

### Step 3: Get Your Webhook URL

After importing the main workflow:

1. Click on the **"WhatsApp Webhook"** node
2. Copy the **Webhook URL** shown
3. It will look like: `http://localhost:5678/webhook/whatsapp-incoming`

---

### Step 4: Connect Twilio to n8n

**For local testing, use ngrok:**

```bash
# Download ngrok from: https://ngrok.com/download
# Then run:
ngrok http 5678
```

This gives you a public URL like: `https://abc123.ngrok.io`

**In Twilio Console:**
1. Go to: https://console.twilio.com
2. Navigate to: Messaging → Try it out → WhatsApp Sandbox
3. Set **"When a message comes in"** to:
   ```
   https://abc123.ngrok.io/webhook/whatsapp-incoming
   ```
4. Method: **POST**
5. Save

---

## ✅ Verification Checklist

- [ ] Twilio credentials added in n8n
- [ ] All 5 workflows imported
- [ ] All workflows activated (toggle is ON)
- [ ] ngrok running (`ngrok http 5678`)
- [ ] Twilio webhook configured with ngrok URL
- [ ] MoneyViya API running (`python -m uvicorn app:app --port 8000`)

---

## 🧪 Test It!

1. Send a WhatsApp message to: **+1 415 523 8886**
   (First join sandbox: send "join <sandbox-word>" as shown in Twilio)

2. Send: **Hi**

3. You should receive the language selection menu!

---

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| MoneyViya API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Admin Panel | http://localhost:8000/static/admin.html |
| Dashboard | http://localhost:8000/static/dashboard.html |
| n8n | http://localhost:5678 |

---

## 🔧 If Something Goes Wrong

### "Credential not found" error
→ Make sure to name your Twilio credential exactly: `Twilio account`

### "Cannot connect to localhost:8000"
→ Make sure MoneyViya is running:
```bash
cd c:\Users\dell\Desktop\MoneyViya
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### Twilio not receiving messages
→ Make sure you've joined the WhatsApp sandbox first

### Workflow not triggering
→ Make sure the workflow is ACTIVATED (toggle should be green/ON)

---

**Ready to go! 🎉 Just import and activate!**

