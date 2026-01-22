#!/usr/bin/env python3
"""
葡萄品种信息提取器
从PDF中提取葡萄品种信息，使用LLM进行结构化解析、改写和翻译

考察要点：
1. 代码健壮性 - 完善的异常处理、类型提示、模块化设计
2. 提示词质量 - 精心设计的prompt，确保输出质量和一致性
"""

import json
import logging
from pathlib import Path
from typing import TypedDict, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

# PDF处理
import pdfplumber

# LLM调用 - 支持多种后端
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== 数据结构定义 ====================

class ParsedInfo(TypedDict):
    """结构化解析后的葡萄信息"""
    region: str
    style: str
    growing: str
    other: str


class StepOutput(TypedDict):
    """单个步骤的输出"""
    step: int
    output: str | ParsedInfo


class VarietyResult(TypedDict):
    """单个葡萄品种的完整结果"""
    page: int
    variety: str
    steps: list[StepOutput]


# ==================== Prompt模板 ====================

PARSE_PROMPT = """You are a wine expert assistant. Parse the following raw text extracted from a grape variety information sheet and extract structured information.

<raw_text>
{raw_text}
</raw_text>

<variety_name>
{variety_name}
</variety_name>

Extract and return a JSON object with exactly these four keys:
1. "region": All growing regions mentioned (keep original format with country codes)
2. "style": Wine style characteristics, flavor profiles for different climates
3. "growing": Combine vine characteristics (budding, ripening timing) AND all hazards/diseases
4. "other": Additional notes about versatility, soil preferences, yield characteristics

Important rules:
- Keep the original text content, just reorganize into categories
- Do NOT include section headers like "HAZARDS", "STYLE", "REGIONS", "OTHER" in the output values
- The "growing" field should include BOTH the timing characteristics AND the hazards
- Clean up any formatting artifacts but preserve the informational content

Return ONLY valid JSON, no markdown formatting or explanation."""


REWRITE_PROMPT = """You are a wine educator writing for beginners who know nothing about grape varieties.

Rewrite the following structured grape variety information into a single, flowing English paragraph that is:
- Educational and accessible to complete beginners
- Comprehensive but concise (around 200-250 words)
- Well-organized: start with introduction, then regions, growing characteristics, wine styles, and conclude with unique qualities
- Free of unexplained jargon (explain technical terms like MLF, millerandage if mentioned)

<variety_name>
{variety_name}
</variety_name>

<structured_info>
Region: {region}

Style: {style}

Growing: {growing}

Other: {other}
</structured_info>

Write a single cohesive paragraph. Do not use bullet points, headers, or lists. Return ONLY the paragraph text."""


TRANSLATE_PROMPT = """You are a professional wine translator specializing in Chinese wine literature.

Translate the following English paragraph about a grape variety into fluent, natural Chinese.

<english_text>
{english_text}
</english_text>

Translation guidelines:
- Use standard simplified Chinese
- Translate wine terminology accurately:
  - MLF (Malolactic Fermentation) → 苹果酸-乳酸发酵
  - millerandage → 小果症/大小粒
  - powdery mildew → 白粉病
  - grey rot / botrytis → 灰霉病
  - downy mildew → 霜霉病
  - Pierce's disease → 皮尔斯病
  - grapevine yellows → 葡萄黄化病
  - wet stones / minerality → 湿石头矿物质感
  - stone fruit → 核果
  - Chardonnay → 霞多丽
  - Pinot Gris/Grigio → 灰皮诺
- Keep region names in their commonly used Chinese translations
- Maintain the same paragraph structure and flow
- The translation should read naturally to Chinese wine enthusiasts

Return ONLY the Chinese translation, no explanation."""


# ==================== LLM抽象层 ====================

class LLMClient(ABC):
    """LLM客户端抽象基类"""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """生成文本响应"""
        pass


