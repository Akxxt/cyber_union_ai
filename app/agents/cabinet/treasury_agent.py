"""
财政部Agent：负责财政资金拨付、税务相关执行、预算落地、财务报表生成。
"""
from typing import Dict, Any
from app.core.agent_base import BaseAgent
from app.core.constants import AgentRole, AgentType
from app.audit.logger import audit_logger


class TreasuryAgent(BaseAgent):
    """财政部Agent，执行财政相关任务。"""

    def __init__(self, **kwargs):
        super().__init__(
            role_name=AgentRole.TREASURY,
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
            f"执行结果：资金已拨付\n"
            f"完成状态：成功\n"
            f"后续建议：跟踪资金使用"
        )
        state["output"] = output
        state["execution_report"] = output
        state["decision"] = "pass"
        return state