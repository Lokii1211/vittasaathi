"""
Scheduler - Daily reminders and automated messages
Run this alongside the main API for scheduled notifications
"""
from datetime import datetime
import time
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False

from database.user_repository import user_repo
from database.reminder_repository import reminder_repo
from services.financial_advisor import financial_advisor
from services.notification_service import notification_service
from services.voice_service import voice_service


def send_morning_greetings():
    """Send morning greetings to all users at their preferred time"""
    
    current_hour = datetime.now().hour
    users = user_repo.get_users_for_reminders(current_hour)
    
    for user in users:
        phone = user.get("phone")
        name = user.get("name", "Friend")
        language = user.get("language", "en")
        voice_enabled = user.get("voice_enabled", True)
        
        # Get personalized daily message
        daily = financial_advisor.get_daily_message(phone)
        message = daily.get("message", f"Good morning {name}!")
        
        # Send WhatsApp
        notification_service.send_whatsapp(phone, message)
        
        # Send voice if enabled
        if voice_enabled:
            voice_path = voice_service.generate_greeting(name, language)
            if voice_path:
                # In production, upload to cloud and get URL
                pass
        
        print(f"[Morning] Sent greeting to {phone}")


def send_evening_reminders():
    """Send evening expense tracking reminders"""
    
    current_hour = datetime.now().hour
    if current_hour != 21:  # 9 PM
        return
    
    all_users = user_repo.get_all_users()
    
    for phone, user in all_users.items():
        if not user.get("onboarding_complete"):
            continue
        
        language = user.get("language", "en")
        name = user.get("name", "Friend")
        
        msgs = {
            "en": f"📊 {name}, don't forget to log today's expenses! Reply with what you spent today.",
            "hi": f"📊 {name}, आज के खर्च लिखना न भूलें! बताइए आज क्या-क्या खर्च हुआ।",
            "ta": f"📊 {name}, இன்றைய செலவுகளை பதிவு செய்ய மறக்காதீர்கள்!",
            "te": f"📊 {name}, ఈరోజు ఖర్చులు నమోదు చేయడం మరచిపోవద్దు!",
        }
        
        message = msgs.get(language, msgs["en"])
        notification_service.send_whatsapp(phone, message)
        print(f"[Evening] Sent reminder to {phone}")


def send_weekly_reports():
    """Send weekly financial reports on Sundays"""
    
    if datetime.now().strftime("%A") != "Sunday":
        return
    
    all_users = user_repo.get_all_users()
    
    for phone, user in all_users.items():
        if not user.get("onboarding_complete"):
            continue
        
        name = user.get("name", "Friend")
        language = user.get("language", "en")
        
        # Get health score
        health = financial_advisor.get_financial_health_score(phone)
        h = health["health"]
        
        message = f"📊 *Weekly Report for {name}*\n\n"
        message += f"🏥 Financial Health: {h['grade']} ({health['total_score']}/100)\n"
        message += f"{h['emoji']} {h['message']}\n\n"
        
        # Get advice
        advice = financial_advisor.get_personalized_advice(phone)
        if advice:
            message += "*This Week's Priority:*\n"
            message += f"{advice[0]['icon']} {advice[0]['title']}\n"
            message += f"{advice[0]['advice']}"
        
        message += "\n\n💪 Keep tracking your finances!"
        
        notification_service.send_whatsapp(phone, message)
        print(f"[Weekly] Sent report to {phone}")


def process_due_reminders():
    """Process all due reminders"""
    
    due = reminder_repo.get_due_reminders()
    
    for reminder in due:
        user_id = reminder.get("user_id")
        reminder_type = reminder.get("type")
        
        if reminder_type == "daily_check":
            # Already handled by morning/evening functions
            pass
        elif reminder_type == "goal_reminder":
            # Send goal progress reminder
            user = user_repo.get_user(user_id)
            if user:
                from database.goal_repository import goal_repo
                milestone = goal_repo.get_next_milestone(user_id)
                if milestone:
                    msg = f"🎯 Goal Update: {milestone['message']}"
                    notification_service.send_whatsapp(user_id, msg)
        
        # Mark as sent
        reminder_repo.mark_sent(reminder["id"])


def run_scheduler():
    """Run the background scheduler"""
    
    if not SCHEDULER_AVAILABLE:
        print("APScheduler not installed. Run: pip install apscheduler")
        return
    
    scheduler = BackgroundScheduler()
    
    # Morning greetings - every hour from 6 AM to 10 AM
    scheduler.add_job(
        send_morning_greetings,
        CronTrigger(hour="6-10", minute=0),
        id="morning_greetings"
    )
    
    # Evening reminders - 9 PM
    scheduler.add_job(
        send_evening_reminders,
        CronTrigger(hour=21, minute=0),
        id="evening_reminders"
    )
    
    # Weekly reports - Sunday 10 AM
    scheduler.add_job(
        send_weekly_reports,
        CronTrigger(day_of_week="sun", hour=10, minute=0),
        id="weekly_reports"
    )
    
    # Process due reminders - every 15 minutes
    scheduler.add_job(
        process_due_reminders,
        CronTrigger(minute="*/15"),
        id="process_reminders"
    )
    
    scheduler.start()
    print("🕐 Scheduler started!")
    print("   - Morning greetings: 6-10 AM")
    print("   - Evening reminders: 9 PM")
    print("   - Weekly reports: Sunday 10 AM")
    print("   - Due reminders: Every 15 min")
    
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("Scheduler stopped.")


if __name__ == "__main__":
    run_scheduler()
