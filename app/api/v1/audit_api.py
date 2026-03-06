"""
审计日志接口：查询、导出。
"""
from fastapi import APIRouter, Query, Path
from typing import Optional
from fastapi.responses import Response

from app.audit.audit_full_link import audit_manager
from app.api.utils import success_response

router = APIRouter(prefix="/audit", tags=["审计日志"])


@router.get("/logs", summary="查询审计日志")
async def query_logs(
    task_id: Optional[str] = Query(None, description="任务ID"),
    log_type: Optional[str] = Query(None, description="日志类型(operation/execution/compliance/token)"),
    start_time: Optional[float] = Query(None, description="开始时间戳"),
    end_time: Optional[float] = Query(None, description="结束时间戳")
):
    """
    查询审计日志，支持按任务ID、类型、时间范围筛选。
    """
    # 简化：仅按任务ID查询，其他筛选可后续实现
    if task_id:
        logs = await audit_manager.get_task_logs(task_id, log_type)
        return success_response(data={"logs": logs})
    # 否则返回最近100条（需实现全局日志查询）
    return success_response(data={"logs": []})


@router.get("/task/{task_id}", summary="查询指定任务的所有日志")
async def get_task_logs(
    task_id: str = Path(..., description="任务ID"),
    log_type: Optional[str] = Query(None, description="日志类型")
):
    """
    获取指定任务的所有审计日志。
    """
    logs = await audit_manager.get_task_logs(task_id, log_type)
    return success_response(data={"logs": logs})


@router.get("/task/{task_id}/export", summary="导出任务日志")
async def export_task_logs(task_id: str = Path(..., description="任务ID")):
    """
    将指定任务的日志导出为JSON文件。
    """
    json_str = await audit_manager.export_task_logs(task_id)
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=audit_{task_id}.json"}
    )