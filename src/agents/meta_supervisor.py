"""Meta-Supervisor - Synthesizes predictions from all agents and forms investment hypotheses."""
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
import uuid
from src.agents.base_agent import BaseAgent
from src.agents.fundamentals_agent import FundamentalsAgent
from src.agents.valuation_agent import ValuationAgent
from src.agents.macro_agent import MacroAgent
from src.agents.events_agent import EventsAgent
from src.agents.technical_agent import TechnicalAgent
from src.agents.sector_agent import SectorAgent
from src.data.schemas import SynthesizedPrediction, AgentPrediction
from src.utils.llm_client import LLMClient
from src.utils.config import config


class MetaSupervisor:
    """Meta-supervisor that orchestrates all 6 specialized agents and synthesizes predictions."""
    
    def __init__(self):
        """Initialize Meta-Supervisor with 6 specialized agents."""
        # 3 Core Agents: Fundamentals, Valuation, Technical
        # 3 Context Agents: Macro, Events, Sector
        self.agents = {
            "fundamentals": FundamentalsAgent(),
            "valuation": ValuationAgent(),
            "technical": TechnicalAgent(),
            "macro": MacroAgent(),
            "events": EventsAgent(),
            "sector": SectorAgent()
        }
        self.llm_client = LLMClient()
        print(f"✓ Meta-Supervisor initialized with {len(self.agents)} agents")
    
    def generate_prediction(
        self,
        symbol: str,
        as_of_date: Optional[date] = None,
        target_date: Optional[date] = None
    ) -> SynthesizedPrediction:
        """
        Generate a synthesized prediction by collecting predictions from all agents.
        
        Args:
            symbol: Stock symbol
            as_of_date: Date to make prediction from
            target_date: Target date for prediction
        
        Returns:
            SynthesizedPrediction with investment hypothesis
        """
        if as_of_date is None:
            as_of_date = date.today()
        if target_date is None:
            target_date = as_of_date + timedelta(days=config.default_prediction_horizon_days)
        
        # Collect predictions from all agents
        agent_predictions = {}
        for agent_name, agent in self.agents.items():
            try:
                prediction = agent.generate_prediction(symbol, as_of_date, target_date)
                agent_predictions[agent_name] = prediction
            except Exception as e:
                print(f"Warning: {agent_name} agent failed: {e}")
                continue
        
        # Synthesize predictions
        synthesized = self._synthesize_predictions(
            symbol=symbol,
            as_of_date=as_of_date,
            target_date=target_date,
            agent_predictions=agent_predictions
        )
        
        return synthesized
    
    def _synthesize_predictions(
        self,
        symbol: str,
        as_of_date: date,
        target_date: date,
        agent_predictions: Dict[str, AgentPrediction]
    ) -> SynthesizedPrediction:
        """Synthesize predictions from all agents using LLM reasoning."""
        
        # Prepare agent contributions summary
        agent_contributions = {}
        predictions_summary = []
        
        for agent_name, prediction in agent_predictions.items():
            agent_contributions[agent_name] = {
                "predicted_return": prediction.predicted_return,
                "confidence": prediction.confidence_score,
                "reasoning": prediction.reasoning
            }
            predictions_summary.append(
                f"{agent_name.upper()} Agent: {prediction.predicted_return:+.2f}% "
                f"(confidence: {prediction.confidence_score:.2f})\n"
                f"Reasoning: {prediction.reasoning}\n"
                f"Key Factors: {', '.join(prediction.key_factors)}\n"
            )
        
        # Calculate weighted average prediction
        total_confidence = sum(p.confidence_score for p in agent_predictions.values())
        if total_confidence > 0:
            weighted_return = sum(
                p.predicted_return * p.confidence_score 
                for p in agent_predictions.values()
            ) / total_confidence
            avg_confidence = total_confidence / len(agent_predictions)
        else:
            weighted_return = 0.0
            avg_confidence = 0.0
        
        # Generate investment hypothesis using LLM
        hypothesis = self._generate_investment_hypothesis(
            symbol=symbol,
            as_of_date=as_of_date,
            target_date=target_date,
            agent_predictions=agent_predictions,
            weighted_return=weighted_return,
            avg_confidence=avg_confidence
        )
        
        # Extract structured data from hypothesis
        hypothesis_data = self._extract_hypothesis_data(hypothesis)
        
        # Build reasoning chain
        reasoning_chain = self._build_reasoning_chain(agent_predictions, hypothesis_data)
        
        return SynthesizedPrediction(
            prediction_id=str(uuid.uuid4()),
            symbol=symbol,
            prediction_date=as_of_date,
            target_date=target_date,
            predicted_return=hypothesis_data.get("predicted_return", weighted_return),
            confidence_score=hypothesis_data.get("confidence_score", avg_confidence),
            investment_hypothesis=hypothesis_data.get("hypothesis", hypothesis),
            reasoning_chain=reasoning_chain,
            agent_contributions=agent_contributions,
            risk_factors=hypothesis_data.get("risk_factors", []),
            key_insights=hypothesis_data.get("key_insights", []),
            created_timestamp=datetime.now()
        )
    
    def _generate_investment_hypothesis(
        self,
        symbol: str,
        as_of_date: date,
        target_date: date,
        agent_predictions: Dict[str, AgentPrediction],
        weighted_return: float,
        avg_confidence: float
    ) -> str:
        """Generate investment hypothesis using LLM."""
        
        system_prompt = """You are a senior investment strategist synthesizing insights from multiple specialized analysts.

Your role is to:
1. Integrate predictions from different analytical perspectives
2. Identify consensus and divergence among analysts
3. Form a coherent investment hypothesis
4. Identify key risks and opportunities
5. Provide actionable insights

Be thorough, balanced, and consider both bullish and bearish factors."""
        
        predictions_text = "\n\n".join([
            f"**{name.upper()} AGENT**\n"
            f"Predicted Return: {pred.predicted_return:+.2f}%\n"
            f"Confidence: {pred.confidence_score:.2f}\n"
            f"Reasoning: {pred.reasoning}\n"
            f"Key Factors: {', '.join(pred.key_factors)}"
            for name, pred in agent_predictions.items()
        ])
        
        user_prompt = f"""Synthesize an investment hypothesis for {symbol} based on the following agent predictions.

Target: Predict price movement from {as_of_date} to {target_date} ({(target_date - as_of_date).days} days)

Weighted Average Prediction: {weighted_return:+.2f}%
Average Confidence: {avg_confidence:.2f}

AGENT PREDICTIONS:
{predictions_text}

Please provide:
1. A synthesized predicted return percentage
2. A confidence score (0.0 to 1.0)
3. A clear investment hypothesis (2-3 sentences)
4. Key insights that support the hypothesis
5. Risk factors that could derail the prediction
6. Reasoning chain explaining how you synthesized the different perspectives

Format your response clearly with sections for each component."""
        
        try:
            return self.llm_client.generate_reasoning(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=3000
            )
        except Exception as e:
            # Fallback if LLM fails
            print(f"⚠ LLM hypothesis generation failed: {e}")
            return self._generate_fallback_hypothesis(
                symbol, weighted_return, avg_confidence, agent_predictions
            )
    
    def _generate_fallback_hypothesis(
        self,
        symbol: str,
        weighted_return: float,
        avg_confidence: float,
        agent_predictions: Dict[str, AgentPrediction]
    ) -> str:
        """Generate a simple rule-based hypothesis when LLM is unavailable."""
        direction = "bullish" if weighted_return > 0 else "bearish"
        strength = "strong" if abs(weighted_return) > 5 else "moderate"
        
        # Extract key factors from agents
        all_factors = []
        for pred in agent_predictions.values():
            all_factors.extend(pred.key_factors[:2])
        
        hypothesis = f"""INVESTMENT HYPOTHESIS FOR {symbol}:

Predicted Return: {weighted_return:+.2f}%
Confidence Score: {avg_confidence:.2f}
Outlook: {strength.capitalize()} {direction}

Based on analysis from {len(agent_predictions)} specialized agents, the consensus indicates a {direction} outlook for {symbol}. 
The weighted prediction of {weighted_return:+.2f}% reflects the synthesized view across fundamental, valuation, technical, macroeconomic, event-driven, and sector-specific factors.

Key Supporting Factors:
{chr(10).join(f"• {factor}" for factor in all_factors[:5])}

Confidence Level: {avg_confidence:.2%} based on agreement across {len(agent_predictions)} agents.

Note: This is a rule-based synthesis. For enhanced reasoning, configure LLM provider."""
        
        return hypothesis
    
    def _extract_hypothesis_data(self, hypothesis_text: str) -> Dict[str, Any]:
        """Extract structured data from hypothesis text."""
        extraction_prompt = f"""Extract structured data from this investment hypothesis:

{hypothesis_text}

Extract:
1. predicted_return: A float representing the predicted return percentage
2. confidence_score: A float between 0.0 and 1.0
3. hypothesis: A concise 2-3 sentence investment hypothesis
4. key_insights: A list of strings with key insights
5. risk_factors: A list of strings with risk factors

Return as JSON."""
        
        try:
            result = self.llm_client.generate_structured_output(
                system_prompt="You are a data extraction assistant.",
                user_prompt=extraction_prompt,
                output_format='''{
  "predicted_return": float,
  "confidence_score": float,
  "hypothesis": "string",
  "key_insights": ["string"],
  "risk_factors": ["string"]
}''',
                temperature=0.3
            )
            return result
        except Exception as e:
            # Fallback parsing
            import re
            return_match = re.search(r'([+-]?\d+\.?\d*)\s*%', hypothesis_text)
            confidence_match = re.search(r'confidence[:\s]+(\d+\.?\d*)', hypothesis_text, re.IGNORECASE)
            
            return {
                "predicted_return": float(return_match.group(1)) if return_match else 0.0,
                "confidence_score": float(confidence_match.group(1)) if confidence_match else 0.5,
                "hypothesis": hypothesis_text[:500],  # First 500 chars as fallback
                "key_insights": [],
                "risk_factors": []
            }
    
    def _build_reasoning_chain(
        self,
        agent_predictions: Dict[str, AgentPrediction],
        hypothesis_data: Dict[str, Any]
    ) -> str:
        """Build a reasoning chain explaining the synthesis."""
        chain_parts = [
            "REASONING CHAIN:",
            "",
            f"1. Collected predictions from {len(agent_predictions)} specialized agents",
            ""
        ]
        
        for i, (name, pred) in enumerate(agent_predictions.items(), 2):
            chain_parts.append(
                f"{i}. {name.upper()} Agent: {pred.predicted_return:+.2f}% "
                f"(confidence: {pred.confidence_score:.2f})"
            )
            chain_parts.append(f"   Key factors: {', '.join(pred.key_factors[:3])}")
            chain_parts.append("")
        
        chain_parts.extend([
            f"{len(agent_predictions) + 2}. Synthesis:",
            f"   - Weighted prediction: {hypothesis_data.get('predicted_return', 0):+.2f}%",
            f"   - Confidence: {hypothesis_data.get('confidence_score', 0):.2f}",
            "",
            "KEY INSIGHTS:",
        ])
        
        for insight in hypothesis_data.get("key_insights", [])[:5]:
            chain_parts.append(f"  • {insight}")
        
        chain_parts.extend([
            "",
            "RISK FACTORS:",
        ])
        
        for risk in hypothesis_data.get("risk_factors", [])[:5]:
            chain_parts.append(f"  • {risk}")
        
        return "\n".join(chain_parts)
    
    def get_agent_summary(self) -> Dict[str, Dict[str, str]]:
        """Get summary of all agents."""
        return {
            name: agent.get_agent_info()
            for name, agent in self.agents.items()
        }
