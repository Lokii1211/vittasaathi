"""
Transaction Repository - Complete transaction management
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path
from collections import defaultdict
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import TRANSACTIONS_DB_FILE, INCOME_CATEGORIES, EXPENSE_CATEGORIES
from database.json_store import JSONStore


class TransactionRepository:
    """Complete transaction management with analytics"""
    
    def __init__(self):
        self.store = JSONStore(TRANSACTIONS_DB_FILE)
    
    def add_transaction(
        self,
        user_id: str,
        amount: int,
        txn_type: str,  # income, expense, transfer
        category: str,
        source: str = "MANUAL",
        description: str = "",
        is_recurring: bool = False,
        receipt_image: str = None
    ) -> Dict:
        """Add a new transaction"""
        
        txn_id = self.store.generate_id()
        transaction = {
            "id": txn_id,
            "user_id": user_id,
            "amount": amount,
            "type": txn_type,
            "category": category,
            "source": source,  # CASH, UPI, BANK, CARD, MANUAL
            "description": description,
            "is_recurring": is_recurring,
            "receipt_image": receipt_image,
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "month": datetime.now().strftime("%Y-%m"),
            "created_at": datetime.now().isoformat(),
        }
        
        self.store.set(txn_id, transaction)
        return transaction
    
    def get_transaction(self, txn_id: str) -> Optional[Dict]:
        """Get transaction by ID"""
        return self.store.get(txn_id)
    
    def get_transactions(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get all transactions for a user - simple alias"""
        return self.get_user_transactions(user_id, limit=limit)
    
    def get_user_transactions(
        self,
        user_id: str,
        txn_type: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        category: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get user transactions with filters"""
        
        all_txns = self.store.get_all()
        user_txns = []
        
        for txn in all_txns.values():
            if txn.get("user_id") != user_id:
                continue
            
            if txn_type and txn.get("type") != txn_type:
                continue
            
            if category and txn.get("category") != category:
                continue
            
            txn_date = datetime.fromisoformat(txn["timestamp"])
            
            if start_date and txn_date < start_date:
                continue
            
            if end_date and txn_date > end_date:
                continue
            
            user_txns.append(txn)
        
        # Sort by timestamp descending
        user_txns.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return user_txns[:limit]
    
    def get_today_transactions(self, user_id: str) -> List[Dict]:
        """Get today's transactions"""
        today = datetime.now().strftime("%Y-%m-%d")
        all_txns = self.store.get_all()
        
        return [
            txn for txn in all_txns.values()
            if txn.get("user_id") == user_id and txn.get("date") == today
        ]
    
    def get_month_transactions(self, user_id: str, month: str = None) -> List[Dict]:
        """Get month's transactions"""
        if not month:
            month = datetime.now().strftime("%Y-%m")
        
        all_txns = self.store.get_all()
        
        return [
            txn for txn in all_txns.values()
            if txn.get("user_id") == user_id and txn.get("month") == month
        ]
    
    def get_transactions_in_range(self, user_id: str, start_date: str, end_date: str) -> List[Dict]:
        """Get transactions within a date range (YYYY-MM-DD format)"""
        all_txns = self.store.get_all()
        
        return [
            txn for txn in all_txns.values()
            if txn.get("user_id") == user_id 
            and txn.get("date", "") >= start_date 
            and txn.get("date", "") <= end_date
        ]
    
    def get_daily_summary(self, user_id: str, date: str = None) -> Dict:
        """Get daily income/expense summary"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        all_txns = self.store.get_all()
        day_txns = [
            txn for txn in all_txns.values()
            if txn.get("user_id") == user_id and txn.get("date") == date
        ]
        
        income = sum(t["amount"] for t in day_txns if t["type"] == "income")
        expense = sum(t["amount"] for t in day_txns if t["type"] == "expense")
        
        return {
            "date": date,
            "income": income,
            "expense": expense,
            "net": income - expense,
            "transaction_count": len(day_txns)
        }
    
    def get_monthly_summary(self, user_id: str, month: str = None) -> Dict:
        """Get monthly income/expense summary"""
        if not month:
            month = datetime.now().strftime("%Y-%m")
        
        txns = self.get_month_transactions(user_id, month)
        
        income = sum(t["amount"] for t in txns if t["type"] == "income")
        expense = sum(t["amount"] for t in txns if t["type"] == "expense")
        
        # Category breakdown
        income_by_category = defaultdict(int)
        expense_by_category = defaultdict(int)
        
        for txn in txns:
            if txn["type"] == "income":
                income_by_category[txn["category"]] += txn["amount"]
            elif txn["type"] == "expense":
                expense_by_category[txn["category"]] += txn["amount"]
        
        return {
            "month": month,
            "total_income": income,
            "total_expense": expense,
            "net_savings": income - expense,
            "savings_rate": round((income - expense) / income * 100, 1) if income > 0 else 0,
            "income_by_category": dict(income_by_category),
            "expense_by_category": dict(expense_by_category),
            "transaction_count": len(txns)
        }
    
    def get_income_history(self, user_id: str, months: int = 6) -> Dict[str, int]:
        """Get monthly income for past N months"""
        all_txns = self.store.get_all()
        monthly_income = defaultdict(int)
        
        cutoff = datetime.now() - timedelta(days=months * 30)
        
        for txn in all_txns.values():
            if txn.get("user_id") != user_id:
                continue
            if txn.get("type") != "income":
                continue
            
            txn_date = datetime.fromisoformat(txn["timestamp"])
            if txn_date < cutoff:
                continue
            
            monthly_income[txn["month"]] += txn["amount"]
        
        return dict(monthly_income)
    
    def get_expense_by_category(self, user_id: str, month: str = None) -> Dict[str, int]:
        """Get expense breakdown by category"""
        txns = self.get_month_transactions(user_id, month)
        
        category_totals = defaultdict(int)
        for txn in txns:
            if txn["type"] == "expense":
                category_totals[txn["category"]] += txn["amount"]
        
        return dict(category_totals)
    
    def get_average_daily_income(self, user_id: str, days: int = 30) -> float:
        """Calculate average daily income"""
        start = datetime.now() - timedelta(days=days)
        txns = self.get_user_transactions(user_id, "income", start_date=start)
        
        if not txns:
            return 0.0
        
        total = sum(t["amount"] for t in txns)
        return round(total / days, 2)
    
    def get_average_daily_expense(self, user_id: str, days: int = 30) -> float:
        """Calculate average daily expense"""
        start = datetime.now() - timedelta(days=days)
        txns = self.get_user_transactions(user_id, "expense", start_date=start)
        
        if not txns:
            return 0.0
        
        total = sum(t["amount"] for t in txns)
        return round(total / days, 2)
    
    def get_income_trend(self, user_id: str) -> Dict:
        """Analyze income trend (increasing/decreasing/stable)"""
        history = self.get_income_history(user_id, 6)
        
        if len(history) < 2:
            return {"trend": "unknown", "message": "Not enough data"}
        
        sorted_months = sorted(history.keys())
        incomes = [history[m] for m in sorted_months]
        
        # Simple trend analysis
        recent_avg = sum(incomes[-3:]) / min(len(incomes), 3)
        older_avg = sum(incomes[:-3]) / max(len(incomes) - 3, 1) if len(incomes) > 3 else incomes[0]
        
        if recent_avg > older_avg * 1.1:
            return {"trend": "increasing", "change": round((recent_avg - older_avg) / older_avg * 100, 1)}
        elif recent_avg < older_avg * 0.9:
            return {"trend": "decreasing", "change": round((recent_avg - older_avg) / older_avg * 100, 1)}
        else:
            return {"trend": "stable", "change": 0}
    
    def get_spending_patterns(self, user_id: str) -> Dict:
        """Analyze spending patterns"""
        today = datetime.now()
        current_month = today.strftime("%Y-%m")
        last_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
        
        current_expenses = self.get_expense_by_category(user_id, current_month)
        last_expenses = self.get_expense_by_category(user_id, last_month)
        
        patterns = {
            "current_month": current_expenses,
            "last_month": last_expenses,
            "changes": {},
            "warnings": []
        }
        
        # Calculate changes
        for category in set(current_expenses.keys()) | set(last_expenses.keys()):
            current = current_expenses.get(category, 0)
            last = last_expenses.get(category, 0)
            
            if last > 0:
                change = ((current - last) / last) * 100
                patterns["changes"][category] = round(change, 1)
                
                if change > 50:
                    patterns["warnings"].append(f"{category} spending increased by {round(change)}%")
        
        return patterns
    
    def count_recent_transactions(self, user_id: str, minutes: int = 10) -> int:
        """Count transactions in last N minutes (for fraud detection)"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        all_txns = self.store.get_all()
        
        count = 0
        for txn in all_txns.values():
            if txn.get("user_id") != user_id:
                continue
            
            txn_time = datetime.fromisoformat(txn["timestamp"])
            if txn_time >= cutoff:
                count += 1
        
        return count
    
    def get_payees(self, user_id: str) -> List[str]:
        """Get all known payees/sources for user"""
        all_txns = self.store.get_all()
        payees = set()
        
        for txn in all_txns.values():
            if txn.get("user_id") == user_id:
                payees.add(txn.get("source", "UNKNOWN"))
        
        return list(payees)
    
    def is_new_payee(self, user_id: str, source: str) -> bool:
        """Check if payee is new (for fraud detection)"""
        return source not in self.get_payees(user_id)


# Global instance  
transaction_repo = TransactionRepository()

