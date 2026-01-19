# Tool-Aware Football Betting Assistant (v1.1)

This project is an educational football betting analysis system that combines:
- statistical models (1X2, BTTS, Over/Under)
- deterministic combo selection
- a local LLM (Mistral via Ollama) for explanation only

This project was created for educational purposes and personal experimentation in my free time.

It is NOT intended to be a serious or production-ready betting system, and it does NOT guarantee profit. 
The models and analyses are simplified and are used primarily to explore machine learning and controlled LLM integration.

Do not use this project for real-money betting decisions.

---

## Features
- Historical match ingestion
- Feature engineering for results and goals
- Trained models for:
  - 1X2
  - BTTS
  - Over/Under 2.5
- Combo engine with expected value and probability
- Tool-aware local LLM (Mistral) for explanation
- Strict intent gating (no accidental betting advice)
- DOES NOT YET SUPPORT LIVE MATCH ODDS OR REAL-TIME BETTING

---

## Requirements
- Linux
- Python 3.10+
- Ollama installed
- A local model (e.g. mistral)

---

## How to run
1. Create a virtual environment
2. Install requirements
3. Ingest historical data
4. Train models
5. Run the chat interface via "python3 src/chat_cli.py"


