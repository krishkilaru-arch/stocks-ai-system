"""Valuation Agent - Analyzes stock valuation metrics and fair value estimates."""
from typing import Dict, Any
from datetime import date
from src.agents.base_agent import BaseAgent
from src.data.loaders import YahooFinanceLoader


class ValuationAgent(BaseAgent):
    """Agent specializing in valuation analysis."""
    
    def __init__(self):
        super().__init__(
            name="Valuation Agent",
            description="Analyzes stock valuation metrics, fair value estimates, and market perception"
        )
        self.data_loader = YahooFinanceLoader()
    
    def get_system_prompt(self) -> str:
        return """You are a valuation analyst specializing in determining fair value of stocks.

Your expertise includes:
- Valuation multiples (P/E, P/B, EV/EBITDA, P/S)
- Discounted Cash Flow (DCF) analysis
- Relative valuation (comparable company analysis)
- Market perception and sentiment
- Value vs. growth characteristics

When making predictions, consider:
1. Current valuation multiples vs. historical averages
2. Valuation multiples vs. industry peers
3. DCF-based fair value estimates
4. Market sentiment and perception shifts
5. Value vs. growth characteristics
6. Mean reversion tendencies in valuations

Provide clear reasoning based on valuation principles and whether the stock is overvalued, undervalued, or fairly valued."""
    
    def collect_signals(self, symbol: str, as_of_date: date) -> Dict[str, Any]:
        """Collect valuation signals."""
        signals = {}
        
        # Get valuation metrics
        valuation = self.data_loader.load_valuation(symbol, as_of_date)
        if valuation:
            signals.update({
                "symbol": symbol,
                "date": as_of_date.isoformat(),
                "market_cap": valuation.market_cap,
                "enterprise_value": valuation.enterprise_value,
                "pe_ratio": valuation.pe_ratio,
                "pb_ratio": valuation.pb_ratio,
                "ev_ebitda": valuation.ev_ebitda,
                "dcf_value": valuation.dcf_value,
                "fair_value_estimate": valuation.fair_value_estimate
            })
        
        # Get current price from technical data
        technical = self.data_loader.load_technical(symbol, as_of_date)
        if technical and technical.close_price:
            signals["current_price"] = technical.close_price
        
        # Get company info
        company = self.data_loader.load_company_info(symbol)
        if company:
            signals["company_name"] = company.company_name
            signals["sector"] = company.sector
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze valuation signals."""
        analysis = {}
        
        # Fair value assessment
        if signals.get("current_price") and signals.get("fair_value_estimate"):
            current = signals["current_price"]
            fair_value = signals["fair_value_estimate"]
            discount_premium = ((current / fair_value) - 1) * 100
            
            if discount_premium < -15:
                analysis["value_assessment"] = "significantly undervalued (-15%+)"
            elif discount_premium < -5:
                analysis["value_assessment"] = "undervalued (-5% to -15%)"
            elif discount_premium > 15:
                analysis["value_assessment"] = "significantly overvalued (+15%+)"
            elif discount_premium > 5:
                analysis["value_assessment"] = "overvalued (+5% to +15%)"
            else:
                analysis["value_assessment"] = "fairly valued (±5%)"
            
            analysis["discount_premium_pct"] = round(discount_premium, 2)
        
        # P/E ratio analysis
        if signals.get("pe_ratio"):
            pe = signals["pe_ratio"]
            if pe < 10:
                analysis["pe_assessment"] = "very low P/E (<10), potential value"
            elif pe < 20:
                analysis["pe_assessment"] = "moderate P/E (10-20), reasonable valuation"
            elif pe < 30:
                analysis["pe_assessment"] = "elevated P/E (20-30), growth expected"
            else:
                analysis["pe_assessment"] = "high P/E (>30), premium valuation"
        
        # P/B ratio analysis
        if signals.get("pb_ratio"):
            pb = signals["pb_ratio"]
            if pb < 1.0:
                analysis["pb_assessment"] = "below book value (P/B <1.0)"
            elif pb < 3.0:
                analysis["pb_assessment"] = "moderate P/B (1.0-3.0)"
            else:
                analysis["pb_assessment"] = "high P/B (>3.0), growth premium"
        
        # EV/EBITDA analysis
        if signals.get("ev_ebitda"):
            ev_ebitda = signals["ev_ebitda"]
            if ev_ebitda < 10:
                analysis["ev_ebitda_assessment"] = "attractive EV/EBITDA (<10)"
            elif ev_ebitda < 15:
                analysis["ev_ebitda_assessment"] = "fair EV/EBITDA (10-15)"
            else:
                analysis["ev_ebitda_assessment"] = "expensive EV/EBITDA (>15)"
        
        return analysis
