"""
国会Agent：负责立法、审批执行方案、验收最终结果。
"""
from typing import Dict, Any
from app.core.agent_base import BaseAgent
from app.core.constants import AgentRole, AgentType
from app.audit.logger import audit_logger


class CongressAgent(BaseAgent):
    """国会Agent，立法分支核心。"""

    def __init__(self, **kwargs):
        super().__init__(
            role_name=AgentRole.CONGRESS,
            role_type=AgentType.LEGISLATIVE,
            branch=AgentType.LEGISLATIVE,
            **kwargs
        )
        self.logger = audit_logger

    async def validate_result(self, raw_output: str) -> bool:
        """
        校验国会输出：
        - 立法环节：必须包含"法案名称"、"条款"、"适用范围"
        - 审批环节：必须包含"审批意见"、"修改建议"（可选）
        - 验收环节：必须包含"验收结论"、"评分"
        """
        if "法案名称" in raw_output and "条款" in raw_output:
            # 立法模式
            return "适用范围" in raw_output
        elif "审批意见" in raw_output:
            # 审批模式
            return True
        elif "验收结论" in raw_output and "评分" in raw_output:
            # 验收模式
            return True
        return False

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        国会核心逻辑：
        - 根据state中的history判断当前环节
        - 立法环节：生成法案
        - 审批环节：审批总统方案，给出decision
        - 验收环节：验收最终结果，给出decision
        """
        history = state.get("history", [])
        output = state.get("output", "")

        # 判断环节
        if "president_plan" in history[-3:]:
            # 审批环节
            if "通过" in output:
                state["decision"] = "pass"
            elif "驳回" in output:
                state["decision"] = "reject"
                state["reject_reason"] = output
            else:
                state["decision"] = "modify"
                state["reject_reason"] = output
        elif "cabinet_execute" in history[-3:]:
            # 验收环节
            if "通过" in output:
                state["decision"] = "pass"
            else:
                state["decision"] = "reject"
                state["reject_reason"] = output
        else:
            # 立法环节
            state["bill"] = output
            state["decision"] = "pass"

        return state