from pydantic_settings import BaseSettings, SettingsConfigDict

# 定义配置类，自动从 .env 文件读取对应变量
class SiliconFlowSettings(BaseSettings):
    # 告诉配置类去读根目录的 .env 文件，编码用 utf-8
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="SF_", extra='ignore')

    # 下面三个变量名必须和 .env 文件里的名字完全一致
    llm_base_url: str
    llm_api_key: str
    llm_model: str

# 创建一个全局的配置实例，后面所有文件直接导入这个对象用
sf_settings = SiliconFlowSettings()

class CloseAISettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="CLOSE_", extra='ignore')

    llm_base_url: str
    llm_api_key: str
    llm_model: str

close_settings = CloseAISettings()
