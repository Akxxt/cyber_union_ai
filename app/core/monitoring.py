"""
异常监控钩子，记录关键指标并触发告警。
"""
import sqlite3
from datetime import datetime
from typing import Dict, Any, List
from app.audit.logger import audit_logger
from app.config.settings import settings


class MetricsRecorder:
    """指标记录器，将关键指标存入SQLite。"""

    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                status TEXT,
                duration REAL,
                token_used INTEGER,
                agent_count INTEGER,
                create_time TIMESTAMP,
                complete_time TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_role TEXT,
                execution_count INTEGER,
                avg_duration REAL,
                total_tokens INTEGER,
                date TEXT
            )
        """)
        conn.commit()
        conn.close()

    def record_task_completion(self, task_id: str, status: str, duration: float,
                               token_used: int, agent_count: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO task_metrics (task_id, status, duration, token_used, agent_count, complete_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (task_id, status, duration, token_used, agent_count, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()


class AlertHook:
    """告警钩子，当指标异常时触发。"""

    @staticmethod
    def check_task_failure_rate(recent_tasks: List[Dict]):
        if not recent_tasks:
            return
        failed = sum(1 for t in recent_tasks if t["status"] == "FAILED")
        rate = failed / len(recent_tasks)
        if rate > 0.1:
            audit_logger.warning(f"任务失败率过高: {rate:.2%}，请检查系统")
            # 可发送HTTP请求到监控系统

    @staticmethod
    def check_token_budget_usage(used: int, budget: int):
        if budget > 0 and used / budget > 0.8:
            audit_logger.warning(f"Token预算使用超过80%: {used}/{budget}")


metrics_recorder = MetricsRecorder()
alert_hook = AlertHook()