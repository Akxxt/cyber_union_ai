"""
内容审核插件：对接Step4合规引擎，进行敏感内容检测、脱敏。
"""
from typing import Optional
from app.plugins.base import BasePlugin, PluginMeta, PluginExecutionException
from app.audit.compliance import compliance_engine
from app.core.constants import ReviewResult


class ContentAuditPlugin(BasePlugin):
    """内容审核插件。"""

    META = {
        "plugin_id": "content_audit",
        "name": "内容审核插件",
        "description": "检测文本中的敏感内容、违规词汇，返回合规报告",
        "version": "1.0.0",
        "author": "system",
        "permission_level": 5,
        "category": "security",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "task_id": {"type": "string"}
            },
            "required": ["content"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "compliant": {"type": "boolean"},
                "violations": {"type": "array"},
                "report": {"type": "string"}
            }
        }
    }

    async def on_load(self): pass
    async def on_unload(self): pass
    async def on_enable(self): pass
    async def on_disable(self): pass

    async def execute(self, **kwargs):
        content = kwargs.get("content")
        task_id = kwargs.get("task_id", "unknown")
        if not content:
            raise PluginExecutionException("缺少 content 参数")

        report = compliance_engine.check_content_compliance(task_id, content, "plugin")
        return {
            "compliant": report.review_result == ReviewResult.PASSED,
            "violations": [v.dict() for v in report.violations],
            "report": compliance_engine.generate_compliance_report(report)
        }