"""
VittaSaathi Extended API
========================
Additional endpoints for advanced features
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

# Import services
from services.analytics_service import analytics_service, report_generator
from services.pdf_service import pdf_service
from services.smart_categorization import smart_categorization, quick_actions
from services.family_service import family_service
from services.engagement_service import (
    challenge_service, peer_comparison_service, 
    streak_service, tips_service, bill_reminder_service
)
from services.education_service import financial_literacy_service
from services.export_service import export_service
from services.calendar_service import calendar_service
from services.backup_service import backup_service
from services.secure_backup_service import (
    encryption_service, secure_backup_service, scheduled_backup_service
)
from services.notification_service import notification_service
from services.cloud_backup_service import cloud_backup_service
from services.tfa_service import tfa_service
from services.webhook_service import webhook_service

from database.user_repository import user_repo


# Create router
extended_router = APIRouter(prefix="/api/v2", tags=["Extended Features"])


# ============== MODELS ==============
class FamilyCreate(BaseModel):
    creator_id: str
    name: str
    monthly_budget: int = 0

class FamilyExpense(BaseModel):
    family_id: str
    amount: int
    category: str
    description: str
    paid_by: str
    split_type: str = "equal"
    split_details: Optional[Dict] = None

class BillReminder(BaseModel):
    user_id: str
    bill_type: str
    amount: int
    due_date: int
    frequency: str = "monthly"

class ChallengeAction(BaseModel):
    user_id: str
    challenge_id: str


# ============== ANALYTICS ENDPOINTS ==============
@extended_router.get("/analytics/{user_id}/trends")
def get_expense_trends(user_id: str, months: int = 6):
    """Get expense trends over multiple months"""
    return analytics_service.get_expense_trends(user_id, months)

@extended_router.get("/analytics/{user_id}/breakdown")
def get_category_breakdown(user_id: str, month: str = None):
    """Get detailed category breakdown"""
    return analytics_service.get_category_breakdown(user_id, month)

@extended_router.get("/analytics/{user_id}/patterns")
def get_spending_patterns(user_id: str, days: int = 30):
    """Get daily spending patterns"""
    return analytics_service.get_daily_spending_pattern(user_id, days)

@extended_router.get("/analytics/{user_id}/prediction")
def get_month_end_prediction(user_id: str):
    """Get month-end financial prediction"""
    return analytics_service.predict_month_end(user_id)

@extended_router.get("/analytics/{user_id}/recurring")
def get_recurring_expenses(user_id: str):
    """Detect recurring/subscription expenses"""
    return analytics_service.detect_recurring_expenses(user_id)

@extended_router.get("/analytics/{user_id}/income-sources")
def get_income_sources(user_id: str, months: int = 3):
    """Analyze income sources"""
    return analytics_service.get_income_sources_analysis(user_id, months)

@extended_router.get("/analytics/{user_id}/savings-health")
def get_savings_health(user_id: str):
    """Get comprehensive savings health"""
    return analytics_service.get_savings_health(user_id)


# ============== REPORT ENDPOINTS ==============
@extended_router.get("/reports/{user_id}/text")
def get_text_report(user_id: str, month: str = None):
    """Get text-based monthly report"""
    return {"report": report_generator.generate_text_report(user_id, month)}

@extended_router.get("/reports/{user_id}/shareable")
def get_shareable_summary(user_id: str):
    """Get shareable summary for WhatsApp"""
    return {"summary": report_generator.generate_shareable_summary(user_id)}

@extended_router.get("/reports/{user_id}/pdf")
def get_pdf_report(user_id: str, month: str = None, background_tasks: BackgroundTasks = None):
    """Generate and download PDF report"""
    if not pdf_service.is_available():
        raise HTTPException(400, "PDF generation not available. Install reportlab: pip install reportlab")
    
    filepath = pdf_service.generate_monthly_report(user_id, month)
    
    if not filepath:
        raise HTTPException(404, "Could not generate report")
    
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=filepath.split("/")[-1] if "/" in filepath else filepath.split("\\")[-1]
    )

@extended_router.get("/reports/{user_id}/pdf/yearly")
def get_yearly_pdf_report(user_id: str, year: int = None):
    """Generate yearly summary PDF"""
    if not pdf_service.is_available():
        raise HTTPException(400, "PDF generation not available")
    
    filepath = pdf_service.generate_yearly_summary(user_id, year)
    
    if not filepath:
        raise HTTPException(404, "Could not generate report")
    
    return FileResponse(filepath, media_type="application/pdf")


# ============== SMART CATEGORIZATION ==============
@extended_router.get("/categorize")
def categorize_transaction(text: str, transaction_type: str = "expense", user_id: str = None):
    """Smart categorize a transaction"""
    category, confidence = smart_categorization.categorize(text, transaction_type, user_id)
    suggestions = smart_categorization.get_category_suggestions(text, transaction_type)
    
    return {
        "detected_category": category,
        "confidence": confidence,
        "suggestions": suggestions
    }

@extended_router.get("/categories")
def get_all_categories(transaction_type: str = "expense"):
    """Get all available categories"""
    return smart_categorization.get_all_categories(transaction_type)

@extended_router.get("/quick-action")
def parse_quick_action(text: str):
    """Parse quick action from text"""
    result = quick_actions.parse_quick_action(text)
    if result:
        return {"found": True, **result}
    return {"found": False}

@extended_router.get("/suggestions/{user_id}")
def get_action_suggestions(user_id: str):
    """Get smart action suggestions"""
    # Get recent transactions for context
    from database.transaction_repository import transaction_repo
    recent = transaction_repo.get_transactions(user_id, limit=5)
    
    return quick_actions.get_suggestions(recent)


# ============== FAMILY/GROUP ENDPOINTS ==============
@extended_router.post("/family")
def create_family(payload: FamilyCreate):
    """Create a new family/group"""
    family = family_service.create_family(
        payload.creator_id,
        payload.name,
        payload.monthly_budget
    )
    return {"success": True, "family": family}

@extended_router.post("/family/{family_id}/join")
def join_family(family_id: str, user_id: str):
    """Join an existing family"""
    return family_service.join_family(family_id, user_id)

@extended_router.post("/family/expense")
def add_family_expense(payload: FamilyExpense):
    """Add shared expense to family"""
    return family_service.add_shared_expense(
        payload.family_id,
        payload.amount,
        payload.category,
        payload.description,
        payload.paid_by,
        payload.split_type,
        payload.split_details
    )

@extended_router.get("/family/{family_id}/summary")
def get_family_summary(family_id: str):
    """Get family expense summary"""
    return family_service.get_family_summary(family_id)

@extended_router.get("/family/{family_id}/budget")
def get_family_budget(family_id: str):
    """Get family budget status"""
    return family_service.get_family_budget_status(family_id)

@extended_router.get("/family/{family_id}/settlements")
def get_settlements(family_id: str):
    """Get settlements needed between members"""
    return family_service.get_settlements_needed(family_id)

@extended_router.get("/family/{family_id}/contributions")
def get_contributions(family_id: str):
    """Get member contributions"""
    return family_service.get_member_contribution(family_id)

@extended_router.get("/family/{family_id}/report")
def get_family_report(family_id: str):
    """Get family report text"""
    return {"report": family_service.generate_family_report_text(family_id)}


# ============== CHALLENGES & ENGAGEMENT ==============
@extended_router.get("/challenges/{user_id}")
def get_available_challenges(user_id: str):
    """Get available savings challenges"""
    return challenge_service.get_available_challenges(user_id)

@extended_router.post("/challenges/start")
def start_challenge(payload: ChallengeAction):
    """Start a savings challenge"""
    return challenge_service.start_challenge(payload.user_id, payload.challenge_id)

@extended_router.get("/challenges/{user_id}/{challenge_id}/status")
def get_challenge_status(user_id: str, challenge_id: str):
    """Get challenge status"""
    return challenge_service.get_challenge_status(user_id, challenge_id)

@extended_router.post("/challenges/{user_id}/{challenge_id}/contribute")
def contribute_to_challenge(user_id: str, challenge_id: str, amount: int):
    """Contribute to a challenge"""
    return challenge_service.contribute_to_challenge(user_id, challenge_id, amount)

@extended_router.get("/peers/{user_id}")
def get_peer_comparison(user_id: str):
    """Get anonymous peer comparison"""
    return peer_comparison_service.get_peer_comparison(user_id)

@extended_router.get("/streak/{user_id}")
def update_streak(user_id: str):
    """Update and get user's streak"""
    return streak_service.update_streak(user_id)

