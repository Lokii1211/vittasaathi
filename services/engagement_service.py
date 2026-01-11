"""
Savings Challenges & Community Features
=======================================
Engaging features to make saving fun and social
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import random
import uuid
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import SAVINGS_CHALLENGES, USER_TYPES
from database.user_repository import user_repo
from database.transaction_repository import transaction_repo


class ChallengeService:
    """Savings challenges to make saving fun"""
    
    def __init__(self):
        self.challenges = SAVINGS_CHALLENGES
    
    def get_available_challenges(self, user_id: str) -> List[Dict]:
        """Get challenges available for user"""
        user = user_repo.get_user(user_id)
        if not user:
            return []
        
        active = user.get("active_challenges", [])
        completed = user.get("completed_challenges", [])
        
        available = []
        for cid, challenge in self.challenges.items():
            if cid not in active and cid not in completed:
                available.append({
                    "id": cid,
                    **challenge
                })
        
        return available
    
    def start_challenge(self, user_id: str, challenge_id: str) -> Dict:
        """Start a savings challenge"""
        
        if challenge_id not in self.challenges:
            return {"success": False, "error": "Challenge not found"}
        
        challenge = self.challenges[challenge_id]
        
        user = user_repo.get_user(user_id)
        active = user.get("active_challenges", [])
        
        if challenge_id in active:
            return {"success": False, "error": "Already in this challenge"}
        
        # Create challenge record
        challenge_record = {
            "id": challenge_id,
            "started_at": datetime.now().isoformat(),
            "current_week": 1,
            "total_saved": 0,
            "last_contribution": None
        }
        
        active.append(challenge_id)
        user_repo.update_user(user_id, {
            "active_challenges": active,
            f"challenge_{challenge_id}": challenge_record
        })
        
        return {
            "success": True,
            "message": f"Started {challenge['name']}! 🎯",
            "challenge": challenge
        }
    
    def get_52_week_target(self, week: int) -> int:
        """Get savings target for 52-week challenge"""
        return week * 10  # ₹10 in week 1, ₹20 in week 2, etc.
    
    def contribute_to_challenge(self, user_id: str, challenge_id: str, amount: int) -> Dict:
        """Add contribution to challenge"""
        
        user = user_repo.get_user(user_id)
        record = user.get(f"challenge_{challenge_id}")
        
        if not record:
            return {"success": False, "error": "Challenge not active"}
        
        record["total_saved"] += amount
        record["last_contribution"] = datetime.now().isoformat()
        
        if challenge_id == "52_week":
            record["current_week"] += 1
        
        user_repo.update_user(user_id, {f"challenge_{challenge_id}": record})
        
        # Check if completed
        challenge = self.challenges[challenge_id]
        completed = False
        
        if challenge_id == "52_week" and record["current_week"] > 52:
            completed = True
        
        return {
            "success": True,
            "total_saved": record["total_saved"],
            "completed": completed,
            "message": f"₹{amount} added! Total: ₹{record['total_saved']} 💰"
        }
    
    def get_challenge_status(self, user_id: str, challenge_id: str) -> Dict:
        """Get current challenge status"""
        
        user = user_repo.get_user(user_id)
        record = user.get(f"challenge_{challenge_id}")
        
        if not record:
            return {"status": "not_started"}
        
        challenge = self.challenges[challenge_id]
        
        status = {
            "id": challenge_id,
            "name": challenge["name"],
            "icon": challenge["icon"],
            "total_saved": record["total_saved"],
            "started_at": record["started_at"]
        }
        
        if challenge_id == "52_week":
            week = record["current_week"]
            target = self.get_52_week_target(week)
            total_target = 13780
            progress = int(record["total_saved"] / total_target * 100)
            
            status.update({
                "current_week": week,
                "week_target": target,
                "total_target": total_target,
                "progress_percent": progress
            })
        
        return status


class PeerComparisonService:
    """Anonymous peer comparison for motivation"""
    
    def __init__(self):
        pass
    
    def get_peer_comparison(self, user_id: str) -> Dict:
        """Compare with anonymous peers in same category"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return {}
        
        user_type = user.get("user_type", "other")
        income = user.get("monthly_income_estimate", 0)
        
        # Get similar users (same type, similar income ±30%)
        all_users = user_repo.get_all_users()
        peers = []
        
        income_low = income * 0.7
        income_high = income * 1.3
        
        for uid, u in all_users.items():
            if uid != user_id and u.get("user_type") == user_type:
                u_income = u.get("monthly_income_estimate", 0)
                if income_low <= u_income <= income_high:
                    peers.append(u)
        
        if len(peers) < 3:
            return {"available": False, "message": "Not enough peers yet"}
        
        # Calculate averages
        peer_savings_rates = [
            self._get_savings_rate(transaction_repo.get_monthly_summary(p.get("phone")))
            for p in peers[:10]
        ]
        
        avg_peer_savings = sum(peer_savings_rates) / len(peer_savings_rates) if peer_savings_rates else 0
        
        user_summary = transaction_repo.get_monthly_summary(user_id)
        user_savings_rate = self._get_savings_rate(user_summary)
        
        # Comparison
        comparison = "same"
        if user_savings_rate > avg_peer_savings + 5:
            comparison = "better"
        elif user_savings_rate < avg_peer_savings - 5:
            comparison = "lower"
        
        return {
            "available": True,
            "peer_count": len(peers),
            "your_savings_rate": user_savings_rate,
            "peer_avg_savings_rate": round(avg_peer_savings, 1),
            "comparison": comparison,
            "message": self._get_comparison_message(comparison, user_savings_rate, avg_peer_savings)
        }
    
    def _get_savings_rate(self, summary: Dict) -> float:
        income = summary.get("total_income", 0)
        savings = summary.get("net_savings", 0)
        if income <= 0:
            return 0
        return round(savings / income * 100, 1)
    
    def _get_comparison_message(self, comparison: str, user_rate: float, peer_rate: float) -> str:
        if comparison == "better":
            return f"🌟 You're saving {user_rate}% - that's better than {int(peer_rate)}% average of similar earners!"
        elif comparison == "lower":
            return f"💪 You're saving {user_rate}%. Others like you save {int(peer_rate)}% on average. You can do it too!"
        else:
            return f"👍 You're saving {user_rate}% - right on track with your peers!"


