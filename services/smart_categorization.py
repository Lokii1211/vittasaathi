"""
Smart Expense Categorization
============================
Auto-categorize expenses using keywords, patterns, and learning
"""
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict
import re
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import EXPENSE_CATEGORIES, INCOME_CATEGORIES


class SmartCategorizationService:
    """Intelligent expense categorization"""
    
    def __init__(self):
        self._build_keyword_index()
        self.user_patterns = defaultdict(lambda: defaultdict(int))  # user_id -> {keyword: category}
    
    def _build_keyword_index(self):
        """Build keyword to category mapping"""
        
        # Expense keywords (most specific first)
        self.expense_keywords = {
            # Food & Groceries
            "food": {
                "keywords": ["biryani", "pizza", "burger", "chai", "tea", "coffee", "lunch", "dinner", 
                            "breakfast", "snack", "food", "meal", "khana", "nashta", "roti", "daal",
                            "rice", "chawal", "sabzi", "thali", "restaurant", "hotel", "dhaba",
                            "mess", "canteen", "tiffin", "samosa", "pakora", "vada pav", "dosa",
                            "idli", "paratha", "naan", "paneer", "chicken", "mutton", "fish",
                            "biriyani", "momos", "chowmein", "maggi"],
                "patterns": [r"(?:zomato|swiggy)\s*order", r"mess\s*(?:bill|fee)"]
            },
            "vegetables": {
                "keywords": ["sabzi", "vegetable", "vegetables", "tamatar", "pyaz", "aloo", "gobhi",
                            "palak", "matar", "bhindi", "baingan", "fruit", "fruits", "aam", "kela",
                            "apple", "banana", "mango", "onion", "potato", "tomato", "सब्जी", "फल"],
                "patterns": [r"sabzi\s*wala", r"mandi"]
            },
            "milk_dairy": {
                "keywords": ["milk", "doodh", "curd", "dahi", "paneer", "butter", "ghee", "cheese",
                            "cream", "lassi", "chaach", "amul", "mother dairy", "दूध", "दही"],
                "patterns": [r"dairy", r"amul\s*parlour"]
            },
            "groceries": {
                "keywords": ["grocery", "groceries", "kirana", "ration", "sugar", "cheeni", "oil",
                            "tel", "atta", "dal", "rice", "chawal", "spices", "masala", "salt",
                            "namak", "soap", "detergent", "shampoo", "toothpaste", "किराना"],
                "patterns": [r"d\s*mart", r"big\s*bazaar", r"reliance\s*fresh", r"super\s*market"]
            },
            
            # Transport
            "petrol": {
                "keywords": ["petrol", "diesel", "fuel", "cng", "gas", "पेट्रोल", "डीज़ल"],
                "patterns": [r"(?:hp|bp|indian\s*oil|iocl|bpcl)\s*pump", r"fuel\s*station"]
            },
            "transport": {
                "keywords": ["auto", "bus", "metro", "train", "cab", "ola", "uber", "rapido",
                            "taxi", "rickshaw", "ऑटो", "बस", "मेट्रो", "ट्रेन"],
                "patterns": [r"(?:ola|uber|rapido)\s*(?:ride|trip)"]
            },
            "vehicle_maintenance": {
                "keywords": ["service", "repair", "puncture", "tyre", "tire", "battery", "mechanic",
                            "garage", "मरम्मत", "पंचर"],
                "patterns": [r"(?:bike|car|scooter|vehicle)\s*(?:service|repair)"]
            },
            
            # Utilities
            "utilities": {
                "keywords": ["electricity", "water", "bijli", "pani", "bill", "बिजली", "पानी"],
                "patterns": [r"(?:electricity|water|power)\s*bill"]
            },
            "gas": {
                "keywords": ["cylinder", "lpg", "gas", "indane", "bharat gas", "hp gas", "गैस"],
                "patterns": [r"gas\s*cylinder", r"lpg\s*refill"]
            },
            "mobile_recharge": {
                "keywords": ["recharge", "mobile", "prepaid", "postpaid", "data", "रिचार्ज"],
                "patterns": [r"(?:jio|airtel|vi|bsnl)\s*recharge"]
            },
            "internet": {
                "keywords": ["wifi", "broadband", "internet", "fiber", "इंटरनेट"],
                "patterns": [r"(?:jio|airtel|act|bsnl)\s*(?:fiber|broadband)"]
            },
            
            # Housing
            "rent": {
                "keywords": ["rent", "kiraya", "housing", "किराया"],
                "patterns": [r"(?:room|house|flat|pg)\s*rent"]
            },
            
            # Health
            "medicine": {
                "keywords": ["medicine", "tablet", "syrup", "pharmacy", "medical", "dawai", "दवाई", "दवा"],
                "patterns": [r"(?:apollo|medplus|netmeds)\s*pharmacy"]
            },
            "doctor": {
                "keywords": ["doctor", "hospital", "clinic", "checkup", "treatment", "test", 
                            "डॉक्टर", "हॉस्पिटल"],
                "patterns": [r"(?:blood|urine|x\s*ray)\s*test", r"opd\s*(?:fee|charge)"]
            },
            
            # Education
            "school_fees": {
                "keywords": ["school", "college", "university", "fees", "admission", "स्कूल", "कॉलेज"],
                "patterns": [r"(?:school|college|university)\s*fee"]
            },
            "books_stationery": {
                "keywords": ["book", "books", "notebook", "pen", "pencil", "stationery", "किताब"],
                "patterns": [r"text\s*book"]
            },
            "tuition_fees": {
                "keywords": ["tuition", "coaching", "classes", "ट्यूशन", "कोचिंग"],
                "patterns": [r"(?:tuition|coaching)\s*(?:fee|class)"]
            },
            
            # Shopping
            "clothes": {
                "keywords": ["clothes", "shirt", "pant", "jeans", "saree", "kurta", "dress", "kapda", "कपड़े"],
                "patterns": [r"(?:myntra|ajio|flipkart|amazon)\s*order"]
            },
            "shopping": {
                "keywords": ["shopping", "amazon", "flipkart", "online", "शॉपिंग"],
                "patterns": [r"(?:amazon|flipkart|meesho)\s*(?:order|purchase)"]
            },
            
            # Entertainment
            "entertainment": {
                "keywords": ["movie", "cinema", "pvr", "inox", "netflix", "prime", "hotstar", 
                            "game", "pubg", "फिल्म", "मूवी"],
                "patterns": [r"(?:netflix|prime|hotstar|zee5)\s*subscription"]
            },
            "eating_out": {
                "keywords": ["restaurant", "cafe", "bar", "party", "outing", "पार्टी"],
                "patterns": [r"(?:friends|family)\s*(?:treat|party|outing)"]
            },
            
            # EMI & Loans
            "emi": {
                "keywords": ["emi", "loan", "installment", "किस्त", "लोन"],
                "patterns": [r"(?:loan|emi)\s*payment"]
            },
            "credit_card": {
                "keywords": ["credit card", "cc", "क्रेडिट कार्ड"],
                "patterns": [r"credit\s*card\s*(?:bill|payment)"]
            },
            
            # Family
            "children": {
                "keywords": ["toy", "toys", "baby", "diaper", "formula", "बच्चे"],
                "patterns": [r"(?:baby|kid|child)\s*(?:food|clothes|toys)"]
            },
            "family_support": {
                "keywords": ["family", "parents", "send home", "परिवार", "घर भेजा"],
                "patterns": [r"(?:money|amount)\s*(?:sent|transfer)\s*(?:home|family)"]
            },
            
            # Religious & Social
            "religious": {
                "keywords": ["temple", "mandir", "puja", "prasad", "gurudwara", "mosque", "church",
                            "donation", "मंदिर", "पूजा"],
                "patterns": [r"(?:temple|mandir|gurudwara)\s*(?:donation|visit)"]
            },
            "gifts": {
                "keywords": ["gift", "shagun", "wedding", "birthday", "गिफ्ट", "शगुन", "शादी"],
                "patterns": [r"(?:wedding|birthday|party)\s*gift"]
            },
        }
        
        # Income keywords
        self.income_keywords = {
            "delivery_earnings": {
                "keywords": ["swiggy", "zomato", "amazon", "flipkart", "dunzo", "delivery", "डिलीवरी"],
                "patterns": [r"(?:swiggy|zomato|amazon)\s*(?:earning|payment)"]
            },
            "ride_earnings": {
                "keywords": ["uber", "ola", "rapido", "ride", "trip", "राइड"],
                "patterns": [r"(?:uber|ola|rapido)\s*(?:earning|payment)"]
            },
            "tips": {
                "keywords": ["tip", "tips", "bonus", "टिप", "बोनस"],
                "patterns": []
            },
            "incentive": {
                "keywords": ["incentive", "bonus", "reward", "इंसेंटिव"],
                "patterns": [r"weekly\s*(?:incentive|bonus)"]
            },
            "salary": {
                "keywords": ["salary", "wages", "सैलरी", "तनख्वाह"],
                "patterns": [r"(?:monthly|weekly)\s*salary"]
            },
            "freelance": {
                "keywords": ["project", "client", "freelance", "payment", "फ्रीलांस"],
                "patterns": [r"(?:project|client)\s*payment"]
            },
            "pocket_money": {
                "keywords": ["pocket money", "allowance", "जेब खर्च", "भत्ता"],
                "patterns": []
            },
            "tuition_income": {
                "keywords": ["tuition", "teaching", "class", "student", "ट्यूशन"],
                "patterns": [r"tuition\s*(?:fee|earning)"]
            },
            "rent_received": {
                "keywords": ["rent received", "tenant", "किराया मिला"],
                "patterns": []
            },
            "government_benefit": {
                "keywords": ["pension", "subsidy", "dbt", "pm kisan", "पेंशन", "सब्सिडी"],
                "patterns": [r"(?:govt|government)\s*(?:payment|benefit)"]
            }
        }
    
    def categorize(self, text: str, transaction_type: str = "expense", user_id: str = None) -> Tuple[str, float]:
        """
        Categorize transaction based on description
        Returns: (category, confidence)
        """
        
        text_lower = text.lower()
        
        # Choose keyword set based on type
        keywords_dict = self.expense_keywords if transaction_type == "expense" else self.income_keywords
        
        best_category = None
        best_score = 0
        
        for category, data in keywords_dict.items():
            score = 0
            
            # Check keywords
            for keyword in data["keywords"]:
                if keyword.lower() in text_lower:
                    score += 2
            
            # Check patterns
            for pattern in data.get("patterns", []):
                if re.search(pattern, text_lower, re.IGNORECASE):
                    score += 3
            
            # Check user's past patterns
            if user_id and category in self.user_patterns.get(user_id, {}):
                score += self.user_patterns[user_id][category] * 0.5
            
            if score > best_score:
                best_score = score
                best_category = category
        
        # Calculate confidence
        if best_score >= 5:
            confidence = 0.95
        elif best_score >= 3:
            confidence = 0.80
        elif best_score >= 2:
            confidence = 0.60
        else:
            confidence = 0.30
            best_category = f"other_{transaction_type}"
        
        return best_category, confidence
    
    def learn_from_user(self, user_id: str, text: str, category: str):
        """Learn from user's manual categorization"""
        
        # Extract keywords from text
        words = text.lower().split()
        for word in words:
            if len(word) > 3:  # Skip short words
                self.user_patterns[user_id][category] += 1
    
    def get_category_suggestions(self, text: str, transaction_type: str = "expense", top_n: int = 3) -> List[Dict]:
        """Get top category suggestions with confidence scores"""
        
        text_lower = text.lower()
        keywords_dict = self.expense_keywords if transaction_type == "expense" else self.income_keywords
        
        scores = []
        
        for category, data in keywords_dict.items():
            score = 0
            matched_keywords = []
            
            for keyword in data["keywords"]:
                if keyword.lower() in text_lower:
                    score += 2
                    matched_keywords.append(keyword)
            
            for pattern in data.get("patterns", []):
                if re.search(pattern, text_lower, re.IGNORECASE):
                    score += 3
            
            if score > 0:
                cat_info = EXPENSE_CATEGORIES.get(category, {}) if transaction_type == "expense" else INCOME_CATEGORIES.get(category, {})
                scores.append({
                    "category": category,
                    "name": cat_info.get("name", category.title()),
                    "icon": cat_info.get("icon", "📦"),
                    "score": score,
                    "confidence": min(score / 6, 1.0),
                    "matched": matched_keywords[:3]
                })
        
        # Sort by score
        scores.sort(key=lambda x: x["score"], reverse=True)
        
        return scores[:top_n]
    
    def get_all_categories(self, transaction_type: str = "expense") -> List[Dict]:
        """Get all categories for selection"""
        
        if transaction_type == "expense":
            return [
                {"category": cat, "name": info.get("name", cat.title()), "icon": info.get("icon", "📦")}
                for cat, info in EXPENSE_CATEGORIES.items()
            ]
        else:
            return [
                {"category": cat, "name": info.get("name", cat.title()), "icon": info.get("icon", "💰")}
                for cat, info in INCOME_CATEGORIES.items()
            ]