@extended_router.get("/tips/{user_id}")
def get_tip(user_id: str):
    """Get a relevant financial tip"""
    return tips_service.get_tip(user_id)

@extended_router.get("/tips/{user_id}/contextual/{context}")
def get_contextual_tip(user_id: str, context: str):
    """Get contextual tip"""
    return tips_service.get_contextual_tip(user_id, context)


# ============== BILL REMINDERS ==============
@extended_router.post("/bills")
def add_bill_reminder(payload: BillReminder):
    """Add a bill reminder"""
    return bill_reminder_service.add_bill_reminder(
        payload.user_id,
        payload.bill_type,
        payload.amount,
        payload.due_date,
        payload.frequency
    )

@extended_router.get("/bills/{user_id}")
def get_bills(user_id: str):
    """Get all bill reminders"""
    return bill_reminder_service.get_bill_summary(user_id)

@extended_router.get("/bills/{user_id}/upcoming")
def get_upcoming_bills(user_id: str, days: int = 7):
    """Get upcoming bills"""
    return bill_reminder_service.get_upcoming_bills(user_id, days)

@extended_router.post("/bills/{user_id}/{bill_id}/paid")
def mark_bill_paid(user_id: str, bill_id: str, amount: int):
    """Mark a bill as paid"""
    return bill_reminder_service.mark_bill_paid(user_id, bill_id, amount)


