"""
最终版状态机：完整三权分立流程，集成所有Agent，支持驳回回滚、异常处理、审计。
"""
import asyncio
from typing import TypedDict, Literal, Optional, List, Dict, Any
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from app.core.constants import TaskStatus, AgentRole, ErrorCode
from app.core.agent_base import BaseAgent
from app.agents.agent_factory import AgentFactory
from app.utils.exception_utils import TaskExecutionException
from app.audit.logger import audit_logger
from app.config.settings import settings
from app.agents.executive.opm_agent import OPMAgent
from app.agents.executive.omb_agent import OMBAgent
from app.core.cabinet_scheduler import CabinetScheduler
from app.audit.audit_full_link import audit_manager


class TaskState(TypedDict):
    """任务状态数据结构（最终版）。"""
    task_id: str
    status: TaskStatus
    input: str
    output: Optional[str]
    token_usage: Dict[str, int]
    audit_logs: List[Dict[str, Any]]
    reject_reason: Optional[str]
    current_agent: Optional[str]
    current_node: Optional[str]
    history: List[str]
    decision: Optional[Literal["pass", "reject", "modify"]]
    target_node: Optional[str]
    retry_count: int
    max_retries: int
    # 各环节产出
    bill: Optional[str]
    review_comment: Optional[str]
    plan: Optional[str]
    sub_tasks: List[Dict]
    execution_reports: Dict[str, str]
    final_output: Optional[str]


