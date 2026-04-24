from langchain_openai import ChatOpenAI

from .config import settings

def get_ds_llm_model():
    return ChatOpenAI(
        model=settings.ds_llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )
 