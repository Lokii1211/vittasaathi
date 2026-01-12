"""
Stock Market Analysis Service - AlphaVantage Integration
==========================================================
Provides real-time market data, analysis, and investment recommendations.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Optional aiohttp for API calls
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

# AlphaVantage API Key
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")


@dataclass
class StockData:
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    high: float
    low: float
    volume: int
    timestamp: str


@dataclass
class MarketSummary:
    nifty50: float
    nifty50_change: float
    sensex: float
    sensex_change: float
    bank_nifty: float
    bank_nifty_change: float
    top_gainers: List[StockData]
    top_losers: List[StockData]
    market_status: str
    analysis: str
    recommendation: str


class StockMarketService:
    """
    Stock Market Analysis Service
    ==============================
    - Fetches real-time market data
    - Analyzes trends
    - Provides investment recommendations
    - Supports Indian markets (NSE/BSE)
    """
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    # Indian market indices
    INDIAN_INDICES = {
        "NIFTY50": "^NSEI",
        "SENSEX": "^BSESN",
        "BANKNIFTY": "^NSEBANK"
    }
    
    # Popular Indian stocks
    POPULAR_STOCKS = [
        {"symbol": "RELIANCE.BSE", "name": "Reliance Industries"},
        {"symbol": "TCS.BSE", "name": "TCS"},
        {"symbol": "HDFCBANK.BSE", "name": "HDFC Bank"},
        {"symbol": "INFY.BSE", "name": "Infosys"},
        {"symbol": "ICICIBANK.BSE", "name": "ICICI Bank"},
        {"symbol": "SBIN.BSE", "name": "SBI"},
        {"symbol": "BHARTIARTL.BSE", "name": "Bharti Airtel"},
        {"symbol": "ITC.BSE", "name": "ITC"},
        {"symbol": "KOTAKBANK.BSE", "name": "Kotak Bank"},
        {"symbol": "LT.BSE", "name": "L&T"}
    ]
    
    def __init__(self):
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 300  # 5 minutes
        
    async def _fetch_data(self, params: Dict) -> Optional[Dict]:
        """Fetch data from AlphaVantage API"""
        params["apikey"] = ALPHA_VANTAGE_API_KEY
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, params=params) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            print(f"[StockService] Error fetching data: {e}")
        
        return None
    
    async def get_quote(self, symbol: str) -> Optional[StockData]:
        """Get real-time quote for a symbol"""
        
        # Check cache
        cache_key = f"quote_{symbol}"
        if cache_key in self.cache:
            if datetime.now().timestamp() < self.cache_expiry.get(cache_key, 0):
                return self.cache[cache_key]
        
        data = await self._fetch_data({
            "function": "GLOBAL_QUOTE",
            "symbol": symbol
        })
        
        if data and "Global Quote" in data:
            quote = data["Global Quote"]
            stock_data = StockData(
                symbol=symbol,
                name=symbol,
                price=float(quote.get("05. price", 0)),
                change=float(quote.get("09. change", 0)),
                change_percent=float(quote.get("10. change percent", "0%").replace("%", "")),
                high=float(quote.get("03. high", 0)),
                low=float(quote.get("04. low", 0)),
                volume=int(quote.get("06. volume", 0)),
                timestamp=quote.get("07. latest trading day", "")
            )
            
            # Cache the result
            self.cache[cache_key] = stock_data
            self.cache_expiry[cache_key] = datetime.now().timestamp() + self.cache_duration
            
            return stock_data
        
        return None
    
    async def get_market_summary(self) -> MarketSummary:
        """Get complete market summary with analysis"""
        
        # For demo purposes, return simulated data
        # In production, fetch real data from AlphaVantage
        
        import random
        
        # Simulate market data
        nifty = 22400 + random.uniform(-200, 300)
        nifty_change = random.uniform(-1.5, 2.0)
        sensex = 74000 + random.uniform(-500, 800)
        sensex_change = random.uniform(-1.5, 2.0)
        bank_nifty = 48500 + random.uniform(-400, 600)
        bank_nifty_change = random.uniform(-2.0, 2.5)
        
        # Simulate top gainers and losers
        top_gainers = [
            StockData("HDFC Bank", "HDFCBANK", 1650 + random.uniform(0, 50), random.uniform(10, 40), random.uniform(1, 3), 0, 0, 0, ""),
            StockData("Reliance", "RELIANCE", 2450 + random.uniform(0, 100), random.uniform(20, 60), random.uniform(1, 2.5), 0, 0, 0, ""),
            StockData("Infosys", "INFY", 1520 + random.uniform(0, 40), random.uniform(10, 30), random.uniform(0.5, 2), 0, 0, 0, "")
        ]
        
        top_losers = [
            StockData("Tata Motors", "TATAMOTORS", 850 - random.uniform(0, 30), -random.uniform(10, 25), -random.uniform(1, 2.5), 0, 0, 0, ""),
            StockData("Bajaj Finance", "BAJFINANCE", 6800 - random.uniform(0, 100), -random.uniform(50, 100), -random.uniform(1, 2), 0, 0, 0, "")
        ]
        
        # Generate analysis
        market_trend = "bullish" if nifty_change > 0 else "bearish"
        
        if market_trend == "bullish":
            analysis = """Markets are showing positive momentum today. Banking sector is leading the gains with HDFC Bank and ICICI Bank performing well. IT stocks are also contributing to the upside.

