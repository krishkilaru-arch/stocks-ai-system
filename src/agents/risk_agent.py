"""Risk Management Agent - Analyzes portfolio risk, VaR, correlations, and regulatory compliance."""
from typing import Dict, Any, List
from datetime import date, timedelta
from src.agents.base_agent import BaseAgent
from src.data.loaders import YahooFinanceLoader
import numpy as np
import yfinance as yf


class RiskAgent(BaseAgent):
    """Agent specializing in risk analysis and portfolio risk management."""
    
    def __init__(self):
        super().__init__(
            name="Risk Management Agent",
            description="Analyzes portfolio risk, VaR, correlations, concentration risk, and regulatory compliance"
        )
        self.data_loader = YahooFinanceLoader()
    
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
        signals = {
            "symbol": symbol,
            "date": as_of_date.isoformat()
        }
        
        # Get company info
        company = self.data_loader.load_company_info(symbol)
        if company:
            signals["company_name"] = company.company_name
            signals["sector"] = company.sector
            signals["industry"] = company.industry
        
        # Get price history for volatility and VaR calculation (1 year)
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if not hist.empty and len(hist) > 20:
                prices = hist['Close'].values
                returns = np.diff(prices) / prices[:-1]
                
                # Volatility (annualized)
                daily_vol = np.std(returns)
                annual_vol = daily_vol * np.sqrt(252)
                signals["volatility"] = float(annual_vol)
                signals["daily_volatility"] = float(daily_vol)
                
                # Returns for VaR calculation
                signals["returns"] = returns.tolist()
                signals["current_price"] = float(prices[-1])
                
                # Downside deviation (for Sortino ratio)
                negative_returns = returns[returns < 0]
                if len(negative_returns) > 0:
                    downside_deviation = np.std(negative_returns) * np.sqrt(252)
                    signals["downside_deviation"] = float(downside_deviation)
                
                # Maximum drawdown
                cumulative = np.cumprod(1 + returns)
                running_max = np.maximum.accumulate(cumulative)
                drawdown = (cumulative - running_max) / running_max
                signals["max_drawdown"] = float(np.min(drawdown))
                
        except Exception as e:
            signals["price_data_note"] = f"Limited price history: {str(e)[:100]}"
        
        # Get market data (S&P 500) for beta and correlation
        try:
            spy = yf.Ticker("SPY")
            spy_hist = spy.history(period="1y")
            
            if not spy_hist.empty and len(spy_hist) > 20 and "returns" in signals:
                spy_prices = spy_hist['Close'].values
                spy_returns = np.diff(spy_prices) / spy_prices[:-1]
                
                # Align lengths
                min_len = min(len(returns), len(spy_returns))
                stock_returns = returns[-min_len:]
                market_returns = spy_returns[-min_len:]
                
                # Calculate correlation
                correlation = np.corrcoef(stock_returns, market_returns)[0, 1]
                signals["market_correlation"] = float(correlation)
                
                # Calculate beta
                market_variance = np.var(market_returns)
                covariance = np.cov(stock_returns, market_returns)[0, 1]
                beta = covariance / market_variance if market_variance > 0 else 1.0
                signals["beta"] = float(beta)
                
        except Exception as e:
            signals["market_data_note"] = f"Limited market data: {str(e)[:100]}"
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risk signals."""
        analysis = {}
        
        # Volatility assessment
        if signals.get("volatility"):
            vol = signals["volatility"]
            if vol > 0.5:
                analysis["volatility_level"] = f"very high ({vol:.1%} annualized)"
                analysis["volatility_risk"] = "extreme price swings expected"
            elif vol > 0.35:
                analysis["volatility_level"] = f"high ({vol:.1%} annualized)"
                analysis["volatility_risk"] = "significant price fluctuations likely"
            elif vol > 0.20:
                analysis["volatility_level"] = f"moderate ({vol:.1%} annualized)"
                analysis["volatility_risk"] = "normal market volatility"
            else:
                analysis["volatility_level"] = f"low ({vol:.1%} annualized)"
                analysis["volatility_risk"] = "stable, lower risk"
        
        # VaR calculation (95% confidence, 1-day)
        if signals.get("returns") and len(signals["returns"]) > 0:
            returns = np.array(signals["returns"])
            var_95 = np.percentile(returns, 5)  # 5th percentile
            var_99 = np.percentile(returns, 1)  # 1st percentile (tail risk)
            
            analysis["var_95_1day_pct"] = f"{var_95:.2%}"
            analysis["var_99_1day_pct"] = f"{var_99:.2%}"
            analysis["var_interpretation"] = f"95% confidence: daily loss won't exceed {abs(var_95):.1%}"
            
            # Expected shortfall (CVaR) - average loss beyond VaR
            tail_losses = returns[returns <= var_95]
            if len(tail_losses) > 0:
                cvar_95 = np.mean(tail_losses)
                analysis["cvar_95"] = f"{cvar_95:.2%}"
                analysis["tail_risk"] = f"If VaR breached, expected loss: {abs(cvar_95):.1%}"
        
        # Maximum drawdown assessment
        if signals.get("max_drawdown"):
            max_dd = signals["max_drawdown"]
            analysis["max_drawdown"] = f"{max_dd:.1%}"
            if max_dd < -0.5:
                analysis["drawdown_risk"] = "severe historical drawdowns (>50%)"
            elif max_dd < -0.3:
                analysis["drawdown_risk"] = "significant historical drawdowns (30-50%)"
            elif max_dd < -0.15:
                analysis["drawdown_risk"] = "moderate historical drawdowns (15-30%)"
            else:
                analysis["drawdown_risk"] = "limited historical drawdowns (<15%)"
        
        # Beta assessment (market sensitivity)
        if signals.get("beta"):
            beta = signals["beta"]
            analysis["beta"] = f"{beta:.2f}"
            if beta > 1.5:
                analysis["market_sensitivity"] = "very high (1.5x+ market moves)"
                analysis["market_risk"] = "amplifies market volatility significantly"
            elif beta > 1.2:
                analysis["market_sensitivity"] = "high (1.2-1.5x market moves)"
                analysis["market_risk"] = "more volatile than market"
            elif beta > 0.8:
                analysis["market_sensitivity"] = "moderate (0.8-1.2x market moves)"
                analysis["market_risk"] = "tracks market closely"
            elif beta > 0:
                analysis["market_sensitivity"] = "low (<0.8x market moves)"
                analysis["market_risk"] = "defensive, less volatile than market"
            else:
                analysis["market_sensitivity"] = "negative beta (hedge)"
                analysis["market_risk"] = "moves opposite to market"
        
        # Correlation assessment (diversification benefit)
        if signals.get("market_correlation"):
            corr = signals["market_correlation"]
            analysis["market_correlation"] = f"{corr:.2f}"
            if corr > 0.8:
                analysis["diversification_benefit"] = "very low (highly correlated)"
            elif corr > 0.5:
                analysis["diversification_benefit"] = "low (correlated)"
            elif corr > 0.2:
                analysis["diversification_benefit"] = "moderate"
            elif corr > -0.2:
                analysis["diversification_benefit"] = "high (uncorrelated)"
            else:
                analysis["diversification_benefit"] = "very high (negative correlation, hedge)"
        
        # Downside risk (for Sortino ratio)
        if signals.get("downside_deviation"):
            dd = signals["downside_deviation"]
            analysis["downside_deviation"] = f"{dd:.1%}"
            analysis["downside_focus"] = "measures only negative return volatility"
        
        # Risk summary
        risk_factors = []
        if signals.get("volatility", 0) > 0.35:
            risk_factors.append("High volatility")
        if signals.get("beta", 1.0) > 1.3:
            risk_factors.append("High market sensitivity")
        if signals.get("max_drawdown", 0) < -0.3:
            risk_factors.append("Severe historical drawdowns")
        
        if risk_factors:
            analysis["key_risk_factors"] = risk_factors
        else:
            analysis["key_risk_factors"] = ["Moderate risk profile"]
        
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