class OpenAIClient(LLMClient):
    """OpenAI API客户端"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: Optional[str] = None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
    
    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()


class AnthropicClient(LLMClient):
    """Anthropic Claude API客户端"""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def generate(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()


class MockLLMClient(LLMClient):
    """模拟LLM客户端，用于测试或无API场景"""
    
    def __init__(self):
        self._responses = {}
    
    def set_response(self, prompt_type: str, response: str):
        """预设响应"""
        self._responses[prompt_type] = response
    
    def generate(self, prompt: str) -> str:
        # 根据prompt内容判断类型并返回预设响应
        if "Parse the following raw text" in prompt:
            return self._responses.get("parse", "{}")
        elif "Rewrite the following structured" in prompt:
            return self._responses.get("rewrite", "")
        elif "Translate the following English" in prompt:
            return self._responses.get("translate", "")
        return ""


# ==================== PDF处理 ====================

@dataclass
class PDFPage:
    """PDF页面数据"""
    page_number: int
    text: str
    variety_name: str


def extract_pdf_text(pdf_path: str | Path) -> list[PDFPage]:
    """
    从PDF中提取每页的文本内容
    
    Args:
        pdf_path: PDF文件路径
        
    Returns:
        包含每页文本的PDFPage对象列表
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
    
    pages = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            
            # 从文本中提取葡萄品种名称（通常是大写的标题）
            variety_name = _extract_variety_name(text)
            
            pages.append(PDFPage(
                page_number=i + 1,
                text=text,
                variety_name=variety_name
            ))
            
            logger.info(f"提取第{i+1}页: {variety_name}")
    
    return pages


def _extract_variety_name(text: str) -> str:
    """从文本中提取葡萄品种名称"""
    # 常见葡萄品种名称
    known_varieties = [
        "Chardonnay", "Pinot Gris", "Pinot Grigio", "Pinot Noir",
        "Cabernet Sauvignon", "Merlot", "Sauvignon Blanc", "Riesling",
        "Syrah", "Shiraz", "Gewürztraminer", "Viognier"
    ]
    
    text_lower = text.lower()
    for variety in known_varieties:
        if variety.lower() in text_lower:
            # 特殊处理 Pinot Gris / Pinot Grigio
            if "pinot gris" in text_lower or "pinot grigio" in text_lower:
                return "Pinot Gris / Pinot Grigio"
            return variety
    
    # 如果没找到，尝试从文本开头提取
    lines = text.strip().split('\n')
    if lines:
        return lines[0].strip()
    
    return "Unknown"


# ==================== 信息处理流水线 ====================

