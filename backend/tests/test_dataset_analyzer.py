"""Tests for DatasetAnalyzer."""
import pytest
from analyzers.dataset_analyzer import DatasetAnalyzer
from models.schemas import ProjectContext


@pytest.fixture
def analyzer():
    return DatasetAnalyzer()


@pytest.fixture
def sample_context():
    return ProjectContext(project_name="test", project_path="/tmp", dataset_paths=["data.json"])


@pytest.mark.asyncio
async def test_dataset_analyzer_success(analyzer, sample_context):
    result = await analyzer.analyze(sample_context)
    assert result["dataset_name"] == "data.json"
    assert result["sample_count"] == 1000
    assert "quality_score" in result
    assert "confidence" in result


@pytest.mark.asyncio
async def test_dataset_analyzer_no_dataset(analyzer):
    context = ProjectContext(project_name="test", project_path="/tmp", dataset_paths=[])
    with pytest.raises(Exception):
        await analyzer.analyze(context)