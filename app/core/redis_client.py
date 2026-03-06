"""
Redis客户端封装，支持分布式锁、优先级队列。
"""
import json
import asyncio
from typing import Optional, Any, List
from redis.asyncio import Redis
from redis.asyncio.lock import Lock
from app.config.settings import settings


class RedisClient:
    """异步Redis客户端单例。"""
    _instance: Optional[Redis] = None

    @classmethod
    async def get_client(cls) -> Redis:
        if cls._instance is None:
            cls._instance = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=settings.redis_db,
                decode_responses=True
            )
        return cls._instance

    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None


class DistributedLock:
    """基于Redis的分布式锁。"""

    def __init__(self, lock_name: str, timeout: int = 30):
        self.lock_name = lock_name
        self.timeout = timeout
        self.lock: Optional[Lock] = None

    async def __aenter__(self):
        redis = await RedisClient.get_client()
        self.lock = redis.lock(f"lock:{self.lock_name}", timeout=self.timeout, blocking_timeout=5)
        acquired = await self.lock.acquire()
        if not acquired:
            raise TimeoutError(f"获取锁失败: {self.lock_name}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.lock:
            await self.lock.release()