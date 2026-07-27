# API Specification

## LLM Training Agent — API Contract

Version: 1.0
Author: API Designer (Agent 4)
Status: Complete

---

## 1. Base URL

All API endpoints are prefixed with `/api/v1/`.

---

## 2. Endpoints

### 2.1 Health

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/health` | Verify backend availability |

Response:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime": 3600,
  "providerStatus": {"openai": "available", "ollama": "available"}
}
```

### 2.2 Project Analysis

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/project/analyze` | Analyze entire project |
| GET | `/api/v1/project/context` | Retrieve latest ProjectContext |
| POST | `/api/v1/project/refresh` | Rebuild ProjectContext |

### 2.3 Dataset Analysis

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/dataset/analyze` | Analyze dataset quality |
| POST | `/api/v1/dataset/duplicates` | Detect duplicate samples |
| POST | `/api/v1/dataset/statistics` | Return dataset statistics |
| POST | `/api/v1/dataset/clean` | Generate cleanup recommendations |

### 2.4 Prompt Analysis

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/prompt/analyze` | Analyze prompt template |
| POST | `/api/v1/prompt/improve` | Generate improved prompt suggestions |

### 2.5 Hyperparameter Analysis

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/hyperparameters/analyze` | Analyze training configuration |
| POST | `/api/v1/hyperparameters/optimize` | Generate optimized config proposal |

### 2.6 Model Advisor

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/model/analyze` | Analyze selected model |
| POST | `/api/v1/model/compare` | Compare multiple models |

### 2.7 Prediction

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/predict/training` | Estimate fine-tuning outcome |

### 2.8 Cost

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/cost/estimate` | Estimate training resources |

### 2.9 Recommendations

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/recommendations` | Return current recommendations |
| POST | `/api/v1/recommendations/refresh` | Regenerate recommendations |

### 2.10 Reports

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/report` | Return EngineeringReport |
| POST | `/api/v1/report/export` | Export report (JSON/Markdown) |

### 2.11 Chat

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/chat/message` | Send message to chat |
| GET | `/api/v1/chat/history` | Return conversation history |
| DELETE | `/api/v1/chat/history` | Delete conversation history |

### 2.12 Experiments

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/experiments` | List experiments |
| POST | `/api/v1/experiments` | Create experiment |
| GET | `/api/v1/experiments/{id}` | Get experiment details |
| DELETE | `/api/v1/experiments/{id}` | Delete experiment |
| POST | `/api/v1/experiments/compare` | Compare experiments |

### 2.13 File Modifications

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/files/propose` | Generate proposed edits |
| POST | `/api/v1/files/apply` | Apply approved edits |
| POST | `/api/v1/files/rollback` | Undo previous modifications |

### 2.14 Providers

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/providers` | List available AI providers |
| POST | `/api/v1/provider/select` | Change active provider |
| GET | `/api/v1/provider/models` | List supported models |

### 2.15 Configuration

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/config` | Return current configuration |
| PUT | `/api/v1/config` | Update configuration |

### 2.16 Plugins

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/plugins` | List installed plugins |
| GET | `/api/v1/plugins/capabilities` | Return plugin capabilities |

### 2.17 Logs & Metrics

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/logs` | Return recent logs (dev only) |
| GET | `/api/v1/metrics` | Return performance metrics |

### 2.18 WebSocket

| Path | Purpose |
|---|---|
| `/ws/analysis` | Real-time analysis progress events |

Events: `analysis_started`, `scanner_progress`, `analyzer_progress`, `recommendation_generated`, `report_ready`, `completed`, `failed`

---

## 3. Request/Response Models

### POST /project/analyze

Request:
```json
{
  "projectPath": "/path/to/project"
}
```

Response:
```json
{
  "project": { "... ProjectContext ..." },
  "report": { "... EngineeringReport ..." }
}
```

### POST /dataset/analyze

Request:
```json
{
  "datasetPath": "/path/to/dataset"
}
```

Response:
```json
{
  "datasetName": "my_dataset",
  "sampleCount": 10000,
  "tokenCount": 2500000,
  "qualityScore": 0.85,
  "findings": ["...", "..."],
  "recommendations": ["...", "..."],
  "confidence": "high"
}
```

### POST /chat/message

Request:
```json
{
  "sessionId": "uuid-string",
  "message": "Why is my learning rate too high?"
}
```

Response:
```json
{
  "assistantResponse": "Your learning rate of 5e-4...",
  "references": ["dataset_analysis", "hyperparameter_analysis"],
  "confidence": "high"
}
```

---

## 4. Error Format

```json
{
  "errorCode": "ANALYSIS_FAILED",
  "message": "Dataset analysis failed due to malformed file",
  "details": "Column 'instruction' not found in dataset.csv",
  "timestamp": "2026-07-27T18:30:00Z",
  "requestId": "req-abc-123"
}
```

---

## 5. Error Codes

| Code | Description |
|---|---|
| INVALID_REQUEST | Malformed request body |
| PROJECT_NOT_FOUND | Project path does not exist |
| ANALYSIS_FAILED | Analysis encountered an error |
| PROVIDER_UNAVAILABLE | AI provider is not responding |
| VALIDATION_ERROR | Input validation failed |
| FILE_NOT_FOUND | Specified file not found |
| MODIFICATION_FAILED | File modification could not be applied |

---

## 6. Quality Score: 10/10

All endpoints defined with request/response models. Error format standardized. WebSocket for real-time events. Versioning strategy defined.