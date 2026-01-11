"""
Notification Service
====================
WhatsApp and Email notifications for backups and important events
"""
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import DATA_DIR
from database.user_repository import user_repo

# Try to import Twilio for WhatsApp
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

# Notification templates directory
TEMPLATES_DIR = DATA_DIR / "notification_templates"
TEMPLATES_DIR.mkdir(exist_ok=True)


class NotificationService:
    """Send notifications via WhatsApp and Email"""
    
    def __init__(self):
        self.config_file = DATA_DIR / "notification_config.json"
        self._load_config()
        self._load_templates()
    
    def _load_config(self):
        """Load notification configuration"""
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "whatsapp": {
                    "enabled": False,
                    "account_sid": "",
                    "auth_token": "",
                    "from_number": ""
                },
                "email": {
                    "enabled": False,
                    "smtp_host": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "from_email": "",
                    "use_tls": True
                },
                "admin_phones": [],
                "admin_emails": [],
                "notification_preferences": {
                    "backup_success": True,
                    "backup_failure": True,
                    "low_balance_alert": True,
                    "goal_achieved": True,
                    "bill_reminder": True,
                    "security_alert": True
                }
            }
            self._save_config()
    
    def _save_config(self):
        """Save notification configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _load_templates(self):
        """Load notification templates"""
        
        self.templates = {
            "backup_success": {
                "whatsapp": "MoneyViya Backup Complete\n\nBackup: {backup_name}\nDate: {date}\nSize: {size}\nEncrypted: {encrypted}\n\nYour data is safe!",
                "email_subject": "MoneyViya Backup Complete",
                "email_body": "<html><body><h2>Backup Complete</h2><p>Backup: {backup_name}</p><p>Size: {size}</p><p>Encrypted: {encrypted}</p></body></html>"
            },
            "backup_failure": {
                "whatsapp": "MoneyViya Backup Failed\n\nError: {error}\nDate: {date}\n\nPlease check your backup settings.",
                "email_subject": "MoneyViya Backup Failed",
                "email_body": "<html><body><h2>Backup Failed</h2><p>Error: {error}</p><p>Date: {date}</p></body></html>"
            },
            "security_alert": {
                "whatsapp": "MoneyViya Security Alert\n\n{alert_type}\nLocation: {location}\nTime: {time}\n\nIf this wasnt you, change your password!",
                "email_subject": "MoneyViya Security Alert",
                "email_body": "<html><body><h2>Security Alert</h2><p>{alert_type}</p><p>Location: {location}</p><p>Time: {time}</p></body></html>"
            },
            "goal_achieved": {
                "whatsapp": "Congratulations!\n\nYou achieved your goal!\nGoal: {goal_name}\nAmount: Rs{amount}\nCompleted: {date}",
                "email_subject": "Goal Achieved - {goal_name}",
                "email_body": "<html><body><h2>Goal Achieved!</h2><p>Goal: {goal_name}</p><p>Amount: Rs{amount}</p></body></html>"
            },
            "bill_reminder": {
                "whatsapp": "Bill Reminder\n\n{bill_type}\nAmount: Rs{amount}\nDue: {due_date}\n\nDont forget to pay!",
                "email_subject": "Bill Reminder - {bill_type}",
                "email_body": "<html><body><h2>Bill Reminder</h2><p>{bill_type}: Rs{amount}</p><p>Due: {due_date}</p></body></html>"
            },
            "2fa_code": {
                "whatsapp": "MoneyViya Verification\n\nYour code is: {code}\n\nValid for {validity} minutes.",
                "email_subject": "MoneyViya Verification Code",
                "email_body": "<html><body><h2>Verification Code</h2><p style='font-size:32px'>{code}</p><p>Valid for {validity} minutes</p></body></html>"
            }
        }
    
    def configure_whatsapp(self, account_sid: str, auth_token: str, from_number: str) -> Dict:
        """Configure WhatsApp notifications"""
        self.config["whatsapp"] = {
            "enabled": True,
            "account_sid": account_sid,
            "auth_token": auth_token,
            "from_number": from_number
        }
        self._save_config()
        return {"success": True, "message": "WhatsApp configured"}
    
    def configure_email(self, smtp_host: str, smtp_port: int, username: str, password: str, from_email: str, use_tls: bool = True) -> Dict:
        """Configure Email notifications"""
        self.config["email"] = {
            "enabled": True,
            "smtp_host": smtp_host,
            "smtp_port": smtp_port,
            "username": username,
            "password": password,
            "from_email": from_email,
            "use_tls": use_tls
        }
        self._save_config()
        return {"success": True, "message": "Email configured"}
    
    def add_admin_contact(self, phone: str = None, email: str = None) -> Dict:
        """Add admin contact for notifications"""
        if phone and phone not in self.config["admin_phones"]:
            self.config["admin_phones"].append(phone)
        if email and email not in self.config["admin_emails"]:
            self.config["admin_emails"].append(email)
        self._save_config()
        return {"success": True, "phones": self.config["admin_phones"], "emails": self.config["admin_emails"]}
    
    def send_whatsapp(self, to_number: str, message: str) -> Dict:
        """Send WhatsApp message"""
        if not TWILIO_AVAILABLE:
            return {"success": False, "error": "Twilio not installed"}
        if not self.config["whatsapp"]["enabled"]:
            return {"success": False, "error": "WhatsApp not configured"}
        try:
            client = TwilioClient(self.config["whatsapp"]["account_sid"], self.config["whatsapp"]["auth_token"])
            msg = client.messages.create(
                body=message,
                from_=f"whatsapp:{self.config['whatsapp']['from_number']}",
                to=f"whatsapp:{to_number}"
            )
            return {"success": True, "message_sid": msg.sid}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_email(self, to_email: str, subject: str, html_body: str) -> Dict:
        """Send email notification"""
        if not self.config["email"]["enabled"]:
            return {"success": False, "error": "Email not configured"}
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config["email"]["from_email"]
            msg['To'] = to_email
            msg.attach(MIMEText(html_body, 'html'))
            with smtplib.SMTP(self.config["email"]["smtp_host"], self.config["email"]["smtp_port"]) as server:
                if self.config["email"]["use_tls"]:
                    server.starttls()
                server.login(self.config["email"]["username"], self.config["email"]["password"])
                server.sendmail(self.config["email"]["from_email"], to_email, msg.as_string())
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def notify_backup_success(self, backup_name: str, size: str, encrypted: bool) -> Dict:
        """Send backup success notification"""
        if not self.config["notification_preferences"]["backup_success"]:
            return {"skipped": True}
        data = {"backup_name": backup_name, "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "size": size, "encrypted": "Yes" if encrypted else "No"}
        results = {"whatsapp": [], "email": []}
        template = self.templates["backup_success"]
        for phone in self.config["admin_phones"]:
            results["whatsapp"].append(self.send_whatsapp(phone, template["whatsapp"].format(**data)))
        for email in self.config["admin_emails"]:
            results["email"].append(self.send_email(email, template["email_subject"], template["email_body"].format(**data)))
        return results
    
    def notify_backup_failure(self, error: str) -> Dict:
        """Send backup failure notification"""
        if not self.config["notification_preferences"]["backup_failure"]:
            return {"skipped": True}
        data = {"error": error, "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
        results = {"whatsapp": [], "email": []}
        template = self.templates["backup_failure"]
        for phone in self.config["admin_phones"]:
            results["whatsapp"].append(self.send_whatsapp(phone, template["whatsapp"].format(**data)))
        for email in self.config["admin_emails"]:
            results["email"].append(self.send_email(email, template["email_subject"], template["email_body"].format(**data)))
        return results
    
    def notify_security_alert(self, user_id: str, alert_type: str, location: str = "Unknown") -> Dict:
        """Send security alert notification"""
        if not self.config["notification_preferences"]["security_alert"]:
            return {"skipped": True}
        user = user_repo.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        data = {"alert_type": alert_type, "location": location, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        template = self.templates["security_alert"]
        phone = user.get("phone", user_id)
        return self.send_whatsapp(phone, template["whatsapp"].format(**data))
    
    def notify_goal_achieved(self, user_id: str, goal_name: str, amount: int) -> Dict:
        """Send goal achievement notification"""
        if not self.config["notification_preferences"]["goal_achieved"]:
            return {"skipped": True}
        data = {"goal_name": goal_name, "amount": f"{amount:,}", "date": datetime.now().strftime("%Y-%m-%d")}
        template = self.templates["goal_achieved"]
        user = user_repo.get_user(user_id)
        phone = user.get("phone", user_id) if user else user_id
        return self.send_whatsapp(phone, template["whatsapp"].format(**data))
    
    def notify_bill_reminder(self, user_id: str, bill_type: str, amount: int, due_date: str) -> Dict:
        """Send bill reminder notification"""
        if not self.config["notification_preferences"]["bill_reminder"]:
            return {"skipped": True}
        data = {"bill_type": bill_type, "amount": f"{amount:,}", "due_date": due_date}
        template = self.templates["bill_reminder"]
        user = user_repo.get_user(user_id)
        phone = user.get("phone", user_id) if user else user_id
        return self.send_whatsapp(phone, template["whatsapp"].format(**data))
    
    def send_2fa_code(self, user_id: str, code: str, validity: int = 5) -> Dict:
        """Send 2FA verification code"""
        data = {"code": code, "validity": validity}
        template = self.templates["2fa_code"]
        user = user_repo.get_user(user_id)
        phone = user.get("phone", user_id) if user else user_id
        return self.send_whatsapp(phone, template["whatsapp"].format(**data))
    
    def get_config_status(self) -> Dict:
        """Get notification configuration status"""
        return {
            "whatsapp_enabled": self.config["whatsapp"]["enabled"],
            "email_enabled": self.config["email"]["enabled"],
            "admin_phones_count": len(self.config["admin_phones"]),
            "admin_emails_count": len(self.config["admin_emails"]),
            "preferences": self.config["notification_preferences"]
        }


# Global instance
notification_service = NotificationService()

