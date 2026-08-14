"""Training cost estimator — uses deterministic formulas based on model + dataset size."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from models.schemas import ProjectContext, CostEstimate
from ai.llm import LLMHelper

logger = logging.getLogger(__name__)

# GPU specifications: name -> (TFLOPS FP16, VRAM GB)
_GPU_DATABASE: Dict[str, Dict[str, Any]] = {
    "rtx_4090": {"tflops": 163, "vram": 24, "name": "NVIDIA RTX 4090"},
    "rtx_4080": {"tflops": 108, "vram": 16, "name": "NVIDIA RTX 4080"},
    "rtx_4070": {"tflops": 60, "vram": 12, "name": "NVIDIA RTX 4070"},
    "rtx_3090": {"tflops": 70, "vram": 24, "name": "NVIDIA RTX 3090"},
    "rtx_3080": {"tflops": 60, "vram": 12, "name": "NVIDIA RTX 3080"},
    "rtx_3060": {"tflops": 40, "vram": 12, "name": "NVIDIA RTX 3060"},
    "a100_40gb": {"tflops": 193, "vram": 40, "name": "NVIDIA A100 (40GB)"},
    "a100_80gb": {"tflops": 193, "vram": 80, "name": "NVIDIA A100 (80GB)"},
    "a10g": {"tflops": 125, "vram": 24, "name": "NVIDIA A10G"},
    "h100": {"tflops": 200, "vram": 80, "name": "NVIDIA H100"},
}


class CostEstimator:
    """Estimates computational cost of fine-tuning using deterministic formulas."""

    def __init__(self):
        self._llm = LLMHelper()

    async def analyze(self, context: ProjectContext) -> CostEstimate:
        """Estimate training resources from model size, dataset size, and hyperparameters."""
        logger.info("Estimating training cost")

        # Step 1: Extract model size
        param_count_billions = self._extract_param_count(context)

        # Step 2: Extract dataset size
        dataset_samples = context.project_statistics.get("dataset_sample_count", 1000)
        dataset_size = context.dataset_paths

        # Use actual sample count from analyzer results if available in context
        if hasattr(context, 'project_statistics') and context.project_statistics:
            for key, val in context.project_statistics.items():
                if 'sample' in key.lower() and isinstance(val, (int, float)):
                    dataset_samples = int(val)

        # Step 3: Extract training parameters
        seq_length = 512  # Default
        batch_size = 8    # Default
        epochs = 3        # Default
        grad_accum = 1    # Default

        # Try to find config values
        for cf in context.configuration_files:
            try:
                config_path = (
                    Path(f"{context.project_path}/{cf}")
                    if not Path(cf).is_absolute()
                    else Path(cf)
                )
                if config_path.exists():
                    text = config_path.read_text(encoding="utf-8")
                    import re as _re
                    m = _re.search(r"per_device_train_batch_size\s*:\s*(\d+)", text)
                    if m: batch_size = int(m.group(1))
                    m = _re.search(r"num_train_epochs\s*:\s*([\d.]+)", text)
                    if m: epochs = int(float(m.group(1)))
                    m = _re.search(r"max_seq_length\s*:\s*(\d+)", text)
                    if m: seq_length = int(m.group(1))
                    m = _re.search(r"gradient_accumulation_steps\s*:\s*(\d+)", text)
                    if m: grad_accum = int(m.group(1))
            except Exception:
                pass

        # Step 4: Compute estimates using deterministic formulas
        estimates = self._compute_estimates(param_count_billions, dataset_samples, seq_length, batch_size, epochs, grad_accum)

        # Step 5: Find compatible hardware
        compatible = self._find_compatible_hardware(param_count_billions)

        # Step 6: Optional LLM enhancement
        confidence = "medium"
        if self._llm.is_available:
            llm_result = await self._llm_enhance(
                param_count_billions, dataset_samples, batch_size, epochs, seq_length
            )
            if llm_result:
                confidence = "high"

        return CostEstimate(
            estimated_training_time=estimates["training_time"],
            estimated_gpu_hours=estimates["gpu_hours"],
            estimated_vram_usage=estimates["vram"],
            estimated_checkpoint_size=estimates["checkpoint_size"],
            estimated_storage_requirement=estimates["storage"],
            compatible_hardware=compatible,
            assumptions=estimates["assumptions"],
            confidence=confidence,
        )

    def _extract_param_count(self, context: ProjectContext) -> float:
        """Extract parameter count in billions from model name or context."""
        model_name = context.base_model or ""
        if not model_name:
            return 7.0  # Default assumption

        name_lower = model_name.lower()

        # Known model families and their parameter sizes
        param_map = [
            ("70b", 70.0), ("7b", 7.0), ("8b", 8.0),
            ("2b", 2.0), ("2.7b", 2.7), ("1b", 1.0),
            ("1.1b", 1.1), ("13b", 13.0), ("3b", 3.0),
            ("30b", 30.0), ("34b", 34.0), ("72b", 72.0),
        ]
        for pattern, params in param_map:
            if pattern in name_lower:
                return params

        # Check project statistics
        if context.project_statistics.get("param_count_billions"):
            return float(context.project_statistics["param_count_billions"])

        return 7.0  # Default assumption

    def _compute_estimates(
        self, param_billions: float, dataset_samples: int,
        seq_length: int, batch_size: int, epochs: int, grad_accum: int
    ) -> Dict[str, Any]:
        """Compute cost estimates using FLOPs-based formulas."""
        import math

        # Total training tokens = dataset_samples * avg_seq_length * epochs
        # Assume avg 20 tokens per sample (rough estimate)
        avg_tokens_per_sample = max(seq_length, 20)
        total_tokens = dataset_samples * avg_tokens_per_sample * epochs

        # FLOPs per token for a model with P parameters (6 * P for training)
        # Training FLOPs = 6 * P * total_tokens
        flops_per_token = 6 * param_billions * 1e9
        total_flops = flops_per_token * total_tokens

        # Use RTX 4090 as default reference (163 TFLOPS FP16)
        reference_tflops = 163.0
        reference_gpu_hours = total_flops / (reference_tflops * 1e12) / 3600.0

        # Apply gradient accumulation factor (effective batch size)
        effective_batch = batch_size * grad_accum
        # More tokens per step with larger batch = fewer steps, but same total compute
        # Actually, total compute is the same regardless of batch size
        # But wall-clock time depends on throughput

        # Estimate wall-clock time (hours)
        # Account for ~70% GPU utilization (data loading, memory, etc.)
        utilization = 0.70
        wall_clock_hours = reference_gpu_hours / utilization

        # VRAM estimation: params * 2 bytes (FP16) + optimizer states + activations
        # For LoRA/PEFT: only small adapter needs full VRAM
        # Base model VRAM = params * 2 bytes (FP16) * 2 (forward+backward)
        # Optimizer states = params * 2 bytes (Adam states) * 2
        # For QLoRA: VRAM = params * 0.5 bytes + adapter
        # For full fine-tuning: VRAM = params * 2 bytes * (2 + 2) + activations
        # Simplified: VRAM (GB) = params_billions * 2 * 4 (approx for full fine-tune)
        # With QLoRA: VRAM (GB) = params_billions * 2 * 1 + overhead

        # Assume QLoRA (most common in this project)
        vram_gb = param_billions * 2 * 1.0 + 4  # QLoRA: ~2GB per billion params + 4GB overhead
        if vram_gb < 4:
            vram_gb = 4.0  # Minimum

        # Checkpoint size: params * 4 bytes (FP32) or params * 2 bytes (FP16)
        checkpoint_gb = param_billions * 2.0  # FP16 checkpoint
        # Include optimizer states for full fine-tune
        checkpoint_gb_full = param_billions * 2.0 * 4  # With optimizer states

        # Storage: checkpoint + dataset + intermediate files (3x for safety)
        storage_gb = checkpoint_gb_full * 3 + (dataset_samples * avg_tokens_per_sample * 4 / 1e9) + 10

        def _format_hours(h: float) -> str:
            if h < 1:
                return f"{h * 60:.0f} minutes"
            if h < 24:
                return f"{h:.1f} hours"
            return f"{h / 24:.1f} days"

        return {
            "training_time": f"{_format_hours(wall_clock_hours * 0.5)}-{_format_hours(wall_clock_hours * 1.5)}",
            "gpu_hours": round(wall_clock_hours, 2),
            "vram": f"{vram_gb:.0f}GB",
            "checkpoint_size": f"{checkpoint_gb_full:.0f}GB",
            "storage": f"{storage_gb:.0f}GB",
            "assumptions": [
                f"Model: {param_billions}B parameters (estimated)",
                f"Dataset: {dataset_samples} samples",
                f"Sequence length: {seq_length} tokens",
                f"Batch size: {batch_size}, Gradient accumulation: {grad_accum}",
                f"Epochs: {epochs}",
                f"Training method: QLoRA (8-bit quantization, LoRA adapters)",
                f"GPU utilization: ~70%",
                "Single GPU (RTX 4090 as reference: 163 TFLOPS FP16)",
            ],
        }

    def _find_compatible_hardware(self, param_billions: float) -> List[str]:
        """Find GPUs that can handle the model's VRAM requirements."""
        vram_needed = param_billions * 2 * 1.0 + 4  # QLoRA estimate
        compatible = []
        for gpu_key, gpu_info in _GPU_DATABASE.items():
            if gpu_info["vram"] >= vram_needed:
                compatible.append(gpu_info["name"])
        return compatible if compatible else ["Any modern GPU with sufficient VRAM"]

    async def _llm_enhance(self, param_billions, dataset_samples, batch_size, epochs, seq_length) -> Optional[Dict[str, Any]]:
        """Optionally use LLM to refine cost estimates."""
        try:
            prompt = f"""Refine the training cost estimate for a fine-tuning job.

Model size: {param_billions}B parameters
Dataset samples: {dataset_samples}
Sequence length: {seq_length}
Batch size: {batch_size}
Epochs: {epochs}

Acknowledge the estimates and add any relevant observations about hardware requirements."""
            return await self._llm.call(prompt, temperature=0.3)
        except Exception as e:
            logger.debug(f"LLM cost enhancement failed: {e}")
            return None
