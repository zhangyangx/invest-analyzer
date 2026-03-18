#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deterministic technical analysis and rating script.
Input JSON:
{
  "quote": {...},
  "daily": {"klines": [...], "indicators": {...}},
  "intraday": {"klines": [...], "indicators": {...}}
}
Output: JSON with pure technical rating and structured signals.
"""

import json
import sys


def load_input():
    if len(sys.argv) >= 3 and sys.argv[1] == "--file":
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            return json.load(f)
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    return json.loads(raw)


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def last(seq, default=0.0):
    return seq[-1] if seq else default


def rising(seq, lookback=3):
    if len(seq) < lookback:
        return False
    window = seq[-lookback:]
    return window[-1] > window[0]


def falling(seq, lookback=3):
    if len(seq) < lookback:
        return False
    window = seq[-lookback:]
    return window[-1] < window[0]


def crossed_above(a_hist, b_hist):
    return len(a_hist) >= 2 and len(b_hist) >= 2 and a_hist[-2] <= b_hist[-2] and a_hist[-1] > b_hist[-1]


def crossed_below(a_hist, b_hist):
    return len(a_hist) >= 2 and len(b_hist) >= 2 and a_hist[-2] >= b_hist[-2] and a_hist[-1] < b_hist[-1]


def get_indicator(indicators, group, name):
    return ((indicators.get(group) or {}).get(name) or {})


def get_current(indicators, group, name):
    return to_float(get_indicator(indicators, group, name).get("current"))


def get_history(indicators, group, name):
    return [to_float(item) for item in get_indicator(indicators, group, name).get("history") or []]


def get_latest_close(section, quote):
    klines = (section or {}).get("klines") or []
    if klines:
        return to_float(klines[-1].get("close"))
    return to_float((quote or {}).get("current"))


def get_volume_ratio(indicators):
    volumes = [to_float(item) for item in ((indicators.get("volume") or {}).get("history") or [])]
    if len(volumes) < 5:
        return 1.0
    current = volumes[-1]
    avg5 = sum(volumes[-5:]) / 5
    if avg5 <= 0:
        return 1.0
    return round(current / avg5, 4)


def analyze_timeframe(name, section, quote):
    indicators = (section or {}).get("indicators") or {}
    if not indicators:
        return {
            "name": name,
            "bias": "neutral",
            "score": 0,
            "bullish_signals": [],
            "bearish_signals": [],
            "risks": [],
            "price": 0.0,
            "volume_ratio": 1.0,
        }

    bullish = []
    bearish = []
    risks = []
    score = 0

    price = get_latest_close(section, quote)
    volume_ratio = get_volume_ratio(indicators)

    ma5 = get_current(indicators, "MA", "MA5")
    ma20 = get_current(indicators, "MA", "MA20")
    ma60 = get_current(indicators, "MA", "MA60")
    ma5_hist = get_history(indicators, "MA", "MA5")

    if ma5 and ma20 and ma60:
        if ma5 > ma20 > ma60:
            bullish.append("ma_bullish_stack")
            score += 2
        elif ma5 < ma20 < ma60:
            bearish.append("ma_bearish_stack")
            score -= 2

    if rising(ma5_hist):
        bullish.append("ma5_rising")
        score += 1
    elif falling(ma5_hist):
        bearish.append("ma5_falling")
        score -= 1

    if price and ma20:
        if price > ma20:
            bullish.append("price_above_ma20")
            score += 1
        elif price < ma20:
            bearish.append("price_below_ma20")
            score -= 1

    dif_hist = get_history(indicators, "MACD", "DIF")
    dea_hist = get_history(indicators, "MACD", "DEA")
    dif = get_current(indicators, "MACD", "DIF")
    dea = get_current(indicators, "MACD", "DEA")
    macd_hist = get_current(indicators, "MACD", "MACD")

    if crossed_above(dif_hist, dea_hist):
        bullish.append("macd_golden_cross")
        score += 2
    elif crossed_below(dif_hist, dea_hist):
        bearish.append("macd_death_cross")
        score -= 2
    elif dif > dea and macd_hist > 0:
        bullish.append("macd_above_signal")
        score += 1
    elif dif < dea and macd_hist < 0:
        bearish.append("macd_below_signal")
        score -= 1

    rsi6_hist = get_history(indicators, "RSI", "RSI6")
    rsi12_hist = get_history(indicators, "RSI", "RSI12")
    rsi6 = get_current(indicators, "RSI", "RSI6")
    rsi12 = get_current(indicators, "RSI", "RSI12")

    if len(rsi6_hist) >= 2 and rsi6_hist[-2] < 30 and rsi6_hist[-1] > rsi6_hist[-2] and rsi6_hist[-1] >= 30:
        bullish.append("rsi_oversold_rebound")
        score += 2
    elif len(rsi6_hist) >= 2 and rsi6_hist[-2] > 70 and rsi6_hist[-1] < rsi6_hist[-2]:
        bearish.append("rsi_overbought_falling")
        score -= 2
    elif rsi12 > 50 and rising(rsi12_hist):
        bullish.append("rsi_midline_up")
        score += 1
    elif rsi12 < 50 and falling(rsi12_hist):
        bearish.append("rsi_midline_down")
        score -= 1

    if rsi6 > 70:
        risks.append("rsi_overbought")
    elif 0 < rsi6 < 30:
        risks.append("rsi_oversold")

    k_hist = get_history(indicators, "KDJ", "K")
    d_hist = get_history(indicators, "KDJ", "D")
    k_value = get_current(indicators, "KDJ", "K")
    d_value = get_current(indicators, "KDJ", "D")
    j_value = get_current(indicators, "KDJ", "J")

    if crossed_above(k_hist, d_hist):
        bullish.append("kdj_golden_cross")
        score += 1
    elif crossed_below(k_hist, d_hist):
        bearish.append("kdj_death_cross")
        score -= 1
    elif k_value > d_value:
        bullish.append("kdj_above_signal")
        score += 1
    elif k_value < d_value:
        bearish.append("kdj_below_signal")
        score -= 1

    if j_value > 100:
        risks.append("kdj_extreme_overbought")
    elif j_value < 0:
        risks.append("kdj_extreme_oversold")

    upper = get_current(indicators, "BOLL", "upper")
    middle = get_current(indicators, "BOLL", "middle")
    lower = get_current(indicators, "BOLL", "lower")

    if price and upper and price > upper:
        risks.append("price_above_upper_band")
        if volume_ratio > 1.2:
            bullish.append("boll_breakout_up")
            score += 2
    elif price and lower and price < lower:
        risks.append("price_below_lower_band")
        if volume_ratio > 1.2:
            bearish.append("boll_breakdown")
            score -= 2
    elif price and middle:
        if price > middle:
            bullish.append("price_above_boll_mid")
            score += 1
        elif price < middle:
            bearish.append("price_below_boll_mid")
            score -= 1

    prev_close = to_float((quote or {}).get("prev_close"))
    current = to_float((quote or {}).get("current"), price)
    if prev_close > 0 and current > 0 and volume_ratio > 1.1:
        if current > prev_close:
            bullish.append("volume_confirms_rise")
            score += 1
        elif current < prev_close:
            bearish.append("volume_confirms_drop")
            score -= 1

    if prev_close > 0:
        amplitude = (to_float((quote or {}).get("high")) - to_float((quote or {}).get("low"))) / prev_close * 100
        if amplitude > 5:
            risks.append("high_intraday_amplitude")

    if score >= 3:
        bias = "bullish"
    elif score <= -3:
        bias = "bearish"
    else:
        bias = "neutral"

    return {
        "name": name,
        "bias": bias,
        "score": score,
        "bullish_signals": sorted(set(bullish)),
        "bearish_signals": sorted(set(bearish)),
        "risks": sorted(set(risks)),
        "price": round(price, 4),
        "volume_ratio": volume_ratio,
    }


def summarize_rating(daily, intraday, rating):
    daily_text = {
        "bullish": "日线趋势偏多",
        "bearish": "日线趋势偏弱",
        "neutral": "日线方向不明",
    }[daily["bias"]]
    intraday_text = {
        "bullish": "5分钟动能配合",
        "bearish": "5分钟短线承压",
        "neutral": "5分钟短线震荡",
    }[intraday["bias"]]
    return f"{daily_text}，{intraday_text}，技术评级为{rating}。"


def determine_rating(daily, intraday):
    daily_bull = "ma_bullish_stack" in daily["bullish_signals"] and any(
        signal in daily["bullish_signals"]
        for signal in ("macd_golden_cross", "rsi_oversold_rebound", "boll_breakout_up")
    )
    daily_bear = "ma_bearish_stack" in daily["bearish_signals"] and any(
        signal in daily["bearish_signals"]
        for signal in ("macd_death_cross", "rsi_overbought_falling", "boll_breakdown")
    )

    intraday_bias = intraday["bias"]
    if daily["bias"] == "bullish" and intraday_bias == "bullish":
        return "买入" if daily_bull else "增持"
    if daily["bias"] == "bearish" and intraday_bias == "bearish":
        return "卖出" if daily_bear else "减持"
    if daily["bias"] == "bullish" and intraday_bias == "neutral":
        return "增持"
    if daily["bias"] == "bearish" and intraday_bias == "neutral":
        return "减持"
    return "持有"


def main():
    try:
        payload = load_input()
    except Exception as exc:
        print(json.dumps({"error": "invalid_input", "detail": str(exc)}, ensure_ascii=False))
        sys.exit(2)

    daily_section = payload.get("daily") or {}
    intraday_section = payload.get("intraday") or {}
    quote = payload.get("quote") or {}

    if not daily_section.get("indicators"):
        print(json.dumps({"error": "missing_daily_indicators"}, ensure_ascii=False))
        sys.exit(3)

    daily = analyze_timeframe("daily", daily_section, quote)
    intraday = analyze_timeframe("intraday", intraday_section, quote)
    rating = determine_rating(daily, intraday)
    technical_score = daily["score"] * 2 + intraday["score"]
    risks = sorted(set(daily["risks"] + intraday["risks"]))
    bullish_signals = sorted(set(daily["bullish_signals"] + intraday["bullish_signals"]))
    bearish_signals = sorted(set(daily["bearish_signals"] + intraday["bearish_signals"]))

    result = {
        "technical_rating": rating,
        "technical_score": technical_score,
        "daily": daily,
        "intraday": intraday,
        "bullish_signals": bullish_signals,
        "bearish_signals": bearish_signals,
        "risks": risks,
        "one_line_conclusion": summarize_rating(daily, intraday, rating),
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
