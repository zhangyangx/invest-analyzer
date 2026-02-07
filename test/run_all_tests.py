#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run all test suites for invest-analyzer scripts.
"""

import subprocess
import sys


def run_test(script_name):
    """Run a single test script and return success status."""
    print(f"\n{'=' * 80}")
    print(f"Running: {script_name}")
    print('=' * 80)
    result = subprocess.run(
        [sys.executable, f"test/{script_name}"],
        capture_output=False,
        text=True
    )
    return result.returncode == 0


def main():
    """Run all test suites."""
    test_scripts = [
        "test_stock_quote.py",
        "test_stock_kline.py",
        "test_stock_indicators.py",
        "test_keyword_expander.py",
        "test_news_fetcher.py",
    ]

    print("\n" + "=" * 80)
    print("INVEST-ANALYZER TEST SUITE")
    print("=" * 80)

    results = {}
    for script in test_scripts:
        success = run_test(script)
        results[script] = success

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for script, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:<8} | {script}")

    total = len(results)
    passed = sum(1 for s in results.values() if s)
    failed = total - passed

    print("=" * 80)
    print(f"Total: {total}, Passed: {passed}, Failed: {failed}")
    print("=" * 80)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
