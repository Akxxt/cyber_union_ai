import pytest
from app.audit.compliance import ComplianceEngine, ComplianceReport
from app.core.constants import ReviewResult


@pytest.fixture
def engine():
    return ComplianceEngine()


def test_content_compliance_pass(engine):
    report = engine.check_content_compliance("task1", "这是一段正常文本", "test")
    assert report.review_result == ReviewResult.PASSED
    assert len(report.violations) == 0


def test_content_compliance_violation(engine):
    report = engine.check_content_compliance("task1", "包含暴恐内容", "test")
    assert len(report.violations) > 0
    assert report.risk_level.value == "high"


def test_constitutional_review_pass(engine):
    legislation = "宪法民主法治齐全"
    report = engine.check_constitutional_review("task1", legislation)
    # 由于基本法检查可能因缺少关键词而失败，这里用全部包含的文本
    legislation = "宪法民主法治齐全"
    report = engine.check_constitutional_review("task1", legislation)
    assert report.review_result == ReviewResult.PASSED


def test_generate_report(engine):
    report = engine.check_content_compliance("task1", "暴恐", "test")
    text = engine.generate_compliance_report(report)
    assert "违规项详情" in text
    assert "暴恐" in text


@pytest.mark.asyncio
async def test_update_rules(engine):
    await engine.update_compliance_rules()