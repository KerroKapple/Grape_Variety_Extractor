"""PDF解析器测试"""

import pytest
from grape_extractor.pdf_parser import extract_variety_name, KNOWN_VARIETIES


class TestExtractVarietyName:
    """测试葡萄品种名称提取"""
    
    def test_extract_chardonnay(self):
        """测试提取Chardonnay"""
        text = "CHARDONNAY\nEARLY BUDDING\nEARLY RIPENING"
        assert extract_variety_name(text) == "Chardonnay"
    
    def test_extract_pinot_gris_grigio(self):
        """测试提取Pinot Gris / Pinot Grigio"""
        text = "pinot gris /\npinot grigio\nEARLY BUDDING"
        assert extract_variety_name(text) == "Pinot Gris / Pinot Grigio"
    
    def test_extract_pinot_gris_only(self):
        """测试仅提取Pinot Gris"""
        text = "PINOT GRIS\nAlsace style"
        assert extract_variety_name(text) == "Pinot Gris"
    
    def test_extract_unknown(self):
        """测试未知品种"""
        text = "Some Unknown Grape\nWith description"
        result = extract_variety_name(text)
        # 应该返回第一行或 "Unknown"
        assert result in ["Some Unknown Grape", "Unknown"]
    
    def test_case_insensitive(self):
        """测试大小写不敏感"""
        text = "chardonnay is a grape variety"
        assert extract_variety_name(text) == "Chardonnay"
    
    def test_known_varieties_list(self):
        """测试已知品种列表"""
        assert "Chardonnay" in KNOWN_VARIETIES
        assert "Pinot Gris" in KNOWN_VARIETIES
        assert "Cabernet Sauvignon" in KNOWN_VARIETIES


class TestPDFExtraction:
    """PDF提取测试（需要实际PDF文件）"""
    
    @pytest.mark.skip(reason="需要实际PDF文件")
    def test_extract_pdf_text(self):
        """测试PDF文本提取"""
        pass
