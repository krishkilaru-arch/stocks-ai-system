"""Base agent framework for specialized supervisor agents."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import date, datetime, timedelta
import uuid
from src.data.schemas import AgentPrediction
from src.utils.llm_client import LLMClient
from src.utils.config import config


class BaseAgent(ABC):
    """Base class for all supervisor agents."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.llm_client = LLMClient()
        self.prediction_horizon_days = config.default_prediction_horizon_days
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass
    
    @abstractmethod
    def collect_signals(self, symbol: str, as_of_date: date) -> Dict[str, Any]:
        """Collect relevant signals for the given symbol and date."""
        pass
    
    @abstractmethod
    def analyze_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze collected signals and extract key insights."""
        pass
    
    def generate_prediction(
        self,
        symbol: str,
        as_of_date: Optional[date] = None,
        target_date: Optional[date] = None
    ) -> AgentPrediction:
        """
        Generate a prediction for the given symbol.
        
        Args:
            symbol: Stock symbol
            as_of_date: Date to make prediction from (defaults to today)
            target_date: Target date for prediction (defaults to as_of_date + horizon)
        
        Returns:
            AgentPrediction with reasoning and confidence
        """
        if as_of_date is None:
            as_of_date = date.today()
        if target_date is None:
            target_date = as_of_date + timedelta(days=self.prediction_horizon_days)
        
        # Collect signals
        signals = self.collect_signals(symbol, as_of_date)
        
        # Analyze signals
        analysis = self.analyze_signals(signals)
        
        # Generate reasoning using LLM
        reasoning = self._generate_reasoning(symbol, signals, analysis, as_of_date, target_date)
        
        # Extract prediction from reasoning
        prediction_data = self._extract_prediction_from_reasoning(reasoning)
        
        return AgentPrediction(
            prediction_id=str(uuid.uuid4()),
            symbol=symbol,
            prediction_date=as_of_date,
            target_date=target_date,
            predicted_return=prediction_data["predicted_return"],
            confidence_score=prediction_data["confidence_score"],
            reasoning=reasoning,
            key_factors=prediction_data.get("key_factors", []),
            created_timestamp=datetime.now()
        )
    
    def _generate_reasoning(
        self,
        symbol: str,
        signals: Dict[str, Any],
        analysis: Dict[str, Any],
        as_of_date: date,
        target_date: date
    ) -> str:
        """Generate reasoning using LLM."""
        system_prompt = self.get_system_prompt()
        
        user_prompt = f"""Analyze the following data for {symbol} and provide a prediction for {target_date}.

Current Date: {as_of_date}
Target Date: {target_date}
Prediction Horizon: {(target_date - as_of_date).days} days

Collected Signals:
{self._format_signals(signals)}

Analysis:
{self._format_analysis(analysis)}

Please provide:
1. A predicted return percentage for {target_date} (e.g., +5.2% or -3.1%)
2. A confidence score between 0.0 and 1.0
3. Detailed reasoning for your prediction
4. Key factors that influenced your prediction

Format your response as a clear analysis with the prediction and confidence clearly stated."""
        
        return self.llm_client.generate_reasoning(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7
        )
    
    def _extract_prediction_from_reasoning(self, reasoning: str) -> Dict[str, Any]:
        """Extract structured prediction data from reasoning text."""
        # Use LLM to extract structured data
        extraction_prompt = f"""Extract the following information from this reasoning text:

{reasoning}

Extract:
1. predicted_return: A float representing the predicted return percentage (e.g., 5.2 for +5.2%)
2. confidence_score: A float between 0.0 and 1.0
3. key_factors: A list of strings describing the key factors

Return as JSON."""
        
        try:
            result = self.llm_client.generate_structured_output(
                system_prompt="You are a data extraction assistant. Extract structured data from text.",
                user_prompt=extraction_prompt,
                output_format='{"predicted_return": float, "confidence_score": float, "key_factors": ["factor1", "factor2"]}',
                temperature=0.3
            )
            return result
        except Exception as e:
            # Fallback: try to parse from text
            import re
            return_match = re.search(r'([+-]?\d+\.?\d*)\s*%', reasoning)
            confidence_match = re.search(r'confidence[:\s]+(\d+\.?\d*)', reasoning, re.IGNORECASE)
            
            predicted_return = float(return_match.group(1)) if return_match else 0.0
            confidence_score = float(confidence_match.group(1)) if confidence_match else 0.5
            
            return {
                "predicted_return": predicted_return,
                "confidence_score": min(max(confidence_score, 0.0), 1.0),
                "key_factors": []
            }
    
    def _format_signals(self, signals: Dict[str, Any]) -> str:
        """Format signals dictionary for display."""
        formatted = []
        for key, value in signals.items():
            if isinstance(value, (int, float)):
                formatted.append(f"{key}: {value:,.2f}" if isinstance(value, float) else f"{key}: {value:,}")
            elif isinstance(value, list):
                formatted.append(f"{key}: {len(value)} items")
            elif isinstance(value, dict):
                formatted.append(f"{key}: {len(value)} sub-items")
            else:
                formatted.append(f"{key}: {value}")
        return "\n".join(formatted)
    
    def _format_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format analysis dictionary for display."""
        return self._format_signals(analysis)
    
    def get_agent_info(self) -> Dict[str, str]:
        """Get information about this agent."""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__
        }
