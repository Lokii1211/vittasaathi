"""
Analytics & Trends Service
==========================
Advanced analytics, trends, patterns, and predictions
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict
import sys

sys.path.append(str(Path(__file__).parent.parent))

from database.user_repository import user_repo
from database.transaction_repository import transaction_repo
from config import EXPENSE_CATEGORIES, INCOME_CATEGORIES


class AnalyticsService:
    """Advanced analytics and trend analysis"""
    
    def __init__(self):
        pass
    
    def get_expense_trends(self, user_id: str, months: int = 6) -> Dict:
        """Get expense trends over multiple months"""
        
        trends = {
            "months": [],
            "total_expense": [],
            "total_income": [],
            "savings": [],
            "by_category": defaultdict(list)
        }
        
        today = datetime.now()
        
        for i in range(months - 1, -1, -1):
            # Calculate month
            target_date = today - timedelta(days=30 * i)
            month_str = target_date.strftime("%Y-%m")
            month_name = target_date.strftime("%b")
            
            # Get summary for that month
            summary = transaction_repo.get_monthly_summary(user_id, month_str)
            
            trends["months"].append(month_name)
            trends["total_expense"].append(summary.get("total_expense", 0))
            trends["total_income"].append(summary.get("total_income", 0))
            trends["savings"].append(summary.get("net_savings", 0))
            
            # Category breakdown
            expenses = transaction_repo.get_expense_by_category(user_id, month_str)
            for cat in ["food", "transport", "rent", "utilities", "entertainment", "shopping"]:
                trends["by_category"][cat].append(expenses.get(cat, 0))
        
        # Calculate trend direction
        if len(trends["total_expense"]) >= 2:
            last = trends["total_expense"][-1]
            prev = trends["total_expense"][-2]
            if last > prev:
                trends["expense_trend"] = "increasing"
                trends["expense_change"] = int((last - prev) / max(prev, 1) * 100)
            elif last < prev:
                trends["expense_trend"] = "decreasing"
                trends["expense_change"] = int((prev - last) / max(prev, 1) * 100)
            else:
                trends["expense_trend"] = "stable"
                trends["expense_change"] = 0
        
        return trends
    
    def get_text_chart(self, data: List[int], labels: List[str], width: int = 20) -> str:
        """Generate text-based bar chart"""
        
        if not data:
            return "No data available"
        
        max_val = max(data) if max(data) > 0 else 1
        chart = ""
        
        for label, value in zip(labels, data):
            bar_length = int(value / max_val * width)
            bar = "█" * bar_length + "░" * (width - bar_length)
            chart += f"{label:>4} |{bar}| ₹{value:,}\n"
        
        return chart
    
    def get_category_breakdown(self, user_id: str, month: str = None) -> Dict:
        """Get detailed category breakdown with percentages"""
        
        expenses = transaction_repo.get_expense_by_category(user_id, month)
        total = sum(expenses.values())
        
        if total == 0:
            return {"categories": [], "total": 0}
        
        breakdown = []
        for cat, amount in sorted(expenses.items(), key=lambda x: x[1], reverse=True):
            cat_info = EXPENSE_CATEGORIES.get(cat, {})
            percentage = round(amount / total * 100, 1)
            
            breakdown.append({
                "category": cat,
                "name": cat_info.get("name", cat.title()),
                "icon": cat_info.get("icon", "📦"),
                "amount": amount,
                "percentage": percentage,
                "bar": self._mini_bar(percentage)
            })
        
        return {
            "categories": breakdown[:10],  # Top 10
            "total": total,
            "month": month or datetime.now().strftime("%Y-%m")
        }
    
    def _mini_bar(self, percentage: float, width: int = 10) -> str:
        """Create mini progress bar from percentage"""
        filled = int(percentage / 100 * width)
        return "▓" * filled + "░" * (width - filled)
    
    def get_daily_spending_pattern(self, user_id: str, days: int = 30) -> Dict:
        """Analyze daily spending patterns"""
        
        patterns = {
            "by_day_of_week": defaultdict(list),
            "by_hour": defaultdict(list),
            "daily_amounts": [],
            "dates": []
        }
        
        today = datetime.now()
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            summary = transaction_repo.get_daily_summary(user_id, date)
            
            patterns["daily_amounts"].insert(0, summary.get("expense", 0))
            patterns["dates"].insert(0, (today - timedelta(days=i)).strftime("%d"))
            
            day_name = (today - timedelta(days=i)).strftime("%A")
            patterns["by_day_of_week"][day_name].append(summary.get("expense", 0))
        
        # Average by day of week
        avg_by_day = {}
        for day, amounts in patterns["by_day_of_week"].items():
            avg_by_day[day] = sum(amounts) / len(amounts) if amounts else 0
        
        patterns["average_by_day"] = avg_by_day
        
        # Find high spending days
        if avg_by_day:
            max_day = max(avg_by_day, key=avg_by_day.get)
            min_day = min(avg_by_day, key=avg_by_day.get)
            patterns["high_spend_day"] = max_day
            patterns["low_spend_day"] = min_day
        
        return patterns
    
    def predict_month_end(self, user_id: str) -> Dict:
        """Predict month-end financial position"""
        
        today = datetime.now()
        day_of_month = today.day
        days_in_month = 30  # Approximate
        days_remaining = days_in_month - day_of_month
        
        # Current month data
        current_summary = transaction_repo.get_monthly_summary(user_id)
        current_income = current_summary.get("total_income", 0)
        current_expense = current_summary.get("total_expense", 0)
        
        # Daily averages
        daily_income = current_income / max(day_of_month, 1)
        daily_expense = current_expense / max(day_of_month, 1)
        
        # Projections
        projected_income = current_income + (daily_income * days_remaining)
        projected_expense = current_expense + (daily_expense * days_remaining)
        projected_savings = projected_income - projected_expense
        
        # Get user target
        user = user_repo.get_user(user_id)
        target_savings = user.get("monthly_income_estimate", 0) * 0.2 if user else 0
        
        on_track = projected_savings >= target_savings
        
        # Recommendation
        if projected_savings < 0:
            recommendation = f"⚠️ You may overspend by ₹{abs(int(projected_savings)):,}. Reduce daily expense to ₹{int(current_income / days_in_month):,}"
        elif projected_savings < target_savings:
            gap = target_savings - projected_savings
            daily_reduction = gap / max(days_remaining, 1)
            recommendation = f"💡 Save ₹{int(daily_reduction):,} more per day to hit target"
        else:
            recommendation = "✅ You're on track! Keep it up!"
        
        return {
            "current_day": day_of_month,
            "days_remaining": days_remaining,
            "current_income": int(current_income),
            "current_expense": int(current_expense),
            "current_savings": int(current_income - current_expense),
            "projected_income": int(projected_income),
            "projected_expense": int(projected_expense),
            "projected_savings": int(projected_savings),
            "target_savings": int(target_savings),
            "on_track": on_track,
            "recommendation": recommendation
        }
    
    def detect_recurring_expenses(self, user_id: str) -> List[Dict]:
        """Detect recurring/subscription expenses"""
        
        # Get transactions from last 3 months
        recurring = []
        seen_patterns = defaultdict(list)
        
        today = datetime.now()
        
        for month_offset in range(3):
            target = today - timedelta(days=30 * month_offset)
            month_str = target.strftime("%Y-%m")
            transactions = transaction_repo.get_transactions(
                user_id, 
                transaction_type="expense",
                month=month_str
            )
            
            for txn in transactions:
                key = (txn.get("category"), txn.get("amount"))
                seen_patterns[key].append(txn.get("date"))
        
        # Find patterns that appear in multiple months
        for (category, amount), dates in seen_patterns.items():
            if len(dates) >= 2:
                cat_info = EXPENSE_CATEGORIES.get(category, {})
                recurring.append({
                    "category": category,
                    "name": cat_info.get("name", category.title()),
                    "icon": cat_info.get("icon", "📦"),
                    "amount": amount,
                    "frequency": "monthly" if len(dates) >= 2 else "occasional",
                    "occurrences": len(dates)
                })
        
        # Sort by amount
        recurring.sort(key=lambda x: x["amount"], reverse=True)
        
        return recurring[:10]
    
    def get_income_sources_analysis(self, user_id: str, months: int = 3) -> Dict:
        """Analyze income sources and reliability"""
        
        sources = defaultdict(list)
        
        today = datetime.now()
        
        for month_offset in range(months):
            target = today - timedelta(days=30 * month_offset)
            month_str = target.strftime("%Y-%m")
            transactions = transaction_repo.get_transactions(
                user_id,
                transaction_type="income",
                month=month_str
            )
            
            for txn in transactions:
                cat = txn.get("category", "other_income")
                sources[cat].append(txn.get("amount", 0))
        
        analysis = []
        for cat, amounts in sources.items():
            cat_info = INCOME_CATEGORIES.get(cat, {})
            total = sum(amounts)
            avg = total / months
            
            # Calculate reliability (consistency)
            if len(amounts) >= 2:
                import statistics
                try:
                    std = statistics.stdev(amounts)
                    reliability = max(0, 100 - int(std / max(avg, 1) * 100))
                except:
                    reliability = 50
            else:
                reliability = 50
            
            analysis.append({
                "category": cat,
                "name": cat_info.get("name", cat.title()),
                "icon": cat_info.get("icon", "💰"),
                "total_3_months": total,
                "monthly_average": int(avg),
                "reliability": reliability,
                "occurrences": len(amounts)
            })
        
        analysis.sort(key=lambda x: x["total_3_months"], reverse=True)
        
        return {
            "sources": analysis,
            "total_income_3_months": sum(s["total_3_months"] for s in analysis),
            "primary_source": analysis[0] if analysis else None
        }
    
    def get_savings_health(self, user_id: str) -> Dict:
        """Comprehensive savings health analysis"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        
        current_savings = user.get("current_savings", 0)
        monthly_income = user.get("monthly_income_estimate", 0)
        monthly_expense = self._get_avg_monthly_expense(user_id)
        
        # Emergency fund status
        required_emergency = monthly_expense * 6
        emergency_months = current_savings / max(monthly_expense, 1)
        emergency_status = min(100, int(emergency_months / 6 * 100))
        
        # Savings rate
        summary = transaction_repo.get_monthly_summary(user_id)
        actual_savings = summary.get("net_savings", 0)
        savings_rate = actual_savings / max(summary.get("total_income", 1), 1) * 100
        
        # Grade
        if savings_rate >= 30:
            grade = "A+"
            message = "Excellent saver!"
        elif savings_rate >= 20:
            grade = "A"
            message = "Great savings habit!"
        elif savings_rate >= 10:
            grade = "B"
            message = "Good, can do better"
        elif savings_rate > 0:
            grade = "C"
            message = "Needs improvement"
        else:
            grade = "D"
            message = "Spending more than earning"
        
        return {
            "current_savings": current_savings,
            "emergency_fund_required": int(required_emergency),
            "emergency_months_covered": round(emergency_months, 1),
            "emergency_status_percent": emergency_status,
            "this_month_savings": int(actual_savings),
            "savings_rate": round(savings_rate, 1),
            "grade": grade,
            "message": message,
            "tips": self._get_savings_tips(savings_rate, emergency_status)
        }
    
    def _get_avg_monthly_expense(self, user_id: str) -> int:
        summary = transaction_repo.get_monthly_summary(user_id)
        return summary.get("total_expense", 15000)
    
    def _get_savings_tips(self, savings_rate: float, emergency_status: int) -> List[str]:
        tips = []
        
        if emergency_status < 100:
            tips.append(f"🎯 Build emergency fund first - you're at {emergency_status}%")
        
        if savings_rate < 10:
            tips.append("💡 Try the 'Pay Yourself First' method - save before spending")
            tips.append("📉 Track small expenses - they add up!")
        elif savings_rate < 20:
            tips.append("📈 Increase savings by 2% each month")
            tips.append("🎯 Set specific savings goals")
        else:
            tips.append("🌟 Consider investing your surplus savings")
            tips.append("📊 Diversify into SIPs and FDs")
        
        return tips[:3]


