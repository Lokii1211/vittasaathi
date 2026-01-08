"""
Export Service - Excel/CSV Export
=================================
Export financial data to Excel and CSV formats
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import csv
import io
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config import DATA_DIR
from database.user_repository import user_repo
from database.transaction_repository import transaction_repo
from services.analytics_service import analytics_service

# Create exports directory
EXPORTS_DIR = DATA_DIR / "exports"
EXPORTS_DIR.mkdir(exist_ok=True)

# Try to import pandas and openpyxl for Excel
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


class ExportService:
    """Export financial data to various formats"""
    
    def __init__(self):
        self.exports_dir = EXPORTS_DIR
    
    def export_transactions_csv(
        self, 
        user_id: str, 
        start_date: str = None, 
        end_date: str = None,
        transaction_type: str = None
    ) -> str:
        """Export transactions to CSV file"""
        
        # Get transactions
        transactions = transaction_repo.get_transactions(
            user_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date
        )
        
        if not transactions:
            return None
        
        # Create filename
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transactions_{user_id}_{date_str}.csv"
        filepath = self.exports_dir / filename
        
        # Write CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Date', 'Time', 'Type', 'Category', 'Amount', 
                'Description', 'Source', 'Balance Impact'
            ])
            
            # Data rows
            for txn in transactions:
                date_obj = datetime.fromisoformat(txn.get('date', ''))
                balance_impact = txn['amount'] if txn['type'] == 'income' else -txn['amount']
                
                writer.writerow([
                    date_obj.strftime('%Y-%m-%d'),
                    date_obj.strftime('%H:%M'),
                    txn.get('type', '').title(),
                    txn.get('category', '').replace('_', ' ').title(),
                    txn.get('amount', 0),
                    txn.get('description', ''),
                    txn.get('source', 'Manual'),
                    balance_impact
                ])
        
        return str(filepath)
    
    def export_monthly_summary_csv(self, user_id: str, months: int = 6) -> str:
        """Export monthly summaries to CSV"""
        
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monthly_summary_{user_id}_{date_str}.csv"
        filepath = self.exports_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Month', 'Total Income', 'Total Expense', 'Savings',
                'Savings Rate %', 'Top Expense Category', 'Top Category Amount'
            ])
            
            today = datetime.now()
            
            for i in range(months):
                target = today - timedelta(days=30 * i)
                month_str = target.strftime("%Y-%m")
                month_name = target.strftime("%B %Y")
                
                summary = transaction_repo.get_monthly_summary(user_id, month_str)
                breakdown = analytics_service.get_category_breakdown(user_id, month_str)
                
                top_cat = breakdown['categories'][0] if breakdown['categories'] else {}
                
                income = summary.get('total_income', 0)
                expense = summary.get('total_expense', 0)
                savings = income - expense
                rate = round(savings / max(income, 1) * 100, 1)
                
                writer.writerow([
                    month_name,
                    income,
                    expense,
                    savings,
                    rate,
                    top_cat.get('name', 'N/A'),
                    top_cat.get('amount', 0)
                ])
        
        return str(filepath)
    
    def export_category_breakdown_csv(self, user_id: str, month: str = None) -> str:
        """Export category breakdown to CSV"""
        
        breakdown = analytics_service.get_category_breakdown(user_id, month)
        
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"category_breakdown_{user_id}_{date_str}.csv"
        filepath = self.exports_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Category', 'Amount', 'Percentage'])
            
            for cat in breakdown.get('categories', []):
                writer.writerow([
                    cat['name'],
                    cat['amount'],
                    f"{cat['percentage']}%"
                ])
            
            # Total
            writer.writerow(['TOTAL', breakdown.get('total', 0), '100%'])
        
        return str(filepath)
    
    def export_to_excel(self, user_id: str, months: int = 3) -> Optional[str]:
        """Export comprehensive data to Excel with multiple sheets"""
        
        if not PANDAS_AVAILABLE:
            return None
        
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vittasaathi_export_{user_id}_{date_str}.xlsx"
        filepath = self.exports_dir / filename
        
        user = user_repo.get_user(user_id)
        user_name = user.get('name', 'User') if user else 'User'
        
        with pd.ExcelWriter(filepath, engine='openpyxl' if EXCEL_AVAILABLE else 'xlsxwriter') as writer:
            
            # Sheet 1: Summary
            summary_data = []
            today = datetime.now()
            
            for i in range(months):
                target = today - timedelta(days=30 * i)
                month_str = target.strftime("%Y-%m")
                month_name = target.strftime("%B %Y")
                
                summary = transaction_repo.get_monthly_summary(user_id, month_str)
                
                summary_data.append({
                    'Month': month_name,
                    'Income': summary.get('total_income', 0),
                    'Expense': summary.get('total_expense', 0),
                    'Savings': summary.get('net_savings', 0),
                    'Savings Rate': f"{summary.get('savings_rate', 0)}%"
                })
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Monthly Summary', index=False)
            
            # Sheet 2: All Transactions
            transactions = transaction_repo.get_transactions(user_id)
            if transactions:
                txn_data = []
                for txn in transactions:
                    date_obj = datetime.fromisoformat(txn.get('date', ''))
                    txn_data.append({
                        'Date': date_obj.strftime('%Y-%m-%d'),
                        'Time': date_obj.strftime('%H:%M'),
                        'Type': txn.get('type', '').title(),
                        'Category': txn.get('category', '').replace('_', ' ').title(),
                        'Amount': txn.get('amount', 0),
                        'Description': txn.get('description', ''),
                        'Source': txn.get('source', 'Manual')
                    })
                
                df_txn = pd.DataFrame(txn_data)
                df_txn.to_excel(writer, sheet_name='Transactions', index=False)
            
            # Sheet 3: Category Breakdown
            breakdown = analytics_service.get_category_breakdown(user_id)
            if breakdown.get('categories'):
                cat_data = [
                    {
                        'Category': c['name'],
                        'Icon': c['icon'],
                        'Amount': c['amount'],
                        'Percentage': f"{c['percentage']}%"
                    }
                    for c in breakdown['categories']
                ]
                df_cat = pd.DataFrame(cat_data)
                df_cat.to_excel(writer, sheet_name='Categories', index=False)
            
            # Sheet 4: User Profile
            if user:
                profile_data = {
                    'Field': ['Name', 'Language', 'User Type', 'Monthly Income', 
                             'Current Savings', 'Current Debt', 'Dependents'],
                    'Value': [
                        user.get('name', ''),
                        user.get('language', 'en'),
                        user.get('user_type', ''),
                        user.get('monthly_income_estimate', 0),
                        user.get('current_savings', 0),
                        user.get('current_debt', 0),
                        user.get('dependents', 0)
                    ]
                }
                df_profile = pd.DataFrame(profile_data)
                df_profile.to_excel(writer, sheet_name='Profile', index=False)
        
        return str(filepath)
    
    def export_to_csv_string(self, user_id: str, data_type: str = "transactions") -> str:
        """Export data to CSV string (for API response)"""
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        if data_type == "transactions":
            transactions = transaction_repo.get_transactions(user_id)
            
            writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Description'])
            
            for txn in transactions:
                date_obj = datetime.fromisoformat(txn.get('date', ''))
                writer.writerow([
                    date_obj.strftime('%Y-%m-%d'),
                    txn.get('type', ''),
                    txn.get('category', ''),
                    txn.get('amount', 0),
                    txn.get('description', '')
                ])
        
        elif data_type == "summary":
            trends = analytics_service.get_expense_trends(user_id, 6)
            
            writer.writerow(['Month', 'Income', 'Expense', 'Savings'])
            
            for i, month in enumerate(trends.get('months', [])):
                writer.writerow([
                    month,
                    trends['total_income'][i],
                    trends['total_expense'][i],
                    trends['savings'][i]
                ])
        
        return output.getvalue()
    
    def get_export_formats(self) -> List[Dict]:
        """Get available export formats"""
        
        formats = [
            {
                "format": "csv",
                "name": "CSV (Comma Separated)",
                "description": "Works with Excel, Google Sheets",
                "available": True
            },
            {
                "format": "xlsx",
                "name": "Excel Workbook",
                "description": "Multiple sheets, formatted",
                "available": PANDAS_AVAILABLE
            }
        ]
        
        return formats


# Global instance
export_service = ExportService()
