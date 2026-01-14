# Phase 5B: Databricks Agent Bricks Integration

## Overview

Integrate our custom multi-agent system with Databricks native **Agent Bricks: Multi-Agent Supervisor** for enhanced orchestration and continuous optimization.

## Current State (Phase 5A)

✅ **Custom Meta-Supervisor Implementation:**
- 6 specialized agents (Fundamentals, Valuation, Technical, Macro, Events, Sector)
- Python-based orchestration with LLM synthesis
- Confidence-weighted prediction averaging
- Working end-to-end pipeline

## Target State (Phase 5B)

🎯 **Databricks Agent Bricks Integration:**
- Deploy agents as Databricks-compatible endpoints
- Use native Multi-Agent Supervisor for orchestration
- Enable SME feedback through Review App
- Continuous optimization with labeled data

## Architecture Comparison

### Current Architecture (Phase 5A)
```
Custom Python Meta-Supervisor
    ├── Fundamentals Agent (Python class)
    ├── Valuation Agent (Python class)
    ├── Technical Agent (Python class)
    ├── Macro Agent (Python class)
    ├── Events Agent (Python class)
    └── Sector Agent (Python class)
```

### Target Architecture (Phase 5B)
```
Databricks Agent Bricks: Multi-Agent Supervisor
    ├── Stock Fundamentals Agent Endpoint (Model Serving)
    ├── Stock Valuation Agent Endpoint (Model Serving)
    ├── Technical Analysis Agent Endpoint (Model Serving)
    ├── Macro Economic Agent Endpoint (Model Serving)
    ├── Events Analysis Agent Endpoint (Model Serving)
    └── Sector Analysis Agent Endpoint (Model Serving)
```

## Implementation Steps

### Step 1: Prerequisites Check

**Requirements from [Databricks Docs](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/multi-agent-supervisor):**

- [ ] Workspace in supported region (`us-east-1` or `us-west-2`)
- [ ] Mosaic AI Agent Bricks Preview enabled
- [ ] Production monitoring for MLflow enabled
- [ ] Agent Framework: On-Behalf-Of-User Authorization enabled
- [ ] Serverless compute enabled
- [ ] Unity Catalog enabled
- [ ] Access to Mosaic AI Model Serving
- [ ] Access to foundation models (`system.ai` schema)
- [ ] Serverless budget policy configured

**Current Workspace:** `https://dbc-47a3dcaa-ae3e.cloud.databricks.com`

**Action Items:**
1. Verify workspace region
2. Enable required preview features in Admin Console
3. Check serverless compute quota
4. Verify `databricks-gte-large-en` endpoint (disable AI Guardrails)

### Step 2: Convert Agents to Deployable Endpoints

**Option A: Agent Framework Endpoints**
- Package each agent as a Databricks Agent Framework endpoint
- Deploy using MLflow model serving
- Implement required interface for agent coordination

**Option B: Unity Catalog Functions**
- Wrap agent logic in UC Functions
- Register as callable tools
- Simpler deployment, less overhead

**Recommended:** Start with **Option B (UC Functions)** for faster iteration

**Implementation:**
```python
# Example: Create UC Function for Fundamentals Agent
from databricks import sql

@udf("stocks_ai_system.agents.analyze_fundamentals")
def analyze_fundamentals(symbol: str, as_of_date: str) -> dict:
    """
    Analyzes fundamental metrics for a stock.
    
    Returns:
        dict: Fundamental analysis with signals and predictions
    """
    from src.agents.fundamentals_agent import FundamentalsAgent
    from datetime import date
    
    agent = FundamentalsAgent()
    prediction = agent.generate_prediction(symbol, date.fromisoformat(as_of_date))
    
    return {
        "predicted_return": prediction.predicted_return,
        "confidence": prediction.confidence_score,
        "reasoning": prediction.reasoning,
        "key_factors": prediction.key_factors
    }
```

### Step 3: Register Agents in Agent Bricks UI

**Navigate to:** Workspace → **Agents** → **Multi-Agent Supervisor** → **Build**

**Configuration:**
1. **Name:** Stock Market Multi-Agent Analyst
2. **Description:** "Analyzes stocks from 6 specialized perspectives: fundamentals, valuation, technical indicators, macroeconomic conditions, corporate events, and sector trends. Synthesizes insights to provide investment recommendations."

3. **Configure Agents (6 total):**

   **Agent 1: Fundamentals Analysis**
   - Type: Unity Catalog Function
   - Function: `stocks_ai_system.agents.analyze_fundamentals`
   - Name: "Fundamentals Agent"
   - Description: "Analyzes company financial health: revenue, earnings, debt, profitability, growth trends"

   **Agent 2: Valuation Analysis**
   - Type: Unity Catalog Function
   - Function: `stocks_ai_system.agents.analyze_valuation`
   - Name: "Valuation Agent"
   - Description: "Determines if stock is overvalued or undervalued: P/E, P/B, DCF, fair value estimates"

   **Agent 3: Technical Analysis**
   - Type: Unity Catalog Function
   - Function: `stocks_ai_system.agents.analyze_technical`
   - Name: "Technical Agent"
   - Description: "Analyzes price trends and momentum: moving averages, RSI, MACD, Bollinger Bands"

   **Agent 4: Macro Economic Analysis**
   - Type: Unity Catalog Function
   - Function: `stocks_ai_system.agents.analyze_macro`
   - Name: "Macro Agent"
   - Description: "Evaluates macroeconomic environment: interest rates, VIX, market sentiment, sector sensitivity"

   **Agent 5: Events Analysis**
   - Type: Unity Catalog Function
   - Function: `stocks_ai_system.agents.analyze_events`
   - Name: "Events Agent"
   - Description: "Tracks corporate events and catalysts: earnings calendar, earnings surprises, news sentiment"

   **Agent 6: Sector Analysis**
   - Type: Unity Catalog Function
   - Function: `stocks_ai_system.agents.analyze_sector`
   - Name: "Sector Agent"
   - Description: "Compares to industry peers: sector performance, relative strength, competitive positioning"

