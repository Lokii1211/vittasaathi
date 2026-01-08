"""
Budget Repository - Budget planning and tracking
"""

from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import BUDGETS_DB_FILE, EXPENSE_CATEGORIES
from database.json_store import JSONStore


class BudgetRepository:
    """Budget planning and expense tracking"""
    
    def __init__(self):
        self.store = JSONStore(BUDGETS_DB_FILE)
    
    def create_monthly_budget(
        self,
        user_id: str,
        month: str,  # YYYY-MM
        total_budget: int,
        category_limits: Dict[str, int] = None
    ) -> Dict:
        """Create monthly budget"""
        
        budget_id = f"{user_id}_{month}"
        
        # Default category distribution if not provided
        if not category_limits:
            category_limits = self._default_category_distribution(total_budget)
        
        budget = {
            "id": budget_id,
            "user_id": user_id,
            "month": month,
            "total_budget": total_budget,
            "category_limits": category_limits,
            "category_spent": {cat: 0 for cat in category_limits.keys()},
            "total_spent": 0,
            "remaining": total_budget,
            "alerts_sent": [],
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        self.store.set(budget_id, budget)
        return budget
    
    def _default_category_distribution(self, total: int) -> Dict[str, int]:
        """Create default budget distribution based on 50/30/20 rule"""
        # Needs (50%): rent, utilities, food, transport, healthcare
        # Wants (30%): entertainment, shopping
        # Savings (20%): savings, investment
        
        return {
            "rent": int(total * 0.25),
            "food": int(total * 0.15),
            "transport": int(total * 0.05),
            "utilities": int(total * 0.05),
            "healthcare": int(total * 0.03),
            "entertainment": int(total * 0.10),
            "shopping": int(total * 0.07),
            "family": int(total * 0.05),
            "savings": int(total * 0.10),
            "investment": int(total * 0.10),
            "other_expense": int(total * 0.05),
        }
    
    def get_current_budget(self, user_id: str) -> Optional[Dict]:
        """Get current month's budget"""
        month = datetime.now().strftime("%Y-%m")
        budget_id = f"{user_id}_{month}"
        return self.store.get(budget_id)
    
    def get_budget(self, user_id: str, month: str) -> Optional[Dict]:
        """Get budget for specific month"""
        budget_id = f"{user_id}_{month}"
        return self.store.get(budget_id)
    
    def record_expense(
        self,
        user_id: str,
        category: str,
        amount: int
    ) -> Dict:
        """Record expense against budget"""
        
        month = datetime.now().strftime("%Y-%m")
        budget = self.get_current_budget(user_id)
        
        if not budget:
            # Create budget if doesn't exist (estimate from user profile)
            budget = self.create_monthly_budget(user_id, month, 25000)  # Default
        
        budget_id = budget["id"]
        
        # Update spent amounts
        category_spent = budget.get("category_spent", {})
        category_spent[category] = category_spent.get(category, 0) + amount
        
        total_spent = budget.get("total_spent", 0) + amount
        remaining = budget["total_budget"] - total_spent
        
        # Check for alerts
        alerts = []
        category_limit = budget["category_limits"].get(category, 0)
        
        if category_spent[category] > category_limit and f"{category}_exceeded" not in budget.get("alerts_sent", []):
            alerts.append({
                "type": "category_exceeded",
                "category": category,
                "spent": category_spent[category],
                "limit": category_limit
            })
        
        if total_spent > budget["total_budget"] * 0.8 and "budget_warning" not in budget.get("alerts_sent", []):
            alerts.append({
                "type": "budget_warning",
                "percentage": round(total_spent / budget["total_budget"] * 100, 1)
            })
        
        alerts_sent = budget.get("alerts_sent", [])
        for alert in alerts:
            if alert["type"] == "category_exceeded":
                alerts_sent.append(f"{category}_exceeded")
            else:
                alerts_sent.append(alert["type"])
        
        updated = self.store.update(budget_id, {
            "category_spent": category_spent,
            "total_spent": total_spent,
            "remaining": remaining,
            "alerts_sent": alerts_sent,
            "updated_at": datetime.now().isoformat()
        })
        
        return {
            "budget": updated,
            "alerts": alerts
        }
    
    def get_budget_status(self, user_id: str) -> Dict:
        """Get comprehensive budget status"""
        budget = self.get_current_budget(user_id)
        
        if not budget:
            return {"status": "no_budget", "message": "No budget set for this month"}
        
        total_budget = budget["total_budget"]
        total_spent = budget["total_spent"]
        remaining = budget["remaining"]
        
        # Days left in month
        today = datetime.now()
        last_day = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        days_left = (last_day - today).days + 1
        
        # Daily allowance
        daily_allowance = remaining / max(1, days_left)
        
        # Category status
        category_status = []
        for cat, limit in budget["category_limits"].items():
            spent = budget["category_spent"].get(cat, 0)
            remaining_cat = limit - spent
            status = "ok" if spent <= limit else "exceeded"
            
            category_status.append({
                "category": cat,
                "limit": limit,
                "spent": spent,
                "remaining": remaining_cat,
                "percent_used": round(spent / limit * 100, 1) if limit > 0 else 0,
                "status": status
            })
        
        return {
            "month": budget["month"],
            "total_budget": total_budget,
            "total_spent": total_spent,
            "remaining": remaining,
            "percent_used": round(total_spent / total_budget * 100, 1),
            "days_left": days_left,
            "daily_allowance": round(daily_allowance),
            "categories": category_status,
            "health": self._calculate_budget_health(total_spent, total_budget, days_left, today.day)
        }
    
    def _calculate_budget_health(self, spent: int, budget: int, days_left: int, day_of_month: int) -> Dict:
        """Calculate budget health score"""
        
        # Expected spending by this day
        days_in_month = day_of_month + days_left - 1
        expected_spent = budget * (day_of_month / days_in_month)
        
        if spent <= expected_spent * 0.8:
            return {"score": "excellent", "emoji": "🌟", "message": "You're doing great!"}
        elif spent <= expected_spent:
            return {"score": "good", "emoji": "✅", "message": "On track!"}
        elif spent <= expected_spent * 1.2:
            return {"score": "warning", "emoji": "⚠️", "message": "Slightly over pace"}
        else:
            return {"score": "danger", "emoji": "🚨", "message": "Spending too fast!"}


# Import timedelta
from datetime import timedelta

# Global instance
budget_repo = BudgetRepository()
