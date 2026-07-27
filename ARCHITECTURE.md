# Architecture

## Overview
- VS Code Extension (TypeScript)
- Python Backend (FastAPI)
- SQLite storage
- AI provider abstraction

## Communication
- REST API: `/api/v1/*`
- WebSocket: `/api/v1/ws/analysis`

## Backend Modules
- core: config, logging, errors, di
- scanner: ProjectScanner, FrameworkDetector
- analyzers: dataset, prompt, hyperparameters, model, cost
- prediction: PredictionEngine
- recommendation: RecommendationEngine
- reports: ReportGenerator
- storage: repositories + SQLAlchemy ORM
- ai: provider abstraction + implementations

## Extension Modules
- sidebar: Project overview
- chat: Conversational interface
- views: Report viewer, diff viewer
- commands: Command palette integration
- services: API client, settings, state