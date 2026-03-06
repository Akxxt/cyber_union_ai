"""
合规校验引擎。
基于Step1审计日志和全局合规红线库，提供内容合规检测、违宪审查、报告生成。
"""
import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.config.compliance_rules import ComplianceRule, RiskLevel, get_compliance_manager
from app.audit.logger import audit_logger
from app.core.constants import ReviewResult


class ComplianceViolation(BaseModel):
    """单个违规项。"""
    rule_id: str
    rule_name: str
    matched_text: str
    risk_level: RiskLevel
    suggestion: str = ""


class ComplianceReport(BaseModel):
    """合规审查报告。"""
    task_id: str
    content_type: str
    content: str
    violations: List[ComplianceViolation]
    risk_level: RiskLevel = RiskLevel.LOW
    review_result: ReviewResult
    review_comment: str = ""
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def is_compliant(self) -> bool:
        return self.review_result == ReviewResult.PASSED


class ComplianceEngine:
    """
    合规校验引擎，提供各类审查功能。
    """

    def __init__(self):
        self.rule_manager = get_compliance_manager()
        self.logger = audit_logger

    def _match_rule(self, text: str, rule: ComplianceRule) -> List[str]:
        """根据规则匹配文本，返回所有匹配的内容片段。"""
        try:
            patterns = json.loads(rule.match_pattern)
            if isinstance(patterns, list):
                matches = []
                for pat in patterns:
                    if pat in text:
                        matches.append(pat)
                return matches
        except (json.JSONDecodeError, TypeError):
            pass

        try:
            compiled = re.compile(rule.match_pattern, re.IGNORECASE)
            return compiled.findall(text)
        except re.error:
            self.logger.error(f"规则 {rule.rule_id} 的正则表达式无效: {rule.match_pattern}")
            return []

    def _risk_level_value(self, level: RiskLevel) -> int:
        mapping = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
        return mapping.get(level, 1)

    def _generate_comment(self, violations: List[ComplianceViolation]) -> str:
        if not violations:
            return "内容合规，无违规项。"
        levels = [v.risk_level.value for v in violations]
        max_level = max(levels, key=lambda x: self._risk_level_value(RiskLevel(x)))
        return f"发现 {len(violations)} 项违规，最高风险等级: {max_level}"

    def check_content_compliance(self, task_id: str, content: str, content_type: str) -> ComplianceReport:
        """
        文本内容合规检测。
        """
        violations = []
        max_risk = RiskLevel.LOW

        rules = self.rule_manager.list_rules(active_only=True)

        for rule in rules:
            matches = self._match_rule(content, rule)
            if matches:
                for match in matches[:5]:
                    violation = ComplianceViolation(
                        rule_id=rule.rule_id,
                        rule_name=rule.rule_name,
                        matched_text=match,
                        risk_level=rule.risk_level,
                        suggestion=f"请移除或修改违规内容: {match}"
                    )
                    violations.append(violation)
                    if self._risk_level_value(rule.risk_level) > self._risk_level_value(max_risk):
                        max_risk = rule.risk_level

        review_result = ReviewResult.PASSED
        if max_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            review_result = ReviewResult.REJECTED
        elif violations:
            review_result = ReviewResult.MODIFIED

        report = ComplianceReport(
            task_id=task_id,
            content_type=content_type,
            content=content,
            violations=violations,
            risk_level=max_risk,
            review_result=review_result,
            review_comment=self._generate_comment(violations)
        )

        self.logger.info(
            f"合规检测完成: {content_type}, 结果: {review_result}, 违规数: {len(violations)}",
            task_id=task_id
        )
        return report

    async def check_constitutional_review(
        self,
        task_id: str,
        legislation: str,
        basic_law: str = "《执行基本法》"
    ) -> ComplianceReport:
        """
        违宪审查：校验立法内容是否符合基本法和合规红线。
        """
        report = self.check_content_compliance(task_id, legislation, "legislation")
        if report.violations:
            return report

        # 检查是否违反基本法（示例关键词）
        basic_law_keywords = ["宪法", "民主", "法治"]
        for kw in basic_law_keywords:
            if kw not in legislation:
                violation = ComplianceViolation(
                    rule_id="basic_law_violation",
                    rule_name="基本法违反",
                    matched_text=f"缺少关键词: {kw}",
                    risk_level=RiskLevel.HIGH,
                    suggestion=f"立法中应包含 {kw} 相关内容"
                )
                report.violations.append(violation)
                report.risk_level = RiskLevel.HIGH
                report.review_result = ReviewResult.REJECTED
                break

        report.review_comment = self._generate_comment(report.violations)
        return report

    def generate_compliance_report(self, report: ComplianceReport) -> str:
        """生成标准化的合规审计报告（文本格式）。"""
        lines = [
            "=" * 60,
            f"合规审计报告",
            f"任务ID: {report.task_id}",
            f"内容类型: {report.content_type}",
            f"审查时间: {report.generated_at.isoformat()}",
            f"审查结论: {report.review_result.value}",
            f"风险等级: {report.risk_level.value}",
            f"审查意见: {report.review_comment}",
            "-" * 60,
        ]
        if report.violations:
            lines.append("违规项详情:")
            for i, v in enumerate(report.violations, 1):
                lines.append(f"  {i}. 规则: {v.rule_name} (ID: {v.rule_id})")
                lines.append(f"     匹配内容: {v.matched_text}")
                lines.append(f"     风险等级: {v.risk_level.value}")
                lines.append(f"     建议: {v.suggestion}")
        else:
            lines.append("未发现违规项。")
        lines.append("=" * 60)
        return "\n".join(lines)

    async def update_compliance_rules(self):
        """动态更新合规规则库（热更新）。"""
        self.rule_manager.reload_from_file()
        self.logger.info("合规规则库已热更新")


# 全局引擎实例
compliance_engine = ComplianceEngine()