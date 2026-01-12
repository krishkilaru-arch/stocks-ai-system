"""Technical Agent - Analyzes price patterns, momentum, and technical indicators."""
from typing import Dict, Any
from datetime import date
from src.agents.base_agent import BaseAgent
from src.data.loaders import DataLoader


class TechnicalAgent(BaseAgent):
    """Agent specializing in technical analysis."""
    
    def __init__(self):
        super().__init__(
            name="Technical Agent",
            description="Analyzes price patterns, momentum, volume, and technical indicators"
        )
        self.data_loader = DataLoader()
    
    def get_system_prompt(self) -> str:
        return """You are a technical analyst specializing in price action and chart patterns.

Your expertise includes:
- Price patterns (support, resistance, trends, breakouts)
- Moving averages (SMA, EMA)
- Momentum indicators (RSI, MACD, Stochastic)
- Volume analysis
- Bollinger Bands and volatility
- Chart patterns (head and shoulders, triangles, etc.)
- Trend identification and strength

When making predictions, consider:
1. Current trend direction and strength
2. Support and resistance levels
3. Momentum indicators (overbought/oversold conditions)
4. Volume patterns and confirmation
5. Moving average relationships
6. Breakout or breakdown patterns
7. Historical price action at similar technical setups

Provide reasoning based on technical analysis principles and chart patterns."""
    
    def collect_signals(self, symbol: str, as_of_date: date) -> Dict[str, Any]:
        """Collect technical signals."""
        signals = {}
        
        # Get technical indicators
        technical = self.data_loader.get_technical_indicators(symbol, as_of_date)
        if technical:
            signals.update({
                "current_price": technical.close_price,
                "sma_50": technical.sma_50,
                "sma_200": technical.sma_200,
                "rsi": technical.rsi,
                "macd": technical.macd,
                "volume": technical.volume,
                "bollinger_upper": technical.bollinger_upper,
                "bollinger_lower": technical.bollinger_lower
            })
        
        # Get price history for pattern analysis
        price_history = self.data_loader.get_price_history(symbol, as_of_date, days=90)
        if price_history:
            signals["price_history"] = {
                "highs": [p.high_price for p in price_history],
                "lows": [p.low_price for p in price_history],
                "closes": [p.close_price for p in price_history],
                "volumes": [p.volume for p in price_history]
            }
        
        # Get support/resistance levels
        support_resistance = self.data_loader.get_support_resistance_levels(symbol, as_of_date)
        if support_resistance:
            signals["support_resistance"] = support_resistance
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical signals."""
        analysis = {}
        
        # Trend analysis
        if signals.get("sma_50") and signals.get("sma_200"):
            sma50 = signals["sma_50"]
            sma200 = signals["sma_200"]
            current_price = signals.get("current_price")
            
            if sma50 > sma200:
                analysis["trend"] = "uptrend"
            else:
                analysis["trend"] = "downtrend"
            
            if current_price:
                if current_price > sma50 > sma200:
                    analysis["trend_strength"] = "strong uptrend"
                elif current_price < sma50 < sma200:
                    analysis["trend_strength"] = "strong downtrend"
                else:
                    analysis["trend_strength"] = "mixed/consolidation"
        
        # RSI analysis
        if signals.get("rsi"):
            rsi = signals["rsi"]
            if rsi > 70:
                analysis["momentum"] = "overbought"
            elif rsi < 30:
                analysis["momentum"] = "oversold"
            elif rsi > 50:
                analysis["momentum"] = "bullish"
            else:
                analysis["momentum"] = "bearish"
        
        # MACD analysis
        if signals.get("macd"):
            macd = signals["macd"]
            if macd > 0:
                analysis["macd_signal"] = "bullish"
            else:
                analysis["macd_signal"] = "bearish"
        
        # Bollinger Bands analysis
        if signals.get("current_price") and signals.get("bollinger_upper") and signals.get("bollinger_lower"):
            price = signals["current_price"]
            upper = signals["bollinger_upper"]
            lower = signals["bollinger_lower"]
            
            if price > upper:
                analysis["bollinger_position"] = "above upper band (potentially overbought)"
            elif price < lower:
                analysis["bollinger_position"] = "below lower band (potentially oversold)"
            else:
                analysis["bollinger_position"] = "within bands"
        
        # Volume analysis
        if "price_history" in signals and signals["price_history"].get("volumes"):
            volumes = signals["price_history"]["volumes"]
            if len(volumes) >= 20:
                recent_avg_volume = sum(volumes[-5:]) / 5
                historical_avg_volume = sum(volumes[-20:]) / 20
                if recent_avg_volume > historical_avg_volume * 1.2:
                    analysis["volume_trend"] = "increasing"
                elif recent_avg_volume < historical_avg_volume * 0.8:
                    analysis["volume_trend"] = "decreasing"
                else:
                    analysis["volume_trend"] = "stable"
        
        return analysis
