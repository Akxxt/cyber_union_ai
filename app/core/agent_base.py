"""
Agent统一基类（最终版）。
所有Agent必须继承此类，统一LLM调用、插件调用、日志、Token统计、超时控制。
"""
import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

from app.config.settings import settings
from app.core.constants import AgentRole, AgentType, ErrorCode
from app.utils.exception_utils import BusinessException
from app.llm.llm_factory import llm_factory
from app.llm.base import LLMResponse
from app.llm.function_calling import function_manager
from app.audit.logger import audit_logger
from app.plugins.manager import plugin_manager


class BaseAgent(ABC):
    """
    所有Agent的抽象基类。
    """

    def __init__(
        self,
        role_name: AgentRole,
        role_type: AgentType,
        branch: AgentType,
        system_prompt: Optional[str] = None,
        token_budget: Optional[int] = None,
        timeout: Optional[int] = None,
        role_id: Optional[str] = None,
    ):
        self.role_id = role_id or f"agent_{uuid4().hex[:8]}"
        self.role_name = role_name
        self.role_type = role_type
        self.branch = branch
        self.system_prompt = system_prompt
        self.token_budget = token_budget or settings.default_token_budget
        self.timeout = timeout or settings.task_max_execution_seconds

        self.is_active = True
        self.execution_count = 0
        self.last_execution_time: Optional[datetime] = None
        self._token_used = 0

        # 通过工厂获取大模型客户端（可按角色指定模型）
        self.llm_client = llm_factory.get_client(role=self.role_name.value)

        self.logger = audit_logger

    async def render_prompt(self, variables: Dict[str, Any]) -> str:
        """渲染Prompt，可从数据库获取模板。"""
        if self.system_prompt:
            template_content = self.system_prompt
        else:
            from app.llm.prompt_template import TemplateManager
            tm = TemplateManager()
            template = await tm.get_active_template(self.role_name)
            template_content = template.content if template else ""

        rendered = template_content
        for key, value in variables.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        return rendered

    @abstractmethod
    async def validate_result(self, raw_output: str) -> bool:
        """校验LLM输出是否符合角色职能要求。"""
        pass

    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """核心业务逻辑。"""
        pass

    def _get_role_permission_level(self) -> int:
        """获取当前角色的权限等级（用于插件过滤）。"""
        mapping = getattr(settings, 'role_permission_levels', {})
        return mapping.get(self.role_name.value, 1)

    async def invoke(self, task_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        核心执行入口。
        """
        self.execution_count += 1
        self.last_execution_time = datetime.now()

        with self.logger.contextualize(task_id=task_id, agent_role=self.role_name.value):
            self.logger.info(f"Agent {self.role_name} 开始执行", module=self.__class__.__name__)

            try:
                # 渲染 Prompt
                variables = state.get("input_variables", {})
                system_prompt = await self.render_prompt(variables)

                # 获取当前角色可用的插件列表（根据权限等级）
                available_plugins = plugin_manager.list_plugins(enabled_only=True, min_level=self._get_role_permission_level())
                if available_plugins:
                    plugin_desc = "\n你可以使用以下工具：\n"
                    for p in available_plugins:
                        plugin_desc += f"- {p.name}: {p.description}\n"
                    system_prompt += plugin_desc

                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": state.get("input", "")})

                # 准备函数调用
                kwargs = {
                    "temperature": 0.3,
                    "max_tokens": 2000,
                }
                if settings.function_calling_enabled:
                    kwargs["functions"] = function_manager.get_definitions()

                # 超时控制调用
                try:
                    response: LLMResponse = await asyncio.wait_for(
                        self.llm_client.agenerate(messages, **kwargs),
                        timeout=self.timeout
                    )
                except asyncio.TimeoutError:
                    self.logger.error(f"Agent执行超时 ({self.timeout}秒)", module="invoke")
                    raise BusinessException(
                        code=ErrorCode.MODEL_TIMEOUT,
                        message=f"Agent {self.role_name} 执行超时"
                    )

                output = response.content

                # 更新 token 消耗
                self._token_used += response.total_tokens
                if self._token_used > self.token_budget:
                    self.logger.warning(f"Token预算超限: 已用 {self._token_used}, 预算 {self.token_budget}")

                # 尝试解析函数调用
                if settings.function_calling_enabled:
                    output = await function_manager.parse_and_execute(output, caller_role=self.role_name.value)

                # 结果校验
                if not await self.validate_result(output):
                    self.logger.warning(f"Agent输出校验失败: {output[:100]}...", module="validate")
                    raise BusinessException(
                        code=ErrorCode.MODEL_INVALID_RESPONSE,
                        message=f"Agent {self.role_name} 输出不符合要求"
                    )

                # 调用子类业务逻辑
                result_state = await self.execute(state)

                self.logger.info(f"Agent {self.role_name} 执行成功", token_used=self._token_used)

                return {
                    "output": output,
                    "token_usage": {
                        "total_tokens": response.total_tokens,
                        "prompt_tokens": response.prompt_tokens,
                        "completion_tokens": response.completion_tokens
                    },
                    "updated_state": result_state
                }

            except BusinessException:
                raise
            except Exception as e:
                self.logger.error(f"Agent执行未知异常: {e}", exc_info=True)
                raise BusinessException(
                    code=ErrorCode.TASK_EXECUTION_FAILED,
                    message=f"Agent {self.role_name} 执行失败",
                    details={"error": str(e)}
                )

    def get_token_usage(self) -> int:
        return self._token_used

    async def handle_timeout(self):
        self.logger.error("Agent执行超时，触发熔断")