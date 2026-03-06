"""
全局异常捕获与处理，确保系统不崩溃，异常可追溯。
"""
import traceback
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from app.audit.logger import audit_logger
from app.utils.exception_utils import CyberUnionException
from app.core.constants import ErrorCode
from app.config.settings import settings


def setup_exception_handlers(app: FastAPI):
    """注册全局异常处理器。"""

    @app.exception_handler(CyberUnionException)
    async def custom_exception_handler(request: Request, exc: CyberUnionException):
        audit_logger.error(f"业务异常: {exc.message}", exc_info=True)
        return JSONResponse(
            status_code=400,
            content={
                "code": getattr(exc.code, "value", 400),
                "message": exc.message,
                "details": exc.details
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        audit_logger.critical(f"未捕获异常: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "code": ErrorCode.INTERNAL_SERVER_ERROR.value,
                "message": "服务器内部错误",
                "details": str(exc) if settings.env == "development" else None
            }
        )