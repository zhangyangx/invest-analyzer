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


def load_input():
    if len(sys.argv) >= 3 and sys.argv[1] == "--file":
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            return json.load(f)
    # default: stdin
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    return json.loads(raw)


def to_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def parse_klines(klines):
    closes = []
    highs = []
    lows = []
    volumes = []
    required_fields = ("open", "high", "low", "close")

    for item in klines:
        if not isinstance(item, dict):
            return None, None, None, None
        if any(field not in item for field in required_fields):
            return None, None, None, None

        close = to_float(item.get("close"))
        high = to_float(item.get("high"))
        low = to_float(item.get("low"))
        volume = to_float(item.get("volume"))
        if close is None or high is None or low is None:
            return None, None, None, None

        closes.append(close)
        highs.append(high)
        lows.append(low)
        volumes.append(volume if volume is not None else 0.0)

    return closes, highs, lows, volumes


def calc_ma(closes, periods):
    """计算MA指标，返回历史序列和当前值"""
    result = {}
    for p in periods:
        history = []
        for i in range(p, len(closes) + 1):
            ma_val = sum(closes[i - p:i]) / p
            history.append(round(ma_val, 4))
        result[f"MA{p}"] = {
            "history": history,
            "current": history[-1] if history else 0.0
        }
    return result


def calc_macd(closes, short=12, long=26, signal=9):
    """计算MACD指标，返回历史序列和当前值"""
    if len(closes) < long + signal:
        return {"DIF": {"history": [], "current": 0.0},
                "DEA": {"history": [], "current": 0.0},
                "MACD": {"history": [], "current": 0.0}}

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

    # 从signal周期之后开始有有效数据
    start_idx = signal - 1
    return {
        "DIF": {
            "history": [round(v, 4) for v in dif[start_idx:]],
            "current": round(dif[-1], 4)
        },
        "DEA": {
            "history": [round(v, 4) for v in dea[start_idx:]],
            "current": round(dea[-1], 4)
        },
        "MACD": {
            "history": [round(v, 4) for v in macd[start_idx:]],
            "current": round(macd[-1], 4)
        },
    }


def calc_kdj(highs, lows, closes, n=9, m1=3, m2=3):
    """计算KDJ指标，返回历史序列和当前值"""
    if len(closes) < n + 2:
        return {"K": {"history": [], "current": 0.0},
                "D": {"history": [], "current": 0.0},
                "J": {"history": [], "current": 0.0}}

    k_values = [50.0]
    d_values = [50.0]
    j_values = []

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
        j = 3 * k - 2 * d
        j_values.append(j)

    # 从第二个有效值开始（初始化值跳过）
    return {
        "K": {
            "history": [round(v, 2) for v in k_values[2:]],
            "current": round(k_values[-1], 2)
        },
        "D": {
            "history": [round(v, 2) for v in d_values[2:]],
            "current": round(d_values[-1], 2)
        },
        "J": {
            "history": [round(v, 2) for v in j_values],
            "current": round(j_values[-1], 2)
        },
    }


def calc_rsi(closes, periods=(6, 12, 24)):
    """计算RSI指标，返回历史序列和当前值"""
    result = {}
    if len(closes) < 2:
        for p in periods:
            result[f"RSI{p}"] = {"history": [], "current": 0.0}
        return result

    gains = []
    losses = []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(abs(min(delta, 0.0)))

    for p in periods:
        history = []
        # 从第p+1个数据点开始有有效RSI
        for i in range(p, len(gains) + 1):
            avg_gain = sum(gains[i - p:i]) / p
            avg_loss = sum(losses[i - p:i]) / p
            if avg_loss == 0:
                rsi = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            history.append(round(rsi, 2))
        result[f"RSI{p}"] = {
            "history": history,
            "current": history[-1] if history else 0.0
        }
    return result


def calc_boll(closes, n=20, k=2):
    """计算BOLL指标，返回历史序列和当前值"""
    if len(closes) < n:
        return {"upper": {"history": [], "current": 0.0},
                "middle": {"history": [], "current": 0.0},
                "lower": {"history": [], "current": 0.0}}

    upper_history = []
    middle_history = []
    lower_history = []

    for i in range(n, len(closes) + 1):
        window = closes[i - n:i]
        mid = sum(window) / n
        var = sum((x - mid) ** 2 for x in window) / n
        std = math.sqrt(var)
        upper = mid + k * std
        lower = mid - k * std
        upper_history.append(round(upper, 4))
        middle_history.append(round(mid, 4))
        lower_history.append(round(lower, 4))

    return {
        "upper": {
            "history": upper_history,
            "current": upper_history[-1] if upper_history else 0.0
        },
        "middle": {
            "history": middle_history,
            "current": middle_history[-1] if middle_history else 0.0
        },
        "lower": {
            "history": lower_history,
            "current": lower_history[-1] if lower_history else 0.0
        },
    }


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

    closes, highs, lows, volumes = parse_klines(klines)
    if closes is None:
        print(json.dumps({"error": "invalid_klines"}, ensure_ascii=False))
        sys.exit(4)

    indicators = {
        "MA": calc_ma(closes, [5, 10, 20, 60, 120]),
        "MACD": calc_macd(closes),
        "KDJ": calc_kdj(highs, lows, closes),
        "RSI": calc_rsi(closes),
        "BOLL": calc_boll(closes),
        # 添加成交量历史数据用于量价分析
        "volume": {
            "history": volumes,
            "current": volumes[-1] if volumes else 0
        }
    }

    print(json.dumps(indicators, ensure_ascii=False))


if __name__ == "__main__":
    main()