class CyberUnionStateMachine:
    """最终版状态机，全流程闭环。"""

    def __init__(self):
        self.logger = audit_logger
        self._agent_cache = {}
        self.checkpointer = SqliteSaver.from_conn_string("sqlite:///state_machine.db")
        self.opm = OPMAgent()
        self.omb = OMBAgent()
        self.cabinet_scheduler = CabinetScheduler()
        self._build_graph()

    def _build_graph(self):
        """构建完整状态图。"""
        builder = StateGraph(TaskState)

        # 定义所有节点
        builder.add_node("white_house_sort", self._white_house_sort)
        builder.add_node("congress_legislate", self._congress_legislate)
        builder.add_node("supreme_court_review_1", self._supreme_court_review_1)
        builder.add_node("president_plan", self._president_plan)
        builder.add_node("congress_approve_plan", self._congress_approve_plan)
        builder.add_node("supreme_court_review_2", self._supreme_court_review_2)
        builder.add_node("cabinet_execute", self._cabinet_execute)
        builder.add_node("president_inspect", self._president_inspect)
        builder.add_node("congress_accept", self._congress_accept)
        builder.add_node("supreme_court_final", self._supreme_court_final)

        builder.set_entry_point("white_house_sort")

        # 条件边
        builder.add_conditional_edges(
            "white_house_sort",
            self._route_after_sort,
            {
                "to_legislate": "congress_legislate",
                "to_reject": END
            }
        )
        builder.add_conditional_edges(
            "congress_legislate",
            self._route_after_legislate,
            {
                "to_review": "supreme_court_review_1",
                "to_white_house": "white_house_sort"
            }
        )
        builder.add_conditional_edges(
            "supreme_court_review_1",
            self._route_after_review1,
            {
                "to_plan": "president_plan",
                "to_congress": "congress_legislate"
            }
        )
        builder.add_conditional_edges(
            "president_plan",
            self._route_after_plan,
            {
                "to_approve": "congress_approve_plan",
                "to_review": "supreme_court_review_1"
            }
        )
        builder.add_conditional_edges(
            "congress_approve_plan",
            self._route_after_approve,
            {
                "to_final_review": "supreme_court_review_2",
                "to_president": "president_plan"
            }
        )
        builder.add_conditional_edges(
            "supreme_court_review_2",
            self._route_after_review2,
            {
                "to_execute": "cabinet_execute",
                "to_president": "president_plan"
            }
        )
        builder.add_conditional_edges(
            "cabinet_execute",
            self._route_after_execute,
            {
                "to_inspect": "president_inspect",
                "to_president": "president_plan"
            }
        )
        builder.add_conditional_edges(
            "president_inspect",
            self._route_after_inspect,
            {
                "to_accept": "congress_accept",
                "to_cabinet": "cabinet_execute"
            }
        )
        builder.add_conditional_edges(
            "congress_accept",
            self._route_after_accept,
            {
                "to_final": "supreme_court_final",
                "to_cabinet": "cabinet_execute",
                "to_president": "president_plan"
            }
        )
        builder.add_conditional_edges(
            "supreme_court_final",
            self._route_after_final,
            {
                "to_complete": END,
                "to_congress": "congress_legislate",
                "to_president": "president_plan"
            }
        )

        self.graph = builder.compile(checkpointer=self.checkpointer)

    async def _run_agent(self, state: TaskState, agent_role: AgentRole) -> TaskState:
        """统一Agent执行逻辑，集成权限/预算校验、循环检测、审计。"""
        task_id = state["task_id"]
        node_name = state["current_node"]

        # 循环检测
        if state["history"].count(node_name) >= 5:
            self.logger.error(f"检测到循环：节点 {node_name} 出现5次，任务终止", task_id=task_id)
            state["status"] = TaskStatus.TERMINATED
            state["reject_reason"] = f"节点 {node_name} 循环超过5次"
            return state

        # 权限检查
        perm_state = await self.opm.execute({
            "task_id": task_id,
            "current_node": node_name,
            "current_agent": agent_role.value,
            **state
        })
        if perm_state.get("decision") == "reject":
            state["reject_reason"] = perm_state["reject_reason"]
            state["status"] = TaskStatus.REJECTED
            return state

        # 预算检查（估计）
        est_tokens = 100
        budget_state = await self.omb.execute({
            "task_id": task_id,
            "estimated_tokens": est_tokens
        })
        if budget_state.get("decision") == "reject":
            state["reject_reason"] = budget_state["reject_reason"]
            state["status"] = TaskStatus.REJECTED
            return state

        # 获取Agent实例
        agent = AgentFactory.create_agent(
            role=agent_role,
            llm_config={
                "model": settings.default_model,
                "openai_api_key": settings.openai_api_key,
                "openai_api_base": settings.openai_base_url,
                "temperature": 0.3
            },
            token_budget=settings.default_token_budget,
            timeout=settings.model_timeout
        )

        # 记录开始
        start_time = datetime.utcnow()
        audit_manager.log_execution(task_id, node_name, agent_role.value, "start", {"input": state.get("input")})

        try:
            result = await asyncio.wait_for(
                agent.invoke(task_id, state),
                timeout=settings.task_max_execution_seconds
            )
            if result.get("updated_state"):
                state.update(result["updated_state"])
            state["output"] = result.get("output", state.get("output"))
            token_usage = result.get("token_usage", {})
            for k, v in token_usage.items():
                state["token_usage"][k] = state["token_usage"].get(k, 0) + v
            await self.omb.record_token_usage(task_id, token_usage.get("total_tokens", 0))
            audit_manager.log_execution(task_id, node_name, agent_role.value, "success", {
                "output": state["output"][:200],
                "tokens": token_usage
            })
            state["history"].append(agent_role.value)
            state["current_agent"] = agent_role.value
            state["retry_count"] = 0
        except asyncio.TimeoutError:
            audit_manager.log_execution(task_id, node_name, agent_role.value, "timeout", {})
            self.logger.error(f"Agent执行超时", task_id=task_id)
            state["reject_reason"] = "执行超时"
            state["status"] = TaskStatus.FAILED
        except Exception as e:
            audit_manager.log_execution(task_id, node_name, agent_role.value, "exception", {"error": str(e)})
            self.logger.error(f"Agent执行异常: {e}", task_id=task_id)
            retries = state.get("retry_count", 0)
            if retries < state["max_retries"]:
                state["retry_count"] = retries + 1
                self.logger.info(f"重试节点 {agent_role} ({retries+1}/{state['max_retries']})", task_id=task_id)
                return await self._run_agent(state, agent_role)
            else:
                state["reject_reason"] = f"节点 {agent_role} 执行失败，已达最大重试次数"
                state["status"] = TaskStatus.FAILED

        return state

    # ---------- 节点执行函数 ----------
    async def _white_house_sort(self, state: TaskState) -> TaskState:
        state["current_node"] = "white_house_sort"
        state = await self._run_agent(state, AgentRole.WHITE_HOUSE_OFFICE)
        state["status"] = TaskStatus.PENDING_SORT
        return state

    async def _congress_legislate(self, state: TaskState) -> TaskState:
        state["current_node"] = "congress_legislate"
        state = await self._run_agent(state, AgentRole.CONGRESS)
        state["status"] = TaskStatus.PENDING_LEGISLATION
        return state

    async def _supreme_court_review_1(self, state: TaskState) -> TaskState:
        state["current_node"] = "supreme_court_review_1"
        state = await self._run_agent(state, AgentRole.SUPREME_COURT)
        state["status"] = TaskStatus.PENDING_CONSTITUTIONAL_REVIEW
        return state

    async def _president_plan(self, state: TaskState) -> TaskState:
        state["current_node"] = "president_plan"
        state = await self._run_agent(state, AgentRole.PRESIDENT)
        state["status"] = TaskStatus.PENDING_PLANNING
        return state

    async def _congress_approve_plan(self, state: TaskState) -> TaskState:
        state["current_node"] = "congress_approve_plan"
        state = await self._run_agent(state, AgentRole.CONGRESS)
        state["status"] = TaskStatus.PENDING_PLAN_APPROVAL
        return state

    async def _supreme_court_review_2(self, state: TaskState) -> TaskState:
        state["current_node"] = "supreme_court_review_2"
        state = await self._run_agent(state, AgentRole.SUPREME_COURT)
        state["status"] = TaskStatus.PENDING_PLAN_FINAL_REVIEW
        return state

    async def _cabinet_execute(self, state: TaskState) -> TaskState:
        task_id = state["task_id"]
        state["current_node"] = "cabinet_execute"
        sub_tasks = state.get("sub_tasks", [])

        if not sub_tasks:
            self.logger.warning("无可执行的子任务", task_id=task_id)
            state["status"] = TaskStatus.FAILED
            return state

        tasks_to_run = []
        for st in sub_tasks:
            role_str = st.get("department")
            try:
                role = AgentRole(role_str)
            except ValueError:
                role = AgentRole.ENERGY_DEPARTMENT
            tasks_to_run.append({"role": role, "task": st.get("task", "")})

        results = await self.cabinet_scheduler.execute_parallel(task_id, tasks_to_run)

        all_success = all(r["success"] for r in results)
        if all_success:
            reports = {}
            for res in results:
                reports[res["role"]] = res["report"]
            state["execution_reports"] = reports
            state["decision"] = "pass"
            state["status"] = TaskStatus.PENDING_EXECUTION
        else:
            failed = [r["role"] for r in results if not r["success"]]
            state["reject_reason"] = f"以下部门执行失败: {failed}"
            state["decision"] = "reject"
            state["status"] = TaskStatus.FAILED
        return state

    async def _president_inspect(self, state: TaskState) -> TaskState:
        state["current_node"] = "president_inspect"
        state = await self._run_agent(state, AgentRole.PRESIDENT)
        state["status"] = TaskStatus.PENDING_FINAL_INSPECTION
        return state

    async def _congress_accept(self, state: TaskState) -> TaskState:
        state["current_node"] = "congress_accept"
        state = await self._run_agent(state, AgentRole.CONGRESS)
        state["status"] = TaskStatus.PENDING_FINAL_REVIEW
        return state

    async def _supreme_court_final(self, state: TaskState) -> TaskState:
        state["current_node"] = "supreme_court_final"
        state = await self._run_agent(state, AgentRole.SUPREME_COURT)
        state["status"] = TaskStatus.COMPLETED
        return state

    # ---------- 路由决策函数 ----------
    def _route_after_sort(self, state: TaskState) -> str:
        if state.get("decision") == "pass":
            return "to_legislate"
        state["target_node"] = None
        return "to_reject"

    def _route_after_legislate(self, state: TaskState) -> str:
        if state.get("decision") == "pass":
            return "to_review"
        state["target_node"] = "white_house_sort"
        return "to_white_house"

    def _route_after_review1(self, state: TaskState) -> str:
        if state.get("decision") == "pass":
            return "to_plan"
        state["target_node"] = "congress_legislate"
        return "to_congress"

    def _route_after_plan(self, state: TaskState) -> str:
        if state.get("decision") == "pass":
            return "to_approve"
        state["target_node"] = "supreme_court_review_1"
        return "to_review"

    def _route_after_approve(self, state: TaskState) -> str:
        if state.get("decision") == "pass":
            return "to_final_review"
        state["target_node"] = "president_plan"
        return "to_president"

    def _route_after_review2(self, state: TaskState) -> str:
        if state.get("decision") == "pass":
            return "to_execute"
        state["target_node"] = "president_plan"
        return "to_president"

    def _route_after_execute(self, state: TaskState) -> str:
        if state.get("decision") == "pass":
            return "to_inspect"
        state["target_node"] = "president_plan"
        return "to_president"

    def _route_after_inspect(self, state: TaskState) -> str:
        if state.get("decision") == "pass":
            return "to_accept"
        state["target_node"] = "cabinet_execute"
        return "to_cabinet"

    def _route_after_accept(self, state: TaskState) -> str:
        decision = state.get("decision", "pass")
        if decision == "pass":
            return "to_final"
        elif decision == "reject":
            state["target_node"] = "cabinet_execute"
            return "to_cabinet"
        else:
            state["target_node"] = "president_plan"
            return "to_president"

    def _route_after_final(self, state: TaskState) -> str:
        decision = state.get("decision", "pass")
        if decision == "pass":
            return "to_complete"
        elif decision == "reject":
            state["target_node"] = "congress_legislate"
            return "to_congress"
        else:
            state["target_node"] = "president_plan"
            return "to_president"

    async def run(self, initial_state: TaskState) -> TaskState:
        config = {"configurable": {"thread_id": initial_state["task_id"]}}
        final_state = await self.graph.arun(initial_state, config=config)
        return final_state

    async def save_state(self, task_id: str, state: TaskState):
        config = {"configurable": {"thread_id": task_id}}
        await self.graph.aupdate_state(config, state)

    async def load_state(self, task_id: str) -> Optional[TaskState]:
        config = {"configurable": {"thread_id": task_id}}
        state = await self.graph.aget_state(config)
        return state.values if state else None