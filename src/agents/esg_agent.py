"""ESG Agent - Analyzes Environmental, Social, and Governance factors."""
from typing import Dict, Any
from datetime import date
from src.agents.base_agent import BaseAgent
from src.data.loaders import DataLoader


class ESGAgent(BaseAgent):
    """Agent specializing in ESG (Environmental, Social, Governance) analysis."""
    
    def __init__(self):
        super().__init__(
            name="ESG Agent",
            description="Analyzes environmental, social, and governance factors and their impact on investment decisions"
        )
        self.data_loader = DataLoader()
    
    def get_system_prompt(self) -> str:
        return """You are an ESG (Environmental, Social, Governance) analyst specializing in sustainable investing.

Your expertise includes:
- Environmental factors (carbon emissions, climate risk, resource usage)
- Social factors (labor practices, diversity, community impact)
- Governance factors (board composition, executive compensation, transparency)
- ESG scoring and ratings
- Climate risk assessment
- Regulatory compliance (SFDR, EU Taxonomy, etc.)
- Impact investing considerations

When making predictions, consider:
1. ESG score trends and improvements
2. Climate risk exposure and transition risks
3. Social controversies and their financial impact
4. Governance quality and shareholder rights
5. Regulatory compliance with ESG frameworks
6. ESG-adjusted risk and return expectations
7. Long-term sustainability of business model

Provide clear ESG analysis with both quantitative scores and qualitative assessment of ESG risks and opportunities."""
    
    def collect_signals(self, symbol: str, as_of_date: date) -> Dict[str, Any]:
        """Collect ESG-related signals."""
        signals = {}
        
        # Get company info
        company_info = self.data_loader.get_company_info(symbol)
        if company_info:
            signals["sector"] = company_info.sector
            signals["industry"] = company_info.industry
        
        # Get ESG scores (would integrate with ESG data providers like MSCI, Sustainalytics)
        esg_scores = self.data_loader.get_esg_scores(symbol)
        if esg_scores:
            signals.update({
                "esg_score": esg_scores.get("overall_score"),
                "environmental_score": esg_scores.get("environmental"),
                "social_score": esg_scores.get("social"),
                "governance_score": esg_scores.get("governance"),
                "esg_rating": esg_scores.get("rating"),  # AAA, AA, A, BBB, etc.
                "esg_trend": esg_scores.get("trend")  # improving, stable, declining
            })
        
        # Get climate risk data
        climate_risk = self.data_loader.get_climate_risk(symbol)
        if climate_risk:
            signals["climate_risk"] = {
                "physical_risk": climate_risk.get("physical_risk"),
                "transition_risk": climate_risk.get("transition_risk"),
                "carbon_footprint": climate_risk.get("carbon_footprint"),
                "renewable_energy_pct": climate_risk.get("renewable_energy_pct")
            }
        
        # Get ESG controversies
        controversies = self.data_loader.get_esg_controversies(symbol, as_of_date, days=365)
        if controversies:
            signals["esg_controversies"] = {
                "count": len(controversies),
                "severity": max([c.get("severity", 0) for c in controversies]) if controversies else 0,
                "recent_controversies": [c.get("title") for c in controversies[:3]]
            }
        
        # Get regulatory compliance
        regulatory_compliance = self.data_loader.get_esg_regulatory_compliance(symbol)
        if regulatory_compliance:
            signals["regulatory_compliance"] = {
                "sfdr_compliant": regulatory_compliance.get("sfdr"),
                "eu_taxonomy_aligned": regulatory_compliance.get("eu_taxonomy"),
                "tcfd_reporting": regulatory_compliance.get("tcfd")
            }
        
        return signals
    
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze ESG signals."""
        analysis = {}
        
        # ESG score assessment
        if signals.get("esg_score"):
            esg_score = signals["esg_score"]
            if esg_score >= 80:
                analysis["esg_quality"] = "excellent"
            elif esg_score >= 60:
                analysis["esg_quality"] = "good"
            elif esg_score >= 40:
                analysis["esg_quality"] = "moderate"
            else:
                analysis["esg_quality"] = "poor"
        
        # ESG rating assessment
        if signals.get("esg_rating"):
            rating = signals["esg_rating"]
            if rating in ["AAA", "AA"]:
                analysis["esg_rating_quality"] = "leader"
            elif rating in ["A", "BBB"]:
                analysis["esg_rating_quality"] = "average"
            else:
                analysis["esg_rating_quality"] = "laggard"
        
        # Climate risk assessment
        if "climate_risk" in signals:
            climate = signals["climate_risk"]
            physical_risk = climate.get("physical_risk", 0)
            transition_risk = climate.get("transition_risk", 0)
            
            if physical_risk > 7 or transition_risk > 7:
                analysis["climate_risk_level"] = "high"
            elif physical_risk > 4 or transition_risk > 4:
                analysis["climate_risk_level"] = "moderate"
            else:
                analysis["climate_risk_level"] = "low"
        
        # Controversy assessment
        if "esg_controversies" in signals:
            controversies = signals["esg_controversies"]
            if controversies.get("count", 0) > 3:
                analysis["controversy_risk"] = "high"
            elif controversies.get("count", 0) > 0:
                analysis["controversy_risk"] = "moderate"
            else:
                analysis["controversy_risk"] = "low"
            
            if controversies.get("severity", 0) > 7:
                analysis["controversy_severity"] = "severe"
        
        # Regulatory compliance
        if "regulatory_compliance" in signals:
            compliance = signals["regulatory_compliance"]
            compliant_count = sum([
                compliance.get("sfdr_compliant", False),
                compliance.get("eu_taxonomy_aligned", False),
                compliance.get("tcfd_reporting", False)
            ])
            
            if compliant_count == 3:
                analysis["regulatory_readiness"] = "fully_compliant"
            elif compliant_count >= 2:
                analysis["regulatory_readiness"] = "mostly_compliant"
            else:
                analysis["regulatory_readiness"] = "needs_improvement"
        
        # ESG trend analysis
        if signals.get("esg_trend"):
            trend = signals["esg_trend"]
            if trend == "improving":
                analysis["esg_momentum"] = "positive"
            elif trend == "declining":
                analysis["esg_momentum"] = "negative"
            else:
                analysis["esg_momentum"] = "stable"
        
        # Sector ESG comparison
        if signals.get("sector"):
            sector_avg_esg = self.data_loader.get_sector_avg_esg(signals["sector"])
            if sector_avg_esg and signals.get("esg_score"):
                if signals["esg_score"] > sector_avg_esg * 1.1:
                    analysis["sector_esg_position"] = "above_average"
                elif signals["esg_score"] < sector_avg_esg * 0.9:
                    analysis["sector_esg_position"] = "below_average"
                else:
                    analysis["sector_esg_position"] = "average"
        
        return analysis
