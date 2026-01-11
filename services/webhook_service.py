"""
Webhook Service
===============
Send real-time notifications to external services
"""
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json
import hmac
import hashlib
import asyncio
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import DATA_DIR

# Try async HTTP client
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    import requests
    HTTPX_AVAILABLE = False

WEBHOOKS_DIR = DATA_DIR / "webhooks"
WEBHOOKS_DIR.mkdir(exist_ok=True)


class WebhookService:
    """Manage and trigger webhooks for external integrations"""
    
    # Available webhook events
    EVENTS = [
        "transaction.created",
        "transaction.updated",
        "transaction.deleted",
        "user.created",
        "user.updated",
        "goal.created",
        "goal.achieved",
        "goal.updated",
        "budget.exceeded",
        "fraud.detected",
        "fraud.confirmed",
        "backup.started",
        "backup.completed",
        "backup.failed",
        "bill.due",
        "bill.paid",
        "challenge.completed",
        "level.up",
        "login.success",
        "login.failed",
        "2fa.enabled",
        "2fa.disabled"
    ]
    
    def __init__(self):
        self.config_file = WEBHOOKS_DIR / "webhooks.json"
        self.log_file = WEBHOOKS_DIR / "webhook_logs.json"
        self._load_config()
    
    def _load_config(self):
        """Load webhook configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.webhooks = json.load(f)
        else:
            self.webhooks = {}
            self._save_config()
        
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                self.logs = json.load(f)
        else:
            self.logs = []
    
    def _save_config(self):
        """Save webhook configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.webhooks, f, indent=2)
    
    def _save_logs(self):
        """Save webhook logs"""
        # Keep only last 1000 logs
        self.logs = self.logs[-1000:]
        with open(self.log_file, 'w') as f:
            json.dump(self.logs, f, indent=2)
    
    def register_webhook(
        self,
        event: str,
        url: str,
        secret: str = None,
        headers: Dict = None,
        active: bool = True
    ) -> Dict:
        """Register a new webhook"""
        
        if event not in self.EVENTS:
            return {"success": False, "error": f"Invalid event. Valid events: {', '.join(self.EVENTS)}"}
        
        webhook_id = f"wh_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.webhooks)}"
        
        self.webhooks[webhook_id] = {
            "id": webhook_id,
            "event": event,
            "url": url,
            "secret": secret,
            "headers": headers or {},
            "active": active,
            "created_at": datetime.now().isoformat(),
            "last_triggered": None,
            "success_count": 0,
            "failure_count": 0
        }
        
        self._save_config()
        
        return {"success": True, "webhook_id": webhook_id, "event": event}
    
    def update_webhook(self, webhook_id: str, **kwargs) -> Dict:
        """Update webhook configuration"""
        
        if webhook_id not in self.webhooks:
            return {"success": False, "error": "Webhook not found"}
        
        for key, value in kwargs.items():
            if key in self.webhooks[webhook_id] and key not in ["id", "created_at"]:
                self.webhooks[webhook_id][key] = value
        
        self._save_config()
        
        return {"success": True, "webhook": self.webhooks[webhook_id]}
    
    def delete_webhook(self, webhook_id: str) -> Dict:
        """Delete a webhook"""
        
        if webhook_id not in self.webhooks:
            return {"success": False, "error": "Webhook not found"}
        
        del self.webhooks[webhook_id]
        self._save_config()
        
        return {"success": True, "deleted": webhook_id}
    
    def list_webhooks(self, event: str = None) -> List[Dict]:
        """List all webhooks, optionally filtered by event"""
        
        webhooks = list(self.webhooks.values())
        
        if event:
            webhooks = [w for w in webhooks if w["event"] == event]
        
        return webhooks
    
    def get_webhook(self, webhook_id: str) -> Optional[Dict]:
        """Get webhook by ID"""
        return self.webhooks.get(webhook_id)
    
    def _generate_signature(self, payload: str, secret: str) -> str:
        """Generate HMAC signature for payload"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _send_webhook_sync(self, webhook: Dict, payload: Dict) -> Dict:
        """Send webhook synchronously"""
        
        json_payload = json.dumps(payload)
        
        headers = {
            "Content-Type": "application/json",
            "X-MoneyViya-Event": payload.get("event", "unknown"),
            "X-MoneyViya-Timestamp": datetime.now().isoformat()
        }
        
        # Add custom headers
        headers.update(webhook.get("headers", {}))
        
        # Add signature if secret is set
        if webhook.get("secret"):
            signature = self._generate_signature(json_payload, webhook["secret"])
            headers["X-MoneyViya-Signature"] = f"sha256={signature}"
        
        try:
            if HTTPX_AVAILABLE:
                with httpx.Client(timeout=10.0) as client:
                    response = client.post(webhook["url"], content=json_payload, headers=headers)
            else:
                response = requests.post(webhook["url"], data=json_payload, headers=headers, timeout=10)
            
            success = 200 <= response.status_code < 300
            
            return {
                "success": success,
                "status_code": response.status_code,
                "response": response.text[:500]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _send_webhook_async(self, webhook: Dict, payload: Dict) -> Dict:
        """Send webhook asynchronously"""
        
        json_payload = json.dumps(payload)
        
        headers = {
            "Content-Type": "application/json",
            "X-MoneyViya-Event": payload.get("event", "unknown"),
            "X-MoneyViya-Timestamp": datetime.now().isoformat()
        }
        
        headers.update(webhook.get("headers", {}))
        
        if webhook.get("secret"):
            signature = self._generate_signature(json_payload, webhook["secret"])
            headers["X-MoneyViya-Signature"] = f"sha256={signature}"
        
        try:
            if HTTPX_AVAILABLE:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(webhook["url"], content=json_payload, headers=headers)
                    
                    return {
                        "success": 200 <= response.status_code < 300,
                        "status_code": response.status_code
                    }
            else:
                # Fallback to sync
                return self._send_webhook_sync(webhook, payload)
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def trigger(self, event: str, data: Dict, user_id: str = None) -> Dict:
        """Trigger webhooks for an event"""
        
        # Find all active webhooks for this event
        matching_webhooks = [
            w for w in self.webhooks.values()
            if w["event"] == event and w.get("active", True)
        ]
        
        if not matching_webhooks:
            return {"triggered": 0, "message": "No webhooks registered for this event"}
        
        payload = {
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        if user_id:
            payload["user_id"] = user_id
        
        results = []
        
        for webhook in matching_webhooks:
            result = self._send_webhook_sync(webhook, payload)
            
            # Update webhook stats
            webhook["last_triggered"] = datetime.now().isoformat()
            if result.get("success"):
                webhook["success_count"] = webhook.get("success_count", 0) + 1
            else:
                webhook["failure_count"] = webhook.get("failure_count", 0) + 1
            
            # Log the webhook call
            self.logs.append({
                "webhook_id": webhook["id"],
                "event": event,
                "timestamp": datetime.now().isoformat(),
                "success": result.get("success", False),
                "status_code": result.get("status_code"),
                "error": result.get("error")
            })
            
            results.append({
                "webhook_id": webhook["id"],
                "url": webhook["url"],
                "success": result.get("success", False)
            })
        
        self._save_config()
        self._save_logs()
        
        return {
            "triggered": len(results),
            "results": results
        }
    
    def test_webhook(self, webhook_id: str) -> Dict:
        """Send test payload to webhook"""
        
        webhook = self.webhooks.get(webhook_id)
        if not webhook:
            return {"success": False, "error": "Webhook not found"}
        
        test_payload = {
            "event": "test",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "message": "This is a test webhook from MoneyViya",
                "webhook_id": webhook_id
            }
        }
        
        result = self._send_webhook_sync(webhook, test_payload)
        
        # Log test
        self.logs.append({
            "webhook_id": webhook_id,
            "event": "test",
            "timestamp": datetime.now().isoformat(),
            "success": result.get("success", False),
            "status_code": result.get("status_code"),
            "error": result.get("error")
        })
        self._save_logs()
        
        return result
    
    def get_logs(self, webhook_id: str = None, limit: int = 100) -> List[Dict]:
        """Get webhook logs"""
        
        logs = self.logs
        
        if webhook_id:
            logs = [l for l in logs if l.get("webhook_id") == webhook_id]
        
        return logs[-limit:]
    
    def get_available_events(self) -> List[str]:
        """Get list of available webhook events"""
        return self.EVENTS
    
    def get_stats(self) -> Dict:
        """Get webhook statistics"""
        
        total_webhooks = len(self.webhooks)
        active_webhooks = len([w for w in self.webhooks.values() if w.get("active", True)])
        
        total_success = sum(w.get("success_count", 0) for w in self.webhooks.values())
        total_failure = sum(w.get("failure_count", 0) for w in self.webhooks.values())
        
        return {
            "total_webhooks": total_webhooks,
            "active_webhooks": active_webhooks,
            "total_triggers": total_success + total_failure,
            "success_rate": round(total_success / max(total_success + total_failure, 1) * 100, 1)
        }


# Global instance
webhook_service = WebhookService()


# Helper functions for easy triggering
def trigger_transaction_created(transaction: Dict, user_id: str):
    """Trigger webhook when transaction is created"""
    return webhook_service.trigger("transaction.created", transaction, user_id)

def trigger_user_created(user: Dict):
    """Trigger webhook when user is created"""
    return webhook_service.trigger("user.created", user, user.get("phone"))

def trigger_goal_achieved(goal: Dict, user_id: str):
    """Trigger webhook when goal is achieved"""
    return webhook_service.trigger("goal.achieved", goal, user_id)

def trigger_fraud_detected(alert: Dict, user_id: str):
    """Trigger webhook when fraud is detected"""
    return webhook_service.trigger("fraud.detected", alert, user_id)

def trigger_backup_completed(backup: Dict):
    """Trigger webhook when backup completes"""
    return webhook_service.trigger("backup.completed", backup)

def trigger_bill_due(bill: Dict, user_id: str):
    """Trigger webhook when bill is due"""
    return webhook_service.trigger("bill.due", bill, user_id)

