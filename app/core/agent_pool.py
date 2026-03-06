"""
Agent实例池，复用Agent避免重复初始化。
"""
from typing import Dict, Optional
from app.core.agent_base import BaseAgent
from app.agents.agent_factory import AgentFactory
from app.core.constants import AgentRole


class AgentPool:
    """Agent池，每个角色可缓存多个实例。"""

    def __init__(self, max_size_per_role: int = 5):
        self._pool: Dict[AgentRole, list] = {}
        self.max_size = max_size_per_role

    async def acquire(self, role: AgentRole) -> BaseAgent:
        if role not in self._pool:
            self._pool[role] = []
        if self._pool[role]:
            return self._pool[role].pop()
        else:
            return AgentFactory.create_agent(role)

    async def release(self, agent: BaseAgent):
        role = agent.role_name
        if role not in self._pool:
            self._pool[role] = []
        if len(self._pool[role]) < self.max_size:
            self._pool[role].append(agent)


agent_pool = AgentPool()