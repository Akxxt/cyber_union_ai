#!/usr/bin/env python
"""
预置模拟数据脚本：创建演示任务、Agent状态、插件等。
仅在数据为空时执行。
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.scheduler import Task, TaskScheduler
from app.core.state_machine import CyberUnionStateMachine
from app.core.constants import TaskPriority, TaskStatus
from app.llm.prompt_template import TemplateManager, PromptTemplate
from app.core.constants import AgentRole
from app.plugins.manager import plugin_manager
from app.audit.audit_full_link import audit_manager
import sqlite3


async def init_demo_data():
    print("开始初始化演示数据...")

    # 检查是否已有数据（以任务表为例）
    sm = CyberUnionStateMachine()
    # 尝试加载一个已知任务ID，如果存在则跳过
    demo_task_id = "demo_task_energy_policy"
    existing = await sm.load_state(demo_task_id)
    if existing:
        print("演示数据已存在，跳过初始化。")
        return

    # 1. 创建一条演示任务（能源政策）
    task = Task(
        task_id=demo_task_id,
        input="制定一项新能源政策，要求减少碳排放30%，并确保能源安全。",
        priority=TaskPriority.HIGH,
        status=TaskStatus.COMPLETED,  # 直接标记完成，或者让状态机模拟执行
        create_time=datetime.utcnow() - timedelta(hours=2),
        update_time=datetime.utcnow()
    )
    # 将任务状态保存到Redis（分布式调度器）
    from app.core.redis_client import RedisClient
    redis = await RedisClient.get_client()
    await redis.set(f"task:{demo_task_id}", task.json())

    # 模拟状态机执行轨迹（简化为最终状态）
    demo_state = {
        "task_id": demo_task_id,
        "status": TaskStatus.COMPLETED,
        "input": task.input,
        "output": "方案已制定并执行，碳排放降低32%，能源安全达标。",
        "token_usage": {"total_tokens": 25000},
        "audit_logs": [
            {"node": "white_house_sort", "time": (datetime.utcnow() - timedelta(hours=2)).isoformat(), "result": "success"},
            {"node": "congress_legislate", "time": (datetime.utcnow() - timedelta(hours=1, minutes=50)).isoformat(), "result": "success"},
            {"node": "supreme_court_review_1", "time": (datetime.utcnow() - timedelta(hours=1, minutes=40)).isoformat(), "result": "success"},
            {"node": "president_plan", "time": (datetime.utcnow() - timedelta(hours=1, minutes=30)).isoformat(), "result": "success"},
            {"node": "congress_approve_plan", "time": (datetime.utcnow() - timedelta(hours=1, minutes=20)).isoformat(), "result": "success"},
            {"node": "supreme_court_review_2", "time": (datetime.utcnow() - timedelta(hours=1, minutes=10)).isoformat(), "result": "success"},
            {"node": "cabinet_execute", "time": (datetime.utcnow() - timedelta(hours=1)).isoformat(), "result": "success"},
            {"node": "president_inspect", "time": (datetime.utcnow() - timedelta(minutes=50)).isoformat(), "result": "success"},
            {"node": "congress_accept", "time": (datetime.utcnow() - timedelta(minutes=40)).isoformat(), "result": "success"},
            {"node": "supreme_court_final", "time": (datetime.utcnow() - timedelta(minutes=30)).isoformat(), "result": "success"},
        ],
        "history": ["white_house_sort", "congress_legislate", "supreme_court_review_1", "president_plan", 
                    "congress_approve_plan", "supreme_court_review_2", "cabinet_execute", "president_inspect", 
                    "congress_accept", "supreme_court_final"],
        "current_agent": None,
        "decision": "pass",
        "retry_count": 0,
        "max_retries": 3,
        "bill": "新能源法案草案...",
        "plan": "能源转型计划...",
        "execution_reports": {"ENERGY_DEPARTMENT": "已完成风电项目", "TREASURY": "资金已拨付"},
        "final_output": "最终交付物..."
    }
    await sm.save_state(demo_task_id, demo_state)

    # 2. 创建一些Prompt模板
    tm = TemplateManager()
    await tm.init_db()
    templates = [
        PromptTemplate(
            role=AgentRole.PRESIDENT,
            content="你是美国总统，请根据国会立法和最高法院意见，制定详细的执行方案。",
            version="1.0",
            description="总统方案制定模板",
            is_active=True
        ),
        PromptTemplate(
            role=AgentRole.CONGRESS,
            content="你是美国国会，负责立法和审批。请根据输入生成法案或审批意见。",
            version="1.0",
            description="国会模板",
            is_active=True
        ),
        PromptTemplate(
            role=AgentRole.SUPREME_COURT,
            content="你是最高法院，进行合宪性审查。请输出审查结论和法律依据。",
            version="1.0",
            description="最高法院模板",
            is_active=True
        )
    ]
    for t in templates:
        await tm.create_template(t)

    # 3. 插件已在插件目录，无需额外创建，但可预置启用状态
    await plugin_manager.scan_and_load()
    # 启用所有插件（默认已启用）
    for pid in plugin_manager._plugins:
        await plugin_manager.enable_plugin(pid)

    # 4. 添加一些审计日志示例
    await audit_manager.log_operation(demo_task_id, "system", "create", {"source": "demo"})
    await audit_manager.log_token(demo_task_id, "PRESIDENT", 5000, "president_plan")
    await audit_manager.log_token(demo_task_id, "CONGRESS", 8000, "congress_legislate")
    await audit_manager.log_compliance(demo_task_id, "sensitive_content", "none", "low", "pass")

    print("演示数据初始化完成！")


if __name__ == "__main__":
    asyncio.run(init_demo_data())