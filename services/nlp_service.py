"""
Advanced NLP Service
====================
Natural Language Processing for multi-language intent detection
Supports Hindi, Tamil, Telugu, and other Indian languages
"""

import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import SUPPORTED_LANGUAGES, INCOME_CATEGORIES, EXPENSE_CATEGORIES


class NLPService:
    """Advanced NLP for WhatsApp message understanding"""
    
    def __init__(self):
        self._load_intent_patterns()
        self._load_entity_patterns()
        self._load_language_mappings()
    
    def _load_intent_patterns(self):
        """Load intent detection patterns for multiple languages"""
        
        self.intent_patterns = {
            "GREETING": {
                "en": ["hi", "hello", "hey", "good morning", "good evening", "good night"],
                "hi": ["नमस्ते", "हेलो", "हाय", "सुप्रभात", "शुभ संध्या"],
                "ta": ["வணக்கம்", "ஹாய்", "ஹலோ", "காலை வணக்கம்"],
                "te": ["నమస్కారం", "హాయ్", "హలో", "శుభోదయం"],
            },
            "INCOME_ENTRY": {
                "en": ["earned", "received", "got", "income", "salary", "payment", "tips", "bonus", "cash received"],
                "hi": ["कमाया", "मिला", "आया", "सैलरी", "पेमेंट", "बोनस", "टिप", "आमदनी"],
                "ta": ["சம்பாதித்தேன்", "வாங்கினேன்", "கிடைத்தது", "சம்பளம்", "வருமானம்"],
                "te": ["సంపాదించాను", "వచ్చింది", "జీతం", "ఆదాయం", "బోనస్"],
            },
            "EXPENSE_ENTRY": {
                "en": ["spent", "paid", "expense", "bought", "purchase", "bill", "gave"],
                "hi": ["खर्च", "दिया", "खरीदा", "बिल", "भुगतान"],
                "ta": ["செலவு", "கொடுத்தேன்", "வாங்கினேன்", "பில்"],
                "te": ["ఖర్చు", "చెల్లించాను", "ఇచ్చాను", "బిల్"],
            },
            "SAVINGS_ENTRY": {
                "en": ["saved", "saving", "put aside", "emergency fund"],
                "hi": ["बचत", "बचाया", "जमा किया"],
                "ta": ["சேமிப்பு", "சேமித்தேன்"],
                "te": ["పొదుపు", "దాచాను"],
            },
            "LOAN_QUERY": {
                "en": ["loan", "emi", "borrow", "credit", "lending"],
                "hi": ["लोन", "कर्ज", "उधार", "ईएमआई"],
                "ta": ["கடன்", "இஎம்ஐ", "லோன்"],
                "te": ["లోన్", "అప్పు", "ఇఎంఐ"],
            },
            "INVESTMENT_QUERY": {
                "en": ["invest", "sip", "mutual fund", "stocks", "fd", "ppf", "nps"],
                "hi": ["निवेश", "सिप", "म्यूचुअल फंड", "शेयर", "एफडी"],
                "ta": ["முதலீடு", "சிப்", "மியூச்சுவல் ஃபண்ட்"],
                "te": ["పెట్టుబడి", "సిప్", "మ్యూచువల్ ఫండ్"],
            },
            "BUDGET_QUERY": {
                "en": ["budget", "limit", "allowance", "how much can i spend"],
                "hi": ["बजट", "खर्च सीमा", "कितना खर्च करूं"],
                "ta": ["பட்ஜெட்", "செலவு வரம்பு"],
                "te": ["బడ్జెట్", "ఖర్చు పరిమితి"],
            },
            "GOAL_QUERY": {
                "en": ["goal", "target", "saving for", "dream", "plan for"],
                "hi": ["लक्ष्य", "टारगेट", "सपना", "प्लान"],
                "ta": ["இலக்கு", "குறிக்கோள்", "கனவு"],
                "te": ["లక్ష్యం", "టార్గెట్", "కల"],
            },
            "SUMMARY_QUERY": {
                "en": ["summary", "report", "how much", "balance", "total", "this month", "today"],
                "hi": ["सारांश", "रिपोर्ट", "कितना", "बैलेंस", "आज", "इस महीने"],
                "ta": ["சுருக்கம்", "ரிப்போர்ட்", "எவ்வளவு", "இன்று", "இந்த மாதம்"],
                "te": ["సారాంశం", "రిపోర్ట్", "ఎంత", "ఈరోజు", "ఈ నెల"],
            },
            "HELP_QUERY": {
                "en": ["help", "what can you do", "how to", "guide", "tutorial"],
                "hi": ["मदद", "क्या कर सकते हो", "कैसे करें"],
                "ta": ["உதவி", "என்ன செய்ய முடியும்", "எப்படி"],
                "te": ["సహాయం", "ఏమి చేయగలవు", "ఎలా"],
            },
            "FRAUD_REPORT": {
                "en": ["fraud", "scam", "cheated", "stolen", "suspicious", "unauthorized"],
                "hi": ["धोखा", "फ्रॉड", "चोरी", "धोखाधड़ी"],
                "ta": ["மோசடி", "ஏமாற்றம்", "திருட்டு"],
                "te": ["మోసం", "దొంగతనం", "నమ్మకద్రోహం"],
            },
            "ADVICE_REQUEST": {
                "en": ["advice", "suggest", "recommend", "what should i do", "help me plan"],
                "hi": ["सलाह", "सुझाव", "क्या करूं", "प्लान बनाओ"],
                "ta": ["ஆலோசனை", "பரிந்துரை", "என்ன செய்ய"],
                "te": ["సలహా", "సూచన", "ఏమి చేయాలి"],
            },
            "DASHBOARD_QUERY": {
                "en": ["dashboard", "monthly report", "monthly summary", "this month", "monthly", "how did i do"],
                "hi": ["डैशबोर्ड", "मासिक रिपोर्ट", "इस महीने", "महीने की रिपोर्ट"],
                "ta": ["டாஷ்போர்ட்", "மாத அறிக்கை", "இந்த மாதம்"],
                "te": ["డాష్‌బోర్డ్", "నెలవారీ రిపోర్ట్", "ఈ నెల"],
            },
            "LEARN_QUERY": {
                "en": ["learn", "teach", "explain", "what is", "how does", "educate", "literacy"],
                "hi": ["सिखाओ", "बताओ", "क्या है", "कैसे होता है", "समझाओ"],
                "ta": ["கற்றுக்கொள்ள", "என்ன", "எப்படி"],
                "te": ["నేర్చుకో", "ఏమిటి", "ఎలా"],
            },
            "CHALLENGE_QUERY": {
                "en": ["challenge", "52 week", "savings challenge", "game"],
                "hi": ["चैलेंज", "बचत चैलेंज", "52 हफ्ते"],
                "ta": ["சவால்", "சேமிப்பு சவால்"],
                "te": ["ఛాలెంజ్", "పొదుపు ఛాలెంజ్"],
            },
            "BILL_QUERY": {
                "en": ["bill", "bills", "reminder", "due", "payment due", "upcoming bills"],
                "hi": ["बिल", "रिमाइंडर", "ड्यू", "भुगतान"],
                "ta": ["பில்", "நினைவூட்டல்", "செலுத்த வேண்டும்"],
                "te": ["బిల్", "రిమైండర్", "చెల్లింపు"],
            },
        }
    
    def _load_entity_patterns(self):
        """Load entity extraction patterns"""
        
        self.amount_patterns = [
            r"₹\s*([\d,]+(?:\.\d{2})?)",
            r"rs\.?\s*([\d,]+(?:\.\d{2})?)",
            r"([\d,]+)\s*(?:rupees?|rs\.?|₹)",
            r"\b([\d,]+)\b",  # Just numbers as fallback
        ]
        
        self.category_keywords = {
            # Income categories
            "delivery_tips": ["tip", "tips", "टिप", "குறிப்பு", "టిప్"],
            "delivery_earnings": ["delivery", "swiggy", "zomato", "डिलीवरी", "டெலிவரி"],
            "salary": ["salary", "salaried", "सैलरी", "சம்பளம்", "జీతం"],
            "freelance": ["freelance", "project", "client payment", "फ्रीलांस"],
            "bonus": ["bonus", "incentive", "बोनस", "போனஸ்", "బోనస్"],
            
            # Expense categories
            "food": ["food", "lunch", "dinner", "breakfast", "खाना", "உணவு", "భోజనం", "biryani", "tea", "coffee"],
            "transport": ["petrol", "fuel", "bus", "auto", "cab", "metro", "पेट्रोल", "பெட்ரோல்"],
            "rent": ["rent", "किराया", "வாடகை", "అద్దె"],
            "utilities": ["electricity", "water", "gas", "bill", "बिजली", "மின்சாரம்"],
            "healthcare": ["medicine", "doctor", "hospital", "दवाई", "மருந்து", "மருத்துவர்"],
            "education": ["school", "tuition", "books", "स्कूल", "பள்ளி"],
            "entertainment": ["movie", "netflix", "game", "फिल्म", "படம்"],
            "shopping": ["clothes", "shopping", "amazon", "flipkart", "खरीदारी"],
            "mobile_recharge": ["recharge", "mobile", "data", "रिचार्ज", "ரீசார்ஜ்"],
        }
        
        self.time_patterns = {
            "today": ["today", "आज", "இன்று", "ఈరోజు"],
            "yesterday": ["yesterday", "कल", "நேற்று", "నిన్న"],
            "this_week": ["this week", "इस हफ्ते", "இந்த வாரம்"],
            "this_month": ["this month", "इस महीने", "இந்த மாதம்", "ఈ నెల"],
            "last_month": ["last month", "पिछले महीने", "கடந்த மாதம்"],
        }
    
    def _load_language_mappings(self):
        """Load common words that help detect language"""
        
        self.language_indicators = {
            "hi": ["है", "हूं", "का", "की", "के", "में", "को", "से", "ने", "और", "यह", "था", "हैं", "मैं", "मुझे"],
            "ta": ["இது", "அது", "என்", "உன்", "நான்", "நீ", "ஒரு", "என்ன", "எப்படி", "ஏன்", "யார்"],
            "te": ["ఇది", "అది", "నేను", "నీవు", "ఏమి", "ఎలా", "ఎందుకు", "మీరు", "మా", "మీ"],
            "kn": ["ಇದು", "ಅದು", "ನಾನು", "ನೀನು", "ಏನು", "ಹೇಗೆ", "ಯಾಕೆ"],
            "ml": ["ഇത്", "അത്", "ഞാൻ", "നീ", "എന്ത്", "എങ്ങനെ", "എന്തുകൊണ്ട്"],
        }
    
    def detect_language(self, text: str) -> str:
        """Detect language from text"""
        
        text_lower = text.lower()
        
        # Check for language-specific characters
        if re.search(r'[\u0900-\u097F]', text):  # Devanagari (Hindi)
            return "hi"
        if re.search(r'[\u0B80-\u0BFF]', text):  # Tamil
            return "ta"
        if re.search(r'[\u0C00-\u0C7F]', text):  # Telugu
            return "te"
        if re.search(r'[\u0C80-\u0CFF]', text):  # Kannada
            return "kn"
        if re.search(r'[\u0D00-\u0D7F]', text):  # Malayalam
            return "ml"
        if re.search(r'[\u0A80-\u0AFF]', text):  # Gujarati
            return "gu"
        if re.search(r'[\u0A00-\u0A7F]', text):  # Gurmukhi (Punjabi)
            return "pa"
        if re.search(r'[\u0980-\u09FF]', text):  # Bengali
            return "bn"
        if re.search(r'[\u0B00-\u0B7F]', text):  # Oriya
            return "or"
        
        # Default to English
        return "en"
    
    def detect_intent(self, text: str, user_language: str = None) -> Dict:
        """Detect user intent from message"""
        
        text_lower = text.lower().strip()
        detected_language = user_language or self.detect_language(text)
        
        # Extract amount first
        amount = self.extract_amount(text)
        category = self.extract_category(text, detected_language)
        time_ref = self.extract_time_reference(text)
        
        # Check each intent pattern
        intent_scores = {}
        
        for intent, lang_patterns in self.intent_patterns.items():
            score = 0
            
            # Check patterns in detected language
            if detected_language in lang_patterns:
                for pattern in lang_patterns[detected_language]:
                    if pattern.lower() in text_lower:
                        score += 2
            
            # Also check English (as fallback)
            if detected_language != "en" and "en" in lang_patterns:
                for pattern in lang_patterns["en"]:
                    if pattern.lower() in text_lower:
                        score += 1
            
            if score > 0:
                intent_scores[intent] = score
        
        # Determine best intent
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[best_intent] / 4, 1.0)  # Normalize to 0-1
        else:
            best_intent = "UNKNOWN"
            confidence = 0.0
        
        # Determine entry type for income/expense
        entry_type = None
        if best_intent == "INCOME_ENTRY":
            entry_type = "income"
        elif best_intent == "EXPENSE_ENTRY":
            entry_type = "expense"
        elif best_intent == "SAVINGS_ENTRY":
            entry_type = "savings"
        
        return {
            "intent": best_intent,
            "confidence": round(confidence, 2),
            "language": detected_language,
            "amount": amount,
            "category": category,
            "entry_type": entry_type,
            "time_reference": time_ref,
            "original_text": text,
        }
    
    def extract_amount(self, text: str) -> Optional[int]:
        """Extract monetary amount from text"""
        
        text_cleaned = text.replace(",", "")
        
        for pattern in self.amount_patterns:
            match = re.search(pattern, text_cleaned, re.IGNORECASE)
            if match:
                try:
                    amount_str = match.group(1).replace(",", "")
                    return int(float(amount_str))
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def extract_category(self, text: str, language: str = "en") -> Optional[str]:
        """Extract expense/income category from text"""
        
        text_lower = text.lower()
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return category
        
        return "other_income" if self.is_income_context(text) else "other_expense"
    
    def is_income_context(self, text: str) -> bool:
        """Check if text is in income context"""
        
        income_words = ["earned", "received", "got", "income", "salary", "कमाया", "मिला", 
                       "சம்பாதித்தேன்", "వచ్చింది", "credit", "credited"]
        
        text_lower = text.lower()
        return any(word in text_lower for word in income_words)
    
    def extract_time_reference(self, text: str) -> Optional[str]:
        """Extract time reference from text"""
        
        text_lower = text.lower()
        
        for time_ref, keywords in self.time_patterns.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return time_ref
        
        return "today"  # Default to today
    
    def parse_onboarding_response(self, text: str, step: str, language: str = "en") -> Dict:
        """Parse user response during onboarding"""
        
        text_clean = text.strip()
        
        if step == "NAME":
            # Extract name - take first few words, remove numbers
            name = re.sub(r'[0-9]', '', text_clean)
            name = ' '.join(name.split()[:3])  # Max 3 words
            return {"name": name.title() if name else None}
        
        elif step == "LANGUAGE":
            # Map to language code
            lang_map = {
                "1": "en", "english": "en", "eng": "en",
                "2": "hi", "hindi": "hi", "हिंदी": "hi",
                "3": "ta", "tamil": "ta", "தமிழ்": "ta",
                "4": "te", "telugu": "te", "తెలుగు": "te",
                "5": "kn", "kannada": "kn", "ಕನ್ನಡ": "kn",
                "6": "ml", "malayalam": "ml", "മലയാളം": "ml",
            }
            code = lang_map.get(text_clean.lower(), "en")
            return {"language": code}
        
        elif step == "PROFESSION" or step == "USER_TYPE":
            # Categorize user type based on keywords
            user_type_keywords = {
                # Gig workers
                "delivery_partner": ["delivery", "swiggy", "zomato", "amazon", "flipkart", "dunzo", "डिलीवरी", "டெலிவரி"],
                "cab_driver": ["uber", "ola", "rapido", "driver", "taxi", "auto", "ड्राइवर", "டிரைவர்", "డ్రైవర్"],
                
                # Students
                "student": ["student", "college", "university", "studying", "छात्र", "पढ़ाई", "மாணவர்", "విద్యార్థి"],
                "student_working": ["part time", "parttime", "intern", "internship", "पार्ट टाइम"],
                
                # Homemakers
                "homemaker": ["housewife", "homemaker", "home maker", "गृहिणी", "housekeeping", "இல்லத்தரசி"],
                "homemaker_earning": ["tiffin", "tailoring", "tuition", "टिफिन", "सिलाई", "ट्यूशन"],
                
                # BPO
                "bpo_worker": ["bpo", "call center", "customer support", "back office", "कॉल सेंटर"],
                "retail_worker": ["retail", "mall", "shop assistant", "salesman", "salesgirl", "दुकान"],
                
                # Small business
                "small_vendor": ["vendor", "shop", "kirana", "store", "दुकान", "merchant", "selling"],
                "skilled_worker": ["electrician", "plumber", "carpenter", "mechanic", "tailor", "कारीगर", "मिस्त्री"],
                
                # Daily/Low income
                "daily_wage": ["labour", "labor", "construction", "mazdoor", "मज़दूर", "கூலி"],
                "low_income_salaried": ["guard", "security", "helper", "peon", "domestic", "चौकीदार", "हेल्पर"],
                
                # Others
                "pensioner": ["pension", "retired", "retirement", "पेंशन", "रिटायर"],
                "farmer": ["farmer", "farming", "kisaan", "किसान", "खेती", "விவசாயி"],
                "freelancer": ["freelance", "freelancer", "consultant", "project", "client", "फ्रीलांस"],
            }
            
            text_lower = text_clean.lower()
            detected_type = "other"
            
            for user_type, keywords in user_type_keywords.items():
                if any(k in text_lower for k in keywords):
                    detected_type = user_type
                    break
            
            # Fallback classification
            if detected_type == "other":
                if "salary" in text_lower or "job" in text_lower or "employee" in text_lower:
                    detected_type = "low_income_salaried"
                elif "business" in text_lower:
                    detected_type = "small_vendor"
            
            return {"profession": text_clean, "user_type": detected_type}
        
        elif step == "MONTHLY_INCOME":
            amount = self.extract_amount(text_clean)
            return {"monthly_income": amount or 0}
        
        elif step == "DEPENDENTS":
            # Extract number
            numbers = re.findall(r'\d+', text_clean)
            count = int(numbers[0]) if numbers else 0
            return {"dependents": min(count, 20)}  # Cap at 20
        
        elif step == "CURRENT_SAVINGS":
            amount = self.extract_amount(text_clean)
            return {"savings": amount or 0}
        
        elif step == "CURRENT_DEBT":
            amount = self.extract_amount(text_clean)
            # Check for "no" or "0"
            if text_lower := text_clean.lower():
                if any(w in text_lower for w in ["no", "none", "0", "नहीं", "இல்லை", "లేదు"]):
                    amount = 0
            return {"debt": amount or 0}
        
        elif step == "GOALS":
            # Extract goals from text
            goals = []
            goal_keywords = {
                "emergency": "emergency_fund",
                "debt": "debt_freedom",
                "loan": "debt_freedom",
                "child": "child_education",
                "education": "child_education",
                "home": "home_purchase",
                "house": "home_purchase",
                "vehicle": "vehicle_purchase",
                "bike": "vehicle_purchase",
                "car": "vehicle_purchase",
                "wedding": "wedding",
                "marriage": "wedding",
                "retire": "retirement",
                "vacation": "vacation",
                "travel": "vacation",
                "business": "business",
            }
            
            text_lower = text_clean.lower()
            for keyword, goal in goal_keywords.items():
                if keyword in text_lower and goal not in goals:
                    goals.append(goal)
            
            if not goals:
                goals = ["emergency_fund"]  # Default goal
            
            return {"goals": goals}
        
        return {}


# Global instance
nlp_service = NLPService()
