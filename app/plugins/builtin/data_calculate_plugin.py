"""
数据计算插件：安全的数值计算、统计分析。
"""
import ast
import operator
from typing import Any, Dict, List, Union
from app.plugins.base import BasePlugin, PluginMeta, PluginExecutionException


class DataCalculatePlugin(BasePlugin):
    """数据计算插件，使用安全eval进行简单计算。"""

    META = {
        "plugin_id": "data_calculate",
        "name": "数据计算插件",
        "description": "执行数值计算、统计分析，支持四则运算、求和、平均值等",
        "version": "1.0.0",
        "author": "system",
        "permission_level": 2,
        "category": "utility",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["calc", "sum", "avg", "max", "min"]},
                "expression": {"type": "string"},
                "numbers": {"type": "array", "items": {"type": "number"}}
            },
            "required": ["operation"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "result": {"type": "any"}
            }
        }
    }

    def __init__(self, meta: PluginMeta):
        super().__init__(meta)
        self._allowed_names = {
            'abs': abs, 'round': round, 'max': max, 'min': min, 'sum': sum,
            'len': len, 'float': float, 'int': int
        }

    async def on_load(self): pass
    async def on_unload(self): pass
    async def on_enable(self): pass
    async def on_disable(self): pass

    def _safe_eval(self, expr: str):
        """使用 ast 安全求值。"""
        tree = ast.parse(expr, mode='eval')
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name) or node.func.id not in self._allowed_names:
                    raise PluginExecutionException(f"不允许的函数调用: {ast.unparse(node)}")
        code = compile(tree, filename='', mode='eval')
        return eval(code, {"__builtins__": {}}, self._allowed_names)

    async def execute(self, **kwargs):
        op = kwargs.get("operation")
        if op == "calc":
            expr = kwargs.get("expression")
            if not expr:
                raise PluginExecutionException("calc 需要 expression 参数")
            try:
                result = self._safe_eval(expr)
            except Exception as e:
                raise PluginExecutionException(f"计算错误: {str(e)}")
            return {"result": result}
        elif op in ("sum", "avg", "max", "min"):
            numbers = kwargs.get("numbers")
            if not numbers or not isinstance(numbers, list):
                raise PluginExecutionException("需要 numbers 列表")
            if op == "sum":
                result = sum(numbers)
            elif op == "avg":
                result = sum(numbers) / len(numbers) if numbers else 0
            elif op == "max":
                result = max(numbers)
            elif op == "min":
                result = min(numbers)
            return {"result": result}
        else:
            raise PluginExecutionException(f"未知操作: {op}")