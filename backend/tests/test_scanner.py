"""Tests for ProjectScanner."""
from pathlib import Path
import pytest
from scanner.scanner import ProjectScanner
from scanner.framework_detector import FrameworkDetector


def test_framework_detector_unknown(tmp_path):
    detector = FrameworkDetector()
    result = detector.detect(tmp_path)
    assert result["framework"] == "unknown"


def test_project_scanner_missing_path():
    with pytest.raises(FileNotFoundError):
        ProjectScanner("/nonexistent/path").scan()


def test_project_scanner_basic(tmp_path):
    (tmp_path / "data.json").write_text('{"key": "value"}')
    (tmp_path / "train.py").write_text("print('train')")
    scanner = ProjectScanner(str(tmp_path))
    result = scanner.scan()
    assert result["project_name"] == tmp_path.name
    assert "data.json" in result["dataset_paths"]
    assert "train.py" in result["training_scripts"]