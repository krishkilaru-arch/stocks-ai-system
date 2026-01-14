# Multi-Supervisor AI System for Stock Price Prediction

A sophisticated multi-agent AI system that predicts stock price movements for Fortune 100 companies by reasoning over multiple signal types and forming investment hypotheses.

## Overview

This system employs a **multi-supervisor architecture** where specialized AI agents analyze different aspects of stock performance:

- **Fundamentals Agent**: Financial metrics, ratios, growth indicators
- **Valuation Agent**: P/E ratios, DCF models, market perception
- **Macro Agent**: GDP, inflation, interest rates, policy changes
- **Events Agent**: Earnings reports, news sentiment, external events
- **Technical Agent**: Price patterns, momentum, volume analysis
- **Sector Agent**: Industry trends, peer comparisons

A **Meta-Supervisor** synthesizes insights from all agents to form coherent investment hypotheses with explainable reasoning.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Meta-Supervisor (Orchestrator)             │
│         Synthesizes predictions & forms hypotheses      │
└─────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐     ┌────▼────┐    ┌────▼────┐
    │Fundamentals│   │ Valuation│   │  Macro  │
    │  Agent     │   │  Agent   │   │  Agent  │
    └───────────┘   └──────────┘   └─────────┘
         │               │               │
    ┌────▼────┐     ┌────▼────┐    ┌────▼────┐
    │  Events │     │Technical│    │ Sector  │
    │  Agent  │     │  Agent  │    │  Agent  │
    └─────────┘     └─────────┘    └─────────┘
```

## Key Features

- **Multi-Agent Reasoning**: Each supervisor agent specializes in a specific domain
- **Signal Integration**: Combines fundamental, technical, macro, and behavioral signals
- **Explainable AI**: Provides reasoning chains for each prediction
- **Databricks Integration**: Built on Delta Lake, MLflow, and Unity Catalog
- **Scalable Architecture**: Designed for Fortune 100 companies and beyond

## Project Structure

```
stocks/
├── README.md
├── requirements.txt
├── databricks.yml
├── setup/
│   └── init.sql              # Unity Catalog setup
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py     # Base agent framework
│   │   ├── fundamentals_agent.py
│   │   ├── valuation_agent.py
│   │   ├── macro_agent.py
│   │   ├── events_agent.py
│   │   ├── technical_agent.py
│   │   ├── sector_agent.py
│   │   └── meta_supervisor.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loaders.py        # Data loading utilities
│   │   ├── processors.py     # Signal processing
│   │   └── schemas.py        # Data schemas
│   └── utils/
│       ├── __init__.py
│       ├── llm_client.py     # LLM integration
│       └── config.py         # Configuration
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_agent_demo.ipynb
│   └── 03_full_pipeline.ipynb
└── tests/
    └── test_agents.py
```

## Getting Started

### Prerequisites

- Databricks workspace with Unity Catalog enabled
- Python 3.10+
- Access to financial data APIs (Yahoo Finance, Alpha Vantage, etc.)

### Installation

```bash
pip install -r requirements.txt
```

### Setup Databricks

1. Configure `databricks.yml` with your workspace details
2. Run `setup/init.sql` to create Unity Catalog schemas
3. Deploy notebooks to your Databricks workspace

### Usage

See example notebooks in the `notebooks/` directory for:
- Data ingestion and processing
- Individual agent demonstrations
- Full pipeline execution

## Use Cases

1. **Investment Hypothesis Formation**: Generate data-driven investment theses
2. **Risk Assessment**: Identify potential risks from multiple signal types
3. **Portfolio Optimization**: Compare predictions across Fortune 100 companies
4. **Market Analysis**: Understand sector and macro trends

## Technology Stack

- **Databricks**: Delta Lake, MLflow, Unity Catalog
- **Python**: Core language
- **LLMs**: OpenAI/Anthropic for agent reasoning
- **Data Sources**: Yahoo Finance, Alpha Vantage, FRED, SEC filings

## License

MIT

## Author

Prepared for Databricks Data + AI Summit 2026
