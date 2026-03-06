import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.core.agent_base import BaseAgent
from app.core.constants import AgentRole, AgentType, ErrorCode
from app.utils.exception_utils import BusinessException


class ConcreteAgent(BaseAgent):
    async def validate_result(self, raw_output: str) -> bool:
        return "valid" in raw_output

    async def execute(self, state: dict) -> dict:
        state["executed"] = True
        return state


@pytest.fixture
def agent():
    return ConcreteAgent(
        role_name=AgentRole.PRESIDENT,
        role_type=AgentType.EXECUTIVE,
        branch=AgentType.EXECUTIVE,
        system_prompt="You are president. Input: {{input}}",
        token_budget=1000,
        timeout=5
    )


@pytest.mark.asyncio
async def test_render_prompt(agent):
    rendered = await agent.render_prompt({"input": "hello"})
    assert rendered == "You are president. Input: hello"


@pytest.mark.asyncio
async def test_invoke_success(agent):
    mock_response = MagicMock()
    mock_response.content = "valid output"
    mock_response.total_tokens = 10
    mock_response.prompt_tokens = 5
    mock_response.completion_tokens = 5
    agent.llm_client.agenerate = AsyncMock(return_value=mock_response)

    state = {"input": "test", "input_variables": {"input": "test"}}
    result = await agent.invoke("task123", state)

    assert result["output"] == "valid output"
    assert result["token_usage"]["total_tokens"] == 10
    assert agent.get_token_usage() == 10


@pytest.mark.asyncio
async def test_invoke_validation_fail(agent):
    mock_response = MagicMock()
    mock_response.content = "invalid output"
    mock_response.total_tokens = 5
    agent.llm_client.agenerate = AsyncMock(return_value=mock_response)

    state = {"input": "test", "input_variables": {}}
    with pytest.raises(BusinessException) as exc:
        await agent.invoke("task123", state)
    assert exc.value.code == ErrorCode.MODEL_INVALID_RESPONSE


@pytest.mark.asyncio
async def test_invoke_timeout(agent):
    async def slow_generate(*args, **kwargs):
        await asyncio.sleep(10)
        return MagicMock()

    agent.llm_client.agenerate = slow_generate
    agent.timeout = 0.1

    state = {"input": "test", "input_variables": {}}
    with pytest.raises(BusinessException) as exc:
        await agent.invoke("task123", state)
    assert exc.value.code == ErrorCode.MODEL_TIMEOUT