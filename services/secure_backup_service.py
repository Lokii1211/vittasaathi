"""
Secure Backup Service with Encryption
======================================
AES-256 encryption for backup files and scheduled backups
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json
import zipfile
import base64
import hashlib
import secrets
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import DATA_DIR

# Try to import cryptography for AES encryption
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# Backup directories
BACKUPS_DIR = DATA_DIR / "backups"
SECURE_BACKUPS_DIR = DATA_DIR / "secure_backups"
KEYS_DIR = DATA_DIR / ".keys"

BACKUPS_DIR.mkdir(exist_ok=True)
SECURE_BACKUPS_DIR.mkdir(exist_ok=True)
KEYS_DIR.mkdir(exist_ok=True)


class EncryptionService:
    """Handle encryption and decryption of backup data"""
    
    def __init__(self):
        self.keys_dir = KEYS_DIR
    
    def is_available(self) -> bool:
        """Check if encryption is available"""
        return CRYPTO_AVAILABLE
    
    def generate_key(self, password: str = None) -> bytes:
        """Generate encryption key from password or random"""
        
        if not CRYPTO_AVAILABLE:
            return None
        
        if password:
            # Derive key from password using PBKDF2
            salt = secrets.token_bytes(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Store salt for later key derivation
            return key, salt
        else:
            # Generate random key
            return Fernet.generate_key(), None
    
    def derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Derive key from password using stored salt"""
        
        if not CRYPTO_AVAILABLE:
            return None
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def encrypt_data(self, data: bytes, key: bytes) -> bytes:
        """Encrypt data using Fernet (AES-128-CBC)"""
        
        if not CRYPTO_AVAILABLE:
            return None
        
        fernet = Fernet(key)
        return fernet.encrypt(data)
    
    def decrypt_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt data using Fernet"""
        
        if not CRYPTO_AVAILABLE:
            return None
        
        try:
            fernet = Fernet(key)
            return fernet.decrypt(encrypted_data)
        except Exception as e:
            return None
    
    def encrypt_file(self, input_path: Path, output_path: Path, key: bytes) -> bool:
        """Encrypt a file"""
        
        if not CRYPTO_AVAILABLE:
            return False
        
        try:
            with open(input_path, 'rb') as f:
                data = f.read()
            
            encrypted = self.encrypt_data(data, key)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted)
            
            return True
        except Exception as e:
            return False
    
    def decrypt_file(self, input_path: Path, output_path: Path, key: bytes) -> bool:
        """Decrypt a file"""
        
        if not CRYPTO_AVAILABLE:
            return False
        
        try:
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted = self.decrypt_data(encrypted_data, key)
            
            if decrypted is None:
                return False
            
            with open(output_path, 'wb') as f:
                f.write(decrypted)
            
            return True
        except Exception as e:
            return False
    
    def save_key_file(self, key_id: str, key: bytes, salt: bytes = None) -> Path:
        """Save encryption key to file (should be stored securely)"""
        
        key_data = {
            "key_id": key_id,
            "key": base64.b64encode(key).decode(),
            "salt": base64.b64encode(salt).decode() if salt else None,
            "created_at": datetime.now().isoformat(),
            "algorithm": "Fernet (AES-128-CBC)"
        }
        
        key_file = self.keys_dir / f"{key_id}.key"
        
        with open(key_file, 'w') as f:
            json.dump(key_data, f, indent=2)
        
        return key_file
    
    def load_key_file(self, key_id: str) -> Optional[Dict]:
        """Load encryption key from file"""
        
        key_file = self.keys_dir / f"{key_id}.key"
        
        if not key_file.exists():
            return None
        
        with open(key_file, 'r') as f:
            key_data = json.load(f)
        
        key_data['key'] = base64.b64decode(key_data['key'])
        if key_data.get('salt'):
            key_data['salt'] = base64.b64decode(key_data['salt'])
        
        return key_data
    
    def hash_data(self, data: bytes) -> str:
        """Create SHA-256 hash of data for integrity verification"""
        return hashlib.sha256(data).hexdigest()


class SecureBackupService:
    """Encrypted backup service"""
    
    def __init__(self):
        self.encryption = EncryptionService()
        self.secure_dir = SECURE_BACKUPS_DIR
    
    def create_encrypted_backup(
        self, 
        backup_name: str = None,
        password: str = None
    ) -> Dict:
        """Create encrypted full backup"""
        
        if not self.encryption.is_available():
            return {"success": False, "error": "Encryption not available. Install cryptography: pip install cryptography"}
        
        from services.backup_service import backup_service
        
        # First create regular backup
        regular_backup = backup_service.create_full_backup(backup_name)
        
        if not regular_backup.get("success"):
            return regular_backup
        
        backup_path = Path(regular_backup["backup_path"])
        
        # Generate or derive key
        if password:
            key, salt = self.encryption.generate_key(password)
        else:
            key, salt = self.encryption.generate_key()
        
        # Create key ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        key_id = f"backup_key_{timestamp}"
        
        # Encrypt the backup file
        encrypted_path = self.secure_dir / f"{backup_path.stem}.encrypted"
        
        if not self.encryption.encrypt_file(backup_path, encrypted_path, key):
            return {"success": False, "error": "Encryption failed"}
        
        # Save key file (if no password)
        if not password:
            key_file = self.encryption.save_key_file(key_id, key, salt)
        else:
            # Save salt for password-based key derivation
            salt_data = {
                "key_id": key_id,
                "salt": base64.b64encode(salt).decode(),
                "password_protected": True,
                "created_at": datetime.now().isoformat()
            }
            key_file = self.encryption.keys_dir / f"{key_id}.salt"
            with open(key_file, 'w') as f:
                json.dump(salt_data, f, indent=2)
        
        # Calculate hash for integrity
        with open(encrypted_path, 'rb') as f:
            file_hash = self.encryption.hash_data(f.read())
        
        # Create metadata
        metadata = {
            "original_backup": regular_backup["backup_name"],
            "encrypted_at": datetime.now().isoformat(),
            "key_id": key_id,
            "password_protected": password is not None,
            "hash": file_hash,
            "size_bytes": encrypted_path.stat().st_size
        }
        
        metadata_path = encrypted_path.with_suffix(".meta")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Optionally delete unencrypted backup
        backup_path.unlink()
        
        return {
            "success": True,
            "encrypted_backup_path": str(encrypted_path),
            "key_id": key_id,
            "password_protected": password is not None,
            "hash": file_hash,
            "size_bytes": metadata["size_bytes"]
        }
    
    def restore_encrypted_backup(
        self,
        encrypted_path: str,
        password: str = None,
        key_id: str = None
    ) -> Dict:
        """Restore from encrypted backup"""
        
        if not self.encryption.is_available():
            return {"success": False, "error": "Encryption not available"}
        
        encrypted_file = Path(encrypted_path)
        
        if not encrypted_file.exists():
            return {"success": False, "error": "Encrypted backup not found"}
        
        # Load metadata
        metadata_path = encrypted_file.with_suffix(".meta")
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            key_id = key_id or metadata.get("key_id")
        
        # Get decryption key
        if password:
            # Load salt and derive key
            salt_file = self.encryption.keys_dir / f"{key_id}.salt"
            if not salt_file.exists():
                return {"success": False, "error": "Salt file not found"}
            
            with open(salt_file, 'r') as f:
                salt_data = json.load(f)
            
            salt = base64.b64decode(salt_data["salt"])
            key = self.encryption.derive_key_from_password(password, salt)
        else:
            # Load key from file
            key_data = self.encryption.load_key_file(key_id)
            if not key_data:
                return {"success": False, "error": "Key file not found"}
            key = key_data["key"]
        
        # Verify hash before decryption
        with open(encrypted_file, 'rb') as f:
            current_hash = self.encryption.hash_data(f.read())
        
        if metadata and current_hash != metadata.get("hash"):
            return {"success": False, "error": "File integrity check failed - backup may be corrupted"}
        
        # Decrypt to temporary file
        temp_path = BACKUPS_DIR / f"temp_restored_{datetime.now().strftime('%H%M%S')}.zip"
        
        if not self.encryption.decrypt_file(encrypted_file, temp_path, key):
            return {"success": False, "error": "Decryption failed - wrong password or corrupted data"}
        
        # Restore from decrypted backup
        from services.backup_service import backup_service
        result = backup_service.restore_full_backup(str(temp_path))
        
        # Clean up temp file
        temp_path.unlink()
        
        return result
    
    def list_encrypted_backups(self) -> List[Dict]:
        """List all encrypted backups"""
        
        backups = []
        
        for encrypted_file in self.secure_dir.glob("*.encrypted"):
            metadata_path = encrypted_file.with_suffix(".meta")
            
            backup_info = {
                "filename": encrypted_file.name,
                "path": str(encrypted_file),
                "size_bytes": encrypted_file.stat().st_size,
                "created_at": datetime.fromtimestamp(encrypted_file.stat().st_mtime).isoformat()
            }
            
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                backup_info.update({
                    "key_id": metadata.get("key_id"),
                    "password_protected": metadata.get("password_protected", False),
                    "original_backup": metadata.get("original_backup")
                })
            
            backups.append(backup_info)
        
        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return backups
    
    def delete_encrypted_backup(self, encrypted_path: str, delete_key: bool = False) -> Dict:
        """Delete encrypted backup and optionally its key"""
        
        encrypted_file = Path(encrypted_path)
        
        if not encrypted_file.exists():
            return {"success": False, "error": "Backup not found"}
        
        # Get key_id from metadata
        metadata_path = encrypted_file.with_suffix(".meta")
        key_id = None
        
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            key_id = metadata.get("key_id")
            metadata_path.unlink()
        
        # Delete encrypted file
        encrypted_file.unlink()
        
        # Optionally delete key
        if delete_key and key_id:
            key_file = self.encryption.keys_dir / f"{key_id}.key"
            salt_file = self.encryption.keys_dir / f"{key_id}.salt"
            
            if key_file.exists():
                key_file.unlink()
            if salt_file.exists():
                salt_file.unlink()
        
        return {"success": True, "deleted": str(encrypted_file)}


class ScheduledBackupService:
    """Manage scheduled automatic backups"""
    
    def __init__(self):
        self.config_file = DATA_DIR / "backup_schedule.json"
        self.secure_backup = SecureBackupService()
        self._load_config()
    
    def _load_config(self):
        """Load backup schedule configuration"""
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "enabled": False,
                "frequency": "daily",  # daily, weekly, monthly
                "time": "02:00",  # 2 AM
                "retention_days": 30,
                "max_backups": 10,
                "encrypt": False,
                "password": None,  # If set, use password-based encryption
                "last_backup": None,
                "next_backup": None,
                "backup_history": []
            }
            self._save_config()
    
    def _save_config(self):
        """Save backup schedule configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def configure_schedule(
        self,
        enabled: bool = True,
        frequency: str = "daily",
        time: str = "02:00",
        retention_days: int = 30,
        max_backups: int = 10,
        encrypt: bool = False,
        password: str = None
    ) -> Dict:
        """Configure backup schedule"""
        
        self.config.update({
            "enabled": enabled,
            "frequency": frequency,
            "time": time,
            "retention_days": retention_days,
            "max_backups": max_backups,
            "encrypt": encrypt,
            "password": password
        })
        
        # Calculate next backup time
        self.config["next_backup"] = self._calculate_next_backup()
        
        self._save_config()
        
        return {
            "success": True,
            "config": {k: v for k, v in self.config.items() if k != "password"}
        }
    
    def _calculate_next_backup(self) -> str:
        """Calculate next scheduled backup time"""
        
        now = datetime.now()
        time_parts = self.config["time"].split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1]) if len(time_parts) > 1 else 0
        
        next_backup = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if next_backup <= now:
            if self.config["frequency"] == "daily":
                next_backup += timedelta(days=1)
            elif self.config["frequency"] == "weekly":
                next_backup += timedelta(weeks=1)
            elif self.config["frequency"] == "monthly":
                next_backup += timedelta(days=30)
        
        return next_backup.isoformat()
    
    def run_scheduled_backup(self) -> Dict:
        """Run a scheduled backup"""
        
        if not self.config.get("enabled"):
            return {"success": False, "error": "Scheduled backups not enabled"}
        
        backup_name = f"scheduled_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if self.config.get("encrypt"):
            # Create encrypted backup
            result = self.secure_backup.create_encrypted_backup(
                backup_name=backup_name,
                password=self.config.get("password")
            )
        else:
            # Create regular backup
            from services.backup_service import backup_service
            result = backup_service.create_full_backup(backup_name)
        
        if result.get("success"):
            # Update history
            self.config["last_backup"] = datetime.now().isoformat()
            self.config["next_backup"] = self._calculate_next_backup()
            
            self.config["backup_history"].append({
                "timestamp": self.config["last_backup"],
                "backup_name": backup_name,
                "encrypted": self.config.get("encrypt", False),
                "size_bytes": result.get("size_bytes", 0)
            })
            
            # Keep only last N entries in history
            self.config["backup_history"] = self.config["backup_history"][-20:]
            
            self._save_config()
            
            # Cleanup old backups
            self._cleanup_old_backups()
        
        return result
    
    def _cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        
        from services.backup_service import backup_service
        
        # Get all backups
        all_backups = backup_service.list_backups()
        encrypted_backups = self.secure_backup.list_encrypted_backups()
        
        # Filter scheduled backups
        scheduled = [b for b in all_backups if "scheduled_backup" in b.get("filename", "")]
        scheduled_encrypted = [b for b in encrypted_backups if "scheduled_backup" in b.get("filename", "")]
        
        # Remove excess backups
        max_backups = self.config.get("max_backups", 10)
        
        if len(scheduled) > max_backups:
            for backup in scheduled[max_backups:]:
                backup_service.delete_backup(backup["path"])
        
        if len(scheduled_encrypted) > max_backups:
            for backup in scheduled_encrypted[max_backups:]:
                self.secure_backup.delete_encrypted_backup(backup["path"])
        
        # Remove backups older than retention period
        retention_days = self.config.get("retention_days", 30)
        cutoff = datetime.now() - timedelta(days=retention_days)
        
        for backup in scheduled:
            try:
                backup_date = datetime.fromisoformat(backup.get("created_at", ""))
                if backup_date < cutoff:
                    backup_service.delete_backup(backup["path"])
            except:
                pass
    
    def check_and_run(self) -> Dict:
        """Check if backup is due and run if needed"""
        
        if not self.config.get("enabled"):
            return {"due": False, "message": "Scheduled backups not enabled"}
        
        next_backup = self.config.get("next_backup")
        
        if not next_backup:
            return {"due": False, "message": "No backup scheduled"}
        
        try:
            next_backup_time = datetime.fromisoformat(next_backup)
        except:
            return {"due": False, "message": "Invalid schedule time"}
        
        if datetime.now() >= next_backup_time:
            result = self.run_scheduled_backup()
            return {"due": True, "ran": True, "result": result}
        
        return {
            "due": False,
            "next_backup": next_backup,
            "time_until": str(next_backup_time - datetime.now())
        }
    
    def get_status(self) -> Dict:
        """Get current backup schedule status"""
        
        return {
            "enabled": self.config.get("enabled", False),
            "frequency": self.config.get("frequency", "daily"),
            "time": self.config.get("time", "02:00"),
            "last_backup": self.config.get("last_backup"),
            "next_backup": self.config.get("next_backup"),
            "retention_days": self.config.get("retention_days", 30),
            "max_backups": self.config.get("max_backups", 10),
            "encrypt": self.config.get("encrypt", False),
            "password_set": self.config.get("password") is not None,
            "backup_count": len(self.config.get("backup_history", [])),
            "recent_backups": self.config.get("backup_history", [])[-5:]
        }
    
    def disable_schedule(self) -> Dict:
        """Disable scheduled backups"""
        
        self.config["enabled"] = False
        self._save_config()
        
        return {"success": True, "message": "Scheduled backups disabled"}


# Global instances
encryption_service = EncryptionService()
secure_backup_service = SecureBackupService()
scheduled_backup_service = ScheduledBackupService()

