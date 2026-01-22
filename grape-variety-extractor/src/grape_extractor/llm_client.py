"""
LLM客户端抽象层

支持多种LLM后端，包括OpenAI、Anthropic等。
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)

# 检查可用的LLM库
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    logger.debug("openai库未安装")

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    logger.debug("anthropic库未安装")


class LLMClient(ABC):
    """LLM客户端抽象基类"""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        生成文本响应
        
        Args:
            prompt: 输入提示词
            
        Returns:
            生成的文本响应
        """
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """返回当前使用的模型名称"""
        pass


class OpenAIClient(LLMClient):
    """OpenAI API客户端"""
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "gpt-4o", 
        base_url: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048
    ):
        """
        初始化OpenAI客户端
        
        Args:
            api_key: API密钥
            model: 模型名称
            base_url: API基础URL（用于兼容服务）
            temperature: 生成温度
            max_tokens: 最大token数
        """
        if not HAS_OPENAI:
            raise ImportError("请安装openai库: pip install openai")
        
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        logger.info(f"初始化OpenAI客户端: model={model}, base_url={base_url or 'default'}")
    
    def generate(self, prompt: str) -> str:
        """生成文本响应"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            raise
    
    @property
    def model_name(self) -> str:
        return self.model


class AnthropicClient(LLMClient):
    """Anthropic Claude API客户端"""
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 2048
    ):
        """
        初始化Anthropic客户端
        
        Args:
            api_key: API密钥
            model: 模型名称
            max_tokens: 最大token数
        """
        if not HAS_ANTHROPIC:
            raise ImportError("请安装anthropic库: pip install anthropic")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        
        logger.info(f"初始化Anthropic客户端: model={model}")
    
    def generate(self, prompt: str) -> str:
        """生成文本响应"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic API调用失败: {e}")
            raise
    
    @property
    def model_name(self) -> str:
        return self.model


class MockLLMClient(LLMClient):
    """
    模拟LLM客户端
    
    用于测试或无API密钥场景。
    """
    
    def __init__(self):
        self._responses: dict[str, str] = {}
        logger.info("初始化Mock LLM客户端")
    
    def set_response(self, prompt_type: str, response: str) -> None:
        """
        预设响应
        
        Args:
            prompt_type: 提示类型 ("parse", "rewrite", "translate")
            response: 预设的响应内容
        """
        self._responses[prompt_type] = response
    
    def generate(self, prompt: str) -> str:
        """根据prompt内容判断类型并返回预设响应"""
        if "Parse the following raw text" in prompt:
            return self._responses.get("parse", '{"region":"","style":"","growing":"","other":""}')
        elif "Rewrite the following structured" in prompt:
            return self._responses.get("rewrite", "Mock rewritten text.")
        elif "Translate the following English" in prompt:
            return self._responses.get("translate", "模拟翻译文本。")
        return "Mock response"
    
    @property
    def model_name(self) -> str:
        return "mock"


def create_llm_client(
    provider: str = "openai",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> LLMClient:
    """
    创建LLM客户端的工厂函数
    
    Args:
        provider: 提供商名称 ("openai", "anthropic", "mock")
        api_key: API密钥
        model: 模型名称
        base_url: API基础URL（用于兼容OpenAI接口的其他服务）
        **kwargs: 其他参数传递给具体客户端
        
    Returns:
        LLMClient实例
        
    Raises:
        ValueError: 不支持的provider
        ImportError: 缺少必要的库
    """
    provider = provider.lower()
    
    if provider == "openai":
        return OpenAIClient(
            api_key=api_key or "",
            model=model or "gpt-4o",
            base_url=base_url,
            **kwargs
        )
    elif provider == "anthropic":
        return AnthropicClient(
            api_key=api_key or "",
            model=model or "claude-sonnet-4-20250514",
            **kwargs
        )
    elif provider == "mock":
        return MockLLMClient()
    else:
        raise ValueError(f"不支持的LLM provider: {provider}. 支持: openai, anthropic, mock")
