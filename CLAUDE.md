# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Invest-Analyzer is a Claude Code Skill for Chinese stock market analysis. It provides real-time quotes, technical indicators (MA/MACD/KDJ/RSI/BOLL), and news fetching through Python scripts that output JSON for AI parsing.

**Important: Every analysis must include both 5-minute K-line (intraday) and daily K-line (trend) analysis.**

## Commands

### Run Tests
```bash
# Run all tests
python3 test/run_all_tests.py

# Run individual test suite
python3 test/test_stock_quote.py
python3 test/test_stock_kline.py
python3 test/test_stock_indicators.py
python3 test/test_stock_search.py
python3 test/test_keyword_expander.py
python3 test/test_news_fetcher.py

# Check external API connectivity
python3 test/third_party_api_checks.py

# Run specific test method
python3 -m unittest test.test_stock_quote.TestStockQuote.test_sh_stock_code_6digit
```

### Run Scripts Manually
```bash
cd scripts

# Search stock by keyword
python3 stock_search.py 贵州茅台
python3 stock_search.py 茅台 --source sina --limit 5

# Get real-time quote
python3 stock_quote.py 600519

# Get K-line data (scale is in minutes)
# 5=5min, 15=15min, 60=1hour, 240=daily (default)
python3 stock_kline.py 600519 5 200    # 5-minute K-line for intraday
python3 stock_kline.py 600519 240 120  # Daily K-line for trend

# Calculate indicators (piped from kline)
python3 stock_kline.py 600519 5 200 | python3 stock_indicators.py
python3 stock_kline.py 600519 240 120 | python3 stock_indicators.py

# Expand keywords for news search
python3 keyword_expander.py --name "贵州茅台" --topic "财报"

# Fetch news (keywords must be English for Google News)
python3 news_fetcher.py --keyword "AAPL" --hours 24 --limit 30
python3 news_fetcher.py --keywords "AAPL,Apple,iPhone" --hours 24
```

## Architecture

### Data Flow
```
User Input → stock_search.py (if name, not code)
          → stock_quote.py (real-time data)
          → stock_kline.py (scale=5 and scale=240) → stock_indicators.py (both timeframes)
          → keyword_expander.py → news_fetcher.py (if news requested)
          → AI generates Markdown report with both intraday and daily analysis
```

### Key Scripts

| Script | Purpose |
|--------|---------|
| `stock_search.py` | Search stock by name/code via Sina/Tencent API |
| `stock_quote.py` | Real-time price/volume via Tencent API |
| `stock_kline.py` | K-line OHLCV data via Sina API (multiple timeframes) |
| `stock_indicators.py` | Calculate MA/MACD/KDJ/RSI/BOLL from stdin JSON |
| `keyword_expander.py` | Generate search keywords from stock name/topic |
| `news_fetcher.py` | Fetch news from Google News RSS |

### K-line Time Scales
| Scale | Meaning | Usage |
|-------|---------|-------|
| `5` | 5-minute | Intraday short-term analysis |
| `15` | 15-minute | Short-term reference |
| `60` | 1-hour | Intraday swing |
| `240` | Daily | Medium/long-term trend (default) |

### External APIs

| API | Purpose |
|-----|---------|
| Sina Suggest API | Stock search |
| Tencent Quote API | Real-time quotes |
| Sina K-line API | Historical OHLCV |
| Google News RSS | Keyword news search |

## Important Conventions

### Stock Code Format
- 6-digit code auto-detects market: `60`/`68` prefix = Shanghai (sh), others = Shenzhen (sz)
- Supports prefixes: `sh600519`, `sz000001`, `SH600519`, `SZ000001`
- Use `normalize_symbol()` in `_utils.py` for conversion

### Dual Timeframe Analysis
Every analysis **must** include both:
1. **5-minute K-line** (`scale=5`) for intraday/short-term analysis
2. **Daily K-line** (`scale=240`) for medium/long-term trend

### News Keywords
- **Must be English** for Google News RSS compatibility
- AI must translate Chinese keywords before calling `news_fetcher.py`
- Example: 贵州茅台 → "Moutai" or "KWE", 财报 → "earnings"

### Piping Pattern
```bash
# Standard pattern: pipe kline to indicators
python3 stock_kline.py 600519 5 200 | python3 stock_indicators.py
python3 stock_kline.py 600519 240 120 | python3 stock_indicators.py
```

### Output Format
- All scripts output JSON with `ensure_ascii=False` for Chinese characters
- Exit codes: 0=success, 1=usage error, 2=invalid input, 3+=runtime errors
- Errors return JSON: `{"error": "message"}`

## Technical Indicators

The `stock_indicators.py` outputs both `history` (array) and `current` (latest value) for each indicator:
- **MA**: 5, 10, 20, 60, 120 periods
- **MACD**: DIF, DEA, MACD histogram
- **KDJ**: K, D, J values
- **RSI**: 6, 12, 24 periods
- **BOLL**: Upper, Middle, Lower bands
- **Volume**: Historical volume data

## Dependencies

Python standard library only - no external packages required:
- `json`, `sys`, `argparse`, `re`, `math`
- `urllib.request`, `urllib.parse`
- `xml.etree.ElementTree`
- `datetime`, `email.utils`

## Documentation

| File | Purpose |
|------|---------|
| `SKILL.md` | AI instruction manual with workflow, script specs, indicator interpretation |
| `SKILL_API.md` | External API documentation with URLs and response formats |
| `README.md` | User guide with installation and usage examples |
| `test/README.md` | Test suite documentation |

## Rating System

Analysis reports use 5-level ratings with specific criteria defined in SKILL.md:
- **Buy**: MA bullish + (MACD golden cross OR RSI oversold bounce OR BOLL breakout with volume) AND no major negatives
- **Add**: 2+ bullish indicators AND no clear negatives
- **Hold**: Mixed indicators, unclear direction
- **Reduce**: 2+ bearish indicators OR broke key support
- **Sell**: MA bearish + (MACD death cross OR RSI overbought decline OR broke BOLL lower band) OR major negative news
