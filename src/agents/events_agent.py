"""Events Agent - Analyzes market events, earnings, and news sentiment."""
from typing import Dict, Any
from datetime import date, timedelta
from src.agents.base_agent import BaseAgent
from src.data.loaders import YahooFinanceLoader
import yfinance as yf


class EventsAgent(BaseAgent):
    """Agent specializing in event-driven analysis."""
    
    def __init__(self):
        super().__init__(
            name="Events Agent",
            description="Analyzes earnings reports, news events, sentiment, and external factors affecting stocks"
        )
        self.data_loader = YahooFinanceLoader()
    
    def get_system_prompt(self) -> str:
        return """You are an event-driven analyst specializing in how specific events affect stock prices.

Your expertise includes:
- Earnings reports and guidance
- News sentiment analysis
- M&A activity and corporate actions
- Regulatory changes and policy impacts
- Product launches and business developments
- Management changes and strategic shifts
- External shocks and black swan events

When making predictions, consider:
1. Recent earnings performance vs. expectations
2. Management guidance and forward-looking statements
3. News sentiment and media coverage
4. Upcoming events (earnings dates, product launches, etc.)
5. Historical impact of similar events
6. Event significance and market reaction patterns
7. Sector-wide events affecting multiple companies

Provide reasoning that connects specific events to expected price movements."""
    
    def collect_signals(self, symbol: str, as_of_date: date) -> Dict[str, Any]:
        """Collect event-related signals."""
        signals = {
            "symbol": symbol,
            "date": as_of_date.isoformat()
        }
        
        # Get company info
        company = self.data_loader.load_company_info(symbol)
        if company:
            signals["company_name"] = company.company_name
            signals["sector"] = company.sector
        
        # Get earnings calendar and history from Yahoo Finance
        try:
            ticker = yf.Ticker(symbol)
            
            # Earnings calendar
            calendar = ticker.calendar
            if calendar is not None and not calendar.empty:
                # Calendar is a DataFrame with earnings dates
                if 'Earnings Date' in calendar.index:
                    earnings_dates = calendar.loc['Earnings Date']
                    if isinstance(earnings_dates, (list, tuple)) and len(earnings_dates) > 0:
                        signals["next_earnings_date"] = str(earnings_dates[0])
                    elif hasattr(earnings_dates, 'values'):
                        signals["next_earnings_date"] = str(earnings_dates.values[0])
            
            # Recent earnings history
            earnings_history = ticker.earnings_dates
            if earnings_history is not None and not earnings_history.empty:
                # Get last 4 earnings
                recent_earnings = earnings_history.head(4)
                if 'Surprise(%)' in recent_earnings.columns:
                    surprises = recent_earnings['Surprise(%)'].dropna()
                    if not surprises.empty:
                        signals["recent_earnings_surprises"] = surprises.tolist()
                        signals["avg_earnings_surprise"] = float(surprises.mean())
            
            # News (from Yahoo Finance)
            news = ticker.news
            if news:
                signals["recent_news_count"] = len(news)
                signals["recent_news_titles"] = [n.get('title', '')[:80] for n in news[:5]]
            
        except Exception as e:
            signals["events_data_note"] = f"Limited events data: {str(e)[:100]}"
        
        # Get fundamental metrics for earnings quality
        fundamentals = self.data_loader.load_fundamentals(symbol, as_of_date)
        if fundamentals:
            signals["last_reported_eps"] = fundamentals.eps
            signals["pe_ratio"] = fundamentals.pe_ratio
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze event signals."""
        analysis = {}
        
        # Earnings surprise pattern analysis
        if signals.get("recent_earnings_surprises"):
            surprises = signals["recent_earnings_surprises"]
            avg_surprise = signals.get("avg_earnings_surprise", 0)
            
            if avg_surprise > 5:
                analysis["earnings_track_record"] = "consistently beating (avg +5%+)"
            elif avg_surprise > 0:
                analysis["earnings_track_record"] = "generally positive surprises"
            elif avg_surprise < -5:
                analysis["earnings_track_record"] = "consistently missing (avg -5%+)"
            elif avg_surprise < 0:
                analysis["earnings_track_record"] = "generally negative surprises"
            else:
                analysis["earnings_track_record"] = "meeting expectations"
            
            # Check consistency
            positive_surprises = sum(1 for s in surprises if s > 0)
            consistency = (positive_surprises / len(surprises) * 100) if surprises else 50
            analysis["earnings_consistency"] = f"{consistency:.0f}% positive surprises"
        
        # Earnings timing assessment
        if signals.get("next_earnings_date"):
            analysis["upcoming_catalyst"] = f"Earnings on {signals['next_earnings_date']}"
            analysis["catalyst_proximity"] = "near-term catalyst"
        else:
            analysis["catalyst_proximity"] = "no immediate earnings catalyst"
        
        # News coverage assessment
        if signals.get("recent_news_count"):
            news_count = signals["recent_news_count"]
            if news_count > 10:
                analysis["media_coverage"] = "high media attention (10+ recent articles)"
            elif news_count > 5:
                analysis["media_coverage"] = "moderate media coverage (5-10 articles)"
            elif news_count > 0:
                analysis["media_coverage"] = "low media coverage (1-5 articles)"
            else:
                analysis["media_coverage"] = "minimal media attention"
        
        # Recent news headlines (for context)
        if signals.get("recent_news_titles"):
            analysis["recent_headlines"] = signals["recent_news_titles"][:3]  # Top 3
        
        return analysis