class QuickActionService:
    """Quick actions and shortcuts for common tasks"""
    
    def __init__(self):
        self.shortcuts = self._load_shortcuts()
    
    def _load_shortcuts(self) -> Dict:
        return {
            # Expense shortcuts
            "chai": {"type": "expense", "category": "food", "default_amount": 20, "icon": "☕"},
            "auto": {"type": "expense", "category": "transport", "default_amount": 50, "icon": "🛺"},
            "petrol": {"type": "expense", "category": "petrol", "default_amount": 500, "icon": "⛽"},
            "lunch": {"type": "expense", "category": "food", "default_amount": 100, "icon": "🍽️"},
            "dinner": {"type": "expense", "category": "food", "default_amount": 150, "icon": "🍽️"},
            "recharge": {"type": "expense", "category": "mobile_recharge", "default_amount": 199, "icon": "📱"},
            "groceries": {"type": "expense", "category": "groceries", "default_amount": 500, "icon": "🛒"},
            "medicine": {"type": "expense", "category": "medicine", "default_amount": 200, "icon": "💊"},
            
            # Income shortcuts
            "delivery": {"type": "income", "category": "delivery_earnings", "icon": "🛵"},
            "ride": {"type": "income", "category": "ride_earnings", "icon": "🚗"},
            "tip": {"type": "income", "category": "tips", "icon": "💝"},
            "salary": {"type": "income", "category": "salary", "icon": "💼"},
            "tuition": {"type": "income", "category": "tuition_income", "icon": "📚"},
            
            # Hindi shortcuts
            "चाय": {"type": "expense", "category": "food", "default_amount": 20, "icon": "☕"},
            "खाना": {"type": "expense", "category": "food", "default_amount": 100, "icon": "🍽️"},
            "पेट्रोल": {"type": "expense", "category": "petrol", "default_amount": 500, "icon": "⛽"},
            "ऑटो": {"type": "expense", "category": "transport", "default_amount": 50, "icon": "🛺"},
            "रिचार्ज": {"type": "expense", "category": "mobile_recharge", "default_amount": 199, "icon": "📱"},
            "दवाई": {"type": "expense", "category": "medicine", "default_amount": 200, "icon": "💊"},
            "किराना": {"type": "expense", "category": "groceries", "default_amount": 500, "icon": "🛒"},
            "टिप": {"type": "income", "category": "tips", "icon": "💝"},
            "सैलरी": {"type": "income", "category": "salary", "icon": "💼"},
        }
    
    def parse_quick_action(self, text: str) -> Optional[Dict]:
        """Parse quick action from text"""
        
        text_lower = text.lower().strip()
        words = text_lower.split()
        
        for word in words:
            if word in self.shortcuts:
                shortcut = self.shortcuts[word].copy()
                
                # Try to extract amount
                amount = self._extract_amount(text)
                if amount:
                    shortcut["amount"] = amount
                elif "default_amount" in shortcut:
                    shortcut["amount"] = shortcut["default_amount"]
                
                shortcut["source_word"] = word
                return shortcut
        
        return None
    
    def _extract_amount(self, text: str) -> Optional[int]:
        """Extract amount from text"""
        
        # Remove commas
        text_clean = text.replace(",", "")
        
        # Try various patterns
        patterns = [
            r"₹\s*(\d+)",
            r"rs\.?\s*(\d+)",
            r"(\d+)\s*(?:rupees?|rs\.?|₹)",
            r"(\d+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        
        return None
    
    def get_suggestions(self, last_transactions: List[Dict], time_of_day: str = None) -> List[Dict]:
        """Get smart action suggestions based on context"""
        
        suggestions = []
        
        # Time-based suggestions
        from datetime import datetime
        hour = datetime.now().hour
        
        if 7 <= hour < 10:
            suggestions.append({
                "text": "☕ Add chai expense",
                "action": "chai 20",
                "icon": "☕"
            })
            suggestions.append({
                "text": "🍳 Add breakfast",
                "action": "breakfast 50",
                "icon": "🍳"
            })
        elif 12 <= hour < 15:
            suggestions.append({
                "text": "🍽️ Add lunch",
                "action": "lunch 100",
                "icon": "🍽️"
            })
        elif 19 <= hour < 22:
            suggestions.append({
                "text": "🍽️ Add dinner",
                "action": "dinner 150",
                "icon": "🍽️"
            })
        
        # Add common actions
        suggestions.extend([
            {"text": "⛽ Add petrol", "action": "petrol", "icon": "⛽"},
            {"text": "🛺 Add auto fare", "action": "auto", "icon": "🛺"},
            {"text": "📊 View summary", "action": "summary", "icon": "📊"},
        ])
        
        return suggestions[:5]


# Global instances
smart_categorization = SmartCategorizationService()
quick_actions = QuickActionService()
