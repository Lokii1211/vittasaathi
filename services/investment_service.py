"""
Advanced Investment Advisory Service v2.0
==========================================
Provides market insights, portfolio allocation, and investment recommendations.
Designed for WhatsApp-first interaction.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

class AdvancedInvestmentService:
    """
    Production-grade Investment Advisory Service
    Provides personalized investment recommendations based on user profile
    """
    
    def __init__(self):
        self.alpha_vantage_key = os.getenv("ALPHAVANTAGE_API_KEY", "")
        
        # Market moods with probabilities for more realistic simulation
        self.market_states = {
            "bullish": {"emoji": "🐂", "weight": 0.35},
            "bearish": {"emoji": "🐻", "weight": 0.25},
            "neutral": {"emoji": "😐", "weight": 0.25},
            "volatile": {"emoji": "⚡", "weight": 0.15}
        }
        
        # Sector data with trends
        self.sectors = [
            {"name": "Green Energy", "emoji": "🌿", "trend": "High Growth", "risk": "Moderate", "funds": ["Tata Ethix ESG", "ICICI Pru ESG"]},
            {"name": "Banking (PSU)", "emoji": "🏦", "trend": "Stable Recovery", "risk": "Low", "funds": ["SBI PSU Fund", "ICICI Banking"]},
            {"name": "IT & Tech", "emoji": "💻", "trend": "Mixed", "risk": "Moderate", "funds": ["ICICI Tech Fund", "Kotak Digital"]},
            {"name": "Defence & Manufacturing", "emoji": "🛡️", "trend": "Government Push", "risk": "High", "funds": ["Defence Funds", "Cap Goods ETF"]},
            {"name": "FMCG", "emoji": "🛒", "trend": "Defensive Play", "risk": "Low", "funds": ["HDFC Consumption", "ICICI FMCG"]},
            {"name": "Pharma & Healthcare", "emoji": "💊", "trend": "Steady Growth", "risk": "Moderate", "funds": ["SBI Healthcare", "Nippon Pharma"]},
            {"name": "Real Estate", "emoji": "🏠", "trend": "Recovering", "risk": "High", "funds": ["REITs", "Embassy REIT"]},
            {"name": "Electric Vehicles", "emoji": "🚗", "trend": "Future Focused", "risk": "Very High", "funds": ["Mirae EV", "Tata Motors Stock"]}
        ]
        
        # Investment instruments for different risk profiles
        self.instruments = {
            "conservative": [
                {"name": "Fixed Deposit", "return": "7-7.5%", "lock": "1-5 years", "risk": "Lowest"},
                {"name": "PPF", "return": "7.1%", "lock": "15 years", "risk": "None"},
                {"name": "Debt Mutual Funds", "return": "6-8%", "lock": "None", "risk": "Low"},
                {"name": "Sovereign Gold Bonds", "return": "2.5% + Gold", "lock": "8 years", "risk": "Low"}
            ],
            "moderate": [
                {"name": "Balanced Funds", "return": "10-12%", "lock": "None", "risk": "Medium"},
                {"name": "Index Funds (Nifty 50)", "return": "12-14%", "lock": "None", "risk": "Medium"},
                {"name": "Large Cap Equity", "return": "12-15%", "lock": "None", "risk": "Medium"},
                {"name": "Corporate Bonds", "return": "8-10%", "lock": "1-3 years", "risk": "Medium-Low"}
            ],
            "aggressive": [
                {"name": "Mid Cap Funds", "return": "15-18%", "lock": "None", "risk": "High"},
                {"name": "Small Cap Funds", "return": "18-25%", "lock": "None", "risk": "Very High"},
                {"name": "Sector Specific", "return": "Variable", "lock": "None", "risk": "Very High"},
                {"name": "Direct Stocks", "return": "Variable", "lock": "None", "risk": "Very High"}
            ]
        }
        
        # Daily tips pool
        self.daily_tips = [
            "Start with index funds if you're new to investing",
            "Never invest money you might need in 1-2 years in stocks",
            "Diversification reduces risk - don't put all eggs in one basket",
            "SIP helps average out market volatility",
            "Review and rebalance your portfolio quarterly",
            "Keep 6 months expenses as emergency fund before investing",
            "Tax saving doesn't mean best investment - compare returns",
            "Gold should be 5-10% of your portfolio as hedge",
            "Avoid timing the market - time IN the market matters more",
            "Read about a fund's portfolio before investing"
        ]
    
    def get_market_analysis(self) -> str:
        """Generate comprehensive market analysis for WhatsApp"""
        
        # Simulate market state
        mood = self._get_market_mood()
        top_sectors = random.sample(self.sectors, 3)
        
        # Build response
        response = f"""📈 *Daily Market Intelligence*
