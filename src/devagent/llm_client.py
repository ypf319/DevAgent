import requests
# 从tenacity导入重试相关的装饰器和配置
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import List, Dict, Any
from .config import close_settings as settings
from .exceptions import LLMRequestError
from .tools.tool_registry import TOOLS_DEFINITION


class LLMClient:
    def __init__(self):
        self.llm_base_url = settings.llm_base_url
        self.llm_api_key = settings.llm_api_key
        self.llm_model = settings.llm_model
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization':f"Bearer {self.llm_api_key}"
        }
    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=1, max=10),
           retry=retry_if_exception_type(LLMRequestError)
           )
    def chat(self,message: List[Dict[str, Any]],tools: List[Dict[str, Any]]) -> dict:


        payload = {
            'messages': message,
            "model": self.llm_model,
        }

        if tools is not None:
            payload["tools"] = tools

        try:
            response = requests.post(url=self.llm_base_url,
                                 headers=self.headers,
                                 json=payload,
                                 timeout=60
                                 )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise LLMRequestError(f"调用大模型失败：{str(e)}")


llm_client = LLMClient()
