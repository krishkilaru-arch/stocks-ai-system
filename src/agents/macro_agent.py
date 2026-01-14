"""Macro Agent - Analyzes macroeconomic indicators and their impact on stocks."""
from typing import Dict, Any
from datetime import date
from src.agents.base_agent import BaseAgent
from src.data.loaders import YahooFinanceLoader
import yfinance as yf


class MacroAgent(BaseAgent):
    """Agent specializing in macroeconomic analysis."""
    
    def __init__(self):
        super().__init__(
            name="Macro Agent",
            description="Analyzes macroeconomic indicators, policy changes, and their impact on stock markets"
        )
        self.data_loader = YahooFinanceLoader()
    
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
        signals = {
            "symbol": symbol,
            "date": as_of_date.isoformat()
        }
        
        # Get company info for sector context
        company = self.data_loader.load_company_info(symbol)
        if company:
            signals["company_name"] = company.company_name
            signals["sector"] = company.sector
            signals["industry"] = company.industry
        
        # Get market indices for macro context
        try:
            # S&P 500 as market proxy
            sp500 = yf.Ticker("^GSPC")
            sp500_info = sp500.info
            signals["market_index"] = "S&P 500"
            signals["market_pe"] = sp500_info.get("trailingPE")
            
            # VIX for volatility/fear gauge
            vix = yf.Ticker("^VIX")
            vix_hist = vix.history(period="5d")
            if not vix_hist.empty:
                signals["vix_index"] = float(vix_hist['Close'].iloc[-1])
            
            # Treasury yields for interest rate environment
            tnx = yf.Ticker("^TNX")  # 10-year treasury
            tnx_hist = tnx.history(period="5d")
            if not tnx_hist.empty:
                signals["treasury_10y"] = float(tnx_hist['Close'].iloc[-1])
                
        except Exception as e:
            signals["macro_data_note"] = f"Limited macro data available: {str(e)[:100]}"
        
        # Placeholder for macro indicators (would come from FRED in production)
        signals["macro_indicators"] = {
            "note": "Using market proxies - integrate FRED API for full macro data",
            "available_indicators": ["VIX", "Treasury Yields", "Market P/E"]
        }
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze macroeconomic signals."""
        analysis = {}
        
        # Interest rate environment assessment (from Treasury yields)
        if signals.get("treasury_10y"):
            rate = signals["treasury_10y"]
            if rate > 4.5:
                analysis["rate_environment"] = "high rates (>4.5%), negative for growth stocks"
            elif rate > 3.5:
                analysis["rate_environment"] = "elevated rates (3.5-4.5%), moderate pressure"
            elif rate > 2.0:
                analysis["rate_environment"] = "normal rates (2-3.5%), balanced"
            else:
                analysis["rate_environment"] = "low rates (<2%), supportive for equities"
            analysis["treasury_10y_yield"] = f"{rate:.2f}%"
        
        # Market sentiment assessment (VIX)
        if signals.get("vix_index"):
            vix = signals["vix_index"]
            if vix > 30:
                analysis["market_sentiment"] = "extreme fear (VIX>30), high volatility"
            elif vix > 20:
                analysis["market_sentiment"] = "elevated fear (VIX 20-30), heightened volatility"
            elif vix > 15:
                analysis["market_sentiment"] = "moderate volatility (VIX 15-20)"
            else:
                analysis["market_sentiment"] = "low fear (VIX<15), calm markets"
            analysis["vix_level"] = f"{vix:.2f}"
        
        # Market valuation assessment
        if signals.get("market_pe"):
            market_pe = signals["market_pe"]
            if market_pe > 22:
                analysis["market_valuation"] = "expensive market (P/E>22), potential correction risk"
            elif market_pe > 18:
                analysis["market_valuation"] = "fairly valued market (P/E 18-22)"
            elif market_pe > 14:
                analysis["market_valuation"] = "attractive market (P/E 14-18), good entry"
            else:
                analysis["market_valuation"] = "cheap market (P/E<14), strong value opportunity"
        
        # Sector-specific macro sensitivity
        sector = signals.get("sector", "")
        if sector:
            # High interest rate sensitivity sectors
            rate_sensitive = ["Real Estate", "Utilities", "Technology"]
            # Cyclical sectors (GDP sensitive)
            cyclical = ["Consumer Discretionary", "Industrials", "Materials", "Energy"]
            # Defensive sectors
            defensive = ["Consumer Staples", "Healthcare", "Utilities"]
            
            if sector in rate_sensitive:
                analysis["sector_macro_profile"] = f"{sector} is rate-sensitive, watch Fed policy"
            elif sector in cyclical:
                analysis["sector_macro_profile"] = f"{sector} is cyclical, tied to economic growth"
            elif sector in defensive:
                analysis["sector_macro_profile"] = f"{sector} is defensive, stable in downturns"
            else:
                analysis["sector_macro_profile"] = f"{sector} macro sensitivity varies"
        
        return analysis
