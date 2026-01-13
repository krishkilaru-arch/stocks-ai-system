"""Data loading and schema definitions."""
from .schemas import (
    Company,
    FundamentalMetrics,
    ValuationMetrics,
    TechnicalIndicators,
    MacroIndicators,
    MarketEvent,
    AgentPrediction,
    SynthesizedPrediction
)
from .loaders import (
    DataLoader,
    YahooFinanceLoader,
    AlphaVantageLoader,
    FREDLoader
)

__all__ = [
    "Company",
    "FundamentalMetrics",
    "ValuationMetrics",
    "TechnicalIndicators",
    "MacroIndicators",
    "MarketEvent",
    "AgentPrediction",
    "SynthesizedPrediction",
    "DataLoader",
    "YahooFinanceLoader",
    "AlphaVantageLoader",
    "FREDLoader"
]
