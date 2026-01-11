"""
MoneyViya Configuration v3.0
==============================
For ALL irregular income earners - Students, Housewives, Gig Workers, 
Freelancers, Small Vendors, BPO Workers, and Middle Class families
"""
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
VOICES_DIR = DATA_DIR / "voices"
UPLOADS_DIR = DATA_DIR / "uploads"
DOCUMENTS_DIR = DATA_DIR / "documents"

# Ensure directories exist
for d in [DATA_DIR, VOICES_DIR, UPLOADS_DIR, DOCUMENTS_DIR]:
    d.mkdir(exist_ok=True)

# Database files
USERS_DB_FILE = DATA_DIR / "users.json"
TRANSACTIONS_DB_FILE = DATA_DIR / "transactions.json"
GOALS_DB_FILE = DATA_DIR / "goals.json"
REMINDERS_DB_FILE = DATA_DIR / "reminders.json"
ALERTS_DB_FILE = DATA_DIR / "alerts.json"
BUDGETS_DB_FILE = DATA_DIR / "budgets.json"

# ================= SUPPORTED LANGUAGES =================
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "greeting": "Hello", "tts_code": "en"},
    "hi": {"name": "हिंदी", "greeting": "नमस्ते", "tts_code": "hi"},
    "ta": {"name": "தமிழ்", "greeting": "வணக்கம்", "tts_code": "ta"},
    "te": {"name": "తెలుగు", "greeting": "నమస్కారం", "tts_code": "te"},
    "kn": {"name": "ಕನ್ನಡ", "greeting": "ನಮಸ್ಕಾರ", "tts_code": "kn"},
    "ml": {"name": "മലയാളം", "greeting": "നമസ്കാരം", "tts_code": "ml"},
    "mr": {"name": "मराठी", "greeting": "नमस्कार", "tts_code": "mr"},
    "gu": {"name": "ગુજરાતી", "greeting": "નમસ્તે", "tts_code": "gu"},
    "bn": {"name": "বাংলা", "greeting": "নমস্কার", "tts_code": "bn"},
    "pa": {"name": "ਪੰਜਾਬੀ", "greeting": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ", "tts_code": "pa"},
}

