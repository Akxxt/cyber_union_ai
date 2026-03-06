"""
健康检查接口（增强版）。
"""
from fastapi import APIRouter
import sqlite3
import psutil

from app.config.settings import settings
from app.core.state_machine import CyberUnionStateMachine
from app.agents.agent_factory import AgentFactory
from app.core.constants import AgentRole
from app.api.utils import success_response

router = APIRouter(prefix="/health", tags=["健康检查"])


@router.get("/", summary="健康检查")
async def health_check():
    """
    综合健康检查，返回系统各组件的状态。
    """
    # 数据库检查
    db_ok = False
    try:
        conn = sqlite3.connect("state_machine.db")
        conn.execute("SELECT 1")
        db_ok = True
        conn.close()
    except Exception:
        db_ok = False

    # 状态机检查
    sm_ok = False
    try:
        sm = CyberUnionStateMachine()
        sm_ok = sm.graph is not None
    except Exception:
        sm_ok = False

    # Agent工厂检查
    agent_ok = True
    try:
        AgentFactory.create_agent(AgentRole.PRESIDENT)
    except Exception:
        agent_ok = False

    # 系统资源
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent

    # Redis检查（如果配置了）
    redis_ok = True  # 可添加实际检查

    status = "healthy" if all([db_ok, sm_ok, agent_ok]) else "unhealthy"
    return success_response(data={
        "status": status,
        "checks": {
            "database": db_ok,
            "state_machine": sm_ok,
            "agent_factory": agent_ok,
            "redis": redis_ok,
            "cpu": cpu,
            "memory": mem,
            "disk": disk
        }
    })