"""
OpenAI Integration Service
Provides voice transcription, smart NLP, and AI-powered responses
"""

import os
import re
import requests
from typing import Dict, Any, Optional
from datetime import datetime

# OpenAI setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

class OpenAIService:
    """OpenAI integration for transcription and NLP"""
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def is_available(self) -> bool:
        """Check if OpenAI is configured"""
        return bool(self.api_key and len(self.api_key) > 20)
    
    def transcribe_audio(self, audio_url: str) -> str:
        """Transcribe audio from URL using Whisper API"""
        if not self.is_available():
            return ""
        
        try:
            # Download audio file
            audio_response = requests.get(audio_url, timeout=30)
            if not audio_response.ok:
                print(f"Failed to download audio: {audio_response.status_code}")
                return ""
            
            # Send to Whisper API
            files = {
                'file': ('audio.ogg', audio_response.content, 'audio/ogg'),
                'model': (None, 'whisper-1'),
                'language': (None, 'hi')  # Hindi - will auto-detect
            }
            
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files=files,
                timeout=60
            )
            
            if response.ok:
                result = response.json()
                transcript = result.get("text", "")
                print(f"Transcribed: {transcript}")
                return transcript
            else:
                print(f"Whisper API error: {response.text}")
                return ""
                
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def understand_message(self, message: str, language: str = "english", context: dict = None) -> Dict[str, Any]:
        """Use GPT to understand financial messages with better NLP - handles multiple transactions"""
        if not self.is_available():
            return self._fallback_parse(message)
        
        try:
            prompt = f"""You are a financial assistant that understands messages in multiple languages (Hindi, Tamil, Telugu, English, etc.)

Parse this message and extract ALL financial transactions. A single message may contain BOTH income AND expense.

User's language: {language}
Message: "{message}"

IMPORTANT: If message contains BOTH earned/income AND spent/expense, return MULTIPLE_TRANSACTIONS.

Respond ONLY with valid JSON in ONE of these formats:

For SINGLE transaction:
{{"intent": "EXPENSE_ENTRY", "amount": 200, "category": "food", "description": "lunch"}}

For MULTIPLE transactions (earned AND spent):
{{"intent": "MULTIPLE_TRANSACTIONS", "transactions": [
    {{"type": "income", "amount": 500, "category": "salary", "description": "earned"}},
    {{"type": "expense", "amount": 200, "category": "other", "description": "spent"}}
]}}

For queries:
{{"intent": "BALANCE_QUERY"}} or {{"intent": "REPORT_QUERY"}} or {{"intent": "GREETING"}}

Examples:
- "I earned 700 and spent 300" = MULTIPLE_TRANSACTIONS with income 700 AND expense 300
- "earned 500, spent 200" = MULTIPLE_TRANSACTIONS
- "500 kamaya 200 kharch" = MULTIPLE_TRANSACTIONS  
- "spent 200 on food" = EXPENSE_ENTRY
- "earned 500" = INCOME_ENTRY
- "hi" / "hello" = GREETING
- "balance" / "report" = BALANCE_QUERY / REPORT_QUERY

Categories: salary, freelance, tips, food, transport, shopping, bills, health, entertainment, other

Now parse this message: "{message}"
"""
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a financial transaction parser. Parse messages for income AND/OR expense. If message contains BOTH, return MULTIPLE_TRANSACTIONS. Always respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 300
                },
                timeout=30
            )
            
            if response.ok:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                
                # Parse JSON from response
                import json
                try:
                    # Find JSON in response
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group())
                        print(f"[NLP] Parsed: {parsed}")
                        return parsed
                except Exception as e:
                    print(f"[NLP] JSON parse error: {e}")
            
            return self._fallback_parse(message)
            
        except Exception as e:
            print(f"OpenAI NLP error: {e}")
            return self._fallback_parse(message)
    
    def _fallback_parse(self, message: str) -> Dict[str, Any]:
        """Fallback NLP when OpenAI is not available"""
        message_lower = message.lower()
        
        # Extract amount
        amount_match = re.search(r'(\d+)', message)
        amount = int(amount_match.group(1)) if amount_match else 0
        
        # Detect intent
        income_words = ['earn', 'income', 'salary', 'got', 'received', 'कमाया', 'കിട്ടി', 'சம்பளம்']
        expense_words = ['spent', 'spend', 'खर्च', 'செலவு', 'ఖర్చు', 'paid', 'bought']
        balance_words = ['balance', 'बैलेंस', 'how much', 'कितना']
        
        intent = "OTHER"
        if any(w in message_lower for w in income_words):
            intent = "INCOME_ENTRY"
        elif any(w in message_lower for w in expense_words):
            intent = "EXPENSE_ENTRY"
        elif any(w in message_lower for w in balance_words):
            intent = "BALANCE_QUERY"
        
        # Detect category
        category = "other"
        food_words = ['food', 'खाना', 'lunch', 'dinner', 'breakfast', 'chai', 'coffee']
        transport_words = ['petrol', 'uber', 'ola', 'auto', 'bus', 'train']
        
        if any(w in message_lower for w in food_words):
            category = "food"
        elif any(w in message_lower for w in transport_words):
            category = "transport"
        
        return {
            "intent": intent,
            "amount": amount,
            "category": category,
            "description": message[:50]
        }
    
    def generate_financial_plan(self, user_data: dict, language: str = "english") -> str:
        """Generate a personalized financial plan using AI"""
        if not self.is_available():
            return self._fallback_plan(user_data, language)
        
        try:
            income = user_data.get("monthly_income", 20000)
            savings = user_data.get("savings_target", int(income * 0.2))
            goals = user_data.get("financial_goals", ["General Savings"])
            name = user_data.get("name", "Friend")
            
            prompt = f"""Create a personalized financial plan in {language} for:
- Name: {name}
- Monthly Income: ₹{income}
- Savings Goal: ₹{savings}/month
- Financial Goals: {', '.join(goals) if isinstance(goals, list) else goals}

Include:
1. Daily income target (if applicable)
2. Daily spending limit
3. Daily savings target
4. Weekly/Monthly milestones
5. Motivational message

Keep it concise and use emojis. Respond in {language}."""

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=self.headers,
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.ok:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
                
        except Exception as e:
            print(f"Plan generation error: {e}")
        
        return self._fallback_plan(user_data, language)
    
    def _fallback_plan(self, user_data: dict, language: str) -> str:
        """Fallback plan generation"""
        income = user_data.get("monthly_income", 20000)
        savings = user_data.get("savings_target", int(income * 0.2))
        daily_budget = (income - savings) // 30
        daily_savings = savings // 30
        
        if language == "hindi":
            return f"""📊 *आपका वित्तीय प्लान*

💰 मासिक आय: ₹{income:,}
💾 बचत लक्ष्य: ₹{savings:,}/माह

📅 *दैनिक लक्ष्य:*
• 💸 खर्च सीमा: ₹{daily_budget:,}/दिन
• 💾 बचत लक्ष्य: ₹{daily_savings:,}/दिन

💪 छोटे कदम, बड़े लक्ष्य!"""
        
        return f"""📊 *Your Financial Plan*

💰 Monthly Income: ₹{income:,}
💾 Savings Goal: ₹{savings:,}/month

📅 *Daily Targets:*
• 💸 Spending Limit: ₹{daily_budget:,}/day
• 💾 Savings Target: ₹{daily_savings:,}/day

💪 Small steps, big goals!"""


# Global instance
openai_service = OpenAIService()


def transcribe_voice(audio_url: str) -> str:
    """Transcribe voice message"""
    return openai_service.transcribe_audio(audio_url)


def understand_message(message: str, language: str = "english") -> Dict[str, Any]:
    """Smart NLP understanding"""
    return openai_service.understand_message(message, language)


def generate_plan(user_data: dict, language: str = "english") -> str:
    """Generate personalized plan"""
    return openai_service.generate_financial_plan(user_data, language)
