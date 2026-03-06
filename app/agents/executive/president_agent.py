"""
总统Agent：行政核心，负责方案制定、任务拆解、结果整合。
"""
import json
import os
from typing import Dict, Any, List
from app.core.agent_base import BaseAgent
from app.core.constants import AgentRole, AgentType, TaskStatus
from app.audit.logger import audit_logger
from app.config.settings import settings


class PresidentAgent(BaseAgent):
    """总统Agent，行政分支核心。"""

    def __init__(self, **kwargs):
        super().__init__(
            role_name=AgentRole.PRESIDENT,
            role_type=AgentType.EXECUTIVE,
            branch=AgentType.EXECUTIVE,
            **kwargs
        )
        self.logger = audit_logger
        self.config_path = getattr(settings, 'executive_config_path', 'app/config/executive_config.json')
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载总统配置。"""
        default_config = {
            "plan_template": "方案目标：{goal}\n执行步骤：{steps}\n责任部门：{departments}\n时间节点：{timeline}\n验收标准：{criteria}",
            "department_mapping": {
                "能源": "ENERGY_DEPARTMENT",
                "财政": "TREASURY",
                "外交": "STATE_DEPARTMENT",
                "司法": "JUSTICE_DEPARTMENT",
                "国土安全": "DHS",
                "情报": "CIA_FBI",
                "监管": "REGULATORS"
            },
            "default_timeline": "30天",
            "default_criteria": "符合预期效果"
        }
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except Exception as e:
                self.logger.error(f"加载总统配置失败: {e}")
        return default_config

    async def validate_result(self, raw_output: str) -> bool:
        """
        校验输出必须包含：
        - 方案目标
        - 执行步骤
        - 责任部门
        - 时间节点
        - 验收标准
        """
        required = ["方案目标", "执行步骤", "责任部门", "时间节点", "验收标准"]
        if not all(phrase in raw_output for phrase in required):
            self.logger.warning("总统输出缺少必要部分")
            return False
        return True

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据当前状态执行对应职能。
        """
        task_id = state.get("task_id", "unknown")
        history = state.get("history", [])
        current_status = state.get("status")

        # 判断当前环节
        if "supreme_court_review_1" in history[-2:] and current_status == TaskStatus.PENDING_PLANNING:
            return await self._make_plan(state, task_id)
        elif "cabinet_execute" in history[-2:]:  # 内阁执行后，总统进行结果整合
            return await self._integrate_results(state, task_id)
        else:
            self.logger.warning(f"未知的总统环节", task_id=task_id)
            state["decision"] = "pass"
            return state

    async def _make_plan(self, state: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """
        方案制定：基于立法和司法意见生成执行方案，并拆分子任务。
        """
        legislation = state.get("bill", "")
        review_comment = state.get("review_comment", "")
        # 调用LLM生成方案（实际应在invoke中完成，此处假设invoke已生成输出）
        output = state.get("output", "")
        if not output:
            # 若invoke未输出，则根据模板构造（模拟）
            goal = "实现能源转型"
            steps = "1.调研；2.立法；3.执行"
            departments = "能源部"
            timeline = self.config["default_timeline"]
            criteria = self.config["default_criteria"]
            output = self.config["plan_template"].format(
                goal=goal,
                steps=steps,
                departments=departments,
                timeline=timeline,
                criteria=criteria
            )
            state["output"] = output

        # 解析方案，拆分子任务
        sub_tasks = []
        for keyword, dept in self.config["department_mapping"].items():
            if keyword in output:
                sub_tasks.append({
                    "department": dept,
                    "task": f"执行关于{keyword}的部分",
                    "status": "pending"
                })
        if not sub_tasks:
            sub_tasks.append({
                "department": "ENERGY_DEPARTMENT",
                "task": "执行方案",
                "status": "pending"
            })

        state["sub_tasks"] = sub_tasks
        state["decision"] = "pass"
        return state

    async def _integrate_results(self, state: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """
        结果整合：汇总内阁执行结果，形成最终交付物。
        """
        sub_tasks = state.get("sub_tasks", [])
        execution_reports = []
        for task in sub_tasks:
            dept = task["department"]
            report = state.get(f"execution_report_{dept}", "无报告")
            execution_reports.append(f"{dept}: {report}")
        final_output = "最终交付物：\n" + "\n".join(execution_reports)
        state["final_output"] = final_output
        state["output"] = final_output
        state["decision"] = "pass"
        return state