# ============== FINANCIAL EDUCATION ==============
@extended_router.get("/learn/lesson")
def get_lesson(category: str = None, lesson_id: str = None):
    """Get a financial lesson"""
    lesson = financial_literacy_service.get_lesson(category, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    return lesson

@extended_router.get("/learn/categories")
def get_learning_categories():
    """Get all learning categories"""
    return financial_literacy_service.get_all_categories()

@extended_router.get("/learn/scam-alert")
def get_scam_alert(scam_id: str = None):
    """Get scam alert information"""
    return financial_literacy_service.get_scam_alert(scam_id)

@extended_router.get("/learn/schemes/{user_type}")
def get_relevant_schemes(user_type: str):
    """Get government schemes relevant to user type"""
    return financial_literacy_service.get_relevant_schemes(user_type)

@extended_router.get("/learn/daily/{user_id}")
def get_daily_learning(user_id: str):
    """Get daily learning content"""
    user = user_repo.get_user(user_id)
    language = user.get("language", "en") if user else "en"
    return financial_literacy_service.get_daily_learning(user_id, language)


# ============== VISUAL CHARTS (TEXT-BASED) ==============
@extended_router.get("/charts/{user_id}/expense-trend")
def get_expense_trend_chart(user_id: str, months: int = 6):
    """Get text-based expense trend chart"""
    trends = analytics_service.get_expense_trends(user_id, months)
    chart = analytics_service.get_text_chart(
        trends.get("total_expense", []),
        trends.get("months", [])
    )
    return {"chart": chart, "data": trends}

@extended_router.get("/charts/{user_id}/category-breakdown")
def get_category_chart(user_id: str, month: str = None):
    """Get category breakdown with visual bars"""
    breakdown = analytics_service.get_category_breakdown(user_id, month)
    
    chart = ""
    for cat in breakdown.get("categories", [])[:10]:
        chart += f"{cat['icon']} {cat['name']:<15} {cat['bar']} ₹{cat['amount']:,} ({cat['percentage']}%)\n"
    
    return {"chart": chart, "data": breakdown}

@extended_router.get("/charts/{user_id}/income-vs-expense")
def get_income_expense_chart(user_id: str, months: int = 3):
    """Get income vs expense comparison chart"""
    trends = analytics_service.get_expense_trends(user_id, months)
    
    chart = "📊 Income vs Expense\n"
    chart += "=" * 40 + "\n\n"
    
    for i, month in enumerate(trends.get("months", [])):
        income = trends["total_income"][i]
        expense = trends["total_expense"][i]
        
        income_bar = "█" * min(20, int(income / max(max(trends["total_income"]), 1) * 20))
        expense_bar = "█" * min(20, int(expense / max(max(trends["total_expense"]), 1) * 20))
        
        chart += f"{month}:\n"
        chart += f"  💰 Income:  {income_bar} ₹{income:,}\n"
        chart += f"  💸 Expense: {expense_bar} ₹{expense:,}\n"
        chart += f"  💾 Savings: ₹{income - expense:,}\n\n"
    
    return {"chart": chart}


# ============== EXPORT ENDPOINTS ==============
@extended_router.get("/export/{user_id}/csv/transactions")
def export_transactions_csv(user_id: str, start_date: str = None, end_date: str = None):
    """Export transactions to CSV file"""
    filepath = export_service.export_transactions_csv(user_id, start_date, end_date)
    
    if not filepath:
        raise HTTPException(404, "No transactions to export")
    
    return FileResponse(
        filepath,
        media_type="text/csv",
        filename=filepath.split("\\")[-1] if "\\" in filepath else filepath.split("/")[-1]
    )

@extended_router.get("/export/{user_id}/csv/summary")
def export_summary_csv(user_id: str, months: int = 6):
    """Export monthly summary to CSV"""
    filepath = export_service.export_monthly_summary_csv(user_id, months)
    
    if not filepath:
        raise HTTPException(404, "Could not generate export")
    
    return FileResponse(filepath, media_type="text/csv")

@extended_router.get("/export/{user_id}/csv/categories")
def export_categories_csv(user_id: str, month: str = None):
    """Export category breakdown to CSV"""
    filepath = export_service.export_category_breakdown_csv(user_id, month)
    
    if not filepath:
        raise HTTPException(404, "Could not generate export")
    
    return FileResponse(filepath, media_type="text/csv")

@extended_router.get("/export/{user_id}/excel")
def export_to_excel(user_id: str, months: int = 3):
    """Export all data to Excel workbook"""
    filepath = export_service.export_to_excel(user_id, months)
    
    if not filepath:
        raise HTTPException(400, "Excel export not available. Install pandas and openpyxl.")
    
    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filepath.split("\\")[-1] if "\\" in filepath else filepath.split("/")[-1]
    )

