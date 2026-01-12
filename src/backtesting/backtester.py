"""Backtesting framework for validating agent predictions."""
from typing import List, Dict, Any, Optional
from datetime import date, timedelta
from dataclasses import dataclass
from src.agents.meta_supervisor import MetaSupervisor
from src.data.loaders import DataLoader
import pandas as pd


@dataclass
class BacktestResult:
    """Results from a backtest run."""
    symbol: str
    prediction_date: date
    target_date: date
    predicted_return: float
    actual_return: float
    error: float
    absolute_error: float
    direction_correct: bool
    confidence_score: float


@dataclass
class BacktestSummary:
    """Summary statistics from backtesting."""
    total_predictions: int
    mean_absolute_error: float
    root_mean_squared_error: float
    direction_accuracy: float  # Percentage of correct direction predictions
    mean_error: float
    sharpe_ratio: Optional[float] = None
    best_prediction: Optional[BacktestResult] = None
    worst_prediction: Optional[BacktestResult] = None


class Backtester:
    """Backtesting framework for validating predictions."""
    
    def __init__(self):
        self.meta_supervisor = MetaSupervisor()
        self.data_loader = DataLoader()
    
    def backtest_prediction(
        self,
        symbol: str,
        prediction_date: date,
        target_date: date
    ) -> Optional[BacktestResult]:
        """
        Backtest a single prediction.
        
        Args:
            symbol: Stock symbol
            prediction_date: Date when prediction was made
            target_date: Target date for prediction
        
        Returns:
            BacktestResult with actual vs predicted performance
        """
        # Generate prediction (as if we were at prediction_date)
        try:
            prediction = self.meta_supervisor.generate_prediction(
                symbol, prediction_date, target_date
            )
        except Exception as e:
            print(f"Error generating prediction for {symbol}: {e}")
            return None
        
        # Get actual return
        actual_return = self._get_actual_return(symbol, prediction_date, target_date)
        if actual_return is None:
            return None
        
        # Calculate metrics
        error = prediction.predicted_return - actual_return
        absolute_error = abs(error)
        direction_correct = (
            (prediction.predicted_return > 0 and actual_return > 0) or
            (prediction.predicted_return < 0 and actual_return < 0)
        )
        
        return BacktestResult(
            symbol=symbol,
            prediction_date=prediction_date,
            target_date=target_date,
            predicted_return=prediction.predicted_return,
            actual_return=actual_return,
            error=error,
            absolute_error=absolute_error,
            direction_correct=direction_correct,
            confidence_score=prediction.confidence_score
        )
    
    def _get_actual_return(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> Optional[float]:
        """Get actual return between two dates."""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty or len(hist) < 2:
                return None
            
            start_price = hist["Close"].iloc[0]
            end_price = hist["Close"].iloc[-1]
            
            return ((end_price / start_price) - 1) * 100  # Return as percentage
        except Exception as e:
            print(f"Error getting actual return for {symbol}: {e}")
            return None
    
    def backtest_historical(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        prediction_horizon_days: int = 30,
        step_days: int = 7  # Make prediction every N days
    ) -> List[BacktestResult]:
        """
        Run backtest over a historical period.
        
        Args:
            symbol: Stock symbol
            start_date: Start of backtest period
            end_date: End of backtest period
            prediction_horizon_days: Days ahead to predict
            step_days: Days between predictions
        
        Returns:
            List of BacktestResult objects
        """
        results = []
        current_date = start_date
        
        while current_date + timedelta(days=prediction_horizon_days) <= end_date:
            target_date = current_date + timedelta(days=prediction_horizon_days)
            
            result = self.backtest_prediction(symbol, current_date, target_date)
            if result:
                results.append(result)
            
            current_date += timedelta(days=step_days)
        
        return results
    
    def summarize_backtest(self, results: List[BacktestResult]) -> BacktestSummary:
        """Summarize backtest results."""
        if not results:
            return BacktestSummary(
                total_predictions=0,
                mean_absolute_error=0.0,
                root_mean_squared_error=0.0,
                direction_accuracy=0.0,
                mean_error=0.0
            )
        
        errors = [r.error for r in results]
        absolute_errors = [r.absolute_error for r in results]
        direction_correct = sum(1 for r in results if r.direction_correct)
        
        mae = sum(absolute_errors) / len(absolute_errors)
        rmse = (sum(e**2 for e in errors) / len(errors)) ** 0.5
        mean_error = sum(errors) / len(errors)
        direction_accuracy = direction_correct / len(results) * 100
        
        # Find best and worst predictions
        best = min(results, key=lambda r: r.absolute_error)
        worst = max(results, key=lambda r: r.absolute_error)
        
        return BacktestSummary(
            total_predictions=len(results),
            mean_absolute_error=mae,
            root_mean_squared_error=rmse,
            direction_accuracy=direction_accuracy,
            mean_error=mean_error,
            best_prediction=best,
            worst_prediction=worst
        )
    
    def compare_agents(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, BacktestSummary]:
        """Compare performance of individual agents."""
        # This would require modifying agents to be testable independently
        # For now, return placeholder
        return {
            "meta_supervisor": self.summarize_backtest(
                self.backtest_historical(symbol, start_date, end_date)
            )
        }
