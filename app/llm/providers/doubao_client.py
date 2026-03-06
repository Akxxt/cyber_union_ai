"""
豆包模型适配器（字节跳动）。
豆包 API 兼容 OpenAI 格式，可直接复用 OpenAIClient。
"""
from typing import Optional
from app.llm.providers.openai_client import OpenAIClient


class DoubaoClient(OpenAIClient):
    """豆包客户端，使用 OpenAI 兼容接口。"""

    def __init__(self, model_name: str = "doubao-pro", api_key: Optional[str] = None,
                 base_url: str = "https://ark.cn-beijing.volces.com/api/v3", **kwargs):
        super().__init__(model_name=model_name, api_key=api_key, base_url=base_url, **kwargs)