"""处理器测试"""

import json
import pytest
from grape_extractor.llm_client import MockLLMClient
from grape_extractor.processor import GrapeInfoProcessor, ParsedInfo
from grape_extractor.pdf_parser import PDFPage


class TestGrapeInfoProcessor:
    """测试GrapeInfoProcessor"""
    
    @pytest.fixture
    def mock_client(self):
        """创建Mock LLM客户端"""
        client = MockLLMClient()
        
        # 设置预期响应
        client.set_response("parse", json.dumps({
            "region": "France: Burgundy",
            "style": "Full-bodied, oak aged",
            "growing": "Early budding, spring frost risk",
            "other": "Versatile variety"
        }))
        client.set_response("rewrite", "Chardonnay is a versatile white grape...")
        client.set_response("translate", "霞多丽是一种多才多艺的白葡萄品种...")
        
        return client
    
    @pytest.fixture
    def sample_page(self):
        """创建示例PDF页面"""
        return PDFPage(
            page_number=1,
            text="CHARDONNAY\nEARLY BUDDING\nFrance: Burgundy",
            variety_name="Chardonnay"
        )
    
    def test_process_page(self, mock_client, sample_page):
        """测试完整的页面处理流程"""
        processor = GrapeInfoProcessor(mock_client)
        result = processor.process_page(sample_page)
        
        assert result["page"] == 1
        assert result["variety"] == "Chardonnay"
        assert len(result["steps"]) == 4
        
        # Step 1: 原始文本
        assert result["steps"][0]["step"] == 1
        assert "CHARDONNAY" in result["steps"][0]["output"]
        
        # Step 2: 结构化解析
        assert result["steps"][1]["step"] == 2
        assert isinstance(result["steps"][1]["output"], dict)
        assert "region" in result["steps"][1]["output"]
        
        # Step 3: 英文改写
        assert result["steps"][2]["step"] == 3
        assert isinstance(result["steps"][2]["output"], str)
        
        # Step 4: 中文翻译
        assert result["steps"][3]["step"] == 4
        assert "霞多丽" in result["steps"][3]["output"]
    
    def test_clean_json_response(self):
        """测试JSON响应清理"""
        # 带markdown代码块
        response = '```json\n{"key": "value"}\n```'
        cleaned = GrapeInfoProcessor._clean_json_response(response)
        assert cleaned == '{"key": "value"}'
        
        # 不带代码块
        response = '{"key": "value"}'
        cleaned = GrapeInfoProcessor._clean_json_response(response)
        assert cleaned == '{"key": "value"}'


class TestParsedInfo:
    """测试ParsedInfo类型"""
    
    def test_parsed_info_creation(self):
        """测试创建ParsedInfo"""
        info: ParsedInfo = {
            "region": "France",
            "style": "Full-bodied",
            "growing": "Early ripening",
            "other": "Notes"
        }
        
        assert info["region"] == "France"
        assert info["style"] == "Full-bodied"
