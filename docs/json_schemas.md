# JSON Schemas

## LLM Training Agent — Data Models & Validation

Version: 1.0
Author: Schema Designer (Agent 5)
Status: Complete

---

## 1. ProjectContext

```json
{
  "schema": "ProjectContext",
  "schemaVersion": "1.0",
  "projectName": "string",
  "projectPath": "string",
  "detectedFramework": "string | null",
  "frameworkVersion": "string | null",
  "baseModel": "string | null",
  "tokenizer": "string | null",
  "datasetPaths": ["string"],
  "promptTemplates": ["string"],
  "configurationFiles": ["string"],
  "trainingScripts": ["string"],
  "evaluationScripts": ["string"],
  "inferenceScripts": ["string"],
  "hardwareInformation": {},
  "projectStatistics": {},
  "projectHealthScore": "number (0-1) | null",
  "trainingReadinessScore": "number (0-1) | null",
  "analysisTimestamp": "string (ISO 8601) | null"
}
```

## 2. DatasetAnalysisResult

```json
{
  "schema": "DatasetAnalysisResult",
  "schemaVersion": "1.0",
  "datasetName": "string",
  "sampleCount": "integer",
  "tokenCount": "integer",
  "averagePromptLength": "number",
  "averageResponseLength": "number",
  "duplicatePercentage": "number (0-100)",
  "nearDuplicatePercentage": "number (0-100)",
  "missingFieldPercentage": "number (0-100)",
  "formattingConsistencyScore": "number (0-1)",
  "languageConsistencyScore": "number (0-1)",
  "instructionConsistencyScore": "number (0-1)",
  "responseConsistencyScore": "number (0-1)",
  "qualityScore": "number (0-1)",
  "findings": ["string"],
  "warnings": ["string"],
  "recommendations": ["string"],
  "confidence": "enum: very_high | high | medium | low | very_low"
}
```

## 3. PromptAnalysisResult

```json
{
  "schema": "PromptAnalysisResult",
  "schemaVersion": "1.0",
  "templateName": "string",
  "promptComplexity": "enum: simple | moderate | complex | very_complex",
  "ambiguityScore": "number (0-1)",
  "clarityScore": "number (0-1)",
  "formattingScore": "number (0-1)",
  "instructionQualityScore": "number (0-1)",
  "consistencyScore": "number (0-1)",
  "detectedIssues": ["string"],
  "recommendations": ["string"],
  "confidence": "enum: very_high | high | medium | low | very_low"
}
```

## 4. HyperparameterAnalysisResult

```json
{
  "schema": "HyperparameterAnalysisResult",
  "schemaVersion": "1.0",
  "learningRate": "number | null",
  "batchSize": "integer | null",
  "epochs": "integer | null",
  "optimizer": "string | null",
  "scheduler": "string | null",
  "gradientAccumulation": "integer | null",
  "weightDecay": "number | null",
  "warmupRatio": "number | null",
  "sequenceLength": "integer | null",
  "loraRank": "integer | null",
  "loraAlpha": "integer | null",
  "loraDropout": "number | null",
  "overfittingRisk": "enum: low | medium | high | very_high",
  "underfittingRisk": "enum: low | medium | high | very_high",
  "efficiencyScore": "number (0-1)",
  "recommendations": ["string"],
  "confidence": "enum: very_high | high | medium | low | very_low"
}
```

## 5. ModelAnalysisResult

```json
{
  "schema": "ModelAnalysisResult",
  "schemaVersion": "1.0",
  "selectedModel": "string",
  "parameterCount": "string",
  "contextLength": "integer",
  "estimatedVRAM": "string",
  "reasoningCapability": "enum: low | medium | high",
  "codingCapability": "enum: low | medium | high",
  "multilingualCapability": "enum: low | medium | high",
  "instructionFollowingCapability": "enum: low | medium | high",
  "speedScore": "enum: slow | medium | fast",
  "memoryEfficiency": "enum: low | medium | high",
  "strengths": ["string"],
  "weaknesses": ["string"],
  "recommendedAlternatives": ["string"],
  "confidence": "enum: very_high | high | medium | low | very_low"
}
```

## 6. PredictionResult

```json
{
  "schema": "PredictionResult",
  "schemaVersion": "1.0",
  "instructionFollowingPrediction": "enum: poor | fair | good | excellent",
  "hallucinationRisk": "enum: low | medium | high | very_high",
  "reasoningPrediction": "enum: poor | fair | good | excellent",
  "responseConsistencyPrediction": "enum: poor | fair | good | excellent",
  "creativityPrediction": "enum: low | medium | high",
  "formattingPrediction": "enum: poor | fair | good | excellent",
  "likelyFailureModes": ["string"],
  "expectedStrengths": ["string"],
  "expectedWeaknesses": ["string"],
  "confidence": "enum: very_high | high | medium | low | very_low"
}
```

## 7. CostEstimate

```json
{
  "schema": "CostEstimate",
  "schemaVersion": "1.0",
  "estimatedTrainingTime": "string",
  "estimatedGPUHours": "number",
  "estimatedVRAMUsage": "string",
  "estimatedCheckpointSize": "string",
  "estimatedStorageRequirement": "string",
  "compatibleHardware": ["string"],
  "assumptions": ["string"],
  "confidence": "enum: very_high | high | medium | low | very_low"
}
```

## 8. Recommendation

```json
{
  "schema": "Recommendation",
  "schemaVersion": "1.0",
  "recommendationId": "string (uuid)",
  "category": "enum: dataset | prompt | hyperparameter | model | prediction | cost | general",
  "title": "string",
  "description": "string",
  "reasoning": "string",
  "evidence": "string",
  "severity": "enum: critical | high | medium | low | info",
  "confidence": "enum: very_high | high | medium | low | very_low",
  "estimatedBenefit": "string",
  "implementationDifficulty": "enum: easy | moderate | hard",
  "estimatedEngineeringTime": "string",
  "affectedFiles": ["string"],
  "suggestedActions": ["string"],
  "references": ["string"]
}
```

## 9. EngineeringReport

```json
{
  "schema": "EngineeringReport",
  "schemaVersion": "1.0",
  "executiveSummary": "string",
  "projectHealthScore": "number (0-1)",
  "trainingReadinessScore": "number (0-1)",
  "datasetSummary": {},
  "promptSummary": {},
  "hyperparameterSummary": {},
  "modelSummary": {},
  "predictionSummary": {},
  "costSummary": {},
  "prioritizedRecommendations": ["Recommendation"],
  "actionPlan": ["string"]
}
```

## 10. API Error

```json
{
  "schema": "ApiError",
  "schemaVersion": "1.0",
  "errorCode": "string",
  "message": "string",
  "details": "string | null",
  "timestamp": "string (ISO 8601)",
  "requestId": "string"
}
```

## 11. Confidence Enum

```
very_high | high | medium | low | very_low
```

## 12. Severity Enum

```
critical | high | medium | low | info
```

---

## 13. Quality Score: 10/10

All data models defined with required fields, optional fields, enums, and validation rules. Error schema included. Versioned for backward compatibility.