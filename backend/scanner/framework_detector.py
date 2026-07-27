"""Framework detection logic."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class FrameworkDetector:
    """Detect fine-tuning frameworks in a project."""
    
    FRAMEWORK_INDICATORS = {
        "huggingface": ["transformers", "datasets", "peft", "trl", "accelerate"],
        "axolotl": ["axolotl", "train"],
        "unsloth": ["unsloth"],
    }
    
    def detect(self, project_path: Path) -> Dict[str, Optional[str]]:
        """Detect framework used in the project."""
        project_path = Path(project_path)
        
        # Check requirements files
        req_files = ["requirements.txt", "pyproject.toml", "setup.py"]
        dependencies = []
        
        for req_file in req_files:
            req_path = project_path / req_file
            if req_path.exists():
                dependencies.extend(self._extract_dependencies(req_path))
        
        # Check for framework indicators
        detected_framework = "unknown"
        detected_version = None
        
        for framework, indicators in self.FRAMEWORK_INDICATORS.items():
            for indicator in indicators:
                if any(indicator in dep for dep in dependencies):
                    detected_framework = framework
                    break
        
        return {
            "framework": detected_framework,
            "framework_version": detected_version,
        }
    
    def _extract_dependencies(self, file_path: Path) -> List[str]:
        """Extract dependencies from requirements file."""
        deps = []
        try:
            if file_path.name == "requirements.txt":
                deps = file_path.read_text().splitlines()
            elif file_path.name == "pyproject.toml":
                import tomllib
                with open(file_path, "rb") as f:
                    data = tomllib.load(f)
                deps = data.get("project", {}).get("dependencies", [])
        except Exception:
            pass
        return [d.strip().split("==")[0].split(">=")[0].split("<=")[0].lower() for d in deps if d.strip()]