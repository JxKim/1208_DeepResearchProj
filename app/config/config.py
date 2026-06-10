from pydantic_settings import BaseSettings,SettingsConfigDict


class DeepResearchConfig(BaseSettings):
    """系统配置对象，负责从环境变量读取后端运行所需的基础配置。

    输入来自默认值、环境变量和项目根目录的 ``.env`` 文件；输出为业务模块可
    直接读取的类型化配置。该类只维护基础设施和模型参数，不保存任何业务状态。

    所有字段均可通过大写环境变量覆盖，例如 ``MONGODB_URI`` 对应
    ``mongodb_uri``。``.env`` 文件中的空值会被安全地解析为 ``None``。
    """

    app_name: str = "AI 研究报告工作台"
    app_version: str = "0.1.0"
    environment: str = "local"
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "deep_research"

    llm_provider: str = "openai"
    llm_model_name: str = "gpt-4.1-mini"
    openai_api_base: str | None = None
    openai_api_key: str | None = None
    deepseek_api_base: str | None = None
    deepseek_api_key: str | None = None
    enable_ragflow:bool = False
    ragflow_base_url: str | None = None
    ragflow_api_key: str | None = None
    tavily_api_key: str | None = None

    report_storage_backend: str = "local"
    report_storage_local_dir: str = "reports"

    # 定义SettingsCOnfigDict，从而使得项目启动时，可以读取.env当中的环境变量，然后赋给我们的配置，例如.env当中有OPENAI_API_BASE - > openai_api_base
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

_settings = None

def get_setting() -> DeepResearchConfig:

    global _settings
    if _settings is not None:
        return _settings
    else:
        _settings = DeepResearchConfig()
        return _settings

