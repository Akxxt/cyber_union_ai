from fastapi.responses import JSONResponse
from typing import Any, Optional


def success_response(data: Any = None, message: str = "success") -> JSONResponse:
    """成功响应统一格式。"""
    return JSONResponse({"code": 200, "message": message, "data": data})


def error_response(code: int = 400, message: str = "error", data: Any = None) -> JSONResponse:
    """错误响应统一格式。"""
    return JSONResponse({"code": code, "message": message, "data": data})