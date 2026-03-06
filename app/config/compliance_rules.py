"""
全局合规红线配置模块。
基于Pydantic实现可动态更新的合规规则库，支持运行时热更新。
"""
import json
import os
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from app.audit.logger import audit_logger


class RiskLevel(str, Enum):
    """风险等级枚举。"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceRule(BaseModel):
    """合规规则数据结构。"""
    rule_id: str = Field(..., description="规则唯一ID")
    rule_name: str = Field(..., description="规则名称")
    description: str = Field("", description="规则描述")
    risk_level: RiskLevel = Field(RiskLevel.MEDIUM, description="风险等级")
    is_active: bool = Field(True, description="是否启用")
    match_pattern: str = Field(..., description="匹配规则，支持正则表达式或关键词列表的JSON字符串")

    class Config:
        use_enum_values = True


class ComplianceRuleManager:
    """
    合规规则管理器，支持增删改查、批量启用/禁用、动态更新。
    规则存储于JSON文件或环境变量，运行时内存缓存。
    """

    def __init__(self, rules_file: str = "compliance_rules.json"):
        self.rules_file = rules_file
        self.rules: Dict[str, ComplianceRule] = {}
        self._load_default_rules()
        self._load_from_file()

    def _load_default_rules(self):
        """加载内置默认规则。"""
        defaults = [
            ComplianceRule(
                rule_id="sensitive_content",
                rule_name="敏感内容检测",
                description="检测涉政、涉黄、涉恐等敏感词汇",
                risk_level=RiskLevel.HIGH,
                match_pattern='["暴恐","色情","政治敏感"]'
            ),
            ComplianceRule(
                rule_id="illegal_content",
                rule_name="违法违规内容拦截",
                description="包含明确违法内容",
                risk_level=RiskLevel.CRITICAL,
                match_pattern='["赌博","毒品","枪支"]'
            ),
            ComplianceRule(
                rule_id="budget_exceed",
                rule_name="预算超限",
                description="预算超出规定上限",
                risk_level=RiskLevel.MEDIUM,
                match_pattern=r'budget\s*>\s*\d+'
            ),
            ComplianceRule(
                rule_id="permission_override",
                rule_name="权限越界",
                description="Agent执行了不属于其职能的操作",
                risk_level=RiskLevel.HIGH,
                match_pattern=r'role\s*!=\s*["\']?[\w]+["\']?'
            ),
            ComplianceRule(
                rule_id="skip_step",
                rule_name="流程跳步",
                description="任务跳过了必要的审批环节",
                risk_level=RiskLevel.HIGH,
                match_pattern='skip_step'
            ),
        ]
        for rule in defaults:
            self.rules[rule.rule_id] = rule

    def _load_from_file(self):
        """从JSON文件加载规则，若文件存在则覆盖默认。"""
        if os.path.exists(self.rules_file):
            try:
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for item in data:
                    rule = ComplianceRule(**item)
                    self.rules[rule.rule_id] = rule
                audit_logger.info(f"从文件加载了 {len(data)} 条合规规则")
            except Exception as e:
                audit_logger.error(f"加载合规规则文件失败: {e}")

    def _save_to_file(self):
        """将当前规则保存到JSON文件。"""
        try:
            data = [rule.dict() for rule in self.rules.values()]
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            audit_logger.info(f"合规规则已保存到 {self.rules_file}")
        except Exception as e:
            audit_logger.error(f"保存合规规则失败: {e}")

    def get_rule(self, rule_id: str) -> Optional[ComplianceRule]:
        return self.rules.get(rule_id)

    def list_rules(self, active_only: bool = False, risk_level: Optional[RiskLevel] = None) -> List[ComplianceRule]:
        rules = list(self.rules.values())
        if active_only:
            rules = [r for r in rules if r.is_active]
        if risk_level:
            rules = [r for r in rules if r.risk_level == risk_level]
        return rules

    def add_rule(self, rule: ComplianceRule) -> None:
        self.rules[rule.rule_id] = rule
        self._save_to_file()

    def update_rule(self, rule_id: str, **updates) -> bool:
        rule = self.get_rule(rule_id)
        if not rule:
            return False
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        self.rules[rule_id] = rule
        self._save_to_file()
        return True

    def delete_rule(self, rule_id: str) -> bool:
        if rule_id in self.rules:
            del self.rules[rule_id]
            self._save_to_file()
            return True
        return False

    def batch_set_active(self, rule_ids: List[str], active: bool) -> int:
        count = 0
        for rid in rule_ids:
            if rid in self.rules:
                self.rules[rid].is_active = active
                count += 1
        if count:
            self._save_to_file()
        return count

    def reload_from_file(self):
        self.rules.clear()
        self._load_default_rules()
        self._load_from_file()
        audit_logger.info("合规规则已热更新")


_compliance_manager = None


def get_compliance_manager() -> ComplianceRuleManager:
    global _compliance_manager
    if _compliance_manager is None:
        _compliance_manager = ComplianceRuleManager()
    return _compliance_manager