# Prompt Engineer 面试题

## 📁 提交内容

```
kerro_prompt_engineer/
├── README.md              # 本说明文件
├── answer.py              # 核心代码（单文件版本）
├── output.json            # 处理结果（包含2页葡萄品种信息）
└── grape-variety-extractor/   # 完整项目（可发布GitHub版本）
    ├── README.md
    ├── src/grape_extractor/
    ├── tests/
    └── ...
```

## 🎯 完成情况

### 处理的葡萄品种

| 页码 | 品种 | 处理状态 |
|------|------|----------|
| 1 | Chardonnay  | ✅ 完成 |
| 2 | Pinot Gris / Pinot Grigio  | ✅ 完成 |

### 四步处理流程

1. **Step 1**: PDF文本提取 - 使用 `pdfplumber` 提取原始文本
2. **Step 2**: 结构化解析 - LLM解析为 region/style/growing/other 四个字段
3. **Step 3**: 英文改写 - LLM改写为适合入门者阅读的段落
4. **Step 4**: 中文翻译 - LLM翻译，准确处理专业术语

## 💡 设计亮点

### 代码健壮性

- **类型提示**: 使用 `TypedDict`、`dataclass` 等确保类型安全
- **异常处理**: 完善的 try-catch，防止单页失败影响整体处理
- **模块化设计**: PDF解析、LLM调用、处理流程分离，便于测试和维护
- **多后端支持**: 抽象LLM客户端，支持OpenAI、Anthropic、Mock等

### Prompt质量

- **结构化输出**: 明确指定JSON输出格式，使用XML标签包裹输入
- **术语对照表**: 内置葡萄酒专业术语中英对照（MLF→苹果酸-乳酸发酵等）
- **角色设定**: 为每个prompt设定专业角色（wine expert、wine educator、wine translator）
- **输出约束**: 明确要求字数范围、段落格式、禁止使用列表等

## 🚀 运行方式

```bash
# 安装依赖
pip install pdfplumber openai anthropic python-dotenv

# 运行（使用answer.py单文件版本）
python answer.py input.pdf -o output.json --provider openai --api-key YOUR_KEY

# 或使用完整项目
cd grape-variety-extractor
pip install -e .
grape-extractor input.pdf -o output.json
```

## 📧 联系方式

- 姓名: [kerro]
- 邮箱: [Kerro99920@gmail.com]
