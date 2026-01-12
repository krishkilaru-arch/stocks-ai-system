"""Sector Agent - Analyzes industry trends and peer comparisons."""
from typing import Dict, Any
from datetime import date
from src.agents.base_agent import BaseAgent
from src.data.loaders import DataLoader


class SectorAgent(BaseAgent):
    """Agent specializing in sector and industry analysis."""
    
    def __init__(self):
        super().__init__(
            name="Sector Agent",
            description="Analyzes industry trends, sector performance, and peer company comparisons"
        )
        self.data_loader = DataLoader()
    
    def get_system_prompt(self) -> str:
        return """You are a sector analyst specializing in industry trends and peer comparisons.

Your expertise includes:
- Industry growth trends and cycles
- Sector rotation patterns
- Competitive positioning
- Peer company performance
- Industry-specific metrics and KPIs
- Regulatory and structural changes in industries
- Market share dynamics

When making predictions, consider:
1. Overall sector performance and trends
2. Company's position relative to peers
3. Industry growth prospects
4. Competitive advantages or disadvantages
5. Sector-specific headwinds or tailwinds
6. Market share trends
7. Industry consolidation or disruption

Provide reasoning that connects sector dynamics to individual stock performance."""
    
    def collect_signals(self, symbol: str, as_of_date: date) -> Dict[str, Any]:
        """Collect sector-related signals."""
        signals = {}
        
        # Get company sector info
        company_info = self.data_loader.get_company_info(symbol)
        if company_info:
            signals["sector"] = company_info.sector
            signals["industry"] = company_info.industry
        
        # Get sector performance
        if signals.get("sector"):
            sector_performance = self.data_loader.get_sector_performance(signals["sector"], as_of_date)
            if sector_performance:
                signals["sector_performance"] = {
                    "ytd_return": sector_performance.get("ytd_return"),
                    "recent_trend": sector_performance.get("trend"),
                    "relative_strength": sector_performance.get("relative_strength")
                }
        
        # Get peer companies
        peers = self.data_loader.get_peer_companies(symbol)
        if peers:
            signals["peer_count"] = len(peers)
            signals["peer_symbols"] = [p.symbol for p in peers]
        
        # Get peer performance comparison
        if peers:
            peer_performance = self.data_loader.get_peer_performance_comparison(symbol, as_of_date)
            if peer_performance:
                signals["peer_comparison"] = {
                    "company_rank": peer_performance.get("rank"),
                    "avg_peer_return": peer_performance.get("avg_return"),
                    "company_return": peer_performance.get("company_return")
                }
        
        # Get industry trends
        if signals.get("industry"):
            industry_trends = self.data_loader.get_industry_trends(signals["industry"], as_of_date)
            if industry_trends:
                signals["industry_trends"] = {
                    "growth_rate": industry_trends.get("growth_rate"),
                    "trend_direction": industry_trends.get("direction"),
                    "key_drivers": industry_trends.get("drivers", [])
                }
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sector signals."""
        analysis = {}
        
        # Sector performance assessment
        if "sector_performance" in signals:
            sector_perf = signals["sector_performance"]
            ytd_return = sector_perf.get("ytd_return", 0)
            
            if ytd_return > 15:
                analysis["sector_performance"] = "strong"
            elif ytd_return > 5:
                analysis["sector_performance"] = "good"
            elif ytd_return < -10:
                analysis["sector_performance"] = "weak"
            elif ytd_return < 0:
                analysis["sector_performance"] = "negative"
            else:
                analysis["sector_performance"] = "moderate"
        
        # Peer comparison
        if "peer_comparison" in signals:
            peer_comp = signals["peer_comparison"]
            company_return = peer_comp.get("company_return", 0)
            avg_peer_return = peer_comp.get("avg_peer_return", 0)
            rank = peer_comp.get("rank")
            
            if company_return > avg_peer_return * 1.1:
                analysis["peer_position"] = "outperforming peers"
            elif company_return < avg_peer_return * 0.9:
                analysis["peer_position"] = "underperforming peers"
            else:
                analysis["peer_position"] = "in line with peers"
            
            if rank:
                total_peers = signals.get("peer_count", 1)
                percentile = (1 - rank / total_peers) * 100
                if percentile > 75:
                    analysis["peer_ranking"] = "top quartile"
                elif percentile > 50:
                    analysis["peer_ranking"] = "above median"
                elif percentile > 25:
                    analysis["peer_ranking"] = "below median"
                else:
                    analysis["peer_ranking"] = "bottom quartile"
        
        # Industry trend assessment
        if "industry_trends" in signals:
            trends = signals["industry_trends"]
            growth_rate = trends.get("growth_rate", 0)
            
            if growth_rate > 10:
                analysis["industry_growth"] = "strong growth"
            elif growth_rate > 5:
                analysis["industry_growth"] = "moderate growth"
            elif growth_rate > 0:
                analysis["industry_growth"] = "slow growth"
            else:
                analysis["industry_growth"] = "declining"
        
        return analysis
