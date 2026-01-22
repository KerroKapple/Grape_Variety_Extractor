#!/usr/bin/env python3
"""
葡萄品种信息提取器 - 主程序入口

从PDF中提取葡萄品种信息，使用LLM进行结构化解析、改写和翻译。
"""

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from .llm_client import create_llm_client
from .processor import process_pdf

# 加载环境变量
load_dotenv()

# 配置日志
def setup_logging(verbose: bool = False) -> None:
    """配置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def get_api_key(provider: str, api_key: str | None) -> str:
    """
    获取API密钥
    
    优先使用命令行参数，其次使用环境变量。
    
    Args:
        provider: LLM提供商
        api_key: 命令行传入的API密钥
        
    Returns:
        API密钥
    """
    if api_key:
        return api_key
    
    if provider == "openai":
        return os.environ.get("OPENAI_API_KEY", "")
    elif provider == "anthropic":
        return os.environ.get("ANTHROPIC_API_KEY", "")
    
    return ""


def main() -> int:
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="葡萄品种信息提取器 - 从PDF提取并处理葡萄品种信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s input.pdf -o output.json
  %(prog)s input.pdf --provider anthropic
  %(prog)s input.pdf --base-url https://api.deepseek.com/v1 --model deepseek-chat
        """
    )
    
    parser.add_argument(
        "pdf_path",
        type=Path,
        help="输入PDF文件路径"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("output.json"),
        help="输出JSON文件路径 (默认: output.json)"
    )
    
    parser.add_argument(
        "--provider",
        choices=["openai", "anthropic", "mock"],
        default=os.environ.get("LLM_PROVIDER", "openai"),
        help="LLM提供商 (默认: openai, 可通过 LLM_PROVIDER 环境变量设置)"
    )
    
    parser.add_argument(
        "--api-key",
        help="API密钥 (也可通过环境变量 OPENAI_API_KEY 或 ANTHROPIC_API_KEY 设置)"
    )
    
    parser.add_argument(
        "--model",
        default=os.environ.get("LLM_MODEL"),
        help="模型名称 (可通过 LLM_MODEL 环境变量设置)"
    )
    
    parser.add_argument(
        "--base-url",
        default=os.environ.get("OPENAI_BASE_URL"),
        help="API基础URL (用于兼容OpenAI接口的服务, 可通过 OPENAI_BASE_URL 环境变量设置)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细日志"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    # 配置日志
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # 检查输入文件
    if not args.pdf_path.exists():
        logger.error(f"输入文件不存在: {args.pdf_path}")
        return 1
    
    # 获取API密钥
    api_key = get_api_key(args.provider, args.api_key)
    
    if args.provider != "mock" and not api_key:
        logger.error(f"未提供API密钥。请通过 --api-key 参数或环境变量设置。")
        return 1
    
    try:
        # 创建LLM客户端
        llm_client = create_llm_client(
            provider=args.provider,
            api_key=api_key,
            model=args.model,
            base_url=args.base_url
        )
        
        logger.info(f"使用 {args.provider} 提供商, 模型: {llm_client.model_name}")
        
        # 处理PDF
        results = process_pdf(
            pdf_path=args.pdf_path,
            output_path=args.output,
            llm_client=llm_client
        )
        
        logger.info(f"成功处理 {len(results)} 个葡萄品种")
        
        # 打印摘要
        print("\n处理完成！")
        print(f"输出文件: {args.output}")
        print(f"\n处理的品种:")
        for result in results:
            print(f"  - Page {result['page']}: {result['variety']}")
        
        return 0
        
    except Exception as e:
        logger.exception(f"处理失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
