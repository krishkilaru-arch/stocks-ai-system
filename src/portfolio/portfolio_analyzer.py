"""Portfolio-level analysis and optimization."""
from typing import List, Dict, Any, Optional
from datetime import date
from dataclasses import dataclass
from src.agents.meta_supervisor import MetaSupervisor
from src.agents.risk_agent import RiskAgent
import numpy as np


@dataclass
class PortfolioPosition:
    """Represents a position in a portfolio."""
    symbol: str
    weight: float  # Portfolio weight (0.0 to 1.0)
    current_value: Optional[float] = None


@dataclass
class PortfolioAnalysis:
    """Comprehensive portfolio analysis."""
    total_positions: int
    predicted_portfolio_return: float
    portfolio_volatility: float
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    concentration_risk: float
    sector_diversification: Dict[str, float]
    risk_adjusted_prediction: float
    individual_predictions: Dict[str, Dict[str, Any]]


class PortfolioAnalyzer:
    """Analyzes portfolios using multi-agent predictions."""
    
    def __init__(self):
        self.meta_supervisor = MetaSupervisor()
        self.risk_agent = RiskAgent()
    
    def analyze_portfolio(
        self,
        positions: List[PortfolioPosition],
        as_of_date: Optional[date] = None,
        target_date: Optional[date] = None,
        risk_free_rate: float = 0.02  # 2% annual risk-free rate
    ) -> PortfolioAnalysis:
        """
        Analyze a portfolio using multi-agent predictions.
        
        Args:
            positions: List of portfolio positions
            as_of_date: Analysis date
            target_date: Target prediction date
            risk_free_rate: Risk-free rate for Sharpe ratio
        
        Returns:
            PortfolioAnalysis with comprehensive metrics
        """
        if as_of_date is None:
            from datetime import date
            as_of_date = date.today()
        if target_date is None:
            from datetime import timedelta
            target_date = as_of_date + timedelta(days=30)
        
        # Normalize weights
        total_weight = sum(p.weight for p in positions)
        if total_weight != 1.0:
            positions = [
                PortfolioPosition(p.symbol, p.weight / total_weight, p.current_value)
                for p in positions
            ]
        
        # Get predictions for each position
        individual_predictions = {}
        weighted_returns = []
        volatilities = []
        
        for position in positions:
            try:
                prediction = self.meta_supervisor.generate_prediction(
                    position.symbol, as_of_date, target_date
                )
                
                # Get risk metrics
                risk_signals = self.risk_agent.collect_signals(position.symbol, as_of_date)
                volatility = risk_signals.get("volatility", 0.2)  # Default 20%
                
                individual_predictions[position.symbol] = {
                    "predicted_return": prediction.predicted_return,
                    "confidence": prediction.confidence_score,
                    "volatility": volatility,
                    "risk_adjusted_return": prediction.predicted_return / volatility if volatility > 0 else 0
                }
                
                weighted_returns.append(position.weight * prediction.predicted_return)
                volatilities.append(volatility)
                
            except Exception as e:
                print(f"Warning: Failed to get prediction for {position.symbol}: {e}")
                continue
        
        # Calculate portfolio metrics
        portfolio_return = sum(weighted_returns)
        
        # Portfolio volatility (simplified - would need correlation matrix)
        portfolio_volatility = np.sqrt(sum(w**2 * v**2 for w, v in zip(
            [p.weight for p in positions[:len(volatilities)]],
            volatilities
        )))
        
        # Sharpe ratio
        sharpe_ratio = None
        if portfolio_volatility > 0:
            sharpe_ratio = (portfolio_return - risk_free_rate * 30/365) / portfolio_volatility
        
        # Sortino ratio (downside deviation)
        sortino_ratio = None
        if portfolio_volatility > 0:
            # Simplified - would need actual downside deviation
            sortino_ratio = portfolio_return / portfolio_volatility
        
        # Concentration risk (max weight)
        concentration_risk = max(p.weight for p in positions)
        
        # Sector diversification
        sector_weights = {}
        for position in positions:
            company_info = self.risk_agent.data_loader.get_company_info(position.symbol)
            if company_info:
                sector = company_info.sector
                sector_weights[sector] = sector_weights.get(sector, 0) + position.weight
        
        # Risk-adjusted prediction
        risk_adjusted = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else portfolio_return
        
        return PortfolioAnalysis(
            total_positions=len(positions),
            predicted_portfolio_return=portfolio_return,
            portfolio_volatility=portfolio_volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            concentration_risk=concentration_risk,
            sector_diversification=sector_weights,
            risk_adjusted_prediction=risk_adjusted,
            individual_predictions=individual_predictions
        )
    
    def optimize_portfolio(
        self,
        candidate_symbols: List[str],
        target_return: Optional[float] = None,
        max_positions: int = 10,
        as_of_date: Optional[date] = None
    ) -> List[PortfolioPosition]:
        """
        Optimize portfolio allocation (simplified version).
        
        In production, would use Markowitz optimization or similar.
        """
        if as_of_date is None:
            from datetime import date
            as_of_date = date.today()
        
        # Get predictions for all candidates
        predictions = {}
        for symbol in candidate_symbols[:max_positions]:
            try:
                pred = self.meta_supervisor.generate_prediction(symbol, as_of_date)
                risk_signals = self.risk_agent.collect_signals(symbol, as_of_date)
                volatility = risk_signals.get("volatility", 0.2)
                
                # Risk-adjusted score
                risk_adjusted_score = pred.predicted_return / volatility if volatility > 0 else pred.predicted_return
                risk_adjusted_score *= pred.confidence_score  # Weight by confidence
                
                predictions[symbol] = risk_adjusted_score
            except Exception as e:
                print(f"Warning: Failed to analyze {symbol}: {e}")
                continue
        
        # Sort by risk-adjusted score
        sorted_symbols = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
        
        # Equal weight allocation (simplified)
        # In production, would optimize weights based on correlation and risk
        positions = [
            PortfolioPosition(symbol, 1.0 / len(sorted_symbols))
            for symbol, _ in sorted_symbols
        ]
        
        return positions
