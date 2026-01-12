"""Risk Management Agent - Analyzes portfolio risk, VaR, correlations, and regulatory compliance."""
from typing import Dict, Any, List
from datetime import date
from src.agents.base_agent import BaseAgent
from src.data.loaders import DataLoader
import numpy as np


class RiskAgent(BaseAgent):
    """Agent specializing in risk analysis and portfolio risk management."""
    
    def __init__(self):
        super().__init__(
            name="Risk Management Agent",
            description="Analyzes portfolio risk, VaR, correlations, concentration risk, and regulatory compliance"
        )
        self.data_loader = DataLoader()
    
    def get_system_prompt(self) -> str:
        return """You are a risk management specialist focusing on portfolio risk analysis.

Your expertise includes:
- Value at Risk (VaR) calculations
- Portfolio correlation analysis
- Concentration risk assessment
- Regulatory risk (Basel, Solvency II, CCAR)
- Stress testing and scenario analysis
- Risk-adjusted returns (Sharpe, Sortino ratios)
- Tail risk and extreme event analysis

When making predictions, consider:
1. Downside risk and potential losses
2. Correlation with market and portfolio
3. Concentration risk in sectors/geographies
4. Regulatory capital requirements
5. Stress scenarios and tail events
6. Risk-adjusted return expectations

Provide clear risk assessment with both quantitative metrics and qualitative risk factors."""
    
    def collect_signals(self, symbol: str, as_of_date: date) -> Dict[str, Any]:
        """Collect risk-related signals."""
        signals = {}
        
        # Get price history for volatility calculation
        price_history = self.data_loader.get_price_history(symbol, as_of_date, days=252)  # 1 year
        if price_history and len(price_history) > 0:
            prices = [p.close_price for p in price_history]
            returns = np.diff(prices) / prices[:-1]
            
            signals["volatility"] = float(np.std(returns) * np.sqrt(252))  # Annualized
            signals["returns"] = returns.tolist()
            signals["price_history"] = prices
        
        # Get current price
        current_price = self.data_loader.get_current_price(symbol)
        if current_price:
            signals["current_price"] = current_price
        
        # Get company info for sector/industry
        company_info = self.data_loader.get_company_info(symbol)
        if company_info:
            signals["sector"] = company_info.sector
            signals["industry"] = company_info.industry
        
        # Get market data (S&P 500 for correlation)
        market_data = self.data_loader.get_price_history("SPY", as_of_date, days=252)
        if market_data and len(market_data) > 0 and "returns" in signals:
            market_prices = [p.close_price for p in market_data]
            market_returns = np.diff(market_prices) / market_prices[:-1]
            
            # Calculate correlation
            if len(returns) == len(market_returns):
                correlation = np.corrcoef(returns, market_returns)[0, 1]
                signals["market_correlation"] = float(correlation)
                signals["beta"] = float(correlation * signals["volatility"] / np.std(market_returns) / np.sqrt(252))
        
        # Get sector peers for concentration analysis
        if company_info:
            peers = self.data_loader.get_peer_companies(symbol)
            if peers:
                signals["peer_count"] = len(peers)
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risk signals."""
        analysis = {}
        
        # Volatility assessment
        if signals.get("volatility"):
            vol = signals["volatility"]
            if vol > 0.4:
                analysis["volatility_level"] = "very high"
            elif vol > 0.3:
                analysis["volatility_level"] = "high"
            elif vol > 0.2:
                analysis["volatility_level"] = "moderate"
            else:
                analysis["volatility_level"] = "low"
        
        # VaR calculation (95% confidence, 1-day)
        if signals.get("returns") and len(signals["returns"]) > 0:
            returns = np.array(signals["returns"])
            var_95 = np.percentile(returns, 5)
            analysis["var_95_1day"] = float(var_95)
            
            # Convert to dollar terms if we have current price
            if signals.get("current_price"):
                analysis["var_95_1day_usd"] = float(var_95 * signals["current_price"])
        
        # Beta assessment
        if signals.get("beta"):
            beta = signals["beta"]
            if beta > 1.2:
                analysis["market_sensitivity"] = "high (aggressive)"
            elif beta > 0.8:
                analysis["market_sensitivity"] = "moderate"
            elif beta > 0:
                analysis["market_sensitivity"] = "low (defensive)"
            else:
                analysis["market_sensitivity"] = "negative (hedge)"
        
        # Correlation assessment
        if signals.get("market_correlation"):
            corr = signals["market_correlation"]
            if corr > 0.7:
                analysis["diversification_benefit"] = "low (highly correlated)"
            elif corr > 0.3:
                analysis["diversification_benefit"] = "moderate"
            else:
                analysis["diversification_benefit"] = "high (low correlation)"
        
        # Concentration risk
        if signals.get("sector"):
            # Simplified - would need portfolio context
            analysis["concentration_risk"] = "requires portfolio context"
        
        # Regulatory risk indicators
        analysis["regulatory_considerations"] = [
            "Basel III capital requirements",
            "Stress testing compliance",
            "Model governance requirements"
        ]
        
        return analysis
    
    def calculate_portfolio_risk(
        self,
        symbols: List[str],
        weights: List[float],
        as_of_date: date
    ) -> Dict[str, Any]:
        """Calculate portfolio-level risk metrics."""
        if len(symbols) != len(weights):
            raise ValueError("Symbols and weights must have same length")
        
        portfolio_returns = []
        portfolio_volatilities = []
        correlations = []
        
        for symbol in symbols:
            signals = self.collect_signals(symbol, as_of_date)
            if signals.get("returns"):
                portfolio_returns.append(signals["returns"])
                portfolio_volatilities.append(signals.get("volatility", 0))
        
        if len(portfolio_returns) < 2:
            return {"error": "Need at least 2 assets for portfolio risk"}
        
        # Calculate portfolio volatility
        # Simplified - would need full covariance matrix
        weighted_vol = sum(w * v for w, v in zip(weights, portfolio_volatilities))
        
        return {
            "portfolio_volatility": weighted_vol,
            "diversification_ratio": weighted_vol / max(portfolio_volatilities) if portfolio_volatilities else 1.0,
            "concentration_risk": max(weights)  # Max weight indicates concentration
        }
