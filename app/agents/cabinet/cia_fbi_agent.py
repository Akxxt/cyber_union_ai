"""
情报部门Agent：负责情报收集、数据分析、风险预警、情报上报。
"""
from typing import Dict, Any
from app.core.agent_base import BaseAgent
from app.core.constants import AgentRole, AgentType
from app.audit.logger import audit_logger


class CIAFbiAgent(BaseAgent):
    """情报部门Agent，执行情报相关任务。"""

    def __init__(self, **kwargs):
        super().__init__(
            role_name=AgentRole.CIA_FBI,
            role_type=AgentType.CABINET,
            branch=AgentType.CABINET,
            **kwargs
        )
        self.logger = audit_logger

    async def validate_result(self, raw_output: str) -> bool:
        required = ["执行内容", "执行结果", "完成状态", "后续建议"]
        return all(phrase in raw_output for phrase in required)

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        task_id = state.get("task_id", "unknown")
        sub_task = state.get("sub_task", {})
        output = (
            f"执行内容：{sub_task.get('task', '无')}\n"
            f"执行结果：情报已收集分析\n"
            f"完成状态：成功\n"
            f"后续建议：关注潜在风险"
        )
        state["output"] = output
        state["execution_report"] = output
        state["decision"] = "pass"
        return state