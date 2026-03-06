"""
任务流可视化接口：获取任务节点和边数据。
"""
from fastapi import APIRouter, Path
from app.core.state_machine import CyberUnionStateMachine
from app.api.utils import success_response, error_response

router = APIRouter(prefix="/visualization", tags=["任务流可视化"])


@router.get("/task/{task_id}/graph", summary="获取任务流程图数据")
async def get_task_graph(task_id: str = Path(..., description="任务ID")):
    """
    返回任务执行流程图所需的节点和边数据。
    """
    sm = CyberUnionStateMachine()
    state = await sm.load_state(task_id)
    if not state:
        return error_response(code=404, message="任务不存在")

    # 构建节点列表（每个历史步骤为一个节点）
    nodes = []
    edges = []
    audit_logs = state.get("audit_logs", [])
    # 按时间排序
    logs = sorted(audit_logs, key=lambda x: x.get("time", ""))

    for i, log in enumerate(logs):
        node_id = f"node_{i}"
        nodes.append({
            "id": node_id,
            "label": log.get("node", ""),
            "status": log.get("result", "unknown"),
            "time": log.get("time"),
            "error": log.get("error"),
            "duration": 0  # 可计算相邻时间差
        })
        if i > 0:
            edges.append({
                "from": f"node_{i-1}",
                "to": node_id
            })

    # 如果任务还在运行，添加当前节点
    if state.get("status") not in ["COMPLETED", "FAILED", "TERMINATED"]:
        nodes.append({
            "id": "current",
            "label": state.get("current_agent", "未知"),
            "status": "running",
            "time": None
        })
        if nodes:
            edges.append({"from": nodes[-2]["id"], "to": "current"})

    return success_response(data={"nodes": nodes, "edges": edges})