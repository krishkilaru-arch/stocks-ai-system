"""Fundamentals Agent - Analyzes company financial metrics and fundamentals."""
from typing import Dict, Any
from datetime import date
from src.agents.base_agent import BaseAgent
from src.data.loaders import YahooFinanceLoader


class FundamentalsAgent(BaseAgent):
    """Agent specializing in fundamental financial analysis."""
    
    def __init__(self):
        super().__init__(
            name="Fundamentals Agent",
            description="Analyzes company financial metrics, ratios, growth indicators, and fundamental health"
        )
        self.data_loader = YahooFinanceLoader()
    
    def get_system_prompt(self) -> str:
        return """You are a financial analyst specializing in fundamental analysis of companies.

Your expertise includes:
- Financial statement analysis (income statement, balance sheet, cash flow)
- Financial ratios (P/E, P/B, debt-to-equity, ROE, ROA, etc.)
- Growth metrics (revenue growth, earnings growth, margin trends)
- Profitability analysis
- Financial health and solvency assessment

When making predictions, consider:
1. Historical financial performance trends
2. Current financial ratios compared to industry averages
3. Growth trajectory and sustainability
4. Profitability and margin trends
5. Debt levels and financial stability
6. Cash flow generation and quality

Provide clear, data-driven reasoning for your predictions based on fundamental analysis principles."""
    
    def collect_signals(self, symbol: str, as_of_date: date) -> Dict[str, Any]:
        """Collect fundamental financial signals."""
        signals = {}
        
        # Get fundamental metrics from data loader
        fundamentals = self.data_loader.load_fundamentals(symbol, as_of_date)
        
        if fundamentals:
            signals.update({
                "symbol": symbol,
                "date": as_of_date.isoformat(),
                "revenue": fundamentals.revenue,
                "net_income": fundamentals.net_income,
                "eps": fundamentals.eps,
                "pe_ratio": fundamentals.pe_ratio,
                "debt_to_equity": fundamentals.debt_to_equity,
                "roe": fundamentals.roe,
                "revenue_growth": fundamentals.revenue_growth
            })
        
        # Get company info for context
        company = self.data_loader.load_company_info(symbol)
        if company:
            signals["company_name"] = company.company_name
            signals["sector"] = company.sector
            signals["industry"] = company.industry
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze fundamental signals."""
        analysis = {}
        
        # Revenue growth assessment
        if signals.get("revenue_growth"):
            growth = signals["revenue_growth"]
            if growth > 20:
                analysis["revenue_assessment"] = "strong growth (>20%)"
            elif growth > 10:
                analysis["revenue_assessment"] = "healthy growth (10-20%)"
            elif growth > 0:
                analysis["revenue_assessment"] = "modest growth (0-10%)"
            else:
                analysis["revenue_assessment"] = "declining revenue"
        
        # Assess financial health (debt-to-equity)
        if signals.get("debt_to_equity"):
            de_ratio = signals["debt_to_equity"]
            if de_ratio < 0.5:
                analysis["financial_health"] = "strong (low debt)"
            elif de_ratio < 1.0:
                analysis["financial_health"] = "moderate debt levels"
            else:
                analysis["financial_health"] = "highly leveraged"
        
        # Profitability assessment (ROE)
        if signals.get("roe"):
            roe = signals["roe"] * 100  # Convert to percentage
            if roe > 15:
                analysis["profitability"] = "excellent (ROE >15%)"
            elif roe > 10:
                analysis["profitability"] = "good (ROE 10-15%)"
            elif roe > 5:
                analysis["profitability"] = "moderate (ROE 5-10%)"
            else:
                analysis["profitability"] = "weak (ROE <5%)"
        
        # Valuation assessment (P/E ratio)
        if signals.get("pe_ratio"):
            pe = signals["pe_ratio"]
            if pe < 15:
                analysis["valuation"] = "attractive (P/E <15)"
            elif pe < 25:
                analysis["valuation"] = "fair (P/E 15-25)"
            else:
                analysis["valuation"] = "expensive (P/E >25)"
        
        # Earnings quality (EPS)
        if signals.get("eps"):
            eps = signals["eps"]
            if eps > 5:
                analysis["earnings_quality"] = "strong earnings per share"
            elif eps > 0:
                analysis["earnings_quality"] = "positive earnings"
            else:
                analysis["earnings_quality"] = "negative earnings"
        
        return analysis
