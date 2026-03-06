"""
文件操作插件：读取、写入、列表查询，限制在指定工作目录。
"""
import os
import aiofiles
from pathlib import Path
from typing import List, Optional
from app.plugins.base import BasePlugin, PluginMeta, PluginExecutionException
from app.config.settings import settings


class FileOperationPlugin(BasePlugin):
    """文件操作插件。"""

    META = {
        "plugin_id": "file_operation",
        "name": "文件操作插件",
        "description": "读取、写入、列出文件，仅限工作目录内操作",
        "version": "1.0.0",
        "author": "system",
        "permission_level": 3,
        "category": "system",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["read", "write", "list"]},
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["action", "path"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {"type": "any"},
                "error": {"type": "string"}
            }
        }
    }

    def __init__(self, meta: PluginMeta):
        super().__init__(meta)
        self.work_dir = Path(getattr(settings, 'file_plugin_work_dir', './plugin_files')).resolve()
        self.work_dir.mkdir(parents=True, exist_ok=True)

    async def on_load(self):
        pass

    async def on_unload(self):
        pass

    async def on_enable(self):
        pass

    async def on_disable(self):
        pass

    def _safe_path(self, path: str) -> Path:
        """将相对路径转换为绝对路径，并检查是否在 work_dir 内。"""
        abs_path = (self.work_dir / path).resolve()
        if not str(abs_path).startswith(str(self.work_dir)):
            raise PluginExecutionException(f"路径越权: {path}")
        return abs_path

    async def execute(self, **kwargs):
        action = kwargs.get("action")
        path = kwargs.get("path")
        if not path:
            raise PluginExecutionException("缺少 path 参数")

        safe_path = self._safe_path(path)

        if action == "read":
            if not safe_path.exists():
                return {"success": False, "error": "文件不存在"}
            if safe_path.is_dir():
                return {"success": False, "error": "路径是目录"}
            async with aiofiles.open(safe_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            return {"success": True, "data": content}

        elif action == "write":
            content = kwargs.get("content")
            if content is None:
                raise PluginExecutionException("写操作需要 content 参数")
            safe_path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(safe_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            return {"success": True}

        elif action == "list":
            if not safe_path.exists():
                return {"success": False, "error": "路径不存在"}
            if safe_path.is_file():
                return {"success": True, "data": [str(safe_path.name)]}
            files = [str(p.relative_to(self.work_dir)) for p in safe_path.iterdir()]
            return {"success": True, "data": files}

        else:
            raise PluginExecutionException(f"未知动作: {action}")