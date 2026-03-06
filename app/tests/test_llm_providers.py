import pytest
from unittest.mock import AsyncMock, patch
from app.llm.providers.openai_client import OpenAIClient


@pytest.mark.asyncio
async def test_openai_agenerate():
    client = OpenAIClient(api_key="test")
    with patch.object(client, 'client') as mock_client:
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock(message=AsyncMock(content="hello"))]
        mock_response.usage.total_tokens = 10
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 5
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        resp = await client.agenerate([{"role": "user", "content": "hi"}])
        assert resp.content == "hello"
        assert resp.total_tokens == 10