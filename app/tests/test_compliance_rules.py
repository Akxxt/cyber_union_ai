import pytest
import tempfile
import os
import json
from app.config.compliance_rules import ComplianceRuleManager, ComplianceRule, RiskLevel


@pytest.fixture
def rules_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('[]')
        f.flush()
        yield f.name
    os.unlink(f.name)


def test_default_rules(rules_file):
    manager = ComplianceRuleManager(rules_file)
    rules = manager.list_rules()
    assert len(rules) >= 5
    assert any(r.rule_id == "sensitive_content" for r in rules)


def test_add_rule(rules_file):
    manager = ComplianceRuleManager(rules_file)
    new_rule = ComplianceRule(
        rule_id="test_rule",
        rule_name="测试规则",
        match_pattern='["test"]',
        risk_level=RiskLevel.LOW
    )
    manager.add_rule(new_rule)
    assert manager.get_rule("test_rule") is not None


def test_update_rule(rules_file):
    manager = ComplianceRuleManager(rules_file)
    manager.update_rule("sensitive_content", is_active=False)
    rule = manager.get_rule("sensitive_content")
    assert rule.is_active is False


def test_delete_rule(rules_file):
    manager = ComplianceRuleManager(rules_file)
    manager.delete_rule("sensitive_content")
    assert manager.get_rule("sensitive_content") is None


def test_batch_set_active(rules_file):
    manager = ComplianceRuleManager(rules_file)
    all_ids = [r.rule_id for r in manager.list_rules()]
    count = manager.batch_set_active(all_ids[:2], False)
    assert count == 2
    for rid in all_ids[:2]:
        assert manager.get_rule(rid).is_active is False


def test_reload(rules_file):
    with open(rules_file, 'w') as f:
        json.dump([{
            "rule_id": "external",
            "rule_name": "外部规则",
            "match_pattern": "external",
            "risk_level": "high",
            "is_active": True
        }], f)
    manager = ComplianceRuleManager(rules_file)
    manager.reload_from_file()
    assert manager.get_rule("external") is not None