"""Technical Agent - Analyzes price patterns, momentum, and technical indicators."""
from typing import Dict, Any
from datetime import date
from src.agents.base_agent import BaseAgent
from src.data.loaders import YahooFinanceLoader


class TechnicalAgent(BaseAgent):
    """Agent specializing in technical analysis."""
    
    def __init__(self):
        super().__init__(
            name="Technical Agent",
            description="Analyzes price patterns, momentum, volume, and technical indicators"
        )
        self.data_loader = YahooFinanceLoader()
    
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
        technical = self.data_loader.load_technical(symbol, as_of_date)
        if technical:
            signals.update({
                "symbol": symbol,
                "date": as_of_date.isoformat(),
                "current_price": technical.close_price,
                "open_price": technical.open_price,
                "high_price": technical.high_price,
                "low_price": technical.low_price,
                "volume": technical.volume,
                "sma_50": technical.sma_50,
                "sma_200": technical.sma_200,
                "rsi": technical.rsi,
                "macd": technical.macd,
                "bollinger_upper": technical.bollinger_upper,
                "bollinger_lower": technical.bollinger_lower
            })
        
        # Get company info
        company = self.data_loader.load_company_info(symbol)
        if company:
            signals["company_name"] = company.company_name
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical signals."""
        analysis = {}
        
        # Trend analysis (Golden/Death Cross)
        if signals.get("sma_50") and signals.get("sma_200"):
            sma50 = signals["sma_50"]
            sma200 = signals["sma_200"]
            current_price = signals.get("current_price")
            
            if sma50 > sma200:
                analysis["trend"] = "bullish (Golden Cross - SMA50 > SMA200)"
            else:
                analysis["trend"] = "bearish (Death Cross - SMA50 < SMA200)"
            
            if current_price:
                if current_price > sma50 > sma200:
                    analysis["trend_strength"] = "strong uptrend (price > SMA50 > SMA200)"
                elif current_price < sma50 < sma200:
                    analysis["trend_strength"] = "strong downtrend (price < SMA50 < SMA200)"
                else:
                    analysis["trend_strength"] = "mixed signals / consolidation"
                
                # Price vs moving averages
                sma50_distance = ((current_price / sma50) - 1) * 100 if sma50 else 0
                sma200_distance = ((current_price / sma200) - 1) * 100 if sma200 else 0
                analysis["price_vs_sma50"] = f"{sma50_distance:+.2f}%"
                analysis["price_vs_sma200"] = f"{sma200_distance:+.2f}%"
        
        # RSI analysis (momentum indicator)
        if signals.get("rsi"):
            rsi = signals["rsi"]
            if rsi > 70:
                analysis["momentum"] = f"overbought (RSI={rsi:.1f} > 70)"
            elif rsi < 30:
                analysis["momentum"] = f"oversold (RSI={rsi:.1f} < 30)"
            elif rsi > 50:
                analysis["momentum"] = f"bullish momentum (RSI={rsi:.1f})"
            else:
                analysis["momentum"] = f"bearish momentum (RSI={rsi:.1f})"
        
        # MACD analysis
        if signals.get("macd"):
            macd = signals["macd"]
            if macd > 0.5:
                analysis["macd_signal"] = "strong bullish (MACD > 0.5)"
            elif macd > 0:
                analysis["macd_signal"] = "bullish (MACD > 0)"
            elif macd < -0.5:
                analysis["macd_signal"] = "strong bearish (MACD < -0.5)"
            else:
                analysis["macd_signal"] = "bearish (MACD < 0)"
        
        # Bollinger Bands analysis (volatility)
        if signals.get("current_price") and signals.get("bollinger_upper") and signals.get("bollinger_lower"):
            price = signals["current_price"]
            upper = signals["bollinger_upper"]
            lower = signals["bollinger_lower"]
            
            if price > upper:
                analysis["bollinger_position"] = "above upper band (overbought, possible reversal)"
            elif price < lower:
                analysis["bollinger_position"] = "below lower band (oversold, possible reversal)"
            else:
                # Calculate position within bands
                band_width = upper - lower
                position_pct = ((price - lower) / band_width * 100) if band_width > 0 else 50
                analysis["bollinger_position"] = f"within bands ({position_pct:.0f}% from lower)"
        
        # Intraday price action
        if signals.get("open_price") and signals.get("close_price") and signals.get("high_price") and signals.get("low_price"):
            open_price = signals["open_price"]
            close_price = signals["close_price"]
            high_price = signals["high_price"]
            low_price = signals["low_price"]
            
            day_change = ((close_price / open_price) - 1) * 100 if open_price else 0
            day_range = ((high_price - low_price) / open_price * 100) if open_price else 0
            
            analysis["intraday_performance"] = f"{day_change:+.2f}% (range: {day_range:.2f}%)"
        
        return analysis
