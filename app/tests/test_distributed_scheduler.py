import pytest
import asyncio
import time
from app.core.distributed_scheduler import DistributedTaskScheduler
from app.core.state_machine import CyberUnionStateMachine
from app.core.scheduler import Task
from app.core.constants import TaskPriority


@pytest.mark.asyncio
async def test_submit_and_execute():
    sm = CyberUnionStateMachine()
    scheduler = DistributedTaskScheduler(sm, node_id="test_node")
    await scheduler.start()

    task = Task(input="test")
    task_id = await scheduler.submit_task(task)

    await asyncio.sleep(2)
    status = await scheduler.get_task_status(task_id)
    assert status is not None
    await scheduler.stop()


@pytest.mark.asyncio
async def test_delayed_task():
    sm = CyberUnionStateMachine()
    scheduler = DistributedTaskScheduler(sm)
    await scheduler.start()

    task = Task(input="delayed")
    start = time.time()
    task_id = await scheduler.submit_task(task, delay_seconds=5)

    status = await scheduler.get_task_status(task_id)
    assert status.status.value == "CREATED"

    await asyncio.sleep(6)
    status = await scheduler.get_task_status(task_id)
    assert status.status.value != "CREATED"
    elapsed = time.time() - start
    assert 5 <= elapsed <= 7
    await scheduler.stop()


@pytest.mark.asyncio
async def test_multi_node():
    sm = CyberUnionStateMachine()
    scheduler1 = DistributedTaskScheduler(sm, node_id="node1")
    scheduler2 = DistributedTaskScheduler(sm, node_id="node2")
    await scheduler1.start()
    await scheduler2.start()

    task_ids = []
    for i in range(10):
        task = Task(input=f"task{i}", priority=TaskPriority.NORMAL)
        task_id = await scheduler1.submit_task(task)
        task_ids.append(task_id)

    await asyncio.sleep(5)
    for tid in task_ids:
        status = await scheduler1.get_task_status(tid)
        assert status is not None
        assert status.status.value in ["COMPLETED", "FAILED", "TERMINATED"]

    await scheduler1.stop()
    await scheduler2.stop()