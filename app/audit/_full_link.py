"""
全链路审计：统一记录操作、执行、合规、Token日志，支持按task_id追溯。
"""
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.core.redis_client import RedisClient
from app.audit.logger import audit_logger


class AuditManager:
    """审计管理器，负责各类日志的写入与查询。"""

    def __init__(self):
        self.redis = None

    async def _get_redis(self):
        if self.redis is None:
            self.redis = await RedisClient.get_client()
        return self.redis

    async def log_operation(self, task_id: str, operator: str, action: str, detail: Dict):
        """操作日志：任务创建、暂停、终止等。"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": task_id,
            "operator": operator,
            "action": action,
            "detail": detail,
            "type": "operation"
        }
        redis = await self._get_redis()
        await redis.rpush(f"audit:task:{task_id}", json.dumps(entry))
        audit_logger.info(f"操作日志: {operator} {action}", task_id=task_id)

    async def log_execution(self, task_id: str, node: str, agent: str, status: str, detail: Dict):
        """执行日志：每个Agent节点执行记录。"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": task_id,
            "node": node,
            "agent": agent,
            "status": status,
            "detail": detail,
            "type": "execution"
        }
        redis = await self._get_redis()
        await redis.rpush(f"audit:task:{task_id}", json.dumps(entry))

    async def log_compliance(self, task_id: str, rule_id: str, content: str, risk: str, result: str):
        """合规日志：敏感内容、违宪等。"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": task_id,
            "rule_id": rule_id,
            "content": content[:100],
            "risk": risk,
            "result": result,
            "type": "compliance"
        }
        redis = await self._get_redis()
        await redis.rpush(f"audit:task:{task_id}", json.dumps(entry))

    async def log_token(self, task_id: str, agent: str, tokens: int, node: str):
        """Token消耗日志。"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": task_id,
            "agent": agent,
            "tokens": tokens,
            "node": node,
            "type": "token"
        }
        redis = await self._get_redis()
        await redis.rpush(f"audit:task:{task_id}", json.dumps(entry))

    async def get_task_logs(self, task_id: str, log_type: Optional[str] = None) -> List[Dict]:
        """获取指定任务的所有日志，可筛选类型。"""
        redis = await self._get_redis()
        raw_logs = await redis.lrange(f"audit:task:{task_id}", 0, -1)
        logs = [json.loads(l) for l in raw_logs]
        if log_type:
            logs = [l for l in logs if l.get("type") == log_type]
        return logs

    async def export_task_logs(self, task_id: str) -> str:
        """导出任务所有日志为JSON字符串。"""
        logs = await self.get_task_logs(task_id)
        return json.dumps(logs, indent=2, ensure_ascii=False)


audit_manager = AuditManager()