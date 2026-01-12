"""
Advanced Scheduler v2.0
========================
Handles all automated notifications and reminders for the WhatsApp Financial Agent.
Designed as a background service that runs alongside the main API.

Features:
- Morning motivational reminders (6 AM)
- Evening expense checkout (8 PM)
- Weekly financial reports (Sunday 10 AM)
- Market updates (9:30 AM weekdays)
- Goal milestone alerts
- Bill payment reminders
"""

from datetime import datetime, timedelta
import time
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

# Scheduler imports
SCHEDULER_AVAILABLE = False
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    print("APScheduler not installed. Run: pip install apscheduler")

# Project imports
from database.user_repository import user_repo
from database.reminder_repository import reminder_repo
from services.financial_advisor import financial_advisor
from services.notification_service import notification_service
from services.whatsapp_cloud_service import whatsapp_cloud_service

# Try to import advanced agent
try:
    from agents.advanced_whatsapp_agent import advanced_agent
    ADVANCED_AGENT = True
except ImportError:
    from agents.moneyviya_agent import moneyviya_agent as advanced_agent
    ADVANCED_AGENT = False


def send_morning_greetings():
    """
    Send personalized morning greetings to all active users.
    Runs at 6 AM daily.
    """
    print(f"[{datetime.now()}] Starting morning greetings...")
    
    try:
        all_users = user_repo.get_all_users()
        sent_count = 0
        
        for phone, user in all_users.items():
            # Skip incomplete onboarding
            if not user.get("onboarding_complete"):
                continue
            
            try:
                # Generate personalized morning message
                if ADVANCED_AGENT:
                    message = advanced_agent.generate_morning_reminder(user)
                else:
                    message = advanced_agent.generate_daily_reminder(user, "morning")
                
                # Send via WhatsApp
                if whatsapp_cloud_service.is_available():
                    clean_phone = phone.replace("+", "")
                    whatsapp_cloud_service.send_text_message(clean_phone, message)
                    sent_count += 1
                    print(f"[Morning] Sent to {phone}")
                else:
                    notification_service.send_whatsapp(phone, message)
                    sent_count += 1
                    
            except Exception as user_error:
                print(f"[Morning] Error for {phone}: {user_error}")
                continue
        
        print(f"[Morning] Complete! Sent {sent_count} messages")
        
    except Exception as e:
        print(f"[Morning] Critical error: {e}")


def send_evening_checkout():
    """
    Send evening expense checkout messages to all active users.
    Asks users to confirm their daily transactions.
    Runs at 8 PM daily.
    """
    print(f"[{datetime.now()}] Starting evening checkout...")
    
    try:
        all_users = user_repo.get_all_users()
        sent_count = 0
        
        for phone, user in all_users.items():
            if not user.get("onboarding_complete"):
                continue
            
            try:
                # Generate evening checkout message
                if ADVANCED_AGENT:
                    message = advanced_agent.generate_evening_checkout(user)
                else:
                    message = advanced_agent.generate_daily_reminder(user, "evening")
                
                # Send via WhatsApp
                if whatsapp_cloud_service.is_available():
                    clean_phone = phone.replace("+", "")
                    whatsapp_cloud_service.send_text_message(clean_phone, message)
                    sent_count += 1
                    print(f"[Evening] Sent to {phone}")
                else:
                    notification_service.send_whatsapp(phone, message)
                    sent_count += 1
                    
            except Exception as user_error:
                print(f"[Evening] Error for {phone}: {user_error}")
                continue
        
        print(f"[Evening] Complete! Sent {sent_count} messages")
        
    except Exception as e:
        print(f"[Evening] Critical error: {e}")


def send_weekly_reports():
    """
    Send comprehensive weekly financial reports.
    Runs on Sundays at 10 AM.
    """
    print(f"[{datetime.now()}] Starting weekly reports...")
    
    try:
        all_users = user_repo.get_all_users()
        sent_count = 0
        
        for phone, user in all_users.items():
            if not user.get("onboarding_complete"):
                continue
            
            try:
                name = user.get("name", "Friend")
                
                # Get financial health
                try:
                    health = financial_advisor.get_financial_health_score(phone)
                    h = health.get("health", {})
                    score = health.get("total_score", 0)
                    grade = h.get("grade", "B")
                except:
                    score = 70
                    grade = "B"
                
                # Get personalized advice
                try:
                    advice_list = financial_advisor.get_personalized_advice(phone)
                    top_advice = advice_list[0] if advice_list else {"title": "Keep tracking", "advice": "Consistency is key!"}
                except:
                    top_advice = {"title": "Stay Focused", "advice": "Every rupee counts!"}
                
                # Build message
                message = f"""📊 *Weekly Financial Report*
{name} | Week of {datetime.now().strftime('%d %b')}
━━━━━━━━━━━━━━━━━━━━

🏥 *Financial Health Score:* {score}/100 ({grade})

{h.get('emoji', '📈')} {h.get('message', 'Keep improving!')}

━━━━━━━━━━━━━━━━━━━━

💡 *This Week's Priority:*
{top_advice.get('icon', '🎯')} *{top_advice.get('title', 'Focus')}*
{top_advice.get('advice', 'Stay consistent!')}

━━━━━━━━━━━━━━━━━━━━

📅 *Coming Week:*
• Track all expenses daily
• Review subscriptions
• Check goal progress

💪 *Keep pushing! You're doing great!*

Type "report" for detailed breakdown."""

                # Send
                if whatsapp_cloud_service.is_available():
                    clean_phone = phone.replace("+", "")
                    whatsapp_cloud_service.send_text_message(clean_phone, message)
                    sent_count += 1
                    print(f"[Weekly] Sent to {phone}")
                else:
                    notification_service.send_whatsapp(phone, message)
                    sent_count += 1
                    
            except Exception as user_error:
                print(f"[Weekly] Error for {phone}: {user_error}")
                continue
        
        print(f"[Weekly] Complete! Sent {sent_count} reports")
        
    except Exception as e:
        print(f"[Weekly] Critical error: {e}")


