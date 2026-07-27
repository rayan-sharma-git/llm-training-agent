"""Framework detection for LLM fine-tuning projects."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List


class FrameworkDetector:
    """Detects fine-tuning frameworks used in a project."""

    FRAMEWORK_SIGNATURES = {
        "huggingface": ["transformers", "datasets", "accelerate", "peft"],
        "peft": ["peft"],
        "trl": ["trl"],
        "unsloth": ["unsloth"],
        "axolotl": ["axolotl"],
    }

    def detect(self, project_path: Path) -> Dict[str, str]:
        """Detect frameworks from requirements and import analysis."""
        detected = []
        version = None
        for pattern in ["requirements.txt", "pyproject.toml", "setup.py", "environment.yml"]:
            req_file = project_path / pattern
            if req_file.exists():
                try:
                    content = req_file.read_text().lower()
                    for framework, keywords in self.FRAMEWORK_SIGNATURES.items():
                        if any(kw in content for kw in keywords):
                            if framework not in detected:
                                detected.append(framework)
                except Exception:
                    pass
        return {
            "framework": detected[0] if detected else "unknown",
            "version": version,
            "all_detected": detected,
        }