Key factors driving the market:
• Strong FII inflows
• Positive global cues
• Robust earnings expectations"""
            
            recommendation = """📌 *For Medium Risk Profile:*
Consider adding to your SIP in:
• Nifty 50 Index Fund
• Banking Sector Fund

Good time to start monthly investments!"""
        else:
            analysis = """Markets are facing some selling pressure today. Global uncertainty and profit booking are weighing on the indices.

Key factors:
• FII outflows
• Global market weakness
• Sector rotation happening"""
            
            recommendation = """📌 *Investment Strategy:*
• Don't panic sell
• Continue your SIPs
• Consider buying quality stocks on dips
• Focus on large caps for stability"""
        
        # Determine market status based on time
        now = datetime.now()
        if now.weekday() >= 5:  # Weekend
            market_status = "🔴 Closed (Weekend)"
        elif now.hour < 9 or (now.hour == 9 and now.minute < 15):
            market_status = "🟡 Pre-Market"
        elif now.hour >= 15 and now.minute >= 30:
            market_status = "🔴 Closed"
        else:
            market_status = "🟢 Open"
        
        return MarketSummary(
            nifty50=round(nifty, 2),
            nifty50_change=round(nifty_change, 2),
            sensex=round(sensex, 2),
            sensex_change=round(sensex_change, 2),
            bank_nifty=round(bank_nifty, 2),
            bank_nifty_change=round(bank_nifty_change, 2),
            top_gainers=top_gainers,
            top_losers=top_losers,
            market_status=market_status,
            analysis=analysis,
            recommendation=recommendation
        )
    
    def format_market_message(self, summary: MarketSummary, lang: str = "en") -> str:
        """Format market summary for WhatsApp message"""
        
        # Format change with emoji
        def fmt_change(change: float) -> str:
            if change > 0:
                return f"🟢 +{change:.2f}%"
            elif change < 0:
                return f"🔴 {change:.2f}%"
            return f"⚪ {change:.2f}%"
        
        # Format top gainers
        gainers_text = ""
        for stock in summary.top_gainers[:3]:
            gainers_text += f"• {stock.name}: {fmt_change(stock.change_percent)}\n"
        
        # Format top losers
        losers_text = ""
        for stock in summary.top_losers[:3]:
            losers_text += f"• {stock.name}: {fmt_change(stock.change_percent)}\n"
        
        if lang == "en":
            return f"""📈 *Market Update - {datetime.now().strftime('%d %b %Y, %I:%M %p')}*

{summary.market_status}

🇮🇳 *Indian Markets:*
━━━━━━━━━━━━━━━━━━━━━
📊 NIFTY 50: {summary.nifty50:,.0f} ({fmt_change(summary.nifty50_change)})
📊 SENSEX: {summary.sensex:,.0f} ({fmt_change(summary.sensex_change)})
🏦 Bank Nifty: {summary.bank_nifty:,.0f} ({fmt_change(summary.bank_nifty_change)})

📈 *Top Gainers:*
{gainers_text}
📉 *Top Losers:*
{losers_text}
💡 *Analysis:*
{summary.analysis}

{summary.recommendation}"""
        
        elif lang == "hi":
            return f"""📈 *बाज़ार अपडेट - {datetime.now().strftime('%d %b %Y')}*

🇮🇳 *भारतीय बाज़ार:*
━━━━━━━━━━━━━━━━━━━━━
📊 NIFTY 50: {summary.nifty50:,.0f} ({fmt_change(summary.nifty50_change)})
📊 SENSEX: {summary.sensex:,.0f} ({fmt_change(summary.sensex_change)})

