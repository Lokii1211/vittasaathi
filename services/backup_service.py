"""
Backup & Restore Service
=========================
Data backup, restore, and migration functionality
"""
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json
import zipfile
import shutil
import io
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import DATA_DIR
from database.json_store import JSONStore
from database.user_repository import user_repo
from database.transaction_repository import transaction_repo
from database.goal_repository import goal_repo
from database.budget_repository import budget_repo
from database.reminder_repository import reminder_repo

# Backup directory
BACKUPS_DIR = DATA_DIR / "backups"
BACKUPS_DIR.mkdir(exist_ok=True)


class BackupService:
    """Handle data backup and restore operations"""
    
    def __init__(self):
        self.backups_dir = BACKUPS_DIR
        self.data_dir = DATA_DIR
    
    def create_full_backup(self, backup_name: str = None) -> Dict:
        """Create a full backup of all data"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = backup_name or f"vittasaathi_backup_{timestamp}"
        
        backup_path = self.backups_dir / f"{backup_name}.zip"
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Backup all JSON files in data directory
                for json_file in self.data_dir.glob("*.json"):
                    zipf.write(json_file, json_file.name)
                
                # Backup subdirectories (voices, reports, exports)
                for subdir in ['voices', 'reports', 'exports']:
                    subdir_path = self.data_dir / subdir
                    if subdir_path.exists():
                        for file in subdir_path.glob("*"):
                            if file.is_file():
                                arcname = f"{subdir}/{file.name}"
                                zipf.write(file, arcname)
                
                # Add metadata
                metadata = {
                    "created_at": datetime.now().isoformat(),
                    "version": "3.0.0",
                    "backup_name": backup_name,
                    "files_count": len(zipf.namelist())
                }
                zipf.writestr("_backup_metadata.json", json.dumps(metadata, indent=2))
            
            # Get backup size
            backup_size = backup_path.stat().st_size
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "backup_name": backup_name,
                "size_bytes": backup_size,
                "size_mb": round(backup_size / (1024 * 1024), 2),
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_user_backup(self, user_id: str) -> Dict:
        """Create backup for a single user"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"user_backup_{user_id}_{timestamp}"
        backup_path = self.backups_dir / f"{backup_name}.json"
        
        try:
            # Collect all user data
            user_data = {
                "metadata": {
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    "version": "3.0.0"
                },
                "user_profile": user_repo.get_user(user_id),
                "transactions": transaction_repo.get_transactions(user_id),
                "goals": goal_repo.get_user_goals(user_id),
                "budget": budget_repo.get_current_budget(user_id),
                "reminders": reminder_repo.get_user_reminders(user_id)
            }
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)
            
            backup_size = backup_path.stat().st_size
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "backup_name": backup_name,
                "size_bytes": backup_size,
                "user_id": user_id,
                "record_counts": {
                    "transactions": len(user_data.get("transactions", [])),
                    "goals": len(user_data.get("goals", [])),
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def restore_full_backup(self, backup_path: str) -> Dict:
        """Restore from a full backup"""
        
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            return {"success": False, "error": "Backup file not found"}
        
        if not backup_file.suffix == '.zip':
            return {"success": False, "error": "Invalid backup file format"}
        
        try:
            # Create a temporary backup of current data
            temp_backup = self.create_full_backup("pre_restore_backup")
            
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # Verify backup integrity
                if "_backup_metadata.json" not in zipf.namelist():
                    return {"success": False, "error": "Invalid backup: missing metadata"}
                
                # Extract to data directory
                for file_info in zipf.infolist():
                    if file_info.filename.startswith("_"):
                        continue  # Skip metadata
                    
                    target_path = self.data_dir / file_info.filename
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with zipf.open(file_info) as source:
                        with open(target_path, 'wb') as target:
                            target.write(source.read())
                
                # Read metadata
                metadata = json.loads(zipf.read("_backup_metadata.json"))
            
            return {
                "success": True,
                "restored_from": str(backup_file),
                "backup_metadata": metadata,
                "pre_restore_backup": temp_backup.get("backup_path")
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def restore_user_backup(self, backup_path: str, merge: bool = False) -> Dict:
        """Restore a single user's data"""
        
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            return {"success": False, "error": "Backup file not found"}
        
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            user_id = backup_data.get("metadata", {}).get("user_id")
            if not user_id:
                return {"success": False, "error": "Invalid backup: no user ID"}
            
            # Restore user profile
            if backup_data.get("user_profile"):
                if merge:
                    existing = user_repo.get_user(user_id) or {}
                    merged = {**existing, **backup_data["user_profile"]}
                    user_repo.update_user(user_id, merged)
                else:
                    user_repo.store.set(user_id, backup_data["user_profile"])
            
            # Restore transactions
            if backup_data.get("transactions"):
                txn_store = transaction_repo.store
                existing_txns = txn_store.get(user_id, [])
                
                if merge:
                    # Add only new transactions
                    existing_ids = {t.get("id") for t in existing_txns}
                    new_txns = [t for t in backup_data["transactions"] 
                               if t.get("id") not in existing_ids]
                    txn_store.set(user_id, existing_txns + new_txns)
                else:
                    txn_store.set(user_id, backup_data["transactions"])
            
            return {
                "success": True,
                "user_id": user_id,
                "merge_mode": merge,
                "restored_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        
        backups = []
        
        for backup_file in self.backups_dir.glob("*.zip"):
            try:
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    if "_backup_metadata.json" in zipf.namelist():
                        metadata = json.loads(zipf.read("_backup_metadata.json"))
                    else:
                        metadata = {}
                
                backups.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "size_bytes": backup_file.stat().st_size,
                    "size_mb": round(backup_file.stat().st_size / (1024 * 1024), 2),
                    "created_at": metadata.get("created_at", backup_file.stat().st_mtime),
                    "version": metadata.get("version", "unknown"),
                    "type": "full"
                })
            except:
                continue
        
        for backup_file in self.backups_dir.glob("user_backup_*.json"):
            try:
                with open(backup_file, 'r') as f:
                    data = json.load(f)
                    metadata = data.get("metadata", {})
                
                backups.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "size_bytes": backup_file.stat().st_size,
                    "user_id": metadata.get("user_id"),
                    "created_at": metadata.get("created_at"),
                    "type": "user"
                })
            except:
                continue
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return backups
    
    def delete_backup(self, backup_path: str) -> Dict:
        """Delete a backup file"""
        
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            return {"success": False, "error": "Backup not found"}
        
        if not backup_file.is_relative_to(self.backups_dir):
            return {"success": False, "error": "Invalid backup path"}
        
        try:
            backup_file.unlink()
            return {"success": True, "deleted": str(backup_file)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def export_user_data_json(self, user_id: str) -> str:
        """Export user data as JSON string (for API download)"""
        
        user_data = {
            "user_profile": user_repo.get_user(user_id),
            "transactions": transaction_repo.get_transactions(user_id),
            "goals": goal_repo.get_user_goals(user_id),
            "budget": budget_repo.get_current_budget(user_id),
            "exported_at": datetime.now().isoformat()
        }
        
        return json.dumps(user_data, indent=2, ensure_ascii=False)
    
    def import_user_data_json(self, user_id: str, json_data: str) -> Dict:
        """Import user data from JSON string"""
        
        try:
            data = json.loads(json_data)
            
            # Validate format
            if not isinstance(data, dict):
                return {"success": False, "error": "Invalid data format"}
            
            imported_counts = {}
            
            # Import transactions
            if "transactions" in data:
                for txn in data["transactions"]:
                    transaction_repo.add_transaction(
                        user_id,
                        txn.get("amount", 0),
                        txn.get("type", "expense"),
                        txn.get("category", "other"),
                        "IMPORT"
                    )
                imported_counts["transactions"] = len(data["transactions"])
            
            # Update user profile
            if "user_profile" in data:
                user_repo.update_user(user_id, data["user_profile"])
                imported_counts["profile"] = 1
            
            return {
                "success": True,
                "imported": imported_counts
            }
            
        except json.JSONDecodeError:
            return {"success": False, "error": "Invalid JSON"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_data_statistics(self) -> Dict:
        """Get statistics about stored data"""
        
        stats = {
            "total_size_mb": 0,
            "json_files": 0,
            "backup_count": 0,
            "user_count": 0,
            "transaction_count": 0,
            "files": []
        }
        
        # Count JSON files
        for json_file in self.data_dir.glob("*.json"):
            size = json_file.stat().st_size
            stats["json_files"] += 1
            stats["total_size_mb"] += size / (1024 * 1024)
            stats["files"].append({
                "name": json_file.name,
                "size_kb": round(size / 1024, 2)
            })
        
        # Count backups
        stats["backup_count"] = len(list(self.backups_dir.glob("*.zip")))
        
        # Count users and transactions
        try:
            all_users = user_repo.get_all_users()
            stats["user_count"] = len(all_users)
            
            for user_id in all_users.keys():
                txns = transaction_repo.get_transactions(user_id)
                stats["transaction_count"] += len(txns)
        except:
            pass
        
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        
        return stats
    
    def cleanup_old_backups(self, keep_count: int = 5) -> Dict:
        """Delete old backups, keeping only the most recent ones"""
        
        backups = self.list_backups()
        full_backups = [b for b in backups if b["type"] == "full"]
        
        deleted = []
        
        if len(full_backups) > keep_count:
            to_delete = full_backups[keep_count:]
            for backup in to_delete:
                result = self.delete_backup(backup["path"])
                if result["success"]:
                    deleted.append(backup["filename"])
        
        return {
            "deleted_count": len(deleted),
            "deleted": deleted,
            "remaining": keep_count
        }


# Global instance
backup_service = BackupService()
