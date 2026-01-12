"""Real-Time Streaming Predictions using Databricks Structured Streaming."""
from typing import Dict, Any, Optional
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, struct
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
from src.agents.meta_supervisor import MetaSupervisor
import json


class RealtimePredictor:
    """Real-time prediction pipeline using Databricks Structured Streaming."""
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.meta_supervisor = MetaSupervisor()
    
    def create_streaming_pipeline(
        self,
        input_stream_path: str,
        output_stream_path: str,
        checkpoint_location: str
    ):
        """
        Create a streaming pipeline for real-time predictions.
        
        Args:
            input_stream_path: Path to input stream (Delta table or Kafka)
            output_stream_path: Path to output stream
            checkpoint_location: Checkpoint location for streaming
        """
        # Read streaming data
        stream_df = self.spark.readStream \
            .format("delta") \
            .load(input_stream_path)
        
        # Define prediction UDF
        predict_udf = udf(
            self._predict_wrapper,
            StructType([
                StructField("predicted_return", DoubleType()),
                StructField("confidence_score", DoubleType()),
                StructField("prediction_id", StringType()),
                StructField("reasoning_chain", StringType()),
                StructField("risk_factors", StringType())
            ])
        )
        
        # Apply predictions
        predictions_df = stream_df \
            .withColumn("prediction", predict_udf(
                col("symbol"),
                col("timestamp")
            )) \
            .select(
                col("symbol"),
                col("timestamp"),
                col("prediction.predicted_return").alias("predicted_return"),
                col("prediction.confidence_score").alias("confidence_score"),
                col("prediction.prediction_id").alias("prediction_id"),
                col("prediction.reasoning_chain").alias("reasoning_chain"),
                col("prediction.risk_factors").alias("risk_factors")
            )
        
        # Write to output stream
        query = predictions_df.writeStream \
            .format("delta") \
            .outputMode("append") \
            .option("checkpointLocation", checkpoint_location) \
            .option("path", output_stream_path) \
            .trigger(processingTime="10 seconds") \
            .start()
        
        return query
    
    def _predict_wrapper(self, symbol: str, timestamp: datetime) -> Dict[str, Any]:
        """Wrapper function for UDF to generate predictions."""
        try:
            from datetime import date, timedelta
            
            prediction_date = timestamp.date() if isinstance(timestamp, datetime) else date.today()
            target_date = prediction_date + timedelta(days=30)
            
            prediction = self.meta_supervisor.generate_prediction(
                symbol, prediction_date, target_date
            )
            
            return {
                "predicted_return": float(prediction.predicted_return),
                "confidence_score": float(prediction.confidence_score),
                "prediction_id": prediction.prediction_id,
                "reasoning_chain": prediction.reasoning_chain[:1000],  # Truncate
                "risk_factors": json.dumps(prediction.risk_factors)
            }
        except Exception as e:
            # Return default values on error
            return {
                "predicted_return": 0.0,
                "confidence_score": 0.0,
                "prediction_id": "error",
                "reasoning_chain": f"Error: {str(e)}",
                "risk_factors": json.dumps([])
            }
    
    def create_signal_stream(
        self,
        symbols: list,
        signal_interval_seconds: int = 60
    ):
        """
        Create a streaming signal source for testing.
        
        Args:
            symbols: List of symbols to stream
            signal_interval_seconds: Interval between signals
        """
        from pyspark.sql import Row
        from datetime import datetime
        
        # Create sample streaming data
        data = [
            Row(
                symbol=symbol,
                timestamp=datetime.now(),
                price=100.0,  # Would be real price data
                volume=1000000
            )
            for symbol in symbols
        ]
        
        df = self.spark.createDataFrame(data)
        
        # Write to Delta table for streaming
        df.write.format("delta").mode("overwrite").save("/tmp/streaming_signals")
        
        return "/tmp/streaming_signals"
    
    def monitor_streaming_performance(
        self,
        stream_query
    ) -> Dict[str, Any]:
        """Monitor streaming query performance."""
        return {
            "is_active": stream_query.isActive,
            "last_progress": stream_query.lastProgress if stream_query.lastProgress else {},
            "status": stream_query.status
        }