class GrapeInfoProcessor:
    """葡萄信息处理器"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def process_page(self, page: PDFPage) -> VarietyResult:
        """
        处理单页PDF，执行完整的4步处理流程
        
        Args:
            page: PDF页面数据
            
        Returns:
            完整的处理结果
        """
        logger.info(f"开始处理: {page.variety_name}")
        
        steps: list[StepOutput] = []
        
        # Step 1: 原始文本（已提取）
        step1_output = page.text
        steps.append({"step": 1, "output": step1_output})
        logger.info("Step 1 完成: 文本提取")
        
        # Step 2: 结构化解析
        step2_output = self._parse_info(page.text, page.variety_name)
        steps.append({"step": 2, "output": step2_output})
        logger.info("Step 2 完成: 结构化解析")
        
        # Step 3: 英文改写
        step3_output = self._rewrite_english(page.variety_name, step2_output)
        steps.append({"step": 3, "output": step3_output})
        logger.info("Step 3 完成: 英文改写")
        
        # Step 4: 中文翻译
        step4_output = self._translate_chinese(step3_output)
        steps.append({"step": 4, "output": step4_output})
        logger.info("Step 4 完成: 中文翻译")
        
        return {
            "page": page.page_number,
            "variety": page.variety_name,
            "steps": steps
        }
    
    def _parse_info(self, raw_text: str, variety_name: str) -> ParsedInfo:
        """Step 2: 使用LLM解析结构化信息"""
        prompt = PARSE_PROMPT.format(
            raw_text=raw_text,
            variety_name=variety_name
        )
        
        response = self.llm.generate(prompt)
        
        # 清理可能的markdown代码块标记
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[1]  # 移除第一行
        if response.endswith("```"):
            response = response.rsplit("\n", 1)[0]  # 移除最后一行
        response = response.strip()
        
        try:
            parsed = json.loads(response)
            return ParsedInfo(
                region=parsed.get("region", ""),
                style=parsed.get("style", ""),
                growing=parsed.get("growing", ""),
                other=parsed.get("other", "")
            )
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.debug(f"原始响应: {response}")
            # 返回空结构
            return ParsedInfo(region="", style="", growing="", other="")
    
    def _rewrite_english(self, variety_name: str, parsed: ParsedInfo) -> str:
        """Step 3: 使用LLM改写为易读的英文段落"""
        prompt = REWRITE_PROMPT.format(
            variety_name=variety_name,
            region=parsed["region"],
            style=parsed["style"],
            growing=parsed["growing"],
            other=parsed["other"]
        )
        
        return self.llm.generate(prompt)
    
    def _translate_chinese(self, english_text: str) -> str:
        """Step 4: 使用LLM翻译为中文"""
        prompt = TRANSLATE_PROMPT.format(english_text=english_text)
        return self.llm.generate(prompt)


# ==================== 主程序 ====================

def create_llm_client(
    provider: str = "openai",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None
) -> LLMClient:
    """
    创建LLM客户端
    
    Args:
        provider: 提供商 ("openai", "anthropic", "mock")
        api_key: API密钥
        model: 模型名称
        base_url: API基础URL（用于兼容OpenAI接口的其他服务）
    """
    if provider == "openai":
        if not HAS_OPENAI:
            raise ImportError("请安装openai: pip install openai")
        return OpenAIClient(
            api_key=api_key or "",
            model=model or "gpt-4o",
            base_url=base_url
        )
    elif provider == "anthropic":
        if not HAS_ANTHROPIC:
            raise ImportError("请安装anthropic: pip install anthropic")
        return AnthropicClient(
            api_key=api_key or "",
            model=model or "claude-sonnet-4-20250514"
        )
    elif provider == "mock":
        return MockLLMClient()
    else:
        raise ValueError(f"不支持的provider: {provider}")


def process_pdf(
    pdf_path: str | Path,
    output_path: str | Path,
    llm_client: LLMClient
) -> list[VarietyResult]:
    """
    处理PDF文件并生成输出JSON
    
    Args:
        pdf_path: 输入PDF路径
        output_path: 输出JSON路径
        llm_client: LLM客户端
        
    Returns:
        处理结果列表
    """
    # 提取PDF文本
    pages = extract_pdf_text(pdf_path)
    
    # 处理每页
    processor = GrapeInfoProcessor(llm_client)
    results = []
    
    for page in pages:
        result = processor.process_page(page)
        results.append(result)
    
    # 保存结果
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"结果已保存至: {output_path}")
    
    return results


# ==================== CLI入口 ====================

def main():
    """命令行入口"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(
        description="葡萄品种信息提取器 - 从PDF提取并处理葡萄品种信息"
    )
    parser.add_argument(
        "pdf_path",
        help="输入PDF文件路径"
    )
    parser.add_argument(
        "-o", "--output",
        default="output.json",
        help="输出JSON文件路径 (默认: output.json)"
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic", "mock"],
        default="openai",
        help="LLM提供商 (默认: openai)"
    )
    parser.add_argument(
        "--api-key",
        help="API密钥 (也可通过环境变量 OPENAI_API_KEY 或 ANTHROPIC_API_KEY 设置)"
    )
    parser.add_argument(
        "--model",
        help="模型名称"
    )
    parser.add_argument(
        "--base-url",
        help="API基础URL (用于兼容OpenAI接口的服务)"
    )
    
    args = parser.parse_args()
    
    # 获取API密钥
    api_key = args.api_key
    if not api_key:
        if args.provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
        elif args.provider == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    # 创建LLM客户端
    llm_client = create_llm_client(
        provider=args.provider,
        api_key=api_key,
        model=args.model,
        base_url=args.base_url
    )
    
    # 处理PDF
    process_pdf(args.pdf_path, args.output, llm_client)


if __name__ == "__main__":
    main()
