"""
基础任务调度器（单机版）。
"""
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import uuid4
import heapq

from pydantic import BaseModel, Field

from app.config.settings import settings
from app.core.constants import TaskStatus, TaskPriority, ErrorCode
from app.core.state_machine import CyberUnionStateMachine, TaskState
from app.audit.logger import audit_logger
from app.utils.exception_utils import TaskExecutionException, BusinessException


class Task(BaseModel):
    """任务数据结构。"""
    task_id: str = Field(default_factory=lambda: f"task_{uuid4().hex}")
    input: str
    status: TaskStatus = TaskStatus.CREATED
    priority: TaskPriority = TaskPriority.NORMAL
    token_budget: int = Field(default_factory=lambda: settings.default_token_budget)
    token_used: int = 0
    create_time: datetime = Field(default_factory=datetime.utcnow)
    update_time: datetime = Field(default_factory=datetime.utcnow)
    executor: Optional[str] = None
    reject_reason: Optional[str] = None
    audit_logs: List[Dict[str, Any]] = []

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class TaskScheduler:
    """基础任务调度器（单机版）。"""

    def __init__(self, state_machine: CyberUnionStateMachine):
        self.state_machine = state_machine
        self.logger = audit_logger
        self._task_queue = asyncio.PriorityQueue()
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._semaphore = asyncio.Semaphore(settings.task_max_concurrent)
        self._shutdown_event = asyncio.Event()
        self._scheduler_task: Optional[asyncio.Task] = None

    def _priority_value(self, task: Task) -> int:
        mapping = {TaskPriority.URGENT: 0, TaskPriority.HIGH: 1, TaskPriority.NORMAL: 2, TaskPriority.LOW: 3}
        return mapping[task.priority]

    async def submit_task(self, task: Task) -> str:
        if task.status != TaskStatus.CREATED:
            raise BusinessException(code=ErrorCode.TASK_STATE_INVALID, message=f"任务状态必须为CREATED")
        await self._task_queue.put((self._priority_value(task), task))
        self.logger.info(f"任务已提交: {task.task_id}", task_id=task.task_id)
        return task.task_id

    async def start(self):
        if self._scheduler_task is not None:
            return
        self._shutdown_event.clear()
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        self.logger.info("任务调度器已启动")

    async def stop(self):
        if self._scheduler_task:
            self._shutdown_event.set()
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
            self._scheduler_task = None
            self.logger.info("任务调度器已停止")

    async def _scheduler_loop(self):
        while not self._shutdown_event.is_set():
            try:
                priority, task = await asyncio.wait_for(self._task_queue.get(), timeout=1.0)
            except asyncio.TimeoutError:
                continue

            await self._semaphore.acquire()
            run_task = asyncio.create_task(self._run_task_wrapper(task))
            self._running_tasks[task.task_id] = run_task
            run_task.add_done_callback(lambda t: self._task_done_callback(t, task.task_id))

    async def _run_task_wrapper(self, task: Task):
        try:
            task.status = TaskStatus.PENDING_SORT
            task.update_time = datetime.utcnow()

            initial_state: TaskState = {
                "task_id": task.task_id,
                "status": task.status,
                "input": task.input,
                "output": None,
                "token_usage": {},
                "audit_logs": [],
                "reject_reason": None,
                "current_agent": None,
                "current_node": None,
                "history": [],
                "decision": None,
                "target_node": None,
                "retry_count": 0,
                "max_retries": settings.single_step_max_retries,
                "bill": None,
                "review_comment": None,
                "plan": None,
                "sub_tasks": [],
                "execution_reports": {},
                "final_output": None
            }

            try:
                final_state = await asyncio.wait_for(
                    self.state_machine.run(initial_state),
                    timeout=settings.task_max_execution_seconds
                )
            except asyncio.TimeoutError:
                self.logger.error(f"任务执行超时", task_id=task.task_id)
                task.status = TaskStatus.FAILED
                task.reject_reason = "执行超时"
                raise TaskExecutionException(code=ErrorCode.TASK_EXECUTION_FAILED, message="任务执行超时")

            task.status = final_state["status"]
            task.token_used = final_state["token_usage"].get("total_tokens", 0)
            task.audit_logs = final_state["audit_logs"]
            task.executor = final_state.get("current_agent")
            task.reject_reason = final_state.get("reject_reason")
            self.logger.info(f"任务执行完成: {task.task_id}, 状态: {task.status}", task_id=task.task_id)

        except Exception as e:
            self.logger.error(f"任务执行异常: {e}", task_id=task.task_id, exc_info=True)
            task.status = TaskStatus.FAILED
            task.reject_reason = str(e)
        finally:
            task.update_time = datetime.utcnow()

    def _task_done_callback(self, future: asyncio.Future, task_id: str):
        self._semaphore.release()
        self._running_tasks.pop(task_id, None)

    async def pause_task(self, task_id: str) -> bool:
        if task_id in self._running_tasks:
            self._running_tasks[task_id].cancel()
        self.logger.info(f"任务暂停: {task_id}", task_id=task_id)
        return True

    async def terminate_task(self, task_id: str) -> bool:
        if task_id in self._running_tasks:
            self._running_tasks[task_id].cancel()
        self.logger.info(f"任务终止: {task_id}", task_id=task_id)
        return True

    async def get_task_status(self, task_id: str) -> Optional[Task]:
        # 实际应从持久化存储读取，此处简化
        return None