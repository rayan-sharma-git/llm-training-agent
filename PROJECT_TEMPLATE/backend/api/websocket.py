"""WebSocket handler for real-time analysis progress."""
from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from scanner.scanner import ProjectScanner
from scanner.context_builder import ContextBuilder
from analyzers.dataset_analyzer import DatasetAnalyzer
from analyzers.prompt_analyzer import PromptAnalyzer
from analyzers.hyperparameter_analyzer import HyperparameterAnalyzer
from analyzers.model_advisor import ModelAdvisor
from analyzers.cost_estimator import CostEstimator
from prediction.engine import PredictionEngine
from recommendation.engine import RecommendationEngine
from reports.generator import ReportGenerator
from models.schemas import ProjectContext
from core.errors import AnalysisError

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_event(self, event_type: str, data: Dict[str, Any]):
        """Send event to all connected clients."""
        event = {"type": event_type, "timestamp": datetime.utcnow().isoformat(), "data": data}
        for connection in self.active_connections:
            try:
                await connection.send_json(event)
            except Exception as e:
                logger.error(f"Failed to send WebSocket event: {e}")


manager = ConnectionManager()


@router.websocket("/ws/analysis")
async def analysis_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time analysis progress."""
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            if data.get("action") == "analyze":
                await run_analysis(data.get("projectPath"), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


async def run_analysis(project_path: str, websocket: WebSocket):
    """Run analysis and stream progress."""
    try:
        await manager.send_event("analysis_started", {"projectPath": project_path})
        await manager.send_event("scanner_progress", {"status": "Scanning project..."})
        scanner = ProjectScanner(project_path)
        scan_result = scanner.scan()
        await manager.send_event("scanner_progress", {"status": "Building context..."})
        context_builder = ContextBuilder()
        context = context_builder.build(scan_result)
        analyzers = {
            "dataset": DatasetAnalyzer(),
            "prompt": PromptAnalyzer(),
            "hyperparameters": HyperparameterAnalyzer(),
            "model": ModelAdvisor(),
            "cost": CostEstimator(),
        }
        results = {}
        for name, analyzer in analyzers.items():
            await manager.send_event("analyzer_progress", {"analyzer": name, "status": "running"})
            try:
                results[name] = await analyzer.analyze(context)
                await manager.send_event("analyzer_progress", {"analyzer": name, "status": "completed"})
            except Exception as e:
                logger.error(f"Analyzer {name} failed: {e}")
                results[name] = {}
                await manager.send_event("analyzer_progress", {"analyzer": name, "status": "failed", "error": str(e)})
        await manager.send_event("recommendation_generated", {"status": "Generating recommendations..."})
        pred_engine = PredictionEngine()
        rec_engine = RecommendationEngine()
        report_gen = ReportGenerator()
        prediction_result = await pred_engine.predict(context, results.get("dataset", {}), results.get("hyperparameters", {}), results.get("model", {}))
        recommendations = await rec_engine.generate(context, results.get("dataset", {}), results.get("prompt", {}), results.get("hyperparameters", {}), results.get("model", {}), results.get("cost", {}), prediction_result)
        report = report_gen.generate(context, results.get("dataset", {}), results.get("prompt", {}), results.get("hyperparameters", {}), results.get("model", {}), results.get("cost", {}), prediction_result, recommendations)
        await manager.send_event("report_ready", {"report": report})
        await manager.send_event("completed", {"status": "Analysis complete"})
    except AnalysisError as e:
        await manager.send_event("failed", {"error": str(e)})
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        await manager.send_event("failed", {"error": str(e)})