"""Model Governance and Compliance Framework."""
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from dataclasses import dataclass, asdict
import json
import mlflow
from src.data.schemas import SynthesizedPrediction, AgentPrediction


@dataclass
class ModelAuditRecord:
    """Audit record for model governance."""
    record_id: str
    timestamp: datetime
    model_version: str
    prediction_id: str
    symbol: str
    prediction_date: date
    predicted_return: float
    confidence_score: float
    agent_contributions: Dict[str, Any]
    reasoning_chain: str
    risk_factors: List[str]
    user_id: Optional[str] = None
    approval_status: Optional[str] = None  # pending, approved, rejected
    regulatory_flags: List[str] = None


@dataclass
class BiasMetrics:
    """Bias and fairness metrics."""
    symbol_bias_score: float
    sector_bias_score: float
    prediction_variance: float
    confidence_variance: float
    demographic_parity: Optional[float] = None


class ModelGovernance:
    """Model governance and compliance framework."""
    
    def __init__(self, mlflow_experiment_name: str = "/Shared/stocks_ai/governance"):
        self.mlflow_experiment = mlflow_experiment_name
        self.audit_trail = []
    
    def log_prediction_for_governance(
        self,
        prediction: SynthesizedPrediction,
        user_id: Optional[str] = None,
        regulatory_context: Optional[Dict[str, Any]] = None
    ) -> ModelAuditRecord:
        """
        Log prediction for governance and compliance tracking.
        
        Args:
            prediction: The synthesized prediction
            user_id: User who generated the prediction
            regulatory_context: Additional regulatory context
        
        Returns:
            ModelAuditRecord for audit trail
        """
        import uuid
        
        # Check for regulatory flags
        regulatory_flags = self._check_regulatory_flags(prediction, regulatory_context)
        
        audit_record = ModelAuditRecord(
            record_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            model_version=self._get_model_version(),
            prediction_id=prediction.prediction_id,
            symbol=prediction.symbol,
            prediction_date=prediction.prediction_date,
            predicted_return=prediction.predicted_return,
            confidence_score=prediction.confidence_score,
            agent_contributions=prediction.agent_contributions,
            reasoning_chain=prediction.reasoning_chain,
            risk_factors=prediction.risk_factors,
            user_id=user_id,
            approval_status="pending",
            regulatory_flags=regulatory_flags
        )
        
        # Log to MLflow for lineage
        with mlflow.start_run(experiment_id=self._get_experiment_id()):
            mlflow.log_dict(asdict(audit_record), "audit_record.json")
            mlflow.log_param("symbol", prediction.symbol)
            mlflow.log_param("prediction_date", str(prediction.prediction_date))
            mlflow.log_metric("predicted_return", prediction.predicted_return)
            mlflow.log_metric("confidence_score", prediction.confidence_score)
            
            if regulatory_flags:
                mlflow.log_param("regulatory_flags", json.dumps(regulatory_flags))
        
        # Store in audit trail
        self.audit_trail.append(audit_record)
        
        return audit_record
    
    def _check_regulatory_flags(
        self,
        prediction: SynthesizedPrediction,
        regulatory_context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Check for regulatory compliance flags."""
        flags = []
        
        # High confidence on extreme predictions
        if abs(prediction.predicted_return) > 20 and prediction.confidence_score > 0.9:
            flags.append("high_confidence_extreme_prediction")
        
        # Low confidence on significant predictions
        if abs(prediction.predicted_return) > 10 and prediction.confidence_score < 0.5:
            flags.append("low_confidence_significant_prediction")
        
        # Missing risk factors
        if not prediction.risk_factors or len(prediction.risk_factors) == 0:
            flags.append("missing_risk_factors")
        
        # Agent disagreement
        if len(prediction.agent_contributions) > 0:
            returns = [c["predicted_return"] for c in prediction.agent_contributions.values()]
            if max(returns) - min(returns) > 15:  # High disagreement
                flags.append("high_agent_disagreement")
        
        # Regulatory context checks
        if regulatory_context:
            if regulatory_context.get("requires_approval", False):
                flags.append("requires_regulatory_approval")
            if regulatory_context.get("high_risk_sector", False):
                flags.append("high_risk_sector")
        
        return flags
    
    def generate_explainability_report(
        self,
        prediction: SynthesizedPrediction
    ) -> Dict[str, Any]:
        """Generate explainability report for regulators."""
        return {
            "prediction_summary": {
                "symbol": prediction.symbol,
                "predicted_return": prediction.predicted_return,
                "confidence_score": prediction.confidence_score,
                "target_date": str(prediction.target_date)
            },
            "reasoning_chain": prediction.reasoning_chain,
            "agent_contributions": {
                agent: {
                    "predicted_return": contrib["predicted_return"],
                    "confidence": contrib["confidence"],
                    "reasoning": contrib["reasoning"][:500]  # Truncated
                }
                for agent, contrib in prediction.agent_contributions.items()
            },
            "risk_factors": prediction.risk_factors,
            "key_insights": prediction.key_insights,
            "model_metadata": {
                "model_version": self._get_model_version(),
                "prediction_timestamp": str(prediction.created_timestamp),
                "agents_used": list(prediction.agent_contributions.keys())
            }
        }
    
    def calculate_bias_metrics(
        self,
        predictions: List[SynthesizedPrediction]
    ) -> BiasMetrics:
        """Calculate bias and fairness metrics."""
        if not predictions:
            return BiasMetrics(0.0, 0.0, 0.0, 0.0)
        
        returns = [p.predicted_return for p in predictions]
        confidences = [p.confidence_score for p in predictions]
        
        # Calculate variance
        import numpy as np
        return_variance = float(np.var(returns))
        confidence_variance = float(np.var(confidences))
        
        # Symbol bias (simplified - would need more sophisticated analysis)
        symbol_bias = return_variance / (abs(np.mean(returns)) + 1e-6)
        
        # Sector bias (simplified)
        sector_bias = confidence_variance
        
        return BiasMetrics(
            symbol_bias_score=symbol_bias,
            sector_bias_score=sector_bias,
            prediction_variance=return_variance,
            confidence_variance=confidence_variance
        )
    
    def approve_prediction(
        self,
        audit_record_id: str,
        approver_id: str,
        approval_notes: Optional[str] = None
    ) -> bool:
        """Approve a prediction for use."""
        record = next((r for r in self.audit_trail if r.record_id == audit_record_id), None)
        if record:
            record.approval_status = "approved"
            # Log approval to MLflow
            with mlflow.start_run(experiment_id=self._get_experiment_id()):
                mlflow.log_param("approval_status", "approved")
                mlflow.log_param("approver_id", approver_id)
                if approval_notes:
                    mlflow.log_param("approval_notes", approval_notes)
            return True
        return False
    
    def get_audit_trail(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[ModelAuditRecord]:
        """Get audit trail with optional filters."""
        filtered = self.audit_trail
        
        if symbol:
            filtered = [r for r in filtered if r.symbol == symbol]
        if start_date:
            filtered = [r for r in filtered if r.prediction_date >= start_date]
        if end_date:
            filtered = [r for r in filtered if r.prediction_date <= end_date]
        
        return filtered
    
    def _get_model_version(self) -> str:
        """Get current model version."""
        # In production, would get from MLflow or version control
        return "1.0.0"
    
    def _get_experiment_id(self) -> str:
        """Get MLflow experiment ID."""
        try:
            experiment = mlflow.get_experiment_by_name(self.mlflow_experiment)
            if experiment:
                return experiment.experiment_id
            else:
                mlflow.create_experiment(self.mlflow_experiment)
                experiment = mlflow.get_experiment_by_name(self.mlflow_experiment)
                return experiment.experiment_id
        except Exception:
            return "0"  # Default experiment
