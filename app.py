"""
MoneyViya v3.0 - WhatsApp Financial Advisor & Manager
========================================================
Complete API with voice replies, dashboards, gamification,
analytics, PDF reports, family finance, and more!
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import io
import re
import os

# OCR
try:
    import pytesseract
    from PIL import Image
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False

# Database
from database.user_repository import user_repo
from database.transaction_repository import transaction_repo
from database.goal_repository import goal_repo
from database.budget_repository import budget_repo
from database.reminder_repository import reminder_repo

# Services
from services.nlp_service import nlp_service
from services.financial_advisor import financial_advisor
from services.message_builder import message_builder
from services.voice_service import voice_service
from services.notification_service import notification_service
from services.document_processor import document_processor
from services.dashboard_service import dashboard_service
from services.advanced_features import gamification_service, smart_insights, smart_reply_service
from services.smart_onboarding_service import get_smart_onboarding
from services.openai_service import openai_service, transcribe_voice, understand_message
from services.ai_onboarding_service import get_ai_onboarding
from services.pdf_report_service import pdf_report_service
from services.whatsapp_cloud_service import whatsapp_cloud_service

# Agents
from agents.fraud_agent import check_fraud
from agents.advanced_fraud_agent import advanced_fraud_check
from agents.moneyviya_agent import moneyviya_agent

# Config
from config import SUPPORTED_LANGUAGES, VOICES_DIR


# ================= APP SETUP =================
app = FastAPI(
    title="MoneyViya API",
    description="WhatsApp Financial Advisor for Gig Workers & Daily Earners - Track, Save, Grow",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app.mount("/static", StaticFiles(directory="static"), name="static")


# Root redirect to new dashboard
@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")


# Include extended API routes
try:
    from extended_api import extended_router
    app.include_router(extended_router)
except ImportError as e:
    print(f"Warning: Extended API not loaded: {e}")


# Health check and status endpoints
@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "3.0.0",
        "whatsapp_cloud_configured": whatsapp_cloud_service.is_available(),
        "openai_configured": openai_service.is_available()
    }


@app.get("/api/whatsapp-status")
def whatsapp_status():
    """Check WhatsApp Cloud API configuration with debug info"""
    # Direct env var check
    token_raw = os.getenv("WHATSAPP_CLOUD_TOKEN", "")
    phone_raw = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    
    # List all WHATSAPP related env vars
    all_whatsapp_vars = {k: "SET" if v else "EMPTY" for k, v in os.environ.items() if "WHATSAPP" in k}
    
    return {
        "configured": whatsapp_cloud_service.is_available(),
        "phone_number_id": phone_raw if phone_raw else "NOT SET",
        "token_set": bool(token_raw),
        "token_length": len(token_raw) if token_raw else 0,
        "all_whatsapp_vars": all_whatsapp_vars
    }


# ================= AI AGENT ENDPOINTS (for n8n) =================
@app.get("/api/users/active")
def get_active_users():
    """Get all active users for daily reminders (used by n8n)"""
    try:
        users = user_repo.get_all_users()
        active_users = [u for u in users if u.get("onboarding_complete")]
        return active_users
    except Exception as e:
        return []


@app.post("/api/send-message")
async def send_direct_message(request: Request):
    """Send direct WhatsApp message (used by n8n evening check)"""
    try:
        data = await request.json()
        phone = data.get("phone")
        message = data.get("message")
        
        if whatsapp_cloud_service.is_available():
            clean_phone = phone.replace("+", "")
            result = whatsapp_cloud_service.send_text_message(clean_phone, message)
            return {"success": True, "result": result}
        
        return {"success": False, "error": "WhatsApp not configured"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/send-reminder")
async def send_reminder(request: Request):
    """Send daily reminder to a user (used by n8n)"""
    try:
        data = await request.json()
        phone = data.get("phone")
        reminder_type = data.get("type", "morning")
        user_data = data.get("user_data", {})
        
        if isinstance(user_data, str):
            import json
            user_data = json.loads(user_data)
        
        # Generate reminder message using AI agent
        reminder_text = moneyviya_agent.generate_daily_reminder(user_data, reminder_type)
        
        # Send via WhatsApp
        if whatsapp_cloud_service.is_available():
            clean_phone = phone.replace("+", "")
            result = whatsapp_cloud_service.send_text_message(clean_phone, reminder_text)
            return {"success": True, "result": result}
        
        return {"success": False, "error": "WhatsApp not configured"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ================= WHATSAPP CLOUD API WEBHOOK =================
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "moneyviya_webhook_2024")


@app.get("/webhook/whatsapp-cloud")
async def verify_whatsapp_webhook(request: Request):
    """Verify webhook for WhatsApp Cloud API (Meta)"""
    try:
        params = dict(request.query_params)
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge")
        
        print(f"[Webhook Verify] mode={mode}, token={token}, challenge={challenge}")
        
        if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
            print("[Webhook Verify] SUCCESS")
            return int(challenge)
        else:
            print(f"[Webhook Verify] FAILED - expected token: {WHATSAPP_VERIFY_TOKEN}")
            raise HTTPException(status_code=403, detail="Verification failed")
    except Exception as e:
        print(f"[Webhook Verify] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/whatsapp-cloud")
async def handle_whatsapp_cloud_webhook(request: Request):
    """Handle incoming messages from WhatsApp Cloud API (Meta Official)"""
    try:
        data = await request.json()
        print(f"[WhatsApp Cloud] Received: {data}")
        
        # Extract message data
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        # Check if it's a message
        if "messages" not in value:
            return {"status": "ok"}
        
        messages = value.get("messages", [])
        contacts = value.get("contacts", [])
        
        for msg in messages:
            msg_type = msg.get("type")
            phone = msg.get("from")  # Sender's phone number
            
            # Get sender name
            sender_name = "Friend"
            for contact in contacts:
                if contact.get("wa_id") == phone:
                    sender_name = contact.get("profile", {}).get("name", "Friend")
            
            # Extract message text
            message_text = ""
            if msg_type == "text":
                message_text = msg.get("text", {}).get("body", "")
            elif msg_type == "interactive":
                interactive = msg.get("interactive", {})
                if interactive.get("type") == "button_reply":
                    message_text = interactive.get("button_reply", {}).get("title", "")
                elif interactive.get("type") == "list_reply":
                    message_text = interactive.get("list_reply", {}).get("title", "")
            elif msg_type == "audio":
                message_text = "[Voice message]"
            elif msg_type == "image":
                message_text = msg.get("image", {}).get("caption", "[Image]")
            else:
                message_text = f"[{msg_type}]"
            
            if not message_text:
                continue
            
            print(f"[WhatsApp Cloud] Message from +{phone}: {message_text}")
            
            # Ensure phone has + prefix
            if not phone.startswith("+"):
                phone = "+" + phone
            
            # Get or create user
            user_repo.update_activity(phone)
            user = user_repo.ensure_user(phone)
            
            if sender_name and sender_name != "Friend" and not user.get("name"):
                user_repo.update_user(phone, {"name": sender_name})
                user["name"] = sender_name
            
            # Process with AI Agent
            try:
                reply_text = moneyviya_agent.process_message(phone, message_text, user)
                user_repo.update_user(phone, user)
            except Exception as agent_error:
                print(f"[Agent Error] {agent_error}")
                reply_text = "I'm having trouble. Try:\n• 'spent 50 on tea'\n• 'earned 500 delivery'\n• 'help'"
            
            # Send reply
            if reply_text and whatsapp_cloud_service.is_available():
                clean_phone = phone.replace("+", "")
                result = whatsapp_cloud_service.send_text_message(clean_phone, reply_text)
                print(f"[WhatsApp Cloud] Reply sent: {result}")
        
        return {"status": "ok"}
        
    except Exception as e:
        print(f"[WhatsApp Cloud] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


# Add direct report routes for n8n (without /api/v2 prefix)
@app.get("/reports/{phone}/weekly-comparison")
def get_weekly_report(phone: str):
    """Weekly report for n8n"""
    from extended_api import get_weekly_comparison
    return get_weekly_comparison(phone)

@app.get("/reports/{phone}/monthly-comparison")
def get_monthly_report(phone: str):
    """Monthly report for n8n"""
    from extended_api import get_monthly_comparison
    return get_monthly_comparison(phone)

# PDF Report Generation
@app.get("/reports/{phone}/pdf/weekly")
def get_weekly_pdf_report(phone: str):
    """Generate weekly PDF report for user"""
    from datetime import datetime, timedelta
    
    user = user_repo.get_user(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get last 7 days of transactions
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    transactions = transaction_repo.get_transactions_by_date_range(
        phone, 
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )
    
    pdf_path = pdf_report_service.generate_weekly_report(user, transactions)
    
    if pdf_path:
        return FileResponse(
            pdf_path, 
            media_type="application/pdf",
            filename=f"MoneyViya_Weekly_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
    else:
        raise HTTPException(status_code=500, detail="PDF generation failed. Install reportlab: pip install reportlab")

@app.get("/reports/{phone}/pdf/monthly")
def get_monthly_pdf_report(phone: str):
    """Generate monthly PDF report for user"""
    from datetime import datetime, timedelta
    
    user = user_repo.get_user(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get last 30 days of transactions
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    transactions = transaction_repo.get_transactions_by_date_range(
        phone,
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )
    
    pdf_path = pdf_report_service.generate_monthly_report(user, transactions)
    
    if pdf_path:
        return FileResponse(
            pdf_path,
            media_type="application/pdf", 
            filename=f"MoneyViya_Monthly_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
    else:
        raise HTTPException(status_code=500, detail="PDF generation failed")


# ================= SCHEDULED TASKS =================
SCHEDULER_AVAILABLE = False
scheduler = None

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    SCHEDULER_AVAILABLE = True
    
    scheduler = BackgroundScheduler()
    
    def check_scheduled_backups():
        """Check and run scheduled backups"""
        try:
            from services.secure_backup_service import scheduled_backup_service
            result = scheduled_backup_service.check_and_run()
            if result.get("ran"):
                print(f"[Scheduler] Backup completed: {result.get('result', {}).get('success')}")
        except Exception as e:
            print(f"[Scheduler] Backup check failed: {e}")
    
    # Add scheduled backup check (runs every hour)
    scheduler.add_job(
        check_scheduled_backups,
        trigger=IntervalTrigger(hours=1),
        id='scheduled_backup_check',
        name='Check and run scheduled backups',
        replace_existing=True
    )
    
except ImportError:
    print("Note: APScheduler not installed. Scheduled backups will run on-demand only.")

@app.on_event("startup")
def startup_event():
    """Start scheduler on app startup"""
    if SCHEDULER_AVAILABLE and scheduler:
        scheduler.start()
        print("[Scheduler] Background scheduler started")
    else:
        print("[Scheduler] Running without background scheduler")

@app.on_event("shutdown")
def shutdown_event():
    """Shutdown scheduler gracefully"""
    if SCHEDULER_AVAILABLE and scheduler:
        scheduler.shutdown()
        print("[Scheduler] Background scheduler stopped")


# ================= MODELS =================
class WebhookPayload(BaseModel):
    phone: str
    message: str
    message_type: str = "text"
    voice_url: Optional[str] = None  # For voice message transcription

class TransactionPayload(BaseModel):
    phone: str
    amount: int
    type: str
    category: Optional[str] = None
    description: Optional[str] = ""

class GoalPayload(BaseModel):
    phone: str
    goal_type: str
    target_amount: int
    target_date: str
    name: Optional[str] = None

class OTPSendPayload(BaseModel):
    phone: str

class OTPVerifyPayload(BaseModel):
    phone: str
    otp: str

# OTP storage (in production use Redis)
import random
otp_store = {}

# ================= RESPONSE HELPER =================
def create_response(user_id: str, text: str, language: str = "en", generate_voice: bool = True) -> dict:
    """Create response with text and voice"""
    
    # Enhance with gamification
    enhanced = smart_reply_service.enhance_reply(user_id, text, language)
    
    return {
        "reply_text": enhanced["text"],
        "voice_text": enhanced["voice_text"],
        "voice_path": enhanced.get("voice_path"),
        "achievements": enhanced.get("achievements", [])
    }


# ================= STATIC FILES =================
from fastapi.staticfiles import StaticFiles
from pathlib import Path

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ================= HEALTH CHECK =================
@app.get("/")
def root():
    return {
        "service": "MoneyViya",
        "version": "3.0.0",
        "status": "running",
        "features": [
            "voice_replies", "dashboards", "gamification", "multi_language",
            "analytics", "pdf_reports", "csv_export", "family_finance", 
            "financial_calendar", "savings_challenges", "financial_education"
        ],
        "dashboard_url": "/static/dashboard.html",
        "admin_url": "/static/admin.html",
        "api_docs": "/docs",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
def health():
    return {"status": "healthy", "ocr": OCR_AVAILABLE}


# ================= USER MANAGEMENT FOR N8N =================
class UserRegister(BaseModel):
    phone: str
    name: str = None
    onboarding_step: str = "language_selection"

class LanguageUpdate(BaseModel):
    preferred_language: str
    onboarding_step: str = None

@app.get("/user/{phone}")
def get_user(phone: str):
    """Get user details by phone"""
    user = user_repo.get_user(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/user/{phone:path}")
async def update_user_profile(phone: str, request: Request):
    """Update user profile"""
    from urllib.parse import unquote
    phone = unquote(phone)
    if not phone.startswith("+"):
        phone = "+" + phone
    
    try:
        data = await request.json()
        name = data.get("name")
        
        if name:
            user_repo.update_user(phone, {"name": name})
        
        user = user_repo.get_user(phone)
        return {"success": True, "user": user}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/users")
def get_all_users():
    """Get all users"""
    return user_repo.get_all_users()

@app.post("/user/register")
def register_user(user: UserRegister):
    """Register a new user"""
    existing = user_repo.get_user(user.phone)
    if existing:
        return existing
    
    # Create new user
    new_user = user_repo.create_user(user.phone)
    
    # Update with provided data
    updates = {"onboarding_step": user.onboarding_step}
    if user.name:
        updates["name"] = user.name
    
    user_repo.update_user(user.phone, updates)
    
    return user_repo.get_user(user.phone)

@app.put("/user/{phone}/language")
def update_user_language(phone: str, data: LanguageUpdate):
    """Update user's preferred language"""
    user = user_repo.get_user(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Save language preference
    user_repo.save_language(phone, data.preferred_language)
    
    # Update onboarding step if provided
    if data.onboarding_step:
        updates = {"onboarding_step": data.onboarding_step}
        # If step is "completed", also mark onboarding as complete
        if data.onboarding_step == "completed":
            updates["onboarding_complete"] = True
        user_repo.update_user(phone, updates)
    
    return {"success": True, "language": data.preferred_language}

@app.put("/user/{phone}")
def update_user(phone: str, updates: dict):
    """Update user details"""
    user = user_repo.get_user(phone)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_repo.update_user(phone, updates)
    return user_repo.get_user(phone)


@app.api_route("/user/{phone}/reset-onboarding", methods=["GET", "POST"])
def reset_user_onboarding(phone: str):
    """Reset user onboarding to restart the flow"""
    user = user_repo.get_user(phone)
    if not user:
        return {"error": "User not found"}
    
    user_repo.update_user(phone, {
        "onboarding_step": "language",
        "onboarding_complete": False
    })
    return {"success": True, "message": "Onboarding reset. Send any message on WhatsApp to restart."}


@app.api_route("/user/{phone}/complete-onboarding", methods=["GET", "POST"])
def force_complete_onboarding(phone: str):
    """Force complete onboarding for a user (GET or POST)"""
    user = user_repo.get_user(phone)
    if not user:
        # Create user if not exists
        user = user_repo.create_user(phone)
    
    user_repo.update_user(phone, {
        "onboarding_step": "completed",
        "onboarding_complete": True,
        "preferred_language": user.get("preferred_language", "english"),
        "name": user.get("name", "User")
    })
    return {"success": True, "message": "Onboarding completed! You can now track expenses on WhatsApp."}


# ================= OTP AUTHENTICATION =================
import random
otp_store = {}  # In production use Redis

@app.post("/api/v2/auth/send-otp")
async def send_otp(data: OTPSendPayload):
    """Send OTP via WhatsApp"""
    phone = data.phone
    
    # Normalize phone
    if not phone.startswith("+"):
        phone = "+91" + phone.replace(" ", "").replace("-", "")
    
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    otp_store[phone] = otp
    
    # Try to send via WhatsApp
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
    
    if account_sid and auth_token:
        try:
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            
            message = client.messages.create(
                from_="whatsapp:+14155238886",
                to=f"whatsapp:{phone}",
                body=f"🔐 Your MoneyViya OTP is: *{otp}*\n\nDo not share this with anyone."
            )
            print(f"[OTP] Sent to {phone}: {otp}")
            return {"success": True, "message": "OTP sent to WhatsApp"}
        except Exception as e:
            print(f"[OTP] WhatsApp send failed: {e}")
            # Fall back to demo mode
            return {"success": True, "demo_otp": otp, "message": "Demo mode - WhatsApp not available"}
    else:
        # Demo mode
        return {"success": True, "demo_otp": otp, "message": "Demo mode - use this OTP"}

@app.post("/api/v2/auth/verify-otp")
async def verify_otp(data: OTPVerifyPayload):
    """Verify OTP"""
    phone = data.phone
    otp = data.otp
    
    # Normalize phone
    if not phone.startswith("+"):
        phone = "+91" + phone.replace(" ", "").replace("-", "")
    
    stored_otp = otp_store.get(phone)
    
    # Allow demo OTP 123456 for testing
    if otp == "123456" or (stored_otp and otp == stored_otp):
        # Clear OTP after successful verification
        if phone in otp_store:
            del otp_store[phone]
        
        # Create or get user
        user = user_repo.get_user(phone)
        if not user:
            user = user_repo.create_user(phone)
        
        return {"success": True, "user": user}
    else:
        return {"success": False, "message": "Invalid OTP"}


# ================= DOWNLOAD ENDPOINTS =================
@app.get("/download/report/{phone:path}")
async def download_report(phone: str, format: str = "pdf"):
    """Download financial report as PDF or HTML"""
    try:
        from datetime import datetime, timedelta
        from urllib.parse import unquote
        
        # Decode phone if URL encoded
        phone = unquote(phone)
        if not phone.startswith("+"):
            phone = "+" + phone
        
        user = user_repo.get_user(phone)
        if not user:
            user = {"name": "User", "phone": phone}
        
        # Get transactions for the month
        today = datetime.now()
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        transactions = transaction_repo.get_transactions(phone) or []
        
        # Calculate totals
        total_income = sum(t.get("amount", 0) for t in transactions if t.get("type") == "income")
        total_expense = sum(t.get("amount", 0) for t in transactions if t.get("type") == "expense")
        savings = total_income - total_expense
        
        # Group by category
        categories = {}
        for t in transactions:
            if t.get("type") == "expense":
                cat = t.get("category", "Other")
                categories[cat] = categories.get(cat, 0) + t.get("amount", 0)
        
        # Create HTML report
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>MoneyViya Report - {user.get('name', 'User')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #4F46E5; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat {{ background: #F8FAFC; border-radius: 10px; padding: 20px; flex: 1; text-align: center; }}
        .stat-value {{ font-size: 28px; font-weight: bold; }}
        .stat-label {{ color: #64748B; }}
        .income {{ color: #10B981; }}
        .expense {{ color: #EF4444; }}
        .savings {{ color: #4F46E5; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #E2E8F0; padding: 12px; text-align: left; }}
        th {{ background: #F8FAFC; }}
    </style>
</head>
<body>
    <h1>💰 MoneyViya Financial Report</h1>
    <p><strong>Name:</strong> {user.get('name', 'User')}</p>
    <p><strong>Phone:</strong> {phone}</p>
    <p><strong>Period:</strong> {start_date} to {end_date}</p>
    
    <div class="summary">
        <div class="stat">
            <div class="stat-value income">₹{total_income:,}</div>
            <div class="stat-label">Total Income</div>
        </div>
        <div class="stat">
            <div class="stat-value expense">₹{total_expense:,}</div>
            <div class="stat-label">Total Expenses</div>
        </div>
        <div class="stat">
            <div class="stat-value savings">₹{savings:,}</div>
            <div class="stat-label">Net Savings</div>
        </div>
    </div>
    
    <h2>📊 Expense by Category</h2>
    <table>
        <tr><th>Category</th><th>Amount</th><th>Percentage</th></tr>
        {"".join(f"<tr><td>{cat}</td><td>₹{amt:,}</td><td>{round(amt/total_expense*100) if total_expense > 0 else 0}%</td></tr>" for cat, amt in categories.items())}
    </table>
    
    <h2>📝 Recent Transactions</h2>
    <table>
        <tr><th>Date</th><th>Type</th><th>Category</th><th>Amount</th></tr>
        {"".join(f"<tr><td>{t.get('date', 'N/A')}</td><td>{t.get('type', 'expense')}</td><td>{t.get('category', 'Other')}</td><td>₹{t.get('amount', 0):,}</td></tr>" for t in transactions[-20:])}
    </table>
    
    <p style="text-align: center; color: #64748B; margin-top: 40px;">
        Generated by MoneyViya • Your Smart Financial Friend
    </p>
</body>
</html>"""
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html)
    except Exception as e:
        print(f"Report error: {e}")
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=f"<html><body><h1>Report Error</h1><p>Unable to generate report. Please try again.</p></body></html>")


@app.get("/download/export/{phone:path}")
async def download_csv(phone: str, format: str = "csv"):
    """Download transactions as CSV"""
    try:
        from urllib.parse import unquote
        
        phone = unquote(phone)
        if not phone.startswith("+"):
            phone = "+" + phone
        
        user = user_repo.get_user(phone)
        transactions = transaction_repo.get_transactions(phone) or []
    
        # Create CSV
        csv_lines = ["Date,Type,Category,Amount,Description"]
        for t in transactions:
            date = t.get("date", "")
            txn_type = t.get("type", "expense")
            category = t.get("category", "Other")
            amount = t.get("amount", 0)
            description = t.get("description", "").replace(",", " ")
            csv_lines.append(f"{date},{txn_type},{category},{amount},{description}")
        
        csv_content = "\n".join(csv_lines)
        
        from fastapi.responses import Response
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=MoneyViya_transactions_{phone.replace('+', '')}.csv"}
        )
    except Exception as e:
        print(f"Export error: {e}")
        from fastapi.responses import Response
        return Response(content="Date,Type,Category,Amount,Description\n", media_type="text/csv")


# ================= DASHBOARD API ENDPOINTS =================
@app.post("/transaction")
async def add_transaction(txn: TransactionPayload):
    """Add a transaction from dashboard"""
    from datetime import datetime
    
    user = user_repo.get_user(txn.phone)
    if not user:
        user = user_repo.create_user(txn.phone)
    
    transaction_repo.add_transaction(
        txn.phone,
        txn.amount,
        txn.type,
        txn.category or "other",
        description=txn.description or "Added from dashboard",
        source="DASHBOARD"
    )
    
    return {"success": True, "message": f"{txn.type.capitalize()} of ₹{txn.amount:,} recorded!"}


@app.get("/transactions/{phone:path}")
async def get_transactions(phone: str, limit: int = 50):
    """Get user transactions"""
    try:
        from urllib.parse import unquote
        phone = unquote(phone)
        if not phone.startswith("+"):
            phone = "+" + phone
        transactions = transaction_repo.get_transactions(phone) or []
        return {"transactions": transactions[-limit:]}
    except Exception as e:
        print(f"Transactions error: {e}")
        return {"transactions": []}


@app.post("/goal")
async def add_goal(goal: GoalPayload):
    """Add a financial goal"""
    from datetime import datetime
    
    user = user_repo.get_user(goal.phone)
    if not user:
        user = user_repo.create_user(goal.phone)
    
    goal_repo.add_goal(
        goal.phone,
        goal.goal_type,
        goal.target_amount,
        goal.target_date,
        name=goal.name or goal.goal_type
    )
    
    return {"success": True, "message": f"Goal '{goal.name or goal.goal_type}' created!"}


@app.get("/goals/{phone:path}")
async def get_goals(phone: str):
    """Get user goals"""
    try:
        from urllib.parse import unquote
        phone = unquote(phone)
        if not phone.startswith("+"):
            phone = "+" + phone
        goals = goal_repo.get_goals(phone) or []
        return {"goals": goals}
    except Exception as e:
        print(f"Goals error: {e}")
        return {"goals": []}


@app.get("/summary/{phone:path}")
async def get_summary(phone: str, period: str = "week"):
    """Get financial summary for dashboard"""
    try:
        from datetime import datetime, timedelta
        from urllib.parse import unquote
        
        # Decode phone if URL encoded
        phone = unquote(phone)
        if not phone.startswith("+"):
            phone = "+" + phone
        
        user = user_repo.get_user(phone)
        if not user:
            return {
                "income": 0,
                "expense": 0,
                "name": "User",
                "daily_budget": 0,
                "chart_data": {"labels": [], "income": [], "expense": []},
                "categories": {}
            }
        
        transactions = transaction_repo.get_transactions(phone) or []
        
        # Calculate totals
        total_income = sum(t.get("amount", 0) for t in transactions if t.get("type") == "income")
        total_expense = sum(t.get("amount", 0) for t in transactions if t.get("type") == "expense")
        
        # Categories
        categories = {}
        for t in transactions:
            if t.get("type") == "expense":
                cat = t.get("category", "Other")
                categories[cat] = categories.get(cat, 0) + t.get("amount", 0)
        
        # Chart data (last 7 days)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        income_data = [0] * 7
        expense_data = [0] * 7
        
        return {
            "income": total_income,
            "expense": total_expense,
            "name": user.get("name", "User"),
            "daily_budget": max(0, (total_income - total_expense) // 30),
            "chart_data": {
                "labels": days,
                "income": income_data,
                "expense": expense_data
            },
            "categories": categories
        }
    except Exception as e:
        print(f"Summary error: {e}")
        return {
            "income": 0,
            "expense": 0,
            "name": "User",
            "daily_budget": 0,
            "chart_data": {"labels": [], "income": [], "expense": []},
            "categories": {}
        }


# ================= TESTIMONIALS =================
testimonials_db = []


@app.get("/testimonials")
def get_testimonials():
    """Get all testimonials"""
    return {"testimonials": testimonials_db[-20:]}  # Last 20

@app.post("/testimonials")
def add_testimonial(data: dict):
    """Add a new testimonial"""
    phone = data.get("phone", "")
    content = data.get("content", "")
    
    if content:
        user = user_repo.get_user(phone)
        name = user.get("name", "Anonymous") if user else "Anonymous"
        
        testimonials_db.append({
            "name": name,
            "role": "MoneyViya User",
            "content": content,
            "saved": "Growing",
            "improvement": "Better"
        })
    
    return {"success": True}


# ================= OTP AUTHENTICATION =================
# Store for pending WhatsApp messages (bot will pick these up)
pending_whatsapp_messages = {}

@app.post("/api/v2/auth/send-otp")
async def send_otp(payload: OTPSendPayload):
    """Send OTP via WhatsApp for web login"""
    phone = payload.phone.strip()
    
    # Ensure + prefix
    if not phone.startswith("+"):
        phone = "+91" + phone.replace(" ", "").replace("-", "")
    
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Store OTP with expiry (5 minutes)
    otp_store[phone] = {
        "otp": otp,
        "expires": datetime.now().timestamp() + 300
    }
    
    # Create OTP message
    otp_message = f"""🔐 *MoneyViya Login OTP*

Your verification code is: *{otp}*

⏰ This code expires in 5 minutes.
⚠️ Do not share this code with anyone!

If you didn't request this, please ignore."""
    
    # Store pending message for WhatsApp bot to send
    pending_whatsapp_messages[phone] = {
        "message": otp_message,
        "created": datetime.now().timestamp()
    }
    
    print(f"[OTP] Generated for {phone}: {otp}")
    
    # Return success - bot will send the message
    return {
        "success": True, 
        "message": "OTP will be sent to your WhatsApp",
        "phone": phone
    }


# Endpoint for bot to fetch pending messages
@app.get("/api/pending-messages/{phone}")
async def get_pending_messages(phone: str):
    """Get pending messages for a phone number (used by WhatsApp bot)"""
    if not phone.startswith("+"):
        phone = "+" + phone
    
    if phone in pending_whatsapp_messages:
        msg = pending_whatsapp_messages.pop(phone)
        return {"has_message": True, "message": msg["message"]}
    
    return {"has_message": False}


@app.post("/api/send-whatsapp")
async def queue_whatsapp_message(phone: str, message: str):
    """Queue a message to be sent via WhatsApp bot"""
    if not phone.startswith("+"):
        phone = "+" + phone
    
    pending_whatsapp_messages[phone] = {
        "message": message,
        "created": datetime.now().timestamp()
    }
    
    return {"success": True, "queued": True}


@app.post("/api/v2/auth/verify-otp")
async def verify_otp(payload: OTPVerifyPayload):
    """Verify OTP and login user"""
    phone = payload.phone.strip()
    otp = payload.otp.strip()
    
    # Ensure + prefix
    if not phone.startswith("+"):
        phone = "+91" + phone.replace(" ", "").replace("-", "")
    
    stored = otp_store.get(phone)
    
    if not stored:
        raise HTTPException(status_code=400, detail="OTP not found. Please request a new OTP.")
    
    if datetime.now().timestamp() > stored["expires"]:
        del otp_store[phone]
        raise HTTPException(status_code=400, detail="OTP expired. Please request a new OTP.")
    
    if stored["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP. Please try again.")
    
    # OTP verified - delete it
    del otp_store[phone]
    
    # Get or create user
    user = user_repo.ensure_user(phone)
    
    return {
        "success": True,
        "message": "Login successful!",
        "user": {
            "phone": phone,
            "name": user.get("name", "User"),
            "onboarding_complete": user.get("onboarding_complete", False)
        }
    }


# ================= OCR BILL PROCESSING =================
async def process_bill_image(media_url: str, media_type: str, phone: str) -> dict:
    """Process bill images and PDFs using OCR and OpenAI Vision"""
    import requests
    import re
    
    try:
        print(f"[OCR] Processing image from {media_url}")
        
        # Download the image
        response = requests.get(media_url, timeout=30)
        if not response.ok:
            return None
        
        image_data = response.content
        
        # Try OpenAI Vision first (better accuracy)
        if openai_service.is_available():
            import base64
            
            # Convert to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Use GPT-4 Vision to analyze the bill
            vision_prompt = """Analyze this bill/receipt image and extract:
1. Total amount (number only)
2. Type: Is this an EXPENSE (payment/purchase), INCOME (salary slip/payment received), or SAVINGS (bank deposit/investment)?
3. Category: food, transport, shopping, bills, health, salary, freelance, investment, other
4. Merchant/Source name
5. Date if visible

Respond ONLY with JSON like:
{"amount": 500, "type": "expense", "category": "food", "merchant": "Swiggy", "date": "2024-01-08"}

If you cannot read the amount clearly, set amount to 0."""

            try:
                api_response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY', '')}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": vision_prompt},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                ]
                            }
                        ],
                        "max_tokens": 300
                    },
                    timeout=60
                )
                
                if api_response.ok:
                    result = api_response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Extract JSON from response
                    import json
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        bill_data = json.loads(json_match.group())
                        
                        amount = bill_data.get("amount", 0)
                        txn_type = bill_data.get("type", "expense").lower()
                        category = bill_data.get("category", "other")
                        merchant = bill_data.get("merchant", "Unknown")
                        
                        if amount > 0:
                            # Record the transaction
                            transaction_repo.add_transaction(
                                phone, amount, txn_type, category,
                                description=f"Bill from {merchant}",
                                source="WHATSAPP_IMAGE"
                            )
                            
                            # Get user's preferred language
                            user = user_repo.get_user(phone)
                            lang = user.get("preferred_language", "english") if user else "english"
                            
                            if txn_type == "income":
                                emoji = "💰"
                                type_text = "income" if lang == "english" else "आय"
                            elif txn_type == "savings":
                                emoji = "💾"
                                type_text = "savings" if lang == "english" else "बचत"
                            else:
                                emoji = "💸"
                                type_text = "expense" if lang == "english" else "खर्च"
                            
                            if lang == "hindi":
                                msg = f"""📄 *बिल स्कैन किया गया!*

{emoji} ₹{amount:,} {type_text} रिकॉर्ड किया
🏪 {merchant}
📁 श्रेणी: {category}

✅ आपके खाते में जोड़ दिया गया!"""
                            else:
                                msg = f"""📄 *Bill Scanned Successfully!*

{emoji} ₹{amount:,} {type_text} recorded
🏪 From: {merchant}
📁 Category: {category}

✅ Added to your account!"""
                            
                            return {"success": True, "message": msg, "amount": amount, "type": txn_type}
                        else:
                            return {"success": False, "message": "❌ Could not extract amount from the bill. Please send clearer image or type the amount manually."}
                            
            except Exception as e:
                print(f"[OCR] Vision API error: {e}")
        
        # Fallback: Try pytesseract OCR
        try:
            from PIL import Image
            import pytesseract
            from io import BytesIO
            
            img = Image.open(BytesIO(image_data))
            text = pytesseract.image_to_string(img)
            
            # Extract amounts from text
            amounts = re.findall(r'₹?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:rs|rupees|inr)?', text.lower())
            
            if amounts:
                # Take the largest amount (likely total)
                amount = max([float(a.replace(',', '')) for a in amounts])
                
                # Try to determine if expense or income
                income_words = ['salary', 'credited', 'received', 'income', 'payment received']
                expense_words = ['total', 'amount', 'bill', 'invoice', 'payment', 'paid']
                
                text_lower = text.lower()
                is_income = any(w in text_lower for w in income_words)
                txn_type = "income" if is_income else "expense"
                
                transaction_repo.add_transaction(
                    phone, int(amount), txn_type, "other",
                    description="Scanned from bill",
                    source="WHATSAPP_IMAGE"
                )
                
                return {
                    "success": True,
                    "message": f"📄 *Bill Scanned!*\n\n{'💰' if is_income else '💸'} ₹{int(amount):,} {txn_type} recorded!\n\n✅ Added to your account!",
                    "amount": int(amount),
                    "type": txn_type
                }
        except Exception as e:
            print(f"[OCR] Pytesseract error: {e}")
        
        return {"success": False, "message": "❌ Could not read the bill. Please send a clearer image or type the amount manually."}
        
    except Exception as e:
        print(f"[OCR] Error: {e}")
        return None

# ================= TWILIO WHATSAPP WEBHOOK =================
from fastapi import Form, Request

@app.post("/webhook/whatsapp-incoming")
async def twilio_webhook(request: Request):
    """Direct Twilio WhatsApp webhook - receives form data and responds via Twilio"""
    from twilio.rest import Client
    from twilio.twiml.messaging_response import MessagingResponse
    
    try:
        # Parse form data from Twilio
        form_data = await request.form()
        
        phone = form_data.get("From", "").replace("whatsapp:", "").strip()
        message = form_data.get("Body", "hi").strip()
        media_url = form_data.get("MediaUrl0")
        media_type = form_data.get("MediaContentType0", "")
        
        if not phone:
            return {"error": "No phone number"}
        
        if not phone.startswith("+"):
            phone = "+" + phone
            
        print(f"[Twilio] Received from {phone}: {message}")
        
        # Handle voice message
        msg_type = "voice" if media_type and "audio" in media_type else "text"
        if msg_type == "voice" and media_url and openai_service.is_available():
            try:
                transcribed = transcribe_voice(media_url)
                if transcribed:
                    message = transcribed
                    print(f"[Voice] Transcribed: {message}")
            except Exception as e:
                print(f"[Voice] Transcription failed: {e}")
        
        # Handle image/PDF - OCR and bill extraction
        is_image = media_type and ("image" in media_type)
        is_pdf = media_type and ("pdf" in media_type or "document" in media_type)
        
        if (is_image or is_pdf) and media_url:
            try:
                ocr_result = await process_bill_image(media_url, media_type, phone)
                if ocr_result:
                    # Return the result directly
                    reply_text = ocr_result["message"]
                    
                    # Send response
                    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
                    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
                    
                    if account_sid and auth_token:
                        try:
                            client = Client(account_sid, auth_token)
                            msg = client.messages.create(
                                from_="whatsapp:+14155238886",
                                to=f"whatsapp:{phone}",
                                body=reply_text
                            )
                        except Exception as e:
                            print(f"[Twilio] Error sending: {e}")
                    
                    twiml = MessagingResponse()
                    return str(twiml)
            except Exception as e:
                print(f"[OCR] Error processing image: {e}")
        
        # Update user activity
        user_repo.update_activity(phone)
        
        # Get or create user
        user = user_repo.ensure_user(phone)
        language = user.get("preferred_language", user.get("language", "english"))
        
        # Map to short code for voice service
        lang_map = {"english": "en", "hindi": "hi", "tamil": "ta", "telugu": "te", "kannada": "kn"}
        lang_code = lang_map.get(language, "en")
        
        # Initialize reply_text
        reply_text = ""
        
        # Check if onboarding is complete
        if not user.get("onboarding_complete"):
            result = await handle_onboarding(phone, message, user)
            reply_text = result["text"]
        else:
            # First try keyword-based detection for common commands
            msg_lower = message.lower().strip()
            intent = None
            
            # Greeting keywords (Hi, Hello, etc.)
            if msg_lower in ["hi", "hello", "hey", "hii", "hiii", "namaste", "नमस्ते"]:
                intent = {"intent": "GREETING", "raw_message": message}
            
            # Balance/Summary keywords
            elif any(kw in msg_lower for kw in ["balance", "summary", "total", "status", "how much", "kitna", "कितना", "बैलेंस"]):
                intent = {"intent": "SUMMARY_QUERY", "raw_message": message}
            
            # Report keywords
            elif any(kw in msg_lower for kw in ["report", "monthly", "weekly", "रिपोर्ट"]):
                intent = {"intent": "DASHBOARD_QUERY", "raw_message": message}
            
            # Help keywords  
            elif any(kw in msg_lower for kw in ["help", "commands", "what can", "मदद", "सहायता"]):
                intent = {"intent": "HELP_QUERY", "raw_message": message}
            
            # Income keywords
            elif any(kw in msg_lower for kw in ["earned", "received", "salary", "income", "got paid", "कमाया", "मिला"]):
                # Extract amount
                import re
                amounts = re.findall(r'\d+', msg_lower)
                amount = int(amounts[0]) if amounts else 0
                intent = {"intent": "INCOME_ENTRY", "amount": amount, "category": "salary", "raw_message": message}
            
            # Expense keywords
            elif any(kw in msg_lower for kw in ["spent", "paid", "expense", "bought", "खर्च", "दिया"]):
                import re
                amounts = re.findall(r'\d+', msg_lower)
                amount = int(amounts[0]) if amounts else 0
                # Try to detect category
                category = "other"
                if any(f in msg_lower for f in ["food", "eat", "lunch", "dinner", "breakfast", "खाना"]):
                    category = "food"
                elif any(f in msg_lower for f in ["transport", "uber", "ola", "auto", "bus", "train", "petrol", "यात्रा"]):
                    category = "transport"
                elif any(f in msg_lower for f in ["shop", "buy", "purchase", "खरीद"]):
                    category = "shopping"
                elif any(f in msg_lower for f in ["bill", "rent", "electricity", "recharge", "बिल"]):
                    category = "bills"
                intent = {"intent": "EXPENSE_ENTRY", "amount": amount, "category": category, "raw_message": message}
            
            # Savings keywords
            elif any(kw in msg_lower for kw in ["saved", "saving", "बचत", "जमा"]):
                import re
                amounts = re.findall(r'\d+', msg_lower)
                amount = int(amounts[0]) if amounts else 0
                intent = {"intent": "SAVINGS_ENTRY", "amount": amount, "raw_message": message}
            
            # Goal keywords
            elif any(kw in msg_lower for kw in ["goal", "target", "लक्ष्य"]):
                intent = {"intent": "GOAL_QUERY", "raw_message": message}
            
            # Investment advice
            elif any(kw in msg_lower for kw in ["invest", "sip", "mutual fund", "निवेश", "investment"]):
                intent = {"intent": "INVESTMENT_QUERY", "raw_message": message}
            
            # Reminder keywords
            elif any(kw in msg_lower for kw in ["reminder", "remind", "daily reminder", "set reminder", "याद", "अलार्म"]):
                intent = {"intent": "REMINDER", "raw_message": message}
            
            # Advice keywords
            elif any(kw in msg_lower for kw in ["advice", "suggest", "recommendation", "सुझाव", "tip"]):
                intent = {"intent": "ADVICE_REQUEST", "raw_message": message}
            # If no keyword match, try OpenAI or fallback NLP
            if intent is None:
                if openai_service.is_available():
                    ai_intent = understand_message(message, language)
                    
                    # Handle MULTIPLE_TRANSACTIONS
                    if ai_intent.get("intent") == "MULTIPLE_TRANSACTIONS":
                        transactions = ai_intent.get("transactions", [])
                        responses = []
                        
                        for txn in transactions:
                            txn_type = txn.get("type", "expense")
                            amount = txn.get("amount", 0)
                            category = txn.get("category", "other")
                            description = txn.get("description", "")
                            
                            if amount > 0:
                                transaction_repo.add_transaction(
                                    phone, amount, txn_type, category,
                                    description=description, source="WHATSAPP"
                                )
                                
                                if txn_type == "income":
                                    responses.append(f"✅ ₹{amount:,} income recorded!")
                                else:
                                    responses.append(f"✅ ₹{amount:,} expense recorded!")
                        
                        summary = transaction_repo.get_daily_summary(phone)
                        
                        if language == "hindi":
                            reply_text = "\n".join(responses) + f"\n\n📊 आज की कमाई: ₹{summary['income']:,}\n💸 आज का खर्च: ₹{summary['expense']:,}\n💰 आज की बचत: ₹{summary['net']:,}"
                        else:
                            reply_text = "\n".join(responses) + f"\n\n📊 Today's Income: ₹{summary['income']:,}\n💸 Today's Expense: ₹{summary['expense']:,}\n💰 Today's Savings: ₹{summary['net']:,}"
                    else:
                        intent = {
                            "intent": ai_intent.get("intent", "OTHER"),
                            "amount": ai_intent.get("amount"),
                            "category": ai_intent.get("category"),
                            "description": ai_intent.get("description"),
                            "raw_message": message
                        }
                else:
                    # Fallback to local NLP
                    intent = nlp_service.detect_intent(message, lang_code)
            
            # Route intent if we have one and didn't already set reply_text
            if intent and not reply_text:
                response = await route_intent(phone, intent, user, lang_code)
                reply_text = response["message"]
        
        print(f"[Twilio] Sending reply to {phone}: {reply_text[:100]}...")
        
        # Send response via Twilio
        account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        
        if account_sid and auth_token:
            try:
                client = Client(account_sid, auth_token)
                msg = client.messages.create(
                    from_="whatsapp:+14155238886",
                    to=f"whatsapp:{phone}",
                    body=reply_text
                )
                print(f"[Twilio] Message sent: {msg.sid}")
            except Exception as e:
                print(f"[Twilio] Error sending: {e}")
        
        # Return TwiML response (empty to avoid double reply)
        twiml = MessagingResponse()
        return str(twiml)

    except Exception as e:
        print(f"[Twilio Webhook] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# ================= BAILEYS/NODE.JS BOT ENDPOINT =================
@app.post("/api/message")
async def baileys_message(request: Request):
    """
    Simple endpoint for Baileys/Node.js WhatsApp bot
    Accepts form data, returns JSON with reply text
    """
    try:
        # Parse form data
        form_data = await request.form()
        
        phone = form_data.get("From", "").replace("whatsapp:", "").strip()
        message = form_data.get("Body", "hi").strip()
        
        if not phone:
            return {"reply": "Error: No phone number provided"}
        
        if not phone.startswith("+"):
            phone = "+" + phone
            
        print(f"[Baileys] Message from {phone}: {message}")
        
        # Update user activity
        user_repo.update_activity(phone)
        
        # Get or create user
        user = user_repo.ensure_user(phone)
        language = user.get("preferred_language", user.get("language", "english"))
        
        # Process message
        reply_text = ""
        
        # Check if onboarding is complete
        if not user.get("onboarding_complete"):
            result = await handle_onboarding(phone, message, user)
            reply_text = result["text"]
        else:
            # Process regular message using intent detection
            msg_lower = message.lower().strip()
            intent = None
            
            # Language change command (works anytime)
            if any(kw in msg_lower for kw in ["change language", "change lang", "भाषा बदलें", "மொழி மாற்று"]):
                user_repo.update_user(phone, {"onboarding_step": "language", "onboarding_complete": False})
                ai_onboarding = get_ai_onboarding(user_repo)
                return {"reply": ai_onboarding.get_welcome_message()}
            
            # Greeting keywords
            if msg_lower in ["hi", "hello", "hey", "hii", "namaste", "good morning", "good evening"]:
                intent = {"intent": "GREETING", "raw_message": message}
            
            # Balance/Summary keywords
            elif any(kw in msg_lower for kw in ["balance", "summary", "total", "status", "kitna", "बैलेंस", "कितना", "இருப்பு"]):
                intent = {"intent": "SUMMARY_QUERY", "raw_message": message}
            
            # Report keywords
            elif any(kw in msg_lower for kw in ["report", "monthly", "weekly", "रिपोर्ट", "अवलोकन", "dashboard"]):
                intent = {"intent": "DASHBOARD_QUERY", "raw_message": message}
            
            # Help keywords
            elif any(kw in msg_lower for kw in ["help", "commands", "मदद", "how to", "क्या कर सकते", "உதவி"]):
                intent = {"intent": "HELP_QUERY", "raw_message": message}
            
            # Income keywords (earned, received, salary, got)
            elif any(kw in msg_lower for kw in ["earned", "received", "salary", "got", "income", "कमाया", "मिला", "சம்பாதித்தேன்"]):
                import re
                amounts = re.findall(r'[\d,]+', message)
                if amounts:
                    amount = int(amounts[0].replace(',', ''))
                    intent = {"intent": "INCOME_ENTRY", "amount": amount, "raw_message": message}
            
            # Expense keywords (spent, paid, bought, kharch)
            elif any(kw in msg_lower for kw in ["spent", "paid", "bought", "expense", "खर्च", "दिया", "செலவு"]):
                import re
                amounts = re.findall(r'[\d,]+', message)
                if amounts:
                    amount = int(amounts[0].replace(',', ''))
                    # Try to detect category
                    category = "other"
                    if any(w in msg_lower for w in ["food", "खाना", "lunch", "dinner", "restaurant"]):
                        category = "food"
                    elif any(w in msg_lower for w in ["petrol", "fuel", "gas"]):
                        category = "petrol"
                    elif any(w in msg_lower for w in ["transport", "uber", "ola", "cab", "auto"]):
                        category = "transport"
                    elif any(w in msg_lower for w in ["mobile", "recharge", "phone"]):
                        category = "mobile_recharge"
                    elif any(w in msg_lower for w in ["shopping", "clothes", "amazon", "flipkart"]):
                        category = "shopping"
                    elif any(w in msg_lower for w in ["medicine", "doctor", "hospital"]):
                        category = "healthcare"
                    intent = {"intent": "EXPENSE_ENTRY", "amount": amount, "category": category, "raw_message": message}
            
            # Budget keywords
            elif any(kw in msg_lower for kw in ["budget", "limit", "बजट", "பட்ஜெட்"]):
                intent = {"intent": "BUDGET_QUERY", "raw_message": message}
            
            # Goal keywords
            elif any(kw in msg_lower for kw in ["goal", "target", "लक्ष्य", "இலக்கு", "savings goal"]):
                intent = {"intent": "GOAL_QUERY", "raw_message": message}
            
            # Advice keywords
            elif any(kw in msg_lower for kw in ["advice", "suggest", "tip", "सलाह", "ஆலோசனை", "invest"]):
                intent = {"intent": "ADVICE_REQUEST", "raw_message": message}
            
            # Use OpenAI for complex messages
            if not intent and openai_service.is_available():
                intent = understand_message(message, language)
            
            # Fallback to NLP service
            if not intent:
                intent = nlp_service.parse_message(message, language)
            
            # Route to handler
            if intent:
                result = await route_intent(phone, intent, user, language)
                reply_text = result.get("message", str(result))
            else:
                reply_text = "I didn't understand. Type 'help' for commands."
        
        print(f"[Baileys] Reply: {reply_text[:100]}...")
        return {"reply": reply_text}
        
    except Exception as e:
        print(f"[Baileys] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"reply": f"Error: {str(e)}"}


# ================= WHATSAPP CLOUD API WEBHOOK (Meta Official) =================
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "MoneyViya_webhook_verify_2024")

@app.get("/webhook/whatsapp-cloud")
async def verify_whatsapp_webhook(request: Request):
    """Verify webhook for WhatsApp Cloud API (Meta)"""
    params = dict(request.query_params)
    
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    print(f"[WhatsApp Cloud] Verification: mode={mode}, token={token}")
    
    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        print("[WhatsApp Cloud] Webhook verified!")
        return int(challenge)
    else:
        print("[WhatsApp Cloud] Verification failed!")
        raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook/whatsapp-cloud")
async def handle_whatsapp_cloud_webhook(request: Request):
    """Handle incoming messages from WhatsApp Cloud API (Meta Official)"""
    try:
        data = await request.json()
        print(f"[WhatsApp Cloud] Received: {data}")
        
        # Extract message data
        entry = data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        # Check if it's a message
        if "messages" not in value:
            return {"status": "ok"}
        
        messages = value.get("messages", [])
        contacts = value.get("contacts", [])
        
        for msg in messages:
            msg_type = msg.get("type")
            phone = msg.get("from")  # Sender's phone number
            msg_id = msg.get("id")
            
            # Get sender name
            sender_name = "Friend"
            for contact in contacts:
                if contact.get("wa_id") == phone:
                    sender_name = contact.get("profile", {}).get("name", "Friend")
            
            # Extract message text
            message_text = ""
            if msg_type == "text":
                message_text = msg.get("text", {}).get("body", "")
            elif msg_type == "interactive":
                # Button/list reply
                interactive = msg.get("interactive", {})
                if interactive.get("type") == "button_reply":
                    message_text = interactive.get("button_reply", {}).get("title", "")
                elif interactive.get("type") == "list_reply":
                    message_text = interactive.get("list_reply", {}).get("title", "")
            elif msg_type == "audio":
                message_text = "[Voice message]"
            elif msg_type == "image":
                message_text = msg.get("image", {}).get("caption", "[Image]")
            else:
                message_text = f"[{msg_type}]"
            
            if not message_text:
                continue
            
            print(f"[WhatsApp Cloud] Message from +{phone}: {message_text}")
            
            # Ensure phone has + prefix
            if not phone.startswith("+"):
                phone = "+" + phone
            
            # Update user activity
            user_repo.update_activity(phone)
            user = user_repo.ensure_user(phone)
            
            # Set name if we have it
            if sender_name and sender_name != "Friend" and not user.get("name"):
                user_repo.update_user(phone, {"name": sender_name})
                user["name"] = sender_name
            
            language = user.get("preferred_language", user.get("language", "english"))
            
            # ===== USE MONEYVIYA AI AGENT =====
            # The agent handles everything: onboarding, NLP, goals, reminders
            try:
                reply_text = moneyviya_agent.process_message(phone, message_text, user)
                
                # Save any updates to user data
                user_repo.update_user(phone, user)
                
            except Exception as agent_error:
                print(f"[Agent Error] {agent_error}")
                # Fallback to basic response
                reply_text = "I'm having trouble understanding. Try:\n• 'spent 50 on tea'\n• 'earned 500 delivery'\n• 'help' for menu"
            
            # Send reply via WhatsApp Cloud API
            if reply_text and whatsapp_cloud_service.is_available():
                clean_phone = phone.replace("+", "")
                result = whatsapp_cloud_service.send_text_message(clean_phone, reply_text)
                print(f"[WhatsApp Cloud] Reply sent: {result}")
        
        return {"status": "ok"}
        
    except Exception as e:
        print(f"[WhatsApp Cloud] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

# ================= MAIN WEBHOOK (for n8n) =================
@app.post("/webhook")
async def handle_webhook(payload: WebhookPayload):
    """Main webhook endpoint for n8n WhatsApp integration"""
    
    phone = payload.phone
    message = payload.message.strip()
    msg_type = payload.message_type
    voice_url = payload.voice_url
    
    # Handle voice message - transcribe using OpenAI Whisper
    if msg_type == "voice" and voice_url and openai_service.is_available():
        try:
            transcribed = transcribe_voice(voice_url)
            if transcribed:
                message = transcribed
                print(f"[Voice] Transcribed: {message}")
        except Exception as e:
            print(f"[Voice] Transcription failed: {e}")
    
    # Update user activity
    user_repo.update_activity(phone)
    
    # Get or create user
    user = user_repo.ensure_user(phone)
    language = user.get("preferred_language", user.get("language", "english"))
    
    # Map to short code for voice service
    lang_map = {"english": "en", "hindi": "hi", "tamil": "ta", "telugu": "te", "kannada": "kn"}
    lang_code = lang_map.get(language, "en")
    
    # Check if onboarding is complete
    if not user.get("onboarding_complete"):
        result = await handle_onboarding(phone, message, user)
        return {
            "phone": phone,
            "reply_text": result["text"],
            "voice_path": result.get("voice_path"),
            "voice_url": None,
            "intent": "ONBOARDING",
            "language": language
        }
    
    # Use OpenAI for better NLP understanding if available
    if openai_service.is_available():
        ai_intent = understand_message(message, language)
        
        # Handle MULTIPLE_TRANSACTIONS (both income and expense in one message)
        if ai_intent.get("intent") == "MULTIPLE_TRANSACTIONS":
            transactions = ai_intent.get("transactions", [])
            responses = []
            
            for txn in transactions:
                txn_type = txn.get("type", "expense")
                amount = txn.get("amount", 0)
                category = txn.get("category", "other")
                description = txn.get("description", "")
                
                if amount > 0:
                    # Record transaction
                    transaction_repo.add_transaction(
                        phone, amount, txn_type, category,
                        description=description, source="WHATSAPP"
                    )
                    
                    if txn_type == "income":
                        responses.append(f"✅ ₹{amount:,} income recorded!")
                    else:
                        responses.append(f"✅ ₹{amount:,} expense recorded!")
            
            # Get today's summary
            summary = transaction_repo.get_daily_summary(phone)
            
            if language == "hindi":
                reply = "\n".join(responses) + f"\n\n📊 आज की कमाई: ₹{summary['income']:,}\n💸 आज का खर्च: ₹{summary['expense']:,}\n💰 आज की बचत: ₹{summary['net']:,}"
            else:
                reply = "\n".join(responses) + f"\n\n📊 Today's Income: ₹{summary['income']:,}\n💸 Today's Expense: ₹{summary['expense']:,}\n💰 Today's Savings: ₹{summary['net']:,}"
            
            enhanced = create_response(phone, reply, lang_code)
            return {
                "phone": phone,
                "reply_text": enhanced["reply_text"],
                "voice_path": enhanced.get("voice_path"),
                "voice_url": None,
                "intent": "MULTIPLE_TRANSACTIONS",
                "language": language,
                "achievements": enhanced.get("achievements", [])
            }
        
        # Single transaction or query
        intent = {
            "intent": ai_intent.get("intent", "OTHER"),
            "amount": ai_intent.get("amount"),
            "category": ai_intent.get("category"),
            "description": ai_intent.get("description"),
            "raw_message": message
        }
    else:
        # Fallback to local NLP
        intent = nlp_service.detect_intent(message, lang_code)
    
    # Route based on intent
    response = await route_intent(phone, intent, user, lang_code)
    
    # Create enhanced response with voice
    enhanced = create_response(phone, response["message"], lang_code)
    
    return {
        "phone": phone,
        "reply_text": enhanced["reply_text"],
        "voice_path": enhanced.get("voice_path"),
        "voice_url": None,
        "intent": intent["intent"],
        "language": language,
        "achievements": enhanced.get("achievements", [])
    }



async def handle_onboarding(phone: str, message: str, user: dict) -> dict:
    """Handle AI-powered onboarding flow with NLP understanding"""
    
    # Refetch user to get latest data
    user = user_repo.get_user(phone) or user
    
    # Use AI-powered onboarding service (falls back gracefully if no OpenAI key)
    ai_onboarding = get_ai_onboarding(user_repo)
    
    # Process the onboarding step with AI understanding
    result = ai_onboarding.process_onboarding(phone, message, user)
    
    # Refetch user after update
    updated_user = user_repo.get_user(phone) or user
    language = updated_user.get("preferred_language", updated_user.get("language", "english"))
    
    # Map language codes
    lang_code_map = {
        "english": "en", "hindi": "hi", "tamil": "ta", 
        "telugu": "te", "kannada": "kn", "marathi": "mr"
    }
    voice_lang = lang_code_map.get(language, "en")
    
    # If onboarding is completed, set up default reminders and budget
    if result.get("step") == "completed":
        reminder_repo.setup_default_reminders(phone)
        
        # Create monthly budget based on their income and savings target
        monthly_income = updated_user.get("monthly_income", 20000)
        savings_target = updated_user.get("savings_target", int(monthly_income * 0.2))
        monthly_budget = monthly_income - savings_target
        
        budget_repo.create_monthly_budget(
            phone, 
            datetime.now().strftime("%Y-%m"),
            monthly_budget
        )
        
        # Award first achievement
        gamification_service.check_achievements(phone)
    
    # Generate voice for the response
    reply_text = result.get("text", "")
    voice_path = None
    
    try:
        voice_path = voice_service.generate_voice(
            smart_reply_service._text_to_voice_text(reply_text),
            voice_lang
        )
    except Exception as e:
        print(f"Voice generation failed: {e}")
    
    return {"text": reply_text, "voice_path": voice_path, "language": language}



async def route_intent(phone: str, intent: dict, user: dict, language: str) -> dict:
    """Route to appropriate handler based on intent"""
    
    intent_type = intent["intent"]
    
    handlers = {
        "GREETING": handle_greeting,
        "INCOME_ENTRY": handle_income,
        "EXPENSE_ENTRY": handle_expense,
        "SAVINGS_ENTRY": handle_savings,
        "SUMMARY_QUERY": handle_summary,
        "INVESTMENT_QUERY": handle_investment_advice,
        "LOAN_QUERY": handle_loan_advice,
        "BUDGET_QUERY": handle_budget,
        "GOAL_QUERY": handle_goals,
        "HELP_QUERY": handle_help,
        "FRAUD_REPORT": handle_fraud_report,
        "ADVICE_REQUEST": handle_advice,
        "DASHBOARD_QUERY": handle_dashboard,
        "REMINDER": handle_reminder,
    }
    
    handler = handlers.get(intent_type, handle_unknown)
    return await handler(phone, intent, user, language)


async def handle_greeting(phone: str, intent: dict, user: dict, language: str) -> dict:
    import random
    from datetime import datetime
    
    name = user.get("name", "Friend")
    
    # Motivational quotes
    motivational_quotes = {
        "english": [
            "💡 Small savings today = Big wealth tomorrow!",
            "🌟 Every rupee saved is a rupee earned!",
            "💪 Financial freedom starts with one step!",
            "🎯 Your goals are closer than you think!",
            "📈 Consistency beats intensity in saving!",
            "🌱 Plant your money seeds today!",
            "✨ Dream big, save bigger!",
            "🚀 Your financial journey is amazing!"
        ],
        "hindi": [
            "💡 आज की छोटी बचत = कल की बड़ी दौलत!",
            "🌟 हर बचाया रुपया कमाया रुपया है!",
            "💪 आर्थिक आज़ादी एक कदम से शुरू होती है!",
            "🎯 आपके लक्ष्य नजदीक हैं!",
            "📈 लगातारता हमेशा जीतती है!",
            "🌱 आज अपने पैसे के बीज बोएं!",
            "✨ बड़े सपने देखो, बड़ा बचाओ!"
        ],
        "tamil": [
            "💡 இன்றைய சிறிய சேமிப்பு = நாளைய பெரிய செல்வம்!",
            "🌟 சேமிக்கும் ஒவ்வொரு ரூபாயும் சம்பாதிக்கும் ரூபாய்!",
            "💪 நிதி சுதந்திரம் ஒரு அடியில் தொடங்குகிறது!"
        ]
    }
    
    # Get time-based greeting
    hour = datetime.now().hour
    if hour < 12:
        time_greeting = {"english": "Good morning", "hindi": "सुप्रभात", "tamil": "காலை வணக்கம்"}
    elif hour < 17:
        time_greeting = {"english": "Good afternoon", "hindi": "नमस्ते", "tamil": "மதிய வணக்கம்"}
    else:
        time_greeting = {"english": "Good evening", "hindi": "शुभ संध्या", "tamil": "மாலை வணக்கம்"}
    
    greeting = time_greeting.get(language, time_greeting["english"])
    quotes = motivational_quotes.get(language, motivational_quotes["english"])
    quote = random.choice(quotes)
    
    # Get financial summary
    daily = financial_advisor.get_daily_message(phone)
    level = gamification_service.get_user_level(phone)
    
    if language == "hindi":
        reply = f"""🙏 *{greeting}, {name}!*

वापस स्वागत है! आप आर्थिक रूप से बढ़ रहे हैं! 📈

{quote}

{level['icon']} स्तर: {level['level']} ({level['points']} अंक)

{daily['message']}

💬 कमांड्स: बैलेंस, रिपोर्ट, खर्च, कमाई, भाषा बदलें"""
    elif language == "tamil":
        reply = f"""🙏 *{greeting}, {name}!*

மீண்டும் வரவேற்கிறோம்! நீங்கள் நிதி ரீதியாக வளர்ந்து கொண்டிருக்கிறீர்கள்! 📈

{quote}

{level['icon']} நிலை: {level['level']} ({level['points']} புள்ளிகள்)

{daily['message']}"""
    else:
        reply = f"""🙏 *{greeting}, {name}!*

Welcome back! You're growing financially! 📈

{quote}

{level['icon']} Level: {level['level']} ({level['points']} points)

{daily['message']}

💬 Commands: balance, report, spent, earned, change language"""
    
    return {"message": reply}


async def handle_income(phone: str, intent: dict, user: dict, language: str) -> dict:
    amount = intent.get("amount")
    if not amount:
        return {"message": message_builder.get_message("error_amount", language)}
    
    category = intent.get("category") or "other_income"
    
    transaction_repo.add_transaction(phone, amount, "income", category, "MANUAL")
    user_repo.add_income(phone, amount)
    
    # Get today's total
    today = transaction_repo.get_daily_summary(phone)
    
    if language == "hi":
        reply = f"✅ ₹{amount:,} आमदनी दर्ज!\n\n📊 आज की कुल आय: ₹{today['income']:,}"
    elif language == "ta":
        reply = f"✅ ₹{amount:,} வருமானம் பதிவாகியது!\n\n📊 இன்றைய மொத்த வருமானம்: ₹{today['income']:,}"
    elif language == "te":
        reply = f"✅ ₹{amount:,} ఆదాయం నమోదైంది!\n\n📊 ఈరోజు మొత్తం ఆదాయం: ₹{today['income']:,}"
    else:
        reply = f"✅ ₹{amount:,} income recorded!\n\n📊 Today's total income: ₹{today['income']:,}"
    
    return {"message": reply}


async def handle_expense(phone: str, intent: dict, user: dict, language: str) -> dict:
    amount = intent.get("amount")
    if not amount:
        return {"message": message_builder.get_message("error_amount", language)}
    
    category = intent.get("category") or "other_expense"
    
    transaction_repo.add_transaction(phone, amount, "expense", category, "MANUAL")
    user_repo.add_expense(phone, amount)
    
    budget_result = budget_repo.record_expense(phone, category, amount)
    remaining = budget_result["budget"].get("remaining", 0) if budget_result.get("budget") else 0
    daily = budget_result["budget"].get("remaining", 0) / max(1, 30 - datetime.now().day) if budget_result.get("budget") else 0
    
    emoji = gamification_service._load_achievements  # Just to prevent unused import
    cat_emoji = dashboard_service._get_category_emoji(category)
    
    if language == "hi":
        reply = f"✅ ₹{amount:,} खर्च दर्ज!\n{cat_emoji} श्रेणी: {category}\n\n"
        reply += f"📊 इस महीने बचा: ₹{max(0, remaining):,}\n💵 रोज़ का बजट: ₹{int(max(0, daily)):,}"
        if remaining < 0:
            reply += "\n\n⚠️ सावधान! बजट खत्म हो गया!"
    else:
        reply = f"✅ ₹{amount:,} expense recorded!\n{cat_emoji} Category: {category.title()}\n\n"
        reply += f"📊 Remaining this month: ₹{max(0, remaining):,}\n💵 Daily budget: ₹{int(max(0, daily)):,}"
        if remaining < 0:
            reply += "\n\n⚠️ Warning! Budget exceeded!"
    
    # Add budget alerts
    if budget_result.get("alerts"):
        for alert in budget_result["alerts"]:
            if alert["type"] == "budget_warning":
                if language == "hi":
                    reply += f"\n\n🚨 {alert['percentage']}% बजट खर्च हो गया!"
                else:
                    reply += f"\n\n🚨 {alert['percentage']}% of budget used!"
    
    return {"message": reply}


async def handle_savings(phone: str, intent: dict, user: dict, language: str) -> dict:
    amount = intent.get("amount")
    if not amount:
        return {"message": message_builder.get_message("error_amount", language)}
    
    current = user.get("current_savings", 0)
    user_repo.update_user(phone, {"current_savings": current + amount, "emergency_fund": current + amount})
    
    goals = goal_repo.get_user_goals(phone, "active")
    if goals:
        goal_repo.add_contribution(goals[0]["id"], amount, "Savings deposit")
    
    transaction_repo.add_transaction(phone, amount, "savings", "savings", "MANUAL")
    
    if language == "hi":
        reply = f"✅ ₹{amount:,} बचत में जोड़ा गया!\n\n💰 कुल बचत: ₹{current + amount:,}"
        if goals:
            reply += f"\n🎯 '{goals[0]['name']}' में जोड़ा गया"
    else:
        reply = f"✅ ₹{amount:,} added to savings!\n\n💰 Total savings: ₹{current + amount:,}"
        if goals:
            reply += f"\n🎯 Added to '{goals[0]['name']}' goal"
    
    return {"message": reply}


async def handle_summary(phone: str, intent: dict, user: dict, language: str) -> dict:
    today = transaction_repo.get_daily_summary(phone)
    budget = budget_repo.get_budget_status(phone)
    
    daily_budget = budget.get("daily_allowance", 1000) if budget.get("status") != "no_budget" else 1000
    
    # Build visual summary
    income_bar = dashboard_service._make_mini_bar(min(100, today['income'] / max(daily_budget * 2, 1) * 100))
    expense_bar = dashboard_service._make_mini_bar(min(100, today['expense'] / max(daily_budget, 1) * 100))
    
    if language == "hi":
        status = "✅ बजट में!" if today['expense'] <= daily_budget else "⚠️ बजट से ज़्यादा!"
        reply = f"""📊 *आज का सारांश*
━━━━━━━━━━━━━━━━━

💰 आय: ₹{today['income']:,}
{income_bar}

💸 खर्च: ₹{today['expense']:,}
{expense_bar}

📈 नेट: ₹{today['net']:,}
🎯 रोज़ का बजट: ₹{daily_budget:,}

{status}"""
    else:
        status = "✅ Within budget!" if today['expense'] <= daily_budget else "⚠️ Over budget!"
        reply = f"""📊 *Today's Summary*
━━━━━━━━━━━━━━━━━

💰 Income: ₹{today['income']:,}
{income_bar}

💸 Expenses: ₹{today['expense']:,}
{expense_bar}

📈 Net: ₹{today['net']:,}
🎯 Daily budget: ₹{daily_budget:,}

{status}"""
    
    return {"message": reply}


async def handle_dashboard(phone: str, intent: dict, user: dict, language: str) -> dict:
    """Handle dashboard/monthly report request"""
    
    dashboard = dashboard_service.generate_monthly_dashboard(phone)
    
    if dashboard.get("error"):
        return {"message": dashboard["error"]}
    
    return {"message": dashboard["dashboard"]}


async def handle_investment_advice(phone: str, intent: dict, user: dict, language: str) -> dict:
    advice = financial_advisor.get_investment_recommendations(phone)
    
    if advice.get("error"):
        return {"message": advice["error"]}
    
    alloc = advice.get("allocation", {})
    
    if language == "hi":
        reply = f"""📈 *निवेश सुझाव*
━━━━━━━━━━━━━━━━━

💰 निवेश योग्य: ₹{advice['recommended_investment']:,}/महीना
🎯 रिस्क प्रोफाइल: {advice['risk_profile']}

*आवंटन:*
🛡️ सुरक्षित: {alloc.get('safe', 0)}%
⚖️ मध्यम: {alloc.get('moderate', 0)}%
📈 ग्रोथ: {alloc.get('growth', 0)}%

*शुरुआत करें:*
₹{advice['sip_amount']:,}/महीना SIP - Index Fund

💡 छोटी शुरुआत करें, धीरे-धीरे बढ़ाएं!"""
    else:
        reply = f"""📈 *Investment Advice*
━━━━━━━━━━━━━━━━━

💰 Investable: ₹{advice['recommended_investment']:,}/month
🎯 Risk Profile: {advice['risk_profile'].title()}

*Allocation:*
🛡️ Safe: {alloc.get('safe', 0)}%
⚖️ Moderate: {alloc.get('moderate', 0)}%
📈 Growth: {alloc.get('growth', 0)}%

*Start with:*
₹{advice['sip_amount']:,}/month SIP in Index Fund

💡 Start small, increase gradually!"""
    
    return {"message": reply}


async def handle_loan_advice(phone: str, intent: dict, user: dict, language: str) -> dict:
    loan = financial_advisor.get_loan_eligibility(phone, intent.get("amount"))
    
    if not loan.get("eligible"):
        reason = loan.get("reason", "Not eligible")
        if language == "hi":
            return {"message": f"❌ {reason}\n\n💡 सुझाव: {loan.get('suggestion', 'पहले आय बढ़ाएं')}"}
        return {"message": f"❌ {reason}\n\n💡 Tip: {loan.get('suggestion', 'Focus on income first')}"}
    
    options = ""
    for o in loan.get("loan_options", [])[:3]:
        options += f"  • {o['tenure_months']} months: ₹{o['max_amount']:,} (EMI ₹{o['emi']:,})\n"
    
    if language == "hi":
        reply = f"""🏦 *लोन पात्रता*
━━━━━━━━━━━━━━━━━

✅ पात्र: हाँ
💰 अधिकतम EMI: ₹{loan['max_emi_capacity']:,}/महीना
🏷️ अधिकतम लोन: ₹{loan['max_loan_amount']:,}
⚠️ जोखिम स्तर: {loan['risk_level']}

*विकल्प:*
{options}
💡 EMI को आय के 30% से नीचे रखें!"""
    else:
        reply = f"""🏦 *Loan Eligibility*
━━━━━━━━━━━━━━━━━

✅ Eligible: Yes
💰 Max EMI: ₹{loan['max_emi_capacity']:,}/month
🏷️ Max Loan: ₹{loan['max_loan_amount']:,}
⚠️ Risk Level: {loan['risk_level']}

*Options:*
{options}
💡 Keep EMI below 30% of income!"""
    
    return {"message": reply}


async def handle_budget(phone: str, intent: dict, user: dict, language: str) -> dict:
    budget = budget_repo.get_budget_status(phone)
    
    if budget.get("status") == "no_budget":
        if language == "hi":
            return {"message": "कोई बजट सेट नहीं है। अपनी मासिक आय बताएं बजट बनाने के लिए।"}
        return {"message": "No budget set. Tell me your monthly income to create one."}
    
    health = budget.get("health", {})
    used_bar = dashboard_service._make_progress_bar(budget['total_spent'], budget['total_budget'])
    
    if language == "hi":
        reply = f"""📊 *बजट स्थिति*
━━━━━━━━━━━━━━━━━

{health.get('emoji', '')} {health.get('message', '')}

{used_bar}
💰 बजट: ₹{budget['total_budget']:,}
💸 खर्च: ₹{budget['total_spent']:,} ({budget['percent_used']}%)
📅 बचा: ₹{budget['remaining']:,}
💵 रोज़: ₹{budget['daily_allowance']:,}

📅 {budget['days_left']} दिन बचे हैं"""
    else:
        reply = f"""📊 *Budget Status*
━━━━━━━━━━━━━━━━━

{health.get('emoji', '')} {health.get('message', '')}

{used_bar}
💰 Budget: ₹{budget['total_budget']:,}
💸 Spent: ₹{budget['total_spent']:,} ({budget['percent_used']}%)
📅 Remaining: ₹{budget['remaining']:,}
💵 Daily: ₹{budget['daily_allowance']:,}

📅 {budget['days_left']} days left"""
    
    return {"message": reply}


async def handle_goals(phone: str, intent: dict, user: dict, language: str) -> dict:
    summary = goal_repo.get_goal_summary(phone)
    
    if summary["total_goals"] == 0:
        if language == "hi":
            return {"message": "कोई गोल सेट नहीं है। बताइए आप किसके लिए बचत करना चाहते हैं!"}
        return {"message": "No goals set yet. Tell me what you're saving for!"}
    
    goals_text = ""
    for g in summary.get("goals", [])[:5]:
        bar = dashboard_service._make_progress_bar(g['saved_amount'], g['target_amount'], 15)
        goals_text += f"\n{g['icon']} *{g['name']}*\n{bar}\n₹{g['saved_amount']:,} / ₹{g['target_amount']:,} ({g['progress_percent']}%)\n"
    
    if language == "hi":
        reply = f"""🎯 *आपके गोल्स*
━━━━━━━━━━━━━━━━━
{goals_text}
📈 कुल प्रगति: {summary['overall_progress']}%
💰 मासिक आवश्यक: ₹{summary['monthly_required']:,}"""
    else:
        reply = f"""🎯 *Your Goals*
━━━━━━━━━━━━━━━━━
{goals_text}
📈 Overall Progress: {summary['overall_progress']}%
💰 Monthly Required: ₹{summary['monthly_required']:,}"""
    
    return {"message": reply}


async def handle_help(phone: str, intent: dict, user: dict, language: str) -> dict:
    level = gamification_service.get_user_level(phone)
    
    if language == "hi":
        reply = f"""📚 *MoneyViya मदद*
━━━━━━━━━━━━━━━━━

{level['icon']} *Level: {level['level']}* ({level['points']} pts)

💰 *पैसे ट्रैक करें:*
• "आज 500 कमाए"
• "पेट्रोल पर 100 खर्च"
• "200 बचाए"
• रसीद की फोटो भेजें

📊 *रिपोर्ट:*
• "आज का सारांश"
• "डैशबोर्ड"
• "मासिक रिपोर्ट"

💡 *सलाह:*
• "निवेश सलाह"
• "लोन एलिजिबिलिटी"
• "बजट दिखाओ"

🎯 *गोल्स:*
• "मेरे गोल्स"
• "बचत में 500 डालो"

🏥 *हेल्थ:*
• "फाइनेंशियल हेल्थ"
• "एडवाइस दो" """
    else:
        reply = f"""📚 *MoneyViya Help*
━━━━━━━━━━━━━━━━━

{level['icon']} *Level: {level['level']}* ({level['points']} pts)

💰 *Track Money:*
• "Earned 500 today"
• "Spent 100 on petrol"
• "Saved 200"
• Send receipt photo

📊 *Reports:*
• "Today's summary"
• "Dashboard"
• "Monthly report"

💡 *Advice:*
• "Investment advice"
• "Loan eligibility"
• "Show budget"

🎯 *Goals:*
• "My goals"
• "Add 500 to savings"

🏥 *Health:*
• "Financial health"
• "Give advice" """
    
    return {"message": reply}


async def handle_fraud_report(phone: str, intent: dict, user: dict, language: str) -> dict:
    if language == "hi":
        reply = """🛡️ *फ्रॉड रिपोर्ट*
━━━━━━━━━━━━━━━━━

मुझे दुख है कि आपके साथ फ्रॉड हुआ।

*तुरंत करें:*
1️⃣ स्कैमर का नंबर ब्लॉक करें
2️⃣ cybercrime.gov.in पर शिकायत करें
3️⃣ 1930 पर कॉल करें (साइबर हेल्पलाइन)
4️⃣ अपने बैंक को सूचित करें
5️⃣ FIR दर्ज करें

💪 सुरक्षित रहें! हम आपके साथ हैं।"""
    else:
        reply = """🛡️ *Fraud Report*
━━━━━━━━━━━━━━━━━

I'm sorry you experienced fraud.

*Take action now:*
1️⃣ Block the scammer's number
2️⃣ Report at cybercrime.gov.in
3️⃣ Call 1930 (Cyber Helpline)
4️⃣ Inform your bank immediately
5️⃣ File an FIR

💪 Stay safe! We're with you."""
    
    # Award fraud fighter badge
    gamification_service.check_achievements(phone)
    
    return {"message": reply}


async def handle_advice(phone: str, intent: dict, user: dict, language: str) -> dict:
    health = financial_advisor.get_financial_health_score(phone)
    advice_list = financial_advisor.get_personalized_advice(phone)
    insights = smart_insights.get_spending_insights(phone)
    prediction = smart_insights.predict_month_end_balance(phone)
    
    h = health["health"]
    health_bar = dashboard_service._make_health_bar(health['total_score'])
    
    if language == "hi":
        reply = f"""🏥 *फाइनेंशियल हेल्थ: {h['grade']}*
{health_bar} {health['total_score']}/100
{h['emoji']} {h['message']}
━━━━━━━━━━━━━━━━━

"""
        if advice_list:
            reply += "*सबसे ज़रूरी:*\n"
            for a in advice_list[:2]:
                reply += f"\n{a['icon']} *{a['title']}*\n{a['advice']}\n"
        
        if prediction.get('on_track') is not None:
            status = "✅ ट्रैक पर!" if prediction['on_track'] else "⚠️ ध्यान दें!"
            reply += f"\n📈 *महीने के अंत का अनुमान:*\n{status}\nअनुमानित बचत: ₹{prediction['projected_savings']:,}"
    else:
        reply = f"""🏥 *Financial Health: {h['grade']}*
{health_bar} {health['total_score']}/100
{h['emoji']} {h['message']}
━━━━━━━━━━━━━━━━━

"""
        if advice_list:
            reply += "*Top Priority:*\n"
            for a in advice_list[:2]:
                reply += f"\n{a['icon']} *{a['title']}*\n{a['advice']}\n"
        
        if prediction.get('on_track') is not None:
            status = "✅ On track!" if prediction['on_track'] else "⚠️ Needs attention!"
            reply += f"\n📈 *Month-end Projection:*\n{status}\nProjected savings: ₹{prediction['projected_savings']:,}"
    
    return {"message": reply}


async def handle_reminder(phone: str, intent: dict, user: dict, language: str) -> dict:
    """Handle reminder setup"""
    # Set up default daily reminders
    reminder_repo.setup_default_reminders(phone)
    
    if language == "hi":
        reply = """⏰ *रिमाइंडर सेट हो गया!*
━━━━━━━━━━━━━━━━━

मैं आपको हर दिन याद दिलाऊंगा:
• 🌅 सुबह 9 बजे - बजट चेक
• 🌙 रात 9 बजे - खर्च दर्ज करें

💡 खर्च दर्ज करने के लिए बस टाइप करें जैसे:
"100 खाने पर खर्च किया" """
    else:
        reply = """⏰ *Daily Reminder Set!*
━━━━━━━━━━━━━━━━━

I'll remind you daily:
• 🌅 9 AM - Check your budget
• 🌙 9 PM - Log your expenses

💡 To log expenses, just type like:
"spent 100 on food" """
    return {"message": reply}


async def handle_unknown(phone: str, intent: dict, user: dict, language: str) -> dict:
    """Handle unknown intents"""
    tip = gamification_service.get_random_tip(language)
    
    if language == "hi":
        reply = f'❓ समझ नहीं आया। "help" बोलें।\n\n{tip}'
    else:
        reply = f'❓ Didn\'t understand. Say "help".\n\n{tip}'
    
    return {"message": reply}


# ================= DASHBOARD API =================
@app.get("/dashboard/{phone}")
def get_dashboard(phone: str, month: str = None):
    """Get monthly dashboard"""
    return dashboard_service.generate_monthly_dashboard(phone, month)

@app.get("/dashboard/{phone}/weekly")
def get_weekly_dashboard(phone: str):
    """Get weekly dashboard"""
    return dashboard_service.generate_weekly_dashboard(phone)


# ================= GAMIFICATION API =================
@app.get("/user/{phone}/level")
def get_user_level(phone: str):
    """Get user's gamification level"""
    return gamification_service.get_user_level(phone)

@app.get("/user/{phone}/achievements")
def get_achievements(phone: str):
    """Get user's achievements"""
    user = user_repo.get_user(phone)
    if not user:
        raise HTTPException(404, "User not found")
    
    earned_ids = user.get("achievements", [])
    all_achievements = gamification_service._load_achievements()
    
    return {
        "earned": [all_achievements[aid] for aid in earned_ids if aid in all_achievements],
        "available": [a for aid, a in all_achievements.items() if aid not in earned_ids],
        "points": user.get("points", 0)
    }


# ================= INSIGHTS API =================
@app.get("/insights/{phone}")
def get_insights(phone: str):
    """Get smart insights"""
    return {
        "spending_insights": smart_insights.get_spending_insights(phone),
        "prediction": smart_insights.predict_month_end_balance(phone),
        "saving_opportunity": smart_insights.get_saving_opportunity(phone)
    }


# ================= OCR ENDPOINT =================
@app.post("/ocr")
async def process_image(file: UploadFile = File(...), phone: str = Form(...)):
    """Process receipt/document image"""
    if not OCR_AVAILABLE:
        raise HTTPException(400, "OCR not available")
    
    contents = await file.read()
    result = await document_processor.process_image(contents)
    
    if result.get("error"):
        return {"success": False, "error": result["error"]}
    
    amount = result.get("total_amount") or (result.get("amounts_found", [None])[0] if result.get("amounts_found") else None)
    
    if amount:
        txn_type = "expense" if result.get("type") == "receipt" else "income"
        transaction_repo.add_transaction(phone, amount, txn_type, "other_" + txn_type, "OCR")
        
        user = user_repo.get_user(phone)
        lang = user.get("language", "en") if user else "en"
        
        response = create_response(phone, f"✅ ₹{amount:,} {txn_type} recorded from image!", lang)
        return {"success": True, "amount": amount, "type": txn_type, **response}
    
    return {"success": False, "error": "No amount detected", "raw": result}


# ================= VOICE ENDPOINT =================
@app.get("/voice/{filename}")
async def get_voice(filename: str):
    """Serve voice file"""
    voice_path = VOICES_DIR / filename
    if voice_path.exists():
        return FileResponse(voice_path, media_type="audio/mpeg")
    raise HTTPException(404, "Voice file not found")


# ================= EXISTING ENDPOINTS =================
@app.post("/transaction")
async def add_transaction(payload: TransactionPayload):
    txn = transaction_repo.add_transaction(
        payload.phone, payload.amount, payload.type,
        payload.category or f"other_{payload.type}", "API", payload.description
    )
    if payload.type == "income":
        user_repo.add_income(payload.phone, payload.amount)
    else:
        user_repo.add_expense(payload.phone, payload.amount)
        budget_repo.record_expense(payload.phone, payload.category or "other_expense", payload.amount)
    return {"success": True, "transaction": txn}


@app.get("/user/{phone}")
def get_user(phone: str):
    user = user_repo.get_user(phone)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@app.get("/user/{phone}/summary")
def get_user_summary(phone: str):
    return user_repo.get_financial_summary(phone)


@app.get("/user/{phone}/health")
def get_financial_health(phone: str):
    return financial_advisor.get_financial_health_score(phone)


@app.get("/user/{phone}/advice")
def get_advice(phone: str):
    return financial_advisor.get_personalized_advice(phone)


@app.post("/goal")
async def create_goal(payload: GoalPayload):
    goal = goal_repo.create_goal(
        payload.phone, payload.goal_type, payload.target_amount,
        payload.target_date, payload.name
    )
    return {"success": True, "goal": goal}


@app.get("/goals/{phone}")
def get_goals(phone: str):
    return goal_repo.get_goal_summary(phone)


@app.post("/goal/{goal_id}/contribute")
async def contribute_to_goal(goal_id: str, amount: int, note: str = ""):
    result = goal_repo.add_contribution(goal_id, amount, note)
    if not result:
        raise HTTPException(404, "Goal not found")
    return {"success": True, "goal": result}


@app.get("/report/{phone}/daily")
def get_daily_report(phone: str, date: str = None):
    return transaction_repo.get_daily_summary(phone, date)


@app.get("/report/{phone}/monthly")
def get_monthly_report(phone: str, month: str = None):
    return transaction_repo.get_monthly_summary(phone, month)


@app.get("/report/{phone}/trends")
def get_trends(phone: str):
    return {
        "income_trend": transaction_repo.get_income_trend(phone),
        "spending_patterns": transaction_repo.get_spending_patterns(phone)
    }


@app.get("/reminders/due")
def get_due_reminders():
    return reminder_repo.get_due_reminders()


@app.post("/reminders/{reminder_id}/sent")
def mark_reminder_sent(reminder_id: str):
    return reminder_repo.mark_sent(reminder_id)


@app.get("/daily-message/{phone}")
def get_daily_message(phone: str):
    return financial_advisor.get_daily_message(phone)


@app.post("/fraud-check")
async def fraud_check(payload: TransactionPayload):
    txn = {
        "amount": payload.amount,
        "type": "debit" if payload.type == "expense" else "credit",
        "source": "API",
        "category": payload.category
    }
    
    basic = check_fraud(txn)
    advanced = advanced_fraud_check(payload.phone, txn)
    
    combined = {
        "decision": "BLOCK" if "BLOCK" in [basic["decision"], advanced["decision"]]
                    else "REVIEW" if "REVIEW" in [basic["decision"], advanced["decision"]]
                    else "ALLOW",
        "risk_score": round(basic["risk_score"] + advanced["risk_score"], 2),
        "reasons": basic["reasons"] + advanced["reasons"]
    }
    
    if combined["decision"] in ["BLOCK", "REVIEW"]:
        user = user_repo.get_user(payload.phone)
        lang = user.get("language", "en") if user else "en"
        alert_msg = message_builder.build_fraud_alert(payload.amount, combined["risk_score"], combined["reasons"], lang)
        notification_service.send_fraud_alert(payload.phone, alert_msg, combined["decision"] == "BLOCK")
    
    return combined


# ================= RUN =================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

