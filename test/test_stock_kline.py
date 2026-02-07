#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for stock_kline.py script.
Tests all supported parameters and edge cases.
"""

import json
import subprocess
import sys
import unittest


class TestStockKline(unittest.TestCase):
    """Test cases for stock_kline.py script."""

    SCRIPT = "scripts/stock_kline.py"

    def run_script(self, *args):
        """Helper to run script and return parsed JSON output."""
        cmd = [sys.executable, self.SCRIPT] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr

    def test_default_parameters(self):
        """Test with default parameters (no scale/count)."""
        code, stdout, stderr = self.run_script("600519")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("symbol", data)
        self.assertIn("scale", data)
        self.assertEqual(data["scale"], 240)  # Default scale
        self.assertIn("count", data)
        self.assertGreater(data["count"], 0)
        self.assertIn("klines", data)
        self.assertIsInstance(data["klines"], list)

    def test_custom_scale_daily(self):
        """Test with custom scale (240 = daily)."""
        code, stdout, stderr = self.run_script("600519", "240")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["scale"], 240)

    def test_custom_scale_60min(self):
        """Test with custom scale (60 = 1-hour)."""
        code, stdout, stderr = self.run_script("600519", "60")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["scale"], 60)

    def test_custom_scale_30min(self):
        """Test with custom scale (30 = 30-minute)."""
        code, stdout, stderr = self.run_script("600519", "30")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["scale"], 30)

    def test_custom_scale_15min(self):
        """Test with custom scale (15 = 15-minute)."""
        code, stdout, stderr = self.run_script("600519", "15")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["scale"], 15)

    def test_custom_scale_5min(self):
        """Test with custom scale (5 = 5-minute)."""
        code, stdout, stderr = self.run_script("600519", "5")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["scale"], 5)

    def test_custom_count(self):
        """Test with custom count parameter."""
        code, stdout, stderr = self.run_script("600519", "240", "200")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertLessEqual(data["count"], 200)

    def test_custom_count_small(self):
        """Test with small count parameter."""
        code, stdout, stderr = self.run_script("600519", "240", "20")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertLessEqual(data["count"], 20)

    def test_sh_stock_code(self):
        """Test with Shanghai stock code."""
        code, stdout, stderr = self.run_script("sh600519", "240")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["symbol"], "sh600519")

    def test_sz_stock_code(self):
        """Test with Shenzhen stock code."""
        code, stdout, stderr = self.run_script("sz000001", "240")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["symbol"], "sz000001")

    def test_kline_structure(self):
        """Test that kline data has correct structure."""
        code, stdout, stderr = self.run_script("600519", "240", "10")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertGreater(len(data["klines"]), 0)
        kline = data["klines"][0]
        required_fields = ["open", "high", "low", "close", "volume"]
        for field in required_fields:
            self.assertIn(field, kline, f"Missing field: {field}")

    def test_kline_values_are_strings(self):
        """Test that kline OHLCV values are strings (as expected)."""
        code, stdout, stderr = self.run_script("600519", "240", "5")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        kline = data["klines"][0]
        for field in ["open", "high", "low", "close", "volume"]:
            self.assertIsInstance(kline[field], str)

    def test_no_arguments_error(self):
        """Test that script fails gracefully with no arguments."""
        code, stdout, stderr = self.run_script()
        self.assertEqual(code, 1)
        self.assertIn("Usage:", stdout)

    def test_invalid_stock_code(self):
        """Test with invalid stock code."""
        code, stdout, stderr = self.run_script("invalid")
        self.assertEqual(code, 2)
        data = json.loads(stdout)
        self.assertEqual(data.get("error"), "invalid_stock_code")

    def test_invalid_scale(self):
        """Test with invalid scale parameter."""
        code, stdout, stderr = self.run_script("600519", "invalid")
        self.assertEqual(code, 3)
        data = json.loads(stdout)
        self.assertEqual(data.get("error"), "invalid_scale")

    def test_invalid_count(self):
        """Test with invalid count parameter."""
        code, stdout, stderr = self.run_script("600519", "240", "invalid")
        self.assertEqual(code, 4)
        data = json.loads(stdout)
        self.assertEqual(data.get("error"), "invalid_count")

    def test_knowledge_board_stock(self):
        """Test ChiNext (300xxx) stock code."""
        code, stdout, stderr = self.run_script("300750", "240")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["symbol"], "sz300750")


def run_tests():
    """Run all tests and print summary."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStockKline)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 80)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
