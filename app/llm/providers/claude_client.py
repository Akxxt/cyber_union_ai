"""
Claude 模型适配器（Anthropic）。
"""
import json
import aiohttp
import asyncio
from typing import List, Dict, Any, AsyncIterator, Optional
from app.llm.base import BaseLLMClient, LLMResponse, LLMCallException


class ClaudeClient(BaseLLMClient):
    """Anthropic Claude 客户端。"""

    def __init__(self, model_name: str = "claude-3-opus-20240229", api_key: Optional[str] = None,
                 base_url: str = "https://api.anthropic.com/v1", **kwargs):
        super().__init__(model_name, api_key, **kwargs)
        self.base_url = base_url
        self.api_version = "2023-06-01"
        self.timeout = kwargs.get("timeout", 60)

    async def agenerate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        # 转换为 Claude 消息格式
        system = None
        claude_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                claude_messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                })
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "content-type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": claude_messages,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "temperature": kwargs.get("temperature", 0.7)
        }
        if system:
            payload["system"] = system
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                ) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        raise LLMCallException(f"Claude API错误: {resp.status} - {text}")
                    data = await resp.json()
                    return self._parse_response(data)
            except asyncio.TimeoutError:
                raise LLMCallException("Claude 请求超时")

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        import asyncio
        return asyncio.run(self.agenerate(messages, **kwargs))

    async def astream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterator[str]:
        # Claude 流式暂简化实现
        resp = await self.agenerate(messages, **kwargs)
        yield resp.content

    def count_tokens(self, text: str) -> int:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            return client.count_tokens(text)
        except:
            return len(text) // 4

    def _parse_response(self, raw: Dict) -> LLMResponse:
        content = raw.get("content", [{}])[0].get("text", "")
        usage = raw.get("usage", {})
        return LLMResponse(
            content=content,
            total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
            model_name=self.model_name,
            finish_reason=raw.get("stop_reason"),
            raw_response=raw
        )