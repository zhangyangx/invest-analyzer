#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock search script by keyword.
Supports Sina and Tencent suggestion APIs.
Output: JSON
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _utils import USER_AGENT, normalize_symbol


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
    try:
        return data.decode("gbk").strip()
    except Exception:
        return data.decode("utf-8", errors="ignore").strip()


def extract_quoted_value(raw: str) -> str:
    if not raw:
        return ""
    start = raw.find('"')
    end = raw.rfind('"')
    if start == -1 or end <= start:
        return ""
    return raw[start + 1:end]


def parse_record_fields(fields):
    symbol = ""
    code = ""
    name = ""
    item_type = fields[0] if fields else ""

    for field in fields:
        if re.fullmatch(r"(sh|sz)\d{6}", field.lower()):
            symbol = field.lower()
            break

    for field in fields:
        if re.fullmatch(r"\d{6}", field):
            code = field
            break

    for field in fields:
        if field and not re.search(r"\d", field) and len(field) >= 2:
            name = field
            break

    if not code and symbol:
        code = symbol[2:]
    if not symbol and code:
        symbol = normalize_symbol(code)
    if not code or not name or not symbol:
        return None

    market = "SH" if symbol.startswith("sh") else "SZ"
    return {
        "name": name,
        "code": code,
        "symbol": symbol,
        "market": market,
        "type": item_type,
    }


def parse_records(payload: str, record_sep: str, field_sep: str, limit: int) -> list:
    if not payload:
        return []
    records = [rec.strip() for rec in payload.split(record_sep) if rec.strip()]
    items = []
    for record in records:
        fields = [f.strip() for f in record.split(field_sep) if f.strip()]
        if not fields:
            continue

        item = parse_record_fields(fields)
        if not item:
            continue

        items.append(item)
        if len(items) >= limit:
            break

    return items


def parse_sina(raw: str, limit: int) -> list:
    payload = extract_quoted_value(raw)
    return parse_records(payload, record_sep=";", field_sep=",", limit=limit)


def parse_tencent(raw: str, limit: int) -> list:
    payload = extract_quoted_value(raw)
    return parse_records(payload, record_sep="^", field_sep="~", limit=limit)


def search_sina(keyword: str, limit: int) -> list:
    query = urllib.parse.quote(keyword)
    url = f"https://suggest3.sinajs.cn/suggest/key={query}"
    raw = fetch_text(url)
    return parse_sina(raw, limit)


def search_tencent(keyword: str, limit: int) -> list:
    query = urllib.parse.quote(keyword)
    url = f"https://smartbox.gtimg.cn/s3/?v=2&t=all&c=1&q={query}"
    raw = fetch_text(url)
    return parse_tencent(raw, limit)


def main():
    parser = argparse.ArgumentParser(description="Search stock by keyword.")
    parser.add_argument("keyword", nargs="?", default="", help="Keyword (stock name or code)")
    parser.add_argument(
        "--source",
        choices=["auto", "sina", "tencent"],
        default="auto",
        help="Search source (default: auto)",
    )
    parser.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")
    args = parser.parse_args()

    keyword = (args.keyword or "").strip()
    if not keyword:
        print("Usage: python3 stock_search.py <keyword> [--source auto|sina|tencent] [--limit N]")
        print("Example: python3 stock_search.py 贵州茅台")
        sys.exit(1)

    limit = max(1, min(args.limit, 50))

    try:
        items = []
        source = args.source
        if args.source in ("auto", "sina"):
            items = search_sina(keyword, limit)
            if items:
                source = "sina"
        if not items and args.source in ("auto", "tencent"):
            items = search_tencent(keyword, limit)
            if items:
                source = "tencent"

        result = {
            "keyword": keyword,
            "source": source,
            "count": len(items),
            "items": items,
        }
        print(json.dumps(result, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": "request_failed", "detail": str(exc)}, ensure_ascii=False))
        sys.exit(4)


if __name__ == "__main__":
    main()
