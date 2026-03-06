"""
OpenAI 模型适配器。
"""
import openai
from openai import AsyncOpenAI, OpenAI
from typing import List, Dict, Any, AsyncIterator
from app.llm.base import BaseLLMClient, LLMResponse, LLMCallException


class OpenAIClient(BaseLLMClient):
    """OpenAI 客户端，支持 GPT 系列。"""

    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None,
                 base_url: Optional[str] = None, **kwargs):
        super().__init__(model_name, api_key, **kwargs)
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.sync_client = OpenAI(api_key=api_key, base_url=base_url)

    async def agenerate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                **kwargs
            )
            return self._parse_response(response)
        except openai.APITimeoutError:
            raise LLMCallException("OpenAI 请求超时")
        except openai.APIError as e:
            raise LLMCallException(f"OpenAI API错误: {e}")
        except Exception as e:
            raise LLMCallException(f"OpenAI 调用异常: {str(e)}")

    def generate(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        try:
            response = self.sync_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                **kwargs
            )
            return self._parse_response(response)
        except Exception as e:
            raise LLMCallException(f"OpenAI 同步调用异常: {str(e)}")

    async def astream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True,
            **kwargs
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    def count_tokens(self, text: str) -> int:
        try:
            import tiktoken
            enc = tiktoken.encoding_for_model(self.model_name)
            return len(enc.encode(text))
        except Exception:
            # 后备方案：简单按字符估算
            return len(text) // 4

    def _parse_response(self, raw) -> LLMResponse:
        choice = raw.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            total_tokens=raw.usage.total_tokens,
            prompt_tokens=raw.usage.prompt_tokens,
            completion_tokens=raw.usage.completion_tokens,
            model_name=self.model_name,
            finish_reason=choice.finish_reason,
            raw_response=raw
        )