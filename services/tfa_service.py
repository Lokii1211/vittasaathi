"""
Two-Factor Authentication Service
=================================
TOTP-based 2FA for sensitive operations
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
from pathlib import Path
import json
import secrets
import hashlib
import base64
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import DATA_DIR
from database.user_repository import user_repo

# Try to import TOTP library
try:
    import pyotp
    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False

# Try to import QR code library
try:
    import qrcode
    from io import BytesIO
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

# 2FA data directory
TFA_DIR = DATA_DIR / "2fa"
TFA_DIR.mkdir(exist_ok=True)


class TwoFactorAuthService:
    """Two-Factor Authentication using TOTP"""
    
    def __init__(self):
        self.secrets_file = TFA_DIR / "secrets.json"
        self.sessions_file = TFA_DIR / "sessions.json"
        self._load_data()
    
    def _load_data(self):
        """Load 2FA data"""
        if self.secrets_file.exists():
            with open(self.secrets_file, 'r') as f:
                self.secrets = json.load(f)
        else:
            self.secrets = {}
            self._save_secrets()
        
        if self.sessions_file.exists():
            with open(self.sessions_file, 'r') as f:
                self.sessions = json.load(f)
        else:
            self.sessions = {}
            self._save_sessions()
    
    def _save_secrets(self):
        """Save 2FA secrets"""
        with open(self.secrets_file, 'w') as f:
            json.dump(self.secrets, f)
    
    def _save_sessions(self):
        """Save 2FA sessions"""
        with open(self.sessions_file, 'w') as f:
            json.dump(self.sessions, f)
    
    def is_available(self) -> bool:
        """Check if 2FA is available"""
        return PYOTP_AVAILABLE
    
    def is_enabled(self, user_id: str) -> bool:
        """Check if user has 2FA enabled"""
        return user_id in self.secrets and self.secrets[user_id].get("enabled", False)
    
    def generate_secret(self, user_id: str) -> Dict:
        """Generate TOTP secret for user"""
        if not PYOTP_AVAILABLE:
            return {"success": False, "error": "pyotp not installed. Run: pip install pyotp"}
        
        # Generate new secret
        secret = pyotp.random_base32()
        
        # Store secret (not enabled yet)
        self.secrets[user_id] = {
            "secret": secret,
            "enabled": False,
            "created_at": datetime.now().isoformat(),
            "backup_codes": self._generate_backup_codes()
        }
        self._save_secrets()
        
        # Generate provisioning URI
        user = user_repo.get_user(user_id)
        user_name = user.get("name", user_id) if user else user_id
        
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_name,
            issuer_name="VittaSaathi"
        )
        
        result = {
            "success": True,
            "secret": secret,
            "provisioning_uri": provisioning_uri,
            "backup_codes": self.secrets[user_id]["backup_codes"],
            "message": "Scan QR code or enter secret in authenticator app"
        }
        
        # Generate QR code if available
        if QRCODE_AVAILABLE:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            
            qr_path = TFA_DIR / f"qr_{user_id}.png"
            img.save(qr_path)
            
            result["qr_code_path"] = str(qr_path)
            result["qr_code_base64"] = base64.b64encode(buffer.getvalue()).decode()
        
        return result
    
    def _generate_backup_codes(self, count: int = 8) -> list:
        """Generate backup codes"""
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()
            code = f"{code[:4]}-{code[4:]}"
            codes.append(code)
        return codes
    
    def verify_and_enable(self, user_id: str, code: str) -> Dict:
        """Verify code and enable 2FA"""
        if not PYOTP_AVAILABLE:
            return {"success": False, "error": "pyotp not installed"}
        
        if user_id not in self.secrets:
            return {"success": False, "error": "No 2FA setup found. Generate secret first."}
        
        secret = self.secrets[user_id]["secret"]
        totp = pyotp.TOTP(secret)
        
        if totp.verify(code, valid_window=1):
            self.secrets[user_id]["enabled"] = True
            self.secrets[user_id]["enabled_at"] = datetime.now().isoformat()
            self._save_secrets()
            
            return {
                "success": True,
                "message": "2FA enabled successfully",
                "backup_codes": self.secrets[user_id]["backup_codes"]
            }
        else:
            return {"success": False, "error": "Invalid code"}
    
    def verify_code(self, user_id: str, code: str) -> Dict:
        """Verify 2FA code"""
        if not self.is_enabled(user_id):
            return {"success": True, "message": "2FA not enabled"}
        
        if not PYOTP_AVAILABLE:
            return {"success": False, "error": "pyotp not installed"}
        
        # Check if it's a backup code
        if code in self.secrets[user_id].get("backup_codes", []):
            self.secrets[user_id]["backup_codes"].remove(code)
            self.secrets[user_id]["last_backup_code_used"] = datetime.now().isoformat()
            self._save_secrets()
            return {"success": True, "message": "Verified with backup code", "backup_code_used": True}
        
        # Verify TOTP
        secret = self.secrets[user_id]["secret"]
        totp = pyotp.TOTP(secret)
        
        if totp.verify(code, valid_window=1):
            return {"success": True, "message": "Code verified"}
        else:
            return {"success": False, "error": "Invalid code"}
    
    def create_session(self, user_id: str, duration_minutes: int = 30) -> Dict:
        """Create authenticated session after 2FA verification"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(minutes=duration_minutes)
        
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
            "verified": True
        }
        self._save_sessions()
        
        return {
            "session_id": session_id,
            "expires_at": expires_at.isoformat(),
            "duration_minutes": duration_minutes
        }
    
    def verify_session(self, session_id: str) -> Dict:
        """Verify if session is valid"""
        if session_id not in self.sessions:
            return {"valid": False, "error": "Session not found"}
        
        session = self.sessions[session_id]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        if datetime.now() > expires_at:
            del self.sessions[session_id]
            self._save_sessions()
            return {"valid": False, "error": "Session expired"}
        
        return {
            "valid": True,
            "user_id": session["user_id"],
            "expires_at": session["expires_at"]
        }
    
    def invalidate_session(self, session_id: str) -> Dict:
        """Invalidate a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()
            return {"success": True}
        return {"success": False, "error": "Session not found"}
    
    def disable_2fa(self, user_id: str, code: str) -> Dict:
        """Disable 2FA (requires valid code)"""
        verify_result = self.verify_code(user_id, code)
        
        if not verify_result.get("success"):
            return verify_result
        
        if user_id in self.secrets:
            del self.secrets[user_id]
            self._save_secrets()
            
            # Delete QR code if exists
            qr_path = TFA_DIR / f"qr_{user_id}.png"
            if qr_path.exists():
                qr_path.unlink()
        
        return {"success": True, "message": "2FA disabled"}
    
    def regenerate_backup_codes(self, user_id: str, code: str) -> Dict:
        """Regenerate backup codes (requires valid code)"""
        verify_result = self.verify_code(user_id, code)
        
        if not verify_result.get("success"):
            return verify_result
        
        if user_id not in self.secrets:
            return {"success": False, "error": "2FA not enabled"}
        
        new_codes = self._generate_backup_codes()
        self.secrets[user_id]["backup_codes"] = new_codes
        self.secrets[user_id]["backup_codes_regenerated"] = datetime.now().isoformat()
        self._save_secrets()
        
        return {
            "success": True,
            "backup_codes": new_codes,
            "message": "Save these codes securely"
        }
    
    def get_status(self, user_id: str) -> Dict:
        """Get 2FA status for user"""
        if user_id not in self.secrets:
            return {
                "enabled": False,
                "setup_pending": False
            }
        
        secret_data = self.secrets[user_id]
        
        return {
            "enabled": secret_data.get("enabled", False),
            "setup_pending": not secret_data.get("enabled", False),
            "enabled_at": secret_data.get("enabled_at"),
            "backup_codes_remaining": len(secret_data.get("backup_codes", []))
        }
    
    def generate_otp_for_action(self, user_id: str, action: str, validity_minutes: int = 5) -> Dict:
        """Generate one-time code for specific action (like password reset)"""
        otp = secrets.randbelow(1000000)
        otp_str = f"{otp:06d}"
        
        # Store OTP
        otp_key = f"{user_id}_{action}"
        if "action_otps" not in self.sessions:
            self.sessions["action_otps"] = {}
        
        self.sessions["action_otps"][otp_key] = {
            "code": otp_str,
            "action": action,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=validity_minutes)).isoformat(),
            "used": False
        }
        self._save_sessions()
        
        return {
            "code": otp_str,
            "action": action,
            "validity_minutes": validity_minutes,
            "expires_at": self.sessions["action_otps"][otp_key]["expires_at"]
        }
    
    def verify_action_otp(self, user_id: str, action: str, code: str) -> Dict:
        """Verify OTP for specific action"""
        otp_key = f"{user_id}_{action}"
        
        if "action_otps" not in self.sessions:
            return {"valid": False, "error": "No OTP found"}
        
        if otp_key not in self.sessions["action_otps"]:
            return {"valid": False, "error": "No OTP found for this action"}
        
        otp_data = self.sessions["action_otps"][otp_key]
        
        # Check expiry
        expires_at = datetime.fromisoformat(otp_data["expires_at"])
        if datetime.now() > expires_at:
            del self.sessions["action_otps"][otp_key]
            self._save_sessions()
            return {"valid": False, "error": "OTP expired"}
        
        # Check if already used
        if otp_data.get("used"):
            return {"valid": False, "error": "OTP already used"}
        
        # Verify code
        if otp_data["code"] == code:
            otp_data["used"] = True
            otp_data["used_at"] = datetime.now().isoformat()
            self._save_sessions()
            return {"valid": True, "action": action}
        
        return {"valid": False, "error": "Invalid OTP"}
    
    def cleanup_expired_sessions(self) -> Dict:
        """Remove expired sessions"""
        now = datetime.now()
        expired = []
        
        for session_id, session in list(self.sessions.items()):
            if session_id == "action_otps":
                continue
            try:
                expires_at = datetime.fromisoformat(session["expires_at"])
                if now > expires_at:
                    expired.append(session_id)
                    del self.sessions[session_id]
            except:
                pass
        
        # Clean expired action OTPs
        if "action_otps" in self.sessions:
            for otp_key, otp_data in list(self.sessions["action_otps"].items()):
                try:
                    expires_at = datetime.fromisoformat(otp_data["expires_at"])
                    if now > expires_at:
                        del self.sessions["action_otps"][otp_key]
                except:
                    pass
        
        self._save_sessions()
        
        return {"cleaned": len(expired)}


# Global instance
tfa_service = TwoFactorAuthService()
