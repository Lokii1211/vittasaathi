"""
VittaSaathi v3.0 - WhatsApp Financial Advisor & Manager
========================================================
Complete API with voice replies, dashboards, gamification,
analytics, PDF reports, family finance, and more!
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import io
import re

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

# Agents
from agents.fraud_agent import check_fraud
from agents.advanced_fraud_agent import advanced_fraud_check

# Config
from config import SUPPORTED_LANGUAGES, VOICES_DIR


# ================= APP SETUP =================
app = FastAPI(
    title="VittaSaathi API",
    description="WhatsApp Financial Advisor for ALL Irregular Income Earners - v3.0",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include extended API routes
try:
    from extended_api import extended_router
    app.include_router(extended_router)
except ImportError as e:
    print(f"Warning: Extended API not loaded: {e}")

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
        "service": "VittaSaathi",
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


# ================= OTP AUTHENTICATION =================
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
    
    # Send OTP via Twilio WhatsApp
    try:
        from twilio.rest import Client
        
        account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        
        if account_sid and auth_token:
            client = Client(account_sid, auth_token)
            
            message = client.messages.create(
                from_="whatsapp:+14155238886",
                to=f"whatsapp:{phone}",
                body=f"🔐 Your VittaSaathi login OTP is: *{otp}*\n\nThis code expires in 5 minutes.\n\n⚠️ Do not share this code with anyone!"
            )
            
            print(f"[OTP] Sent to {phone}: {otp}")
            return {"success": True, "message": "OTP sent to your WhatsApp"}
        else:
            # Demo mode - just store OTP
            print(f"[OTP] Demo mode - OTP for {phone}: {otp}")
            return {"success": True, "message": "OTP sent to your WhatsApp", "demo_otp": otp}
            
    except Exception as e:
        print(f"[OTP] Error sending: {e}")
        # Return success anyway with demo OTP for testing
        return {"success": True, "message": "OTP sent to your WhatsApp", "demo_otp": otp}


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
            reply_text = result["text"]
        else:
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
                    # Single transaction or query
                    intent = {
                        "intent": ai_intent.get("intent", "OTHER"),
                        "amount": ai_intent.get("amount"),
                        "category": ai_intent.get("category"),
                        "description": ai_intent.get("description"),
                        "raw_message": message
                    }
                    response = await route_intent(phone, intent, user, lang_code)
                    reply_text = response["message"]
            else:
                # Fallback to local NLP
                intent = nlp_service.detect_intent(message, lang_code)
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
    """Handle smart onboarding flow with multi-language support, goals, and personalized plans"""
    
    # Get smart onboarding service
    smart_onboarding = get_smart_onboarding(user_repo)
    
    # Process the onboarding step
    result = smart_onboarding.process_onboarding(phone, message, user)
    
    language = user.get("preferred_language", user.get("language", "english"))
    
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
        updated_user = user_repo.get_user(phone)
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
    }
    
    handler = handlers.get(intent_type, handle_unknown)
    return await handler(phone, intent, user, language)


async def handle_greeting(phone: str, intent: dict, user: dict, language: str) -> dict:
    name = user.get("name", "Friend")
    daily = financial_advisor.get_daily_message(phone)
    
    # Add level info
    level = gamification_service.get_user_level(phone)
    level_text = f"\n\n{level['icon']} Level: {level['level']} ({level['points']} pts)"
    
    return {"message": daily["message"] + level_text}


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
        reply = f"""📚 *VittaSaathi मदद*
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
        reply = f"""📚 *VittaSaathi Help*
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


async def handle_unknown(phone: str, intent: dict, user: dict, language: str) -> dict:
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
