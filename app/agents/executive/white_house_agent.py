"""
白宫办公室Agent：负责任务分拣、格式校验。
"""
from typing import Dict, Any
from app.core.agent_base import BaseAgent
from app.core.constants import AgentRole, AgentType, TaskPriority
from app.audit.logger import audit_logger


class WhiteHouseOfficeAgent(BaseAgent):
    """白宫办公室Agent：任务分拣、优先级分配。"""

    def __init__(self, **kwargs):
        super().__init__(
            role_name=AgentRole.WHITE_HOUSE_OFFICE,
            role_type=AgentType.EXECUTIVE,
            branch=AgentType.EXECUTIVE,
            **kwargs
        )
        self.logger = audit_logger

    async def validate_result(self, raw_output: str) -> bool:
        """
        校验分拣结果：必须包含"任务分类"、"优先级"、"目标分支"。
        """
        required = ["任务分类", "优先级", "目标分支"]
        return all(phrase in raw_output for phrase in required)

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        分拣逻辑：
        - 解析输入任务，判断是否符合格式要求
        - 分配优先级，指定目标处理分支
        - 更新state的decision字段
        """
        # 从invoke的output中获取分拣结果
        output = state.get("output", "")
        # 简单模拟解析：若output包含"urgent"，则设为高优
        if "urgent" in output.lower():
            state["priority"] = TaskPriority.URGENT
        elif "high" in output.lower():
            state["priority"] = TaskPriority.HIGH
        else:
            state["priority"] = TaskPriority.NORMAL

        # 设置目标分支（通常为立法分支）
        state["target_branch"] = AgentType.LEGISLATIVE.value
        state["decision"] = "pass"  # 分拣通过

        return state