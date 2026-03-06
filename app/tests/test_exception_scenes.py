import pytest
from app.core.state_machine import CyberUnionStateMachine, TaskState
from app.core.constants import TaskStatus, AgentRole
from app.agents.executive.opm_agent import OPMAgent
from app.agents.executive.omb_agent import OMBAgent, budget_manager


@pytest.mark.asyncio
async def test_permission_denied():
    sm = CyberUnionStateMachine()
    state: TaskState = {
        "task_id": "test_perm",
        "status": TaskStatus.CREATED,
        "input": "test",
        "output": "",
        "token_usage": {},
        "audit_logs": [],
        "reject_reason": None,
        "current_agent": None,
        "current_node": "congress_legislate",
        "history": [],
        "decision": None,
        "target_node": None,
        "retry_count": 0,
        "max_retries": 3,
        "bill": None,
        "review_comment": None,
        "plan": None,
        "sub_tasks": [],
        "execution_reports": {},
        "final_output": None
    }
    new_state = await sm._run_agent(state, AgentRole.PRESIDENT)
    assert new_state["status"] == TaskStatus.REJECTED
    assert "权限不足" in new_state["reject_reason"]


@pytest.mark.asyncio
async def test_budget_exceed():
    budget_manager.set_budget("test_budget", 100)
    budget_manager.record_usage("test_budget", 90)
    omb = OMBAgent()
    state = {"task_id": "test_budget", "estimated_tokens": 20}
    result = await omb.execute(state)
    assert result["decision"] == "reject"
    assert "预算不足" in result["reject_reason"]