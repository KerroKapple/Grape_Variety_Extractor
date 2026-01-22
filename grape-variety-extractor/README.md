# 🍇 Grape Variety Information Extractor

从葡萄品种PDF信息卡中自动提取、结构化解析、改写和翻译葡萄品种信息的工具。

## ✨ 功能特点

- **PDF文本提取**: 使用 `pdfplumber` 精准提取PDF中的文本内容
- **LLM结构化解析**: 将非结构化文本解析为产区、风格、种植特性等结构化字段
- **智能改写**: 将专业术语改写为适合入门者阅读的易懂段落
- **中文翻译**: 准确翻译葡萄酒专业术语（如MLF、millerandage等）
- **多LLM支持**: 支持 OpenAI、Anthropic Claude 等多种LLM后端

## 📁 项目结构

```
grape-variety-extractor/
├── README.md                 # 项目说明文档
├── requirements.txt          # Python依赖
├── setup.py                  # 包安装配置
├── .gitignore               # Git忽略文件
├── .env.example             # 环境变量示例
├── src/
│   └── grape_extractor/
│       ├── __init__.py
│       ├── main.py          # 主程序入口
│       ├── pdf_parser.py    # PDF解析模块
│       ├── llm_client.py    # LLM客户端抽象层
│       ├── processor.py     # 信息处理流水线
│       └── prompts.py       # Prompt模板
├── examples/
│   ├── sample_input.pdf     # 示例输入PDF
│   └── sample_output.json   # 示例输出JSON
├── tests/
│   ├── __init__.py
│   ├── test_pdf_parser.py
│   ├── test_processor.py
│   └── test_prompts.py
└── output/
    └── .gitkeep
```

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/grape-variety-extractor.git
cd grape-variety-extractor

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 或以开发模式安装
pip install -e .
```

### 配置

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的API密钥
```

### 使用

```bash
# 基本用法
python -m grape_extractor input.pdf -o output.json

# 指定LLM提供商
python -m grape_extractor input.pdf --provider anthropic

# 使用自定义模型
python -m grape_extractor input.pdf --provider openai --model gpt-4o

# 使用兼容OpenAI接口的其他服务
python -m grape_extractor input.pdf --base-url https://api.deepseek.com/v1 --model deepseek-chat
```

### Python API

```python
from grape_extractor import process_pdf, create_llm_client

# 创建LLM客户端
client = create_llm_client(
    provider="openai",
    api_key="your-api-key",
    model="gpt-4o"
)

# 处理PDF
results = process_pdf(
    pdf_path="input.pdf",
    output_path="output.json",
    llm_client=client
)

# 结果是一个列表，每个元素对应PDF的一页
for result in results:
    print(f"品种: {result['variety']}")
    print(f"中文介绍: {result['steps'][3]['output']}")
```

## 📊 输出格式

```json
[
  {
    "page": 1,
    "variety": "Chardonnay",
    "steps": [
      {
        "step": 1,
        "output": "原始提取文本..."
      },
      {
        "step": 2,
        "output": {
          "region": "产区信息...",
          "style": "风格特点...",
          "growing": "种植特性和风险...",
          "other": "其他信息..."
        }
      },
      {
        "step": 3,
        "output": "英文易读段落..."
      },
      {
        "step": 4,
        "output": "中文翻译段落..."
      }
    ]
  }
]
```

## 🔧 配置选项

| 参数 | 环境变量 | 说明 | 默认值 |
|------|----------|------|--------|
| `--provider` | `LLM_PROVIDER` | LLM提供商 | `openai` |
| `--api-key` | `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | API密钥 | - |
| `--model` | `LLM_MODEL` | 模型名称 | `gpt-4o` |
| `--base-url` | `OPENAI_BASE_URL` | API基础URL | - |
| `-o, --output` | - | 输出文件路径 | `output.json` |

## 🧪 运行测试

```bash
# 运行所有测试
pytest

# 运行带覆盖率的测试
pytest --cov=grape_extractor

# 运行特定测试
pytest tests/test_processor.py -v
```

## 📝 Prompt设计说明

本项目的核心在于精心设计的Prompt，确保LLM输出的质量和一致性：

1. **解析Prompt** (`PARSE_PROMPT`): 将非结构化文本解析为4个固定字段
2. **改写Prompt** (`REWRITE_PROMPT`): 面向入门者，解释专业术语
3. **翻译Prompt** (`TRANSLATE_PROMPT`): 内置葡萄酒术语对照表，确保翻译准确

详见 `src/grape_extractor/prompts.py`

## 🍷 支持的葡萄酒术语翻译

| 英文术语 | 中文翻译 |
|----------|----------|
| MLF (Malolactic Fermentation) | 苹果酸-乳酸发酵 |
| millerandage | 小果症/大小粒 |
| powdery mildew | 白粉病 |
| downy mildew | 霜霉病 |
| grey rot / botrytis | 灰霉病 |
| Pierce's disease | 皮尔斯病 |
| grapevine yellows | 葡萄黄化病 |
| wet stones / minerality | 湿石头矿物质感 |
| stone fruit | 核果 |

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF文本提取
- [OpenAI](https://openai.com/) / [Anthropic](https://anthropic.com/) - LLM API
