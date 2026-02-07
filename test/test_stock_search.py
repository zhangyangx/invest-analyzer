#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for stock_search.py script.
Tests keyword search and error handling.
"""

import json
import subprocess
import sys
import unittest


class TestStockSearch(unittest.TestCase):
    """Test cases for stock_search.py script."""

    SCRIPT = "scripts/stock_search.py"

    def run_script(self, *args):
        cmd = [sys.executable, self.SCRIPT] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr

    def test_default_search_keyword(self):
        code, stdout, stderr = self.run_script("茅台")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("items", data)
        self.assertIn("count", data)
        if data["count"] > 0:
            first = data["items"][0]
            self.assertIn("name", first)
            self.assertIn("code", first)
            self.assertIn("symbol", first)

    def test_search_sina_source(self):
        code, stdout, stderr = self.run_script("茅台", "--source", "sina", "--limit", "5")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data.get("source"), "sina")
        self.assertIn("items", data)

    def test_search_tencent_source(self):
        code, stdout, stderr = self.run_script("茅台", "--source", "tencent", "--limit", "5")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data.get("source"), "tencent")
        self.assertIn("items", data)

    def test_no_arguments_error(self):
        code, stdout, stderr = self.run_script()
        self.assertEqual(code, 1)
        self.assertIn("Usage:", stdout)

    def test_blank_keyword_error(self):
        code, stdout, stderr = self.run_script("   ")
        self.assertEqual(code, 1)
        self.assertIn("Usage:", stdout)


def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStockSearch)
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
