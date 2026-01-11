"""
Evolution API Service
Provides WhatsApp integration using Evolution API (free, unlimited messages)
"""

import os
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

class EvolutionAPIService:
    """
    Evolution API integration for WhatsApp messaging
    https://github.com/EvolutionAPI/evolution-api
    """
    
    def __init__(self):
        self.base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        self.api_key = os.getenv("EVOLUTION_API_KEY", "")
        self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "MoneyViya")
        
    def _get_headers(self) -> dict:
        """Get API headers"""
        return {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
    
    def is_available(self) -> bool:
        """Check if Evolution API is configured and running"""
        if not self.api_key:
            return False
        try:
            response = requests.get(
                f"{self.base_url}/instance/fetchInstances",
                headers=self._get_headers(),
                timeout=5
            )
            return response.ok
        except:
            return False
    
    def get_instance_status(self) -> dict:
        """Get status of WhatsApp instance"""
        try:
            response = requests.get(
                f"{self.base_url}/instance/connectionState/{self.instance_name}",
                headers=self._get_headers(),
                timeout=10
            )
            if response.ok:
                return response.json()
            return {"error": response.text}
        except Exception as e:
            return {"error": str(e)}
    
    def create_instance(self) -> dict:
        """Create a new WhatsApp instance"""
        try:
            response = requests.post(
                f"{self.base_url}/instance/create",
                headers=self._get_headers(),
                json={
                    "instanceName": self.instance_name,
                    "qrcode": True,
                    "integration": "WHATSAPP-BAILEYS"
                },
                timeout=30
            )
            if response.ok:
                return response.json()
            return {"error": response.text}
        except Exception as e:
            return {"error": str(e)}
    
    def get_qr_code(self) -> Optional[str]:
        """Get QR code for WhatsApp Web authentication"""
        try:
            response = requests.get(
                f"{self.base_url}/instance/connect/{self.instance_name}",
                headers=self._get_headers(),
                timeout=30
            )
            if response.ok:
                data = response.json()
                return data.get("base64", data.get("qrcode"))
            return None
        except Exception as e:
            print(f"QR code error: {e}")
            return None
    
    def send_text_message(self, phone: str, message: str) -> dict:
        """
        Send text message via WhatsApp
        
        Args:
            phone: Phone number with country code (e.g., +919003360494 or 919003360494)
            message: Message text to send
        """
        # Clean phone number
        phone = phone.replace("+", "").replace(" ", "").replace("-", "")
        
        try:
            response = requests.post(
                f"{self.base_url}/message/sendText/{self.instance_name}",
                headers=self._get_headers(),
                json={
                    "number": phone,
                    "text": message
                },
                timeout=30
            )
            
            if response.ok:
                print(f"[Evolution] Message sent to {phone}")
                return {"success": True, "data": response.json()}
            else:
                print(f"[Evolution] Error: {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"[Evolution] Exception: {e}")
            return {"success": False, "error": str(e)}
    
    def send_media_message(self, phone: str, media_url: str, 
                           caption: str = "", media_type: str = "image") -> dict:
        """
        Send media message (image, video, audio, document)
        
        Args:
            phone: Phone number
            media_url: URL of the media file
            caption: Optional caption
            media_type: image, video, audio, document
        """
        phone = phone.replace("+", "").replace(" ", "")
        
        try:
            response = requests.post(
                f"{self.base_url}/message/sendMedia/{self.instance_name}",
                headers=self._get_headers(),
                json={
                    "number": phone,
                    "mediatype": media_type,
                    "media": media_url,
                    "caption": caption
                },
                timeout=60
            )
            
            if response.ok:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": response.text}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_audio_message(self, phone: str, audio_url: str) -> dict:
        """Send audio/voice message"""
        return self.send_media_message(phone, audio_url, media_type="audio")
    
    def send_document(self, phone: str, doc_url: str, filename: str) -> dict:
        """Send document (PDF, etc.)"""
        phone = phone.replace("+", "").replace(" ", "")
        
        try:
            response = requests.post(
                f"{self.base_url}/message/sendMedia/{self.instance_name}",
                headers=self._get_headers(),
                json={
                    "number": phone,
                    "mediatype": "document",
                    "media": doc_url,
                    "fileName": filename
                },
                timeout=60
            )
            
            if response.ok:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": response.text}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def set_webhook(self, webhook_url: str, events: List[str] = None) -> dict:
        """
        Set webhook URL to receive incoming messages
        
        Args:
            webhook_url: URL to receive webhook events
            events: List of events to subscribe to
        """
        if events is None:
            events = [
                "MESSAGES_UPSERT",  # New messages
                "MESSAGES_UPDATE",   # Message status updates
                "CONNECTION_UPDATE"  # Connection status
            ]
        
        try:
            response = requests.post(
                f"{self.base_url}/webhook/set/{self.instance_name}",
                headers=self._get_headers(),
                json={
                    "enabled": True,
                    "url": webhook_url,
                    "webhookByEvents": True,
                    "events": events
                },
                timeout=30
            )
            
            if response.ok:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": response.text}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_profile_picture(self, phone: str) -> Optional[str]:
        """Get profile picture URL of a phone number"""
        phone = phone.replace("+", "").replace(" ", "")
        
        try:
            response = requests.get(
                f"{self.base_url}/chat/fetchProfilePictureUrl/{self.instance_name}",
                headers=self._get_headers(),
                params={"number": phone},
                timeout=10
            )
            
            if response.ok:
                data = response.json()
                return data.get("profilePictureUrl")
            return None
            
        except Exception as e:
            return None


# Singleton instance
evolution_service = EvolutionAPIService()


# Helper function to check which messaging service to use
def get_messaging_service():
    """
    Get the appropriate messaging service
    Returns Evolution API if available, otherwise falls back to Twilio
    """
    if evolution_service.is_available():
        return "evolution"
    
    # Check Twilio
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    if twilio_sid:
        return "twilio"
    
    return None


def send_whatsapp_message(phone: str, message: str) -> dict:
    """
    Universal function to send WhatsApp message
    Uses Evolution API if available, falls back to Twilio
    """
    service = get_messaging_service()
    
    if service == "evolution":
        return evolution_service.send_text_message(phone, message)
    
    elif service == "twilio":
        # Twilio fallback
        from twilio.rest import Client
        
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        try:
            client = Client(account_sid, auth_token)
            msg = client.messages.create(
                from_="whatsapp:+14155238886",
                to=f"whatsapp:{phone}",
                body=message
            )
            return {"success": True, "sid": msg.sid}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    else:
        return {"success": False, "error": "No messaging service configured"}

