"""
Financial Literacy & Education Service
======================================
Educate users about personal finance in simple language
"""
from typing import Dict, List
from datetime import datetime
import random


class FinancialLiteracyService:
    """Simple financial education for all"""
    
    def __init__(self):
        self.lessons = self._load_lessons()
        self.scam_alerts = self._load_scam_alerts()
        self.government_schemes = self._load_schemes()
    
    def _load_lessons(self) -> Dict[str, List[Dict]]:
        """Financial lessons in simple language"""
        return {
            "basics": [
                {
                    "id": "income_expense",
                    "title": "Income vs Expense",
                    "title_hi": "आमदनी बनाम खर्च",
                    "content": "Income is money you earn. Expense is money you spend. Income - Expense = Savings. Always try to keep Income > Expense.",
                    "content_hi": "आमदनी = कमाई। खर्च = जो पैसे खर्च होते हैं। आमदनी - खर्च = बचत। हमेशा कोशिश करें कि आमदनी > खर्च।",
                    "icon": "📊"
                },
                {
                    "id": "emergency_fund",
                    "title": "Emergency Fund - Your Safety Net",
                    "title_hi": "इमरजेंसी फंड - आपका सुरक्षा कवच",
                    "content": "Emergency fund = 3-6 months of expenses saved. It protects you when: job loss, medical emergency, vehicle breakdown. Keep it in a separate savings account. Don't invest it - keep it liquid.",
                    "content_hi": "इमरजेंसी फंड = 3-6 महीने का खर्च बचाकर रखना। ये आपको बचाता है: नौकरी जाने पर, मेडिकल इमरजेंसी में, गाड़ी खराब होने पर। इसे अलग सेविंग्स अकाउंट में रखें। इसे invest न करें।",
                    "icon": "🆘"
                },
                {
                    "id": "compound_interest",
                    "title": "The Magic of Compound Interest",
                    "title_hi": "चक्रवृद्धि ब्याज का जादू",
                    "content": "Compound interest = Interest on interest. ₹1000/month at 12% for 20 years = ₹9.9 lakhs! Start early. Even small amounts grow big over time.",
                    "content_hi": "चक्रवृद्धि ब्याज = ब्याज पर ब्याज। ₹1000/महीना 12% पर 20 साल में = ₹9.9 लाख! जल्दी शुरू करें। छोटी रकम भी बड़ी बन जाती है।",
                    "icon": "📈"
                },
            ],
            "savings": [
                {
                    "id": "pay_yourself_first",
                    "title": "Pay Yourself First",
                    "title_hi": "पहले खुद को भुगतान करें",
                    "content": "When income comes, first transfer 10-20% to savings. Then spend what's left. Don't save what's left after spending - spend what's left after saving.",
                    "content_hi": "जब पैसे आएं, पहले 10-20% बचत में डालें। बाकी खर्च करें। खर्च के बाद बचाना नहीं - बचत के बाद खर्च करना।",
                    "icon": "💰"
                },
                {
                    "id": "50_30_20_rule",
                    "title": "50-30-20 Rule",
                    "title_hi": "50-30-20 का नियम",
                    "content": "50% for needs (rent, food, bills). 30% for wants (entertainment, shopping). 20% for savings and debt repayment. Adjust based on your income level.",
                    "content_hi": "50% जरूरतों के लिए (किराया, खाना, बिल)। 30% इच्छाओं के लिए (मनोरंजन, शॉपिंग)। 20% बचत और कर्ज चुकाने के लिए। अपनी आय के हिसाब से adjust करें।",
                    "icon": "🥧"
                },
            ],
            "debt": [
                {
                    "id": "good_vs_bad_debt",
                    "title": "Good Debt vs Bad Debt",
                    "title_hi": "अच्छा कर्ज vs बुरा कर्ज",
                    "content": "Good debt: Education loan, home loan - assets that grow. Bad debt: Credit card, personal loan for wants, loan apps. Avoid bad debt at all costs!",
                    "content_hi": "अच्छा कर्ज: एजुकेशन लोन, होम लोन - जो आपको बढ़ाए। बुरा कर्ज: क्रेडिट कार्ड, शौक के लिए पर्सनल लोन, लोन ऐप। बुरे कर्ज से बचें!",
                    "icon": "⚖️"
                },
                {
                    "id": "emi_trap",
                    "title": "EMI Trap",
                    "title_hi": "EMI का जाल",
                    "content": "EMI = Equated Monthly Installment. It looks easy but adds up. Total EMIs should never exceed 30% of income. Before any EMI, ask: Can I wait and pay cash?",
                    "content_hi": "EMI = हर महीने की किस्त। आसान लगती है पर जुड़ती जाती है। कुल EMI आय के 30% से ज्यादा नहीं होनी चाहिए। किसी भी EMI से पहले सोचें: क्या कैश देकर खरीद सकता हूं?",
                    "icon": "⚠️"
                },
                {
                    "id": "credit_card_danger",
                    "title": "Credit Card - Use Wisely",
                    "title_hi": "क्रेडिट कार्ड - समझदारी से इस्तेमाल करें",
                    "content": "Credit card interest = 24-48% per year! Always pay full amount by due date. Minimum payment trap: ₹10,000 can become ₹25,000 in 3 years. Use for convenience, not for credit.",
                    "content_hi": "क्रेडिट कार्ड ब्याज = 24-48% सालाना! हमेशा पूरी रकम due date तक चुकाएं। Minimum payment का जाल: ₹10,000 3 साल में ₹25,000 हो सकता है। सुविधा के लिए इस्तेमाल करें, उधार के लिए नहीं।",
                    "icon": "💳"
                },
            ],
            "investment": [
                {
                    "id": "investment_basics",
                    "title": "Investment for Beginners",
                    "title_hi": "निवेश की शुरुआत",
                    "content": "Start with: 1) Emergency fund (3-6 months). 2) Health insurance. 3) Term insurance if family depends on you. 4) Then invest in PPF, FD, or SIP. Don't chase high returns - consistency wins.",
                    "content_hi": "शुरुआत करें: 1) इमरजेंसी फंड (3-6 महीने)। 2) हेल्थ इंश्योरेंस। 3) टर्म इंश्योरेंस अगर परिवार आप पर निर्भर है। 4) फिर PPF, FD, या SIP में निवेश। ज्यादा रिटर्न के पीछे न भागें।",
                    "icon": "📈"
                },
                {
                    "id": "sip_power",
                    "title": "Power of SIP",
                    "title_hi": "SIP की ताकत",
                    "content": "SIP = Systematic Investment Plan. Invest fixed amount monthly. ₹500/month in index fund for 20 years at 12% = ₹4.9 lakhs! Start with minimum amount, increase over time.",
                    "content_hi": "SIP = हर महीने fixed रकम invest करना। ₹500/महीने index fund में 20 साल, 12% पर = ₹4.9 लाख! minimum से शुरू करें, धीरे-धीरे बढ़ाएं।",
                    "icon": "💹"
                },
            ],
            "insurance": [
                {
                    "id": "health_insurance",
                    "title": "Health Insurance - Not Optional",
                    "title_hi": "हेल्थ इंश्योरेंस - जरूरी है",
                    "content": "1 hospital trip can wipe out savings of years. ₹300-500/month premium can cover ₹5-10 lakh treatment. Ayushman Bharat: Free for eligible families. Don't skip health cover!",
                    "content_hi": "1 बार हॉस्पिटल जाने पर सालों की बचत खत्म। ₹300-500/महीने का premium ₹5-10 लाख इलाज कवर कर सकता है। आयुष्मान भारत: eligible परिवारों के लिए free। हेल्थ कवर छोड़ें नहीं!",
                    "icon": "🏥"
                },
                {
                    "id": "term_insurance",
                    "title": "Term Insurance - Family Protection",
                    "title_hi": "टर्म इंश्योरेंस - परिवार की सुरक्षा",
                    "content": "If family depends on your income, get term insurance. Coverage = 10-15x annual income. ₹1 crore cover for ₹10,000-15,000/year. LIC endowment is NOT insurance, it's poor investment.",
                    "content_hi": "अगर परिवार आपकी आय पर निर्भर है तो term insurance लें। कवरेज = 10-15x सालाना आय। ₹1 करोड़ कवर ₹10,000-15,000/साल में। LIC endowment बीमा नहीं है, खराब निवेश है।",
                    "icon": "🛡️"
                },
            ]
        }
    
    def _load_scam_alerts(self) -> List[Dict]:
        """Common scams to be aware of"""
        return [
            {
                "id": "loan_app_scam",
                "title": "Instant Loan App Scam",
                "title_hi": "लोन ऐप स्कैम",
                "description": "Apps promising instant loans with no paperwork",
                "danger": "100-300% hidden interest, contacts harassment, photo blackmail",
                "how_to_avoid": "Never download unknown loan apps. Use only bank/NBFC apps.",
                "icon": "📱🚨"
            },
            {
                "id": "otp_scam",
                "title": "OTP/KYC Scam",
                "title_hi": "OTP/KYC स्कैम",
                "description": "Calls claiming to be from bank asking for OTP or KYC update",
                "danger": "Empty bank account in seconds",
                "how_to_avoid": "NEVER share OTP with anyone. Bank never asks for OTP on call.",
                "icon": "📞🚨"
            },
            {
                "id": "kyc_link_scam",
                "title": "KYC Update Link Scam",
                "title_hi": "KYC लिंक स्कैम",
                "description": "SMS/WhatsApp with link to update KYC",
                "danger": "Steals your bank login credentials",
                "how_to_avoid": "Never click links in SMS. Go directly to bank app/website.",
                "icon": "🔗🚨"
            },
            {
                "id": "job_scam",
                "title": "Work from Home Job Scam",
                "title_hi": "घर से काम का स्कैम",
                "description": "High paying work from home jobs asking for registration fee",
                "danger": "Lose money, personal data gets stolen",
                "how_to_avoid": "Real jobs never ask for payment. Research company first.",
                "icon": "💼🚨"
            },
            {
                "id": "double_money_scam",
                "title": "Double Money Scheme",
                "title_hi": "पैसा डबल स्कीम",
                "description": "Promises to double your money in weeks/months",
                "danger": "Ponzi scheme - you lose everything",
                "how_to_avoid": "If returns sound too good, it's a scam. 8-15% is realistic.",
                "icon": "💰🚨"
            },
            {
                "id": "lucky_draw_scam",
                "title": "Lottery/Lucky Draw Scam",
                "title_hi": "लॉटरी स्कैम",
                "description": "You won a prize! Pay processing fee to claim",
                "danger": "No real prize - just takes your money and info",
                "how_to_avoid": "You can't win a lottery you didn't enter. Ignore these.",
                "icon": "🎰🚨"
            },
        ]
    
    def _load_schemes(self) -> List[Dict]:
        """Government schemes for financial help"""
        return [
            {
                "id": "pmjdy",
                "name": "PM Jan Dhan Yojana",
                "name_hi": "पीएम जन धन योजना",
                "benefit": "Zero balance bank account with ₹2 lakh accident insurance, ₹30,000 life cover, overdraft facility",
                "for": ["all"],
                "how_to_apply": "Any bank branch with Aadhaar + photo"
            },
            {
                "id": "pmsby",
                "name": "PM Suraksha Bima Yojana",
                "name_hi": "पीएम सुरक्षा बीमा योजना",
                "benefit": "₹2 lakh accident insurance for just ₹20/year",
                "for": ["all"],
                "how_to_apply": "Any bank branch, auto-debit from account"
            },
            {
                "id": "pmjjby",
                "name": "PM Jeevan Jyoti Bima Yojana",
                "name_hi": "पीएम जीवन ज्योति बीमा योजना",
                "benefit": "₹2 lakh life insurance for ₹436/year",
                "for": ["all"],
                "how_to_apply": "Any bank branch, auto-debit from account"
            },
            {
                "id": "ayushman",
                "name": "Ayushman Bharat",
                "name_hi": "आयुष्मान भारत",
                "benefit": "₹5 lakh/year free health coverage for eligible families",
                "for": ["low_income_salaried", "daily_wage", "farmer"],
                "how_to_apply": "Check eligibility at pmjay.gov.in or any hospital"
            },
            {
                "id": "pmmy",
                "name": "PM Mudra Yojana",
                "name_hi": "पीएम मुद्रा योजना",
                "benefit": "Loans up to ₹10 lakh for small business without collateral",
                "for": ["small_vendor", "homemaker_earning", "skilled_worker"],
                "how_to_apply": "Any bank with business plan"
            },
            {
                "id": "sukanya",
                "name": "Sukanya Samriddhi Yojana",
                "name_hi": "सुकन्या समृद्धि योजना",
                "benefit": "8%+ interest, tax free - for girl child's education/marriage",
                "for": ["homemaker", "all_with_daughter"],
                "how_to_apply": "Post office or bank with birth certificate"
            },
            {
                "id": "atal_pension",
                "name": "Atal Pension Yojana",
                "name_hi": "अटल पेंशन योजना",
                "benefit": "Guaranteed pension ₹1000-5000/month after 60",
                "for": ["delivery_partner", "cab_driver", "daily_wage", "small_vendor"],
                "how_to_apply": "Any bank branch, early start = low contribution"
            },
            {
                "id": "pmay",
                "name": "PM Awas Yojana",
                "name_hi": "पीएम आवास योजना",
                "benefit": "Subsidy of ₹1.5-2.67 lakh on home loan interest",
                "for": ["low_income_salaried", "bpo_worker"],
                "how_to_apply": "Through housing finance company or pmaymis.gov.in"
            },
        ]
    
    def get_lesson(self, category: str = None, lesson_id: str = None) -> Dict:
        """Get a financial lesson"""
        
        if lesson_id:
            for cat, lessons in self.lessons.items():
                for lesson in lessons:
                    if lesson["id"] == lesson_id:
                        return lesson
            return None
        
        if category:
            lessons = self.lessons.get(category, [])
            return random.choice(lessons) if lessons else None
        
        # Random lesson
        all_lessons = []
        for lessons in self.lessons.values():
            all_lessons.extend(lessons)
        return random.choice(all_lessons)
    
    def get_all_categories(self) -> List[str]:
        return list(self.lessons.keys())
    
    def get_scam_alert(self, scam_id: str = None) -> Dict:
        """Get scam alert information"""
        
        if scam_id:
            for scam in self.scam_alerts:
                if scam["id"] == scam_id:
                    return scam
            return None
        
        return random.choice(self.scam_alerts)
    
    def get_relevant_schemes(self, user_type: str) -> List[Dict]:
        """Get government schemes relevant to user type"""
        
        relevant = []
        for scheme in self.government_schemes:
            if user_type in scheme["for"] or "all" in scheme["for"]:
                relevant.append(scheme)
        
        return relevant
    
    def get_daily_learning(self, user_id: str, language: str = "en") -> Dict:
        """Get daily learning content for user"""
        
        # Mix of lesson, tip, and scheme
        content_type = random.choice(["lesson", "lesson", "scam_alert", "scheme"])
        
        if content_type == "lesson":
            lesson = self.get_lesson()
            return {
                "type": "lesson",
                "icon": lesson["icon"],
                "title": lesson.get(f"title_{language[:2]}", lesson["title"]),
                "content": lesson.get(f"content_{language[:2]}", lesson["content"])
            }
        elif content_type == "scam_alert":
            scam = self.get_scam_alert()
            return {
                "type": "scam_alert",
                "icon": scam["icon"],
                "title": "⚠️ Scam Alert: " + scam.get(f"title_{language[:2]}", scam["title"]),
                "content": scam["danger"] + "\n\n✅ " + scam["how_to_avoid"]
            }
        else:
            scheme = random.choice(self.government_schemes)
            return {
                "type": "scheme",
                "icon": "🏛️",
                "title": scheme.get(f"name_{language[:2]}", scheme["name"]),
                "content": scheme["benefit"] + "\n\n📝 " + scheme["how_to_apply"]
            }


financial_literacy_service = FinancialLiteracyService()

