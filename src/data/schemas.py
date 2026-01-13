"""Data schemas for the multi-supervisor AI system."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class Company(BaseModel):
    """Company master data."""
    symbol: str = Field(..., description="Stock symbol")
    company_name: Optional[str] = Field(None, description="Full company name")
    sector: Optional[str] = Field(None, description="Sector")
    industry: Optional[str] = Field(None, description="Industry")
    market_cap: Optional[int] = Field(None, description="Market capitalization")
    fortune_rank: Optional[int] = Field(None, description="Fortune rank")
    added_date: Optional[datetime] = Field(None, description="Date added")
    updated_date: Optional[datetime] = Field(None, description="Last updated")


class FundamentalMetrics(BaseModel):
    """Company fundamental financial metrics."""
    symbol: str
    date: date
    revenue: Optional[int] = Field(None, description="Revenue in USD")
    net_income: Optional[int] = Field(None, description="Net income in USD")
    eps: Optional[float] = Field(None, description="Earnings per share")
    pe_ratio: Optional[float] = Field(None, description="Price-to-earnings ratio")
    debt_to_equity: Optional[float] = Field(None, description="Debt-to-equity ratio")
    roe: Optional[float] = Field(None, description="Return on equity")
    revenue_growth: Optional[float] = Field(None, description="Revenue growth rate")
    ingestion_timestamp: Optional[datetime] = Field(None, description="When data was ingested")


class ValuationMetrics(BaseModel):
    """Company valuation metrics."""
    symbol: str
    date: date
    market_cap: Optional[int] = Field(None, description="Market capitalization")
    enterprise_value: Optional[int] = Field(None, description="Enterprise value")
    pe_ratio: Optional[float] = Field(None, description="Price-to-earnings ratio")
    pb_ratio: Optional[float] = Field(None, description="Price-to-book ratio")
    ev_ebitda: Optional[float] = Field(None, description="EV/EBITDA ratio")
    dcf_value: Optional[float] = Field(None, description="DCF valuation")
    fair_value_estimate: Optional[float] = Field(None, description="Fair value estimate")
    ingestion_timestamp: Optional[datetime] = Field(None, description="When data was ingested")


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators."""
    symbol: str
    date: date
    open_price: Optional[float] = Field(None, description="Opening price")
    high_price: Optional[float] = Field(None, description="High price")
    low_price: Optional[float] = Field(None, description="Low price")
    close_price: Optional[float] = Field(None, description="Closing price")
    volume: Optional[int] = Field(None, description="Trading volume")
    sma_50: Optional[float] = Field(None, description="50-day simple moving average")
    sma_200: Optional[float] = Field(None, description="200-day simple moving average")
    rsi: Optional[float] = Field(None, description="Relative Strength Index")
    macd: Optional[float] = Field(None, description="MACD indicator")
    bollinger_upper: Optional[float] = Field(None, description="Bollinger upper band")
    bollinger_lower: Optional[float] = Field(None, description="Bollinger lower band")
    ingestion_timestamp: Optional[datetime] = Field(None, description="When data was ingested")


class MacroIndicators(BaseModel):
    """Macroeconomic indicators."""
    date: date
    gdp_growth: Optional[float] = Field(None, description="GDP growth rate")
    inflation_rate: Optional[float] = Field(None, description="Inflation rate (CPI)")
    interest_rate: Optional[float] = Field(None, description="Interest rate")
    unemployment_rate: Optional[float] = Field(None, description="Unemployment rate")
    consumer_confidence: Optional[float] = Field(None, description="Consumer confidence index")
    vix_index: Optional[float] = Field(None, description="VIX volatility index")
    ingestion_timestamp: Optional[datetime] = Field(None, description="When data was ingested")


class EventType(str, Enum):
    """Market event types."""
    EARNINGS = "earnings"
    NEWS = "news"
    MERGER = "merger"
    DIVIDEND = "dividend"
    SPLIT = "split"
    OTHER = "other"


class MarketEvent(BaseModel):
    """Market event or news."""
    event_id: str
    symbol: Optional[str] = Field(None, description="Related stock symbol")
    event_type: Optional[EventType] = Field(None, description="Type of event")
    event_date: Optional[date] = Field(None, description="Event date")
    title: Optional[str] = Field(None, description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    sentiment_score: Optional[float] = Field(None, description="Sentiment score (-1 to 1)")
    impact_score: Optional[float] = Field(None, description="Impact score (0 to 1)")
    ingestion_timestamp: Optional[datetime] = Field(None, description="When data was ingested")


class AgentPrediction(BaseModel):
    """Prediction from a single agent."""
    prediction_id: str
    symbol: str
    prediction_date: date
    target_date: date
    predicted_return: float = Field(..., description="Predicted return percentage")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    reasoning: str = Field(..., description="Reasoning chain")
    key_factors: List[str] = Field(default_factory=list, description="Key factors influencing prediction")
    created_timestamp: datetime = Field(default_factory=datetime.now)


class SynthesizedPrediction(BaseModel):
    """Meta-supervisor synthesized prediction."""
    prediction_id: str
    symbol: str
    prediction_date: date
    target_date: date
    predicted_return: float = Field(..., description="Synthesized predicted return percentage")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Synthesized confidence score")
    investment_hypothesis: str = Field(..., description="Investment hypothesis")
    reasoning_chain: str = Field(..., description="Complete reasoning chain")
    agent_contributions: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Contributions from each agent"
    )
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    key_insights: List[str] = Field(default_factory=list, description="Key insights")
    created_timestamp: datetime = Field(default_factory=datetime.now)
