"""Project scanner for detecting fine-tuning project components."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from scanner.framework_detector import FrameworkDetector


class ProjectScanner:
    """Scans project directory to detect framework, datasets, configs, models."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.framework_detector = FrameworkDetector()

    def scan(self) -> Dict[str, Any]:
        """Perform full project scan."""
        if not self.project_path.exists():
            raise FileNotFoundError(f"Project path not found: {self.project_path}")
        framework_info = self.framework_detector.detect(self.project_path)
        return {
            "project_name": self.project_path.name,
            "project_path": str(self.project_path),
            "detected_framework": framework_info.get("framework"),
            "framework_version": framework_info.get("version"),
            "base_model": self._detect_base_model(),
            "tokenizer": self._detect_tokenizer(),
            "dataset_paths": self._discover_datasets(),
            "prompt_templates": self._discover_prompts(),
            "configuration_files": self._discover_configs(),
            "training_scripts": self._discover_scripts("train"),
            "evaluation_scripts": self._discover_scripts("eval"),
            "inference_scripts": self._discover_scripts("infer"),
            "hardware_information": self._detect_hardware(),
            "project_statistics": self._compute_statistics(),
        }

    def _detect_base_model(self) -> Optional[str]:
        """Detect base model from config files."""
        for pattern in ["**/config.json", "**/training_args.json", "**/*.yaml", "**/*.yml"]:
            for path in self.project_path.glob(pattern):
                try:
                    content = path.read_text()
                    if "base_model" in content or "model_name" in content:
                        return "detected-from-config"
                except Exception:
                    pass
        return None

    def _detect_tokenizer(self) -> Optional[str]:
        """Detect tokenizer from config files."""
        for pattern in ["**/tokenizer_config.json", "**/tokenizer.json"]:
            for path in self.project_path.glob(pattern):
                if path.exists():
                    return path.parent.name
        return None

    def _discover_datasets(self) -> List[str]:
        """Discover dataset files."""
        patterns = ["**/*.json", "**/*.jsonl", "**/*.csv", "**/*.parquet"]
        datasets = []
        for pattern in patterns:
            datasets.extend(str(p.relative_to(self.project_path)) for p in self.project_path.glob(pattern) if p.is_file())
        return datasets[:50]

    def _discover_prompts(self) -> List[str]:
        """Discover prompt template files."""
        patterns = ["**/prompt*.txt", "**/prompt*.md", "**/template*.txt", "**/template*.md"]
        prompts = []
        for pattern in patterns:
            prompts.extend(str(p.relative_to(self.project_path)) for p in self.project_path.glob(pattern) if p.is_file())
        return prompts[:20]

    def _discover_configs(self) -> List[str]:
        """Discover configuration files."""
        patterns = ["**/*.yaml", "**/*.yml", "**/*.toml", "**/*.json"]
        configs = []
        for pattern in patterns:
            configs.extend(str(p.relative_to(self.project_path)) for p in self.project_path.glob(pattern) if p.is_file())
        return configs[:30]

    def _discover_scripts(self, keyword: str) -> List[str]:
        """Discover training/evaluation/inference scripts."""
        scripts = []
        for p in self.project_path.rglob("*.py"):
            if keyword in p.name.lower():
                scripts.append(str(p.relative_to(self.project_path)))
        return scripts[:20]

    def _detect_hardware(self) -> Dict[str, Any]:
        """Detect available hardware information."""
        return {"gpu_available": False, "cpu_count": os.cpu_count()}

    def _compute_statistics(self) -> Dict[str, Any]:
        """Compute basic project statistics."""
        file_count = sum(1 for _ in self.project_path.rglob("*") if _.is_file())
        total_size = sum(f.stat().st_size for f in self.project_path.rglob("*") if f.is_file())
        return {"file_count": file_count, "total_size_bytes": total_size}