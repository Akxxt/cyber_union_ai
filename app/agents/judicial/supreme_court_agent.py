"""
最高法院Agent：负责违宪审查、合规终审、最终裁决。
严格继承BaseAgent，仅执行审查裁决职能。
"""
from typing import Dict, Any, Optional
from app.core.agent_base import BaseAgent
from app.core.constants import AgentRole, AgentType, ReviewResult
from app.audit.compliance import ComplianceEngine, compliance_engine
from app.audit.logger import audit_logger
from app.config.settings import settings


class SupremeCourtAgent(BaseAgent):
    """最高法院Agent，三权分立之司法分支。"""

    def __init__(self, **kwargs):
        super().__init__(
            role_name=AgentRole.SUPREME_COURT,
            role_type=AgentType.JUDICIAL,
            branch=AgentType.JUDICIAL,
            **kwargs
        )
        self.compliance: ComplianceEngine = compliance_engine
        self.logger = audit_logger

    async def validate_result(self, raw_output: str) -> bool:
        """
        校验输出必须包含四个核心部分：
        - 审查结论（通过/驳回/修改）
        - 法律依据
        - 违规项（如有）
        - 整改建议（如有）
        """
        required = ["审查结论", "法律依据"]
        # 违规项和整改建议为非必需但建议有
        if not all(phrase in raw_output for phrase in required):
            self.logger.warning("输出缺少核心部分")
            return False
        return True

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行三大核心职能，根据当前状态判断进入哪个环节。
        """
        task_id = state.get("task_id", "unknown")
        history = state.get("history", [])
        current_status = state.get("status")

        # 判断当前环节
        if "congress_legislate" in history[-2:]:
            # 立法环节违宪审查
            return await self._review_legislation(state, task_id)
        elif "congress_approve_plan" in history[-2:]:
            # 方案环节合规终审
            return await self._review_plan(state, task_id)
        elif "congress_accept" in history[-2:]:
            # 结果环节最终裁决
            return await self._final_verdict(state, task_id)
        else:
            self.logger.warning("未知的审查环节", task_id=task_id)
            state["decision"] = "reject"
            state["reject_reason"] = "无法确定审查环节"
            return state

    async def _review_legislation(self, state: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """
        立法环节违宪审查。
        """
        legislation = state.get("bill", state.get("output", ""))
        if not legislation:
            self.logger.error("无立法内容可审查", task_id=task_id)
            state["decision"] = "reject"
            return state

        # 调用合规引擎进行违宪审查
        report = await self.compliance.check_constitutional_review(task_id, legislation)

        # 记录合规报告到state（可选）
        state["compliance_report"] = report.dict()

        if report.review_result == ReviewResult.PASSED:
            state["decision"] = "pass"
            state["review_comment"] = "立法内容符合宪法和合规要求"
        else:
            state["decision"] = "reject" if report.risk_level in ["high", "critical"] else "modify"
            state["reject_reason"] = report.review_comment
            # 生成详细报告作为输出
            state["output"] = self.compliance.generate_compliance_report(report)

        return state

    async def _review_plan(self, state: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """
        方案环节合规终审。
        """
        plan = state.get("plan", state.get("output", ""))
        if not plan:
            self.logger.error("无执行方案可审查", task_id=task_id)
            state["decision"] = "reject"
            return state

        report = self.compliance.check_content_compliance(task_id, plan, "plan")
        state["compliance_report"] = report.dict()

        if report.review_result == ReviewResult.PASSED:
            state["decision"] = "pass"
        else:
            state["decision"] = "reject" if report.risk_level in ["high", "critical"] else "modify"
            state["reject_reason"] = report.review_comment
            state["output"] = self.compliance.generate_compliance_report(report)

        return state

    async def _final_verdict(self, state: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """
        结果环节最终裁决。
        """
        execution_result = state.get("execution_report", state.get("output", ""))
        if not execution_result:
            self.logger.error("无执行结果可裁决", task_id=task_id)
            state["decision"] = "reject"
            return state

        report = self.compliance.check_content_compliance(task_id, execution_result, "execution")
        state["compliance_report"] = report.dict()

        if report.review_result == ReviewResult.PASSED:
            state["decision"] = "pass"
            state["status"] = "COMPLETED"  # 最终裁决通过，任务完成
        else:
            state["decision"] = "reject"
            state["reject_reason"] = report.review_comment
            state["output"] = self.compliance.generate_compliance_report(report)

        return state