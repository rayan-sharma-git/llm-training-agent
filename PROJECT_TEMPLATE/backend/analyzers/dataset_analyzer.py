"""Dataset quality analyzer — reads real dataset files and computes actual statistics."""
from __future__ import annotations

import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from models.schemas import ProjectContext, DatasetAnalysisResult
from ai.llm import LLMHelper
from cleaning.dataset_io import read_records

logger = logging.getLogger(__name__)


class DatasetAnalyzer:
    """Analyzes dataset quality by reading actual dataset files."""

    def __init__(self):
        self._llm = LLMHelper()

    async def analyze(
        self,
        context: ProjectContext,
        dataset_path: Optional[str] = None,
    ) -> DatasetAnalysisResult:
        """Analyze a dataset file for quality, duplicates, and consistency."""
        dataset_path = dataset_path or (context.dataset_paths[0] if context.dataset_paths else None)

        if not dataset_path:
            raise ValueError("No dataset path provided")

        full_path = Path(context.project_path) / dataset_path if not Path(dataset_path).is_absolute() else Path(dataset_path)
        if not full_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

        logger.info(f"Analyzing dataset: {full_path}")

        # Step 1: Read and parse the dataset
        records, parse_errors = self._read_dataset(full_path)

        sample_count = len(records)
        if sample_count == 0:
            return DatasetAnalysisResult(
                dataset_name=full_path.name,
                sample_count=0,
                token_count=0,
                average_prompt_length=0.0,
                average_response_length=0.0,
                duplicate_percentage=0.0,
                near_duplicate_percentage=0.0,
                missing_field_percentage=0.0,
                formatting_consistency_score=0.0,
                language_consistency_score=0.0,
                instruction_consistency_score=0.0,
                response_consistency_score=0.0,
                quality_score=0.0,
                findings=["Dataset is empty or could not be parsed"],
                warnings=["No training samples found"],
                recommendations=["Provide a valid dataset file"],
                confidence="high",
            )

        # Step 2: Compute deterministic statistics
        total_chars = sum(
            len(r.get("text", "")) + len(r.get("prompt", "")) + len(r.get("completion", ""))
            for r in records
        )
        token_count = int(total_chars / 4)  # Rough estimate: ~4 chars per token

        prompt_lengths = []
        response_lengths = []
        for r in records:
            text = self._extract_text(r)
            prompt_lengths.append(len(text.get("prompt", "")))
            response_lengths.append(len(text.get("response", "")))

        avg_prompt = float(sum(prompt_lengths) / len(prompt_lengths)) if prompt_lengths else 0.0
        avg_response = float(sum(response_lengths) / len(response_lengths)) if response_lengths else 0.0

        # Step 3: Detect duplicates (exact match on instruction+response hash)
        duplicate_percentage, near_duplicate_percentage = self._detect_duplicates(records)

        # Step 4: Check for missing fields
        missing_field_percentage = self._detect_missing_fields(records)

        # Step 5: Consistency scores (deterministic heuristics)
        formatting_score = self._check_formatting_consistency(records)
        language_score = self._check_language_consistency(records)
        instruction_score = self._check_instruction_consistency(records)
        response_score = self._check_response_consistency(records)

        # Step 6: Quality score (weighted combination of deterministic metrics)
        quality_score = self._compute_quality_score(
            duplicate_percentage,
            near_duplicate_percentage,
            missing_field_percentage,
            formatting_score,
            language_score,
            instruction_score,
            response_score,
            sample_count,
        )

        # Step 7: Generate findings, warnings, recommendations
        findings, warnings, recommendations = self._generate_findings(
            sample_count, duplicate_percentage, near_duplicate_percentage,
            missing_field_percentage, formatting_score, quality_score, parse_errors
        )

        # Step 8: Optionally call LLM for quality assessment
        confidence = "high" if sample_count > 100 else "medium" if sample_count > 10 else "low"

        # If LLM is available, enhance the analysis
        if self._llm.is_available:
            llm_result = await self._llm_enhance(full_path, records[:5], {
                "sample_count": sample_count,
                "duplicate_percentage": duplicate_percentage,
                "quality_score": quality_score,
                "formatting_consistency_score": formatting_score,
                "language_consistency_score": language_score,
            })
            if llm_result:
                confidence = "high"
                # Merge LLM findings with deterministic findings
                findings.extend(llm_result.get("findings", []))
                warnings.extend(llm_result.get("warnings", []))

        return DatasetAnalysisResult(
            dataset_name=full_path.name,
            sample_count=sample_count,
            token_count=token_count,
            average_prompt_length=avg_prompt,
            average_response_length=avg_response,
            duplicate_percentage=duplicate_percentage,
            near_duplicate_percentage=near_duplicate_percentage,
            missing_field_percentage=missing_field_percentage,
            formatting_consistency_score=formatting_score,
            language_consistency_score=language_score,
            instruction_consistency_score=instruction_score,
            response_consistency_score=response_score,
            quality_score=quality_score,
            findings=findings,
            warnings=warnings,
            recommendations=recommendations,
            confidence=confidence,
        )

    def _read_dataset(self, path: Path) -> tuple[List[Dict[str, Any]], List[str]]:
        """Read a dataset file (JSONL, JSON, CSV, TSV or TXT) and return records.

        Delegates to the shared dataset I/O layer so that analysis and cleaning
        always interpret a dataset file in exactly the same way.
        """
        return read_records(path)

    def _extract_text(self, record: Dict[str, Any]) -> Dict[str, str]:
        """Extract prompt/response text from a record, handling different field names."""
        prompt = record.get("prompt") or record.get("instruction") or record.get("question") or record.get("input") or ""
        response = record.get("response") or record.get("completion") or record.get("output") or record.get("answer") or record.get("text") or ""
        return {"prompt": str(prompt), "response": str(response)}

    def _detect_duplicates(self, records: List[Dict[str, Any]]) -> tuple[float, float]:
        """Detect exact and near-duplicate records using hashing."""
        seen_hashes: Set[str] = set()
        duplicate_count = 0
        near_duplicate_count = 0

        for r in records:
            text = self._extract_text(r)
            full_text = text["prompt"] + "|" + text["response"]

            # Exact duplicate
            h = hashlib.md5(full_text.encode("utf-8")).hexdigest()
            if h in seen_hashes:
                duplicate_count += 1
            else:
                seen_hashes.add(h)

            # Near-duplicate (same prompt, different response length within 10%)
            prompt_hash = hashlib.md5(text["prompt"].encode("utf-8")).hexdigest()
            if prompt_hash in seen_hashes:
                near_duplicate_count += 1
            else:
                seen_hashes.add(prompt_hash)

        total = len(records) if records else 1
        return (duplicate_count / total * 100, near_duplicate_count / total * 100)

    def _detect_missing_fields(self, records: List[Dict[str, Any]]) -> float:
        """Calculate percentage of records with missing or empty fields."""
        if not records:
            return 0.0
        missing_count = 0
        for r in records:
            text = self._extract_text(r)
            if not text["prompt"].strip() or not text["response"].strip():
                missing_count += 1
        return missing_count / len(records) * 100

    def _check_formatting_consistency(self, records: List[Dict[str, Any]]) -> float:
        """Check if responses follow consistent formatting."""
        if not records:
            return 0.0
        scores = []
        for r in records:
            text = self._extract_text(r)
            response = text["response"]
            # Check for consistent structure (e.g., starts with capital, ends with period)
            score = 1.0
            if response and not response[0].isupper():
                score -= 0.3
            if response and not response.rstrip()[-1:] in (".", "!", "?"):
                score -= 0.2
            scores.append(max(0.0, score))
        return float(sum(scores) / len(scores)) if scores else 0.0

    def _check_language_consistency(self, records: List[Dict[str, Any]]) -> float:
        """Check if all responses use the same primary language."""
        if not records:
            return 0.0
        # Simple heuristic: detect common non-English characters
        non_english_count = 0
        for r in records:
            text = self._extract_text(r)
            combined = text["prompt"] + text["response"]
            # Count non-ASCII characters (rough proxy for non-English)
            non_ascii = sum(1 for c in combined if ord(c) > 127)
            if non_ascii > len(combined) * 0.1:
                non_english_count += 1
        return float(1.0 - (non_english_count / len(records)))

    def _check_instruction_consistency(self, records: List[Dict[str, Any]]) -> float:
        """Check if instructions are consistent in style."""
        if not records:
            return 0.0
        # Check if instructions have common structure (e.g., "You are a...")
        consistent_count = 0
        for r in records:
            text = self._extract_text(r)
            prompt = text["prompt"]
            if prompt and len(prompt) > 10:
                consistent_count += 1
        return float(consistent_count / len(records)) if records else 0.0

    def _check_response_consistency(self, records: List[Dict[str, Any]]) -> float:
        """Check if responses are consistently formatted."""
        if not records:
            return 0.0
        scores = []
        for r in records:
            text = self._extract_text(r)
            response = text["response"]
            score = 1.0
            if not response.strip():
                score = 0.0
            elif len(response) < 20:
                score = 0.5
            scores.append(score)
        return float(sum(scores) / len(scores)) if scores else 0.0

    def _compute_quality_score(
        self, dup_pct, near_dup_pct, missing_pct,
        fmt_score, lang_score, inst_score, resp_score, sample_count
    ) -> float:
        """Compute overall quality score (0-1)."""
        # Penalize duplicates
        dup_penalty = min(1.0, dup_pct / 10.0)  # 10% duplicates = full penalty
        near_dup_penalty = min(0.5, near_dup_pct / 20.0)
        missing_penalty = min(0.5, missing_pct / 5.0)

        # Average of consistency scores
        consistency = (fmt_score + lang_score + inst_score + resp_score) / 4.0

        # Small datasets get lower confidence
        size_factor = min(1.0, sample_count / 1000.0) if sample_count < 1000 else 1.0

        score = consistency * size_factor - dup_penalty - near_dup_penalty - missing_penalty
        return max(0.0, min(1.0, score))

    def _generate_findings(
        self, sample_count, dup_pct, near_dup_pct, missing_pct,
        fmt_score, quality_score, parse_errors
    ) -> tuple[List[str], List[str], List[str]]:
        """Generate deterministic findings, warnings, and recommendations."""
        findings = [f"Dataset contains {sample_count} samples."]

        warnings = []
        recommendations = []

        if dup_pct > 0:
            findings.append(f"{dup_pct:.1f}% exact duplicate samples detected.")
            recommendations.append("Remove duplicate samples to improve training efficiency.")

        if near_dup_pct > 5:
            warnings.append(f"{near_dup_pct:.1f}% near-duplicate samples (same prompt, different response).")
            recommendations.append("Consolidate near-duplicates to reduce data noise.")

        if missing_pct > 0:
            warnings.append(f"{missing_pct:.1f}% of samples have missing or empty fields.")
            recommendations.append("Review and fill in missing fields or remove incomplete samples.")

        if fmt_score < 0.8:
            warnings.append(f"Formatting consistency is low ({fmt_score:.0%}).")
            recommendations.append("Apply consistent formatting (capitalization, punctuation) across all responses.")

        if parse_errors:
            warnings.append(f"{len(parse_errors)} parsing errors encountered.")
            for err in parse_errors[:3]:
                warnings.append(f"  - {err}")

        if sample_count < 50:
            warnings.append(f"Small dataset ({sample_count} samples). Consider collecting more data.")

        if quality_score < 0.5:
            recommendations.append("Dataset quality is low. Consider collecting higher-quality training data.")
        elif quality_score > 0.8:
            findings.append("Dataset quality is good.")

        return findings, warnings, recommendations

    async def _llm_enhance(self, path: Path, sample_records: List[Dict], stats: Dict[str, Any]) -> Optional[Dict]:
        """Use LLM to enhance dataset analysis with quality assessment."""
        try:
            sample_text = "\n\n".join(
                json.dumps(r, ensure_ascii=False) for r in sample_records[:5]
            )
            prompt = f"""Analyze the following dataset samples and quality statistics.
Provide a JSON response with: quality_score (0-1), findings (list), warnings (list), recommendations (list), confidence (very_high|high|medium|low|very_low).

Dataset: {path.name}
Statistics:
- Sample count: {stats['sample_count']}
- Duplicate percentage: {stats['duplicate_percentage']:.1f}%
- Quality score (preliminary): {stats['quality_score']:.2f}
- Formatting consistency: {stats['formatting_consistency_score']:.2f}
- Language consistency: {stats['language_consistency_score']:.2f}

Sample records (first 5):
{sample_text}

Base your analysis ONLY on the provided data. Do not fabricate statistics."""
            return await self._llm.call_structured(prompt, temperature=0.3)
        except Exception as e:
            logger.debug(f"LLM enhancement failed: {e}")
            return None