💡 *विश्लेषण:*
बाज़ार सकारात्मक है। SIP जारी रखें!"""
        
        elif lang == "ta":
            return f"""📈 *சந்தை புதுப்பிப்பு - {datetime.now().strftime('%d %b %Y')}*

🇮🇳 *இந்திய சந்தைகள்:*
━━━━━━━━━━━━━━━━━━━━━
📊 NIFTY 50: {summary.nifty50:,.0f} ({fmt_change(summary.nifty50_change)})
📊 SENSEX: {summary.sensex:,.0f} ({fmt_change(summary.sensex_change)})

💡 *பகுப்பாய்வு:*
சந்தை நேர்மறையாக உள்ளது. SIP தொடருங்கள்!"""
        
        return self.format_market_message(summary, "en")
    
    async def get_investment_tips(self, risk_profile: str, monthly_amount: float) -> str:
        """Generate investment tips based on risk profile"""
        
        if risk_profile.lower() == "low":
            return f"""💰 *Investment Recommendations (Low Risk)*

Based on ₹{monthly_amount:,.0f}/month:

🔒 *Safe Options:*
• Fixed Deposit: ₹{monthly_amount * 0.4:,.0f}/month (6-7% returns)
• PPF: ₹{monthly_amount * 0.3:,.0f}/month (7.1% tax-free)
• Debt Mutual Funds: ₹{monthly_amount * 0.3:,.0f}/month

📈 *Expected Returns:* 6-8% annually
⏰ *Best for:* Stable, guaranteed growth

_Start SIPs in liquid funds for emergency access!_"""
        
        elif risk_profile.lower() == "high":
            return f"""💰 *Investment Recommendations (High Risk)*

Based on ₹{monthly_amount:,.0f}/month:

🚀 *Aggressive Options:*
• Equity MF (Small Cap): ₹{monthly_amount * 0.4:,.0f}/month
• Direct Stocks: ₹{monthly_amount * 0.3:,.0f}/month
• Sectoral Funds: ₹{monthly_amount * 0.2:,.0f}/month
• Emergency Fund: ₹{monthly_amount * 0.1:,.0f}/month

📈 *Expected Returns:* 12-18% annually
⚠️ *Risk:* High volatility, long-term focus needed

_Only invest money you won't need for 5+ years!_"""
        
        else:  # Medium risk (default)
            return f"""💰 *Investment Recommendations (Balanced)*

Based on ₹{monthly_amount:,.0f}/month:

⚖️ *Balanced Approach:*
• Nifty Index Fund SIP: ₹{monthly_amount * 0.35:,.0f}/month
• Debt MF / PPF: ₹{monthly_amount * 0.25:,.0f}/month
• Large Cap MF: ₹{monthly_amount * 0.25:,.0f}/month
• Emergency Fund: ₹{monthly_amount * 0.15:,.0f}/month

📈 *Expected Returns:* 10-12% annually
✅ *Risk:* Moderate, good for most goals

_This is ideal for 3-5 year goals like a car or vacation!_"""
    
    async def analyze_investment_opportunity(self, symbol: str) -> str:
        """Analyze a specific stock/investment"""
        
        quote = await self.get_quote(symbol)
        
        if not quote:
            return f"Could not fetch data for {symbol}. Please try again."
        
        # Simple analysis
        trend = "bullish" if quote.change > 0 else "bearish"
        
        return f"""📊 *{symbol} Analysis*

💰 Current Price: ₹{quote.price:,.2f}
📈 Change: ₹{quote.change:,.2f} ({quote.change_percent:,.2f}%)
📊 Day Range: ₹{quote.low:,.2f} - ₹{quote.high:,.2f}
📦 Volume: {quote.volume:,}

🔍 *Trend:* {trend.upper()}

💡 *Recommendation:*
{'Consider buying on dips for long-term.' if trend == 'bullish' else 'Wait for better entry point.'}"""


# Create singleton instance
stock_market_service = StockMarketService()


# Export functions
async def get_market_update(lang: str = "en") -> str:
    """Get formatted market update message"""
    summary = await stock_market_service.get_market_summary()
    return stock_market_service.format_market_message(summary, lang)


async def get_investment_advice(risk_profile: str, monthly_amount: float) -> str:
    """Get investment advice based on profile"""
    return await stock_market_service.get_investment_tips(risk_profile, monthly_amount)
