"""
WhatsApp Business Cloud API Service
Official Meta API - Free for 1000 conversations/month
"""

import os
import requests
from typing import Dict, Any, Optional

class WhatsAppCloudAPIService:
    """
    WhatsApp Business Cloud API integration
    https://developers.facebook.com/docs/whatsapp/cloud-api
    
    Free tier: 1000 conversations/month
    """
    
    def __init__(self):
        self.access_token = os.getenv("WHATSAPP_CLOUD_TOKEN", "")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}"
    
    def is_available(self) -> bool:
        """Check if WhatsApp Cloud API is configured"""
        return bool(self.access_token and self.phone_number_id)
    
    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def send_text_message(self, phone: str, message: str) -> dict:
        """
        Send text message via WhatsApp Cloud API
        
        Args:
            phone: Phone number with country code (e.g., 919003360494)
            message: Message text
        """
        if not self.is_available():
            return {"success": False, "error": "WhatsApp Cloud API not configured"}
        
        # Clean phone number
        phone = phone.replace("+", "").replace(" ", "").replace("-", "")
        
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self._get_headers(),
                json={
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone,
                    "type": "text",
                    "text": {
                        "preview_url": False,
                        "body": message
                    }
                },
                timeout=30
            )
            
            if response.ok:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_template_message(self, phone: str, template_name: str, 
                              language_code: str = "en",
                              components: list = None) -> dict:
        """
        Send template message (for first contact with users)
        Templates must be pre-approved by Meta
        """
        if not self.is_available():
            return {"success": False, "error": "Not configured"}
        
        phone = phone.replace("+", "").replace(" ", "")
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.ok:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": response.text}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_image_message(self, phone: str, image_url: str, caption: str = "") -> dict:
        """Send image message"""
        if not self.is_available():
            return {"success": False, "error": "Not configured"}
        
        phone = phone.replace("+", "").replace(" ", "")
        
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self._get_headers(),
                json={
                    "messaging_product": "whatsapp",
                    "to": phone,
                    "type": "image",
                    "image": {
                        "link": image_url,
                        "caption": caption
                    }
                },
                timeout=30
            )
            
            if response.ok:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": response.text}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_document_message(self, phone: str, doc_url: str, 
                              filename: str, caption: str = "") -> dict:
        """Send document (PDF, etc.)"""
        if not self.is_available():
            return {"success": False, "error": "Not configured"}
        
        phone = phone.replace("+", "").replace(" ", "")
        
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self._get_headers(),
                json={
                    "messaging_product": "whatsapp",
                    "to": phone,
                    "type": "document",
                    "document": {
                        "link": doc_url,
                        "filename": filename,
                        "caption": caption
                    }
                },
                timeout=30
            )
            
            if response.ok:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": response.text}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_audio_message(self, phone: str, audio_url: str) -> dict:
        """Send audio/voice message"""
        if not self.is_available():
            return {"success": False, "error": "Not configured"}
        
        phone = phone.replace("+", "").replace(" ", "")
        
        try:
            response = requests.post(
                f"{self.base_url}/messages",
                headers=self._get_headers(),
                json={
                    "messaging_product": "whatsapp",
                    "to": phone,
                    "type": "audio",
                    "audio": {
                        "link": audio_url
                    }
                },
                timeout=30
            )
            
            if response.ok:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": response.text}
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
whatsapp_cloud_service = WhatsAppCloudAPIService()
