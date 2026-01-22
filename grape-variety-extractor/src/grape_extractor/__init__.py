"""
Grape Variety Information Extractor

从葡萄品种PDF信息卡中自动提取、结构化解析、改写和翻译葡萄品种信息。
"""

__version__ = "1.0.0"

from .llm_client import create_llm_client, LLMClient, OpenAIClient, AnthropicClient
from .pdf_parser import extract_pdf_text, PDFPage
from .processor import GrapeInfoProcessor, process_pdf
from .prompts import PARSE_PROMPT, REWRITE_PROMPT, TRANSLATE_PROMPT

__all__ = [
    # Version
    "__version__",
    # LLM
    "create_llm_client",
    "LLMClient",
    "OpenAIClient", 
    "AnthropicClient",
    # PDF
    "extract_pdf_text",
    "PDFPage",
    # Processing
    "GrapeInfoProcessor",
    "process_pdf",
    # Prompts
    "PARSE_PROMPT",
    "REWRITE_PROMPT",
    "TRANSLATE_PROMPT",
]
