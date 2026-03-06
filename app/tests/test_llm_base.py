import pytest
from app.llm.base import LLMResponse, LLMCallException


def test_llm_response_creation():
    resp = LLMResponse(content="test", model_name="gpt-4")
    assert resp.content == "test"
    assert resp.total_tokens == 0