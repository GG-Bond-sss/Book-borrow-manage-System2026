"""DeepSeek AI 客户端。"""
import httpx
from config import settings


class DeepSeekClient:
    """DeepSeek 大模型 API 客户端。"""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.model = settings.DEEPSEEK_MODEL

    async def chat(self, message: str, history: list = None) -> str:
        """调用 DeepSeek 对话接口。

        Args:
            message: 用户消息
            history: 对话历史

        Returns:
            AI 回复文本
        """
        if not self.api_key:
            return "AI 助手未配置 API Key，请联系管理员。"

        messages = [
            {
                "role": "system",
                "content": (
                    "你是一个图书借阅管理系统的智能助手，可以帮助用户："
                    "1. 推荐图书 2. 查询借阅规则 3. 解答使用问题。"
                    "请用简洁友好的中文回答。"
                ),
            }
        ]
        if history:
            for h in history:
                messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": message})

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except httpx.TimeoutException:
            return "请求超时，请稍后重试。"
        except httpx.HTTPStatusError as e:
            return f"AI 服务异常：HTTP {e.response.status_code}"
        except Exception as e:
            return f"AI 服务异常：{str(e)}"

    def chat_sync(self, message: str, history: list = None) -> str:
        """同步调用 DeepSeek 对话接口（用于测试）。"""
        if not self.api_key:
            return "AI 助手未配置 API Key，请联系管理员。"

        messages = [
            {
                "role": "system",
                "content": (
                    "你是一个图书借阅管理系统的智能助手，可以帮助用户："
                    "1. 推荐图书 2. 查询借阅规则 3. 解答使用问题。"
                    "请用简洁友好的中文回答。"
                ),
            }
        ]
        if history:
            for h in history:
                messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": message})

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"AI 服务异常：{str(e)}"
