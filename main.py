from fastapi import FastAPI, File, UploadFile
import io
import re

# ======================
# OCR IMPORTS (FIX)
# ======================
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ======================
# UTILS
# ======================
from utils.transaction_parser import parse_transaction_message
from utils.storage import save_transaction
from utils.alert_manager import create_alert
from utils.alert_message import build_alert_message
from utils.language_manager import get_user_language
from utils.translator import translate_text
from utils.voice_generator import generate_voice
from utils.transaction_classifier import classify_transaction

from utils.income_aggregator import get_monthly_income
from utils.income_stability import calculate_income_stability
from utils.income_trends import classify_months
from utils.income_timeseries import build_daily_income_series
from utils.income_predictor import predict_next_month_income

from utils.emi_calculator import calculate_safe_emi
from utils.loan_eligibility import calculate_loan_eligibility

from agents.advanced_fraud_agent import advanced_fraud_check
from agents.fraud_agent import check_fraud

from utils.investment_eligibility import check_investment_eligibility
from utils.sip_calculator import calculate_sip_amount
from utils.investment_allocator import investment_allocation
from utils.investment_guard import should_pause_investment

from utils.intent_detector import detect_intent
from utils.cash_entry import save_cash_entry, calculate_monthly_estimate, CASH_DB
from utils.loan_engine import loan_amount_from_emi, loan_decision

from utils.user_store import get_user, create_user, save_name, save_language

from utils.whatsapp_sender import send_whatsapp_message
from utils.call_alert import make_fraud_call

# ======================
# APP
# ======================
app = FastAPI(title="VittaSaathi API", version="1.0")


@app.get("/")
def root():
    return {"message": "VittaSaathi backend running successfully"}


# ======================
# INTENT DETECTION
# ======================
@app.post("/intent-detect")
def intent_detect(payload: dict):
    text = payload.get("text", "")
    return detect_intent(text)


# ======================
# MESSAGE INGESTION
# ======================
@app.post("/ingest-message")
def ingest_message(message: str, user_id: str):

    txn = parse_transaction_message(message)
    if not txn:
        return {"status": "ignored", "reason": "Not a transaction"}

    category = classify_transaction(txn, message)
    txn["category"] = category

    basic_fraud = check_fraud(txn)
    advanced_fraud = advanced_fraud_check(user_id, txn)

    fraud_result = {
        "decision": (
            "BLOCK"
            if "BLOCK" in [basic_fraud["decision"], advanced_fraud["decision"]]
            else "REVIEW"
            if "REVIEW" in [basic_fraud["decision"], advanced_fraud["decision"]]
            else "ALLOW"
        ),
        "risk_score": round(
            basic_fraud["risk_score"] + advanced_fraud["risk_score"], 2
        ),
        "reasons": basic_fraud["reasons"] + advanced_fraud["reasons"],
    }

    save_transaction(txn, user_id)

    response = {
        "status": "transaction_processed",
        "transaction": txn,
        "fraud_analysis": fraud_result,
    }

    if fraud_result["decision"] in ["BLOCK", "REVIEW"]:
        alert_id = create_alert(user_id, txn, fraud_result)
        language, voice_enabled = get_user_language(user_id)

        base_message = build_alert_message(txn, fraud_result)
        translated_message = translate_text(base_message, language)

        if voice_enabled:
            generate_voice(translated_message, language)

        send_whatsapp_message("+919003360494", translated_message)

        if fraud_result["decision"] == "BLOCK":
            make_fraud_call(
                "+919003360494",
                "Suspicious transaction detected. Please check WhatsApp.",
            )

        response["alert_id"] = alert_id

    return response


# ======================
# CASH ENTRY (UPDATED)
# ======================
@app.post("/cash-entry")
def cash_entry(payload: dict):
    user_id = payload.get("user_id")
    amount = payload.get("amount")
    entry_type = payload.get("entry_type", "income")

    record = save_cash_entry(user_id, amount, entry_type)
    estimate = calculate_monthly_estimate(user_id)

    language = get_user_language(user_id)

    if language == "ta":
        reply = f"₹{amount} வெற்றிகரமாக சேமிக்கப்பட்டது ✅"
    elif language == "hi":
        reply = f"₹{amount} सफलतापूर्वक सेव किया गया ✅"
    elif language == "te":
        reply = f"₹{amount} విజయవంతంగా సేవ్ చేయబడింది ✅"
    else:
        reply = f"₹{amount} saved successfully ✅"

    return {
        "reply_text": reply,
        "record": record,
        "monthly_estimate": estimate,
    }


# ======================
# OCR CASH ENTRY (NEW)
# ======================
@app.post("/ocr-cash-entry")
async def ocr_cash_entry(file: UploadFile = File(...), user_id: str = ""):

    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    extracted_text = pytesseract.image_to_string(image)
    match = re.search(r"₹?\s?([\d,]+)", extracted_text)

    if not match:
        return {"reply_text": "❌ Amount not detected. Send clear image."}

    amount = int(match.group(1).replace(",", ""))
    save_cash_entry(user_id, amount, "income")

    language = get_user_language(user_id)
    if language == "ta":
        reply = f"✅ ₹{amount} வருமானம் சேமிக்கப்பட்டது"
    elif language == "hi":
        reply = f"✅ ₹{amount} आय दर्ज की गई"
    elif language == "te":
        reply = f"✅ ₹{amount} ఆదాయం నమోదు చేయబడింది"
    else:
        reply = f"✅ ₹{amount} income recorded successfully"

    return {"reply_text": reply}


# ======================
# INCOME / LOAN / INVESTMENT
# ======================
@app.get("/income-analysis/{user_id}")
def income_analysis(user_id: str):
    monthly_income = get_monthly_income(user_id)
    return {
        "monthly_income": monthly_income,
        "stability": calculate_income_stability(monthly_income),
        "trends": classify_months(monthly_income),
    }


@app.get("/loan-advice/{user_id}")
def loan_advice(user_id: str):
    monthly_income = calculate_monthly_estimate(user_id)
    if monthly_income <= 0:
        return {"reply_text": "❌ Not enough income data"}

    safe_emi = calculate_safe_emi(monthly_income)
    loan_amount = loan_amount_from_emi(safe_emi)

    return {
        "reply_text": f"Safe EMI ₹{safe_emi}, Estimated Loan ₹{loan_amount}"
    }


@app.get("/investment-advice/{user_id}")
def investment_advice(user_id: str):
    monthly_income = get_monthly_income(user_id)
    stability = calculate_income_stability(monthly_income)
    df = build_daily_income_series(user_id)
    prediction = predict_next_month_income(df)

    sip = calculate_sip_amount(prediction, stability["stability_score"])
    allocation = investment_allocation(stability["stability_score"])

    return {
        "reply_text": f"📈 SIP ₹{sip}, Allocation: {allocation}"
    }


# ======================
# USER ONBOARDING
# ======================
@app.get("/user-exists")
def user_exists(phone: str):
    user = get_user(phone)
    if not user:
        user = create_user(phone)

    return {
        "exists": user["onboarding_step"] == "DONE",
        "name": user.get("name"),
        "language": user.get("language"),
    }


@app.post("/save-name")
def save_user_name(payload: dict):
    save_name(payload["phone"], payload["name"])
    return {
        "reply_text": "Choose language:\n1 English\n2 Tamil\n3 Hindi\n4 Telugu"
    }


@app.post("/save-language")
def save_user_language(payload: dict):
    save_language(payload["phone"], payload["language_choice"])
    return {"reply_text": "🎉 Setup complete. How can I help?"}