# ================= USER TYPES (Broader Categories) =================
USER_TYPES = {
    # Gig Economy Workers
    "delivery_partner": {
        "name": "Delivery Partner",
        "name_hi": "डिलीवरी पार्टनर",
        "description": "Swiggy, Zomato, Amazon, Flipkart, Dunzo, etc.",
        "income_type": "daily_variable",
        "typical_income": (15000, 35000),
        "tips": ["Track daily earnings", "Save on high-earning days", "Emergency fund for slow days"]
    },
    "cab_driver": {
        "name": "Cab/Auto Driver",
        "name_hi": "कैब/ऑटो ड्राइवर",
        "description": "Uber, Ola, Rapido, personal auto/taxi",
        "income_type": "daily_variable",
        "typical_income": (20000, 50000),
        "tips": ["Track fuel expenses", "Maintain vehicle fund", "Plan for EMI carefully"]
    },
    "freelancer": {
        "name": "Freelancer",
        "name_hi": "फ्रीलांसर",
        "description": "Content writer, designer, developer, consultant",
        "income_type": "project_based",
        "typical_income": (20000, 100000),
        "tips": ["Invoice tracking", "Tax savings", "Diversify clients"]
    },
    
    # Students
    "student": {
        "name": "Student",
        "name_hi": "छात्र/छात्रा",
        "description": "College/university student managing pocket money or part-time work",
        "income_type": "allowance_parttime",
        "typical_income": (2000, 15000),
        "tips": ["Track hostel expenses", "Save from pocket money", "Build habits now"]
    },
    "student_working": {
        "name": "Working Student",
        "name_hi": "काम करने वाला छात्र",
        "description": "Student with part-time job or internship",
        "income_type": "part_time",
        "typical_income": (5000, 25000),
        "tips": ["Balance work and study", "Save 10% minimum", "Build emergency fund"]
    },
    
    # Homemakers
    "homemaker": {
        "name": "Homemaker",
        "name_hi": "गृहिणी",
        "description": "Managing household budget and expenses",
        "income_type": "household_budget",
        "typical_income": (0, 0),  # Works with household budget
        "tips": ["Track grocery expenses", "Save on utilities", "Monthly household planning"]
    },
    "homemaker_earning": {
        "name": "Earning Homemaker",
        "name_hi": "कमाने वाली गृहिणी",
        "description": "Homemaker with side income (tiffin, tailoring, tuition, etc.)",
        "income_type": "side_business",
        "typical_income": (3000, 20000),
        "tips": ["Separate business and household", "Track material costs", "Grow your business"]
    },
    
    # BPO & Service Workers
    "bpo_worker": {
        "name": "BPO/Call Center",
        "name_hi": "BPO/कॉल सेंटर",
        "description": "Call center, customer support, back office",
        "income_type": "salary_incentive",
        "typical_income": (15000, 40000),
        "tips": ["Track incentives", "Plan for variable pay", "Night shift savings"]
    },
    "retail_worker": {
        "name": "Retail/Shop Worker",
        "name_hi": "दुकान कर्मचारी",
        "description": "Shop assistant, mall staff, salesperson",
        "income_type": "salary_commission",
        "typical_income": (10000, 25000),
        "tips": ["Track commission separately", "Save during festivals", "Plan for slow months"]
    },
    
    # Small Business
    "small_vendor": {
        "name": "Small Vendor/Shopkeeper",
        "name_hi": "छोटा दुकानदार",
        "description": "Street vendor, small shop owner, kirana store",
        "income_type": "daily_business",
        "typical_income": (15000, 60000),
        "tips": ["Separate personal and business", "Track stock costs", "Save for slow seasons"]
    },
    "skilled_worker": {
        "name": "Skilled Worker",
        "name_hi": "कारीगर",
        "description": "Electrician, plumber, carpenter, mechanic, tailor",
        "income_type": "job_based",
        "typical_income": (15000, 50000),
        "tips": ["Track material costs", "Save for tool upgrades", "Build customer base"]
    },
    
    # Fixed but Limited Income
    "low_income_salaried": {
        "name": "Low-income Salaried",
        "name_hi": "कम वेतन वाला",
        "description": "Security guard, helper, driver, domestic worker",
        "income_type": "fixed_low",
        "typical_income": (8000, 18000),
        "tips": ["Every rupee matters", "Avoid debt traps", "Small savings big future"]
    },
    "pensioner": {
        "name": "Pensioner/Retired",
        "name_hi": "पेंशनभोगी",
        "description": "Retired person living on pension",
        "income_type": "fixed_pension",
        "typical_income": (10000, 40000),
        "tips": ["Medical fund priority", "Safe investments only", "Track medicine expenses"]
    },
    
    # Others
    "daily_wage": {
        "name": "Daily Wage Worker",
        "name_hi": "दैनिक मजदूर",
        "description": "Construction, labor, farm worker",
        "income_type": "daily_cash",
        "typical_income": (8000, 20000),
        "tips": ["Save on earning days", "Track work days", "Build rainy day fund"]
    },
    "farmer": {
        "name": "Farmer/Kisaan",
        "name_hi": "किसान",
        "description": "Small/marginal farmer with seasonal income",
        "income_type": "seasonal",
        "typical_income": (5000, 50000),
        "tips": ["Plan for off-season", "Track crop expenses", "Dairy as side income"]
    },
    "other": {
        "name": "Other",
        "name_hi": "अन्य",
        "description": "Any other profession",
        "income_type": "variable",
        "typical_income": (10000, 50000),
        "tips": ["Track everything", "Save 20% if possible", "Build emergency fund"]
    }
}

