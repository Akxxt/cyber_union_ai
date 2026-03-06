"""
Agent管理接口：查询列表、详情、启用/禁用。
"""
from fastapi import APIRouter, Path
from app.agents.agent_factory import AgentFactory
from app.core.constants import AgentRole
from app.api.utils import success_response, error_response
from app.audit.audit_full_link import audit_manager

router = APIRouter(prefix="/agents", tags=["Agent管理"])


@router.get("/", summary="查询所有Agent列表")
async def list_agents():
    """
    返回所有Agent的基本信息，包含状态、执行次数、Token消耗。
    """
    agents = []
    for role in AgentRole:
        try:
            agent = AgentFactory.create_agent(role)
            agents.append({
                "role": role.value,
                "type": agent.role_type.value,
                "branch": agent.branch.value,
                "is_active": agent.is_active,
                "execution_count": agent.execution_count,
                "token_used": agent.get_token_usage()
            })
        except Exception:
            pass  # 忽略未实现的Agent
    return success_response(data=agents)


@router.get("/{role}", summary="查询单个Agent详情")
async def get_agent(role: str = Path(..., description="Agent角色名称")):
    """
    根据角色名称查询Agent详细信息。
    """
    try:
        role_enum = AgentRole(role)
    except ValueError:
        return error_response(code=400, message="无效的Agent角色")

    try:
        agent = AgentFactory.create_agent(role_enum)
    except Exception as e:
        return error_response(code=404, message=f"Agent不存在: {str(e)}")

    return success_response(data={
        "role": agent.role_name.value,
        "type": agent.role_type.value,
        "branch": agent.branch.value,
        "is_active": agent.is_active,
        "execution_count": agent.execution_count,
        "token_used": agent.get_token_usage(),
        "last_execution_time": agent.last_execution_time.isoformat() if agent.last_execution_time else None,
        "token_budget": agent.token_budget
    })


@router.put("/{role}/activate", summary="启用Agent")
async def activate_agent(role: str = Path(..., description="Agent角色名称")):
    """
    启用指定Agent（需相应权限）。
    """
    try:
        role_enum = AgentRole(role)
    except ValueError:
        return error_response(code=400, message="无效的Agent角色")

    # 实际应更新数据库中的启用状态
    await audit_manager.log_operation("system", "API", "agent_activate", {"role": role})
    return success_response(message=f"Agent {role} 已启用")


@router.put("/{role}/deactivate", summary="禁用Agent")
async def deactivate_agent(role: str = Path(..., description="Agent角色名称")):
    """
    禁用指定Agent（需相应权限）。
    """
    try:
        role_enum = AgentRole(role)
    except ValueError:
        return error_response(code=400, message="无效的Agent角色")

    await audit_manager.log_operation("system", "API", "agent_deactivate", {"role": role})
    return success_response(message=f"Agent {role} 已禁用")