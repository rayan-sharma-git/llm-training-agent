# LLM Training Agent

AI-powered engineering assistant for LLM fine-tuning in VS Code.

## Features
- Project scanning and framework detection
- Dataset, prompt, hyperparameter, model analysis
- Training cost estimation
- Outcome prediction
- Recommendations and reports
- Chat interface
- Safe file editing with diffs

## Quick Start
1. Install Python 3.10+ and Node.js 18+
2. Install backend dependencies: `pip install -r backend/requirements.txt`
3. Install extension dependencies: `npm install` in `extension/`
4. Run backend: `uvicorn backend.main:app --reload`
5. Run extension: press F5 in VS Code

## Architecture
- VS Code Extension (TypeScript)
- Python Backend (FastAPI)
- SQLite storage with repository abstraction
- AI provider abstraction (OpenAI, Anthropic, Ollama)

## License
MIT