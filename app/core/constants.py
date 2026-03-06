"""
全局常量与枚举定义模块。
包含任务状态、Agent类型、角色、审核结果、优先级、错误码等。
"""
from enum import Enum, unique
from typing import Final


# ==================== 项目基本信息 ====================
PROJECT_NAME: Final[str] = "赛博合众国AI协作架构"
VERSION: Final[str] = "1.0.0"
DEFAULT_TIMEOUT: Final[int] = 30
DEFAULT_RETRY: Final[int] = 3
LOG_FORMAT: Final[str] = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"


# ==================== 任务状态枚举 ====================
@unique
class TaskStatus(str, Enum):
    """任务全流程状态枚举，覆盖从创建到完成的全链路节点"""
    CREATED = "CREATED"
    PENDING_SORT = "PENDING_SORT"
    PENDING_LEGISLATION = "PENDING_LEGISLATION"
    PENDING_CONSTITUTIONAL_REVIEW = "PENDING_CONSTITUTIONAL_REVIEW"
    PENDING_PLANNING = "PENDING_PLANNING"
    PENDING_PLAN_APPROVAL = "PENDING_PLAN_APPROVAL"
    PENDING_PLAN_FINAL_REVIEW = "PENDING_PLAN_FINAL_REVIEW"
    PENDING_EXECUTION = "PENDING_EXECUTION"
    PENDING_FINAL_INSPECTION = "PENDING_FINAL_INSPECTION"
    PENDING_FINAL_REVIEW = "PENDING_FINAL_REVIEW"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"
    TERMINATED = "TERMINATED"


# ==================== Agent角色类型枚举 ====================
@unique
class AgentType(str, Enum):
    EXECUTIVE = "EXECUTIVE"
    LEGISLATIVE = "LEGISLATIVE"
    JUDICIAL = "JUDICIAL"
    CABINET = "CABINET"


# ==================== Agent角色名称枚举 ====================
@unique
class AgentRole(str, Enum):
    PRESIDENT = "PRESIDENT"
    WHITE_HOUSE_OFFICE = "WHITE_HOUSE_OFFICE"
    OPM = "OPM"
    OMB = "OMB"
    CONGRESS = "CONGRESS"
    SUPREME_COURT = "SUPREME_COURT"
    TREASURY = "TREASURY"
    STATE_DEPARTMENT = "STATE_DEPARTMENT"
    JUSTICE_DEPARTMENT = "JUSTICE_DEPARTMENT"
    ENERGY_DEPARTMENT = "ENERGY_DEPARTMENT"
    DHS = "DHS"
    CIA_FBI = "CIA_FBI"
    REGULATORS = "REGULATORS"


# ==================== 审核结果枚举 ====================
@unique
class ReviewResult(str, Enum):
    PASSED = "PASSED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"


# ==================== 任务优先级枚举 ====================
@unique
class TaskPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


# ==================== 错误码枚举 ====================
@unique
class ErrorCode(str, Enum):
    # 参数错误 (4000-4099)
    PARAM_INVALID = "PARAM_INVALID"
    PARAM_MISSING = "PARAM_MISSING"
    # 权限错误 (4100-4199)
    PERMISSION_DENIED = "PERMISSION_DENIED"
    UNAUTHORIZED = "UNAUTHORIZED"
    # 模型调用错误 (4200-4299)
    MODEL_TIMEOUT = "MODEL_TIMEOUT"
    MODEL_RATE_LIMIT = "MODEL_RATE_LIMIT"
    MODEL_INVALID_RESPONSE = "MODEL_INVALID_RESPONSE"
    MODEL_CALL_ERROR = "MODEL_CALL_ERROR"
    # 任务执行错误 (4300-4399)
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_STATE_INVALID = "TASK_STATE_INVALID"
    TASK_EXECUTION_FAILED = "TASK_EXECUTION_FAILED"
    # 插件错误 (4400-4499)
    PLUGIN_EXECUTION_ERROR = "PLUGIN_EXECUTION_ERROR"
    PLUGIN_LOAD_ERROR = "PLUGIN_LOAD_ERROR"
    # 系统错误 (5000-5099)
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    REDIS_ERROR = "REDIS_ERROR"
    # 其他
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


ERROR_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.PARAM_INVALID: "参数无效",
    ErrorCode.PARAM_MISSING: "缺少必要参数",
    ErrorCode.PERMISSION_DENIED: "权限不足",
    ErrorCode.UNAUTHORIZED: "未授权",
    ErrorCode.MODEL_TIMEOUT: "模型调用超时",
    ErrorCode.MODEL_RATE_LIMIT: "模型调用频率超限",
    ErrorCode.MODEL_INVALID_RESPONSE: "模型返回无效响应",
    ErrorCode.MODEL_CALL_ERROR: "模型调用失败",
    ErrorCode.TASK_NOT_FOUND: "任务不存在",
    ErrorCode.TASK_STATE_INVALID: "任务状态无效",
    ErrorCode.TASK_EXECUTION_FAILED: "任务执行失败",
    ErrorCode.PLUGIN_EXECUTION_ERROR: "插件执行异常",
    ErrorCode.PLUGIN_LOAD_ERROR: "插件加载失败",
    ErrorCode.INTERNAL_SERVER_ERROR: "内部服务器错误",
    ErrorCode.DATABASE_ERROR: "数据库错误",
    ErrorCode.REDIS_ERROR: "Redis错误",
    ErrorCode.UNKNOWN_ERROR: "未知错误",
}