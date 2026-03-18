#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for stock_technical_snapshot.py script.
"""

import io
import json
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scripts.stock_technical_snapshot import ScriptError, build_snapshot, main


class TestStockTechnicalSnapshot(unittest.TestCase):
    """Test cases for stock_technical_snapshot.py."""

    def test_build_snapshot_runs_expected_pipeline(self):
        calls = []

        def fake_runner(cmd, input=None, capture_output=True, text=True, timeout=60):
            script = os.path.basename(cmd[1])
            calls.append(script)

            if script == "stock_quote.py":
                return subprocess.CompletedProcess(
                    cmd, 0, json.dumps({
                        "name": "贵州茅台",
                        "code": "600519",
                        "symbol": "sh600519",
                        "current": 112.0,
                        "prev_close": 108.0,
                        "open": 109.0,
                        "high": 113.0,
                        "low": 108.0,
                    }), ""
                )

            if script == "stock_kline.py":
                scale = int(cmd[3])
                return subprocess.CompletedProcess(
                    cmd, 0, json.dumps({
                        "symbol": "sh600519",
                        "scale": scale,
                        "count": 2,
                        "klines": [
                            {"close": "100", "high": "101", "low": "99", "open": "100", "volume": "10"},
                            {"close": "102", "high": "103", "low": "100", "open": "101", "volume": "12"},
                        ],
                    }), ""
                )

            if script == "stock_indicators.py":
                scale = json.loads(input)["scale"]
                indicator_payload = {
                    "MA": {"MA5": {"history": [100, 101, 102], "current": 102}},
                    "MACD": {"DIF": {"history": [0.1, 0.2], "current": 0.2}},
                    "KDJ": {"K": {"history": [40, 50], "current": 50}},
                    "RSI": {"RSI6": {"history": [45, 55], "current": 55}},
                    "BOLL": {"upper": {"history": [103], "current": 103}},
                    "volume": {"history": [10, 12], "current": 12},
                    "meta_scale": scale,
                }
                return subprocess.CompletedProcess(cmd, 0, json.dumps(indicator_payload), "")

            if script == "stock_technical_analysis.py":
                payload = json.loads(input)
                self.assertEqual(payload["quote"]["code"], "600519")
                self.assertEqual(payload["daily"]["klines"][-1]["close"], "102")
                self.assertEqual(payload["intraday"]["indicators"]["meta_scale"], 5)
                return subprocess.CompletedProcess(
                    cmd, 0, json.dumps({"technical_rating": "买入", "technical_score": 6}), ""
                )

            raise AssertionError(f"Unexpected command: {cmd}")

        snapshot = build_snapshot("600519", runner=fake_runner)

        self.assertEqual(snapshot["technical_analysis"]["technical_rating"], "买入")
        self.assertEqual(snapshot["quote"]["symbol"], "sh600519")
        self.assertEqual(snapshot["daily"]["indicators"]["meta_scale"], 240)
        self.assertEqual(snapshot["intraday"]["indicators"]["meta_scale"], 5)
        self.assertEqual(
            calls,
            [
                "stock_quote.py",
                "stock_kline.py",
                "stock_kline.py",
                "stock_indicators.py",
                "stock_indicators.py",
                "stock_technical_analysis.py",
            ],
        )

    def test_build_snapshot_raises_on_upstream_failure(self):
        def fake_runner(cmd, input=None, capture_output=True, text=True, timeout=60):
            script = os.path.basename(cmd[1])
            if script == "stock_quote.py":
                return subprocess.CompletedProcess(cmd, 0, json.dumps({"code": "600519"}), "")
            return subprocess.CompletedProcess(
                cmd, 7, json.dumps({"error": "request_failed"}), "network error"
            )

        with self.assertRaises(ScriptError) as ctx:
            build_snapshot("600519", runner=fake_runner)

        self.assertEqual(ctx.exception.script_name, "stock_kline.py")
        self.assertEqual(ctx.exception.exit_code, 7)

    def test_main_prints_snapshot_json(self):
        fake_snapshot = {"technical_analysis": {"technical_rating": "增持"}}

        with patch("scripts.stock_technical_snapshot.build_snapshot", return_value=fake_snapshot):
            with patch.object(sys, "argv", ["stock_technical_snapshot.py", "600519"]):
                buffer = io.StringIO()
                with redirect_stdout(buffer):
                    main()

        self.assertEqual(json.loads(buffer.getvalue()), fake_snapshot)


if __name__ == "__main__":
    unittest.main()
