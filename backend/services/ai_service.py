"""AI 助手服务层。"""
from ai.deepseek_client import DeepSeekClient


class AIService:
    """AI 助手业务逻辑。"""

    def __init__(self):
        self.client = DeepSeekClient()

    async def chat(self, message: str, history: list = None) -> str:
        """AI 对话。"""
        return await self.client.chat(message, history)

    def chat_sync(self, message: str, history: list = None) -> str:
        """同步 AI 对话（用于测试）。"""
        return self.client.chat_sync(message, history)
