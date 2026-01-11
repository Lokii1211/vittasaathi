# 💰 MoneyViya - Your Financial Friend on WhatsApp

> **India's First WhatsApp Financial Advisor for EVERYONE with Irregular Income**
> 
> 👩‍🎓 Students | 👩‍🍳 Homemakers | 🛵 Delivery Partners | 📞 BPO Workers | 🛒 Shopkeepers | 👷 Daily Wage Workers | 👴 Pensioners

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![API Routes](https://img.shields.io/badge/API%20routes-130+-orange)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 🎯 Who Is This For?

MoneyViya is built for **everyone managing money on uncertain income**:

| User Type | How MoneyViya Helps |
|-----------|----------------------|
| 👩‍🎓 **Students** | Track pocket money, part-time earnings, hostel expenses |
| 👩‍🍳 **Homemakers** | Manage household budget, track grocery expenses, save for goals |
| 🧵 **Earning Homemakers** | Track tiffin/tailoring/tuition income, separate business from household |
| 🛵 **Delivery Partners** | Daily earnings tracking, petrol expense management, incentive tracking |
| 🚗 **Cab/Auto Drivers** | Ride earnings, fuel costs, vehicle maintenance fund |
| 📞 **BPO Workers** | Variable pay tracking, night shift allowance savings |
| 🛒 **Small Vendors** | Business income, stock purchase tracking, profit calculation |
| 👷 **Daily Wage Workers** | Work day tracking, save on earning days, avoid debt traps |
| 👴 **Pensioners** | Fixed income management, medical fund, safe investment advice |
| 💼 **Freelancers** | Project-based income, client payments, tax planning |

---

## ✨ Features That Make Us Stand Out

### 💬 Natural WhatsApp Conversation
```
You: "आज 500 कमाए"
Bot: ✅ ₹500 आमदनी दर्ज!
     📊 आज की कुल आय: ₹1,200
     🔥 7 दिन का स्ट्रीक!

You: "petrol pe 100 kharch"
Bot: ✅ ₹100 खर्च दर्ज!
     ⛽ श्रेणी: पेट्रोल
     📊 इस महीने बचा: ₹4,500
```

### 📊 Beautiful Interactive Dashboard
Access at: `http://localhost:8000/static/dashboard.html?phone=YOUR_PHONE`
- Donut charts for expense breakdown
- Gauge meters for financial health
- Progress rings for goals
- Mini calendar with income/expense indicators
- Real-time data refresh

### 🔊 Voice Replies in Your Language
- Every response comes with text + voice
- Supports **Hindi, Tamil, Telugu, Kannada, Malayalam, Marathi, Gujarati, Bengali, Punjabi**
- Perfect for users who prefer listening

### 🎮 Gamification & Rewards
- **Levels**: Beginner → Learner → Saver → Tracker → Planner → Pro → Expert → Master
- **Achievements**: Unlock badges for savings milestones, streaks, goals
- **Points**: Earn points for every good financial behavior

### 🏆 Savings Challenges
- **52 Week Challenge** - Save ₹10 in week 1, ₹20 in week 2... = ₹13,780 total!
- **No Spend Day** - One expense-free day per week
- **Round-Up Savings** - Auto-save spare change
- **Digital Coin Jar** - Save all small amounts

### 👨‍👩‍👧‍👦 Family Finance Management
- Add and manage family members
- Track shared expenses
- Split bills easily
- Family budget tracking
- Settlement reports

### 📚 Financial Education
- Daily learning tips in simple language
- Government schemes you're eligible for
- Scam alerts to keep you safe
- Investment basics explained simply

### 🛡️ Fraud Protection
- Real-time transaction monitoring
- Behavioral pattern analysis
- WhatsApp + Voice call alerts for suspicious activity
- One-tap YES/NO confirmation

### 📅 Smart Financial Calendar
- Predict income/expense patterns
- Bill due date tracking
- Festival expense planning
- Recurring payment detection

### 💾 Enterprise-Grade Backup System
- **Local Backups**: Full system and user-specific
- **Encrypted Backups**: AES-256 encryption with password protection
- **Cloud Backups**: AWS S3 and Google Cloud Storage support
- **Scheduled Backups**: Daily, weekly, or monthly auto-backups
- **Backup Notifications**: WhatsApp and Email alerts

### 🔐 Two-Factor Authentication
- TOTP-based authentication
- QR code for authenticator apps
- Backup codes for recovery
- Session management

### 📤 Data Export
- CSV exports (transactions, summaries)
- Excel exports with multiple sheets
- PDF monthly/yearly reports

---

## 🚀 Quick Start

### 1. Installation
```bash
cd MoneyViya
pip install -r requirements.txt
```

### 2. Start API Server
```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### 3. Access Dashboard
Open: http://localhost:8000/static/dashboard.html?phone=YOUR_PHONE

### 4. API Documentation
Open: http://localhost:8000/docs

### 5. Import n8n Workflows
See `n8n/N8N_SETUP_GUIDE.md` for detailed instructions.

---

## 🔌 API Overview (130+ Routes)

| Category | Routes | Description |
|----------|--------|-------------|
| **Core** | 20+ | Users, transactions, goals, budgets |
| **Analytics** | 10 | Trends, predictions, breakdowns |
| **Reports** | 5 | PDF generation |
| **Export** | 6 | CSV, Excel |
| **Smart Features** | 4 | Auto-categorization, quick actions |
| **Family Finance** | 8 | Groups, splits, shared budgets |
| **Challenges** | 5 | Savings challenges |
| **Bills** | 4 | Reminders, tracking |
| **Education** | 5 | Tips, schemes, lessons |
| **Calendar** | 5 | Events, predictions |
| **Charts** | 3 | Visual analytics |
| **Backup** | 10 | Local backup/restore |
| **Encrypted Backup** | 5 | Secure backups |
| **Cloud Backup** | 8 | AWS S3, GCS |
| **Scheduled Backup** | 5 | Auto-backup |
| **Notifications** | 6 | WhatsApp, Email |
| **2FA** | 14 | Two-factor auth |

---

## 📱 Supported Languages

| Language | Status | Example |
|----------|--------|---------|
| 🇬🇧 English | ✅ Full | "I earned 500 today" |
| 🇮🇳 Hindi | ✅ Full | "आज 500 कमाए" |
| 🇮🇳 Tamil | ✅ Full | "இன்று 500 சம்பாதித்தேன்" |
| 🇮🇳 Telugu | ✅ Full | "ఈరోజు 500 సంపాదించాను" |
| 🇮🇳 Kannada | 🟡 Basic | Coming soon |
| 🇮🇳 Malayalam | 🟡 Basic | Coming soon |
| 🇮🇳 Marathi | 🟡 Basic | Coming soon |
| 🇮🇳 Bengali | 🟡 Basic | Coming soon |

---

## 💡 Key Features Comparison

| Feature | MoneyViya | Other Apps |
|---------|-------------|------------|
| **WhatsApp Native** | ✅ No app download | ❌ Separate app |
| **Irregular Income Focus** | ✅ Built for variable earnings | ❌ Assumes fixed salary |
| **Multi-Language** | ✅ 10+ Indian languages | ❌ English only |
| **Voice Replies** | ✅ Every response | ❌ None |
| **Gamification** | ✅ Levels, badges, challenges | ❌ Basic or none |
| **Fraud Protection** | ✅ AI + Voice calls | ❌ Basic alerts |
| **Financial Education** | ✅ Daily tips, schemes | ❌ Limited |
| **Cloud Backup** | ✅ AWS S3, GCS | ❌ None |
| **2FA Security** | ✅ TOTP + Backup codes | ❌ Basic |
| **Free to Use** | ✅ Completely free | ❌ Subscription |

---

## 🏗️ Project Structure

```
MoneyViya/
├── app.py                        # Main FastAPI (v3.0, 130+ routes)
├── extended_api.py               # Extended API endpoints
├── config.py                     # 16 user types, all categories
├── scheduler.py                  # Background reminders
│
├── database/                     # Persistent JSON storage
│   ├── user_repository.py        # User management
│   ├── transaction_repository.py # All transactions
│   ├── goal_repository.py        # Financial goals
│   ├── budget_repository.py      # Monthly budgets
│   └── reminder_repository.py    # Bill reminders
│
├── services/                     # Core services
│   ├── nlp_service.py            # Multi-language NLP
│   ├── financial_advisor.py      # AI advice engine
│   ├── dashboard_service.py      # Monthly dashboards
│   ├── analytics_service.py      # Advanced analytics
│   ├── engagement_service.py     # Challenges & streaks
│   ├── education_service.py      # Financial literacy
│   ├── family_service.py         # Family finance
│   ├── voice_service.py          # TTS in local languages
│   ├── notification_service.py   # WhatsApp + Email
│   ├── export_service.py         # CSV/Excel exports
│   ├── pdf_service.py            # PDF reports
│   ├── calendar_service.py       # Financial calendar
│   ├── backup_service.py         # Local backup/restore
│   ├── secure_backup_service.py  # Encrypted backups
│   ├── cloud_backup_service.py   # AWS S3 / GCS
│   ├── tfa_service.py            # Two-factor auth
│   └── personality_service.py    # Friendly AI personality
│
├── agents/                       # Fraud detection
│   └── advanced_fraud_agent.py   # Behavioral analysis
│
├── static/                       # Web assets
│   └── dashboard.html            # Interactive dashboard
│
└── n8n/                          # n8n workflows
    ├── N8N_SETUP_GUIDE.md       
    └── workflows/
        ├── whatsapp_main_workflow.json
        ├── daily_reminders_workflow.json
        ├── weekly_dashboard_workflow.json
        ├── monthly_dashboard_workflow.json
        └── fraud_alert_workflow.json
```

---

## 🔒 Security Features

| Feature | Details |
|---------|---------|
| **Encryption** | AES-256 (Fernet) for backups |
| **Key Derivation** | PBKDF2-HMAC-SHA256 (480,000 iterations) |
| **2FA** | TOTP with 30-second codes |
| **Backup Codes** | 8 emergency codes per user |
| **Session Management** | Configurable expiry |
| **Integrity Check** | SHA-256 hash verification |

---

## 🎯 Government Schemes Integrated

We help users discover and apply for:

| Scheme | Benefit | For Whom |
|--------|---------|----------|
| PM Jan Dhan | Zero balance account + ₹2L insurance | Everyone |
| PM Suraksha Bima | ₹2L accident cover @ ₹20/year | Everyone |
| PM Jeevan Jyoti | ₹2L life insurance @ ₹436/year | Everyone |
| Ayushman Bharat | ₹5L free health coverage | Low income |
| PM Mudra | Business loan up to ₹10L | Small vendors |
| Sukanya Samriddhi | 8%+ for girl child | Parents |
| Atal Pension | ₹1000-5000/month pension | Gig workers |

---

## 🚨 Scam Alerts

MoneyViya actively warns about:
- 📱 Instant loan app traps (100-300% hidden interest)
- 📞 OTP/KYC phone scams
- 🔗 Fake KYC update links
- 💼 Work from home job scams
- 💰 Double money Ponzi schemes
- 🎰 Lottery/lucky draw fraud

---

## 📦 Dependencies

### Core
- FastAPI, Uvicorn, Pandas, NumPy

### Communication
- Twilio (WhatsApp), gTTS (Voice)

### Documents
- Pytesseract (OCR), Pillow, PyPDF2, ReportLab

### Security
- Cryptography (AES), PyOTP (2FA), QRCode

### Cloud (Optional)
- boto3 (AWS S3), google-cloud-storage (GCS)

### Scheduling
- APScheduler

---

## 📞 Support

For issues or feature requests, please create an issue on GitHub.

---

**Made with ❤️ for India's hardworking people**

*"हर रुपया मायने रखता है | ஒவ்வொரு ரூபாயும் முக்கியம் | ప్రతి రూపాయి ముఖ్యం"*