# ================= INCOME CATEGORIES =================
INCOME_CATEGORIES = {
    # Gig/Delivery
    "delivery_earnings": {"name": "Delivery Earnings", "name_hi": "डिलीवरी कमाई", "icon": "🛵"},
    "ride_earnings": {"name": "Ride Earnings", "name_hi": "राइड कमाई", "icon": "🚗"},
    "tips": {"name": "Tips", "name_hi": "टिप", "icon": "💝"},
    "incentive": {"name": "Incentive/Bonus", "name_hi": "इंसेंटिव/बोनस", "icon": "🎁"},
    
    # Salary/Job
    "salary": {"name": "Salary", "name_hi": "सैलरी", "icon": "💼"},
    "overtime": {"name": "Overtime", "name_hi": "ओवरटाइम", "icon": "⏰"},
    "commission": {"name": "Commission", "name_hi": "कमीशन", "icon": "📊"},
    
    # Business
    "sales": {"name": "Sales/Business", "name_hi": "बिक्री/व्यापार", "icon": "🏪"},
    "service_income": {"name": "Service Income", "name_hi": "सेवा आय", "icon": "🔧"},
    
    # Student/Home
    "pocket_money": {"name": "Pocket Money", "name_hi": "जेब खर्च", "icon": "👛"},
    "allowance": {"name": "Allowance", "name_hi": "भत्ता", "icon": "💵"},
    "part_time": {"name": "Part-time Work", "name_hi": "पार्ट-टाइम", "icon": "📝"},
    "tuition_income": {"name": "Tuition Income", "name_hi": "ट्यूशन आय", "icon": "📚"},
    "tiffin_income": {"name": "Tiffin/Food Income", "name_hi": "टिफिन आय", "icon": "🍱"},
    "tailoring_income": {"name": "Tailoring Income", "name_hi": "सिलाई आय", "icon": "🧵"},
    
    # Other
    "freelance": {"name": "Freelance", "name_hi": "फ्रीलांस", "icon": "💻"},
    "daily_wage": {"name": "Daily Wage", "name_hi": "दैनिक मजदूरी", "icon": "🏗️"},
    "pension": {"name": "Pension", "name_hi": "पेंशन", "icon": "👴"},
    "rent_received": {"name": "Rent Received", "name_hi": "किराया प्राप्त", "icon": "🏠"},
    "interest": {"name": "Interest", "name_hi": "ब्याज", "icon": "🏦"},
    "gift": {"name": "Gift/Help", "name_hi": "उपहार/मदद", "icon": "🎀"},
    "refund": {"name": "Refund", "name_hi": "रिफंड", "icon": "↩️"},
    "government_benefit": {"name": "Government Benefit", "name_hi": "सरकारी लाभ", "icon": "🏛️"},
    "other_income": {"name": "Other Income", "name_hi": "अन्य आय", "icon": "💰"},
}

