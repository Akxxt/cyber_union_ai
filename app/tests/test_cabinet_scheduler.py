import pytest
from app.core.cabinet_scheduler import CabinetScheduler
from app.core.constants import AgentRole


@pytest.mark.asyncio
async def test_execute_subtask_success():
    scheduler = CabinetScheduler()
    sub_task = {"task": "测试任务"}
    result = await scheduler.execute_subtask("test123", AgentRole.ENERGY_DEPARTMENT, sub_task)
    assert result["success"] is True
    assert "report" in result


@pytest.mark.asyncio
async def test_execute_parallel():
    scheduler = CabinetScheduler()
    sub_tasks = [
        {"role": AgentRole.ENERGY_DEPARTMENT, "task": "能源任务"},
        {"role": AgentRole.TREASURY, "task": "财政任务"},
        {"role": AgentRole.STATE_DEPARTMENT, "task": "外交任务"}
    ]
    results = await scheduler.execute_parallel("test123", sub_tasks)
    assert len(results) == 3
    assert all(r["success"] for r in results)


@pytest.mark.asyncio
async def test_execute_with_failure(monkeypatch):
    scheduler = CabinetScheduler()
    async def fail_execute(*args, **kwargs):
        raise Exception("模拟失败")
    monkeypatch.setattr(scheduler, 'execute_subtask', fail_execute)
    sub_tasks = [{"role": AgentRole.ENERGY_DEPARTMENT, "task": "任务"}]
    results = await scheduler.execute_parallel("test123", sub_tasks)
    assert results[0]["success"] is False