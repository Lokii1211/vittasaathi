# MoneyViya n8n AI Agent Workflows
## Complete Guide - What, Why, and How

---

## 📋 Overview

n8n is a **workflow automation platform** that acts as the "brain" connecting all parts of MoneyViya. It's like having a smart assistant that:
- Receives messages
- Understands what user wants (using AI)
- Routes to appropriate handler
- Sends back responses

---

## 🤖 AI Agent Workflow (`ai_agent_workflow.json`)

### What is it?
The **main intelligent workflow** that processes all WhatsApp messages using AI to understand user intent.

### Purpose:
- Receive incoming WhatsApp messages
- Use GPT-4 to understand what the user wants
- Process the request (expense, income, report, etc.)
- Return smart, contextual responses

### How it works:

```
[WhatsApp Message]
       ↓
[1. Webhook Trigger] ← Receives incoming message
       ↓
[2. Extract Data] ← Parses phone, message, type
       ↓
[3. Check Voice?] ← Is it a voice message?
       ↓         ↘
[4a. Whisper]    [4b. Skip]
(Transcribe)      (Text)
       ↓         ↓
[5. GPT-4 AI Understanding] ← Understands intent
       ↓
[6. Parse AI Response] ← Extract intent, amount, category
       ↓
[7. Call Backend API] ← Process with MoneyViya
       ↓
[8. Prepare Reply] ← Format response
       ↓
[9. Send Response] ← Return to user
```

### Key AI Nodes:

#### Node: "AI Understand Intent (GPT)"
```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "system",
      "content": "You are MoneyViya, analyze user message and extract: intent, amount, category, response"
    },
    {
      "role": "user", 
      "content": "{{ user's message }}"
    }
  ]
}
```

**Output:**
```json
{
  "intent": "EXPENSE_ENTRY",
  "amount": 500,
  "category": "food",
  "response": "₹500 expense on food recorded!"
}
```

### How to Import and Use:

1. **Open n8n** (locally or n8n.cloud)

2. **Import Workflow:**
   - Click `Workflows` → `Import from file`
   - Select `n8n/workflows/ai_agent_workflow.json`
   - Click `Import`

3. **Configure Credentials:**
   - Click on "AI Understand Intent (GPT)" node
   - Add OpenAI API credential:
     - Name: `OpenAI`
     - API Key: `sk-proj-xxxxx`

4. **Set Environment Variables:**
   - Go to `Settings` → `Environment Variables`
   - Add: `OPENAI_API_KEY=sk-proj-xxxxx`

5. **Activate:**
   - Click the `Active` toggle (top right)
   - Workflow is now live!

6. **Get Webhook URL:**
   - Click on "Webhook Trigger" node
   - Copy the "Production URL"
   - Example: `https://your-n8n.app/webhook/MoneyViya-agent`

7. **Connect to WhatsApp Bot:**
   - Update `whatsapp-bot/index.js`:
   ```javascript
   const CONFIG = {
     BACKEND_URL: 'https://your-n8n.app/webhook',
     // ...
   };
   ```

---

## 📅 Daily Reminders Workflow (`daily_reminders_flow.json`)

### What is it?
Automated scheduled workflow that sends **morning and evening financial reminders**.

### Purpose:
- Morning (8 AM): "Good morning! Your budget for today is ₹X"
- Evening (8 PM): "Today you spent ₹Y. Great job saving!"

### How it works:
```
[CRON Trigger: 8 AM]
       ↓
[Get All Active Users] ← From database
       ↓
[For Each User]
       ↓
[Calculate Daily Budget] ← Based on monthly budget
       ↓
[Generate Message] ← Personalized greeting
       ↓
[Send WhatsApp] ← Via API
```

### CRON Schedule:
- Morning: `0 8 * * *` (8:00 AM daily)
- Evening: `0 20 * * *` (8:00 PM daily)

---

## 📊 Weekly/Monthly Reports (`weekly_monthly_reports.json`)

### What is it?
Automated workflow that generates and sends **financial reports** on schedule.

### Purpose:
- Weekly (Sunday 9 AM): Summary of week's income/expense
- Monthly (1st of month): Full month dashboard with charts

### How it works:
```
[CRON Trigger: Sunday 9 AM]
       ↓
[Get Users Who Want Reports]
       ↓
[For Each User]
       ↓
[Fetch Transactions (7 days)]
       ↓
[Calculate Totals]
       ↓
[Generate PDF Report] ← Call /reports/{phone}/pdf/weekly
       ↓
[Send Report via WhatsApp]
```

---

## 🚨 Fraud Alert Workflow (`fraud_alert_workflow.json`)

### What is it?
Real-time **fraud detection** workflow that alerts users of suspicious activity.

### Purpose:
- Detect unusual spending patterns
- Alert user immediately
- Log suspicious transactions

### Triggers:
- Large transaction (> 10x average)
- Multiple transactions in short time
- New/unknown payee
- Unusual time/location

### How it works:
```
[Transaction Event]
       ↓
[Check Amount vs Average]
       ↓
[Check Transaction Frequency]
       ↓
[Is Suspicious?]
       ↓
 Yes → [Send Alert] → "⚠️ Large expense detected: ₹50,000"
 No  → [Log & Continue]
```

---

## 💡 Bill Reminder Workflow (`bill_reminder_workflow.json`)

### What is it?
Workflow that sends **bill payment reminders** before due dates.

### Purpose:
- Remind users about upcoming bills
- Prevent late fees
- Track recurring payments

---

## 🎯 For Your Hackathon

### Demo Script:

1. **Show the n8n Interface**
   - "This is our agentic automation platform"
   - "Each box is a step in our AI pipeline"

2. **Highlight AI Nodes**
   - "Here's where GPT-4 understands user intent"
   - "It extracts amount, category, and generates response"

3. **Show Voice Processing**
   - "Voice messages go through Whisper for transcription"
   - "Then the text is analyzed by GPT"

4. **Live Demo**
   - Send a WhatsApp message
   - Show real-time execution in n8n
   - Watch the green checkmarks flow through nodes

5. **Emphasize Agentic Features**
   - "The agent decides what to do based on user message"
   - "It's autonomous - no human intervention needed"
   - "Handles expenses, income, reports, advice - all automatically"

### Judges Will Be Impressed By:
- ✅ Visual workflow (easy to understand)
- ✅ AI integration (GPT-4, Whisper)
- ✅ Real-time processing
- ✅ Multi-modal (text + voice)
- ✅ Scheduled automation
- ✅ Fraud detection
- ✅ Scalable architecture

---

## 🔧 Quick Setup Commands

```bash
# Install n8n locally
npm install -g n8n

# Start n8n
n8n start

# Access at http://localhost:5678
```

### Or use n8n Cloud:
1. Go to https://n8n.cloud
2. Sign up for free trial
3. Import workflows
4. Configure credentials
5. Activate!

---

## 📞 Architecture Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER (WhatsApp)                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               NODE.JS BAILEYS BOT (Local/VPS)                   │
│                   Forwards messages to n8n                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      n8n WORKFLOWS                              │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐       │
│  │  AI Agent     │  │   Reminders   │  │    Reports    │       │
│  │  (GPT-4)      │  │   (CRON)      │  │   (CRON)      │       │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘       │
│          │                  │                  │                │
│          └──────────────────┼──────────────────┘                │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   OpenAI API                             │   │
│  │        GPT-4 (Understanding) + Whisper (Voice)           │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  MoneyViya BACKEND (Render)                   │
│              Transaction Processing, Reports, etc.              │
└─────────────────────────────────────────────────────────────────┘
```

---

**Good luck with your hackathon! 🚀**

