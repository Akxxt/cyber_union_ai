import pytest
import asyncio
from app.core.state_machine import CyberUnionStateMachine
from app.core.scheduler import TaskScheduler, Task
from app.core.constants import TaskStatus


@pytest.mark.asyncio
async def test_full_flow_success():
    sm = CyberUnionStateMachine()
    scheduler = TaskScheduler(sm)
    await scheduler.start()

    task = Task(input="制定一项新能源政策", priority="NORMAL")
    task_id = await scheduler.submit_task(task)

    for _ in range(60):
        await asyncio.sleep(1)
        state = await sm.load_state(task_id)
        if state and state["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.TERMINATED]:
            break

    assert state is not None
    assert state["status"] == TaskStatus.COMPLETED
    await scheduler.stop()