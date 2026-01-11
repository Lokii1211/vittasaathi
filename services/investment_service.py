import random
from typing import Dict, List

class InvestmentService:
    """
    Advanced Investment Advisory Service
    Provides market insights, portfolio allocation, and trend analysis.
    """
    
    def __init__(self):
        self.market_moods = ["Bullish 🐂", "Bearish 🐻", "Neutral 😐", "Volatile ⚡"]
        self.sectors = [
            {"name": "Green Energy 🌿", "trend": "High Growth", "risk": "Moderate"},
            {"name": "Banking (PSU) 🏦", "trend": "Stable", "risk": "Low"},
            {"name": "IT & Tech 💻", "trend": "Recovering", "risk": "Moderate"},
            {"name": "Defense 🛡️", "trend": "Booming", "risk": "High"},
            {"name": "FMCG 🛒", "trend": "Defensive", "risk": "Low"}
        ]
    
    def get_market_analysis(self) -> str:
        """Simulate a deep market analysis"""
        mood = random.choice(self.market_moods)
        sector = random.choice(self.sectors)
        
        return f"""
📈 *Daily Market Pulse*
*Mood:* {mood}
*Top Sector:* {sector['name']} ({sector['trend']})

*Analyst View:* 
The market is currently showing {mood.lower().split(' ')[0]} signs. Smart money is moving towards {sector['name']}. 
Suggested Action: {self._get_action_for_mood(mood)}
"""

    def _get_action_for_mood(self, mood: str) -> str:
        if "Bullish" in mood: return "Buy on dips. Focus on quality midcaps."
        if "Bearish" in mood: return "Accumulate Bluechips. Stay cash rich."
        return "SIP is the best strategy. Don't time the market."
        
    def get_portfolio_plan(self, amount: float, age: int = 30) -> str:
        """Generate a personalized investment plan"""
        
        # Simple Rule of 100 for Equity
        equity_pct = 100 - age
        debt_pct = age
        
        equity_amt = (amount * equity_pct) / 100
        debt_amt = (amount * debt_pct) / 100
        gold_amt = amount * 0.10 # 10% Gold standard
        
        # Adjust equity/debt after gold
        equity_amt = equity_amt * 0.9
        debt_amt = debt_amt * 0.9
        
        return f"""
📊 *Recommended Portfolio Allocation*
For investment of ₹{amount:,.0f}:

1️⃣ *Equity (Growth)* - ₹{equity_amt:,.0f} ({equity_pct}%)
   - Index Funds (Nifty 50): 60%
   - Midcap Funds: 30%
   - Smallcap: 10%

2️⃣ *Debt (Stability)* - ₹{debt_amt:,.0f} ({debt_pct}%)
   - PPF / EPF / FD
   - Liquid Mutual Funds

3️⃣ *Gold (Hedge)* - ₹{gold_amt:,.0f} (10%)
   - SGB or Digital Gold

💡 *Strategy:* Start an SIP of ₹{amount/12:,.0f}/month to average out volatility.
"""

investment_service = InvestmentService()
