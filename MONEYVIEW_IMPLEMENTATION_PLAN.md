# MoneyView - Personal Financial Manager & Advisor Agent
## Complete System Architecture & Implementation Plan

---

## 🎯 Vision Statement

**MoneyView** is an AI-powered Personal Finance Agent accessible via WhatsApp that acts as a financial advisor, manager, and motivator. It helps users manage money, achieve goals, understand investments, and build wealth through personalized guidance in their preferred language.

---

## 📊 Problem Statement

Most people lack financial literacy and discipline:
- They forget their financial goals within days
- No structured approach to saving and investing
- Don't track daily expenses
- Miss investment opportunities
- No personalized financial advice accessible 24/7

**Solution**: MoneyView - A WhatsApp-based AI agent that:
- Remembers and tracks all financial goals
- Sends timely reminders and motivation
- Provides personalized financial advice
- Analyzes stock markets daily
- Manages budgets automatically
- Speaks user's language

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         MoneyView Architecture                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────────┐│
│  │   WhatsApp   │────▶│ Baileys Bot  │────▶│      n8n Workflow        ││
│  │    User      │◀────│  (Local)     │◀────│   (Process Engine)       ││
│  └──────────────┘     └──────────────┘     └───────────┬──────────────┘│
│                                                        │                │
│                                                        ▼                │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                     FastAPI Backend (Railway)                        ││
│  ├─────────────────────────────────────────────────────────────────────┤│
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ ││
│  │  │ MoneyView   │  │   Stock     │  │  Document   │  │   Report    │ ││
│  │  │   Agent     │  │  Analysis   │  │   Scanner   │  │  Generator  │ ││
│  │  │  (OpenAI)   │  │ (AlphaVant) │  │ (OCR/Vision)│  │   (PDF)     │ ││
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ ││
│  │                                                                      ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ ││
│  │  │   Goal      │  │   Budget    │  │  Investment │  │  Reminder   │ ││
│  │  │  Manager    │  │   Planner   │  │   Advisor   │  │   Service   │ ││
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                      PostgreSQL Database                             ││
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        ││
│  │  │  Users  │ │  Goals  │ │ Transac │ │ Markets │ │ Reports │        ││
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘        ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────────┤
│  │                    Web Dashboard (View Only)                         │
│  │  • Live Transaction Dashboard  • Goal Progress  • Investment Charts  │
│  └──────────────────────────────────────────────────────────────────────┘
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📱 Feature Breakdown

### 1. Onboarding Flow (Comprehensive)
```
Step 1:  Language Selection (EN/HI/TA/TE/KN)
Step 2:  Name
Step 3:  Occupation (Student/Employee/Business/Freelancer/Homemaker)
Step 4:  Monthly Income (approximate)
Step 5:  Monthly Fixed Expenses (rent, EMI, bills)
Step 6:  Monthly Variable Expenses (food, transport, shopping)
Step 7:  Current Savings (in bank)
Step 8:  Current Investments (FD, MF, Stocks, Gold)
Step 9:  Risk Appetite (Low/Medium/High)
Step 10: Primary Goal (House/Car/Education/Retirement/Emergency)
Step 11: Goal Amount
Step 12: Target Timeline
→ AI generates personalized Financial Plan
```

### 2. Daily Automation Schedule
| Time | Action | Content |
|------|--------|---------|
| 6:00 AM | Morning Briefing | Yesterday's summary + Today's targets + Motivation |
| 9:00 AM | Market Analysis | Stock market update, investment opportunities |
| 8:00 PM | Evening Check-in | Ask for today's data, calculate, update progress |
| 10:00 PM | Night Summary | Final day report, savings achieved, goal progress |

### 3. Core Features

#### A. Transaction Tracking
- Log expenses: "Spent 500 on groceries"
- Log income: "Earned 5000 from freelance"
- Smart categorization using AI
- Photo/PDF receipt scanning

#### B. Multiple Goal Management
- Add goals: "Add goal: Buy iPhone, 80000, 6 months"
- Track progress for each
- Prioritize goals
- Celebrate achievements

#### C. Investment Advisory
- Daily market analysis (AlphaVantage)
- Personalized recommendations
- Risk-based suggestions
- SIP reminders

#### D. Budget Management
- Auto-calculate daily budget
- Category-wise limits
- Alert when exceeding
- Smart adjustments

#### E. Reports & Analytics
- Daily summary
- Weekly comparison (% change)
- Monthly detailed report
- PDF generation

### 4. AI Capabilities

#### OpenAI Integration
- Natural language understanding
- Personalized financial advice
- Motivational messages
- Document text extraction
- Multilingual responses

#### AlphaVantage Integration
- Real-time stock prices
- Market trends
- Top performers
- Investment recommendations

---

