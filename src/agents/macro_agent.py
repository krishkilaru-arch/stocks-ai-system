"""Macro Agent - Analyzes macroeconomic indicators and their impact on stocks."""
from typing import Dict, Any
from datetime import date
from src.agents.base_agent import BaseAgent
from src.data.loaders import DataLoader


class MacroAgent(BaseAgent):
    """Agent specializing in macroeconomic analysis."""
    
    def __init__(self):
        super().__init__(
            name="Macro Agent",
            description="Analyzes macroeconomic indicators, policy changes, and their impact on stock markets"
        )
        self.data_loader = DataLoader()
    
    def get_system_prompt(self) -> str:
        return """You are a macroeconomist specializing in how macroeconomic factors affect stock markets.

Your expertise includes:
- GDP growth and economic cycles
- Inflation and interest rates
- Monetary and fiscal policy
- Unemployment and labor markets
- Consumer confidence and sentiment
- Market volatility (VIX)
- Sector rotation and economic cycles

When making predictions, consider:
1. Current economic cycle phase (expansion, peak, contraction, trough)
2. Interest rate environment and Fed policy
3. Inflation trends and their impact on different sectors
4. Consumer confidence and spending patterns
5. Market volatility and risk sentiment
6. Sector sensitivity to macro factors
7. Historical correlations between macro indicators and stock performance

Provide reasoning that connects macroeconomic conditions to expected stock performance."""
    
    def collect_signals(self, symbol: str, as_of_date: date) -> Dict[str, Any]:
        """Collect macroeconomic signals."""
        signals = {}
        
        # Get macro indicators
        macro = self.data_loader.get_macro_indicators(as_of_date)
        if macro:
            signals.update({
                "gdp_growth": macro.gdp_growth,
                "inflation_rate": macro.inflation_rate,
                "interest_rate": macro.interest_rate,
                "unemployment_rate": macro.unemployment_rate,
                "consumer_confidence": macro.consumer_confidence,
                "vix_index": macro.vix_index
            })
        
        # Get historical macro trends
        macro_history = self.data_loader.get_macro_history(as_of_date, months=12)
        if macro_history:
            signals["macro_trends"] = {
                "gdp_trend": [m.gdp_growth for m in macro_history if m.gdp_growth],
                "inflation_trend": [m.inflation_rate for m in macro_history if m.inflation_rate],
                "interest_rate_trend": [m.interest_rate for m in macro_history if m.interest_rate]
            }
        
        # Get sector sensitivity
        sector_sensitivity = self.data_loader.get_sector_macro_sensitivity(symbol)
        if sector_sensitivity:
            signals["sector_sensitivity"] = sector_sensitivity
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze macroeconomic signals."""
        analysis = {}
        
        # Economic cycle assessment
        if signals.get("gdp_growth"):
            gdp_growth = signals["gdp_growth"]
            if gdp_growth > 3:
                analysis["economic_phase"] = "strong expansion"
            elif gdp_growth > 1:
                analysis["economic_phase"] = "moderate expansion"
            elif gdp_growth > 0:
                analysis["economic_phase"] = "slow growth"
            else:
                analysis["economic_phase"] = "contraction"
        
        # Interest rate environment
        if signals.get("interest_rate"):
            rate = signals["interest_rate"]
            if rate > 5:
                analysis["rate_environment"] = "high"
            elif rate > 2:
                analysis["rate_environment"] = "moderate"
            else:
                analysis["rate_environment"] = "low"
        
        # Inflation assessment
        if signals.get("inflation_rate"):
            inflation = signals["inflation_rate"]
            if inflation > 4:
                analysis["inflation_status"] = "high"
            elif inflation > 2:
                analysis["inflation_status"] = "moderate"
            else:
                analysis["inflation_status"] = "low"
        
        # Market sentiment (VIX)
        if signals.get("vix_index"):
            vix = signals["vix_index"]
            if vix > 25:
                analysis["market_sentiment"] = "high fear/volatility"
            elif vix > 15:
                analysis["market_sentiment"] = "moderate volatility"
            else:
                analysis["market_sentiment"] = "low volatility/calm"
        
        # Trend analysis
        if "macro_trends" in signals:
            trends = signals["macro_trends"]
            if "interest_rate_trend" in trends and len(trends["interest_rate_trend"]) >= 2:
                rate_trend = trends["interest_rate_trend"]
                if rate_trend[-1] > rate_trend[0]:
                    analysis["rate_trend"] = "rising"
                elif rate_trend[-1] < rate_trend[0]:
                    analysis["rate_trend"] = "falling"
                else:
                    analysis["rate_trend"] = "stable"
        
        return analysis
