"""
能源部Agent：负责能源政策落地、能源项目执行、能耗管理、环保相关执行。
"""
from typing import Dict, Any
from app.core.agent_base import BaseAgent
from app.core.constants import AgentRole, AgentType
from app.audit.logger import audit_logger


class EnergyDepartmentAgent(BaseAgent):
    """能源部Agent，执行能源相关任务。"""

    def __init__(self, **kwargs):
        super().__init__(
            role_name=AgentRole.ENERGY_DEPARTMENT,
            role_type=AgentType.CABINET,
            branch=AgentType.CABINET,
            **kwargs
        )
        self.logger = audit_logger

    async def validate_result(self, raw_output: str) -> bool:
        """
        校验输出是否包含：执行内容、执行结果、完成状态、后续建议。
        """
        required = ["执行内容", "执行结果", "完成状态", "后续建议"]
        return all(phrase in raw_output for phrase in required)

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行能源部任务。
        """
        task_id = state.get("task_id", "unknown")
        sub_task = state.get("sub_task", {})

        # 实际应调用LLM生成执行报告，此处简化为模拟
        output = (
            f"执行内容：{sub_task.get('task', '无')}\n"
            f"执行结果：已完成能源项目\n"
            f"完成状态：成功\n"
            f"后续建议：无"
        )
        state["output"] = output
        state["execution_report"] = output
        state["decision"] = "pass"  # 执行完成，默认通过
        return state