"""Events Agent - Analyzes market events, earnings, and news sentiment."""
from typing import Dict, Any
from datetime import date, timedelta
from src.agents.base_agent import BaseAgent
from src.data.loaders import DataLoader


class EventsAgent(BaseAgent):
    """Agent specializing in event-driven analysis."""
    
    def __init__(self):
        super().__init__(
            name="Events Agent",
            description="Analyzes earnings reports, news events, sentiment, and external factors affecting stocks"
        )
        self.data_loader = DataLoader()
    
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
        signals = {}
        
        # Get recent events
        recent_events = self.data_loader.get_recent_events(symbol, as_of_date, days=30)
        if recent_events:
            signals["recent_events"] = [
                {
                    "type": e.event_type,
                    "date": e.event_date.isoformat(),
                    "title": e.title,
                    "sentiment": e.sentiment_score,
                    "impact": e.impact_score
                }
                for e in recent_events
            ]
        
        # Get upcoming events
        upcoming_events = self.data_loader.get_upcoming_events(symbol, as_of_date, days=30)
        if upcoming_events:
            signals["upcoming_events"] = [
                {
                    "type": e.event_type,
                    "date": e.event_date.isoformat(),
                    "title": e.title
                }
                for e in upcoming_events
            ]
        
        # Get earnings data
        earnings = self.data_loader.get_earnings_data(symbol, as_of_date)
        if earnings:
            signals["earnings"] = {
                "last_earnings_date": earnings.get("last_date"),
                "last_eps": earnings.get("last_eps"),
                "expected_eps": earnings.get("expected_eps"),
                "surprise": earnings.get("surprise"),
                "next_earnings_date": earnings.get("next_date")
            }
        
        # Get news sentiment
        news_sentiment = self.data_loader.get_news_sentiment(symbol, as_of_date, days=7)
        if news_sentiment:
            signals["news_sentiment"] = {
                "avg_sentiment": news_sentiment.get("avg_sentiment"),
                "sentiment_trend": news_sentiment.get("trend"),
                "article_count": news_sentiment.get("count")
            }
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze event signals."""
        analysis = {}
        
        # Earnings analysis
        if "earnings" in signals:
            earnings = signals["earnings"]
            if earnings.get("surprise"):
                surprise = earnings["surprise"]
                if surprise > 0.1:
                    analysis["earnings_performance"] = "strong beat"
                elif surprise > 0.05:
                    analysis["earnings_performance"] = "beat"
                elif surprise < -0.1:
                    analysis["earnings_performance"] = "significant miss"
                elif surprise < -0.05:
                    analysis["earnings_performance"] = "miss"
                else:
                    analysis["earnings_performance"] = "in line"
        
        # News sentiment analysis
        if "news_sentiment" in signals:
            sentiment = signals["news_sentiment"]
            avg_sentiment = sentiment.get("avg_sentiment", 0)
            if avg_sentiment > 0.3:
                analysis["sentiment"] = "very positive"
            elif avg_sentiment > 0.1:
                analysis["sentiment"] = "positive"
            elif avg_sentiment < -0.3:
                analysis["sentiment"] = "very negative"
            elif avg_sentiment < -0.1:
                analysis["sentiment"] = "negative"
            else:
                analysis["sentiment"] = "neutral"
        
        # Event impact assessment
        if "recent_events" in signals:
            events = signals["recent_events"]
            high_impact_events = [e for e in events if e.get("impact", 0) > 0.7]
            if high_impact_events:
                analysis["recent_high_impact_events"] = len(high_impact_events)
                analysis["event_impact"] = "high"
            elif events:
                analysis["recent_high_impact_events"] = 0
                analysis["event_impact"] = "moderate"
            else:
                analysis["event_impact"] = "low"
        
        # Upcoming events
        if "upcoming_events" in signals:
            upcoming = signals["upcoming_events"]
            earnings_events = [e for e in upcoming if e.get("type") == "earnings"]
            if earnings_events:
                analysis["upcoming_earnings"] = True
                analysis["next_earnings_date"] = earnings_events[0].get("date")
            else:
                analysis["upcoming_earnings"] = False
        
        return analysis