@extended_router.get("/export/{user_id}/csv-string")
def export_csv_string(user_id: str, data_type: str = "transactions"):
    """Get CSV data as string (for direct download)"""
    csv_data = export_service.export_to_csv_string(user_id, data_type)
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={data_type}_{user_id}.csv"}
    )

@extended_router.get("/export/formats")
def get_export_formats():
    """Get available export formats"""
    return export_service.get_export_formats()


# ============== CALENDAR ENDPOINTS ==============
@extended_router.get("/calendar/{user_id}")
def get_calendar(user_id: str, year: int = None, month: int = None):
    """Get financial calendar for a month"""
    return calendar_service.get_month_calendar(user_id, year, month)

@extended_router.get("/calendar/{user_id}/text")
def get_text_calendar(user_id: str, year: int = None, month: int = None):
    """Get text-based calendar for WhatsApp"""
    return {"calendar": calendar_service.get_text_calendar(user_id, year, month)}

@extended_router.get("/calendar/{user_id}/events")
def get_upcoming_events(user_id: str, days: int = 14):
    """Get upcoming financial events"""
    return calendar_service.get_upcoming_events(user_id, days)

@extended_router.get("/calendar/{user_id}/forecast")
def get_earning_forecast(user_id: str, days: int = 30):
    """Get income/expense forecast"""
    return calendar_service.get_earning_forecast(user_id, days)


# ============== SPECIAL DATES ==============
@extended_router.get("/calendar/special-dates/{year}")
def get_special_dates(year: int = 2026):
    """Get special financial dates for a year"""
    return calendar_service.special_dates.get(str(year), {})


# ============== BACKUP & RESTORE ==============
@extended_router.post("/backup/full")
def create_full_backup(backup_name: str = None):
    """Create full system backup"""
    return backup_service.create_full_backup(backup_name)

@extended_router.get("/backup/{user_id}")
def create_user_backup(user_id: str):
    """Create backup for a single user"""
    return backup_service.create_user_backup(user_id)

@extended_router.get("/backup/list")
def list_backups():
    """List all available backups"""
    return backup_service.list_backups()

@extended_router.post("/restore/full")
def restore_full_backup(backup_path: str):
    """Restore from full backup"""
    return backup_service.restore_full_backup(backup_path)

@extended_router.post("/restore/user")
def restore_user_backup(backup_path: str, merge: bool = False):
    """Restore single user backup"""
    return backup_service.restore_user_backup(backup_path, merge)

@extended_router.delete("/backup")
def delete_backup(backup_path: str):
    """Delete a backup file"""
    return backup_service.delete_backup(backup_path)