## 💾 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(100),
    language VARCHAR(5) DEFAULT 'en',
    occupation VARCHAR(50),
    monthly_income DECIMAL(15,2),
    fixed_expenses DECIMAL(15,2),
    variable_expenses DECIMAL(15,2),
    current_savings DECIMAL(15,2),
    current_investments DECIMAL(15,2),
    risk_appetite VARCHAR(20),
    daily_budget DECIMAL(15,2),
    onboarding_complete BOOLEAN DEFAULT FALSE,
    onboarding_step INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP
);
```

### Goals Table
```sql
CREATE TABLE goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    target_amount DECIMAL(15,2),
    current_amount DECIMAL(15,2) DEFAULT 0,
    deadline DATE,
    priority INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'active',
    achieved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(20) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    category VARCHAR(50),
    description TEXT,
    source VARCHAR(50),
    date TIMESTAMP DEFAULT NOW()
);
```

### Investments Table
```sql
CREATE TABLE investments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(50),
    name VARCHAR(100),
    amount DECIMAL(15,2),
    current_value DECIMAL(15,2),
    purchase_date DATE,
    notes TEXT
);
```

### Market_Data Table
```sql
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    price DECIMAL(15,2),
    change_percent DECIMAL(5,2),
    trend VARCHAR(20),
    fetched_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔄 n8n Workflow Design

### Workflow 1: Message Processing
```
Webhook (WhatsApp) → Extract Data → MoneyView API → Generate Reply → Baileys Send
```

### Workflow 2: Morning Briefing (6 AM)
```
Schedule 6AM → Get Users → Generate Yesterday Summary → Calculate Today Target → 
Motivational Quote → Send via Baileys
```

### Workflow 3: Market Analysis (9 AM)
```
Schedule 9AM → Fetch AlphaVantage → Analyze Trends → 
Generate Recommendations → Send to Interested Users
```

### Workflow 4: Evening Check-in (8 PM)
```
Schedule 8PM → Get Users → Calculate Today's Data → 
Ask for Additional Data → Update Records → Send Summary
```

### Workflow 5: Weekly Report (Sunday 10 AM)
```
Schedule Sunday → Get Week Data → Compare with Last Week → 
Calculate % Change → Generate PDF → Send Report
```

---

## 🌍 Multilingual Support

| Language | Code | Greeting | Expense Logged |
|----------|------|----------|----------------|
| English | en | Good Morning! | ✅ Expense recorded! |
| Hindi | hi | सुप्रभात! | ✅ खर्च दर्ज! |
| Tamil | ta | காலை வணக்கம்! | ✅ செலவு பதிவு! |
| Telugu | te | శుభోదయం! | ✅ ఖర్చు నమోదు! |
| Kannada | kn | ಶುಭೋದಯ! | ✅ ವೆಚ್ಚ ದಾಖಲು! |

---

## 📱 Conversation Examples

### Scenario 1: Lokesh (College Student)
```
Lokesh: Hi
MoneyView: 👋 Welcome to MoneyView! I'm your AI financial advisor.
          Let's set up your profile. What language do you prefer?
          1. English  2. हिंदी  3. தமிழ்  4. తెలుగు

Lokesh: 1
MoneyView: Great! What should I call you?

Lokesh: Lokesh
MoneyView: Nice to meet you, Lokesh! 😊 What do you do?
          1. Student  2. Employee  3. Business  4. Freelancer  5. Homemaker

Lokesh: 4
MoneyView: Awesome, freelancer! 💪 What's your approximate monthly income?

Lokesh: 25000
MoneyView: ₹25,000/month - good start! 
          What are your fixed monthly expenses? (rent, EMI, subscriptions)

Lokesh: 8000
MoneyView: Got it. And how much do you spend on variable things?
          (food, transport, entertainment)

Lokesh: 10000
MoneyView: I see you have about ₹7,000 left to save/invest.
          Do you have any current savings in bank?

Lokesh: 50000
MoneyView: Great! ₹50,000 emergency fund. 
          Any investments? (FD, Mutual Funds, Stocks)

Lokesh: Nope
MoneyView: No worries, we'll build that! What's your risk tolerance?
          1. Low (Safe)  2. Medium (Balanced)  3. High (Aggressive)

Lokesh: 2
MoneyView: Perfect! Now, what's your dream goal?

Lokesh: I want to clear my education loan of 20 lakh and buy a bike

MoneyView: Great goals! Let me set these up:
          🎯 Goal 1: Clear Education Loan - ₹20,00,000
          🎯 Goal 2: Buy Bike - ₹1,50,000 (estimated)
          
          By when do you want to achieve the loan goal?

Lokesh: 5 years

MoneyView: 🎉 *Your MoneyView Financial Plan is Ready!*

📊 *Profile Summary:*
━━━━━━━━━━━━━━━━━━
👤 Lokesh (Freelancer)
💰 Income: ₹25,000/month
💸 Expenses: ₹18,000/month
💵 Savings: ₹50,000

🎯 *Goals:*
1. Education Loan: ₹20,00,000 in 5 years
2. Bike: ₹1,50,000

📈 *My Recommendation:*
• Monthly Savings Target: ₹7,000
• For Loan: ₹5,500/month (in SIP or RD)
• For Bike: ₹1,500/month (in RD)
• Emergency kept: ₹50,000 ✅

⏰ *I'll remind you:*
• 6 AM: Yesterday's summary + Today's targets
• 9 AM: Stock market updates
• 8 PM: End of day check-in

Let's start! Type "help" anytime 💪
```