def send_market_updates():
    """
    Send morning market updates to users interested in investments.
    Runs at 9:30 AM on weekdays.
    """
    print(f"[{datetime.now()}] Starting market updates...")
    
    # Only on weekdays
    if datetime.now().weekday() >= 5:
        print("[Market] Skipping - Weekend")
        return
    
    try:
        from services.investment_service import investment_service
        
        all_users = user_repo.get_all_users()
        sent_count = 0
        
        for phone, user in all_users.items():
            if not user.get("onboarding_complete"):
                continue
            
            # Only send to users interested in investing
            # Check if they've asked about investments or have investment goal
            goal = user.get("goal_type", "").lower()
            if "invest" not in goal and "stock" not in goal and not user.get("market_updates_enabled"):
                continue
            
            try:
                message = investment_service.get_market_analysis()
                
                if whatsapp_cloud_service.is_available():
                    clean_phone = phone.replace("+", "")
                    whatsapp_cloud_service.send_text_message(clean_phone, message)
                    sent_count += 1
                    print(f"[Market] Sent to {phone}")
                    
            except Exception as user_error:
                print(f"[Market] Error for {phone}: {user_error}")
                continue
        
        print(f"[Market] Complete! Sent {sent_count} updates")
        
    except Exception as e:
        print(f"[Market] Critical error: {e}")


def process_due_reminders():
    """
    Process all due reminders (bill payments, goal milestones, etc.)
    Runs every 15 minutes.
    """
    try:
        due_reminders = reminder_repo.get_due_reminders()
        
        for reminder in due_reminders:
            user_id = reminder.get("user_id")
            reminder_type = reminder.get("type")
            
            try:
                user = user_repo.get_user(user_id)
                if not user:
                    continue
                
                message = ""
                
                if reminder_type == "bill_payment":
                    bill_name = reminder.get("bill_name", "Bill")
                    amount = reminder.get("amount", 0)
                    message = f"""🔔 *Bill Reminder!*

💳 *{bill_name}*
💰 Amount: ₹{amount}
📅 Due: Today

Don't forget to pay on time to avoid late fees!

Reply "paid" after payment."""

                elif reminder_type == "goal_milestone":
                    message = f"""🎯 *Goal Milestone Alert!*

{reminder.get('message', 'You are making progress!')}

Keep going! 💪"""

                elif reminder_type == "savings_tip":
                    message = reminder.get("message", "💡 Quick tip: Review your subscriptions monthly!")

                if message and whatsapp_cloud_service.is_available():
                    clean_phone = user_id.replace("+", "")
                    whatsapp_cloud_service.send_text_message(clean_phone, message)
                    print(f"[Reminder] Sent {reminder_type} to {user_id}")
                
                # Mark as sent
                reminder_repo.mark_sent(reminder.get("id"))
                
            except Exception as r_error:
                print(f"[Reminder] Error: {r_error}")
                continue
                
    except Exception as e:
        print(f"[Reminders] Critical error: {e}")


def run_scheduler():
    """
    Initialize and run the background scheduler with all jobs.
    """
    if not SCHEDULER_AVAILABLE:
        print("❌ APScheduler not installed!")
        print("   Run: pip install apscheduler")
        return
    
    scheduler = BackgroundScheduler()
    
    # ===== Morning Greetings - 6 AM =====
    scheduler.add_job(
        send_morning_greetings,
        CronTrigger(hour=6, minute=0),
        id="morning_greetings",
        name="Morning Motivational Greetings",
        replace_existing=True
    )
    
    # ===== Evening Checkout - 8 PM =====
    scheduler.add_job(
        send_evening_checkout,
        CronTrigger(hour=20, minute=0),
        id="evening_checkout",
        name="Evening Expense Checkout",
        replace_existing=True
    )
    
    # ===== Weekly Reports - Sunday 10 AM =====
    scheduler.add_job(
        send_weekly_reports,
        CronTrigger(day_of_week="sun", hour=10, minute=0),
        id="weekly_reports",
        name="Weekly Financial Reports",
        replace_existing=True
    )
    
    # ===== Market Updates - 9:30 AM Weekdays =====
    scheduler.add_job(
        send_market_updates,
        CronTrigger(day_of_week="mon-fri", hour=9, minute=30),
        id="market_updates",
        name="Daily Market Updates",
        replace_existing=True
    )
    
    # ===== Due Reminders - Every 15 minutes =====
    scheduler.add_job(
        process_due_reminders,
        IntervalTrigger(minutes=15),
        id="process_reminders",
        name="Process Due Reminders",
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    
    print("""
╔══════════════════════════════════════════════════╗
║     MoneyViya Scheduler v2.0 Started!            ║
╠══════════════════════════════════════════════════╣
║  📅 Scheduled Jobs:                              ║
║  ─────────────────────────────────────────────   ║
║  ⏰ 6:00 AM   - Morning Greetings                ║
║  📈 9:30 AM   - Market Updates (Weekdays)        ║
║  🌙 8:00 PM   - Evening Checkout                 ║
║  📊 Sunday    - Weekly Reports                   ║
║  🔔 Every 15m - Process Reminders                ║
╠══════════════════════════════════════════════════╣
║  Press Ctrl+C to stop                            ║
╚══════════════════════════════════════════════════╝
    """)
    
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n👋 Shutting down scheduler...")
        scheduler.shutdown()
        print("✅ Scheduler stopped gracefully.")


if __name__ == "__main__":
    run_scheduler()
