"""
Document Processor
==================
Process bank statements, receipts, and other financial documents
Supports PDF, Images (JPG, PNG), and text extraction
"""

import re
import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import sys

# For OCR
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# For PDF
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

sys.path.append(str(Path(__file__).parent.parent))
from config import TESSERACT_CMD, UPLOADS_DIR


if OCR_AVAILABLE:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


class DocumentProcessor:
    """Process financial documents for data extraction"""
    
    def __init__(self):
        self.bank_patterns = self._load_bank_patterns()
    
    def _load_bank_patterns(self) -> Dict:
        """Load patterns for different Indian banks"""
        
        return {
            "sbi": {
                "name": "State Bank of India",
                "credit_pattern": r"credited.*?Rs\.?\s*([\d,]+(?:\.\d{2})?)",
                "debit_pattern": r"debited.*?Rs\.?\s*([\d,]+(?:\.\d{2})?)",
                "balance_pattern": r"balance.*?Rs\.?\s*([\d,]+(?:\.\d{2})?)",
                "upi_pattern": r"UPI[^\d]*([\w@]+)",
            },
            "hdfc": {
                "name": "HDFC Bank",
                "credit_pattern": r"credited.*?INR\s*([\d,]+(?:\.\d{2})?)",
                "debit_pattern": r"debited.*?INR\s*([\d,]+(?:\.\d{2})?)",
                "balance_pattern": r"Bal.*?INR\s*([\d,]+(?:\.\d{2})?)",
            },
            "icici": {
                "name": "ICICI Bank",
                "credit_pattern": r"credited.*?Rs\s*([\d,]+(?:\.\d{2})?)",
                "debit_pattern": r"debited.*?Rs\s*([\d,]+(?:\.\d{2})?)",
            },
            "paytm": {
                "name": "Paytm",
                "credit_pattern": r"received.*?Rs\.?\s*([\d,]+(?:\.\d{2})?)",
                "debit_pattern": r"sent|paid.*?Rs\.?\s*([\d,]+(?:\.\d{2})?)",
            },
            "gpay": {
                "name": "Google Pay",
                "credit_pattern": r"received.*?₹\s*([\d,]+(?:\.\d{2})?)",
                "debit_pattern": r"sent|paid.*?₹\s*([\d,]+(?:\.\d{2})?)",
            },
            "phonepe": {
                "name": "PhonePe",
                "credit_pattern": r"received.*?Rs\.?\s*([\d,]+(?:\.\d{2})?)",
                "debit_pattern": r"payment.*?Rs\.?\s*([\d,]+(?:\.\d{2})?)",
            },
        }
    
    async def process_image(self, image_bytes: bytes) -> Dict:
        """Process image (receipt, screenshot, etc.)"""
        
        if not OCR_AVAILABLE:
            return {"error": "OCR not available. Please install pytesseract."}
        
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # Pre-process image for better OCR
            image = self._preprocess_image(image)
            
            # Extract text
            extracted_text = pytesseract.image_to_string(image, lang='eng+hin+tam+tel')
            
            # Parse the text
            return self._parse_extracted_text(extracted_text)
            
        except Exception as e:
            return {"error": f"Failed to process image: {str(e)}"}
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR"""
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too small
        if image.width < 300:
            ratio = 300 / image.width
            new_size = (300, int(image.height * ratio))
            image = image.resize(new_size, Image.LANCZOS)
        
        return image
    
    async def process_pdf(self, pdf_bytes: bytes) -> Dict:
        """Process PDF document (bank statement, etc.)"""
        
        if not PDF_AVAILABLE:
            return {"error": "PDF processing not available. Please install PyPDF2."}
        
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            
            all_text = ""
            for page in pdf_reader.pages:
                all_text += page.extract_text() + "\n"
            
            return self._parse_bank_statement(all_text)
            
        except Exception as e:
            return {"error": f"Failed to process PDF: {str(e)}"}
    
    def _parse_extracted_text(self, text: str) -> Dict:
        """Parse extracted text from image"""
        
        result = {
            "raw_text": text,
            "transactions": [],
            "amounts_found": [],
            "type": "unknown"
        }
        
        text_lower = text.lower()
        
        # Detect if it's a receipt, bank SMS, or other
        if any(word in text_lower for word in ["bill", "invoice", "receipt", "total"]):
            result["type"] = "receipt"
            result.update(self._parse_receipt(text))
        elif any(word in text_lower for word in ["upi", "credit", "debit", "transfer"]):
            result["type"] = "bank_sms"
            result.update(self._parse_bank_message(text))
        else:
            result["type"] = "general"
            result["amounts_found"] = self._extract_all_amounts(text)
        
        return result
    
    def _parse_receipt(self, text: str) -> Dict:
        """Parse receipt text"""
        
        result = {
            "total_amount": None,
            "items": [],
            "merchant": None,
            "date": None,
        }
        
        # Try to find total
        total_patterns = [
            r"total[:\s]*₹?\s*([\d,]+(?:\.\d{2})?)",
            r"grand\s*total[:\s]*₹?\s*([\d,]+(?:\.\d{2})?)",
            r"amount[:\s]*₹?\s*([\d,]+(?:\.\d{2})?)",
            r"payable[:\s]*₹?\s*([\d,]+(?:\.\d{2})?)",
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    result["total_amount"] = int(float(match.group(1).replace(",", "")))
                    break
                except:
                    continue
        
        # If no total found, get the largest amount
        if not result["total_amount"]:
            amounts = self._extract_all_amounts(text)
            if amounts:
                result["total_amount"] = max(amounts)
        
        return result
    
    def _parse_bank_message(self, text: str) -> Dict:
        """Parse bank SMS or screenshot"""
        
        result = {
            "amount": None,
            "transaction_type": None,  # credit or debit
            "source": None,
            "balance": None,
        }
        
        text_lower = text.lower()
        
        # Determine transaction type
        if "credit" in text_lower or "received" in text_lower or "deposited" in text_lower:
            result["transaction_type"] = "credit"
        elif "debit" in text_lower or "spent" in text_lower or "withdrawn" in text_lower or "sent" in text_lower:
            result["transaction_type"] = "debit"
        
        # Try bank-specific patterns
        for bank_id, patterns in self.bank_patterns.items():
            if bank_id.lower() in text_lower or patterns["name"].lower() in text_lower:
                if result["transaction_type"] == "credit" and "credit_pattern" in patterns:
                    match = re.search(patterns["credit_pattern"], text, re.IGNORECASE)
                    if match:
                        result["amount"] = int(float(match.group(1).replace(",", "")))
                        result["source"] = patterns["name"]
                
                elif result["transaction_type"] == "debit" and "debit_pattern" in patterns:
                    match = re.search(patterns["debit_pattern"], text, re.IGNORECASE)
                    if match:
                        result["amount"] = int(float(match.group(1).replace(",", "")))
                        result["source"] = patterns["name"]
                
                if "balance_pattern" in patterns:
                    balance_match = re.search(patterns["balance_pattern"], text, re.IGNORECASE)
                    if balance_match:
                        result["balance"] = int(float(balance_match.group(1).replace(",", "")))
                
                break
        
        # Generic extraction if bank-specific didn't work
        if not result["amount"]:
            amounts = self._extract_all_amounts(text)
            if amounts:
                result["amount"] = amounts[0]  # Take first amount
        
        return result
    
    def _parse_bank_statement(self, text: str) -> Dict:
        """Parse bank statement PDF"""
        
        result = {
            "type": "bank_statement",
            "transactions": [],
            "total_credits": 0,
            "total_debits": 0,
            "opening_balance": None,
            "closing_balance": None,
        }
        
        lines = text.split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            # Look for transaction patterns
            # Common formats: Date | Description | Debit | Credit | Balance
            
            amounts = self._extract_all_amounts(line)
            
            if len(amounts) >= 1:
                # Try to determine if credit or debit
                line_lower = line.lower()
                
                if "cr" in line_lower or "credit" in line_lower:
                    result["transactions"].append({
                        "type": "credit",
                        "amount": amounts[0],
                        "description": line[:50]
                    })
                    result["total_credits"] += amounts[0]
                elif "dr" in line_lower or "debit" in line_lower:
                    result["transactions"].append({
                        "type": "debit",
                        "amount": amounts[0],
                        "description": line[:50]
                    })
                    result["total_debits"] += amounts[0]
        
        result["net"] = result["total_credits"] - result["total_debits"]
        
        return result
    
    def _extract_all_amounts(self, text: str) -> List[int]:
        """Extract all monetary amounts from text"""
        
        amounts = []
        
        patterns = [
            r"₹\s*([\d,]+(?:\.\d{2})?)",
            r"rs\.?\s*([\d,]+(?:\.\d{2})?)",
            r"inr\s*([\d,]+(?:\.\d{2})?)",
            r"\b([\d,]+\.\d{2})\b",  # Decimal amounts
        ]
        
        text_clean = text.replace(",", "")
        
        for pattern in patterns:
            matches = re.findall(pattern, text_clean, re.IGNORECASE)
            for match in matches:
                try:
                    amount = int(float(match.replace(",", "")))
                    if 1 <= amount <= 10000000:  # Reasonable range
                        amounts.append(amount)
                except:
                    continue
        
        return sorted(set(amounts), reverse=True)
    
    def process_voice_transcription(self, text: str) -> Dict:
        """Process transcribed voice message"""
        
        # Voice messages are typically in natural language
        # Parse for transaction info
        
        from services.nlp_service import nlp_service
        
        intent_result = nlp_service.detect_intent(text)
        
        return {
            "type": "voice_transcription",
            "text": text,
            "intent": intent_result["intent"],
            "amount": intent_result["amount"],
            "category": intent_result["category"],
            "entry_type": intent_result["entry_type"],
        }
    
    async def save_upload(self, file_bytes: bytes, filename: str, user_id: str) -> str:
        """Save uploaded file and return path"""
        
        # Create user upload directory
        user_dir = UPLOADS_DIR / user_id
        user_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = re.sub(r'[^\w\-\.]', '_', filename)
        unique_filename = f"{timestamp}_{safe_filename}"
        
        file_path = user_dir / unique_filename
        
        with open(file_path, 'wb') as f:
            f.write(file_bytes)
        
        return str(file_path)


# Global instance
document_processor = DocumentProcessor()