@extended_router.get("/backup/stats")
def get_data_statistics():
    """Get data storage statistics"""
    return backup_service.get_data_statistics()

@extended_router.post("/backup/cleanup")
def cleanup_old_backups(keep_count: int = 5):
    """Clean up old backups, keeping most recent"""
    return backup_service.cleanup_old_backups(keep_count)

@extended_router.get("/backup/{user_id}/export-json")
def export_user_json(user_id: str):
    """Export user data as JSON string"""
    json_data = backup_service.export_user_data_json(user_id)
    return Response(
        content=json_data,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=vittasaathi_user_{user_id}.json"}
    )

@extended_router.post("/backup/{user_id}/import-json")
def import_user_json(user_id: str, json_data: str):
    """Import user data from JSON string"""
    return backup_service.import_user_data_json(user_id, json_data)


# ============== ENCRYPTED BACKUP ==============
@extended_router.get("/secure-backup/available")
def check_encryption_available():
    """Check if encryption is available"""
    return {
        "available": encryption_service.is_available(),
        "message": "Install cryptography package for encryption" if not encryption_service.is_available() else "Encryption ready"
    }

@extended_router.post("/secure-backup/create")
def create_encrypted_backup(backup_name: str = None, password: str = None):
    """Create encrypted backup"""
    return secure_backup_service.create_encrypted_backup(backup_name, password)

@extended_router.post("/secure-backup/restore")
def restore_encrypted_backup(encrypted_path: str, password: str = None, key_id: str = None):
    """Restore from encrypted backup"""
    return secure_backup_service.restore_encrypted_backup(encrypted_path, password, key_id)

@extended_router.get("/secure-backup/list")
def list_encrypted_backups():
    """List all encrypted backups"""
    return secure_backup_service.list_encrypted_backups()

@extended_router.delete("/secure-backup")
def delete_encrypted_backup(encrypted_path: str, delete_key: bool = False):
    """Delete encrypted backup"""
    return secure_backup_service.delete_encrypted_backup(encrypted_path, delete_key)


# ============== SCHEDULED BACKUPS ==============
class ScheduleConfig(BaseModel):
    enabled: bool = True
    frequency: str = "daily"  # daily, weekly, monthly
    time: str = "02:00"
    retention_days: int = 30
    max_backups: int = 10
    encrypt: bool = False
    password: Optional[str] = None

@extended_router.post("/backup/schedule/configure")
def configure_backup_schedule(config: ScheduleConfig):
    """Configure scheduled backups"""
    return scheduled_backup_service.configure_schedule(
        enabled=config.enabled,
        frequency=config.frequency,
        time=config.time,
        retention_days=config.retention_days,
        max_backups=config.max_backups,
        encrypt=config.encrypt,
        password=config.password
    )

@extended_router.get("/backup/schedule/status")
def get_schedule_status():
    """Get backup schedule status"""
    return scheduled_backup_service.get_status()

@extended_router.post("/backup/schedule/run")
def run_scheduled_backup():
    """Manually run scheduled backup"""
    return scheduled_backup_service.run_scheduled_backup()

@extended_router.get("/backup/schedule/check")
def check_and_run_backup():
    """Check if backup is due and run if needed"""
    return scheduled_backup_service.check_and_run()

@extended_router.post("/backup/schedule/disable")
def disable_backup_schedule():
    """Disable scheduled backups"""
    return scheduled_backup_service.disable_schedule()


# ============== NOTIFICATIONS ==============
class NotificationConfig(BaseModel):
    whatsapp_sid: Optional[str] = None
    whatsapp_token: Optional[str] = None
    whatsapp_number: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: Optional[str] = None

@extended_router.post("/notifications/configure/whatsapp")
def configure_whatsapp_notifications(sid: str, token: str, from_number: str):
    """Configure WhatsApp notifications"""
    return notification_service.configure_whatsapp(sid, token, from_number)

@extended_router.post("/notifications/configure/email")
def configure_email_notifications(host: str, port: int, username: str, password: str, from_email: str):
    """Configure email notifications"""
    return notification_service.configure_email(host, port, username, password, from_email)

@extended_router.post("/notifications/admin")
def add_admin_contact(phone: str = None, email: str = None):
    """Add admin contact for notifications"""
    return notification_service.add_admin_contact(phone, email)

@extended_router.get("/notifications/status")
def get_notification_status():
    """Get notification configuration status"""
    return notification_service.get_config_status()

