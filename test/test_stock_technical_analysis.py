#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for stock_technical_analysis.py script.
"""

import json
import subprocess
import sys
import unittest


class TestStockTechnicalAnalysis(unittest.TestCase):
    """Test cases for stock_technical_analysis.py script."""

    SCRIPT = "scripts/stock_technical_analysis.py"

    def run_script(self, payload):
        result = subprocess.run(
            [sys.executable, self.SCRIPT],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr

    def make_payload(self, daily_indicators, intraday_indicators, quote=None, extra=None):
        payload = {
            "quote": quote or {
                "current": 112,
                "prev_close": 108,
                "open": 109,
                "high": 113,
                "low": 108,
            },
            "daily": {
                "klines": [{"close": "111", "volume": "150"}],
                "indicators": daily_indicators,
            },
            "intraday": {
                "klines": [{"close": "112", "volume": "80"}],
                "indicators": intraday_indicators,
            },
        }
        if extra:
            payload.update(extra)
        return payload

    def bullish_indicators(self):
        return {
            "MA": {
                "MA5": {"history": [100, 102, 104], "current": 104},
                "MA10": {"history": [99, 100, 102], "current": 102},
                "MA20": {"history": [95, 97, 99], "current": 99},
                "MA60": {"history": [90, 91, 92], "current": 92},
                "MA120": {"history": [85, 86, 87], "current": 87},
            },
            "MACD": {
                "DIF": {"history": [-0.6, -0.3, 0.2], "current": 0.2},
                "DEA": {"history": [-0.4, -0.2, 0.0], "current": 0.0},
                "MACD": {"history": [-0.4, -0.2, 0.4], "current": 0.4},
            },
            "KDJ": {
                "K": {"history": [20, 28, 40], "current": 40},
                "D": {"history": [25, 27, 31], "current": 31},
                "J": {"history": [10, 30, 58], "current": 58},
            },
            "RSI": {
                "RSI6": {"history": [24, 28, 35], "current": 35},
                "RSI12": {"history": [42, 46, 52], "current": 52},
                "RSI24": {"history": [45, 48, 50], "current": 50},
            },
            "BOLL": {
                "upper": {"history": [108, 110, 111], "current": 111},
                "middle": {"history": [100, 101, 102], "current": 102},
                "lower": {"history": [92, 92, 93], "current": 93},
            },
            "volume": {"history": [80, 90, 100, 110, 150], "current": 150},
        }

    def bearish_indicators(self):
        return {
            "MA": {
                "MA5": {"history": [104, 102, 99], "current": 99},
                "MA10": {"history": [106, 104, 101], "current": 101},
                "MA20": {"history": [108, 107, 105], "current": 105},
                "MA60": {"history": [112, 111, 110], "current": 110},
                "MA120": {"history": [118, 117, 116], "current": 116},
            },
            "MACD": {
                "DIF": {"history": [0.6, 0.2, -0.3], "current": -0.3},
                "DEA": {"history": [0.4, 0.1, -0.1], "current": -0.1},
                "MACD": {"history": [0.4, 0.2, -0.4], "current": -0.4},
            },
            "KDJ": {
                "K": {"history": [82, 72, 58], "current": 58},
                "D": {"history": [76, 74, 66], "current": 66},
                "J": {"history": [94, 68, 42], "current": 42},
            },
            "RSI": {
                "RSI6": {"history": [82, 74, 66], "current": 66},
                "RSI12": {"history": [62, 56, 48], "current": 48},
                "RSI24": {"history": [58, 54, 49], "current": 49},
            },
            "BOLL": {
                "upper": {"history": [110, 109, 108], "current": 108},
                "middle": {"history": [104, 103, 102], "current": 102},
                "lower": {"history": [98, 97, 96], "current": 96},
            },
            "volume": {"history": [90, 95, 100, 110, 180], "current": 180},
        }

    def test_buy_rating_is_deterministic_and_technical_only(self):
        payload = self.make_payload(
            self.bullish_indicators(),
            self.bullish_indicators(),
            extra={"news_sentiment": "major_negative"},
        )
        code, stdout, stderr = self.run_script(payload)

        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["technical_rating"], "买入")
        self.assertGreater(data["technical_score"], 0)
        self.assertEqual(data["daily"]["bias"], "bullish")
        self.assertEqual(data["intraday"]["bias"], "bullish")
        self.assertNotIn("news_sentiment", data)

    def test_sell_rating_is_deterministic_and_technical_only(self):
        payload = self.make_payload(
            self.bearish_indicators(),
            self.bearish_indicators(),
            quote={
                "current": 94,
                "prev_close": 100,
                "open": 99,
                "high": 100,
                "low": 93,
            },
        )
        code, stdout, stderr = self.run_script(payload)

        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["technical_rating"], "卖出")
        self.assertLess(data["technical_score"], 0)
        self.assertEqual(data["daily"]["bias"], "bearish")
        self.assertEqual(data["intraday"]["bias"], "bearish")

    def test_mixed_signals_result_in_hold(self):
        payload = self.make_payload(
            self.bullish_indicators(),
            self.bearish_indicators(),
        )
        code, stdout, stderr = self.run_script(payload)

        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["technical_rating"], "持有")
        self.assertEqual(data["daily"]["bias"], "bullish")
        self.assertEqual(data["intraday"]["bias"], "bearish")


if __name__ == "__main__":
    unittest.main()
