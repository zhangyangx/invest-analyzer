#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keyword expander for news search.
No manual mapping required.

Input:
  --name <stock_name>
  [--topic <text>]          Chinese or mixed topic
  [--topic-en <text>]       English topic (AI-provided translation)
  [--extra "a,b,c"]         Extra keywords
Output: JSON {"keywords": [..]}
"""

import argparse
import json
import re


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, default="")
    parser.add_argument("--topic", type=str, default="")
    parser.add_argument("--topic-en", type=str, default="")
    parser.add_argument("--extra", type=str, default="")
    args = parser.parse_args()

    name = (args.name or "").strip()
    if not name:
        print(json.dumps({"error": "invalid_stock_name"}, ensure_ascii=False))
        return

    keywords = []

    base = name
    keywords.append(base)

    def split_terms(text: str):
        if not text:
            return []
        parts = re.split(r"[,\n;，；\s]+", text.strip())
        return [p for p in (s.strip() for s in parts) if p]

    # Topic-driven keywords (Chinese or mixed)
    topic = args.topic.strip()
    for t in split_terms(topic):
        keywords.append(t)
        keywords.append(f"{base} {t}")
        keywords.append(f"{base} 相关 {t}")

    # English topic terms (AI-provided translation)
    topic_en = args.topic_en.strip()
    for t in split_terms(topic_en):
        keywords.append(t)
        keywords.append(f"{base} {t}")
        keywords.append(f"{base} related {t}")

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
