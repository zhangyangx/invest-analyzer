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
    if code.startswith(("60", "68")):
        return f"sh{code}"
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
