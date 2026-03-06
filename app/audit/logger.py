"""
全链路日志系统模块。
基于loguru实现，支持任务ID、Agent角色等上下文绑定，分模块、分级别存储。
"""
import sys
from pathlib import Path
from typing import Optional
from functools import lru_cache

from loguru import logger
from app.config.settings import settings
from app.core.constants import LOG_FORMAT


class Logger:
    """
    日志管理器，封装loguru，提供统一的日志记录接口。
    """

    def __init__(self):
        self._logger = logger
        self._configured = False

    def configure(self):
        """配置日志处理器：控制台输出和文件输出。"""
        if self._configured:
            return

        # 移除默认的处理器
        self._logger.remove()

        # 控制台输出（根据环境设置级别）
        console_level = settings.log_level.upper()
        self._logger.add(
            sys.stdout,
            format=LOG_FORMAT,
            level=console_level,
            colorize=True,
            enqueue=True,  # 线程安全
        )

        # 文件输出 - 所有级别
        log_path = Path(settings.log_path)
        log_path.mkdir(parents=True, exist_ok=True)

        # 全量日志文件
        self._logger.add(
            log_path / "cyber_union_{time:YYYY-MM-DD}.log",
            format=LOG_FORMAT,
            level="DEBUG",
            rotation=settings.log_file_max_size,
            retention=settings.log_backup_count,
            compression="zip",
            enqueue=True,
            serialize=False,
        )

        # 错误日志单独文件
        self._logger.add(
            log_path / "error_{time:YYYY-MM-DD}.log",
            format=LOG_FORMAT,
            level="ERROR",
            rotation=settings.log_file_max_size,
            retention=settings.log_backup_count,
            compression="zip",
            enqueue=True,
        )

        self._configured = True

    def _bind_context(self, **kwargs):
        """
        绑定上下文到日志记录器。
        """
        context = {k: v for k, v in kwargs.items() if v is not None}
        if context:
            return self._logger.bind(**context)
        return self._logger

    def debug(self, msg: str, *args, **kwargs):
        task_id = kwargs.pop('task_id', None)
        agent_role = kwargs.pop('agent_role', None)
        module = kwargs.pop('module', None)
        logger_with_ctx = self._bind_context(
            task_id=task_id,
            agent_role=agent_role,
            module=module
        )
        logger_with_ctx.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        task_id = kwargs.pop('task_id', None)
        agent_role = kwargs.pop('agent_role', None)
        module = kwargs.pop('module', None)
        logger_with_ctx = self._bind_context(
            task_id=task_id,
            agent_role=agent_role,
            module=module
        )
        logger_with_ctx.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        task_id = kwargs.pop('task_id', None)
        agent_role = kwargs.pop('agent_role', None)
        module = kwargs.pop('module', None)
        logger_with_ctx = self._bind_context(
            task_id=task_id,
            agent_role=agent_role,
            module=module
        )
        logger_with_ctx.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        task_id = kwargs.pop('task_id', None)
        agent_role = kwargs.pop('agent_role', None)
        module = kwargs.pop('module', None)
        exc_info = kwargs.pop('exc_info', True)
        logger_with_ctx = self._bind_context(
            task_id=task_id,
            agent_role=agent_role,
            module=module
        )
        logger_with_ctx.error(msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        task_id = kwargs.pop('task_id', None)
        agent_role = kwargs.pop('agent_role', None)
        module = kwargs.pop('module', None)
        logger_with_ctx = self._bind_context(
            task_id=task_id,
            agent_role=agent_role,
            module=module
        )
        logger_with_ctx.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        task_id = kwargs.pop('task_id', None)
        agent_role = kwargs.pop('agent_role', None)
        module = kwargs.pop('module', None)
        logger_with_ctx = self._bind_context(
            task_id=task_id,
            agent_role=agent_role,
            module=module
        )
        logger_with_ctx.exception(msg, *args, **kwargs)

    def contextualize(self, **kwargs):
        """返回上下文管理器，用于with语句中临时绑定上下文。"""
        return self._logger.contextualize(**kwargs)


@lru_cache()
def get_logger() -> Logger:
    log = Logger()
    log.configure()
    return log


audit_logger = get_logger()