class StreakService:
    """Track and celebrate user streaks"""
    
    def __init__(self):
        pass
    
    def update_streak(self, user_id: str) -> Dict:
        """Update user's tracking streak"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return {}
        
        last_active = user.get("last_active")
        current_streak = user.get("streak_days", 0)
        longest_streak = user.get("longest_streak", 0)
        
        today = datetime.now().date()
        
        if last_active:
            last_date = datetime.fromisoformat(last_active).date()
            days_diff = (today - last_date).days
            
            if days_diff == 1:
                # Continued streak
                current_streak += 1
            elif days_diff == 0:
                # Same day, no change
                pass
            else:
                # Streak broken
                current_streak = 1
        else:
            current_streak = 1
        
        # Update longest streak
        if current_streak > longest_streak:
            longest_streak = current_streak
        
        # Check for celebration milestones
        celebration = None
        if current_streak in [7, 14, 21, 30, 50, 100, 365]:
            celebration = self._get_celebration(current_streak)
        
        user_repo.update_user(user_id, {
            "streak_days": current_streak,
            "longest_streak": longest_streak,
            "last_active": datetime.now().isoformat()
        })
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "celebration": celebration
        }
    
    def _get_celebration(self, days: int) -> Dict:
        celebrations = {
            7: {"emoji": "🔥", "title": "1 Week Streak!", "points": 50},
            14: {"emoji": "⚡", "title": "2 Week Streak!", "points": 100},
            21: {"emoji": "💪", "title": "3 Week Streak!", "points": 150},
            30: {"emoji": "🏆", "title": "1 Month Streak!", "points": 300},
            50: {"emoji": "🌟", "title": "50 Day Streak!", "points": 500},
            100: {"emoji": "👑", "title": "100 Day Legend!", "points": 1000},
            365: {"emoji": "🎊", "title": "1 Year Champion!", "points": 5000},
        }
        return celebrations.get(days)


class TipsService:
    """Contextual financial tips based on user behavior"""
    
    def __init__(self):
        self.tips = self._load_tips()
    
    def _load_tips(self) -> Dict[str, List[Dict]]:
        return {
            "student": [
                {"tip": "Use student discounts everywhere!", "icon": "🎓"},
                {"tip": "Cook at hostel instead of ordering food", "icon": "🍳"},
                {"tip": "Buy second-hand books, save 50%+", "icon": "📚"},
                {"tip": "Free online courses are as good as paid ones", "icon": "💻"},
                {"tip": "Share subscriptions with roommates", "icon": "📱"},
            ],
            "homemaker": [
                {"tip": "Buy vegetables in evening - often discounted", "icon": "🥬"},
                {"tip": "Monthly grocery list prevents impulse buying", "icon": "📝"},
                {"tip": "Bulk buying staples saves 20-30%", "icon": "🛒"},
                {"tip": "Home-cooked tiffin service can earn extra", "icon": "🍱"},
                {"tip": "Compare prices before big purchases", "icon": "💰"},
            ],
            "delivery_partner": [
                {"tip": "Track petrol separately from earnings", "icon": "⛽"},
                {"tip": "Save extra on high-incentive days", "icon": "📈"},
                {"tip": "Vehicle maintenance fund prevents emergencies", "icon": "🔧"},
                {"tip": "Rest days prevent burnout and accidents", "icon": "😴"},
                {"tip": "Know your actual per-delivery earning", "icon": "📊"},
            ],
            "cab_driver": [
                {"tip": "Airport runs = better tips, plan accordingly", "icon": "✈️"},
                {"tip": "Fuel cards give cashback on petrol", "icon": "💳"},
                {"tip": "Track kilometers for accurate expense", "icon": "📏"},
                {"tip": "Don't chase every surge, sometimes rest pays more", "icon": "⏸️"},
            ],
            "small_vendor": [
                {"tip": "Separate business and personal expenses", "icon": "📂"},
                {"tip": "Track inventory daily, prevent theft", "icon": "📦"},
                {"tip": "UPI payments reduce cash handling risk", "icon": "📱"},
                {"tip": "Slow season savings = survival", "icon": "💰"},
                {"tip": "Customer credit can kill small business", "icon": "⚠️"},
            ],
            "bpo_worker": [
                {"tip": "Night shift allowance should be saved, not spent", "icon": "🌙"},
                {"tip": "Track variable pay separately", "icon": "💵"},
                {"tip": "Health insurance is crucial for odd hours", "icon": "🏥"},
                {"tip": "Meal planning saves vs canteen eating", "icon": "🍱"},
            ],
            "daily_wage": [
                {"tip": "Save first, then spend - even ₹10 counts", "icon": "💰"},
                {"tip": "Track work days to predict monthly income", "icon": "📅"},
                {"tip": "Avoid daily interest loans at any cost", "icon": "🚫"},
                {"tip": "Festival advance = debt trap, plan ahead", "icon": "⚠️"},
            ],
            "general": [
                {"tip": "Emergency fund first, investment later", "icon": "🆘"},
                {"tip": "Never share OTP with anyone - bank never asks", "icon": "🔒"},
                {"tip": "₹500/month SIP can grow to lakhs", "icon": "📈"},
                {"tip": "Health insurance is not optional", "icon": "🏥"},
                {"tip": "Track every expense - awareness is power", "icon": "👁️"},
                {"tip": "Avoid loan apps - 100-300% hidden interest", "icon": "🚨"},
                {"tip": "LIC is not best investment, just insurance", "icon": "📊"},
                {"tip": "Credit card minimum payment = debt trap", "icon": "💳"},
            ]
        }
    
    def get_tip(self, user_id: str) -> Dict:
        """Get relevant tip for user"""
        
        user = user_repo.get_user(user_id)
        if not user:
            tips = self.tips["general"]
        else:
            user_type = user.get("user_type", "other")
            tips = self.tips.get(user_type, []) + self.tips["general"]
        
        return random.choice(tips)
    
    def get_contextual_tip(self, user_id: str, context: str) -> Dict:
        """Get tip based on current context"""
        
        context_tips = {
            "high_expense": {
                "tip": "High spending detected! Review if all was necessary.",
                "icon": "⚠️"
            },
            "no_savings": {
                "tip": "Even ₹10/day = ₹300/month. Start small!",
                "icon": "💡"
            },
            "good_savings": {
                "tip": "Great savings! Consider starting a SIP now.",
                "icon": "🌟"
            },
            "streak_broken": {
                "tip": "Missed a day? No worries, start fresh today!",
                "icon": "🔄"
            },
            "goal_close": {
                "tip": "So close to your goal! One more push!",
                "icon": "🎯"
            }
        }
        
        return context_tips.get(context, self.get_tip(user_id))


class BillReminderService:
    """Smart bill payment reminders"""
    
    def __init__(self):
        pass
    
    def add_bill_reminder(
        self,
        user_id: str,
        bill_type: str,
        amount: int,
        due_date: int,  # Day of month
        frequency: str = "monthly"
    ) -> Dict:
        """Add a recurring bill reminder"""
        
        user = user_repo.get_user(user_id)
        bills = user.get("bill_reminders", [])
        
        bill = {
            "id": str(uuid.uuid4())[:8],
            "type": bill_type,
            "amount": amount,
            "due_date": due_date,
            "frequency": frequency,
            "created_at": datetime.now().isoformat(),
            "last_reminded": None,
            "last_paid": None
        }
        
        bills.append(bill)
        user_repo.update_user(user_id, {"bill_reminders": bills})
        
        return {"success": True, "bill": bill}
    
    def get_upcoming_bills(self, user_id: str, days: int = 7) -> List[Dict]:
        """Get bills due in next N days"""
        
        user = user_repo.get_user(user_id)
        bills = user.get("bill_reminders", [])
        
        today = datetime.now().day
        upcoming = []
        
        for bill in bills:
            due = bill["due_date"]
            days_until = due - today
            
            # Handle month wrapping
            if days_until < 0:
                days_until += 30  # Approx
            
            if 0 <= days_until <= days:
                bill["days_until"] = days_until
                upcoming.append(bill)
        
        return sorted(upcoming, key=lambda x: x["days_until"])
    
    def mark_bill_paid(self, user_id: str, bill_id: str, amount: int) -> Dict:
        """Mark a bill as paid"""
        
        user = user_repo.get_user(user_id)
        bills = user.get("bill_reminders", [])
        
        for bill in bills:
            if bill["id"] == bill_id:
                bill["last_paid"] = datetime.now().isoformat()
                bill["amount"] = amount  # Update if changed
                break
        
        user_repo.update_user(user_id, {"bill_reminders": bills})
        
        return {"success": True}
    
    def get_bill_summary(self, user_id: str) -> Dict:
        """Get monthly bill summary"""
        
        user = user_repo.get_user(user_id)
        bills = user.get("bill_reminders", [])
        
        monthly_bills = [b for b in bills if b.get("frequency") == "monthly"]
        total_monthly = sum(b.get("amount", 0) for b in monthly_bills)
        
        return {
            "total_bills": len(bills),
            "monthly_bills": len(monthly_bills),
            "total_monthly_amount": total_monthly,
            "bills": bills
        }


# Global instances
challenge_service = ChallengeService()
peer_comparison_service = PeerComparisonService()
streak_service = StreakService()
tips_service = TipsService()
bill_reminder_service = BillReminderService()

