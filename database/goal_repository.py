"""
Goal Repository - Financial goal tracking
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import GOALS_DB_FILE, GOAL_TYPES
from database.json_store import JSONStore


class GoalRepository:
    """Financial goal tracking and progress management"""
    
    def __init__(self):
        self.store = JSONStore(GOALS_DB_FILE)
    
    def create_goal(
        self,
        user_id: str,
        goal_type: str,
        target_amount: int,
        target_date: str,
        name: str = None,
        priority: int = None
    ) -> Dict:
        """Create a new financial goal"""
        
        goal_id = self.store.generate_id()
        goal_info = GOAL_TYPES.get(goal_type, {"icon": "🎯", "priority": 10})
        
        goal = {
            "id": goal_id,
            "user_id": user_id,
            "type": goal_type,
            "name": name or goal_type.replace("_", " ").title(),
            "icon": goal_info["icon"],
            "target_amount": target_amount,
            "saved_amount": 0,
            "target_date": target_date,
            "priority": priority or goal_info["priority"],
            "status": "active",  # active, paused, completed, cancelled
            "progress_percent": 0,
            "monthly_target": self._calculate_monthly_target(target_amount, target_date),
            "contributions": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        self.store.set(goal_id, goal)
        return goal
    
    def _calculate_monthly_target(self, target_amount: int, target_date: str) -> int:
        """Calculate required monthly savings to reach goal"""
        try:
            target = datetime.strptime(target_date, "%Y-%m-%d")
            today = datetime.now()
            months_left = max(1, (target.year - today.year) * 12 + target.month - today.month)
            return int(target_amount / months_left)
        except:
            return int(target_amount / 12)  # Default to 1 year
    
    def add_contribution(self, goal_id: str, amount: int, note: str = "") -> Optional[Dict]:
        """Add money towards a goal"""
        goal = self.store.get(goal_id)
        if not goal:
            return None
        
        contribution = {
            "amount": amount,
            "date": datetime.now().isoformat(),
            "note": note
        }
        
        new_saved = goal["saved_amount"] + amount
        progress = min(100, round(new_saved / goal["target_amount"] * 100, 1))
        
        status = "completed" if progress >= 100 else goal["status"]
        
        contributions = goal.get("contributions", [])
        contributions.append(contribution)
        
        return self.store.update(goal_id, {
            "saved_amount": new_saved,
            "progress_percent": progress,
            "status": status,
            "contributions": contributions,
            "updated_at": datetime.now().isoformat()
        })
    
    def get_user_goals(self, user_id: str, status: str = None) -> List[Dict]:
        """Get all goals for a user"""
        all_goals = self.store.get_all()
        
        goals = [
            g for g in all_goals.values()
            if g.get("user_id") == user_id and (not status or g.get("status") == status)
        ]
        
        # Sort by priority
        goals.sort(key=lambda x: x.get("priority", 10))
        return goals
    
    # Aliases for API compatibility
    def add_goal(self, user_id: str, goal_type: str, target_amount: int, target_date: str, name: str = None) -> Dict:
        """Alias for create_goal"""
        return self.create_goal(user_id, goal_type, target_amount, target_date, name)
    
    def get_goals(self, user_id: str) -> List[Dict]:
        """Alias for get_user_goals"""
        return self.get_user_goals(user_id)
    
    def get_goal(self, goal_id: str) -> Optional[Dict]:
        """Get goal by ID"""
        return self.store.get(goal_id)
    
    def update_goal_status(self, goal_id: str, status: str) -> Optional[Dict]:
        """Update goal status"""
        return self.store.update(goal_id, {
            "status": status,
            "updated_at": datetime.now().isoformat()
        })
    
    def get_goal_summary(self, user_id: str) -> Dict:
        """Get summary of all user's goals"""
        goals = self.get_user_goals(user_id)
        
        active = [g for g in goals if g["status"] == "active"]
        completed = [g for g in goals if g["status"] == "completed"]
        
        total_target = sum(g["target_amount"] for g in active)
        total_saved = sum(g["saved_amount"] for g in active)
        
        return {
            "total_goals": len(goals),
            "active_goals": len(active),
            "completed_goals": len(completed),
            "total_target_amount": total_target,
            "total_saved_amount": total_saved,
            "overall_progress": round(total_saved / total_target * 100, 1) if total_target > 0 else 0,
            "monthly_required": sum(g["monthly_target"] for g in active),
            "goals": goals
        }
    
    def get_next_milestone(self, user_id: str) -> Optional[Dict]:
        """Get the nearest goal milestone"""
        goals = self.get_user_goals(user_id, "active")
        
        if not goals:
            return None
        
        # Find goal closest to completion
        goals.sort(key=lambda x: x["progress_percent"], reverse=True)
        nearest = goals[0]
        
        remaining = nearest["target_amount"] - nearest["saved_amount"]
        
        return {
            "goal": nearest["name"],
            "icon": nearest["icon"],
            "progress": nearest["progress_percent"],
            "remaining": remaining,
            "target_date": nearest["target_date"],
            "message": f"Just ₹{remaining:,} more to reach your {nearest['name']} goal!"
        }


# Global instance
goal_repo = GoalRepository()
