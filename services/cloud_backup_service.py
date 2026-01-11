"""
Cloud Backup Service
====================
Support for AWS S3 and Google Cloud Storage backup
"""
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import DATA_DIR

# Try to import cloud SDKs
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    from google.cloud import storage as gcs
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False


class CloudBackupService:
    """Cloud backup to AWS S3 and Google Cloud Storage"""
    
    def __init__(self):
        self.config_file = DATA_DIR / "cloud_config.json"
        self._load_config()
    
    def _load_config(self):
        """Load cloud configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "aws": {
                    "enabled": False,
                    "access_key_id": "",
                    "secret_access_key": "",
                    "region": "ap-south-1",
                    "bucket_name": "MoneyViya-backups"
                },
                "gcs": {
                    "enabled": False,
                    "credentials_path": "",
                    "bucket_name": "MoneyViya-backups"
                },
                "default_provider": "aws",
                "auto_sync": False,
                "upload_history": []
            }
            self._save_config()
    
    def _save_config(self):
        """Save cloud configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def configure_aws(self, access_key_id: str, secret_access_key: str, region: str = "ap-south-1", bucket_name: str = "MoneyViya-backups") -> Dict:
        """Configure AWS S3"""
        if not AWS_AVAILABLE:
            return {"success": False, "error": "boto3 not installed. Run: pip install boto3"}
        
        self.config["aws"] = {
            "enabled": True,
            "access_key_id": access_key_id,
            "secret_access_key": secret_access_key,
            "region": region,
            "bucket_name": bucket_name
        }
        self.config["default_provider"] = "aws"
        self._save_config()
        
        # Test connection
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region
            )
            # Check if bucket exists or create it
            try:
                s3.head_bucket(Bucket=bucket_name)
            except ClientError:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            return {"success": True, "message": "AWS S3 configured and connected"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def configure_gcs(self, credentials_path: str, bucket_name: str = "MoneyViya-backups") -> Dict:
        """Configure Google Cloud Storage"""
        if not GCS_AVAILABLE:
            return {"success": False, "error": "google-cloud-storage not installed. Run: pip install google-cloud-storage"}
        
        self.config["gcs"] = {
            "enabled": True,
            "credentials_path": credentials_path,
            "bucket_name": bucket_name
        }
        self.config["default_provider"] = "gcs"
        self._save_config()
        
        # Test connection
        try:
            client = gcs.Client.from_service_account_json(credentials_path)
            bucket = client.bucket(bucket_name)
            if not bucket.exists():
                bucket.create(location="asia-south1")
            return {"success": True, "message": "GCS configured and connected"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_s3_client(self):
        """Get AWS S3 client"""
        if not AWS_AVAILABLE or not self.config["aws"]["enabled"]:
            return None
        return boto3.client(
            's3',
            aws_access_key_id=self.config["aws"]["access_key_id"],
            aws_secret_access_key=self.config["aws"]["secret_access_key"],
            region_name=self.config["aws"]["region"]
        )
    
    def _get_gcs_client(self):
        """Get GCS client"""
        if not GCS_AVAILABLE or not self.config["gcs"]["enabled"]:
            return None
        return gcs.Client.from_service_account_json(self.config["gcs"]["credentials_path"])
    
    def upload_to_s3(self, local_path: str, remote_key: str = None) -> Dict:
        """Upload file to AWS S3"""
        s3 = self._get_s3_client()
        if not s3:
            return {"success": False, "error": "AWS S3 not configured"}
        
        local_file = Path(local_path)
        if not local_file.exists():
            return {"success": False, "error": "File not found"}
        
        remote_key = remote_key or f"backups/{datetime.now().strftime('%Y/%m/%d')}/{local_file.name}"
        
        try:
            s3.upload_file(str(local_file), self.config["aws"]["bucket_name"], remote_key)
            
            # Log upload
            self.config["upload_history"].append({
                "timestamp": datetime.now().isoformat(),
                "provider": "aws",
                "remote_key": remote_key,
                "size_bytes": local_file.stat().st_size
            })
            self.config["upload_history"] = self.config["upload_history"][-50:]
            self._save_config()
            
            return {
                "success": True,
                "provider": "aws",
                "bucket": self.config["aws"]["bucket_name"],
                "key": remote_key,
                "url": f"s3://{self.config['aws']['bucket_name']}/{remote_key}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def upload_to_gcs(self, local_path: str, remote_name: str = None) -> Dict:
        """Upload file to Google Cloud Storage"""
        client = self._get_gcs_client()
        if not client:
            return {"success": False, "error": "GCS not configured"}
        
        local_file = Path(local_path)
        if not local_file.exists():
            return {"success": False, "error": "File not found"}
        
        remote_name = remote_name or f"backups/{datetime.now().strftime('%Y/%m/%d')}/{local_file.name}"
        
        try:
            bucket = client.bucket(self.config["gcs"]["bucket_name"])
            blob = bucket.blob(remote_name)
            blob.upload_from_filename(str(local_file))
            
            # Log upload
            self.config["upload_history"].append({
                "timestamp": datetime.now().isoformat(),
                "provider": "gcs",
                "remote_key": remote_name,
                "size_bytes": local_file.stat().st_size
            })
            self.config["upload_history"] = self.config["upload_history"][-50:]
            self._save_config()
            
            return {
                "success": True,
                "provider": "gcs",
                "bucket": self.config["gcs"]["bucket_name"],
                "name": remote_name,
                "url": f"gs://{self.config['gcs']['bucket_name']}/{remote_name}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def upload_backup(self, local_path: str, provider: str = None) -> Dict:
        """Upload backup to configured cloud provider"""
        provider = provider or self.config["default_provider"]
        
        if provider == "aws":
            return self.upload_to_s3(local_path)
        elif provider == "gcs":
            return self.upload_to_gcs(local_path)
        else:
            return {"success": False, "error": f"Unknown provider: {provider}"}
    
    def download_from_s3(self, remote_key: str, local_path: str) -> Dict:
        """Download file from AWS S3"""
        s3 = self._get_s3_client()
        if not s3:
            return {"success": False, "error": "AWS S3 not configured"}
        
        try:
            s3.download_file(self.config["aws"]["bucket_name"], remote_key, local_path)
            return {"success": True, "local_path": local_path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def download_from_gcs(self, remote_name: str, local_path: str) -> Dict:
        """Download file from GCS"""
        client = self._get_gcs_client()
        if not client:
            return {"success": False, "error": "GCS not configured"}
        
        try:
            bucket = client.bucket(self.config["gcs"]["bucket_name"])
            blob = bucket.blob(remote_name)
            blob.download_to_filename(local_path)
            return {"success": True, "local_path": local_path}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_s3_backups(self, prefix: str = "backups/") -> List[Dict]:
        """List backups in S3"""
        s3 = self._get_s3_client()
        if not s3:
            return []
        
        try:
            response = s3.list_objects_v2(Bucket=self.config["aws"]["bucket_name"], Prefix=prefix)
            backups = []
            for obj in response.get('Contents', []):
                backups.append({
                    "key": obj['Key'],
                    "size_bytes": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat()
                })
            return backups
        except Exception:
            return []
    
    def list_gcs_backups(self, prefix: str = "backups/") -> List[Dict]:
        """List backups in GCS"""
        client = self._get_gcs_client()
        if not client:
            return []
        
        try:
            bucket = client.bucket(self.config["gcs"]["bucket_name"])
            blobs = bucket.list_blobs(prefix=prefix)
            backups = []
            for blob in blobs:
                backups.append({
                    "name": blob.name,
                    "size_bytes": blob.size,
                    "updated": blob.updated.isoformat() if blob.updated else None
                })
            return backups
        except Exception:
            return []
    
    def list_cloud_backups(self, provider: str = None) -> List[Dict]:
        """List all cloud backups"""
        provider = provider or self.config["default_provider"]
        
        if provider == "aws":
            return self.list_s3_backups()
        elif provider == "gcs":
            return self.list_gcs_backups()
        return []
    
    def delete_s3_backup(self, remote_key: str) -> Dict:
        """Delete backup from S3"""
        s3 = self._get_s3_client()
        if not s3:
            return {"success": False, "error": "AWS S3 not configured"}
        
        try:
            s3.delete_object(Bucket=self.config["aws"]["bucket_name"], Key=remote_key)
            return {"success": True, "deleted": remote_key}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_gcs_backup(self, remote_name: str) -> Dict:
        """Delete backup from GCS"""
        client = self._get_gcs_client()
        if not client:
            return {"success": False, "error": "GCS not configured"}
        
        try:
            bucket = client.bucket(self.config["gcs"]["bucket_name"])
            blob = bucket.blob(remote_name)
            blob.delete()
            return {"success": True, "deleted": remote_name}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict:
        """Get cloud backup status"""
        return {
            "aws_available": AWS_AVAILABLE,
            "aws_enabled": self.config["aws"]["enabled"],
            "aws_bucket": self.config["aws"]["bucket_name"] if self.config["aws"]["enabled"] else None,
            "gcs_available": GCS_AVAILABLE,
            "gcs_enabled": self.config["gcs"]["enabled"],
            "gcs_bucket": self.config["gcs"]["bucket_name"] if self.config["gcs"]["enabled"] else None,
            "default_provider": self.config["default_provider"],
            "auto_sync": self.config["auto_sync"],
            "recent_uploads": self.config["upload_history"][-5:]
        }
    
    def sync_local_backups(self, provider: str = None) -> Dict:
        """Sync all local backups to cloud"""
        from services.backup_service import backup_service
        
        provider = provider or self.config["default_provider"]
        backups = backup_service.list_backups()
        
        uploaded = []
        failed = []
        
        for backup in backups:
            result = self.upload_backup(backup["path"], provider)
            if result.get("success"):
                uploaded.append(backup["filename"])
            else:
                failed.append({"file": backup["filename"], "error": result.get("error")})
        
        return {
            "uploaded": len(uploaded),
            "failed": len(failed),
            "uploaded_files": uploaded,
            "failed_files": failed
        }


# Global instance
cloud_backup_service = CloudBackupService()

