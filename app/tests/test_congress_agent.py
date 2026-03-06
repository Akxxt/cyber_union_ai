import pytest
from app.agents.legislative.congress_agent import CongressAgent
from app.core.constants import AgentRole


@pytest.fixture
def agent():
    return CongressAgent()


@pytest.mark.asyncio
async def test_validate_result_legislation(agent):
    output = "法案名称：能源法；条款：第一条...；适用范围：全国"
    assert await agent.validate_result(output) is True


@pytest.mark.asyncio
async def test_validate_result_approve(agent):
    output = "审批意见：同意；修改建议：无"
    assert await agent.validate_result(output) is True


@pytest.mark.asyncio
async def test_validate_result_accept(agent):
    output = "验收结论：通过；评分：9"
    assert await agent.validate_result(output) is True


@pytest.mark.asyncio
async def test_execute_legislation(agent):
    state = {
        "history": ["white_house_sort"],
        "output": "法案内容"
    }
    new_state = await agent.execute(state)
    assert new_state["bill"] == "法案内容"
    assert new_state["decision"] == "pass"


@pytest.mark.asyncio
async def test_execute_approve_pass(agent):
    state = {
        "history": ["president_plan"],
        "output": "审批意见：通过"
    }
    new_state = await agent.execute(state)
    assert new_state["decision"] == "pass"


@pytest.mark.asyncio
async def test_execute_approve_reject(agent):
    state = {
        "history": ["president_plan"],
        "output": "审批意见：驳回，因为预算不足"
    }
    new_state = await agent.execute(state)
    assert new_state["decision"] == "reject"
    assert new_state["reject_reason"] == "审批意见：驳回，因为预算不足"