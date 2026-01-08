"""
User Repository - Complete user management with onboarding
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import USERS_DB_FILE, ONBOARDING_STEPS, SUPPORTED_LANGUAGES
from database.json_store import JSONStore


class UserRepository:
    """Complete user management with onboarding, preferences, and profiles"""
    
    def __init__(self):
        self.store = JSONStore(USERS_DB_FILE)
    
    def get_user(self, phone: str) -> Optional[Dict]:
        """Get user by phone number"""
        return self.store.get(phone)
    
    def create_user(self, phone: str) -> Dict:
        """Create new user with initial onboarding state"""
        user = {
            "phone": phone,
            "name": None,
            "language": "en",
            "voice_enabled": True,
            "onboarding_step": "NAME",
            "onboarding_complete": False,
            
            # Profile
            "profession": None,
            "profession_type": None,  # salaried, freelance, gig_worker, business
            "monthly_income_estimate": 0,
            "income_type": "irregular",  # regular, irregular
            "dependents": 0,
            
            # Financial Status
            "current_savings": 0,
            "current_debt": 0,
            "debt_details": [],
            "emergency_fund": 0,
            
            # Goals
            "goals": [],
            "primary_goal": None,
            
            # Preferences
            "reminder_time": "09:00",
            "weekly_report_day": "Sunday",
            "currency": "INR",
            
            # Stats
            "total_income_recorded": 0,
            "total_expense_recorded": 0,
            "streak_days": 0,
            "last_active": datetime.now().isoformat(),
            "first_seen": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self.store.set(phone, user)
        return user
    
    def ensure_user(self, phone: str) -> Dict:
        """Get or create user"""
        user = self.get_user(phone)
        if not user:
            user = self.create_user(phone)
        return user
    
    def update_user(self, phone: str, updates: Dict) -> Optional[Dict]:
        """Update user fields"""
        return self.store.update(phone, updates)
    
    def save_name(self, phone: str, name: str) -> Dict:
        """Save user name and advance onboarding"""
        user = self.ensure_user(phone)
        updates = {
            "name": name,
            "onboarding_step": "LANGUAGE",
            "updated_at": datetime.now().isoformat()
        }
        return self.store.update(phone, updates)
    
    def save_language(self, phone: str, language: str) -> Dict:
        """Save language preference"""
        if language not in SUPPORTED_LANGUAGES:
            language = "en"
        
        updates = {
            "language": language,
            "onboarding_step": "PROFESSION",
            "updated_at": datetime.now().isoformat()
        }
        return self.store.update(phone, updates)
    
    def save_profession(self, phone: str, profession: str, profession_type: str) -> Dict:
        """Save profession details"""
        income_type = "regular" if profession_type == "salaried" else "irregular"
        updates = {
            "profession": profession,
            "profession_type": profession_type,
            "income_type": income_type,
            "onboarding_step": "MONTHLY_INCOME",
            "updated_at": datetime.now().isoformat()
        }
        return self.store.update(phone, updates)
    
    def save_monthly_income(self, phone: str, amount: int) -> Dict:
        """Save estimated monthly income"""
        updates = {
            "monthly_income_estimate": amount,
            "onboarding_step": "DEPENDENTS",
            "updated_at": datetime.now().isoformat()
        }
        return self.store.update(phone, updates)
    
    def save_dependents(self, phone: str, count: int) -> Dict:
        """Save number of dependents"""
        updates = {
            "dependents": count,
            "onboarding_step": "CURRENT_SAVINGS",
            "updated_at": datetime.now().isoformat()
        }
        return self.store.update(phone, updates)
    
    def save_current_savings(self, phone: str, amount: int) -> Dict:
        """Save current savings"""
        updates = {
            "current_savings": amount,
            "emergency_fund": amount,
            "onboarding_step": "CURRENT_DEBT",
            "updated_at": datetime.now().isoformat()
        }
        return self.store.update(phone, updates)
    
    def save_current_debt(self, phone: str, amount: int, details: List[Dict] = None) -> Dict:
        """Save current debt information"""
        updates = {
            "current_debt": amount,
            "debt_details": details or [],
            "onboarding_step": "GOALS",
            "updated_at": datetime.now().isoformat()
        }
        return self.store.update(phone, updates)
    
    def save_goals(self, phone: str, goals: List[str], primary_goal: str = None) -> Dict:
        """Save financial goals and complete onboarding"""
        updates = {
            "goals": goals,
            "primary_goal": primary_goal or (goals[0] if goals else None),
            "onboarding_step": "DONE",
            "onboarding_complete": True,
            "updated_at": datetime.now().isoformat()
        }
        return self.store.update(phone, updates)
    
    def get_onboarding_step(self, phone: str) -> str:
        """Get current onboarding step"""
        user = self.ensure_user(phone)
        return user.get("onboarding_step", "NAME")
    
    def is_onboarding_complete(self, phone: str) -> bool:
        """Check if onboarding is complete"""
        user = self.get_user(phone)
        return user.get("onboarding_complete", False) if user else False
    
    def get_language(self, phone: str) -> str:
        """Get user's preferred language"""
        user = self.get_user(phone)
        return user.get("language", "en") if user else "en"
    
    def get_voice_enabled(self, phone: str) -> bool:
        """Check if voice messages are enabled"""
        user = self.get_user(phone)
        return user.get("voice_enabled", True) if user else True
    
    def update_activity(self, phone: str) -> None:
        """Update last activity timestamp and streak"""
        user = self.ensure_user(phone)
        last_active = user.get("last_active", "")
        
        today = datetime.now().date()
        streak = user.get("streak_days", 0)
        
        if last_active:
            last_date = datetime.fromisoformat(last_active).date()
            days_diff = (today - last_date).days
            
            if days_diff == 1:
                streak += 1
            elif days_diff > 1:
                streak = 1
        else:
            streak = 1
        
        self.store.update(phone, {
            "last_active": datetime.now().isoformat(),
            "streak_days": streak
        })
    
    def add_income(self, phone: str, amount: int) -> None:
        """Add to total income recorded"""
        user = self.ensure_user(phone)
        total = user.get("total_income_recorded", 0) + amount
        self.store.update(phone, {"total_income_recorded": total})
    
    def add_expense(self, phone: str, amount: int) -> None:
        """Add to total expense recorded"""
        user = self.ensure_user(phone)
        total = user.get("total_expense_recorded", 0) + amount
        self.store.update(phone, {"total_expense_recorded": total})
    
    def get_all_users(self) -> Dict[str, Dict]:
        """Get all users"""
        return self.store.get_all()
    
    def get_users_for_reminders(self, current_hour: int) -> List[Dict]:
        """Get users who should receive reminders at this hour"""
        all_users = self.store.get_all()
        users = []
        
        for phone, user in all_users.items():
            if not user.get("onboarding_complete"):
                continue
            
            reminder_time = user.get("reminder_time", "09:00")
            reminder_hour = int(reminder_time.split(":")[0])
            
            if reminder_hour == current_hour:
                users.append(user)
        
        return users
    
    def get_financial_summary(self, phone: str) -> Dict:
        """Get user's financial summary for AI advice"""
        user = self.ensure_user(phone)
        
        return {
            "name": user.get("name", "User"),
            "profession": user.get("profession"),
            "income_type": user.get("income_type", "irregular"),
            "monthly_income": user.get("monthly_income_estimate", 0),
            "dependents": user.get("dependents", 0),
            "current_savings": user.get("current_savings", 0),
            "emergency_fund": user.get("emergency_fund", 0),
            "current_debt": user.get("current_debt", 0),
            "goals": user.get("goals", []),
            "primary_goal": user.get("primary_goal"),
            "total_income_recorded": user.get("total_income_recorded", 0),
            "total_expense_recorded": user.get("total_expense_recorded", 0),
            "streak_days": user.get("streak_days", 0),
        }


# Global instance
user_repo = UserRepository()
