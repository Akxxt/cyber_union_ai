import pytest
from app.agents.executive.opm_agent import OPMAgent, PermissionManager
from app.core.constants import AgentRole


@pytest.fixture
def agent():
    return OPMAgent()


def test_permission_manager():
    pm = PermissionManager()
    perms = pm.get_permissions(AgentRole.PRESIDENT)
    assert "allowed_nodes" in perms
    assert "president_plan" in perms["allowed_nodes"]


@pytest.mark.asyncio
async def test_check_node_access_pass(agent):
    state = {
        "task_id": "test",
        "current_node": "president_plan",
        "current_agent": AgentRole.PRESIDENT
    }
    new_state = await agent.execute(state)
    assert new_state["decision"] == "pass"


@pytest.mark.asyncio
async def test_check_node_access_fail(agent):
    state = {
        "task_id": "test",
        "current_node": "congress_legislate",
        "current_agent": AgentRole.PRESIDENT
    }
    new_state = await agent.execute(state)
    assert new_state["decision"] == "reject"
    assert "权限不足" in new_state["reject_reason"]