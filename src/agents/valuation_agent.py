"""Valuation Agent - Analyzes stock valuation metrics and fair value estimates."""
from typing import Dict, Any
from datetime import date
from src.agents.base_agent import BaseAgent
from src.data.loaders import DataLoader


class ValuationAgent(BaseAgent):
    """Agent specializing in valuation analysis."""
    
    def __init__(self):
        super().__init__(
            name="Valuation Agent",
            description="Analyzes stock valuation metrics, fair value estimates, and market perception"
        )
        self.data_loader = DataLoader()
    
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
        valuation = self.data_loader.get_valuation(symbol, as_of_date)
        if valuation:
            signals.update({
                "market_cap": valuation.market_cap,
                "enterprise_value": valuation.enterprise_value,
                "pe_ratio": valuation.pe_ratio,
                "pb_ratio": valuation.pb_ratio,
                "ev_ebitda": valuation.ev_ebitda,
                "dcf_value": valuation.dcf_value,
                "fair_value_estimate": valuation.fair_value_estimate
            })
        
        # Get current price
        current_price = self.data_loader.get_current_price(symbol)
        if current_price:
            signals["current_price"] = current_price
        
        # Get historical valuation ranges
        historical_valuation = self.data_loader.get_valuation_history(symbol, as_of_date, periods=12)
        if historical_valuation:
            pe_ratios = [v.pe_ratio for v in historical_valuation if v.pe_ratio]
            if pe_ratios:
                signals["historical_pe_range"] = {
                    "min": min(pe_ratios),
                    "max": max(pe_ratios),
                    "avg": sum(pe_ratios) / len(pe_ratios),
                    "current": valuation.pe_ratio if valuation and valuation.pe_ratio else None
                }
        
        # Get peer valuations
        peer_valuations = self.data_loader.get_peer_valuations(symbol)
        if peer_valuations:
            signals["peer_valuations"] = peer_valuations
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze valuation signals."""
        analysis = {}
        
        # Fair value assessment
        if signals.get("current_price") and signals.get("fair_value_estimate"):
            current = signals["current_price"]
            fair_value = signals["fair_value_estimate"]
            discount_premium = ((current / fair_value) - 1) * 100
            
            if discount_premium < -10:
                analysis["value_assessment"] = "significantly undervalued"
            elif discount_premium < -5:
                analysis["value_assessment"] = "undervalued"
            elif discount_premium > 10:
                analysis["value_assessment"] = "significantly overvalued"
            elif discount_premium > 5:
                analysis["value_assessment"] = "overvalued"
            else:
                analysis["value_assessment"] = "fairly valued"
            
            analysis["discount_premium_pct"] = discount_premium
        
        # P/E ratio analysis
        if "historical_pe_range" in signals:
            pe_range = signals["historical_pe_range"]
            current_pe = pe_range.get("current")
            avg_pe = pe_range.get("avg")
            
            if current_pe and avg_pe:
                pe_vs_avg = ((current_pe / avg_pe) - 1) * 100
                if pe_vs_avg < -20:
                    analysis["pe_assessment"] = "well below historical average"
                elif pe_vs_avg > 20:
                    analysis["pe_assessment"] = "well above historical average"
                else:
                    analysis["pe_assessment"] = "near historical average"
        
        # Peer comparison
        if "peer_valuations" in signals:
            peer_pe = signals["peer_valuations"].get("avg_pe_ratio")
            current_pe = signals.get("pe_ratio")
            if peer_pe and current_pe:
                if current_pe < peer_pe * 0.9:
                    analysis["peer_comparison"] = "trading at discount to peers"
                elif current_pe > peer_pe * 1.1:
                    analysis["peer_comparison"] = "trading at premium to peers"
                else:
                    analysis["peer_comparison"] = "in line with peers"
        
        return analysis
