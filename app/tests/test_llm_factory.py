import pytest
from app.llm.llm_factory import llm_factory
from app.llm.providers.openai_client import OpenAIClient


def test_factory_get_client():
    client = llm_factory.get_client(model_name="gpt-4")
    assert isinstance(client, OpenAIClient)
    assert client.model_name == "gpt-4"