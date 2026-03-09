#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stock K-line script (Sina K-line API).
Input: stock code only (e.g., 600519 or sh600519 or sz000001)
Optional: scale (default 240), count (default 120)
Output: JSON
"""

import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _utils import USER_AGENT, normalize_symbol


def fetch_kline(symbol: str, scale: int, count: int) -> str:
    url = (
        "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
        f"CN_MarketData.getKLineData?symbol={symbol}&scale={scale}&ma=no&datalen={count}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
    return data.decode("utf-8", errors="ignore").strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 stock_kline.py <stock_code> [scale] [count]")
        print("Example: python3 stock_kline.py 600519 240 120")
        sys.exit(1)

    symbol = normalize_symbol(sys.argv[1])
    if not symbol:
        print(json.dumps({"error": "invalid_stock_code"}, ensure_ascii=False))
        sys.exit(2)

    scale = 240
    count = 120
    if len(sys.argv) > 2:
        try:
            scale = int(sys.argv[2])
        except Exception:
            print(json.dumps({"error": "invalid_scale"}, ensure_ascii=False))
            sys.exit(3)
        if scale <= 0:
            print(json.dumps({"error": "invalid_scale"}, ensure_ascii=False))
            sys.exit(3)
    if len(sys.argv) > 3:
        try:
            count = int(sys.argv[3])
        except Exception:
            print(json.dumps({"error": "invalid_count"}, ensure_ascii=False))
            sys.exit(4)
        if count <= 0:
            print(json.dumps({"error": "invalid_count"}, ensure_ascii=False))
            sys.exit(4)

    try:
        raw = fetch_kline(symbol, scale, count)
        if not raw:
            print(json.dumps({"error": "no_data"}, ensure_ascii=False))
            sys.exit(5)
        payload = json.loads(raw)
        if not isinstance(payload, list):
            print(json.dumps({"error": "unexpected_payload"}, ensure_ascii=False))
            sys.exit(6)
        print(json.dumps({
            "symbol": symbol,
            "scale": scale,
            "count": len(payload),
            "klines": payload,
        }, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": "request_failed", "detail": str(exc)}, ensure_ascii=False))
        sys.exit(7)


if __name__ == "__main__":
    main()