# ================= EXPENSE CATEGORIES =================
EXPENSE_CATEGORIES = {
    # Essential
    "food": {"name": "Food/Groceries", "name_hi": "खाना/किराना", "icon": "🍔", "priority": 1},
    "vegetables": {"name": "Vegetables/Sabzi", "name_hi": "सब्जी", "icon": "🥬", "priority": 1},
    "milk_dairy": {"name": "Milk/Dairy", "name_hi": "दूध/डेयरी", "icon": "🥛", "priority": 1},
    "rent": {"name": "Rent/Housing", "name_hi": "किराया/घर", "icon": "🏠", "priority": 1},
    "utilities": {"name": "Electricity/Water", "name_hi": "बिजली/पानी", "icon": "💡", "priority": 1},
    "gas": {"name": "Cooking Gas", "name_hi": "गैस सिलेंडर", "icon": "🔥", "priority": 1},
    
    # Transport
    "petrol": {"name": "Petrol/Diesel", "name_hi": "पेट्रोल/डीज़ल", "icon": "⛽", "priority": 2},
    "transport": {"name": "Transport/Auto", "name_hi": "ट्रांसपोर्ट/ऑटो", "icon": "🚌", "priority": 2},
    "vehicle_maintenance": {"name": "Vehicle Repair", "name_hi": "गाड़ी मरम्मत", "icon": "🔧", "priority": 2},
    
    # Communication
    "mobile_recharge": {"name": "Mobile Recharge", "name_hi": "मोबाइल रिचार्ज", "icon": "📱", "priority": 2},
    "internet": {"name": "Internet/WiFi", "name_hi": "इंटरनेट", "icon": "📶", "priority": 2},
    
    # Health
    "medicine": {"name": "Medicine", "name_hi": "दवाई", "icon": "💊", "priority": 1},
    "doctor": {"name": "Doctor/Hospital", "name_hi": "डॉक्टर/हॉस्पिटल", "icon": "🏥", "priority": 1},
    
    # Education
    "school_fees": {"name": "School/College Fees", "name_hi": "स्कूल/कॉलेज फीस", "icon": "🎓", "priority": 1},
    "books_stationery": {"name": "Books/Stationery", "name_hi": "किताबें/स्टेशनरी", "icon": "📚", "priority": 2},
    "tuition_fees": {"name": "Tuition Fees", "name_hi": "ट्यूशन फीस", "icon": "✏️", "priority": 2},
    
    # Family
    "children": {"name": "Children Expenses", "name_hi": "बच्चों का खर्च", "icon": "👶", "priority": 2},
    "family_support": {"name": "Family Support", "name_hi": "परिवार की मदद", "icon": "👨‍👩‍👧", "priority": 2},
    
    # Loans/EMI
    "emi": {"name": "EMI/Loan", "name_hi": "EMI/लोन", "icon": "🏦", "priority": 1},
    "credit_card": {"name": "Credit Card", "name_hi": "क्रेडिट कार्ड", "icon": "💳", "priority": 1},
    
    # Insurance & Investment
    "insurance": {"name": "Insurance", "name_hi": "बीमा", "icon": "🛡️", "priority": 2},
    "investment": {"name": "Investment/SIP", "name_hi": "निवेश/SIP", "icon": "📈", "priority": 3},
    
    # Shopping
    "clothes": {"name": "Clothes", "name_hi": "कपड़े", "icon": "👕", "priority": 3},
    "shopping": {"name": "Shopping", "name_hi": "शॉपिंग", "icon": "🛍️", "priority": 3},
    
    # Entertainment
    "entertainment": {"name": "Entertainment", "name_hi": "मनोरंजन", "icon": "🎬", "priority": 4},
    "eating_out": {"name": "Eating Out", "name_hi": "बाहर खाना", "icon": "🍽️", "priority": 4},
    
    # Social
    "religious": {"name": "Religious/Puja", "name_hi": "धार्मिक/पूजा", "icon": "🛕", "priority": 3},
    "gifts": {"name": "Gifts/Shagun", "name_hi": "तोहफे/शगुन", "icon": "🎁", "priority": 3},
    "charity": {"name": "Charity/Donation", "name_hi": "दान", "icon": "🙏", "priority": 3},
    
    # Business (for vendors)
    "stock_purchase": {"name": "Stock/Inventory", "name_hi": "स्टॉक/माल", "icon": "📦", "priority": 1},
    "raw_material": {"name": "Raw Material", "name_hi": "कच्चा माल", "icon": "🧱", "priority": 1},
    "shop_rent": {"name": "Shop Rent", "name_hi": "दुकान किराया", "icon": "🏪", "priority": 1},
    
    # Other
    "other_expense": {"name": "Other", "name_hi": "अन्य", "icon": "📦", "priority": 4},
}

# ================= FINANCIAL GOALS =================
GOAL_TYPES = {
    "emergency_fund": {"name": "Emergency Fund", "name_hi": "इमरजेंसी फंड", "icon": "🆘", "months": 6},
    "debt_free": {"name": "Become Debt Free", "name_hi": "कर्ज मुक्त", "icon": "⛓️", "priority": 1},
    "child_education": {"name": "Child's Education", "name_hi": "बच्चों की पढ़ाई", "icon": "🎓", "years": 18},
    "higher_education": {"name": "Higher Education", "name_hi": "उच्च शिक्षा", "icon": "📚", "years": 3},
    "home": {"name": "Buy Home", "name_hi": "घर खरीदना", "icon": "🏠", "years": 15},
    "vehicle_bike": {"name": "Buy Bike/Scooter", "name_hi": "बाइक/स्कूटर", "icon": "🛵", "years": 2},
    "vehicle_car": {"name": "Buy Car", "name_hi": "कार खरीदना", "icon": "🚗", "years": 5},
    "wedding": {"name": "Wedding", "name_hi": "शादी", "icon": "💒", "years": 5},
    "retirement": {"name": "Retirement", "name_hi": "रिटायरमेंट", "icon": "🏖️", "years": 25},
    "vacation": {"name": "Vacation/Travel", "name_hi": "छुट्टी/यात्रा", "icon": "✈️", "years": 1},
    "start_business": {"name": "Start Business", "name_hi": "बिज़नेस शुरू करना", "icon": "🚀", "years": 3},
    "upgrade_shop": {"name": "Upgrade Shop", "name_hi": "दुकान बड़ी करना", "icon": "🏪", "years": 2},
    "phone": {"name": "Buy Phone", "name_hi": "फोन खरीदना", "icon": "📱", "months": 6},
    "laptop": {"name": "Buy Laptop", "name_hi": "लैपटॉप खरीदना", "icon": "💻", "months": 12},
    "gold": {"name": "Buy Gold/Jewelry", "name_hi": "सोना/गहने", "icon": "💍", "years": 3},
    "medical": {"name": "Medical Fund", "name_hi": "मेडिकल फंड", "icon": "🏥", "months": 12},
    "festival": {"name": "Festival Savings", "name_hi": "त्योहार बचत", "icon": "🎉", "months": 6},
    "other": {"name": "Other Goal", "name_hi": "अन्य लक्ष्य", "icon": "🎯", "years": 1},
}