@extended_router.post("/notifications/test/whatsapp")
def test_whatsapp_notification(phone: str, message: str = "VittaSaathi test notification"):
    """Test WhatsApp notification"""
    return notification_service.send_whatsapp(phone, message)

@extended_router.post("/notifications/test/email")
def test_email_notification(email: str, subject: str = "VittaSaathi Test", body: str = "<h1>Test Email</h1>"):
    """Test email notification"""
    return notification_service.send_email(email, subject, body)


# ============== CLOUD BACKUP ==============
@extended_router.get("/cloud-backup/status")
def get_cloud_backup_status():
    """Get cloud backup status"""
    return cloud_backup_service.get_status()

@extended_router.post("/cloud-backup/configure/aws")
def configure_aws_backup(access_key: str, secret_key: str, region: str = "ap-south-1", bucket: str = "vittasaathi-backups"):
    """Configure AWS S3 backup"""
    return cloud_backup_service.configure_aws(access_key, secret_key, region, bucket)

@extended_router.post("/cloud-backup/configure/gcs")
def configure_gcs_backup(credentials_path: str, bucket: str = "vittasaathi-backups"):
    """Configure Google Cloud Storage backup"""
    return cloud_backup_service.configure_gcs(credentials_path, bucket)

@extended_router.post("/cloud-backup/upload")
def upload_to_cloud(local_path: str, provider: str = None):
    """Upload backup to cloud"""
    return cloud_backup_service.upload_backup(local_path, provider)

@extended_router.get("/cloud-backup/list")
def list_cloud_backups(provider: str = None):
    """List cloud backups"""
    return cloud_backup_service.list_cloud_backups(provider)

@extended_router.post("/cloud-backup/download")
def download_from_cloud(remote_key: str, local_path: str, provider: str = "aws"):
    """Download backup from cloud"""
    if provider == "aws":
        return cloud_backup_service.download_from_s3(remote_key, local_path)
    elif provider == "gcs":
        return cloud_backup_service.download_from_gcs(remote_key, local_path)
    return {"error": "Unknown provider"}

@extended_router.post("/cloud-backup/sync")
def sync_to_cloud(provider: str = None):
    """Sync all local backups to cloud"""
    return cloud_backup_service.sync_local_backups(provider)

@extended_router.delete("/cloud-backup")
def delete_cloud_backup(remote_key: str, provider: str = "aws"):
    """Delete backup from cloud"""
    if provider == "aws":
        return cloud_backup_service.delete_s3_backup(remote_key)
    elif provider == "gcs":
        return cloud_backup_service.delete_gcs_backup(remote_key)
    return {"error": "Unknown provider"}


# ============== TWO-FACTOR AUTHENTICATION ==============
@extended_router.get("/2fa/available")
def check_2fa_available():
    """Check if 2FA is available"""
    return {
        "available": tfa_service.is_available(),
        "message": "Install pyotp for 2FA: pip install pyotp" if not tfa_service.is_available() else "2FA ready"
    }

@extended_router.get("/2fa/{user_id}/status")
def get_2fa_status(user_id: str):
    """Get 2FA status for user"""
    return tfa_service.get_status(user_id)

@extended_router.post("/2fa/{user_id}/setup")
def setup_2fa(user_id: str):
    """Generate 2FA secret and QR code"""
    return tfa_service.generate_secret(user_id)

@extended_router.post("/2fa/{user_id}/enable")
def enable_2fa(user_id: str, code: str):
    """Enable 2FA after verifying code"""
    return tfa_service.verify_and_enable(user_id, code)

@extended_router.post("/2fa/{user_id}/verify")
def verify_2fa_code(user_id: str, code: str):
    """Verify 2FA code"""
    return tfa_service.verify_code(user_id, code)

@extended_router.post("/2fa/{user_id}/disable")
def disable_2fa(user_id: str, code: str):
    """Disable 2FA (requires valid code)"""
    return tfa_service.disable_2fa(user_id, code)

@extended_router.post("/2fa/{user_id}/backup-codes")
def regenerate_backup_codes(user_id: str, code: str):
    """Regenerate backup codes"""
    return tfa_service.regenerate_backup_codes(user_id, code)