━━━━━━━━━━━━━━━━━━━━

🎯 *Market Mood:* {mood['name']} {mood['emoji']}

📊 *Today's Hot Sectors:*
"""
        for i, sector in enumerate(top_sectors, 1):
            response += f"{i}. {sector['emoji']} *{sector['name']}*\n"
            response += f"   Trend: {sector['trend']} | Risk: {sector['risk']}\n"
        
        response += f"""
💡 *Strategy for Today:*
{self._get_strategy_for_mood(mood['name'])}

📌 *Quick Tip:*
{random.choice(self.daily_tips)}

━━━━━━━━━━━━━━━━━━━━
*Commands:*
• "Invest 10000" - Get personalized plan
• "Safe investment" - Low risk options
• "High returns" - Growth options

⚠️ *Disclaimer:* This is for educational purposes only. Consult a financial advisor before investing."""
        
        return response
    
    def get_portfolio_plan(self, amount: float, age: int = 30, risk_profile: str = "moderate") -> str:
        """Generate personalized portfolio allocation"""
        
        # Calculate allocation based on Rule of 100 (modified)
        equity_pct = min(80, max(20, 100 - age))
        debt_pct = 100 - equity_pct - 10  # Reserve 10% for gold
        gold_pct = 10
        
        # Adjust for risk profile
        if risk_profile == "conservative":
            equity_pct = max(20, equity_pct - 15)
            debt_pct = min(70, debt_pct + 15)
        elif risk_profile == "aggressive":
            equity_pct = min(85, equity_pct + 10)
            debt_pct = max(5, debt_pct - 10)
        
        # Calculate amounts
        equity_amt = amount * equity_pct / 100
        debt_amt = amount * debt_pct / 100
        gold_amt = amount * gold_pct / 100
        
        # Get recommended funds
        equity_instruments = self.instruments[risk_profile][:2]
        debt_instruments = self.instruments["conservative"][:2]
        
        response = f"""📊 *Your Personalized Investment Plan*
━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 *Investment Amount:* ₹{amount:,.0f}
📊 *Risk Profile:* {risk_profile.title()}

━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ *Equity (Growth)* - ₹{equity_amt:,.0f} ({equity_pct}%)
"""
        for inst in equity_instruments:
            response += f"   • {inst['name']}: {inst['return']} returns\n"
        
        response += f"""
2️⃣ *Debt (Stability)* - ₹{debt_amt:,.0f} ({debt_pct}%)
"""
        for inst in debt_instruments:
            response += f"   • {inst['name']}: {inst['return']} returns\n"
        
        response += f"""
3️⃣ *Gold (Hedge)* - ₹{gold_amt:,.0f} ({gold_pct}%)
   • Sovereign Gold Bonds (Best)
   • Digital Gold (PhonePe/GooglePay)

━━━━━━━━━━━━━━━━━━━━━━━━━━

🗓️ *Suggested SIP:* ₹{amount/12:,.0f}/month
This spreads risk through rupee cost averaging

📈 *Expected Returns (Long Term):*
• Conservative: 8-10% p.a.
• Moderate: 10-14% p.a.
• Aggressive: 12-18% p.a.

💡 *Pro Tip:* Start with monthly SIP, increase amount with income growth.

━━━━━━━━━━━━━━━━━━━━━━━━━━
*Next Steps:*
1. Open Demat account (Zerodha/Groww)
2. Complete KYC
3. Start SIP on day 1 of month

