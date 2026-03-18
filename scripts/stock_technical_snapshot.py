#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-click technical snapshot pipeline.

Fetches quote, daily/intraday K-lines, indicators, and deterministic
technical analysis in a single command.
"""

import argparse
import json
import os
import subprocess
import sys


class ScriptError(Exception):
    """Raised when a downstream script exits unsuccessfully."""

    def __init__(self, script_name, exit_code, detail="", payload=None):
        super().__init__(f"{script_name} exited with {exit_code}")
        self.script_name = script_name
        self.exit_code = exit_code
        self.detail = detail
        self.payload = payload or {}


def script_path(script_name):
    return os.path.join(os.path.dirname(__file__), script_name)


def run_json_script(script_name, args=None, input_data=None, runner=subprocess.run, timeout=60):
    cmd = [sys.executable, script_path(script_name)]
    if args:
        cmd.extend(args)

    result = runner(
        cmd,
        input=input_data,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()

    if result.returncode != 0:
        payload = {}
        if stdout:
            try:
                payload = json.loads(stdout)
            except json.JSONDecodeError:
                payload = {}
        raise ScriptError(script_name, result.returncode, stderr or stdout, payload)

    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ScriptError(script_name, result.returncode, f"invalid_json_output: {exc}", {}) from exc


def build_snapshot(stock_code, daily_count=120, intraday_count=200, runner=subprocess.run, timeout=60):
    quote = run_json_script("stock_quote.py", [stock_code], runner=runner, timeout=timeout)
    daily_kline = run_json_script(
        "stock_kline.py",
        [stock_code, "240", str(daily_count)],
        runner=runner,
        timeout=timeout,
    )
    intraday_kline = run_json_script(
        "stock_kline.py",
        [stock_code, "5", str(intraday_count)],
        runner=runner,
        timeout=timeout,
    )

    daily_indicators = run_json_script(
        "stock_indicators.py",
        input_data=json.dumps(daily_kline, ensure_ascii=False),
        runner=runner,
        timeout=timeout,
    )
    intraday_indicators = run_json_script(
        "stock_indicators.py",
        input_data=json.dumps(intraday_kline, ensure_ascii=False),
        runner=runner,
        timeout=timeout,
    )

    analysis_payload = {
        "quote": quote,
        "daily": {
            "klines": daily_kline.get("klines") or [],
            "indicators": daily_indicators,
        },
        "intraday": {
            "klines": intraday_kline.get("klines") or [],
            "indicators": intraday_indicators,
        },
    }
    technical_analysis = run_json_script(
        "stock_technical_analysis.py",
        input_data=json.dumps(analysis_payload, ensure_ascii=False),
        runner=runner,
        timeout=timeout,
    )

    return {
        "quote": quote,
        "daily": {
            "symbol": daily_kline.get("symbol"),
            "scale": daily_kline.get("scale"),
            "count": daily_kline.get("count"),
            "klines": daily_kline.get("klines") or [],
            "indicators": daily_indicators,
        },
        "intraday": {
            "symbol": intraday_kline.get("symbol"),
            "scale": intraday_kline.get("scale"),
            "count": intraday_kline.get("count"),
            "klines": intraday_kline.get("klines") or [],
            "indicators": intraday_indicators,
        },
        "technical_analysis": technical_analysis,
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Fetch a full technical snapshot for a stock code."
    )
    parser.add_argument("stock_code", help="6-digit stock code, with or without market prefix")
    parser.add_argument("--daily-count", type=int, default=120, help="Daily K-line count, default 120")
    parser.add_argument("--intraday-count", type=int, default=200, help="5-minute K-line count, default 200")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds for each child script")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    try:
        snapshot = build_snapshot(
            args.stock_code,
            daily_count=args.daily_count,
            intraday_count=args.intraday_count,
            timeout=args.timeout,
        )
        print(json.dumps(snapshot, ensure_ascii=False))
    except ScriptError as exc:
        print(json.dumps({
            "error": "upstream_failed",
            "script": exc.script_name,
            "exit_code": exc.exit_code,
            "detail": exc.detail,
            "payload": exc.payload,
        }, ensure_ascii=False))
        sys.exit(3)


if __name__ == "__main__":
    main()
