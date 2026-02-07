#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for keyword_expander.py script.
Tests all supported parameters and combinations.
"""

import json
import subprocess
import sys
import unittest


class TestKeywordExpander(unittest.TestCase):
    """Test cases for keyword_expander.py script."""

    SCRIPT = "scripts/keyword_expander.py"

    def run_script(self, *args):
        """Helper to run script and return parsed JSON output."""
        cmd = [sys.executable, self.SCRIPT] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode, result.stdout, result.stderr

    def test_code_only(self):
        """Test with only stock code (no topic)."""
        code, stdout, stderr = self.run_script("--code", "600519")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("keywords", data)
        self.assertGreater(len(data["keywords"]), 0)
        # Should contain base keywords
        self.assertIn("600519", data["keywords"])
        self.assertIn("600519 股票", data["keywords"])
        self.assertIn("600519 公司", data["keywords"])

    def test_code_with_topic_chinese(self):
        """Test with code and Chinese topic."""
        code, stdout, stderr = self.run_script(
            "--code", "600519",
            "--topic", "财报"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        # Should contain topic-related keywords
        self.assertIn("财报", keywords)
        self.assertIn("600519 财报", keywords)
        self.assertIn("600519 相关 财报", keywords)

    def test_code_with_topic_en(self):
        """Test with code and English topic."""
        code, stdout, stderr = self.run_script(
            "--code", "600519",
            "--topic-en", "earnings"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        # Should contain English topic keywords
        self.assertIn("earnings", keywords)
        self.assertIn("600519 earnings", keywords)
        self.assertIn("600519 related earnings", keywords)

    def test_code_with_both_topics(self):
        """Test with code, Chinese topic, and English topic."""
        code, stdout, stderr = self.run_script(
            "--code", "600519",
            "--topic", "财报",
            "--topic-en", "earnings"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        # Should contain both Chinese and English keywords
        self.assertIn("财报", keywords)
        self.assertIn("600519 财报", keywords)
        self.assertIn("earnings", keywords)
        self.assertIn("600519 earnings", keywords)

    def test_extra_keywords(self):
        """Test with extra keywords."""
        code, stdout, stderr = self.run_script(
            "--code", "600519",
            "--extra", "重组,资产,并购"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        self.assertIn("重组", keywords)
        self.assertIn("资产", keywords)
        self.assertIn("并购", keywords)

    def test_topic_with_multiple_terms(self):
        """Test topic with comma-separated terms."""
        code, stdout, stderr = self.run_script(
            "--code", "600519",
            "--topic", "财报,业绩,公告"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        self.assertIn("财报", keywords)
        self.assertIn("业绩", keywords)
        self.assertIn("公告", keywords)
        self.assertIn("600519 财报", keywords)
        self.assertIn("600519 业绩", keywords)

    def test_topic_en_with_multiple_terms(self):
        """Test English topic with comma-separated terms."""
        code, stdout, stderr = self.run_script(
            "--code", "600519",
            "--topic-en", "earnings,revenue,profit"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        self.assertIn("earnings", keywords)
        self.assertIn("revenue", keywords)
        self.assertIn("profit", keywords)

    def test_all_parameters(self):
        """Test with all parameters combined."""
        code, stdout, stderr = self.run_script(
            "--code", "600519",
            "--topic", "财报",
            "--topic-en", "earnings",
            "--extra", "重组,并购"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        # Should contain all types of keywords
        self.assertIn("600519", keywords)
        self.assertIn("600519 财报", keywords)
        self.assertIn("600519 earnings", keywords)
        self.assertIn("重组", keywords)
        self.assertIn("并购", keywords)

    def test_code_with_prefix(self):
        """Test stock code with market prefix."""
        code, stdout, stderr = self.run_script(
            "--code", "sh600519",
            "--topic", "财报"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        # Should normalize to 6-digit code
        self.assertIn("600519", data["keywords"])

    def test_sz_stock_code(self):
        """Test Shenzhen stock code."""
        code, stdout, stderr = self.run_script(
            "--code", "sz000001",
            "--topic", "业绩"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        # Should normalize to 6-digit code
        self.assertIn("000001", data["keywords"])

    def test_keywords_are_unique(self):
        """Test that keywords are deduplicated."""
        code, stdout, stderr = self.run_script(
            "--code", "600519",
            "--topic", "财报,财报",  # Duplicate in topic
            "--extra", "财报"  # Same as topic
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        # Check no duplicates
        self.assertEqual(len(keywords), len(set(keywords)))

    def test_keywords_order_preserved(self):
        """Test that keyword order is preserved (no reordering)."""
        code, stdout, stderr = self.run_script(
            "--code", "600519",
            "--topic", "财报,业绩"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        # First keywords should be base keywords
        self.assertEqual(keywords[0], "600519")

    def test_topic_with_spaces(self):
        """Test topic with spaces."""
        code, stdout, stderr = self.run_script(
            "--code", "600519",
            "--topic", "  财报 ,  业绩  "
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        # Should trim spaces
        self.assertIn("财报", keywords)
        self.assertIn("业绩", keywords)

    def test_topic_with_newline_separators(self):
        """Test topic with newline separators."""
        code, stdout, stderr = self.run_script(
            "--code", "600519",
            "--topic", "财报\n业绩"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        self.assertIn("财报", keywords)
        self.assertIn("业绩", keywords)

    def test_empty_topic(self):
        """Test with empty topic."""
        code, stdout, stderr = self.run_script(
            "--code", "600519",
            "--topic", ""
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        # Should still have base keywords
        self.assertIn("600519", data["keywords"])

    def test_missing_code_parameter(self):
        """Test without --code parameter (should still work but return error)."""
        code, stdout, stderr = self.run_script("--topic", "财报")
        self.assertEqual(code, 0)
        data = json.loads(stdout)
        self.assertEqual(data.get("error"), "invalid_stock_code")

    def test_invalid_code(self):
        """Test with invalid stock code."""
        code, stdout, stderr = self.run_script("--code", "invalid")
        self.assertEqual(code, 0)
        data = json.loads(stdout)
        self.assertEqual(data.get("error"), "invalid_stock_code")

    def test_short_code(self):
        """Test with short stock code."""
        code, stdout, stderr = self.run_script("--code", "123")
        self.assertEqual(code, 0)
        data = json.loads(stdout)
        self.assertEqual(data.get("error"), "invalid_stock_code")


def run_tests():
    """Run all tests and print summary."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestKeywordExpander)
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