⚠️ Past returns don't guarantee future performance."""
        
        return response
    
    def get_safe_investments(self) -> str:
        """Return low-risk investment options"""
        
        options = self.instruments["conservative"]
        
        response = """🛡️ *Safe Investment Options*
━━━━━━━━━━━━━━━━━━━━

Best for: Emergency fund, short-term goals, risk-averse investors

"""
        for i, opt in enumerate(options, 1):
            response += f"""{i}. *{opt['name']}*
   📈 Returns: {opt['return']}
   🔒 Lock-in: {opt['lock']}
   ⚡ Risk: {opt['risk']}

"""
        
        response += """━━━━━━━━━━━━━━━━━━━━

💡 *Recommendation:*
Split between FD (50%) and Debt Funds (50%) for optimal liquidity and returns.

📌 *Tax Note:*
PPF interest is tax-free. FD interest is taxable.

Type "invest [amount]" for a personalized plan!"""
        
        return response
    
    def get_growth_investments(self) -> str:
        """Return high-growth investment options"""
        
        moderate_options = self.instruments["moderate"]
        aggressive_options = self.instruments["aggressive"][:2]
        
        response = """🚀 *High Growth Investment Options*
━━━━━━━━━━━━━━━━━━━━

Best for: Long-term wealth creation (5+ years)

*📊 Moderate Growth:*
"""
        for opt in moderate_options:
            response += f"• {opt['name']}: {opt['return']} ({opt['risk']} risk)\n"
        
        response += """
*🔥 Aggressive Growth:*
"""
        for opt in aggressive_options:
            response += f"• {opt['name']}: {opt['return']} ({opt['risk']})\n"
        
        response += """
━━━━━━━━━━━━━━━━━━━━

💡 *Smart Strategy:*
• Start with Index Funds (Nifty 50)
• Add Mid Cap after 2 years experience
• Only 10-15% in individual stocks

📌 *Golden Rule:*
"Time in market beats timing the market"

⚠️ Only invest money you won't need for 5+ years."""
        
        return response
    
    def get_sip_recommendation(self, monthly_income: float, age: int = 30) -> str:
        """Calculate ideal SIP amount and allocation"""
        
        # 20-30% of income for investment is ideal
        min_sip = monthly_income * 0.20
        ideal_sip = monthly_income * 0.25
        max_sip = monthly_income * 0.30
        
        # Equity allocation based on age
        equity_pct = 100 - age
        
        response = f"""📈 *Your Ideal SIP Plan*
━━━━━━━━━━━━━━━━━━━━

💰 *Monthly Income:* ₹{monthly_income:,.0f}

🎯 *Recommended SIP:*
• Minimum: ₹{min_sip:,.0f}/month (20%)
• Ideal: ₹{ideal_sip:,.0f}/month (25%)
• Maximum: ₹{max_sip:,.0f}/month (30%)

━━━━━━━━━━━━━━━━━━━━

📊 *Suggested Allocation:*
• Equity Funds: {equity_pct}% (₹{ideal_sip * equity_pct / 100:,.0f})
• Debt Funds: {100 - equity_pct - 10}% (₹{ideal_sip * (100 - equity_pct - 10) / 100:,.0f})
• Gold: 10% (₹{ideal_sip * 0.10:,.0f})

*My Picks:*
1. Nifty 50 Index Fund - Core holding
2. Nifty Midcap 150 - Growth boost
3. Liquid Fund - Emergency access
4. SGB - Gold exposure

━━━━━━━━━━━━━━━━━━━━

💡 *Auto-increase Strategy:*
Increase SIP by 10% every year with salary hike.

📅 Best SIP date: 1st-5th of month"""
        
        return response
    
    def _get_market_mood(self) -> Dict:
        """Simulate market mood with weighted probability"""
        moods = list(self.market_states.keys())
        weights = [self.market_states[m]["weight"] for m in moods]
        selected = random.choices(moods, weights=weights)[0]
        
        return {
            "name": selected.title(),
            "emoji": self.market_states[selected]["emoji"]
        }
    
    def _get_strategy_for_mood(self, mood: str) -> str:
        """Get investment strategy based on market mood"""
        strategies = {
            "Bullish": """✅ *Buy on strength*
   • Continue SIP as planned
   • Consider adding mid-caps
   • Book partial profits on high gains""",
            
            "Bearish": """⛑️ *Defensive mode*
   • Don't panic - continue SIP
   • Great time to accumulate quality stocks
   • Avoid fresh lump sum investments""",
            
            "Neutral": """⚖️ *Balanced approach*
   • Stick to your SIP schedule
   • Review and rebalance portfolio
   • Perfect for starting new investments""",
            
            "Volatile": """⚡ *Stay cautious*
   • Avoid lump sum, prefer SIP
   • Keep 20% cash for opportunities
   • Focus on large caps and debt"""
        }
        return strategies.get(mood, strategies["Neutral"])


# Create global instance
investment_service = AdvancedInvestmentService()
