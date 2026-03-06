"""
Prompt模板管理接口：增删改查、启用/禁用。
"""
from fastapi import APIRouter, Body, Query, Path
from typing import Optional
from pydantic import BaseModel

from app.llm.prompt_template import TemplateManager, PromptTemplate
from app.core.constants import AgentRole
from app.api.utils import success_response, error_response

router = APIRouter(prefix="/templates", tags=["模板管理"])

manager = TemplateManager()


class TemplateCreateRequest(BaseModel):
    role: AgentRole
    content: str
    description: Optional[str] = ""
    version: str = "1.0.0"
    is_active: bool = True


class TemplateUpdateRequest(BaseModel):
    content: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None


@router.post("/", summary="创建模板")
async def create_template(req: TemplateCreateRequest):
    """
    创建新的Prompt模板。
    """
    template = PromptTemplate(
        role=req.role,
        content=req.content,
        description=req.description,
        version=req.version,
        is_active=req.is_active
    )
    template_id = await manager.create_template(template)
    return success_response(data={"template_id": template_id})


@router.get("/", summary="查询模板列表")
async def list_templates(role: Optional[AgentRole] = Query(None, description="按角色筛选")):
    """
    返回所有模板，可按角色筛选。
    """
    templates = await manager.list_templates(role)
    data = [t.dict() for t in templates]
    return success_response(data=data)


@router.get("/{template_id}", summary="查询单个模板")
async def get_template(template_id: str = Path(..., description="模板ID")):
    """
    根据ID查询模板详情。
    """
    template = await manager.get_template(template_id)
    if template:
        return success_response(data=template.dict())
    return error_response(code=404, message="模板不存在")


@router.put("/{template_id}", summary="更新模板")
async def update_template(
    template_id: str = Path(..., description="模板ID"),
    req: TemplateUpdateRequest = Body(...)
):
    """
    更新模板的部分字段。
    """
    updates = req.dict(exclude_unset=True)
    success = await manager.update_template(template_id, **updates)
    if success:
        return success_response(message="模板更新成功")
    return error_response(code=404, message="模板不存在")


@router.delete("/{template_id}", summary="删除模板")
async def delete_template(template_id: str = Path(..., description="模板ID")):
    """
    物理删除模板。
    """
    success = await manager.delete_template(template_id)
    if success:
        return success_response(message="模板删除成功")
    return error_response(code=404, message="模板不存在")


@router.put("/{template_id}/activate", summary="启用模板")
async def activate_template(template_id: str = Path(..., description="模板ID")):
    """
    将指定模板设为启用状态（其他同角色模板自动禁用？根据业务决定）。
    """
    success = await manager.update_template(template_id, is_active=True)
    if success:
        return success_response(message="模板已启用")
    return error_response(code=404, message="模板不存在")