"""Prompt模板测试"""

import pytest
from grape_extractor.prompts import (
    PARSE_PROMPT,
    REWRITE_PROMPT,
    TRANSLATE_PROMPT,
    WINE_TERMINOLOGY,
    get_chinese_term,
)


class TestPromptTemplates:
    """测试Prompt模板"""
    
    def test_parse_prompt_format(self):
        """测试解析Prompt格式化"""
        formatted = PARSE_PROMPT.format(
            raw_text="Sample text",
            variety_name="Chardonnay"
        )
        
        assert "Sample text" in formatted
        assert "Chardonnay" in formatted
        assert "region" in formatted
        assert "style" in formatted
        assert "growing" in formatted
        assert "other" in formatted
    
    def test_rewrite_prompt_format(self):
        """测试改写Prompt格式化"""
        formatted = REWRITE_PROMPT.format(
            variety_name="Chardonnay",
            region="France: Burgundy",
            style="Full-bodied",
            growing="Early budding",
            other="Versatile"
        )
        
        assert "Chardonnay" in formatted
        assert "France: Burgundy" in formatted
        assert "beginners" in formatted.lower()
    
    def test_translate_prompt_format(self):
        """测试翻译Prompt格式化"""
        formatted = TRANSLATE_PROMPT.format(
            english_text="Chardonnay is a grape variety."
        )
        
        assert "Chardonnay is a grape variety." in formatted
        assert "Chinese" in formatted
        assert "MLF" in formatted  # 术语表应该包含在prompt中


class TestWineTerminology:
    """测试葡萄酒术语词典"""
    
    def test_terminology_dict(self):
        """测试术语词典内容"""
        assert "MLF" in WINE_TERMINOLOGY
        assert "Chardonnay" in WINE_TERMINOLOGY
        assert "millerandage" in WINE_TERMINOLOGY
    
    def test_get_chinese_term_found(self):
        """测试获取已知术语的中文翻译"""
        assert get_chinese_term("MLF") == "苹果酸-乳酸发酵"
        assert get_chinese_term("Chardonnay") == "霞多丽"
        assert get_chinese_term("millerandage") == "小果症"
    
    def test_get_chinese_term_not_found(self):
        """测试获取未知术语（返回原文）"""
        assert get_chinese_term("Unknown Term") == "Unknown Term"
    
    def test_disease_terms(self):
        """测试病害术语"""
        assert WINE_TERMINOLOGY["powdery mildew"] == "白粉病"
        assert WINE_TERMINOLOGY["downy mildew"] == "霜霉病"
        assert WINE_TERMINOLOGY["grey rot"] == "灰霉病"
    
    def test_region_terms(self):
        """测试产区术语"""
        assert WINE_TERMINOLOGY["Burgundy"] == "勃艮第"
        assert WINE_TERMINOLOGY["Bordeaux"] == "波尔多"
