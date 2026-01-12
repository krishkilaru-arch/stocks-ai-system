"""Demo script for the multi-supervisor AI stock prediction system."""
import os
from datetime import date, timedelta
from dotenv import load_dotenv
from src.agents.meta_supervisor import MetaSupervisor

# Load environment variables
load_dotenv()


def main():
    """Run a demo prediction for a Fortune 100 company."""
    
    print("=" * 80)
    print("Multi-Supervisor AI System for Stock Price Prediction")
    print("=" * 80)
    print()
    
    # Initialize meta-supervisor
    print("Initializing Meta-Supervisor and specialized agents...")
    supervisor = MetaSupervisor()
    
    # Display agent summary
    print("\nAvailable Agents:")
    for name, info in supervisor.get_agent_summary().items():
        print(f"  • {info['name']}: {info['description']}")
    
    # Example: Predict for Apple (AAPL)
    symbol = "AAPL"
    as_of_date = date.today()
    target_date = as_of_date + timedelta(days=30)
    
    print(f"\n{'=' * 80}")
    print(f"Generating prediction for {symbol}")
    print(f"Prediction Date: {as_of_date}")
    print(f"Target Date: {target_date} ({(target_date - as_of_date).days} days)")
    print(f"{'=' * 80}\n")
    
    try:
        # Generate prediction
        print("Collecting signals from specialized agents...")
        prediction = supervisor.generate_prediction(symbol, as_of_date, target_date)
        
        # Display results
        print("\n" + "=" * 80)
        print("SYNTHESIZED PREDICTION")
        print("=" * 80)
        print(f"\nSymbol: {prediction.symbol}")
        print(f"Predicted Return: {prediction.predicted_return:+.2f}%")
        print(f"Confidence Score: {prediction.confidence_score:.2f}")
        print(f"\nTarget Date: {prediction.target_date}")
        
        print("\n" + "-" * 80)
        print("INVESTMENT HYPOTHESIS")
        print("-" * 80)
        print(prediction.investment_hypothesis)
        
        print("\n" + "-" * 80)
        print("KEY INSIGHTS")
        print("-" * 80)
        for insight in prediction.key_insights:
            print(f"  • {insight}")
        
        print("\n" + "-" * 80)
        print("RISK FACTORS")
        print("-" * 80)
        for risk in prediction.risk_factors:
            print(f"  • {risk}")
        
        print("\n" + "-" * 80)
        print("AGENT CONTRIBUTIONS")
        print("-" * 80)
        for agent_name, contribution in prediction.agent_contributions.items():
            print(f"\n{agent_name.upper()} Agent:")
            print(f"  Predicted Return: {contribution['predicted_return']:+.2f}%")
            print(f"  Confidence: {contribution['confidence']:.2f}")
            print(f"  Reasoning: {contribution['reasoning'][:200]}...")
        
        print("\n" + "-" * 80)
        print("REASONING CHAIN")
        print("-" * 80)
        print(prediction.reasoning_chain)
        
        print("\n" + "=" * 80)
        print("Prediction completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nError generating prediction: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
