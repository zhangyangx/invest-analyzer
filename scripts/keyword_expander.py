#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keyword expander for news search.
No manual mapping required.

Input:
  --code <stock_code>
  [--topic <text>]          Chinese or mixed topic
  [--topic-en <text>]       English topic (AI-provided translation)
  [--extra "a,b,c"]         Extra keywords
Output: JSON {"keywords": [..]}
"""

import argparse
import json
import re


def normalize_code(code: str) -> str:
    code = (code or "").strip()
    if re.fullmatch(r"\d{6}", code):
        return code
    code = code.lower().replace("sh", "").replace("sz", "")
    if re.fullmatch(r"\d{6}", code):
        return code
    return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", type=str, default="")
    parser.add_argument("--topic", type=str, default="")
    parser.add_argument("--topic-en", type=str, default="")
    parser.add_argument("--extra", type=str, default="")
    args = parser.parse_args()

    code = normalize_code(args.code)
    if not code:
        print(json.dumps({"error": "invalid_stock_code"}, ensure_ascii=False))
        return

    keywords = []

    # Base keywords (no mapping, just code and generic finance context)
    keywords.append(code)
    keywords.append(f"{code} 股票")
    keywords.append(f"{code} 公司")

    def split_terms(text: str):
        if not text:
            return []
        parts = re.split(r"[,\n;，；\s]+", text.strip())
        return [p for p in (s.strip() for s in parts) if p]

    # Topic-driven keywords (Chinese or mixed)
    topic = args.topic.strip()
    for t in split_terms(topic):
        keywords.append(t)
        keywords.append(f"{code} {t}")
        keywords.append(f"{code} 相关 {t}")

    # English topic terms (AI-provided translation)
    topic_en = args.topic_en.strip()
    for t in split_terms(topic_en):
        keywords.append(t)
        keywords.append(f"{code} {t}")
        keywords.append(f"{code} related {t}")

    # Extra keywords (comma-separated)
    extra = split_terms(args.extra or "")
    keywords.extend(extra)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            unique.append(k)

    print(json.dumps({"keywords": unique}, ensure_ascii=False))


if __name__ == "__main__":
    main()
