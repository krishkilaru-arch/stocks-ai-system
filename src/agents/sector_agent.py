"""Sector Agent - Analyzes industry trends and peer comparisons."""
from typing import Dict, Any, List
from datetime import date, timedelta
from src.agents.base_agent import BaseAgent
from src.data.loaders import YahooFinanceLoader
import yfinance as yf


class SectorAgent(BaseAgent):
    """Agent specializing in sector and industry analysis."""
    
    def __init__(self):
        super().__init__(
            name="Sector Agent",
            description="Analyzes industry trends, sector performance, and peer company comparisons"
        )
        self.data_loader = YahooFinanceLoader()
    
    def get_system_prompt(self) -> str:
        return """You are a sector analyst specializing in industry trends and peer comparisons.

Your expertise includes:
- Industry growth trends and cycles
- Sector rotation patterns
- Competitive positioning
- Peer company performance
- Industry-specific metrics and KPIs
- Regulatory and structural changes in industries
- Market share dynamics

When making predictions, consider:
1. Overall sector performance and trends
2. Company's position relative to peers
3. Industry growth prospects
4. Competitive advantages or disadvantages
5. Sector-specific headwinds or tailwinds
6. Market share trends
7. Industry consolidation or disruption

Provide reasoning that connects sector dynamics to individual stock performance."""
    
    def collect_signals(self, symbol: str, as_of_date: date) -> Dict[str, Any]:
        """Collect sector-related signals."""
        signals = {
            "symbol": symbol,
            "date": as_of_date.isoformat()
        }
        
        # Get company sector info
        company = self.data_loader.load_company_info(symbol)
        if company:
            signals["company_name"] = company.company_name
            signals["sector"] = company.sector
            signals["industry"] = company.industry
            signals["market_cap"] = company.market_cap
        
        # Get sector ETF performance as proxy
        sector_etf_map = {
            "Technology": "XLK",
            "Healthcare": "XLV",
            "Financials": "XLF",
            "Consumer Discretionary": "XLY",
            "Consumer Staples": "XLP",
            "Energy": "XLE",
            "Industrials": "XLI",
            "Materials": "XLB",
            "Real Estate": "XLRE",
            "Utilities": "XLU",
            "Communication Services": "XLC"
        }
        
        sector = signals.get("sector", "")
        if sector in sector_etf_map:
            try:
                etf_symbol = sector_etf_map[sector]
                etf = yf.Ticker(etf_symbol)
                etf_hist = etf.history(period="6mo")
                
                if not etf_hist.empty:
                    # Calculate sector performance
                    first_close = etf_hist['Close'].iloc[0]
                    last_close = etf_hist['Close'].iloc[-1]
                    sector_return = ((last_close / first_close) - 1) * 100
                    
                    signals["sector_etf"] = etf_symbol
                    signals["sector_6m_return"] = round(sector_return, 2)
                    
                    # Recent momentum (1 month)
                    if len(etf_hist) >= 20:
                        month_ago_close = etf_hist['Close'].iloc[-20]
                        recent_return = ((last_close / month_ago_close) - 1) * 100
                        signals["sector_1m_return"] = round(recent_return, 2)
            except:
                pass
        
        # Get company's own performance for comparison
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="6mo")
            if not hist.empty:
                first_close = hist['Close'].iloc[0]
                last_close = hist['Close'].iloc[-1]
                company_return = ((last_close / first_close) - 1) * 100
                signals["company_6m_return"] = round(company_return, 2)
                
                if len(hist) >= 20:
                    month_ago_close = hist['Close'].iloc[-20]
                    recent_return = ((last_close / month_ago_close) - 1) * 100
                    signals["company_1m_return"] = round(recent_return, 2)
        except:
            pass
        
        # Simplified peer analysis using sector
        signals["peer_analysis_note"] = "Using sector ETF as benchmark - add specific peer symbols for detailed comparison"
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sector signals."""
        analysis = {}
        
        # Sector performance assessment (6-month)
        if signals.get("sector_6m_return") is not None:
            sector_return = signals["sector_6m_return"]
            
            if sector_return > 20:
                analysis["sector_performance"] = "strong sector (6M: +20%+)"
            elif sector_return > 10:
                analysis["sector_performance"] = "outperforming sector (6M: +10-20%)"
            elif sector_return > 0:
                analysis["sector_performance"] = "positive sector (6M: 0-10%)"
            elif sector_return > -10:
                analysis["sector_performance"] = "weak sector (6M: 0 to -10%)"
            else:
                analysis["sector_performance"] = "underperforming sector (6M: -10%+)"
            
            analysis["sector_6m_return_pct"] = f"{sector_return:+.2f}%"
        
        # Recent sector momentum (1-month)
        if signals.get("sector_1m_return") is not None:
            recent = signals["sector_1m_return"]
            if recent > 5:
                analysis["sector_momentum"] = "strong recent momentum (+5%+ in 1M)"
            elif recent > 2:
                analysis["sector_momentum"] = "positive momentum (+2-5% in 1M)"
            elif recent > -2:
                analysis["sector_momentum"] = "neutral momentum (±2% in 1M)"
            elif recent > -5:
                analysis["sector_momentum"] = "negative momentum (-2 to -5% in 1M)"
            else:
                analysis["sector_momentum"] = "weak momentum (-5%+ in 1M)"
        
        # Company vs Sector comparison
        if signals.get("company_6m_return") is not None and signals.get("sector_6m_return") is not None:
            company_ret = signals["company_6m_return"]
            sector_ret = signals["sector_6m_return"]
            relative_perf = company_ret - sector_ret
            
            if relative_perf > 10:
                analysis["relative_performance"] = f"strongly outperforming sector (+{relative_perf:.1f}% vs sector)"
            elif relative_perf > 5:
                analysis["relative_performance"] = f"outperforming sector (+{relative_perf:.1f}% vs sector)"
            elif relative_perf > -5:
                analysis["relative_performance"] = f"in line with sector ({relative_perf:+.1f}% vs sector)"
            elif relative_perf > -10:
                analysis["relative_performance"] = f"underperforming sector ({relative_perf:.1f}% vs sector)"
            else:
                analysis["relative_performance"] = f"significantly lagging sector ({relative_perf:.1f}% vs sector)"
        
        # Recent relative momentum (1-month)
        if signals.get("company_1m_return") is not None and signals.get("sector_1m_return") is not None:
            company_1m = signals["company_1m_return"]
            sector_1m = signals["sector_1m_return"]
            recent_relative = company_1m - sector_1m
            
            if recent_relative > 3:
                analysis["recent_relative_strength"] = "gaining on sector peers"
            elif recent_relative < -3:
                analysis["recent_relative_strength"] = "losing to sector peers"
            else:
                analysis["recent_relative_strength"] = "tracking sector"
        
        # Sector positioning
        sector_name = signals.get("sector", "Unknown")
        analysis["sector_context"] = f"{sector_name} sector analysis"
        
        return analysis
