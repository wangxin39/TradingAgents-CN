import os
import json
from typing import Any, Dict, List, Optional, Union, Iterator, AsyncIterator, Sequence
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks.manager import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import Field, SecretStr

class ChatDeepSeek(BaseChatModel):
    """DeepSeek 大模型的 LangChain 适配器"""

    # 模型配置
    model: str = Field(default="deepseek-chat", description="DeepSeek 模型名称")
    api_key: Optional[SecretStr] = Field(default=None, description="DeepSeek API 密钥")
    temperature: float = Field(default=0.1, description="生成温度")
    max_tokens: int = Field(default=2000, description="最大生成token数")
    top_p: float = Field(default=0.9, description="核采样参数")

    _client: Any = None

    def __init__(self, **kwargs):
        """初始化 DeepSeek 客户端"""
        super().__init__(**kwargs)
        api_key = self.api_key
        if api_key is None:
            api_key = os.getenv("DEEPSEEK_API_KEY")
        if api_key is None:
            raise ValueError(
                "DeepSeek API key not found. Please set DEEPSEEK_API_KEY environment variable "
                "or pass api_key parameter."
            )
        # 假设 deepseek.api_key 用于设置全局密钥
        if isinstance(api_key, SecretStr):
            import deepseek
            deepseek.api_key = api_key.get_secret_value()
        else:
            import deepseek
            deepseek.api_key = api_key

    @property
    def _llm_type(self) -> str:
        return "deepseek"

    def _convert_messages_to_deepseek_format(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """将 LangChain 消息格式转换为 DeepSeek 格式"""
        deepseek_messages = []
        for message in messages:
            if isinstance(message, SystemMessage):
                role = "system"
            elif isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            else:
                role = "user"
            content = message.content
            if isinstance(content, list):
                text_content = ""
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_content += item.get("text", "")
                content = text_content
            deepseek_messages.append({
                "role": role,
                "content": str(content)
            })
        return deepseek_messages

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """生成聊天回复"""
        deepseek_messages = self._convert_messages_to_deepseek_format(messages)
        request_params = {
            "model": self.model,
            "messages": deepseek_messages,
            "result_format": "message",
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }
        if stop:
            request_params["stop"] = stop
        request_params.update(kwargs)
        try:
            import deepseek
            response = deepseek.Generation.call(**request_params)
            if response.status_code == 200:
                output = response.output
                message_content = output.choices[0].message.content
                ai_message = AIMessage(content=message_content)
                generation = ChatGeneration(message=ai_message)
                return ChatResult(generations=[generation])
            else:
                raise Exception(f"DeepSeek API error: {response.code} - {response.message}")
        except Exception as e:
            raise Exception(f"Error calling DeepSeek API: {str(e)}")

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        return self._generate(messages, stop, run_manager, **kwargs)

    def bind_tools(
        self,
        tools: Sequence[Union[Dict[str, Any], type, BaseTool]],
        **kwargs: Any,
    ) -> "ChatDeepSeek":
        formatted_tools = []
        for tool in tools:
            if hasattr(tool, "name") and hasattr(tool, "description"):
                formatted_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": getattr(tool, "args_schema", {})
                })
            elif isinstance(tool, dict):
                formatted_tools.append(tool)
            else:
                try:
                    formatted_tools.append(convert_to_openai_tool(tool))
                except Exception:
                    pass
        new_instance = self.__class__(
            model=self.model,
            api_key=self.api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            **kwargs
        )
        new_instance._tools = formatted_tools
        return new_instance

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }