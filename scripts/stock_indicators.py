#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Technical indicators calculator.
Input: JSON from stdin or --file <path>
Expected JSON: {"klines": [ {"open","high","low","close"} ... ] }
Output: JSON with latest indicator values.
"""

import json
import math
import sys


def safe_float(val):
    try:
        return float(val)
    except Exception:
        return 0.0


def load_input():
    if len(sys.argv) >= 3 and sys.argv[1] == "--file":
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            return json.load(f)
    # default: stdin
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    return json.loads(raw)


def calc_ma(closes, periods):
    out = {}
    for p in periods:
        if len(closes) >= p:
            out[f"MA{p}"] = round(sum(closes[-p:]) / p, 4)
        else:
            out[f"MA{p}"] = 0.0
    return out


def calc_macd(closes, short=12, long=26, signal=9):
    if len(closes) < long + signal:
        return {"DIF": 0.0, "DEA": 0.0, "MACD": 0.0}

    def ema(series, period):
        alpha = 2 / (period + 1)
        out = [series[0]]
        for price in series[1:]:
            out.append(alpha * price + (1 - alpha) * out[-1])
        return out

    ema_short = ema(closes, short)
    ema_long = ema(closes, long)
    dif = [ema_short[i] - ema_long[i] for i in range(len(ema_short))]
    dea = ema(dif, signal)
    macd = [(dif[i] - dea[i]) * 2 for i in range(len(dif))]

    return {
        "DIF": round(dif[-1], 4),
        "DEA": round(dea[-1], 4),
        "MACD": round(macd[-1], 4),
    }


def calc_kdj(highs, lows, closes, n=9, m1=3, m2=3):
    if len(closes) < n + 2:
        return {"K": 0.0, "D": 0.0, "J": 0.0}

    k_values = [50.0]
    d_values = [50.0]

    start = len(closes) - (n + 2)
    for i in range(start + n, len(closes)):
        window_high = max(highs[i - n + 1:i + 1])
        window_low = min(lows[i - n + 1:i + 1])
        close = closes[i]
        if window_high == window_low:
            rsv = 50.0
        else:
            rsv = (close - window_low) / (window_high - window_low) * 100
        k = (m1 - 1) / m1 * k_values[-1] + 1 / m1 * rsv
        d = (m2 - 1) / m2 * d_values[-1] + 1 / m2 * k
        k_values.append(k)
        d_values.append(d)

    k = k_values[-1]
    d = d_values[-1]
    j = 3 * k - 2 * d
    return {"K": round(k, 2), "D": round(d, 2), "J": round(j, 2)}


def calc_rsi(closes, periods=(6, 12, 24)):
    out = {}
    if len(closes) < 2:
        for p in periods:
            out[f"RSI{p}"] = 0.0
        return out

    gains = []
    losses = []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(abs(min(delta, 0.0)))

    for p in periods:
        if len(closes) < p + 1:
            out[f"RSI{p}"] = 0.0
            continue
        avg_gain = sum(gains[-p:]) / p
        avg_loss = sum(losses[-p:]) / p
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        out[f"RSI{p}"] = round(rsi, 2)
    return out


def calc_boll(closes, n=20, k=2):
    if len(closes) < n:
        return {"upper": 0.0, "middle": 0.0, "lower": 0.0}
    window = closes[-n:]
    mid = sum(window) / n
    var = sum((x - mid) ** 2 for x in window) / n
    std = math.sqrt(var)
    upper = mid + k * std
    lower = mid - k * std
    return {"upper": round(upper, 4), "middle": round(mid, 4), "lower": round(lower, 4)}


def main():
    try:
        payload = load_input()
    except Exception as exc:
        print(json.dumps({"error": "invalid_input", "detail": str(exc)}, ensure_ascii=False))
        sys.exit(2)

    klines = payload.get("klines") or []
    if not klines:
        print(json.dumps({"error": "no_klines"}, ensure_ascii=False))
        sys.exit(3)

    closes = [safe_float(k.get("close")) for k in klines]
    highs = [safe_float(k.get("high")) for k in klines]
    lows = [safe_float(k.get("low")) for k in klines]

    if not closes or not highs or not lows:
        print(json.dumps({"error": "invalid_klines"}, ensure_ascii=False))
        sys.exit(4)

    indicators = {
        "MA": calc_ma(closes, [5, 10, 20, 60, 120]),
        "MACD": calc_macd(closes),
        "KDJ": calc_kdj(highs, lows, closes),
        "RSI": calc_rsi(closes),
        "BOLL": calc_boll(closes),
    }

    print(json.dumps(indicators, ensure_ascii=False))


if __name__ == "__main__":
    main()
