"""
Reminder Repository - Daily reminders and notifications
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import REMINDERS_DB_FILE
from database.json_store import JSONStore


class ReminderRepository:
    """Manage user reminders and scheduled notifications"""
    
    def __init__(self):
        self.store = JSONStore(REMINDERS_DB_FILE)
    
    def create_reminder(
        self,
        user_id: str,
        reminder_type: str,  # daily_check, goal_reminder, bill_payment, investment_sip
        message: str,
        schedule_time: str = "09:00",
        frequency: str = "daily",  # daily, weekly, monthly, once
        metadata: Dict = None
    ) -> Dict:
        """Create a new reminder"""
        
        reminder_id = self.store.generate_id()
        reminder = {
            "id": reminder_id,
            "user_id": user_id,
            "type": reminder_type,
            "message": message,
            "schedule_time": schedule_time,
            "frequency": frequency,
            "is_active": True,
            "metadata": metadata or {},
            "last_sent": None,
            "next_due": self._calculate_next_due(schedule_time, frequency),
            "created_at": datetime.now().isoformat(),
        }
        
        self.store.set(reminder_id, reminder)
        return reminder
    
    def _calculate_next_due(self, schedule_time: str, frequency: str) -> str:
        """Calculate next due datetime"""
        now = datetime.now()
        hour, minute = map(int, schedule_time.split(":"))
        
        next_due = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if next_due <= now:
            if frequency == "daily":
                next_due += timedelta(days=1)
            elif frequency == "weekly":
                next_due += timedelta(weeks=1)
            elif frequency == "monthly":
                next_due += timedelta(days=30)
        
        return next_due.isoformat()
    
    def get_due_reminders(self) -> List[Dict]:
        """Get all reminders that are due now"""
        all_reminders = self.store.get_all()
        now = datetime.now()
        due = []
        
        for reminder in all_reminders.values():
            if not reminder.get("is_active"):
                continue
            
            next_due = datetime.fromisoformat(reminder["next_due"])
            
            if next_due <= now:
                due.append(reminder)
        
        return due
    
    def mark_sent(self, reminder_id: str) -> Optional[Dict]:
        """Mark reminder as sent and update next due"""
        reminder = self.store.get(reminder_id)
        if not reminder:
            return None
        
        now = datetime.now()
        frequency = reminder.get("frequency", "daily")
        
        # Calculate next due based on frequency
        if frequency == "once":
            return self.store.update(reminder_id, {
                "is_active": False,
                "last_sent": now.isoformat()
            })
        
        next_due = self._calculate_next_due(
            reminder.get("schedule_time", "09:00"),
            frequency
        )
        
        return self.store.update(reminder_id, {
            "last_sent": now.isoformat(),
            "next_due": next_due
        })
    
    def get_user_reminders(self, user_id: str) -> List[Dict]:
        """Get all reminders for a user"""
        all_reminders = self.store.get_all()
        return [r for r in all_reminders.values() if r.get("user_id") == user_id]
    
    def deactivate_reminder(self, reminder_id: str) -> Optional[Dict]:
        """Deactivate a reminder"""
        return self.store.update(reminder_id, {"is_active": False})
    
    def activate_reminder(self, reminder_id: str) -> Optional[Dict]:
        """Activate a reminder"""
        return self.store.update(reminder_id, {"is_active": True})
    
    def setup_default_reminders(self, user_id: str) -> List[Dict]:
        """Setup default reminders for new user"""
        reminders = []
        
        # Morning check-in
        reminders.append(self.create_reminder(
            user_id,
            "daily_check",
            "morning_greeting",
            "09:00",
            "daily",
            {"greeting_type": "morning"}
        ))
        
        # Evening expense reminder
        reminders.append(self.create_reminder(
            user_id,
            "daily_check",
            "evening_expense",
            "21:00",
            "daily",
            {"check_type": "expense_log"}
        ))
        
        # Weekly summary
        reminders.append(self.create_reminder(
            user_id,
            "weekly_summary",
            "weekly_report",
            "10:00",
            "weekly",
            {"report_type": "weekly"}
        ))
        
        return reminders


# Global instance
reminder_repo = ReminderRepository()
