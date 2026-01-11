# MoneyViya n8n Agentic Workflows
## Hackathon Showcase Guide

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      n8n AGENTIC AUTOMATION                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  AI Agent    │    │  Scheduled   │    │   Event      │       │
│  │  Workflow    │    │  Automation  │    │   Triggers   │       │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘       │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              OPENAI GPT-4 INTEGRATION                 │       │
│  │  • Intent Recognition  • NLP Understanding           │       │
│  │  • Voice Transcription (Whisper)                     │       │
│  │  • Smart Response Generation                         │       │
│  └──────────────────────────────────────────────────────┘       │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────┐       │
│  │           MoneyViya BACKEND (FastAPI)               │       │
│  │  • Transaction Processing  • User Management          │       │
│  │  • Report Generation       • Goal Tracking            │       │
│  └──────────────────────────────────────────────────────┘       │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────┐       │
│  │              WHATSAPP DELIVERY                        │       │
│  │  Node.js Baileys Bot / Evolution API                  │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Available Workflows

### 1. **AI Agent Workflow** (`ai_agent_workflow.json`)
The main agentic workflow demonstrating AI capabilities.

**Features:**
- 🤖 GPT-4 powered intent recognition
- 🎤 Voice message transcription (Whisper)
- 🧠 Natural language understanding
- 💬 Multi-language support
- 📊 Smart financial categorization

**Flow:**
```
Webhook → Extract Data → Voice Check → AI Understanding → Backend → Response
```

### 2. **Daily Reminders** (`daily_reminders_flow.json`)
Automated morning and evening financial reminders.

**Schedule:** 
- Morning: 8:00 AM - Budget reminder
- Evening: 8:00 PM - Expense summary

### 3. **Weekly/Monthly Reports** (`weekly_monthly_reports.json`)
Automated report generation and delivery.

**Schedule:**
- Weekly: Every Sunday at 9:00 AM
- Monthly: 1st of every month

### 4. **Fraud Alert** (`fraud_alert_workflow.json`)
Real-time fraud detection and alerting.

**Triggers on:**
- Large transactions
- Unusual patterns
- New payees

### 5. **Bill Reminders** (`bill_reminder_workflow.json`)
Automated bill payment reminders.

---

## 🚀 Why n8n for This Project?

### Agentic Automation Benefits:

| Feature | Benefit |
|---------|---------|
| **Visual Workflow** | Easy to understand and modify |
| **AI Integration** | Direct OpenAI/GPT nodes |
| **No-Code** | Rapid prototyping |
| **Scalable** | Handle thousands of users |
| **Event-Driven** | Real-time processing |
| **Self-Hosted** | Data privacy control |

### Hackathon Showcase Points:

1. **🤖 AI Agent Capabilities**
   - GPT-4 for understanding user intent
   - Whisper for voice transcription
   - Multi-language NLP

2. **⚡ Real-time Processing**
   - Webhook-triggered workflows
   - Instant response generation

3. **📊 Automated Intelligence**
   - Scheduled financial reports
   - Smart spending alerts
   - Fraud detection

4. **🔗 Integration Power**
   - WhatsApp integration
   - Backend API calls
   - Database operations

---

## 📋 How to Import Workflows

### Step 1: Open n8n
Go to your n8n instance (local or cloud)

### Step 2: Import Workflow
1. Click **Workflows** → **Import from file**
2. Select the JSON file from `n8n/workflows/`
3. Click **Import**

### Step 3: Configure Credentials
1. Set up **OpenAI API** credentials
2. Set up **HTTP Request** authentication
3. Configure environment variables

### Step 4: Activate Workflow
Click **Active** toggle to enable the workflow

---

## 🔧 Environment Variables Required

```
OPENAI_API_KEY=sk-proj-xxxxx
MoneyViya_API_URL=https://MoneyViya-1.onrender.com
```

---

## 🎯 Hackathon Demo Script

### Demo Flow:

1. **Show Architecture Diagram**
   - Explain the agentic flow
   - Highlight AI components

2. **Import AI Agent Workflow**
   - Open n8n
   - Import `ai_agent_workflow.json`
   - Show the visual flow

3. **Demonstrate Voice Message Processing**
   - Show Whisper transcription node
   - Explain audio → text conversion

4. **Show GPT Integration**
   - Highlight intent recognition
   - Show JSON response parsing

5. **Trigger Live Demo**
   - Send WhatsApp message
   - Show real-time processing in n8n
   - Display response

6. **Show Scheduled Automation**
   - Open daily reminders workflow
   - Explain CRON scheduling
   - Show report generation

---

## 💡 Key Agentic Features to Highlight

### 1. Intent Recognition Agent
```javascript
// AI understands user intent automatically
{
  "intent": "EXPENSE_ENTRY",
  "amount": 500,
  "category": "food",
  "response": "₹500 expense on food recorded!"
}
```

### 2. Multi-Modal Processing
```
Text Message → GPT-4 → Intent → Backend
Voice Message → Whisper → Text → GPT-4 → Intent → Backend
Image (Bill) → OCR → Text → GPT-4 → Intent → Backend
```

### 3. Autonomous Scheduling
```
CRON Trigger → Fetch Users → Generate Reports → Send via WhatsApp
```

### 4. Event-Driven Reactions
```
Transaction Event → Fraud Check → Alert if Suspicious
```

---

## 📊 Workflow Complexity Matrix

| Workflow | Nodes | AI Nodes | Triggers | Complexity |
|----------|-------|----------|----------|------------|
| AI Agent | 10 | 2 (GPT, Whisper) | Webhook | High |
| Daily Reminders | 8 | 0 | CRON | Medium |
| Reports | 12 | 1 (GPT) | CRON | High |
| Fraud Alert | 6 | 1 (GPT) | Event | Medium |
| Bill Reminder | 5 | 0 | CRON | Low |

---

## 🏆 Hackathon Scoring Points

### Technical Excellence:
- ✅ AI/ML Integration (GPT-4, Whisper)
- ✅ Agentic Automation (n8n workflows)
- ✅ Real-time Processing
- ✅ Multi-language Support
- ✅ Voice Interface

### Innovation:
- ✅ Personal Financial AI Assistant
- ✅ WhatsApp-first approach
- ✅ Automated financial insights
- ✅ Fraud detection

### Scalability:
- ✅ Cloud-ready architecture
- ✅ Modular design
- ✅ Event-driven processing

---

## 🎬 Recording Demo Tips

1. **Screen Layout:**
   - n8n workflow editor (left)
   - WhatsApp Web (right)

2. **Show Real Execution:**
   - Send message
   - Watch n8n execution in real-time
   - See green checkmarks on nodes

3. **Highlight AI Processing:**
   - Zoom into GPT node
   - Show input/output data

4. **Timing:**
   - Keep demo under 5 minutes
   - Practice the flow beforehand

---

## 📞 Support

- n8n Docs: https://docs.n8n.io
- OpenAI API: https://platform.openai.com
- MoneyViya Backend: https://MoneyViya-1.onrender.com

---

**Good luck with your hackathon! 🚀**

