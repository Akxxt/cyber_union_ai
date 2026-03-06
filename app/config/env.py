"""
环境变量加载与管理模块。
支持开发/测试/生产环境切换，可读取系统环境变量与.env文件。
"""
import os
from typing import Optional
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class EnvSettings(BaseSettings):
    """
    环境变量配置类，自动从环境变量或.env文件加载。
    """
    # 环境标识
    ENV: str = Field("development", description="运行环境: development/testing/production")
    
    # 服务基础配置
    SERVICE_NAME: str = Field("cyber-union-ai", description="服务名称")
    VERSION: str = Field("1.0.0", description="API版本")
    HOST: str = Field("0.0.0.0", description="监听主机")
    PORT: int = Field(8000, description="监听端口")
    
    # 跨域配置
    CORS_ORIGINS: list[str] = Field(["*"], description="允许的跨域源")
    
    # 大模型配置
    OPENAI_API_KEY: Optional[str] = Field(None, description="OpenAI API密钥")
    OPENAI_BASE_URL: Optional[str] = Field(None, description="OpenAI基础地址")
    DEFAULT_MODEL: str = Field("gpt-4", description="默认模型")
    MODEL_TIMEOUT: int = Field(60, description="模型调用超时时间(秒)")
    MODEL_MAX_RETRIES: int = Field(3, description="模型调用最大重试次数")
    
    # 数据库配置
    SQLITE_URL: str = Field("sqlite+aiosqlite:///./cyber_union.db", description="SQLite连接地址")
    REDIS_HOST: str = Field("localhost", description="Redis主机")
    REDIS_PORT: int = Field(6379, description="Redis端口")
    REDIS_PASSWORD: Optional[str] = Field(None, description="Redis密码")
    REDIS_DB: int = Field(0, description="Redis数据库编号")
    
    # 任务配置
    TASK_MAX_CONCURRENT: int = Field(10, description="任务最大并发数")
    TASK_MAX_EXECUTION_SECONDS: int = Field(300, description="单任务最大执行时长(秒)")
    DEFAULT_TOKEN_BUDGET: int = Field(100000, description="默认Token预算上限")
    SINGLE_STEP_MAX_RETRIES: int = Field(3, description="单环节最大重试次数")
    
    # 日志配置
    LOG_PATH: str = Field("./logs", description="日志存储路径")
    LOG_LEVEL: str = Field("INFO", description="日志级别")
    LOG_FILE_MAX_SIZE: str = Field("100 MB", description="日志文件最大大小")
    LOG_BACKUP_COUNT: int = Field(10, description="日志备份数量")
    
    # 安全配置
    COMPLIANCE_SWITCH: bool = Field(True, description="全局合规红线开关")
    SENSITIVE_DETECT_SWITCH: bool = Field(True, description="敏感内容检测开关")
    API_SECRET_KEY: Optional[str] = Field(None, description="API接口鉴权密钥")
    
    # 模型提供商配置（Step8新增）
    DEEPSEEK_API_KEY: Optional[str] = Field(None, description="DeepSeek API密钥")
    DEEPSEEK_BASE_URL: Optional[str] = Field("https://api.deepseek.com/v1", description="DeepSeek基础地址")
    CLAUDE_API_KEY: Optional[str] = Field(None, description="Claude API密钥")
    CLAUDE_BASE_URL: Optional[str] = Field("https://api.anthropic.com/v1", description="Claude基础地址")
    DOUBAO_API_KEY: Optional[str] = Field(None, description="豆包API密钥")
    DOUBAO_BASE_URL: Optional[str] = Field("https://ark.cn-beijing.volces.com/api/v3", description="豆包基础地址")
    
    # 角色专属模型映射（JSON字符串）
    ROLE_MODEL_MAPPING: dict = Field(default_factory=dict, description="角色模型映射")
    
    # 函数调用配置
    FUNCTION_CALLING_ENABLED: bool = Field(True, description="是否启用函数调用")
    FUNCTION_SANDBOX: bool = Field(True, description="是否启用沙箱隔离")
    
    # 插件配置（Step9新增）
    PLUGIN_DIR: str = Field("app/plugins/builtin", description="插件目录")
    PLUGIN_TIMEOUT: int = Field(30, description="插件执行超时秒数")
    MAX_CONCURRENT_PLUGINS: int = Field(10, description="插件最大并发数")
    HTTP_DOMAIN_WHITELIST: list[str] = Field(default_factory=list, description="HTTP插件允许的域名")
    FILE_PLUGIN_WORK_DIR: str = Field("./plugin_files", description="文件插件工作目录")
    ROLE_PERMISSION_LEVELS: dict = Field(default_factory=dict, description="角色权限等级映射")
    
    # 行政分支配置
    EXECUTIVE_CONFIG_PATH: str = Field("app/config/executive_config.json", description="行政配置文件路径")
    BUDGET_WARNING_THRESHOLD: float = Field(0.8, description="预算预警阈值")
    
    # 内阁配置
    CABINET_PARALLEL_MAX_WORKERS: int = Field(5, description="内阁并行执行最大工作数")
    CABINET_EXECUTION_TIMEOUT: int = Field(60, description="内阁单任务执行超时秒数")
    CABINET_RETRY_MAX_TIMES: int = Field(3, description="内阁任务最大重试次数")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


@lru_cache()
def get_env_settings() -> EnvSettings:
    return EnvSettings()


env_settings = get_env_settings()