4. **Instructions:**
```
You are a senior investment analyst coordinating 6 specialized analysts. 

When analyzing a stock:
1. Always consult ALL 6 agents for comprehensive analysis
2. Weight predictions by agent confidence scores
3. Identify consensus and divergence among agents
4. Highlight key risks and opportunities
5. Provide clear, actionable investment thesis

Output format:
- Synthesized Prediction: [+/- X.X%]
- Confidence: [0-100%]
- Investment Thesis: [2-3 sentences]
- Key Supporting Factors: [bullet points]
- Risk Factors: [bullet points]
- Agent Consensus: [bullish/bearish/mixed]
```

### Step 4: Test and Optimize

**Testing Scenarios:**
1. **Bullish Stock:** AAPL, MSFT (test unanimous positive)
2. **Bearish Stock:** Test underperforming stock
3. **Mixed Signals:** Stock with conflicting indicators
4. **Sector Rotation:** Test during sector-specific events
5. **Earnings Season:** Test with upcoming earnings

**AI Playground Testing:**
- Open supervisor in Playground
- Enable **AI Judge** for evaluation
- Enable **Synthetic task generation**
- Test with various stock symbols and questions

### Step 5: Collect Human Feedback

**Labeling Session Setup:**
1. Create task scenarios:
   - "Analyze AAPL for 30-day investment horizon"
   - "Is TSLA overvalued given current macro conditions?"
   - "Compare NVDA vs AMD for semiconductor exposure"
   - "What are the risks for banking sector now?"
   
2. Start labeling session
3. Grant SME permissions to domain experts:
   - Portfolio managers
   - Research analysts
   - Risk managers
   
4. Reviewers provide feedback in Review App:
   - Rate agent coordination quality
   - Add expectations and guidelines
   - Suggest improvements

5. Merge feedback and retrain

### Step 6: Production Deployment

**Access Control:**
- Grant `CAN QUERY` to end users
- Configure on-behalf-of-user authentication
- Test permissions with different user roles

**Integration:**
- Get endpoint URL from Agent Bricks
- Update downstream applications (chatbots, dashboards)
- Monitor usage and performance

**Monitoring:**
- Enable MLflow tracing
- Track agent coordination patterns
- Monitor latency and costs

## Benefits of Agent Bricks Integration

### 1. **No-Code Orchestration**
- UI-based configuration (no Python changes needed)
- Visual agent coordination management
- Easier for non-technical stakeholders

### 2. **Continuous Optimization**
- Human feedback loop through Review App
- Automatic retraining with labeled data
- Improves coordination quality over time

### 3. **Native Databricks Integration**
- Built-in access controls (Unity Catalog)
- Serverless scaling (cost-efficient)
- Tracing and monitoring (MLflow)

### 4. **Enterprise Features**
- On-behalf-of-user authorization
- Fine-grained permissions
- Compliance and governance

### 5. **Simplified Maintenance**
- Databricks manages infrastructure
- Automatic scaling
- Built-in observability

## Comparison: When to Use Each Approach

### Use **Custom Meta-Supervisor (Phase 5A)** when:
- ✅ Need full control over synthesis logic
- ✅ Require custom confidence weighting algorithms
- ✅ Want portable code (non-Databricks deployment)
- ✅ Need complex domain-specific orchestration
- ✅ Working in development/research phase

### Use **Agent Bricks Multi-Agent Supervisor (Phase 5B)** when:
- ✅ Ready for production deployment
- ✅ Want no-code agent management
- ✅ Need human-in-the-loop optimization
- ✅ Require enterprise governance features
- ✅ Want automatic scaling and cost optimization
- ✅ Need native Databricks integration

## Migration Path

### Phase 1: Dual Deployment (Recommended)
- Keep custom Meta-Supervisor (Phase 5A) for flexibility
- Deploy Agent Bricks (Phase 5B) in parallel
- A/B test both approaches
- Gather user feedback

### Phase 2: Production Rollout
- Use Agent Bricks for production workloads
- Keep custom implementation for research/development
- Monitor performance and cost differences

### Phase 3: Optimization
- Collect SME feedback through Review App
- Fine-tune agent coordination
- Measure improvement in prediction quality

## Success Metrics

- **Coordination Quality:** Agent selection accuracy
- **Prediction Accuracy:** Compared to actual stock performance
- **User Satisfaction:** SME feedback scores
- **Cost Efficiency:** Compared to custom implementation
- **Latency:** End-to-end response time
- **Adoption:** Number of queries per day

## Next Steps

1. **Immediate:** Check workspace prerequisites
2. **Week 1:** Create UC Functions for all 6 agents
3. **Week 2:** Configure Agent Bricks Multi-Agent Supervisor
4. **Week 3:** Test with AI Playground and initial users
5. **Week 4:** Start labeling session with SMEs
6. **Week 5:** Production deployment and monitoring

## References

- [Databricks Agent Bricks: Multi-Agent Supervisor Documentation](https://docs.databricks.com/aws/en/generative-ai/agent-bricks/multi-agent-supervisor)
- [Create AI agent tools using Unity Catalog functions](https://docs.databricks.com/en/generative-ai/agent-framework/create-tools.html)
- [Databricks Agent Framework](https://docs.databricks.com/en/generative-ai/agent-framework/index.html)
