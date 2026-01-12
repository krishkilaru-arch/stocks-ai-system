"""Fundamentals Agent - Analyzes company financial metrics and fundamentals."""
from typing import Dict, Any
from datetime import date
from src.agents.base_agent import BaseAgent
from src.data.loaders import DataLoader


class FundamentalsAgent(BaseAgent):
    """Agent specializing in fundamental financial analysis."""
    
    def __init__(self):
        super().__init__(
            name="Fundamentals Agent",
            description="Analyzes company financial metrics, ratios, growth indicators, and fundamental health"
        )
        self.data_loader = DataLoader()
    
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
        fundamentals = self.data_loader.get_fundamentals(symbol, as_of_date)
        
        if fundamentals:
            signals.update({
                "revenue": fundamentals.revenue,
                "net_income": fundamentals.net_income,
                "eps": fundamentals.eps,
                "pe_ratio": fundamentals.pe_ratio,
                "debt_to_equity": fundamentals.debt_to_equity,
                "roe": fundamentals.roe,
                "revenue_growth": fundamentals.revenue_growth
            })
        
        # Get historical trends (last 4 quarters)
        historical = self.data_loader.get_fundamentals_history(symbol, as_of_date, quarters=4)
        if historical:
            signals["historical_trends"] = {
                "revenue_trend": [f.revenue for f in historical if f.revenue],
                "eps_trend": [f.eps for f in historical if f.eps],
                "roe_trend": [f.roe for f in historical if f.roe]
            }
        
        # Get industry comparison
        industry_avg = self.data_loader.get_industry_averages(symbol)
        if industry_avg:
            signals["industry_comparison"] = industry_avg
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze fundamental signals."""
        analysis = {}
        
        # Calculate growth trends
        if "historical_trends" in signals:
            revenue_trend = signals["historical_trends"].get("revenue_trend", [])
            if len(revenue_trend) >= 2:
                analysis["revenue_momentum"] = "increasing" if revenue_trend[-1] > revenue_trend[0] else "decreasing"
                analysis["revenue_growth_rate"] = ((revenue_trend[-1] / revenue_trend[0]) - 1) * 100 if revenue_trend[0] > 0 else 0
        
        # Assess financial health
        if signals.get("debt_to_equity"):
            de_ratio = signals["debt_to_equity"]
            if de_ratio < 0.5:
                analysis["financial_health"] = "strong"
            elif de_ratio < 1.0:
                analysis["financial_health"] = "moderate"
            else:
                analysis["financial_health"] = "leveraged"
        
        # Profitability assessment
        if signals.get("roe"):
            roe = signals["roe"]
            if roe > 15:
                analysis["profitability"] = "excellent"
            elif roe > 10:
                analysis["profitability"] = "good"
            else:
                analysis["profitability"] = "moderate"
        
        # Valuation assessment
        if signals.get("pe_ratio"):
            pe = signals["pe_ratio"]
            industry_pe = signals.get("industry_comparison", {}).get("avg_pe_ratio")
            if industry_pe:
                if pe < industry_pe * 0.8:
                    analysis["valuation"] = "undervalued"
                elif pe > industry_pe * 1.2:
                    analysis["valuation"] = "overvalued"
                else:
                    analysis["valuation"] = "fair"
        
        return analysis