# ================= INVESTMENT OPTIONS (India Specific) =================
INVESTMENT_OPTIONS = {
    # Ultra Safe (for beginners/low income)
    "piggy_bank": {
        "name": "Digital Piggy Bank (App)",
        "name_hi": "डिजिटल गुल्लक",
        "risk": "none",
        "min_amount": 1,
        "returns": "0%",
        "for": ["student", "daily_wage", "low_income_salaried"]
    },
    "post_office_rd": {
        "name": "Post Office RD",
        "name_hi": "पोस्ट ऑफिस RD",
        "risk": "none",
        "min_amount": 100,
        "returns": "6.5%",
        "for": ["all"]
    },
    "sukanya": {
        "name": "Sukanya Samriddhi (Girl Child)",
        "name_hi": "सुकन्या समृद्धि",
        "risk": "none",
        "min_amount": 250,
        "returns": "8%",
        "for": ["homemaker", "low_income_salaried"]
    },
    
    # Low Risk
    "ppf": {
        "name": "PPF",
        "name_hi": "PPF",
        "risk": "very_low",
        "min_amount": 500,
        "returns": "7.1%",
        "lock_in": "15 years",
        "for": ["all"]
    },
    "fd": {
        "name": "Fixed Deposit",
        "name_hi": "FD",
        "risk": "very_low",
        "min_amount": 1000,
        "returns": "6-7%",
        "for": ["all"]
    },
    
    # Medium Risk
    "liquid_fund": {
        "name": "Liquid Fund",
        "name_hi": "लिक्विड फंड",
        "risk": "low",
        "min_amount": 500,
        "returns": "6-7%",
        "for": ["freelancer", "small_vendor", "bpo_worker"]
    },
    "debt_fund": {
        "name": "Debt Mutual Fund",
        "name_hi": "डेट म्यूचुअल फंड",
        "risk": "low",
        "min_amount": 1000,
        "returns": "7-9%",
        "for": ["freelancer", "bpo_worker", "skilled_worker"]
    },
    "balanced_fund": {
        "name": "Balanced/Hybrid Fund",
        "name_hi": "बैलेंस्ड फंड",
        "risk": "medium",
        "min_amount": 500,
        "returns": "10-12%",
        "for": ["freelancer", "cab_driver", "small_vendor"]
    },
    
    # Higher Risk (For stable income only)
    "index_fund": {
        "name": "Index Fund (Nifty 50)",
        "name_hi": "इंडेक्स फंड",
        "risk": "medium",
        "min_amount": 500,
        "returns": "12-15%",
        "for": ["freelancer", "bpo_worker"]
    },
    "gold_etf": {
        "name": "Gold ETF/SGB",
        "name_hi": "गोल्ड ETF",
        "risk": "medium",
        "min_amount": 1000,
        "returns": "8-10%",
        "for": ["all"]
    },
    
    # Traditional
    "chit_fund": {
        "name": "Chit Fund (Registered)",
        "name_hi": "चिट फंड",
        "risk": "medium",
        "min_amount": 500,
        "returns": "variable",
        "for": ["small_vendor", "skilled_worker", "homemaker"]
    },
}

# ================= FINANCIAL CONSTANTS =================
FINANCIAL_CONSTANTS = {
    "emergency_fund_months": 6,
    "min_emergency_months": 3,
    "safe_emi_percent": 30,
    "max_emi_percent": 40,
    "recommended_savings_percent": 20,
    "min_savings_percent": 10,
    "debt_danger_ratio": 50,  # Debt > 50% of annual income is dangerous
}

