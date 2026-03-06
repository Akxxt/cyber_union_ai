"""
内阁调度器：负责任务派发、并行执行、结果收集、异常处理。
"""
import asyncio
from typing import Dict, Any, List, Optional

from app.agents.cabinet.energy_agent import EnergyDepartmentAgent
from app.agents.cabinet.treasury_agent import TreasuryAgent
from app.agents.cabinet.state_agent import StateDepartmentAgent
from app.agents.cabinet.justice_agent import JusticeDepartmentAgent
from app.agents.cabinet.dhs_agent import DHSAgent
from app.agents.cabinet.cia_fbi_agent import CIAFbiAgent
from app.agents.cabinet.regulators_agent import RegulatorsAgent
from app.core.constants import AgentRole
from app.audit.logger import audit_logger
from app.config.settings import settings
from app.agents.executive.opm_agent import OPMAgent
from app.agents.executive.omb_agent import OMBAgent


class CabinetScheduler:
    """内阁调度器，管理并行任务执行。"""

    def __init__(self):
        self.agents = {
            AgentRole.ENERGY_DEPARTMENT: EnergyDepartmentAgent,
            AgentRole.TREASURY: TreasuryAgent,
            AgentRole.STATE_DEPARTMENT: StateDepartmentAgent,
            AgentRole.JUSTICE_DEPARTMENT: JusticeDepartmentAgent,
            AgentRole.DHS: DHSAgent,
            AgentRole.CIA_FBI: CIAFbiAgent,
            AgentRole.REGULATORS: RegulatorsAgent,
        }
        self.logger = audit_logger
        self.max_workers = getattr(settings, 'cabinet_parallel_max_workers', 5)
        self.execution_timeout = getattr(settings, 'cabinet_execution_timeout', 60)
        self.max_retries = getattr(settings, 'cabinet_retry_max_times', 3)
        self.opm = OPMAgent()
        self.omb = OMBAgent()

    async def _check_permissions_and_budget(self, task_id: str, role: AgentRole, node: str) -> bool:
        perm_state = await self.opm.execute({
            "task_id": task_id,
            "current_node": node,
            "current_agent": role,
        })
        if perm_state.get("decision") == "reject":
            self.logger.warning(f"权限校验失败: {role} 不能执行 {node}", task_id=task_id)
            return False
        budget_state = await self.omb.execute({
            "task_id": task_id,
            "estimated_tokens": 100
        })
        if budget_state.get("decision") == "reject":
            self.logger.warning(f"预算不足", task_id=task_id)
            return False
        return True

    async def execute_subtask(self, task_id: str, role: AgentRole, sub_task: Dict) -> Dict:
        agent_class = self.agents.get(role)
        if not agent_class:
            raise ValueError(f"未知部门角色: {role}")
        agent = agent_class()

        if not await self._check_permissions_and_budget(task_id, role, "cabinet_execute"):
            return {"role": role.value, "success": False, "error": "权限或预算校验失败", "report": ""}

        for attempt in range(1, self.max_retries + 1):
            try:
                state = {"task_id": task_id, "sub_task": sub_task, "attempt": attempt}
                result = await asyncio.wait_for(agent.execute(state), timeout=self.execution_timeout)
                report = result.get("execution_report", "")
                await self.omb.record_token_usage(task_id, 100)
                return {"role": role.value, "success": True, "report": report, "attempt": attempt}
            except asyncio.TimeoutError:
                self.logger.warning(f"{role} 执行超时 (attempt {attempt})", task_id=task_id)
                if attempt == self.max_retries:
                    return {"role": role.value, "success": False, "error": "执行超时", "report": ""}
            except Exception as e:
                self.logger.error(f"{role} 执行异常: {e}", task_id=task_id)
                if attempt == self.max_retries:
                    return {"role": role.value, "success": False, "error": str(e), "report": ""}
            await asyncio.sleep(1)

    async def execute_parallel(self, task_id: str, sub_tasks: List[Dict]) -> List[Dict]:
        semaphore = asyncio.Semaphore(self.max_workers)

        async def limited_execute(st):
            async with semaphore:
                return await self.execute_subtask(task_id, st["role"], st)

        tasks = [limited_execute(st) for st in sub_tasks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        final_results = []
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                final_results.append({
                    "role": sub_tasks[i]["role"].value,
                    "success": False,
                    "error": str(res),
                    "report": ""
                })
            else:
                final_results.append(res)
        return final_results