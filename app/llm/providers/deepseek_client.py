"""
DeepSeek 模型适配器。
DeepSeek API 兼容 OpenAI 接口格式，可直接复用 OpenAI 客户端的逻辑。
"""
import json
from typing import List, Dict, Any, AsyncIterator, Optional
import aiohttp
from app.llm.base import BaseLLMClient, LLMResponse, LLMCallException


class DeepSeekClient(BaseLLMClient):
    """DeepSeek 模型客户端，兼容 OpenAI 接口。"""

    def __init__(self, model_name: str = "deepseek-chat", api_key: Optional[str] = None,
                 base_url: str = "https://api.deepseek.com/v1", **kwargs):
        super().__init__(model_name, api_key, **kwargs)
        self.base_url = base_url
        self.timeout = kwargs.get("timeout", 60)
        self.max_retries = kwargs.get("max_retries", 3)

    async def agenerate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            **kwargs
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                ) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        raise LLMCallException(f"DeepSeek API 错误: {resp.status} - {text}")
                    data = await resp.json()
                    return self._parse_response(data)
            except asyncio.TimeoutError:
                raise LLMCallException("DeepSeek 请求超时")
            except Exception as e:
                raise LLMCallException(f"DeepSeek 调用异常: {str(e)}")

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        import asyncio
        return asyncio.run(self.agenerate(messages, **kwargs))

    async def astream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterator[str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise LLMCallException(f"DeepSeek 流式错误: {resp.status} - {text}")
                async for line in resp.content:
                    if line:
                        line = line.decode('utf-8').strip()
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if delta:
                                    yield delta
                            except json.JSONDecodeError:
                                continue

    def count_tokens(self, text: str) -> int:
        try:
            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except ImportError:
            return len(text) // 4

    def _parse_response(self, raw: Dict) -> LLMResponse:
        choice = raw.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content", "")
        usage = raw.get("usage", {})
        return LLMResponse(
            content=content,
            total_tokens=usage.get("total_tokens", 0),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            model_name=self.model_name,
            finish_reason=choice.get("finish_reason"),
            raw_response=raw
        )