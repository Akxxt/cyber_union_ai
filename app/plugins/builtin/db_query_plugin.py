"""
数据库查询插件：只读SQL查询，限制为SELECT，防止注入。
"""
import sqlite3
import re
from typing import List, Dict, Any
from app.plugins.base import BasePlugin, PluginMeta, PluginExecutionException
from app.config.settings import settings


class DbQueryPlugin(BasePlugin):
    """数据库查询插件，仅允许 SELECT 查询。"""

    META = {
        "plugin_id": "db_query",
        "name": "数据库查询插件",
        "description": "执行只读SQL查询，返回结果集",
        "version": "1.0.0",
        "author": "system",
        "permission_level": 4,
        "category": "data",
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {"type": "string"},
                "params": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["sql"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "columns": {"type": "array", "items": {"type": "string"}},
                "rows": {"type": "array", "items": {"type": "array"}}
            }
        }
    }

    def __init__(self, meta: PluginMeta):
        super().__init__(meta)
        self.db_path = settings.sqlite_url.replace("sqlite+aiosqlite:///", "")

    def _validate_sql(self, sql: str):
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith("SELECT"):
            raise PluginExecutionException("仅允许 SELECT 查询")
        # 防止多重语句
        if ";" in sql and not sql.strip().endswith(";"):
            raise PluginExecutionException("不支持多条语句")
        dangerous = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "PRAGMA"]
        for word in dangerous:
            if re.search(rf'\b{word}\b', sql_upper):
                raise PluginExecutionException(f"禁止使用 {word} 语句")

    async def on_load(self): pass
    async def on_unload(self): pass
    async def on_enable(self): pass
    async def on_disable(self): pass

    async def execute(self, **kwargs):
        sql = kwargs.get("sql")
        params = kwargs.get("params", [])
        self._validate_sql(sql)

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description] if cursor.description else []
            result_rows = [list(row) for row in rows]
            conn.close()
            return {"columns": columns, "rows": result_rows}
        except Exception as e:
            raise PluginExecutionException(f"查询失败: {str(e)}")