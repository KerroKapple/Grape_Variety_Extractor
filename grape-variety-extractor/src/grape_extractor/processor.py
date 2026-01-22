"""
信息处理流水线

负责调用LLM进行结构化解析、改写和翻译。
"""

import json
import logging
from pathlib import Path
from typing import TypedDict

from .llm_client import LLMClient
from .pdf_parser import PDFPage, extract_pdf_text
from .prompts import PARSE_PROMPT, REWRITE_PROMPT, TRANSLATE_PROMPT

logger = logging.getLogger(__name__)


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


class GrapeInfoProcessor:
    """
    葡萄信息处理器
    
    执行完整的4步处理流程：
    1. PDF文本提取
    2. LLM结构化解析
    3. LLM英文改写
    4. LLM中文翻译
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        初始化处理器
        
        Args:
            llm_client: LLM客户端实例
        """
        self.llm = llm_client
        logger.info(f"初始化GrapeInfoProcessor, 使用模型: {llm_client.model_name}")
    
    def process_page(self, page: PDFPage) -> VarietyResult:
        """
        处理单页PDF，执行完整的4步处理流程
        
        Args:
            page: PDF页面数据
            
        Returns:
            完整的处理结果
        """
        logger.info(f"开始处理: Page {page.page_number} - {page.variety_name}")
        
        steps: list[StepOutput] = []
        
        # Step 1: 原始文本（已提取）
        step1_output = page.text
        steps.append({"step": 1, "output": step1_output})
        logger.debug("Step 1 完成: 文本提取")
        
        # Step 2: 结构化解析
        step2_output = self._parse_info(page.text, page.variety_name)
        steps.append({"step": 2, "output": step2_output})
        logger.debug("Step 2 完成: 结构化解析")
        
        # Step 3: 英文改写
        step3_output = self._rewrite_english(page.variety_name, step2_output)
        steps.append({"step": 3, "output": step3_output})
        logger.debug("Step 3 完成: 英文改写")
        
        # Step 4: 中文翻译
        step4_output = self._translate_chinese(step3_output)
        steps.append({"step": 4, "output": step4_output})
        logger.debug("Step 4 完成: 中文翻译")
        
        logger.info(f"完成处理: {page.variety_name}")
        
        return {
            "page": page.page_number,
            "variety": page.variety_name,
            "steps": steps
        }
    
    def _parse_info(self, raw_text: str, variety_name: str) -> ParsedInfo:
        """
        Step 2: 使用LLM解析结构化信息
        
        Args:
            raw_text: 原始文本
            variety_name: 葡萄品种名称
            
        Returns:
            结构化的葡萄信息
        """
        prompt = PARSE_PROMPT.format(
            raw_text=raw_text,
            variety_name=variety_name
        )
        
        response = self.llm.generate(prompt)
        
        # 清理可能的markdown代码块标记
        response = self._clean_json_response(response)
        
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
            logger.debug(f"原始响应: {response[:500]}...")
            # 返回空结构，避免流程中断
            return ParsedInfo(region="", style="", growing="", other="")
    
    def _rewrite_english(self, variety_name: str, parsed: ParsedInfo) -> str:
        """
        Step 3: 使用LLM改写为易读的英文段落
        
        Args:
            variety_name: 葡萄品种名称
            parsed: 结构化信息
            
        Returns:
            改写后的英文段落
        """
        prompt = REWRITE_PROMPT.format(
            variety_name=variety_name,
            region=parsed["region"],
            style=parsed["style"],
            growing=parsed["growing"],
            other=parsed["other"]
        )
        
        return self.llm.generate(prompt)
    
    def _translate_chinese(self, english_text: str) -> str:
        """
        Step 4: 使用LLM翻译为中文
        
        Args:
            english_text: 英文段落
            
        Returns:
            中文翻译
        """
        prompt = TRANSLATE_PROMPT.format(english_text=english_text)
        return self.llm.generate(prompt)
    
    @staticmethod
    def _clean_json_response(response: str) -> str:
        """
        清理LLM返回的JSON响应
        
        移除可能的markdown代码块标记等。
        
        Args:
            response: 原始响应
            
        Returns:
            清理后的JSON字符串
        """
        response = response.strip()
        
        # 移除markdown代码块
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        return response.strip()


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
    
    if not pages:
        logger.warning("PDF中没有可处理的页面")
        return []
    
    # 处理每页
    processor = GrapeInfoProcessor(llm_client)
    results: list[VarietyResult] = []
    
    for page in pages:
        try:
            result = processor.process_page(page)
            results.append(result)
        except Exception as e:
            logger.error(f"处理第{page.page_number}页失败: {e}")
            # 继续处理其他页面
            continue
    
    # 保存结果
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"结果已保存至: {output_path}")
    
    return results
