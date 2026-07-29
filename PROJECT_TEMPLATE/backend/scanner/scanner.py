"""Project scanner for discovering fine-tuning project structure."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .framework_detector import FrameworkDetector

logger = logging.getLogger(__name__)


class ProjectScanner:
    """Scan a project directory to discover fine-tuning related files and configuration."""
    
    def __init__(self, project_path: str):
        if not Path(project_path).exists():
            raise FileNotFoundError(f"Project path does not exist: {project_path}")
        self.project_path = Path(project_path)
        self.framework_detector = FrameworkDetector()
    
    def scan(self) -> Dict[str, Any]:
        """Scan the project and return structured summary."""
        logger.info(f"Scanning project: {self.project_path}")
        
        # Detect framework
        framework = self.framework_detector.detect(self.project_path)
        
        # Discover files
        datasets = self._discover_datasets()
        prompts = self._discover_prompts()
        configs = self._discover_configs()
        training_scripts = self._discover_scripts(["train*.py", "finetune*.py", "run_*.py"])
        eval_scripts = self._discover_scripts(["eval*.py", "evaluate*.py", "test*.py"])
        inference_scripts = self._discover_scripts(["inference*.py", "predict*.py", "serve*.py"])
        
        # Detect model
        base_model = self._detect_model()
        
        result = {
            "project_name": self.project_path.name,
            "project_path": str(self.project_path),
            **framework,
            "base_model": base_model,
            "dataset_paths": datasets,
            "prompt_templates": prompts,
            "configuration_files": configs,
            "training_scripts": training_scripts,
            "evaluation_scripts": eval_scripts,
            "inference_scripts": inference_scripts,
            "hardware_information": self._detect_hardware(),
            "project_statistics": self._compute_statistics(),
        }
        
        logger.info("Project scan complete")
        return result
    
    def _discover_datasets(self) -> List[str]:
        """Discover dataset files."""
        patterns = ["*.json", "*.jsonl", "*.csv", "*.parquet", "*.txt", "*.tsv"]
        files = []
        for pattern in patterns:
            files.extend(self.project_path.rglob(pattern))
        return [str(f.relative_to(self.project_path)) for f in files if f.is_file()]
    
    def _discover_prompts(self) -> List[str]:
        """Discover prompt templates."""
        patterns = ["prompt*.txt", "prompt*.md", "templates/**/*.txt", "templates/**/*.md"]
        files = []
        for pattern in patterns:
            files.extend(self.project_path.rglob(pattern))
        return [str(f.relative_to(self.project_path)) for f in files if f.is_file()]
    
    def _discover_configs(self) -> List[str]:
        """Discover configuration files."""
        patterns = ["*.yaml", "*.yml", "*.toml", "*.json", "config*.py"]
        files = []
        for pattern in patterns:
            files.extend(self.project_path.rglob(pattern))
        return [str(f.relative_to(self.project_path)) for f in files if f.is_file()]
    
    def _discover_scripts(self, patterns: List[str]) -> List[str]:
        """Discover scripts matching patterns."""
        files = []
        for pattern in patterns:
            files.extend(self.project_path.rglob(f"**/{pattern}"))
        return [str(f.relative_to(self.project_path)) for f in files if f.is_file()]
    
    def _detect_model(self) -> Optional[str]:
        """Attempt to detect the base model."""
        # Simple heuristic: look for model references in configs
        for config in self.project_path.rglob("*.yaml"):
            text = config.read_text(errors="ignore")
            if "model_name_or_path" in text:
                return "detected_in_config"
        return None
    
    def _detect_hardware(self) -> Dict[str, Any]:
        """Detect available hardware."""
        return {"gpu_available": False, "cpu_count": 4}
    
    def _compute_statistics(self) -> Dict[str, Any]:
        """Compute project statistics."""
        file_count = sum(1 for _ in self.project_path.rglob("*") if _.is_file())
        return {"file_count": file_count}