"""
分布式任务调度器，基于Redis实现优先级队列、延迟任务、去重。
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

from app.core.redis_client import RedisClient, DistributedLock
from app.core.scheduler import Task, TaskScheduler as BaseScheduler
from app.core.state_machine import CyberUnionStateMachine
from app.core.constants import TaskStatus, TaskPriority
from app.audit.logger import audit_logger
from app.config.settings import settings


class DistributedTaskScheduler(BaseScheduler):
    """分布式任务调度器。"""

    def __init__(self, state_machine: CyberUnionStateMachine, node_id: Optional[str] = None):
        super().__init__(state_machine)
        self.node_id = node_id or f"node_{uuid4().hex[:8]}"
        self.redis = None
        self._poll_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def start(self):
        self.redis = await RedisClient.get_client()
        await self.redis.hset("scheduler:nodes", self.node_id, time.time())
        self._poll_task = asyncio.create_task(self._poll_loop())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        audit_logger.info(f"分布式调度器启动，节点ID: {self.node_id}")

    async def stop(self):
        if self._poll_task:
            self._poll_task.cancel()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self.redis:
            await self.redis.hdel("scheduler:nodes", self.node_id)
        audit_logger.info(f"分布式调度器停止，节点ID: {self.node_id}")

    async def submit_task(self, task: Task, delay_seconds: int = 0) -> str:
        task_data = task.dict()
        task_data["status"] = TaskStatus.CREATED.value
        task_data["create_time"] = task.create_time.isoformat()
        task_data["update_time"] = task.update_time.isoformat()
        async with DistributedLock(f"task:{task.task_id}"):
            exists = await self.redis.exists(f"task:{task.task_id}")
            if exists:
                raise ValueError(f"任务ID已存在: {task.task_id}")
            await self.redis.set(f"task:{task.task_id}", json.dumps(task_data))
            priority_map = {TaskPriority.URGENT: 0, TaskPriority.HIGH: 1, TaskPriority.NORMAL: 2, TaskPriority.LOW: 3}
            score = priority_map[task.priority] * 1e13 + time.time()
            if delay_seconds > 0:
                execute_at = time.time() + delay_seconds
                await self.redis.zadd("scheduler:delayed", {task.task_id: execute_at})
            else:
                await self.redis.zadd("scheduler:queue", {task.task_id: score})
        audit_logger.info(f"任务已提交: {task.task_id}, 延迟: {delay_seconds}s")
        return task.task_id

    async def _poll_loop(self):
        while True:
            try:
                now = time.time()
                delayed_tasks = await self.redis.zrangebyscore("scheduler:delayed", 0, now)
                for task_id in delayed_tasks:
                    await self.redis.zrem("scheduler:delayed", task_id)
                    await self.redis.zadd("scheduler:queue", {task_id: now})
                async with DistributedLock("scheduler:pop"):
                    items = await self.redis.zpopmin("scheduler:queue", count=1)
                    if items:
                        task_id, score = items[0]
                        async with DistributedLock(f"task:exec:{task_id}", timeout=60):
                            await self._execute_task(task_id)
            except asyncio.CancelledError:
                break
            except Exception as e:
                audit_logger.error(f"调度轮询异常: {e}")
                await asyncio.sleep(1)

    async def _execute_task(self, task_id: str):
        task_json = await self.redis.get(f"task:{task_id}")
        if not task_json:
            audit_logger.error(f"任务数据不存在: {task_id}")
            return
        task_data = json.loads(task_json)
        task = Task(**task_data)
        task.status = TaskStatus.PENDING_SORT
        await self.redis.set(f"task:{task_id}", json.dumps(task.dict()))
        try:
            await self._run_task_wrapper(task)
        except Exception as e:
            audit_logger.error(f"任务执行异常: {e}", task_id=task_id)
            task.status = TaskStatus.FAILED
            await self.redis.set(f"task:{task_id}", json.dumps(task.dict()))

    async def _heartbeat_loop(self):
        while True:
            try:
                await self.redis.hset("scheduler:nodes", self.node_id, time.time())
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                audit_logger.error(f"心跳异常: {e}")

    async def pause_task(self, task_id: str) -> bool:
        async with DistributedLock(f"task:{task_id}"):
            task_json = await self.redis.get(f"task:{task_id}")
            if not task_json:
                return False
            task_data = json.loads(task_json)
            task_data["status"] = TaskStatus.PAUSED.value
            await self.redis.set(f"task:{task_id}", json.dumps(task_data))
        return True

    async def terminate_task(self, task_id: str) -> bool:
        async with DistributedLock(f"task:{task_id}"):
            task_json = await self.redis.get(f"task:{task_id}")
            if not task_json:
                return False
            task_data = json.loads(task_json)
            task_data["status"] = TaskStatus.TERMINATED.value
            await self.redis.set(f"task:{task_id}", json.dumps(task_data))
        return True

    async def get_task_status(self, task_id: str) -> Optional[Task]:
        task_json = await self.redis.get(f"task:{task_id}")
        if not task_json:
            return None
        return Task(**json.loads(task_json))