# Development Guide

## Prerequisites
- Python 3.10+
- Node.js 18+
- VS Code
- Git

## Backend Setup
1. Create virtual environment: `python -m venv venv`
2. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix)
3. Install dependencies: `pip install -r backend/requirements.txt`
4. Run server: `uvicorn backend.main:app --reload`
5. Access docs: http://127.0.0.1:8000/docs

## Extension Setup
1. Open extension folder in VS Code
2. Run `npm install`
3. Press F5 to launch Extension Development Host

## Running Tests
- Backend: `cd backend && pytest`
- Extension: `npm test`

## Code Quality
- Python: `ruff check .` and `black .`
- TypeScript: `eslint .` and `prettier --check .`