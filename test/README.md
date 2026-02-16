# Test Suite for Invest-Analyzer

This directory contains comprehensive test suites for all invest-analyzer scripts.

## Test Files

| Test File | Script Tested | Test Count | Coverage |
|-----------|--------------|-----------|----------|
| `test_stock_search.py` | `scripts/stock_search.py` | 5 tests | Keyword search, sources, error handling |
| `test_stock_quote.py` | `scripts/stock_quote.py` | 12 tests | All parameters, error handling, data validation |
| `test_stock_kline.py` | `scripts/stock_kline.py` | 17 tests | All scales, counts, stock codes |
| `test_stock_indicators.py` | `scripts/stock_indicators.py` | 16 tests | All indicators, stdin/file input, edge cases |
| `test_keyword_expander.py` | `scripts/keyword_expander.py` | 18 tests | All parameters, deduplication, normalization |
| `test_news_fetcher.py` | `scripts/news_fetcher.py` | 18 tests | Google News keyword search, filtering, time sorting |
| `third_party_api_checks.py` | API connectivity | 3 checks | External API availability |

## Running Tests

### Run All Tests

```bash
# From project root
python3 test/run_all_tests.py

# Or directly
python3 test/test_stock_quote.py
python3 test/test_stock_kline.py
python3 test/test_stock_indicators.py
python3 test/test_stock_search.py
python3 test/test_keyword_expander.py
python3 test/test_news_fetcher.py
```

### Run Individual Test Suites

```bash
# Test stock quote script
python3 test/test_stock_quote.py

# Test stock search script
python3 test/test_stock_search.py

# Test K-line script
python3 test/test_stock_kline.py

# Test indicators script
python3 test/test_stock_indicators.py

# Test keyword expander script
python3 test/test_keyword_expander.py

# Test news fetcher script
python3 test/test_news_fetcher.py

# Check external APIs
python3 test/third_party_api_checks.py
```

### Run Specific Test Cases

```bash
# Run a specific test class
python3 -m unittest test.test_stock_quote.TestStockQuote

# Run a specific test method
python3 -m unittest test.test_stock_quote.TestStockQuote.test_sh_stock_code_6digit
```

## Test Coverage

### stock_quote.py (12 tests)
- ✓ 6-digit stock codes (Shanghai/Shenzhen)
- ✓ Market prefixes (sh/sz/SH/SZ)
- ✓ All required fields (price, volume, OHLC, change)
- ✓ Level-1 quotes (buy/sell orders)
- ✓ Change calculation validation
- ✓ Error handling (invalid codes, missing args)
- ✓ ChiNext board stocks (300xxx)

### stock_kline.py (17 tests)
- ✓ Default parameters
- ✓ All scale options (5/15/30/60/240)
- ✓ Custom count parameters
- ✓ All market prefixes
- ✓ K-line data structure validation
- ✓ OHLCV field types
- ✓ Error handling (invalid codes, scales, counts)

### stock_indicators.py (16 tests)
- ✓ stdin and file input methods
- ✓ MA calculation (5/10/20/60/120 periods)
- ✓ MACD calculation (DIF, DEA, MACD relationship)
- ✓ KDJ calculation (K, D, J relationship)
- ✓ RSI calculation (6/12/24 periods, 0-100 range)
- ✓ BOLL calculation (upper > middle > lower)
- ✓ Insufficient data handling
- ✓ Invalid input handling
- ✓ Real data integration with stock_kline.py

### keyword_expander.py (18 tests)
- ✓ Code-only mode (base keywords)
- ✓ Chinese topic expansion
- ✓ English topic expansion
- ✓ Mixed Chinese/English topics
- ✓ Extra keywords parameter
- ✓ Multiple term handling (comma/newline separators)
- ✓ Stock code normalization
- ✓ Deduplication
- ✓ Order preservation
- ✓ Whitespace handling
- ✓ Error handling (invalid codes)

### news_fetcher.py (18 tests)
- ✓ Single/multiple keywords
- ✓ All parameters (--hours, --limit)
- ✓ Item structure validation
- ✓ Time-based filtering
- ✓ Duplicate removal
- ✓ Chinese keywords
- ✓ Google News integration
- ✓ No helper fields in output
- ✓ Count field accuracy
- ✓ Error handling (missing keywords)

### stock_search.py (5 tests)
- ✓ Keyword search (default source)
- ✓ Source selection (sina/tencent)
- ✓ Result structure validation
- ✓ Error handling (missing args, blank keyword)

### third_party_api_checks.py (3 checks)
- ✓ Tencent Quote API
- ✓ Sina K-line API
- ✓ Google News RSS

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)
- Network connection for API tests

## Test Output Format

Each test suite provides:
1. Individual test results with pass/fail status
2. Summary with total tests, successes, failures, and errors
3. Exit code 0 if all pass, non-zero if any fail

Example:
```
test_sh_stock_code_6digit (__main__.TestStockQuote.test_sh_stock_code_6digit) ... ok
test_sz_stock_code_6digit (__main__.TestStockQuote.test_sz_stock_code_6digit) ... ok

----------------------------------------------------------------------
Ran 12 tests in 2.396s

OK

================================================================================
Tests run: 12
Successes: 12
Failures: 0
Errors: 0
================================================================================
```

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    python3 test/run_all_tests.py
```

## Adding New Tests

When adding new features or scripts:
1. Create a new test file following the naming pattern `test_<script_name>.py`
2. Use `unittest.TestCase` class structure
3. Include tests for all parameters and edge cases
4. Add the new test to `run_all_tests.py`
5. Update this README with coverage details
