"""
Prompt模板模块

包含用于信息提取、改写和翻译的精心设计的Prompt模板。
"""

# ==================== 解析Prompt ====================

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


# ==================== 改写Prompt ====================

REWRITE_PROMPT = """You are a wine educator writing for beginners who know nothing about grape varieties.

Rewrite the following structured grape variety information into a single, flowing English paragraph that is:
- Educational and accessible to complete beginners
- Comprehensive but concise (around 200-300 words)
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


# ==================== 翻译Prompt ====================

TRANSLATE_PROMPT = """You are a professional wine translator specializing in Chinese wine literature.

Translate the following English paragraph about a grape variety into fluent, natural Chinese.

<english_text>
{english_text}
</english_text>

Translation guidelines:
- Use standard simplified Chinese
- Translate wine terminology accurately using these standard translations:
  * MLF (Malolactic Fermentation) → 苹果酸-乳酸发酵
  * millerandage → 小果症/大小粒
  * powdery mildew → 白粉病
  * downy mildew → 霜霉病
  * grey rot / botrytis → 灰霉病
  * Pierce's disease → 皮尔斯病
  * grapevine yellows → 葡萄黄化病
  * wet stones / minerality → 湿石头矿物质感
  * stone fruit → 核果
  * Chardonnay → 霞多丽
  * Pinot Gris/Grigio → 灰皮诺
  * Sauvignon Blanc → 长相思
  * Cabernet Sauvignon → 赤霞珠
  * Merlot → 美乐/梅洛
  * Pinot Noir → 黑皮诺
  * Riesling → 雷司令
  * Gewürztraminer → 琼瑶浆
- Keep region names in their commonly used Chinese translations
- Maintain the same paragraph structure and flow
- The translation should read naturally to Chinese wine enthusiasts

Return ONLY the Chinese translation, no explanation."""


# ==================== 葡萄酒术语词典 ====================

WINE_TERMINOLOGY = {
    # 酿造术语
    "MLF": "苹果酸-乳酸发酵",
    "Malolactic Fermentation": "苹果酸-乳酸发酵",
    "oak aging": "橡木桶陈酿",
    "barrel fermentation": "橡木桶发酵",
    
    # 病害
    "millerandage": "小果症",
    "powdery mildew": "白粉病",
    "downy mildew": "霜霉病",
    "grey rot": "灰霉病",
    "botrytis": "灰霉病",
    "botrytis bunch rot": "灰霉病",
    "Pierce's disease": "皮尔斯病",
    "grapevine yellows": "葡萄黄化病",
    
    # 风味描述
    "wet stones": "湿石头矿物质感",
    "minerality": "矿物质感",
    "stone fruit": "核果",
    "citrus": "柑橘类",
    "tropical fruit": "热带水果",
    
    # 葡萄品种
    "Chardonnay": "霞多丽",
    "Pinot Gris": "灰皮诺",
    "Pinot Grigio": "灰皮诺",
    "Sauvignon Blanc": "长相思",
    "Cabernet Sauvignon": "赤霞珠",
    "Merlot": "美乐",
    "Pinot Noir": "黑皮诺",
    "Riesling": "雷司令",
    "Gewürztraminer": "琼瑶浆",
    "Syrah": "西拉",
    "Shiraz": "设拉子",
    "Viognier": "维欧尼",
    
    # 产区
    "Burgundy": "勃艮第",
    "Bordeaux": "波尔多",
    "Champagne": "香槟",
    "Alsace": "阿尔萨斯",
    "Loire Valley": "卢瓦尔河谷",
    "Rhône Valley": "罗纳河谷",
    "Napa Valley": "纳帕谷",
}


def get_chinese_term(english_term: str) -> str:
    """
    获取英文葡萄酒术语的中文翻译
    
    Args:
        english_term: 英文术语
        
    Returns:
        中文翻译，如果没找到则返回原文
    """
    return WINE_TERMINOLOGY.get(english_term, english_term)