@extended_router.post("/2fa/{user_id}/session")
def create_2fa_session(user_id: str, code: str, duration: int = 30):
    """Create authenticated session after 2FA"""
    verify = tfa_service.verify_code(user_id, code)
    if not verify.get("success"):
        return verify
    return tfa_service.create_session(user_id, duration)

@extended_router.get("/2fa/session/{session_id}")
def verify_2fa_session(session_id: str):
    """Verify if 2FA session is valid"""
    return tfa_service.verify_session(session_id)

@extended_router.delete("/2fa/session/{session_id}")
def invalidate_2fa_session(session_id: str):
    """Invalidate 2FA session (logout)"""
    return tfa_service.invalidate_session(session_id)

@extended_router.post("/2fa/{user_id}/otp/{action}")
def generate_action_otp(user_id: str, action: str, validity: int = 5):
    """Generate OTP for specific action"""
    result = tfa_service.generate_otp_for_action(user_id, action, validity)
    # Send via notification
    notification_service.send_2fa_code(user_id, result["code"], validity)
    return {"sent": True, "action": action, "validity_minutes": validity}

@extended_router.post("/2fa/{user_id}/otp/{action}/verify")
def verify_action_otp(user_id: str, action: str, code: str):
    """Verify OTP for action"""
    return tfa_service.verify_action_otp(user_id, action, code)


# ============== WEBHOOKS ==============
class WebhookCreate(BaseModel):
    event: str
    url: str
    secret: Optional[str] = None
    headers: Optional[dict] = None
    active: bool = True

@extended_router.get("/webhooks/events")
def get_webhook_events():
    """Get list of available webhook events"""
    return {"events": webhook_service.get_available_events()}

@extended_router.get("/webhooks")
def list_webhooks(event: str = None):
    """List all registered webhooks"""
    return webhook_service.list_webhooks(event)

@extended_router.post("/webhooks")
def register_webhook(webhook: WebhookCreate):
    """Register a new webhook"""
    return webhook_service.register_webhook(
        event=webhook.event,
        url=webhook.url,
        secret=webhook.secret,
        headers=webhook.headers,
        active=webhook.active
    )

@extended_router.get("/webhooks/{webhook_id}")
def get_webhook(webhook_id: str):
    """Get webhook by ID"""
    webhook = webhook_service.get_webhook(webhook_id)
    if not webhook:
        return {"error": "Webhook not found"}
    return webhook

@extended_router.patch("/webhooks/{webhook_id}")
def update_webhook(webhook_id: str, url: str = None, active: bool = None):
    """Update webhook"""
    kwargs = {}
    if url is not None:
        kwargs["url"] = url
    if active is not None:
        kwargs["active"] = active
    return webhook_service.update_webhook(webhook_id, **kwargs)

@extended_router.delete("/webhooks/{webhook_id}")
def delete_webhook(webhook_id: str):
    """Delete webhook"""
    return webhook_service.delete_webhook(webhook_id)

@extended_router.post("/webhooks/{webhook_id}/test")
def test_webhook(webhook_id: str):
    """Send test webhook"""
    return webhook_service.test_webhook(webhook_id)

@extended_router.get("/webhooks/{webhook_id}/logs")
def get_webhook_logs(webhook_id: str, limit: int = 50):
    """Get webhook logs"""
    return webhook_service.get_logs(webhook_id, limit)

@extended_router.get("/webhooks/stats/overview")
def get_webhook_stats():
    """Get webhook statistics"""
    return webhook_service.get_stats()

@extended_router.post("/webhooks/trigger/{event}")
def trigger_webhook_event(event: str, data: dict = None, user_id: str = None):
    """Manually trigger a webhook event"""
    return webhook_service.trigger(event, data or {}, user_id)


# ============== REPORT COMPARISON ENDPOINTS ==============
from datetime import datetime, timedelta
from database.transaction_repository import transaction_repo