### Scenario 2: Kaviya (Homemaker)
```
MoneyView (8 PM): 🌙 Good evening, Kaviya!

Today's Summary:
💵 Income: ₹0
💸 Spent: ₹450 (groceries)
💰 Saved: ₹550 (from daily budget)

Did you have any other income or expenses today?
Just type: "Spent 200 on vegetables" or "Earned 500"

Kaviya: I earned 300 from selling pickles

MoneyView: 🎉 That's wonderful, Kaviya!

✅ *Income Added:* ₹300 (Side Business)

📊 *Updated Today:*
💵 Income: ₹300
💸 Spent: ₹450
💰 Net: -₹150

But with your daily budget surplus, you're still saving!
Weekly Savings so far: ₹2,850 🎯

Your pickle business is growing! Should I track this separately?
Type "yes" to create a business income category.
```

### Scenario 3: Market Analysis
```
MoneyView (9 AM): 📈 *Good Morning, Lokesh!*

*Today's Market Pulse:*
━━━━━━━━━━━━━━━━━━
🟢 NIFTY 50: 22,456 (+0.8%)
🟢 SENSEX: 74,125 (+0.7%)
💹 Bank Nifty: 48,890 (+1.2%)

*Top Gainers:*
• HDFC Bank: +2.5%
• Reliance: +1.8%
• Infosys: +1.5%

*My Pick for SIP:*
📌 Nifty Index Fund - Perfect for medium risk
   Start with ₹500/month

*Investment Tip:*
💡 Markets are trending up. Good time to 
   start your monthly SIP!

Want me to explain how to start? Type "SIP guide"
```

---

## 🛠️ Implementation Phases

### Phase 1: Core Agent (Week 1)
- [ ] MoneyView Agent with OpenAI
- [ ] Complete onboarding flow
- [ ] Transaction logging
- [ ] Basic budget calculation
- [ ] Database setup

### Phase 2: Market & Investment (Week 2)
- [ ] AlphaVantage integration
- [ ] Stock market analysis
- [ ] Investment recommendations
- [ ] SIP tracking

### Phase 3: Automation (Week 3)
- [ ] n8n workflows for all schedules
- [ ] Morning/Evening/Night messages
- [ ] Weekly/Monthly reports
- [ ] PDF generation

### Phase 4: Advanced Features (Week 4)
- [ ] Document scanning (receipts)
- [ ] Multiple goals management
- [ ] Goal celebration
- [ ] Voice note support

### Phase 5: Dashboard & Polish (Week 5)
- [ ] Web dashboard UI
- [ ] Real-time charts
- [ ] Mobile optimization
- [ ] Testing & deployment

### Phase 6: Future Roadmap (Post-Hackathon)
- [ ] **Voice Reply Integration:** Two-way voice conversations
- [ ] **UPI Integration:** Deep integration with payments
- [ ] **Family Accounts:** Shared budgeting
- [ ] **AI Investment Desk:** Automated portfolio management


---

## 📁 File Structure

```
moneyview/
├── agents/
│   └── moneyview_agent.py      # Main AI agent
├── services/
│   ├── stock_market_service.py  # AlphaVantage integration
│   ├── document_scanner.py      # Receipt/PDF scanning
│   ├── report_generator.py      # PDF reports
│   ├── budget_advisor.py        # Budget calculations
│   └── investment_advisor.py    # Investment recommendations
├── database/
│   ├── models.py                # SQLAlchemy models
│   ├── user_repository.py
│   ├── goal_repository.py
│   ├── transaction_repository.py
│   └── investment_repository.py
├── n8n/
│   └── workflows/
│       └── moneyview_complete.json
├── whatsapp-bot/
│   └── index.js                 # Baileys bot
├── static/
│   └── dashboard.html           # Web dashboard
├── app.py                       # FastAPI main
└── requirements.txt
```

---

## 🔐 Security

- Phone-based authentication
- OTP via WhatsApp
- Password hashing (bcrypt)
- API key encryption
- Rate limiting

---

## 📊 Success Metrics

- User retention rate
- Goals achieved rate
- Monthly savings increase
- User engagement (messages/day)
- Accuracy of market predictions

---

*MoneyView - Your Personal Finance Partner* 💰
