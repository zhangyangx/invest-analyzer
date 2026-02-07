#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for stock_indicators.py script.
Tests all input methods and indicator calculations.
"""

import json
import subprocess
import sys
import tempfile
import unittest


class TestStockIndicators(unittest.TestCase):
    """Test cases for stock_indicators.py script."""

    SCRIPT = "scripts/stock_indicators.py"

    def run_script(self, stdin_data=None, file_path=None):
        """Helper to run script and return parsed JSON output."""
        cmd = [sys.executable, self.SCRIPT]
        if file_path:
            cmd.extend(["--file", file_path])
        result = subprocess.run(
            cmd,
            input=stdin_data,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr

    def create_kline_data(self, count=50):
        """Create synthetic kline data for testing."""
        klines = []
        price = 100.0
        for i in range(count):
            open_p = price
            close = price + (i % 5 - 2)  # Small variation
            high = max(open_p, close) + 1
            low = min(open_p, close) - 1
            klines.append({
                "open": str(round(open_p, 2)),
                "high": str(round(high, 2)),
                "low": str(round(low, 2)),
                "close": str(round(close, 2))
            })
            price = close
        return {"klines": klines}

    def test_stdin_input(self):
        """Test reading K-line data from stdin."""
        kline_data = self.create_kline_data(150)
        code, stdout, stderr = self.run_script(stdin_data=json.dumps(kline_data))
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        self.assertIn("MA", data)
        self.assertIn("MACD", data)
        self.assertIn("KDJ", data)
        self.assertIn("RSI", data)
        self.assertIn("BOLL", data)

    def test_file_input(self):
        """Test reading K-line data from file."""
        kline_data = self.create_kline_data(150)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(kline_data, f)
            temp_path = f.name

        try:
            code, stdout, stderr = self.run_script(file_path=temp_path)
            self.assertEqual(code, 0, f"Script failed: {stderr}")
            data = json.loads(stdout)
            self.assertIn("MA", data)
        finally:
            import os
            os.unlink(temp_path)

    def test_ma_calculation(self):
        """Test MA (Moving Average) calculation."""
        kline = self.create_kline_data(150)
        code, stdout, stderr = self.run_script(stdin_data=json.dumps(kline))
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        ma = data["MA"]
        self.assertIn("MA5", ma)
        self.assertIn("MA10", ma)
        self.assertIn("MA20", ma)
        self.assertIn("MA60", ma)
        self.assertIn("MA120", ma)
        # All MA values should be positive
        for period in ["MA5", "MA10", "MA20", "MA60", "MA120"]:
            self.assertGreater(ma[period], 0)

    def test_macd_calculation(self):
        """Test MACD calculation."""
        kline = self.create_kline_data(150)
        code, stdout, stderr = self.run_script(stdin_data=json.dumps(kline))
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        macd = data["MACD"]
        self.assertIn("DIF", macd)
        self.assertIn("DEA", macd)
        self.assertIn("MACD", macd)
        # MACD = (DIF - DEA) * 2
        expected_macd = round((macd["DIF"] - macd["DEA"]) * 2, 4)
        self.assertAlmostEqual(macd["MACD"], expected_macd, places=4)

    def test_kdj_calculation(self):
        """Test KDJ calculation."""
        kline = self.create_kline_data(50)
        code, stdout, stderr = self.run_script(stdin_data=json.dumps(kline))
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        kdj = data["KDJ"]
        self.assertIn("K", kdj)
        self.assertIn("D", kdj)
        self.assertIn("J", kdj)
        # J = 3*K - 2*D
        expected_j = round(3 * kdj["K"] - 2 * kdj["D"], 2)
        self.assertAlmostEqual(kdj["J"], expected_j, places=1)

    def test_rsi_calculation(self):
        """Test RSI calculation."""
        kline = self.create_kline_data(150)
        code, stdout, stderr = self.run_script(stdin_data=json.dumps(kline))
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        rsi = data["RSI"]
        self.assertIn("RSI6", rsi)
        self.assertIn("RSI12", rsi)
        self.assertIn("RSI24", rsi)
        # RSI should be between 0 and 100
        for period in ["RSI6", "RSI12", "RSI24"]:
            self.assertGreaterEqual(rsi[period], 0)
            self.assertLessEqual(rsi[period], 100)

    def test_boll_calculation(self):
        """Test BOLL (Bollinger Bands) calculation."""
        kline = self.create_kline_data(50)
        code, stdout, stderr = self.run_script(stdin_data=json.dumps(kline))
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        boll = data["BOLL"]
        self.assertIn("upper", boll)
        self.assertIn("middle", boll)
        self.assertIn("lower", boll)
        # upper > middle > lower
        self.assertGreater(boll["upper"], boll["middle"])
        self.assertGreater(boll["middle"], boll["lower"])

    def test_insufficient_data_for_ma120(self):
        """Test with insufficient data for MA120."""
        kline = self.create_kline_data(100)  # Less than 120
        code, stdout, stderr = self.run_script(stdin_data=json.dumps(kline))
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        # MA120 should be 0 when insufficient data
        self.assertEqual(data["MA"]["MA120"], 0.0)

    def test_insufficient_data_for_macd(self):
        """Test with insufficient data for MACD (needs 26+9=35 periods)."""
        kline = self.create_kline_data(30)
        code, stdout, stderr = self.run_script(stdin_data=json.dumps(kline))
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        # MACD should return zeros when insufficient data
        self.assertEqual(data["MACD"]["DIF"], 0.0)
        self.assertEqual(data["MACD"]["DEA"], 0.0)
        self.assertEqual(data["MACD"]["MACD"], 0.0)

    def test_insufficient_data_for_kdj(self):
        """Test with insufficient data for KDJ."""
        kline = self.create_kline_data(10)
        code, stdout, stderr = self.run_script(stdin_data=json.dumps(kline))
        self.assertEqual(code, 0, f"Script failed: {stderr}")
        data = json.loads(stdout)
        # KDJ should return zeros when insufficient data
        self.assertEqual(data["KDJ"]["K"], 0.0)
        self.assertEqual(data["KDJ"]["D"], 0.0)
        self.assertEqual(data["KDJ"]["J"], 0.0)

    def test_empty_input(self):
        """Test with empty input."""
        code, stdout, stderr = self.run_script(stdin_data="")
        self.assertEqual(code, 3)  # Returns no_klines for empty input
        data = json.loads(stdout)
        self.assertEqual(data.get("error"), "no_klines")

    def test_missing_klines_field(self):
        """Test with missing 'klines' field."""
        code, stdout, stderr = self.run_script(stdin_data='{"data": []}')
        self.assertEqual(code, 3)
        data = json.loads(stdout)
        self.assertEqual(data.get("error"), "no_klines")

    def test_empty_klines_array(self):
        """Test with empty klines array."""
        code, stdout, stderr = self.run_script(stdin_data='{"klines": []}')
        self.assertEqual(code, 3)
        data = json.loads(stdout)
        self.assertEqual(data.get("error"), "no_klines")

    def test_invalid_json_input(self):
        """Test with invalid JSON input."""
        code, stdout, stderr = self.run_script(stdin_data="invalid json")
        self.assertEqual(code, 2)
        data = json.loads(stdout)
        self.assertEqual(data.get("error"), "invalid_input")

    def test_missing_required_ohlc_fields(self):
        """Test with missing required OHLC fields."""
        kline = {"klines": [{"open": "100"}]}  # Missing high, low, close
        code, stdout, stderr = self.run_script(stdin_data=json.dumps(kline))
        self.assertEqual(code, 0)
        data = json.loads(stdout)
        # Script returns zeros for all indicators when data is invalid
        self.assertEqual(data["MACD"]["DIF"], 0.0)

    def test_real_kline_data_integration(self):
        """Test with real K-line data from stock_kline.py."""
        # Get real K-line data
        cmd = [sys.executable, "scripts/stock_kline.py", "600519", "240", "120"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            kline_data = json.loads(result.stdout)
            # Pipe to indicators
            code, stdout, stderr = self.run_script(stdin_data=json.dumps(kline_data))
            self.assertEqual(code, 0, f"Script failed: {stderr}")
            data = json.loads(stdout)
            self.assertIn("MA", data)
            self.assertIn("MACD", data)


def run_tests():
    """Run all tests and print summary."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStockIndicators)
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
