"""
PDF解析模块

从PDF文件中提取文本内容和葡萄品种名称。
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pdfplumber

logger = logging.getLogger(__name__)


@dataclass
class PDFPage:
    """PDF页面数据"""
    page_number: int
    text: str
    variety_name: str


# 已知的葡萄品种名称列表
KNOWN_VARIETIES = [
    "Chardonnay",
    "Pinot Gris",
    "Pinot Grigio", 
    "Pinot Noir",
    "Cabernet Sauvignon",
    "Merlot",
    "Sauvignon Blanc",
    "Riesling",
    "Syrah",
    "Shiraz",
    "Gewürztraminer",
    "Viognier",
    "Chenin Blanc",
    "Sémillon",
    "Tempranillo",
    "Sangiovese",
    "Nebbiolo",
    "Grenache",
    "Mourvèdre",
    "Malbec",
    "Zinfandel",
    "Cabernet Franc",
]


def extract_variety_name(text: str) -> str:
    """
    从文本中提取葡萄品种名称
    
    Args:
        text: PDF页面文本
        
    Returns:
        识别出的葡萄品种名称
    """
    text_lower = text.lower()
    
    for variety in KNOWN_VARIETIES:
        if variety.lower() in text_lower:
            # 特殊处理 Pinot Gris / Pinot Grigio
            if "pinot gris" in text_lower and "pinot grigio" in text_lower:
                return "Pinot Gris / Pinot Grigio"
            if "pinot gris" in text_lower or "pinot grigio" in text_lower:
                # 检查是否两个名称都出现
                has_gris = "pinot gris" in text_lower
                has_grigio = "pinot grigio" in text_lower
                if has_gris and has_grigio:
                    return "Pinot Gris / Pinot Grigio"
                elif has_gris:
                    return "Pinot Gris"
                else:
                    return "Pinot Grigio"
            return variety
    
    # 如果没找到已知品种，尝试从文本开头提取
    lines = text.strip().split('\n')
    if lines:
        first_line = lines[0].strip()
        # 过滤掉太长的行（可能不是标题）
        if len(first_line) < 50:
            return first_line
    
    return "Unknown"


def extract_pdf_text(pdf_path: str | Path) -> list[PDFPage]:
    """
    从PDF中提取每页的文本内容
    
    Args:
        pdf_path: PDF文件路径
        
    Returns:
        包含每页文本的PDFPage对象列表
        
    Raises:
        FileNotFoundError: PDF文件不存在
        Exception: PDF解析错误
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
    
    if not pdf_path.suffix.lower() == '.pdf':
        logger.warning(f"文件可能不是PDF格式: {pdf_path}")
    
    pages: list[PDFPage] = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"开始解析PDF: {pdf_path}, 共{total_pages}页")
            
            for i, page in enumerate(pdf.pages):
                # 提取文本
                text = page.extract_text() or ""
                
                if not text.strip():
                    logger.warning(f"第{i+1}页文本为空")
                
                # 提取葡萄品种名称
                variety_name = extract_variety_name(text)
                
                page_data = PDFPage(
                    page_number=i + 1,
                    text=text,
                    variety_name=variety_name
                )
                pages.append(page_data)
                
                logger.info(f"提取第{i+1}/{total_pages}页: {variety_name}")
    
    except Exception as e:
        logger.error(f"PDF解析失败: {e}")
        raise
    
    return pages


def extract_single_page(pdf_path: str | Path, page_number: int) -> Optional[PDFPage]:
    """
    提取PDF中指定页面的文本
    
    Args:
        pdf_path: PDF文件路径
        page_number: 页码（从1开始）
        
    Returns:
        PDFPage对象，如果页码无效则返回None
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_number < 1 or page_number > len(pdf.pages):
                logger.error(f"无效的页码: {page_number}, PDF共{len(pdf.pages)}页")
                return None
            
            page = pdf.pages[page_number - 1]
            text = page.extract_text() or ""
            variety_name = extract_variety_name(text)
            
            return PDFPage(
                page_number=page_number,
                text=text,
                variety_name=variety_name
            )
    
    except Exception as e:
        logger.error(f"提取第{page_number}页失败: {e}")
        raise
