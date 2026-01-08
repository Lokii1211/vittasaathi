"""
Financial Advisor Service
=========================
Core financial advice engine with personalized recommendations
based on user's income patterns, goals, and current market trends
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import statistics
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import (
    FINANCIAL_CONSTANTS, INVESTMENT_OPTIONS, GOAL_TYPES
)

# Extract constants
EMERGENCY_FUND_MONTHS = FINANCIAL_CONSTANTS.get("emergency_fund_months", 6)
SAFE_EMI_PERCENTAGE = FINANCIAL_CONSTANTS.get("safe_emi_percent", 30) / 100
MINIMUM_SAVINGS_PERCENTAGE = FINANCIAL_CONSTANTS.get("min_savings_percent", 10) / 100

from database.user_repository import user_repo
from database.transaction_repository import transaction_repo
from database.goal_repository import goal_repo
from database.budget_repository import budget_repo


class FinancialAdvisor:
    """AI-powered financial advisor for irregular income earners"""
    
    def __init__(self):
        pass
    
    def get_financial_health_score(self, user_id: str) -> Dict:
        """Calculate overall financial health score (0-100)"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return {"score": 0, "message": "User not found"}
        
        scores = {}
        
        # 1. Emergency Fund Score (25 points)
        monthly_expense = self._get_average_monthly_expense(user_id)
        required_emergency = monthly_expense * EMERGENCY_FUND_MONTHS
        current_emergency = user.get("emergency_fund", 0)
        emergency_ratio = min(current_emergency / max(required_emergency, 1), 1)
        scores["emergency_fund"] = {
            "score": round(emergency_ratio * 25),
            "max": 25,
            "status": "✅" if emergency_ratio >= 1 else "⚠️" if emergency_ratio >= 0.5 else "🔴"
        }
        
        # 2. Debt Management Score (25 points)
        current_debt = user.get("current_debt", 0)
        monthly_income = user.get("monthly_income_estimate", 0)
        if current_debt == 0:
            debt_score = 25
        else:
            debt_to_income = current_debt / max(monthly_income * 12, 1)
            debt_score = max(0, 25 - int(debt_to_income * 25))
        scores["debt_management"] = {
            "score": debt_score,
            "max": 25,
            "status": "✅" if debt_score >= 20 else "⚠️" if debt_score >= 10 else "🔴"
        }
        
        # 3. Savings Rate Score (25 points)
        summary = transaction_repo.get_monthly_summary(user_id)
        savings_rate = summary.get("savings_rate", 0)
        savings_score = min(25, int(savings_rate / 4))  # 100% savings = 25 points
        scores["savings_rate"] = {
            "score": savings_score,
            "max": 25,
            "status": "✅" if savings_rate >= 20 else "⚠️" if savings_rate >= 10 else "🔴"
        }
        
        # 4. Income Stability Score (25 points)
        stability = self._calculate_income_stability(user_id)
        stability_score = int(stability.get("stability_score", 0) / 4)
        scores["income_stability"] = {
            "score": stability_score,
            "max": 25,
            "status": "✅" if stability_score >= 17 else "⚠️" if stability_score >= 10 else "🔴"
        }
        
        total_score = sum(s["score"] for s in scores.values())
        
        # Overall health category
        if total_score >= 80:
            health = {"grade": "A", "emoji": "🌟", "message": "Excellent financial health!"}
        elif total_score >= 60:
            health = {"grade": "B", "emoji": "✅", "message": "Good financial health"}
        elif total_score >= 40:
            health = {"grade": "C", "emoji": "⚠️", "message": "Needs improvement"}
        else:
            health = {"grade": "D", "emoji": "🔴", "message": "Needs urgent attention"}
        
        return {
            "total_score": total_score,
            "max_score": 100,
            "health": health,
            "breakdown": scores,
            "generated_at": datetime.now().isoformat()
        }
    
    def get_personalized_advice(self, user_id: str) -> List[Dict]:
        """Generate personalized financial advice"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return []
        
        advice_list = []
        priority = 1
        
        # Get financial data
        health = self.get_financial_health_score(user_id)
        monthly_income = user.get("monthly_income_estimate", 0)
        monthly_expense = self._get_average_monthly_expense(user_id)
        current_savings = user.get("current_savings", 0)
        current_debt = user.get("current_debt", 0)
        goals = user.get("goals", [])
        
        # PRIORITY 1: Emergency Fund
        required_emergency = monthly_expense * EMERGENCY_FUND_MONTHS
        if current_savings < required_emergency:
            gap = required_emergency - current_savings
            advice_list.append({
                "priority": priority,
                "category": "Emergency Fund",
                "icon": "🏥",
                "title": "Build Emergency Fund",
                "advice": f"You need ₹{gap:,} more for a {EMERGENCY_FUND_MONTHS}-month emergency fund.",
                "action": f"Save ₹{int(gap/6):,} per month for the next 6 months.",
                "impact": "HIGH"
            })
            priority += 1
        
        # PRIORITY 2: Debt Reduction
        if current_debt > 0:
            debt_months = current_debt / max(monthly_income * 0.3, 1)
            advice_list.append({
                "priority": priority,
                "category": "Debt Management",
                "icon": "💳",
                "title": "Pay Off Debt First",
                "advice": f"Your debt of ₹{current_debt:,} should be your priority.",
                "action": f"Pay ₹{int(current_debt/debt_months):,}/month to clear in {int(debt_months)} months.",
                "impact": "HIGH"
            })
            priority += 1
        
        # PRIORITY 3: Savings Rate Improvement
        savings_rate = health["breakdown"]["savings_rate"]["score"] * 4  # Convert back to %
        if savings_rate < 20:
            target_savings = int(monthly_income * 0.2)
            current_savings_monthly = int(monthly_income * savings_rate / 100)
            gap = target_savings - current_savings_monthly
            
            advice_list.append({
                "priority": priority,
                "category": "Savings",
                "icon": "💰",
                "title": "Increase Savings Rate",
                "advice": f"Try to save 20% of income (₹{target_savings:,}/month).",
                "action": f"Find ways to save ₹{gap:,} more each month.",
                "impact": "MEDIUM"
            })
            priority += 1
        
        # PRIORITY 4: Investment Advice
        if current_savings >= required_emergency * 0.5 and current_debt == 0:
            investment_advice = self.get_investment_recommendations(user_id)
            advice_list.append({
                "priority": priority,
                "category": "Investment",
                "icon": "📈",
                "title": "Start Investing",
                "advice": investment_advice["summary"],
                "action": investment_advice["recommended_action"],
                "impact": "MEDIUM"
            })
            priority += 1
        
        # PRIORITY 5: Expense Optimization
        spending_patterns = transaction_repo.get_spending_patterns(user_id)
        if spending_patterns.get("warnings"):
            for warning in spending_patterns["warnings"][:2]:  # Top 2 warnings
                advice_list.append({
                    "priority": priority,
                    "category": "Expenses",
                    "icon": "📊",
                    "title": "Spending Alert",
                    "advice": warning,
                    "action": "Review this category and find ways to reduce.",
                    "impact": "LOW"
                })
                priority += 1
        
        # PRIORITY 6: Goal Progress
        goal_summary = goal_repo.get_goal_summary(user_id)
        if goal_summary.get("active_goals", 0) > 0:
            milestone = goal_repo.get_next_milestone(user_id)
            if milestone:
                advice_list.append({
                    "priority": priority,
                    "category": "Goals",
                    "icon": milestone["icon"],
                    "title": "Goal Progress",
                    "advice": milestone["message"],
                    "action": f"You're {milestone['progress']}% there!",
                    "impact": "MEDIUM"
                })
        
        return advice_list
    
    def get_investment_recommendations(self, user_id: str) -> Dict:
        """Get personalized investment recommendations"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        
        monthly_income = user.get("monthly_income_estimate", 0)
        income_type = user.get("income_type", "irregular")
        stability = self._calculate_income_stability(user_id)
        stability_score = stability.get("stability_score", 50)
        
        # Determine investable amount (after expenses and savings)
        monthly_expense = self._get_average_monthly_expense(user_id)
        monthly_savings_target = monthly_income * MINIMUM_SAVINGS_PERCENTAGE
        investable = max(0, monthly_income - monthly_expense - monthly_savings_target)
        
        # Adjust based on income stability
        if income_type == "irregular":
            # For irregular income, be more conservative
            safe_investment = investable * 0.5  # Only invest 50% of investable
        else:
            safe_investment = investable * 0.7
        
        # Determine risk profile
        if stability_score >= 70:
            risk_profile = "moderate"
            allocation = {"safe": 20, "moderate": 40, "growth": 40}
        elif stability_score >= 40:
            risk_profile = "conservative"
            allocation = {"safe": 40, "moderate": 40, "growth": 20}
        else:
            risk_profile = "very_conservative"
            allocation = {"safe": 60, "moderate": 30, "growth": 10}
        
        # Build recommendations
        recommendations = []
        
        for category, percentage in allocation.items():
            if percentage > 0:
                amount = int(safe_investment * percentage / 100)
                options = INVESTMENT_OPTIONS.get(category, [])
                
                if amount >= 500:  # Minimum SIP amount
                    for option in options[:2]:  # Top 2 options per category
                        recommendations.append({
                            "name": option["name"],
                            "amount": amount,
                            "return_range": option["return_range"],
                            "risk": option["risk"],
                            "category": category
                        })
        
        # SIP recommendation
        if safe_investment >= 500:
            sip_amount = (safe_investment // 500) * 500  # Round to nearest 500
        else:
            sip_amount = 500  # Minimum SIP
        
        return {
            "risk_profile": risk_profile,
            "investable_amount": int(investable),
            "recommended_investment": int(safe_investment),
            "allocation": allocation,
            "recommendations": recommendations,
            "sip_amount": sip_amount,
            "summary": f"Based on your {income_type} income, invest ₹{int(safe_investment):,}/month",
            "recommended_action": f"Start a SIP of ₹{sip_amount:,} in an index fund"
        }
    
    def get_loan_eligibility(self, user_id: str, requested_amount: int = None) -> Dict:
        """Calculate loan eligibility for irregular income earners"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return {"eligible": False, "reason": "User not found"}
        
        monthly_income = user.get("monthly_income_estimate", 0)
        current_debt = user.get("current_debt", 0)
        stability = self._calculate_income_stability(user_id)
        stability_score = stability.get("stability_score", 0)
        
        # Minimum requirements
        if monthly_income < 10000:
            return {
                "eligible": False,
                "reason": "Minimum income of ₹10,000/month required",
                "suggestion": "Focus on increasing income first"
            }
        
        if stability_score < 30:
            return {
                "eligible": False,
                "reason": "Income too irregular for loan",
                "suggestion": "Build 6 months of consistent income records"
            }
        
        # Calculate safe EMI capacity
        # For irregular income: use 80% of worst month
        income_history = transaction_repo.get_income_history(user_id, 6)
        if income_history:
            worst_month = min(income_history.values())
            safe_base = worst_month * 0.8
        else:
            safe_base = monthly_income * 0.7
        
        # Deduct existing EMI obligations
        available_for_emi = safe_base * SAFE_EMI_PERCENTAGE
        if current_debt > 0:
            estimated_existing_emi = current_debt / 24  # Assume 2-year loan
            available_for_emi -= estimated_existing_emi
        
        available_for_emi = max(0, available_for_emi)
        
        # Calculate max loan amount (assuming 14% interest, 24-month tenure)
        max_loan = self._calculate_loan_from_emi(available_for_emi, 0.14, 24)
        
        # Loan options
        loan_options = []
        for tenure in [12, 24, 36]:
            loan_amount = self._calculate_loan_from_emi(available_for_emi, 0.14, tenure)
            loan_options.append({
                "tenure_months": tenure,
                "max_amount": int(loan_amount),
                "emi": int(available_for_emi),
                "total_payment": int(available_for_emi * tenure),
                "interest_rate": "12-16%"
            })
        
        # Risk assessment
        if stability_score >= 70:
            risk_level = "LOW"
            approval_chance = "HIGH"
        elif stability_score >= 50:
            risk_level = "MEDIUM"
            approval_chance = "MEDIUM"
        else:
            risk_level = "HIGH"
            approval_chance = "LOW"
        
        result = {
            "eligible": available_for_emi >= 1000,
            "max_emi_capacity": int(available_for_emi),
            "max_loan_amount": int(max_loan),
            "risk_level": risk_level,
            "approval_chance": approval_chance,
            "loan_options": loan_options,
            "stability_score": stability_score,
        }
        
        # Check if requested amount is feasible
        if requested_amount:
            feasible = requested_amount <= max_loan
            result["requested_amount"] = requested_amount
            result["request_feasible"] = feasible
            if not feasible:
                result["suggestion"] = f"Maximum loan you can get is ₹{int(max_loan):,}"
        
        return result
    
    def get_budget_recommendation(self, user_id: str) -> Dict:
        """Get personalized budget recommendation"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        
        monthly_income = user.get("monthly_income_estimate", 0)
        dependents = user.get("dependents", 0)
        current_debt = user.get("current_debt", 0)
        
        # Adjust budget based on dependents
        family_factor = 1 + (dependents * 0.1)  # 10% more expenses per dependent
        
        # For irregular income, plan on 80% of estimated income
        safe_income = monthly_income * 0.8
        
        # 50/30/20 Rule adjusted for Indian context
        needs = safe_income * 0.50 * family_factor
        wants = safe_income * 0.20
        savings = safe_income * 0.20
        debt_payment = safe_income * 0.10 if current_debt > 0 else 0
        
        # Adjust if total exceeds income
        total = needs + wants + savings + debt_payment
        if total > safe_income:
            scale = safe_income / total
            needs *= scale
            wants *= scale
            savings *= scale
            debt_payment *= scale
        
        # Category breakdown
        budget = {
            "total_budget": int(safe_income),
            "categories": {
                "rent": int(needs * 0.40),
                "food": int(needs * 0.30),
                "transport": int(needs * 0.15),
                "utilities": int(needs * 0.10),
                "healthcare": int(needs * 0.05),
                "entertainment": int(wants * 0.40),
                "shopping": int(wants * 0.30),
                "personal": int(wants * 0.30),
                "savings": int(savings * 0.50),
                "investment": int(savings * 0.30),
                "emergency_fund": int(savings * 0.20),
            },
            "debt_payment": int(debt_payment),
            "daily_allowance": int(safe_income / 30),
            "tips": [
                "Track every expense, even small ones",
                "Use cash for discretionary spending",
                "Review expenses weekly",
                f"Keep ₹{int(safe_income * 0.1):,} as buffer for unexpected expenses"
            ]
        }
        
        return budget
    
    def get_daily_message(self, user_id: str) -> Dict:
        """Generate personalized daily message/greeting"""
        
        user = user_repo.get_user(user_id)
        if not user:
            return {"message": "Please complete your profile first"}
        
        name = user.get("name", "Friend")
        language = user.get("language", "en")
        
        # Get yesterday's summary
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        yesterday_summary = transaction_repo.get_daily_summary(user_id, yesterday)
        
        # Get today's target
        budget_status = budget_repo.get_budget_status(user_id)
        daily_allowance = budget_status.get("daily_allowance", 0)
        
        # Get streak
        streak = user.get("streak_days", 0)
        
        # Build message based on language
        if language == "hi":
            if yesterday_summary["income"] > 0:
                earning_msg = f"कल आपने ₹{yesterday_summary['income']:,} कमाए! 🎉"
            else:
                earning_msg = "कल कोई आमदनी दर्ज नहीं हुई।"
            
            target_msg = f"आज का खर्च लक्ष्य: ₹{daily_allowance:,}"
            streak_msg = f"🔥 {streak} दिन का स्ट्रीक!" if streak > 1 else ""
            
            message = f"🌅 सुप्रभात {name}!\n\n{earning_msg}\n{target_msg}\n{streak_msg}"
        
        elif language == "ta":
            if yesterday_summary["income"] > 0:
                earning_msg = f"நேற்று ₹{yesterday_summary['income']:,} சம்பாதித்தீர்கள்! 🎉"
            else:
                earning_msg = "நேற்று வருமானம் பதிவாகவில்லை."
            
            target_msg = f"இன்றைய செலவு இலக்கு: ₹{daily_allowance:,}"
            streak_msg = f"🔥 {streak} நாள் ஸ்ட்ரீக்!" if streak > 1 else ""
            
            message = f"🌅 காலை வணக்கம் {name}!\n\n{earning_msg}\n{target_msg}\n{streak_msg}"
        
        else:  # English default
            if yesterday_summary["income"] > 0:
                earning_msg = f"Yesterday you earned ₹{yesterday_summary['income']:,}! 🎉"
            else:
                earning_msg = "No income recorded yesterday."
            
            target_msg = f"Today's spending target: ₹{daily_allowance:,}"
            streak_msg = f"🔥 {streak} day streak!" if streak > 1 else ""
            
            message = f"🌅 Good Morning {name}!\n\n{earning_msg}\n{target_msg}\n{streak_msg}"
        
        # Add motivational tip
        goals = user.get("goals", [])
        if goals:
            goal_info = GOAL_TYPES.get(goals[0], {})
            icon = goal_info.get("icon", "🎯")
            message += f"\n\n{icon} Keep saving for your {goals[0].replace('_', ' ')} goal!"
        
        return {
            "message": message,
            "yesterday_summary": yesterday_summary,
            "daily_target": daily_allowance,
            "streak": streak,
        }
    
    def _get_average_monthly_expense(self, user_id: str) -> int:
        """Calculate average monthly expense"""
        
        summary = transaction_repo.get_monthly_summary(user_id)
        if summary.get("total_expense", 0) > 0:
            return summary["total_expense"]
        
        # Fallback: estimate from income
        user = user_repo.get_user(user_id)
        if user:
            return int(user.get("monthly_income_estimate", 0) * 0.7)
        
        return 15000  # Default estimate
    
    def _calculate_income_stability(self, user_id: str) -> Dict:
        """Calculate income stability metrics"""
        
        income_history = transaction_repo.get_income_history(user_id, 6)
        
        if len(income_history) < 2:
            return {
                "stability_score": 50,
                "volatility": 0,
                "remark": "Not enough data"
            }
        
        incomes = list(income_history.values())
        avg_income = statistics.mean(incomes)
        std_dev = statistics.stdev(incomes)
        
        volatility = std_dev / avg_income if avg_income > 0 else 0
        stability_score = max(0, 100 - int(volatility * 100))
        
        if stability_score >= 70:
            remark = "Stable Income"
        elif stability_score >= 40:
            remark = "Moderately Irregular"
        else:
            remark = "Highly Irregular"
        
        return {
            "stability_score": stability_score,
            "average_income": round(avg_income, 2),
            "volatility": round(volatility, 2),
            "remark": remark
        }
    
    def _calculate_loan_from_emi(self, emi: float, annual_rate: float, months: int) -> float:
        """Calculate loan amount from EMI"""
        
        if emi <= 0:
            return 0
        
        r = annual_rate / 12
        loan = emi * ((1 + r) ** months - 1) / (r * (1 + r) ** months)
        return loan


# Global instance
financial_advisor = FinancialAdvisor()
