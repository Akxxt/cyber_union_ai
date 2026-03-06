import pytest
from app.agents.cabinet.energy_agent import EnergyDepartmentAgent
from app.agents.cabinet.treasury_agent import TreasuryAgent
from app.agents.cabinet.state_agent import StateDepartmentAgent
from app.agents.cabinet.justice_agent import JusticeDepartmentAgent
from app.agents.cabinet.dhs_agent import DHSAgent
from app.agents.cabinet.cia_fbi_agent import CIAFbiAgent
from app.agents.cabinet.regulators_agent import RegulatorsAgent


@pytest.mark.parametrize("agent_class", [
    EnergyDepartmentAgent,
    TreasuryAgent,
    StateDepartmentAgent,
    JusticeDepartmentAgent,
    DHSAgent,
    CIAFbiAgent,
    RegulatorsAgent
])
@pytest.mark.asyncio
async def test_cabinet_agent_validate(agent_class):
    agent = agent_class()
    valid_output = "执行内容：测试；执行结果：成功；完成状态：成功；后续建议：无"
    invalid_output = "执行内容：测试"
    assert await agent.validate_result(valid_output) is True
    assert await agent.validate_result(invalid_output) is False


@pytest.mark.parametrize("agent_class", [
    EnergyDepartmentAgent,
    TreasuryAgent,
    StateDepartmentAgent,
    JusticeDepartmentAgent,
    DHSAgent,
    CIAFbiAgent,
    RegulatorsAgent
])
@pytest.mark.asyncio
async def test_cabinet_agent_execute(agent_class):
    agent = agent_class()
    state = {
        "task_id": "test",
        "sub_task": {"task": "执行任务"}
    }
    new_state = await agent.execute(state)
    assert new_state["decision"] == "pass"
    assert "execution_report" in new_state
    assert "执行内容" in new_state["execution_report"]