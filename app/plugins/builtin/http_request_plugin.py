"""
HTTP请求插件：发送HTTP请求，域名白名单限制。
"""
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from app.plugins.base import BasePlugin, PluginMeta, PluginExecutionException
from app.config.settings import settings


class HttpRequestPlugin(BasePlugin):
    """HTTP请求插件。"""

    META = {
        "plugin_id": "http_request",
        "name": "HTTP请求插件",
        "description": "发送HTTP GET/POST请求，域名需在白名单内",
        "version": "1.0.0",
        "author": "system",
        "permission_level": 4,
        "category": "network",
        "input_schema": {
            "type": "object",
            "properties": {
                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                "url": {"type": "string"},
                "headers": {"type": "object"},
                "params": {"type": "object"},
                "json": {"type": "object"},
                "timeout": {"type": "integer", "default": 10}
            },
            "required": ["method", "url"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "integer"},
                "headers": {"type": "object"},
                "body": {"type": "any"}
            }
        }
    }

    def __init__(self, meta: PluginMeta):
        super().__init__(meta)
        self.whitelist = getattr(settings, 'http_domain_whitelist', [])

    def _check_url(self, url: str):
        parsed = urlparse(url)
        host = parsed.hostname
        if not host:
            raise PluginExecutionException("无效URL")
        allowed = False
        for pattern in self.whitelist:
            if pattern in host or host == pattern:
                allowed = True
                break
        if not allowed:
            raise PluginExecutionException(f"域名 {host} 不在白名单内")

    async def on_load(self): pass
    async def on_unload(self): pass
    async def on_enable(self): pass
    async def on_disable(self): pass

    async def execute(self, **kwargs):
        method = kwargs.get("method", "GET").upper()
        url = kwargs.get("url")
        if not url:
            raise PluginExecutionException("缺少 url 参数")
        self._check_url(url)

        headers = kwargs.get("headers", {})
        params = kwargs.get("params")
        json_data = kwargs.get("json")
        timeout = kwargs.get("timeout", 10)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=timeout
                ) as resp:
                    try:
                        body = await resp.json()
                    except:
                        body = await resp.text()
                    return {
                        "status": resp.status,
                        "headers": dict(resp.headers),
                        "body": body
                    }
            except asyncio.TimeoutError:
                raise PluginExecutionException("请求超时")
            except Exception as e:
                raise PluginExecutionException(f"请求异常: {str(e)}")