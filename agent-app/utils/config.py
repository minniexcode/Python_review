from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ── LLM（OpenAI 兼容 / GPUStack）──────────────────────────────────────
    llm_base_url: str = "https://new-api.fletcher0516.online/v1"
    llm_api_key: str = "sk-MYNyhzr03f1AjF4QcFgrmKL1kJm930smNK98BB9ecDqkDaa3"
    # deepseek-v3.2
    ds_llm_model: str = "deepseek-v3.2"
    # qwen3-vl-plus
    vl_llm_name: str = "qwen3-vl-plus"
    # qwen3.6 plus
    qwen_llm_name: str = "qwen3.6-plus"


    app_api_key: str = "sk-MYNyhzr03f1AjF4QcFgrmKL1kJm930smNK98BB9ecDqkDaa3"

settings = Settings()