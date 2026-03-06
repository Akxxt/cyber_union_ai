"""
人事管理办公室 Agent：权限管理、Prompt分配、越权拦截。
"""
import json
import os
from typing import Dict, Any, Optional
from app.core.agent_base import BaseAgent
from app.core.constants import AgentRole, AgentType
from app.audit.logger import audit_logger
from app.config.settings import settings


class PermissionManager:
    """权限管理器，存储角色可执行的操作、可访问的数据。"""

    def __init__(self, config_path: str = "app/config/executive_config.json"):
        self.config_path = config_path
        self.permissions: Dict[str, Dict] = {}
        self._load_config()

    def _load_config(self):
        """从配置文件加载权限规则。"""
        default = {
            "PRESIDENT": {
                "allowed_nodes": ["president_plan", "president_inspect"],
                "allowed_data": ["bill", "review_comment", "sub_tasks"],
                "prompt_templates": ["president_plan", "president_inspect"]
            },
            "CONGRESS": {
                "allowed_nodes": ["congress_legislate", "congress_approve_plan", "congress_accept"],
                "allowed_data": ["bill", "plan", "execution_report"],
                "prompt_templates": ["congress_legislate", "congress_approve_plan", "congress_accept"]
            },
            "SUPREME_COURT": {
                "allowed_nodes": ["supreme_court_review_1", "supreme_court_review_2", "supreme_court_final"],
                "allowed_data": ["bill", "plan", "execution_report"],
                "prompt_templates": ["supreme_court_review"]
            },
            "ENERGY_DEPARTMENT": {
                "allowed_nodes": ["cabinet_execute"],
                "allowed_data": ["plan", "sub_tasks"],
                "prompt_templates": ["cabinet_execute"]
            }
        }
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if "permissions" in config:
                        default.update(config["permissions"])
            except Exception as e:
                audit_logger.error(f"加载权限配置失败: {e}")
        self.permissions = default

    def get_permissions(self, role: AgentRole) -> Dict:
        return self.permissions.get(role.value, {})

    def check_node_access(self, role: AgentRole, node_name: str) -> bool:
        perms = self.get_permissions(role)
        allowed = perms.get("allowed_nodes", [])
        return node_name in allowed

    def check_data_access(self, role: AgentRole, data_key: str) -> bool:
        perms = self.get_permissions(role)
        allowed = perms.get("allowed_data", [])
        return data_key in allowed

    def get_prompt_template(self, role: AgentRole, node_name: str) -> Optional[str]:
        perms = self.get_permissions(role)
        templates = perms.get("prompt_templates", [])
        return templates[0] if templates else None


class OPMAgent(BaseAgent):
    """人事管理办公室 Agent：权限管控。"""

    def __init__(self, **kwargs):
        super().__init__(
            role_name=AgentRole.OPM,
            role_type=AgentType.EXECUTIVE,
            branch=AgentType.EXECUTIVE,
            **kwargs
        )
        self.logger = audit_logger
        self.permission_manager = PermissionManager()

    async def validate_result(self, raw_output: str) -> bool:
        return True

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行权限检查：根据当前节点和角色，校验是否允许。
        """
        task_id = state.get("task_id", "unknown")
        current_node = state.get("current_node")
        current_role = state.get("current_agent")
        if not current_role:
            self.logger.warning("无法获取当前角色", task_id=task_id)
            state["decision"] = "reject"
            state["reject_reason"] = "无法确定当前角色"
            return state

        # 将字符串角色转换为枚举（如果传入的是字符串）
        if isinstance(current_role, str):
            try:
                current_role = AgentRole(current_role)
            except ValueError:
                self.logger.warning(f"无效的角色名称: {current_role}", task_id=task_id)
                state["decision"] = "reject"
                state["reject_reason"] = f"无效的角色: {current_role}"
                return state

        if not self.permission_manager.check_node_access(current_role, current_node):
            self.logger.warning(f"角色 {current_role.value} 无权执行节点 {current_node}", task_id=task_id)
            state["decision"] = "reject"
            state["reject_reason"] = f"权限不足：角色 {current_role.value} 不能执行 {current_node}"
            return state

        # 校验关键数据字段访问
        for key in ["bill", "plan", "execution_report"]:
            if key in state and not self.permission_manager.check_data_access(current_role, key):
                self.logger.warning(f"角色 {current_role.value} 无权访问数据 {key}", task_id=task_id)
                state["decision"] = "reject"
                state["reject_reason"] = f"权限不足：无权访问 {key}"
                return state

        state["decision"] = "pass"
        return state

    async def get_prompt_for_role(self, role: AgentRole, node: str) -> Optional[str]:
        return self.permission_manager.get_prompt_template(role, node)