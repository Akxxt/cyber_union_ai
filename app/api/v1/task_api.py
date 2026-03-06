"""
任务管理接口：创建、查询、暂停、终止、重试。
"""
from fastapi import APIRouter, Query, Body, Depends, Path
from typing import Optional, List
from pydantic import BaseModel

from app.core.scheduler import TaskScheduler, Task
from app.core.state_machine import CyberUnionStateMachine
from app.core.constants import TaskStatus, TaskPriority
from app.api.utils import success_response, error_response
from app.audit.audit_full_link import audit_manager
import asyncio

router = APIRouter(prefix="/tasks", tags=["任务管理"])


def get_scheduler():
    sm = CyberUnionStateMachine()
    return TaskScheduler(sm)


class TaskCreateRequest(BaseModel):
    input: str
    priority: TaskPriority = TaskPriority.NORMAL


class TaskResponse(BaseModel):
    task_id: str
    input: str
    status: TaskStatus
    priority: TaskPriority
    create_time: str
    update_time: str
    executor: Optional[str]
    reject_reason: Optional[str]


@router.post("/", summary="创建任务")
async def create_task(
    req: TaskCreateRequest,
    scheduler: TaskScheduler = Depends(get_scheduler)
):
    """
    创建新任务，返回任务ID。
    """
    try:
        task = Task(input=req.input, priority=req.priority)
        task_id = await scheduler.submit_task(task)
        await audit_manager.log_operation(task_id, "API", "create", {"input": req.input})
        return success_response(data={"task_id": task_id})
    except Exception as e:
        return error_response(code=500, message=f"创建任务失败: {str(e)}")


@router.get("/", summary="查询任务列表")
async def list_tasks(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[TaskStatus] = Query(None, description="按状态筛选"),
    scheduler: TaskScheduler = Depends(get_scheduler)
):
    """
    分页查询任务列表，支持状态筛选。
    """
    # 实际应从数据库分页查询，此处简化返回空列表
    # 建议使用状态机持久化存储查询
    return success_response(data={
        "tasks": [],
        "total": 0,
        "page": page,
        "size": size
    })


@router.get("/{task_id}", summary="查询任务详情")
async def get_task(
    task_id: str = Path(..., description="任务ID"),
    scheduler: TaskScheduler = Depends(get_scheduler)
):
    """
    根据任务ID查询详细信息，包含当前状态、执行历史、Token消耗等。
    """
    sm = CyberUnionStateMachine()
    state = await sm.load_state(task_id)
    if not state:
        return error_response(code=404, message="任务不存在")
    return success_response(data=state)


@router.put("/{task_id}/pause", summary="暂停任务")
async def pause_task(
    task_id: str = Path(..., description="任务ID"),
    scheduler: TaskScheduler = Depends(get_scheduler)
):
    """
    暂停正在运行的任务。
    """
    success = await scheduler.pause_task(task_id)
    if success:
        await audit_manager.log_operation(task_id, "API", "pause", {})
        return success_response(message="任务已暂停")
    return error_response(code=400, message="暂停失败")


@router.put("/{task_id}/terminate", summary="终止任务")
async def terminate_task(
    task_id: str = Path(..., description="任务ID"),
    scheduler: TaskScheduler = Depends(get_scheduler)
):
    """
    终止任务（不可恢复）。
    """
    success = await scheduler.terminate_task(task_id)
    if success:
        await audit_manager.log_operation(task_id, "API", "terminate", {})
        return success_response(message="任务已终止")
    return error_response(code=400, message="终止失败")


@router.put("/{task_id}/retry", summary="重试任务")
async def retry_task(
    task_id: str = Path(..., description="任务ID"),
    scheduler: TaskScheduler = Depends(get_scheduler)
):
    """
    手动重试失败的任务。
    """
    sm = CyberUnionStateMachine()
    state = await sm.load_state(task_id)
    if not state:
        return error_response(code=404, message="任务不存在")
    # 重置状态为初始，重新提交
    state["status"] = TaskStatus.CREATED
    state["retry_count"] = 0
    state["history"] = []
    await sm.save_state(task_id, state)
    # 重新加入队列
    asyncio.create_task(sm.run(state))
    await audit_manager.log_operation(task_id, "API", "retry", {})
    return success_response(message="任务已重试")