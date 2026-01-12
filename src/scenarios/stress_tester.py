"""Scenario Analysis and Stress Testing."""
from typing import Dict, Any, List, Optional
from datetime import date, timedelta
from dataclasses import dataclass
import numpy as np
from src.agents.meta_supervisor import MetaSupervisor
from src.portfolio.portfolio_analyzer import PortfolioAnalyzer, PortfolioPosition


@dataclass
class StressScenario:
    """Defines a stress testing scenario."""
    name: str
    description: str
    market_shock: float  # Market decline percentage
    volatility_increase: float  # Volatility multiplier
    correlation_increase: float  # Correlation increase
    sector_impacts: Dict[str, float]  # Sector-specific impacts


@dataclass
class StressTestResult:
    """Results from a stress test."""
    scenario_name: str
    portfolio_value_before: float
    portfolio_value_after: float
    portfolio_loss: float
    portfolio_loss_pct: float
    var_95: float
    var_99: float
    worst_case_loss: float
    recovery_time_days: Optional[int] = None


class StressTester:
    """Stress testing and scenario analysis framework."""
    
    def __init__(self):
        self.meta_supervisor = MetaSupervisor()
        self.portfolio_analyzer = PortfolioAnalyzer()
    
    def run_stress_test(
        self,
        positions: List[PortfolioPosition],
        scenario: StressScenario,
        as_of_date: Optional[date] = None
    ) -> StressTestResult:
        """
        Run a stress test on a portfolio.
        
        Args:
            positions: Portfolio positions
            scenario: Stress scenario to apply
            as_of_date: Analysis date
        
        Returns:
            StressTestResult with impact analysis
        """
        if as_of_date is None:
            as_of_date = date.today()
        
        # Get baseline portfolio value
        portfolio_value_before = sum(
            p.current_value if p.current_value else 100000 * p.weight
            for p in positions
        )
        
        # Apply stress scenario
        stressed_returns = []
        for position in positions:
            # Get base prediction
            try:
                prediction = self.meta_supervisor.generate_prediction(
                    position.symbol, as_of_date
                )
                base_return = prediction.predicted_return
            except:
                base_return = 0.0
            
            # Apply market shock
            stressed_return = base_return - scenario.market_shock
            
            # Apply sector-specific impact
            company_info = self.meta_supervisor.agents["sector"].data_loader.get_company_info(position.symbol)
            if company_info and company_info.sector in scenario.sector_impacts:
                stressed_return -= scenario.sector_impacts[company_info.sector]
            
            stressed_returns.append(stressed_return * position.weight)
        
        # Calculate portfolio impact
        portfolio_return_after = sum(stressed_returns)
        portfolio_value_after = portfolio_value_before * (1 + portfolio_return_after / 100)
        portfolio_loss = portfolio_value_before - portfolio_value_after
        portfolio_loss_pct = (portfolio_loss / portfolio_value_before) * 100
        
        # Calculate VaR
        var_95 = self._calculate_var(positions, scenario, confidence=0.95)
        var_99 = self._calculate_var(positions, scenario, confidence=0.99)
        
        # Worst case (99.9% confidence)
        worst_case = self._calculate_var(positions, scenario, confidence=0.999)
        
        return StressTestResult(
            scenario_name=scenario.name,
            portfolio_value_before=portfolio_value_before,
            portfolio_value_after=portfolio_value_after,
            portfolio_loss=portfolio_loss,
            portfolio_loss_pct=portfolio_loss_pct,
            var_95=var_95,
            var_99=var_99,
            worst_case_loss=worst_case
        )
    
    def _calculate_var(
        self,
        positions: List[PortfolioPosition],
        scenario: StressScenario,
        confidence: float = 0.95
    ) -> float:
        """Calculate Value at Risk for the scenario."""
        # Simplified VaR calculation
        # In production, would use full Monte Carlo simulation
        
        portfolio_value = sum(
            p.current_value if p.current_value else 100000 * p.weight
            for p in positions
        )
        
        # Estimate portfolio volatility under stress
        base_volatility = 0.15  # 15% base volatility
        stressed_volatility = base_volatility * scenario.volatility_increase
        
        # Calculate VaR using normal distribution approximation
        from scipy.stats import norm
        z_score = norm.ppf(1 - confidence)
        var = abs(z_score * stressed_volatility * portfolio_value)
        
        return var
    
    def run_monte_carlo_simulation(
        self,
        positions: List[PortfolioPosition],
        num_simulations: int = 10000,
        time_horizon_days: int = 30,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for portfolio.
        
        Args:
            positions: Portfolio positions
            num_simulations: Number of Monte Carlo simulations
            time_horizon_days: Time horizon for simulation
            as_of_date: Analysis date
        
        Returns:
            Simulation results with percentiles
        """
        if as_of_date is None:
            as_of_date = date.today()
        
        portfolio_value = sum(
            p.current_value if p.current_value else 100000 * p.weight
            for p in positions
        )
        
        # Get base returns and volatilities
        returns = []
        volatilities = []
        
        for position in positions:
            try:
                prediction = self.meta_supervisor.generate_prediction(position.symbol, as_of_date)
                returns.append(prediction.predicted_return)
                
                risk_signals = self.meta_supervisor.agents["risk"].collect_signals(
                    position.symbol, as_of_date
                )
                volatilities.append(risk_signals.get("volatility", 0.2))
            except:
                returns.append(0.0)
                volatilities.append(0.2)
        
        # Run Monte Carlo simulations
        np.random.seed(42)
        simulated_returns = []
        
        for _ in range(num_simulations):
            # Simulate returns for each position
            position_returns = []
            for i, position in enumerate(positions):
                # Random return based on predicted return and volatility
                simulated_return = np.random.normal(
                    returns[i] / 100,  # Convert to decimal
                    volatilities[i] / np.sqrt(252)  # Daily volatility
                )
                position_returns.append(simulated_return * position.weight)
            
            portfolio_return = sum(position_returns)
            simulated_returns.append(portfolio_return * 100)  # Convert back to percentage
        
        # Calculate statistics
        simulated_returns = np.array(simulated_returns)
        
        return {
            "mean_return": float(np.mean(simulated_returns)),
            "std_return": float(np.std(simulated_returns)),
            "percentile_5": float(np.percentile(simulated_returns, 5)),
            "percentile_25": float(np.percentile(simulated_returns, 25)),
            "percentile_50": float(np.percentile(simulated_returns, 50)),
            "percentile_75": float(np.percentile(simulated_returns, 75)),
            "percentile_95": float(np.percentile(simulated_returns, 95)),
            "percentile_99": float(np.percentile(simulated_returns, 99)),
            "var_95": float(np.percentile(simulated_returns, 5)) * portfolio_value / 100,
            "var_99": float(np.percentile(simulated_returns, 1)) * portfolio_value / 100
        }
    
    def create_standard_scenarios(self) -> List[StressScenario]:
        """Create standard stress testing scenarios."""
        return [
            StressScenario(
                name="Market Crash 2008",
                description="Similar to 2008 financial crisis",
                market_shock=30.0,
                volatility_increase=2.5,
                correlation_increase=0.3,
                sector_impacts={
                    "Financial Services": 40.0,
                    "Real Estate": 35.0,
                    "Consumer Cyclical": 25.0
                }
            ),
            StressScenario(
                name="COVID-19 Pandemic",
                description="Similar to March 2020 market crash",
                market_shock=20.0,
                volatility_increase=3.0,
                correlation_increase=0.4,
                sector_impacts={
                    "Travel & Leisure": 50.0,
                    "Energy": 30.0,
                    "Technology": -5.0  # Tech actually gained
                }
            ),
            StressScenario(
                name="Interest Rate Shock",
                description="Rapid interest rate increase",
                market_shock=15.0,
                volatility_increase=1.8,
                correlation_increase=0.2,
                sector_impacts={
                    "Real Estate": 25.0,
                    "Utilities": 20.0,
                    "Financial Services": 10.0
                }
            ),
            StressScenario(
                name="Inflation Spike",
                description="High inflation scenario",
                market_shock=10.0,
                volatility_increase=1.5,
                correlation_increase=0.15,
                sector_impacts={
                    "Consumer Staples": -5.0,  # Defensive
                    "Technology": 15.0,
                    "Energy": -10.0  # Benefits from inflation
                }
            )
        ]
