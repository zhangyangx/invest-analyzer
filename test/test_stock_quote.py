#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for stock_quote.py script.
Tests all supported parameters and edge cases.
"""

import json
import subprocess
import sys
import unittest


class TestStockQuote(unittest.TestCase):
    """Test cases for stock_quote.py script."""

    SCRIPT = "scripts/stock_quote.py"

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

    def test_sh_stock_code_6digit(self):
        """Test Shanghai stock with 6-digit code (e.g., 600519)."""
        code, stdout, stderr = self.run_script("600519")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("name", data)
        self.assertIn("code", data)
        self.assertEqual(data["code"], "600519")
        self.assertIn("current", data)
        self.assertIn("change", data)
        self.assertIn("pct_change", data)

    def test_sz_stock_code_6digit(self):
        """Test Shenzhen stock with 6-digit code (e.g., 000001)."""
        code, stdout, stderr = self.run_script("000001")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["code"], "000001")

    def test_stock_code_with_sh_prefix(self):
        """Test stock code with 'sh' prefix."""
        code, stdout, stderr = self.run_script("sh600519")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["code"], "600519")
        self.assertEqual(data["symbol"], "sh600519")

    def test_stock_code_with_sz_prefix(self):
        """Test stock code with 'sz' prefix."""
        code, stdout, stderr = self.run_script("sz000001")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["code"], "000001")
        self.assertEqual(data["symbol"], "sz000001")

    def test_stock_code_uppercase_prefix(self):
        """Test stock code with uppercase 'SH' prefix."""
        code, stdout, stderr = self.run_script("SH600519")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["code"], "600519")

    def test_level1_quotes_present(self):
        """Test that level-1 quotes (buy/sell orders) are present."""
        code, stdout, stderr = self.run_script("600519")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        # Check for at least buy1 and sell1
        self.assertIn("buy1_p", data)
        self.assertIn("buy1_v", data)
        self.assertIn("sell1_p", data)
        self.assertIn("sell1_v", data)

    def test_required_fields_present(self):
        """Test that all required fields are present."""
        code, stdout, stderr = self.run_script("600519")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        required_fields = [
            "name", "code", "symbol", "current",
            "prev_close", "open", "high", "low", "volume", "amount",
            "change", "pct_change"
        ]
        for field in required_fields:
            self.assertIn(field, data, f"Missing field: {field}")
        self.assertGreaterEqual(data["amount"], 0)

    def test_no_arguments_error(self):
        """Test that script fails gracefully with no arguments."""
        code, stdout, stderr = self.run_script()
        self.assertEqual(code, 1)
        self.assertIn("Usage:", stdout)

    def test_invalid_stock_code(self):
        """Test with invalid stock code (non-numeric)."""
        code, stdout, stderr = self.run_script("invalid")
        self.assertEqual(code, 2)
        data = json.loads(stdout)
        self.assertEqual(data.get("error"), "invalid_stock_code")

    def test_invalid_stock_code_short(self):
        """Test with invalid stock code (too short)."""
        code, stdout, stderr = self.run_script("123")
        self.assertEqual(code, 2)
        data = json.loads(stdout)
        self.assertEqual(data.get("error"), "invalid_stock_code")

    def test_knowledge_board_stock(self):
        """Test ChiNext (300xxx) stock code."""
        code, stdout, stderr = self.run_script("300750")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["code"], "300750")
        self.assertEqual(data["symbol"], "sz300750")

    def test_change_calculation(self):
        """Test that change and percentage change are calculated correctly."""
        code, stdout, stderr = self.run_script("600519")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        # Verify: change = current - prev_close
        expected_change = round(data["current"] - data["prev_close"], 4)
        self.assertEqual(data["change"], expected_change)
        # Verify: pct_change = change / prev_close * 100
        if data["prev_close"] > 0:
            expected_pct = round(expected_change / data["prev_close"] * 100, 2)
            self.assertEqual(data["pct_change"], expected_pct)


def run_tests():
    """Run all tests and print summary."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStockQuote)
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
