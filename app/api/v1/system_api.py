"""
系统状态接口：预算、权限查询。
"""
from fastapi import APIRouter, Path
from app.agents.executive.omb_agent import OMBAgent, budget_manager
from app.agents.executive.opm_agent import PermissionManager
from app.api.utils import success_response, error_response

router = APIRouter(prefix="/system", tags=["系统状态"])


@router.get("/budget/{task_id}", summary="查询任务预算状态")
async def get_budget_status(task_id: str = Path(..., description="任务ID")):
    """
    返回指定任务的Token预算使用情况。
    """
    omb = OMBAgent()
    status = await omb.get_budget_status(task_id)
    return success_response(data=status)


@router.get("/permissions/{role}", summary="查询角色权限")
async def get_permissions(role: str = Path(..., description="角色名称")):
    """
    返回指定角色的权限配置。
    """
    pm = PermissionManager()
    perms = pm.get_permissions(role)
    return success_response(data=perms)