@extended_router.get("/reports/{phone}/weekly-comparison")
def get_weekly_comparison(phone: str):
    """Get weekly report with comparison to last week"""
    today = datetime.now()
    
    # This week (Monday to Sunday)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Last week
    start_last_week = start_of_week - timedelta(days=7)
    end_last_week = start_of_week - timedelta(days=1)
    
    # Get transactions
    this_week_txns = transaction_repo.get_transactions_in_range(
        phone, start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d")
    )
    last_week_txns = transaction_repo.get_transactions_in_range(
        phone, start_last_week.strftime("%Y-%m-%d"), end_last_week.strftime("%Y-%m-%d")
    )
    
    # Calculate this week
    this_income = sum(t.get("amount", 0) for t in this_week_txns if t.get("type") == "income")
    this_expense = sum(t.get("amount", 0) for t in this_week_txns if t.get("type") == "expense")
    
    # Calculate last week
    last_income = sum(t.get("amount", 0) for t in last_week_txns if t.get("type") == "income")
    last_expense = sum(t.get("amount", 0) for t in last_week_txns if t.get("type") == "expense")
    
    # Category breakdown for this week
    categories = {}
    for t in this_week_txns:
        if t.get("type") == "expense":
            cat = t.get("category", "other")
            categories[cat] = categories.get(cat, 0) + t.get("amount", 0)
    
    # Calculate changes
    income_change = round(((this_income - last_income) / last_income * 100)) if last_income > 0 else 0
    expense_change = round(((this_expense - last_expense) / last_expense * 100)) if last_expense > 0 else 0
    
    return {
        "phone": phone,
        "period": "weekly",
        "this_week": {
            "income": this_income,
            "expense": this_expense,
            "savings": this_income - this_expense,
            "start": start_of_week.strftime("%Y-%m-%d"),
            "end": end_of_week.strftime("%Y-%m-%d")
        },
        "last_week": {
            "income": last_income,
            "expense": last_expense,
            "savings": last_income - last_expense
        },
        "changes": {
            "income_percent": income_change,
            "expense_percent": expense_change,
            "income_trend": "up" if income_change >= 0 else "down",
            "expense_trend": "up" if expense_change >= 0 else "down"
        },
        "categories": categories
    }


@extended_router.get("/reports/{phone}/monthly-comparison")
def get_monthly_comparison(phone: str):
    """Get monthly report with comparison to last month"""
    today = datetime.now()
    
    # This month
    start_of_month = today.replace(day=1)
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    # Last month
    if today.month == 1:
        start_last_month = today.replace(year=today.year - 1, month=12, day=1)
    else:
        start_last_month = today.replace(month=today.month - 1, day=1)
    end_last_month = start_of_month - timedelta(days=1)
    
    # Get transactions
    this_month_txns = transaction_repo.get_transactions_in_range(
        phone, start_of_month.strftime("%Y-%m-%d"), end_of_month.strftime("%Y-%m-%d")
    )
    last_month_txns = transaction_repo.get_transactions_in_range(
        phone, start_last_month.strftime("%Y-%m-%d"), end_last_month.strftime("%Y-%m-%d")
    )
    
    # Calculate this month
    this_income = sum(t.get("amount", 0) for t in this_month_txns if t.get("type") == "income")
    this_expense = sum(t.get("amount", 0) for t in this_month_txns if t.get("type") == "expense")
    
    # Calculate last month
    last_income = sum(t.get("amount", 0) for t in last_month_txns if t.get("type") == "income")
    last_expense = sum(t.get("amount", 0) for t in last_month_txns if t.get("type") == "expense")
    
    # Category breakdown
    categories = {}
    for t in this_month_txns:
        if t.get("type") == "expense":
            cat = t.get("category", "other")
            categories[cat] = categories.get(cat, 0) + t.get("amount", 0)
    
    # User data for goals
    user = user_repo.get_user(phone)
    savings_target = user.get("savings_target", 0) if user else 0
    goals = user.get("financial_goals", []) if user else []
    
    # Calculate changes
    income_change = round(((this_income - last_income) / last_income * 100)) if last_income > 0 else 0
    expense_change = round(((this_expense - last_expense) / last_expense * 100)) if last_expense > 0 else 0
    
    # Goals progress (simplified)
    goals_progress = {}
    actual_savings = this_income - this_expense
    if savings_target > 0:
        goals_progress["Savings Target"] = min(100, round((actual_savings / savings_target) * 100))
    
    return {
        "phone": phone,
        "period": "monthly",
        "this_month": {
            "income": this_income,
            "expense": this_expense,
            "savings": this_income - this_expense,
            "savings_target": savings_target,
            "month": today.strftime("%B %Y")
        },
        "last_month": {
            "income": last_income,
            "expense": last_expense,
            "savings": last_income - last_expense
        },
        "changes": {
            "income_percent": income_change,
            "expense_percent": expense_change
        },
        "categories": categories,
        "goals_progress": goals_progress
    }
