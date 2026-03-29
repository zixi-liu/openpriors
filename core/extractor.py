"""
Prior Extractor

Takes raw input (URL content, PDF text, user notes) and extracts
actionable principles that can be practiced.
"""

from typing import Dict, Any

from core.llm import complete_json

EXTRACT_PROMPT = """You are an expert at turning knowledge into actionable practice.

The user has shared something they learned. Extract actionable "priors" — principles
they can integrate into their daily life through practice.

SOURCE:
---
{content}
---

For each prior, provide:
- name: Short name (2-5 words)
- principle: The core insight in one sentence
- practice: A concrete way to practice this (specific, doable in under 5 minutes)
- trigger: When/where in daily life this applies (e.g., "before a meeting", "when writing an email")
- source: Where this came from (book title, article, etc.)

Return JSON:
{{
  "title": "source title or topic",
  "summary": "2-3 sentence summary of the source material",
  "priors": [
    {{
      "name": "...",
      "principle": "...",
      "practice": "...",
      "trigger": "...",
      "source": "..."
    }}
  ]
}}

Extract 3-7 priors. Focus on the most actionable, life-changing insights.
Return ONLY valid JSON."""


async def extract_priors(content: str, source_hint: str = "") -> Dict[str, Any]:
    """Extract actionable priors from raw content."""
    prompt = EXTRACT_PROMPT.format(content=content[:15000])
    if source_hint:
        prompt += f"\n\nSource hint: {source_hint}"

    return await complete_json(prompt)


URL_EXTRACT_PROMPT = """You are extracting content from a URL for learning purposes.

URL: {url}

Instructions:
1. Access and read the content from this URL
2. Extract the main ideas, key insights, actionable advice, and memorable quotes
3. If you cannot access the URL, use your knowledge about the topic/author

Return JSON:
{{
  "accessible": true,
  "title": "title of the content",
  "content": "Full extracted text with key points, insights, and quotes. Be thorough."
}}

Return ONLY valid JSON."""


async def extract_from_url(url: str) -> Dict[str, Any]:
    """Extract content from a URL."""
    prompt = URL_EXTRACT_PROMPT.format(url=url)
    return await complete_json(prompt)
