#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock real-time quote script (Tencent quote API).
Input: stock code only (e.g., 600519 or sh600519 or sz000001)
Output: JSON
"""

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _utils import USER_AGENT, normalize_symbol, safe_float, safe_int


def fetch_quote(symbol: str) -> str:
    url = f"https://qt.gtimg.cn/q={symbol}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
    try:
        return data.decode("gbk").strip()
    except Exception:
        return data.decode("utf-8", errors="ignore").strip()


def parse_quote(raw: str, symbol: str) -> dict:
    if not raw or f"v_{symbol}=" not in raw:
        return {}

    clean = raw.replace(f'v_{symbol}="', "").replace('";', "").replace('"', "").replace("\n", "")
    parts = clean.split("~")
    if len(parts) < 10:
        return {}

    name = parts[1] if len(parts) > 1 else ""
    code = parts[2] if len(parts) > 2 else symbol.replace("sh", "").replace("sz", "")

    current = safe_float(parts[3]) if len(parts) > 3 else 0.0
    prev_close = safe_float(parts[4]) if len(parts) > 4 else 0.0
    open_price = safe_float(parts[5]) if len(parts) > 5 else 0.0
    volume = safe_int(parts[6]) if len(parts) > 6 else 0
    amount = 0.0

    if len(parts) > 35 and "/" in parts[35]:
        # Prefer the precise amount from the bundled "price/volume/amount" field.
        ratio_parts = parts[35].split("/")
        if len(ratio_parts) >= 3:
            amount = safe_float(ratio_parts[2])
    if amount <= 0 and len(parts) > 37:
        # Fallback: index 37 is usually turnover amount in 10k CNY.
        amount = round(safe_float(parts[37]) * 10000, 2)

    high = safe_float(parts[33]) if len(parts) > 33 else 0.0
    low = safe_float(parts[34]) if len(parts) > 34 else 0.0

    pct_change = 0.0
    change = 0.0
    if prev_close > 0:
        change = current - prev_close
        pct_change = round(change / prev_close * 100, 2)

    data = {
        "name": name,
        "code": code,
        "symbol": symbol,
        "current": current,
        "prev_close": prev_close,
        "open": open_price,
        "high": high,
        "low": low,
        "volume": volume,
        "amount": amount,
        "change": round(change, 4),
        "pct_change": pct_change,
    }

    # Optional level-1 quotes (if present)
    for i in range(5):
        bi = 9 + i * 2
        si = 19 + i * 2
        if len(parts) > si + 1:
            data[f"buy{i+1}_p"] = safe_float(parts[bi])
            data[f"buy{i+1}_v"] = safe_int(parts[bi + 1])
            data[f"sell{i+1}_p"] = safe_float(parts[si])
            data[f"sell{i+1}_v"] = safe_int(parts[si + 1])

    return data


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 stock_quote.py <stock_code>")
        print("Example: python3 stock_quote.py 600519")
        sys.exit(1)

    symbol = normalize_symbol(sys.argv[1])
    if not symbol:
        print(json.dumps({"error": "invalid_stock_code"}, ensure_ascii=False))
        sys.exit(2)

    try:
        raw = fetch_quote(symbol)
        data = parse_quote(raw, symbol)
        if not data:
            print(json.dumps({"error": "no_data"}, ensure_ascii=False))
            sys.exit(3)
        print(json.dumps(data, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": "request_failed", "detail": str(exc)}, ensure_ascii=False))
        sys.exit(4)


if __name__ == "__main__":
    main()
