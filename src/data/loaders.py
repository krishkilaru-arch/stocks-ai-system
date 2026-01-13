"""Data loaders for various financial data sources."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import date, datetime, timedelta
import yfinance as yf
from src.data.schemas import (
    Company,
    FundamentalMetrics,
    ValuationMetrics,
    TechnicalIndicators,
    MacroIndicators,
    MarketEvent
)
from src.utils.config import config


class DataLoader(ABC):
    """Base class for data loaders."""
    
    @abstractmethod
    def load_company_info(self, symbol: str) -> Optional[Company]:
        """Load company master data."""
        pass
    
    @abstractmethod
    def load_fundamentals(self, symbol: str, as_of_date: Optional[date] = None) -> Optional[FundamentalMetrics]:
        """Load fundamental metrics."""
        pass
    
    @abstractmethod
    def load_valuation(self, symbol: str, as_of_date: Optional[date] = None) -> Optional[ValuationMetrics]:
        """Load valuation metrics."""
        pass
    
    @abstractmethod
    def load_technical(self, symbol: str, as_of_date: Optional[date] = None) -> Optional[TechnicalIndicators]:
        """Load technical indicators."""
        pass


class YahooFinanceLoader(DataLoader):
    """Yahoo Finance data loader."""
    
    def __init__(self):
        self.enabled = config.yahoo_finance_enabled
    
    def load_company_info(self, symbol: str) -> Optional[Company]:
        """Load company information from Yahoo Finance."""
        if not self.enabled:
            return None
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return Company(
                symbol=symbol,
                company_name=info.get("longName"),
                sector=info.get("sector"),
                industry=info.get("industry"),
                market_cap=info.get("marketCap"),
                fortune_rank=None,
                added_date=datetime.now(),
                updated_date=datetime.now()
            )
        except Exception as e:
            print(f"Error loading company info for {symbol}: {e}")
            return None
    
    def load_fundamentals(self, symbol: str, as_of_date: Optional[date] = None) -> Optional[FundamentalMetrics]:
        """Load fundamental metrics from Yahoo Finance."""
        if not self.enabled:
            return None
        
        if as_of_date is None:
            as_of_date = date.today()
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get financials
            financials = ticker.financials
            income_stmt = ticker.income_stmt
            balance_sheet = ticker.balance_sheet
            
            # Calculate revenue growth if we have historical data
            revenue_growth = None
            if income_stmt is not None and not income_stmt.empty:
                revenues = income_stmt.loc["Total Revenue"] if "Total Revenue" in income_stmt.index else None
                if revenues is not None and len(revenues) > 1:
                    try:
                        current = float(revenues.iloc[0])
                        previous = float(revenues.iloc[1])
                        if previous != 0:
                            revenue_growth = ((current - previous) / previous) * 100
                    except:
                        pass
            
            return FundamentalMetrics(
                symbol=symbol,
                date=as_of_date,
                revenue=info.get("totalRevenue"),
                net_income=info.get("netIncomeToCommon"),
                eps=info.get("trailingEps"),
                pe_ratio=info.get("trailingPE"),
                debt_to_equity=info.get("debtToEquity"),
                roe=info.get("returnOnEquity"),
                revenue_growth=revenue_growth,
                ingestion_timestamp=datetime.now()
            )
        except Exception as e:
            print(f"Error loading fundamentals for {symbol}: {e}")
            return None
    
    def load_valuation(self, symbol: str, as_of_date: Optional[date] = None) -> Optional[ValuationMetrics]:
        """Load valuation metrics from Yahoo Finance."""
        if not self.enabled:
            return None
        
        if as_of_date is None:
            as_of_date = date.today()
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return ValuationMetrics(
                symbol=symbol,
                date=as_of_date,
                market_cap=info.get("marketCap"),
                enterprise_value=info.get("enterpriseValue"),
                pe_ratio=info.get("trailingPE"),
                pb_ratio=info.get("priceToBook"),
                ev_ebitda=info.get("enterpriseToEbitda"),
                dcf_value=None,  # Would need separate calculation
                fair_value_estimate=info.get("targetMeanPrice"),
                ingestion_timestamp=datetime.now()
            )
        except Exception as e:
            print(f"Error loading valuation for {symbol}: {e}")
            return None
    
    def load_technical(self, symbol: str, as_of_date: Optional[date] = None, period: str = "1y") -> Optional[TechnicalIndicators]:
        """Load technical indicators from Yahoo Finance."""
        if not self.enabled:
            return None
        
        if as_of_date is None:
            as_of_date = date.today()
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # Get latest data
            latest = hist.iloc[-1]
            
            # Calculate moving averages
            sma_50 = hist['Close'].tail(50).mean() if len(hist) >= 50 else None
            sma_200 = hist['Close'].tail(200).mean() if len(hist) >= 200 else None
            
            # Calculate RSI (simplified)
            rsi = self._calculate_rsi(hist['Close']) if len(hist) >= 14 else None
            
            # Calculate MACD (simplified)
            macd = self._calculate_macd(hist['Close']) if len(hist) >= 26 else None
            
            # Calculate Bollinger Bands
            bb_upper, bb_lower = self._calculate_bollinger_bands(hist['Close']) if len(hist) >= 20 else (None, None)
            
            return TechnicalIndicators(
                symbol=symbol,
                date=as_of_date,
                open_price=float(latest['Open']),
                high_price=float(latest['High']),
                low_price=float(latest['Low']),
                close_price=float(latest['Close']),
                volume=int(latest['Volume']),
                sma_50=sma_50,
                sma_200=sma_200,
                rsi=rsi,
                macd=macd,
                bollinger_upper=bb_upper,
                bollinger_lower=bb_lower,
                ingestion_timestamp=datetime.now()
            )
        except Exception as e:
            print(f"Error loading technical indicators for {symbol}: {e}")
            return None
    
    def _calculate_rsi(self, prices: Any, period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index."""
        try:
            deltas = prices.diff()
            gains = deltas.where(deltas > 0, 0)
            losses = -deltas.where(deltas < 0, 0)
            
            avg_gain = gains.rolling(window=period).mean()
            avg_loss = losses.rolling(window=period).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi.iloc[-1]) if not rsi.empty else None
        except:
            return None
    
    def _calculate_macd(self, prices: Any, fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[float]:
        """Calculate MACD indicator."""
        try:
            import pandas as pd
            ema_fast = prices.ewm(span=fast).mean()
            ema_slow = prices.ewm(span=slow).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal).mean()
            macd = macd_line.iloc[-1] - signal_line.iloc[-1]
            return float(macd) if not pd.isna(macd) else None
        except:
            return None
    
    def _calculate_bollinger_bands(self, prices: Any, period: int = 20, std_dev: float = 2.0) -> tuple:
        """Calculate Bollinger Bands."""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper = sma + (std * std_dev)
            lower = sma - (std * std_dev)
            return (float(upper.iloc[-1]), float(lower.iloc[-1])) if not upper.empty else (None, None)
        except:
            return (None, None)