# ================= ONBOARDING STEPS =================
ONBOARDING_STEPS = [
    "NAME",
    "LANGUAGE", 
    "USER_TYPE",      # Changed from PROFESSION
    "MONTHLY_INCOME",
    "INCOME_SOURCES", # NEW: Multiple income sources
    "DEPENDENTS",
    "CURRENT_SAVINGS",
    "CURRENT_DEBT",
    "EMI_AMOUNT",     # NEW: Monthly EMI if any
    "GOALS",
]

# ================= SAVINGS CHALLENGES =================
SAVINGS_CHALLENGES = {
    "52_week": {
        "name": "52 Week Challenge",
        "name_hi": "52 हफ्ते चैलेंज",
        "description": "Save ₹10 in week 1, ₹20 in week 2... ₹520 in week 52",
        "total_savings": 13780,
        "duration_weeks": 52,
        "icon": "📅"
    },
    "no_spend_day": {
        "name": "No Spend Day",
        "name_hi": "खर्च-मुक्त दिन",
        "description": "Have one no-spend day per week",
        "frequency": "weekly",
        "icon": "🚫"
    },
    "round_up": {
        "name": "Round-Up Savings",
        "name_hi": "राउंड-अप बचत",
        "description": "Round up expenses and save the difference",
        "icon": "⬆️"
    },
    "coin_jar": {
        "name": "Digital Coin Jar",
        "name_hi": "डिजिटल गुल्लक",
        "description": "Save all amounts under ₹50",
        "icon": "🏺"
    },
    "1_percent": {
        "name": "1% More Each Month",
        "name_hi": "हर महीने 1% ज़्यादा",
        "description": "Increase savings by 1% every month",
        "icon": "📈"
    },
}

# ================= BILL REMINDERS =================
BILL_TYPES = {
    "electricity": {"name": "Electricity Bill", "name_hi": "बिजली बिल", "icon": "💡", "frequency": "monthly"},
    "water": {"name": "Water Bill", "name_hi": "पानी बिल", "icon": "💧", "frequency": "monthly"},
    "gas": {"name": "Gas Cylinder", "name_hi": "गैस सिलेंडर", "icon": "🔥", "frequency": "monthly"},
    "mobile": {"name": "Mobile Recharge", "name_hi": "मोबाइल रिचार्ज", "icon": "📱", "frequency": "monthly"},
    "internet": {"name": "Internet Bill", "name_hi": "इंटरनेट बिल", "icon": "📶", "frequency": "monthly"},
    "rent": {"name": "Rent", "name_hi": "किराया", "icon": "🏠", "frequency": "monthly"},
    "emi_loan": {"name": "Loan EMI", "name_hi": "लोन EMI", "icon": "🏦", "frequency": "monthly"},
    "emi_vehicle": {"name": "Vehicle EMI", "name_hi": "गाड़ी EMI", "icon": "🛵", "frequency": "monthly"},
    "insurance": {"name": "Insurance Premium", "name_hi": "बीमा प्रीमियम", "icon": "🛡️", "frequency": "yearly"},
    "school_fees": {"name": "School Fees", "name_hi": "स्कूल फीस", "icon": "🎓", "frequency": "quarterly"},
    "sip": {"name": "SIP Investment", "name_hi": "SIP निवेश", "icon": "📈", "frequency": "monthly"},
}

# ================= DANGER ALERTS =================
FINANCIAL_DANGERS = {
    "loan_apps": {
        "name": "Loan App Trap",
        "name_hi": "लोन ऐप का जाल",
        "description": "High interest instant loan apps",
        "warning": "⚠️ These apps charge 100-300% interest!"
    },
    "scam_calls": {
        "name": "OTP/KYC Scam",
        "name_hi": "OTP/KYC धोखा",
        "description": "Calls asking for OTP or KYC update",
        "warning": "🚨 Never share OTP with anyone!"
    },
    "ponzi": {
        "name": "Double Money Scheme",
        "name_hi": "पैसा डबल स्कीम",
        "description": "Too good to be true returns",
        "warning": "🚫 If it sounds too good, it's a scam!"
    },
}

# ================= API CONFIGURATIONS =================
# Twilio (loaded from environment variables)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
TWILIO_VOICE_NUMBER = os.getenv("TWILIO_VOICE_NUMBER", "")

# OCR
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Market data (optional)
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "YUBGZ4Y4QS5SI0IX")

