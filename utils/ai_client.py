"""
DeepSeek API client for novel generation.
Uses OpenAI-compatible interface.
"""
import json
import re
from openai import OpenAI


class NovelAI:
    """AI client for generating novel outlines and chapters via DeepSeek API."""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        self.model = "deepseek-chat"

    def _call(self, system_prompt: str, user_prompt: str, temperature: float = 0.8,
              max_tokens: int = 4096) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def generate_outline(self, config: dict) -> dict:
        """Generate a chapter outline based on novel configuration."""
        system_prompt = """\
你是一位资深的网络小说作家和编辑。根据用户提供的小说设定，你需要生成一份详细的章节大纲。

要求：
1. 每个章节包含：章节序号(number)、章节标题(title)、简短内容概要(summary，1-2句话)
2. 章节数量要与用户指定的篇幅相匹配
3. 整体结构要有起承转合，高潮部分安排在合适的位置
4. 大纲要体现用户指定的风格和基调
5. 同时为小说起一个吸引人的标题(title)，并提供一段100字以内的小说简介(synopsis)

请严格以JSON格式输出，不要输出任何额外文本：
{
  "title": "小说标题",
  "synopsis": "小说整体简介",
  "chapters": [
    {"number": 1, "title": "章节标题", "summary": "章节内容概要"}
  ]
}"""

        categories = "、".join(config.get("categories", []))
        styles = "、".join(config.get("styles", []))
        user_prompt = f"""\
请根据以下设定生成小说大纲：

【小说标题（用户自定义）】{config.get('novel_title', '未指定')}
【分类】{categories}
【主角】{config.get('protagonist', '未指定')}
【篇幅】{config.get('length', '未指定')}
【风格/基调】{styles}
【其他设定】{config.get('free_text', '无')}"""

        raw = self._call(system_prompt, user_prompt)
        return self._parse_json(raw)

    def generate_chapter(self, config: dict, outline: list, chapter_index: int,
                         previous_summary: str = "") -> str:
        """Generate a single chapter of the novel."""
        chapter = outline[chapter_index]
        total = len(outline)

        word_range = self._word_count_for_length(config.get("length", ""))

        system_prompt = f"""\
你是一位专业的网络小说作家。请根据以下设定和要求，撰写指定章节的内容。

写作要求：
- 严格按照指定的风格和基调进行创作
- 注重情节推进和人物塑造
- 对话自然流畅，描写生动细腻
- 保持与前文的连贯性
- 本章字数控制在{word_range}左右
- 直接输出章节正文，不需要标题和章节号"""

        categories = "、".join(config.get("categories", []))
        styles = "、".join(config.get("styles", []))
        note = chapter.get("note", "")
        note_section = f"\n【本章特别要求】{note}" if note else ""

        user_prompt = f"""\
【小说分类】{categories}
【风格基调】{styles}
【主角设定】{config.get('protagonist', '')}

【前文概要】{previous_summary if previous_summary else '（这是第一章，无前文）'}

【本章信息】
第{chapter['number']}章 / 共{total}章
章节标题：{chapter['title']}
内容概要：{chapter['summary']}{note_section}

请开始撰写本章正文："""

        return self._call(system_prompt, user_prompt, temperature=0.85, max_tokens=8192)

    def generate_full_novel(self, config: dict, outline: list = None) -> str:
        """Generate the complete novel in one go."""
        categories = "、".join(config.get("categories", []))
        styles = "、".join(config.get("styles", []))
        word_range = self._word_count_for_length(config.get("length", ""))

        system_prompt = f"""\
你是一位专业的网络小说作家。请根据用户设定，创作一部完整的网络小说。

要求：
- 总字数控制在{word_range}左右
- 结构完整，有明确的开头、发展、高潮和结局
- 风格和基调严格遵照用户设定
- 用"第X章 章节标题"作为每章的分隔标记"""

        user_prompt = f"""\
【小说标题】{config.get('novel_title', '未命名')}
【分类】{categories}
【主角设定】{config.get('protagonist', '')}
【风格基调】{styles}
【篇幅要求】{config.get('length', '')}
【额外设定】{config.get('free_text', '')}

请开始创作："""

        return self._call(system_prompt, user_prompt, temperature=0.85, max_tokens=16384)

    def continue_chapter(self, config: dict, existing_text: str,
                         direction: str) -> str:
        """Interactive continuation: continue writing based on user direction."""
        categories = "、".join(config.get("categories", []))
        styles = "、".join(config.get("styles", []))

        system_prompt = """\
你是一位网络小说作家。请根据前文内容和用户的续写方向，继续创作后续内容。
保持与前文一致的风格、人设和世界观。直接输出续写内容，不需要额外说明。"""

        user_prompt = f"""\
【小说分类】{categories}
【风格基调】{styles}

【前文内容】
{existing_text[-2000:]}

【续写方向】
{direction}

请续写："""

        return self._call(system_prompt, user_prompt, temperature=0.85, max_tokens=4096)

    def _parse_json(self, raw: str) -> dict:
        """Extract JSON from AI response, handling markdown code blocks."""
        raw = raw.strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            raw = match.group()
        return json.loads(raw)

    @staticmethod
    def _word_count_for_length(length: str) -> str:
        mapping = {
            "短篇（1-3万字）": "2000字",
            "中篇（5-10万字）": "3000字",
            "长篇（20-50万字）": "4000字",
            "超长篇（100万字以上）": "5000字",
        }
        for key, val in mapping.items():
            if key in length:
                return val
        return "3000字"