class ReportGenerator:
    """Generate exportable reports"""
    
    def __init__(self):
        self.analytics = AnalyticsService()
    
    def generate_text_report(self, user_id: str, month: str = None) -> str:
        """Generate comprehensive text report"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return "User not found"
        
        month = month or datetime.now().strftime("%Y-%m")
        month_name = datetime.strptime(month, "%Y-%m").strftime("%B %Y")
        
        name = user.get("name", "User")
        
        # Get all data
        summary = transaction_repo.get_monthly_summary(user_id, month)
        breakdown = self.analytics.get_category_breakdown(user_id, month)
        trends = self.analytics.get_expense_trends(user_id, 3)
        savings_health = self.analytics.get_savings_health(user_id)
        prediction = self.analytics.predict_month_end(user_id)
        recurring = self.analytics.detect_recurring_expenses(user_id)
        
        # Build report
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║             💰 VittaSaathi Financial Report                  ║
║                    {month_name:^20}                    ║
╚══════════════════════════════════════════════════════════════╝

👤 *{name}*
📅 Report Generated: {datetime.now().strftime("%d %b %Y, %I:%M %p")}

═══════════════════════════════════════════════════════════════
                        📊 SUMMARY
═══════════════════════════════════════════════════════════════

💰 Total Income     : ₹{summary.get('total_income', 0):,}
💸 Total Expenses   : ₹{summary.get('total_expense', 0):,}
💾 Net Savings      : ₹{summary.get('net_savings', 0):,}
📊 Savings Rate     : {savings_health.get('savings_rate', 0)}%
🏆 Grade            : {savings_health.get('grade', 'N/A')}

═══════════════════════════════════════════════════════════════
                    📈 EXPENSE BREAKDOWN
═══════════════════════════════════════════════════════════════
"""
        
        for cat in breakdown.get("categories", [])[:8]:
            report += f"\n{cat['icon']} {cat['name']:<15} {cat['bar']} ₹{cat['amount']:>8,} ({cat['percentage']}%)"
        
        report += f"""

═══════════════════════════════════════════════════════════════
                    📈 3-MONTH TREND
═══════════════════════════════════════════════════════════════

"""
        
        # Trend chart
        report += self.analytics.get_text_chart(
            trends.get("total_expense", []),
            trends.get("months", [])
        )
        
        report += f"""
Expense Trend: {trends.get('expense_trend', 'N/A').upper()} ({trends.get('expense_change', 0)}%)

═══════════════════════════════════════════════════════════════
                    🔄 RECURRING EXPENSES
═══════════════════════════════════════════════════════════════
"""
        
        for rec in recurring[:5]:
            report += f"\n{rec['icon']} {rec['name']:<15} ₹{rec['amount']:,}/month"
        
        total_recurring = sum(r['amount'] for r in recurring)
        report += f"\n\n📊 Total Recurring: ₹{total_recurring:,}/month"
        
        report += f"""

═══════════════════════════════════════════════════════════════
                    🎯 MONTH-END PROJECTION
═══════════════════════════════════════════════════════════════

📅 Days Remaining    : {prediction.get('days_remaining', 0)}
📈 Projected Income  : ₹{prediction.get('projected_income', 0):,}
📉 Projected Expense : ₹{prediction.get('projected_expense', 0):,}
💾 Projected Savings : ₹{prediction.get('projected_savings', 0):,}

{prediction.get('recommendation', '')}

═══════════════════════════════════════════════════════════════
                    🏥 SAVINGS HEALTH
═══════════════════════════════════════════════════════════════

🆘 Emergency Fund Required : ₹{savings_health.get('emergency_fund_required', 0):,}
📊 Current Coverage        : {savings_health.get('emergency_months_covered', 0)} months
🎯 Status                  : {savings_health.get('emergency_status_percent', 0)}% complete

💡 Tips:
"""
        
        for tip in savings_health.get('tips', []):
            report += f"\n   • {tip}"
        
        report += f"""

═══════════════════════════════════════════════════════════════
                    📝 RECOMMENDATIONS
═══════════════════════════════════════════════════════════════

"""
        
        # Generate recommendations
        recommendations = self._generate_recommendations(user_id, summary, savings_health)
        for i, rec in enumerate(recommendations[:5], 1):
            report += f"{i}. {rec}\n"
        
        report += """
═══════════════════════════════════════════════════════════════

        Thank you for using VittaSaathi! 🙏
        "हर रुपया मायने रखता है"

═══════════════════════════════════════════════════════════════
"""
        
        return report
    
    def _generate_recommendations(self, user_id: str, summary: Dict, savings: Dict) -> List[str]:
        recommendations = []
        
        savings_rate = savings.get("savings_rate", 0)
        emergency_status = savings.get("emergency_status_percent", 0)
        
        if emergency_status < 50:
            recommendations.append("🆘 Priority: Build your emergency fund to 3 months of expenses")
        
        if savings_rate < 10:
            recommendations.append("💰 Increase savings to at least 10% of income")
        
        # High expense categories
        breakdown = self.analytics.get_category_breakdown(user_id)
        for cat in breakdown.get("categories", [])[:3]:
            if cat["percentage"] > 30:
                recommendations.append(f"📉 Reduce {cat['name'].lower()} spending - currently {cat['percentage']}% of expenses")
        
        if savings_rate >= 20:
            recommendations.append("📈 Start SIP with ₹500/month in index fund")
        
        recommendations.append("📱 Keep tracking all expenses daily")
        
        return recommendations
    
    def generate_shareable_summary(self, user_id: str) -> str:
        """Generate short shareable summary for WhatsApp"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return "User not found"
        
        name = user.get("name", "User")
        summary = transaction_repo.get_monthly_summary(user_id)
        savings_health = self.analytics.get_savings_health(user_id)
        
        month_name = datetime.now().strftime("%B")
        
        card = f"""
📊 *{name}'s {month_name} Summary*
━━━━━━━━━━━━━━━━━━

💰 Income: ₹{summary.get('total_income', 0):,}
💸 Expense: ₹{summary.get('total_expense', 0):,}
💾 Saved: ₹{summary.get('net_savings', 0):,}

🏆 Grade: *{savings_health.get('grade', 'N/A')}*
📊 Savings: {savings_health.get('savings_rate', 0)}%

_Tracked with VittaSaathi_ 📱
"""
        
        return card


# Global instances
analytics_service = AnalyticsService()
report_generator = ReportGenerator()
