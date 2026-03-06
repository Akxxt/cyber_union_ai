import pytest
from app.agents.executive.omb_agent import OMBAgent, budget_manager


@pytest.fixture
def agent():
    return OMBAgent()


@pytest.mark.asyncio
async def test_budget_check_pass(agent):
    budget_manager.set_budget("test", 100)
    budget_manager.record_usage("test", 30)
    state = {
        "task_id": "test",
        "estimated_tokens": 20
    }
    new_state = await agent.execute(state)
    assert new_state["decision"] == "pass"


@pytest.mark.asyncio
async def test_budget_check_fail(agent):
    budget_manager.set_budget("test", 100)
    budget_manager.record_usage("test", 90)
    state = {
        "task_id": "test",
        "estimated_tokens": 20
    }
    new_state = await agent.execute(state)
    assert new_state["decision"] == "reject"
    assert "预算不足" in new_state["reject_reason"]


@pytest.mark.asyncio
async def test_record_usage(agent):
    budget_manager.set_budget("test", 100)
    await agent.record_token_usage("test", 50)
    assert budget_manager.get_usage("test") == 50


@pytest.mark.asyncio
async def test_budget_status(agent):
    budget_manager.set_budget("test", 100)
    budget_manager.record_usage("test", 30)
    status = await agent.get_budget_status("test")
    assert status["used"] == 30
    assert status["remaining"] == 70