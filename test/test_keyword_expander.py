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

    def test_name_only(self):
        """Test with only stock name (no code)."""
        code, stdout, stderr = self.run_script("--name", "贵州茅台")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        self.assertIn("贵州茅台", keywords)
        self.assertNotIn("600519", keywords)

    def test_name_with_topic_chinese(self):
        """Test with name and Chinese topic."""
        code, stdout, stderr = self.run_script(
            "--name", "贵州茅台",
            "--topic", "财报"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        self.assertIn("财报", keywords)
        self.assertIn("贵州茅台 财报", keywords)
        self.assertIn("贵州茅台 相关 财报", keywords)

    def test_name_with_topic_en(self):
        """Test with name and English topic."""
        code, stdout, stderr = self.run_script(
            "--name", "贵州茅台",
            "--topic-en", "earnings"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        self.assertIn("earnings", keywords)
        self.assertIn("贵州茅台 earnings", keywords)
        self.assertIn("贵州茅台 related earnings", keywords)

    def test_name_with_both_topics(self):
        """Test with name, Chinese topic, and English topic."""
        code, stdout, stderr = self.run_script(
            "--name", "贵州茅台",
            "--topic", "财报",
            "--topic-en", "earnings"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        # Should contain both Chinese and English keywords
        self.assertIn("财报", keywords)
        self.assertIn("贵州茅台 财报", keywords)
        self.assertIn("earnings", keywords)
        self.assertIn("贵州茅台 earnings", keywords)

    def test_extra_keywords(self):
        """Test with extra keywords."""
        code, stdout, stderr = self.run_script(
            "--name", "贵州茅台",
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
            "--name", "贵州茅台",
            "--topic", "财报,业绩,公告"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        self.assertIn("财报", keywords)
        self.assertIn("业绩", keywords)
        self.assertIn("公告", keywords)
        self.assertIn("贵州茅台 财报", keywords)
        self.assertIn("贵州茅台 业绩", keywords)

    def test_topic_en_with_multiple_terms(self):
        """Test English topic with comma-separated terms."""
        code, stdout, stderr = self.run_script(
            "--name", "贵州茅台",
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
            "--name", "贵州茅台",
            "--topic", "财报",
            "--topic-en", "earnings",
            "--extra", "重组,并购"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        # Should contain all types of keywords
        self.assertIn("贵州茅台", keywords)
        self.assertIn("贵州茅台 财报", keywords)
        self.assertIn("贵州茅台 earnings", keywords)
        self.assertIn("重组", keywords)
        self.assertIn("并购", keywords)

    def test_name_with_full_company_name(self):
        """Test stock name with full company name."""
        code, stdout, stderr = self.run_script(
            "--name", "平安银行",
            "--topic", "财报"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        # Should use the full name
        self.assertIn("平安银行", data["keywords"])

    def test_keywords_are_unique(self):
        """Test that keywords are deduplicated."""
        code, stdout, stderr = self.run_script(
            "--name", "贵州茅台",
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
            "--name", "贵州茅台",
            "--topic", "财报,业绩"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        # First keywords should be base keywords
        self.assertEqual(keywords[0], "贵州茅台")

    def test_topic_with_spaces(self):
        """Test topic with spaces."""
        code, stdout, stderr = self.run_script(
            "--name", "贵州茅台",
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
            "--name", "贵州茅台",
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
            "--name", "贵州茅台",
            "--topic", ""
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        # Should still have base keywords
        self.assertIn("贵州茅台", data["keywords"])

    def test_missing_name(self):
        """Test without --name (should return error with exit code 2)."""
        code, stdout, stderr = self.run_script("--topic", "财报")
        self.assertEqual(code, 2)
        data = json.loads(stdout)
        self.assertEqual(data.get("error"), "invalid_stock_name")

    def test_name_en_for_english_source(self):
        """Test with English name."""
        code, stdout, stderr = self.run_script(
            "--name", "TBEA",
            "--topic-en", "photovoltaic"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        self.assertIn("TBEA", keywords)
        self.assertIn("TBEA photovoltaic", keywords)
        self.assertIn("TBEA related photovoltaic", keywords)

    def test_topic_en_generates_keywords(self):
        """Test English topic generates keywords."""
        code, stdout, stderr = self.run_script(
            "--name", "贵州茅台",
            "--topic-en", "earnings"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        keywords = data["keywords"]
        self.assertIn("earnings", keywords)
        self.assertIn("贵州茅台 earnings", keywords)


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
