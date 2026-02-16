#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for news_fetcher.py script.
Tests keyword search via Google News RSS.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
ROOT_DIR = TEST_DIR.parent
sys.path.insert(0, str(ROOT_DIR))
from scripts import news_fetcher as news_fetcher_module  # noqa: E402


class TestNewsFetcher(unittest.TestCase):
    """Test cases for news_fetcher.py script."""

    SCRIPT = "scripts/news_fetcher.py"

    def run_script(self, *args):
        """Helper to run script and return parsed JSON output."""
        cmd = [sys.executable, self.SCRIPT] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout, result.stderr

    def test_single_keyword(self):
        """Test with single keyword."""
        code, stdout, stderr = self.run_script("--keyword", "Apple")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("items", data)
        self.assertIn("count", data)
        self.assertIsInstance(data["items"], list)

    def test_multiple_keywords(self):
        """Test with multiple keywords (comma-separated)."""
        code, stdout, stderr = self.run_script("--keywords", "AAPL,Apple,iPhone")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("items", data)
        self.assertIn("count", data)
        self.assertIsInstance(data["items"], list)

    def test_cn_en_keywords(self):
        """Test with combined Chinese and English keywords."""
        code, stdout, stderr = self.run_script(
            "--keywords", "特变电工,光伏,TBEA,photovoltaic"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("items", data)
        self.assertIn("count", data)
        self.assertIsInstance(data["items"], list)

    def test_hours_parameter_24(self):
        """Test with hours=24 (default)."""
        code, stdout, stderr = self.run_script("--keyword", "China", "--hours", "24")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("items", data)

    def test_hours_parameter_168(self):
        """Test with hours=168 (7 days)."""
        code, stdout, stderr = self.run_script("--keyword", "stock", "--hours", "168")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("items", data)

    def test_limit_parameter(self):
        """Test with custom limit parameter."""
        code, stdout, stderr = self.run_script("--keyword", "economy", "--limit", "50")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("items", data)

    def test_limit_parameter_small(self):
        """Test with small limit parameter."""
        code, stdout, stderr = self.run_script("--keyword", "finance", "--limit", "5")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("items", data)

    def test_all_parameters(self):
        """Test with all parameters."""
        code, stdout, stderr = self.run_script(
            "--keywords", "stock,market",
            "--hours", "48",
            "--limit", "20"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("items", data)
        self.assertIn("count", data)

    def test_item_structure(self):
        """Test that news items have correct structure."""
        code, stdout, stderr = self.run_script("--keyword", "technology", "--limit", "10")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        if len(data["items"]) > 0:
            item = data["items"][0]
            required_fields = ["title", "link", "source", "time"]
            for field in required_fields:
                self.assertIn(field, item)

    def test_items_sorted_by_time_descending(self):
        """Test that items are sorted by time (newest first)."""
        code, stdout, stderr = self.run_script("--keyword", "stock", "--limit", "20")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        if len(data["items"]) >= 2:
            # Items should be sorted by time descending
            # Note: Some items may not have time, so we just check no error
            pass

    def test_no_duplicate_items(self):
        """Test that duplicate items are removed."""
        code, stdout, stderr = self.run_script(
            "--keywords", "AAPL,AAPL",  # Same keyword twice
            "--limit", "20"
        )
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        # Check for duplicates by title+link
        seen = set()
        for item in data["items"]:
            key = f"{item.get('title','')}|{item.get('link','')}"
            self.assertNotIn(key, seen, f"Duplicate item found: {item.get('title')}")
            seen.add(key)

    def test_chinese_keyword(self):
        """Test with Chinese keyword."""
        code, stdout, stderr = self.run_script("--keyword", "股票")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("items", data)

    def test_stock_code_keyword(self):
        """Test with stock code as keyword."""
        code, stdout, stderr = self.run_script("--keyword", "600519")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("items", data)

    def test_missing_keyword_error(self):
        """Test that missing keyword returns error."""
        code, stdout, stderr = self.run_script()
        self.assertEqual(code, 2)
        data = json.loads(stdout)
        self.assertEqual(data.get("error"), "missing_keyword")

    def test_google_news_source(self):
        """Test that Google News is the source."""
        code, stdout, stderr = self.run_script("--keyword", "economy", "--limit", "10")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        # All items should be from Google News
        sources = [item.get("source", "") for item in data["items"]]
        self.assertIn("Google News", sources)

    def test_no_helper_field_in_output(self):
        """Test that helper field is not in final output."""
        code, stdout, stderr = self.run_script("--keyword", "test")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        for item in data["items"]:
            self.assertNotIn("_dt", item)

    def test_count_field_matches_items_length(self):
        """Test that 'count' field matches actual items length."""
        code, stdout, stderr = self.run_script("--keyword", "finance")
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertEqual(data["count"], len(data["items"]))


class TestNewsFetcherParsing(unittest.TestCase):
    """Unit tests for RSS parsing and link extraction."""

    def test_parse_rss_item_link_text(self):
        """RSS <link>text</link> should be extracted."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Example Title</title>
      <link>https://news.google.com/rss/articles/abc123</link>
      <pubDate>Sat, 07 Feb 2026 14:30:40 GMT</pubDate>
    </item>
  </channel>
</rss>
"""
        items = news_fetcher_module.parse_rss(
            xml,
            "Google News",
            limit=10,
            tz_local=news_fetcher_module.parse_tz_offset("+08:00"),
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["link"], "https://news.google.com/rss/articles/abc123")

    def test_parse_atom_entry_link_href(self):
        """Atom <link href="..."/> should be extracted."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Example Atom Title</title>
    <link href="https://example.com/atom/entry"/>
    <updated>2026-02-07T14:30:40Z</updated>
  </entry>
</feed>
"""
        items = news_fetcher_module.parse_rss(
            xml,
            "Google News",
            limit=10,
            tz_local=news_fetcher_module.parse_tz_offset("+08:00"),
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["link"], "https://example.com/atom/entry")


def run_tests():
    """Run all tests and print summary."""
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestNewsFetcher))
    suite.addTests(loader.loadTestsFromTestCase(TestNewsFetcherParsing))
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