class AlphaVantageLoader(DataLoader):
    """Alpha Vantage data loader (optional)."""
    
    def __init__(self):
        self.api_key = config.alpha_vantage_api_key
        self.enabled = self.api_key is not None
    
    def load_company_info(self, symbol: str) -> Optional[Company]:
        """Load company info from Alpha Vantage."""
        # Alpha Vantage doesn't provide company info, use Yahoo Finance
        return None
    
    def load_fundamentals(self, symbol: str, as_of_date: Optional[date] = None) -> Optional[FundamentalMetrics]:
        """Load fundamentals from Alpha Vantage."""
        if not self.enabled:
            return None
        # Implementation would go here if API key is available
        return None
    
    def load_valuation(self, symbol: str, as_of_date: Optional[date] = None) -> Optional[ValuationMetrics]:
        """Load valuation from Alpha Vantage."""
        if not self.enabled:
            return None
        # Implementation would go here if API key is available
        return None
    
    def load_technical(self, symbol: str, as_of_date: Optional[date] = None) -> Optional[TechnicalIndicators]:
        """Load technical indicators from Alpha Vantage."""
        if not self.enabled:
            return None
        # Implementation would go here if API key is available
        return None


class FREDLoader:
    """FRED (Federal Reserve Economic Data) loader for macroeconomic indicators."""
    
    def __init__(self):
        self.api_key = config.fred_api_key
        self.enabled = self.api_key is not None
    
    def load_macro_indicators(self, as_of_date: Optional[date] = None) -> Optional[MacroIndicators]:
        """Load macroeconomic indicators from FRED."""
        if not self.enabled:
            return None
        
        if as_of_date is None:
            as_of_date = date.today()
        
        try:
            from fredapi import Fred
            fred = Fred(api_key=self.api_key)
            
            # Get various economic indicators
            # Note: These are example series IDs - adjust as needed
            gdp_growth = None
            inflation_rate = None
            interest_rate = None
            unemployment_rate = None
            consumer_confidence = None
            
            # Try to fetch data (with error handling)
            try:
                # GDP growth (quarterly, need to calculate)
                # inflation_rate = fred.get_series('CPIAUCSL', end=as_of_date)
                # interest_rate = fred.get_series('FEDFUNDS', end=as_of_date)
                # unemployment_rate = fred.get_series('UNRATE', end=as_of_date)
                pass
            except:
                pass
            
            return MacroIndicators(
                date=as_of_date,
                gdp_growth=gdp_growth,
                inflation_rate=inflation_rate,
                interest_rate=interest_rate,
                unemployment_rate=unemployment_rate,
                consumer_confidence=consumer_confidence,
                vix_index=None,  # VIX is from CBOE, not FRED
                ingestion_timestamp=datetime.now()
            )
        except Exception as e:
            print(f"Error loading macro indicators from FRED: {e}")
            return None
