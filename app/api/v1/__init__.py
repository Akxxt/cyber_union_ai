from fastapi import APIRouter
from . import task_api, agent_api, template_api, audit_api, health, visualization_api, system_api, plugin_api

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(task_api.router)
v1_router.include_router(agent_api.router)
v1_router.include_router(template_api.router)
v1_router.include_router(audit_api.router)
v1_router.include_router(health.router)
v1_router.include_router(visualization_api.router)
v1_router.include_router(system_api.router)
v1_router.include_router(plugin_api.router)