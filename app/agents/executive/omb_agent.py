"""
预算管理办公室 Agent：Token预算管控、消耗统计、进度跟踪。
"""
from typing import Dict, Any, Optional
from app.core.agent_base import BaseAgent
from app.core.constants import AgentRole, AgentType
from app.audit.logger import audit_logger
from app.config.settings import settings


class BudgetManager:
    """预算管理器，全局单例。"""

    def __init__(self):
        self.task_budgets: Dict[str, int] = {}
        self.task_used: Dict[str, int] = {}
        self.warning_threshold = getattr(settings, 'budget_warning_threshold', 0.8)

    def set_budget(self, task_id: str, budget: int):
        self.task_budgets[task_id] = budget
        self.task_used[task_id] = 0

    def record_usage(self, task_id: str, tokens: int):
        if task_id in self.task_used:
            self.task_used[task_id] += tokens
        else:
            self.task_used[task_id] = tokens

    def get_usage(self, task_id: str) -> int:
        return self.task_used.get(task_id, 0)

    def get_budget(self, task_id: str) -> int:
        return self.task_budgets.get(task_id, settings.default_token_budget)

    def check_budget(self, task_id: str, additional_tokens: int = 0) -> bool:
        used = self.get_usage(task_id)
        budget = self.get_budget(task_id)
        return (used + additional_tokens) <= budget

    def check_warning(self, task_id: str) -> bool:
        used = self.get_usage(task_id)
        budget = self.get_budget(task_id)
        if budget == 0:
            return False
        return used / budget >= self.warning_threshold


# 全局预算管理器
budget_manager = BudgetManager()


class OMBAgent(BaseAgent):
    """预算管理办公室 Agent。"""

    def __init__(self, **kwargs):
        super().__init__(
            role_name=AgentRole.OMB,
            role_type=AgentType.EXECUTIVE,
            branch=AgentType.EXECUTIVE,
            **kwargs
        )
        self.logger = audit_logger
        self.budget_manager = budget_manager

    async def validate_result(self, raw_output: str) -> bool:
        return True

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行预算检查：在节点执行前调用，检查是否超预算。
        """
        task_id = state.get("task_id", "unknown")
        estimated_tokens = state.get("estimated_tokens", 0)

        if not self.budget_manager.check_budget(task_id, estimated_tokens):
            self.logger.warning(f"任务 {task_id} 预算不足", task_id=task_id)
            state["decision"] = "reject"
            state["reject_reason"] = "预算不足，无法执行"
            return state

        if self.budget_manager.check_warning(task_id):
            self.logger.warning(f"任务 {task_id} 预算使用超过预警线", task_id=task_id)

        state["decision"] = "pass"
        return state

    async def record_token_usage(self, task_id: str, tokens: int):
        """记录Token消耗。"""
        self.budget_manager.record_usage(task_id, tokens)
        self.logger.info(f"任务 {task_id} 消耗Token: {tokens}", task_id=task_id)

    async def get_budget_status(self, task_id: str) -> Dict:
        used = self.budget_manager.get_usage(task_id)
        budget = self.budget_manager.get_budget(task_id)
        return {
            "task_id": task_id,
            "budget": budget,
            "used": used,
            "remaining": budget - used,
            "percentage": (used / budget * 100) if budget > 0 else 0
        }