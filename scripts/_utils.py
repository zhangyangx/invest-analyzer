#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared helpers for stock scripts.
"""

import re

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"


def normalize_symbol(code: str) -> str:
    code = (code or "").strip().lower().replace("sh", "").replace("sz", "")
    if not re.fullmatch(r"\d{6}", code):
        return ""
    # Shanghai: main board (60), STAR (68), ETF/fund (50/51/52)
    if code.startswith(("60", "68", "50", "51", "52")):
        return f"sh{code}"
    # Shenzhen: main board (00), ChiNext (30), ETF/fund (15/16/18)
    if code.startswith(("00", "30", "15", "16", "18")):
        return f"sz{code}"
    return f"sz{code}"


def safe_float(val: str) -> float:
    try:
        return float(val)
    except Exception:
        return 0.0


def safe_int(val: str) -> int:
    try:
        return int(float(val))
    except Exception:
        return 0
