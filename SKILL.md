---
name: invest-analyzer
version: 1.0.0
description: Investment analysis skill spec for quotes, technical indicators, and news.
---

# Skill Spec: Stock Analysis

## 1. Skill Structure
1. Entry: users chat with the AI in the command line.
1. Input constraint: users can provide a stock code or stock name; stock names should be resolved via keyword search.
1. Data access: the AI calls scripts in this directory to fetch structured data.
1. Output: the AI generates structured Markdown results.
1. Scope constraints: no sector analysis; users never call scripts directly, only the AI does.

## 2. Script Inventory

### 2.1 Stock search (`scripts/stock_search.py`)
- **Purpose**: search stock code by keyword (stock name or partial code).

**Usage:**
```bash
python3 stock_search.py <keyword> [--source auto|sina|tencent] [--limit N]
```

**Parameters:**
- `keyword` (required): Stock name or keyword
- `--source` (optional): `auto` (default), `sina`, or `tencent`
- `--limit` (optional): Max results, default `10`, max `50`

**Examples:**
```bash
python3 stock_search.py 贵州茅台
python3 stock_search.py 茅台 --source sina
python3 stock_search.py 6005 --limit 5
```

**Output (JSON):**
```json
{
  "keyword": "贵州茅台",
  "source": "sina",
  "count": 1,
  "items": [
    {
      "name": "贵州茅台",
      "code": "600519",
      "symbol": "sh600519",
      "market": "SH",
      "type": "stock"
    }
  ]
}
```

### 2.2 Real-time quote (`scripts/stock_quote.py`)
- **Purpose**: fetch current price, change, volume, and level-1 quotes.

**Usage:**
```bash
python3 stock_quote.py <stock_code>
```

**Parameters:**
- `stock_code` (required): Stock code in 6-digit format
  - Supports: `600519`, `sh600519`, `sz000001`
  - Auto-detects market prefix (sh for 60/68, sz for others)

**Examples:**
```bash
python3 stock_quote.py 600519
python3 stock_quote.py sh600519
python3 stock_quote.py sz000001
```

**Output (JSON):**
```json
{
  "name": "贵州茅台",
  "code": "600519",
  "symbol": "sh600519",
  "current": 1680.00,
  "prev_close": 1670.00,
  "open": 1675.00,
  "high": 1690.00,
  "low": 1670.00,
  "volume": 2500000,
  "change": 10.00,
  "pct_change": 0.60,
  "buy1_p": 1679.50,
  "buy1_v": 100,
  "sell1_p": 1680.50,
  "sell1_v": 200,
  ...
}
```

### 2.3 K-line data (`scripts/stock_kline.py`)
- **Purpose**: fetch K-line data for indicator calculation.

**Usage:**
```bash
python3 stock_kline.py <stock_code> [scale] [count]
```

**Parameters:**
- `stock_code` (required): Stock code (same format as stock_quote.py)
- `scale` (optional): K-line time period (default: `240`)
  - Common values: `5`=5min, `15`=15min, `30`=30min, `60`=1hour, `240`=daily
- `count` (optional): Number of data points to fetch (default: `120`)

**Examples:**
```bash
# Daily K-line, 120 periods (default)
python3 stock_kline.py 600519

# 5-minute K-line, 200 periods
python3 stock_kline.py 600519 5 200

# 1-hour K-line, 150 periods
python3 stock_kline.py 600519 60 150
```

**Output (JSON):**
```json
{
  "symbol": "sh600519",
  "scale": 240,
  "count": 120,
  "klines": [
    {
      "open": "1670.00",
      "high": "1690.00",
      "low": "1665.00",
      "close": "1680.00",
      "volume": "2500000"
    },
    ...
  ]
}
```

### 2.4 Technical indicators (`scripts/stock_indicators.py`)
- **Purpose**: compute MA/MACD/KDJ/RSI/BOLL from K-line data.

**Usage:**
```bash
# Method 1: Pipe JSON from stdin
python3 stock_kline.py 600519 | python3 stock_indicators.py

# Method 2: Read from file
python3 stock_indicators.py --file kline_data.json
```

**Parameters:**
- `--file <path>` (optional): Read K-line JSON from file instead of stdin
- **Input format** (stdin or file):
```json
{
  "klines": [
    {
      "open": "1670.00",
      "high": "1690.00",
      "low": "1665.00",
      "close": "1680.00"
    },
    ...
  ]
}
```

**Examples:**
```bash
# Direct pipe from K-line script
python3 stock_kline.py 600519 | python3 stock_indicators.py

# From saved file
python3 stock_kline.py 600519 > /tmp/kline.json
python3 stock_indicators.py --file /tmp/kline.json
```

**Output (JSON):**
```json
{
  "MA": {
    "MA5": 1675.20,
    "MA10": 1672.50,
    "MA20": 1670.80,
    "MA60": 1665.40,
    "MA120": 1660.20
  },
  "MACD": {
    "DIF": 5.23,
    "DEA": 4.18,
    "MACD": 2.10
  },
  "KDJ": {
    "K": 65.20,
    "D": 60.15,
    "J": 75.30
  },
  "RSI": {
    "RSI6": 58.20,
    "RSI12": 55.40,
    "RSI24": 52.80
  },
  "BOLL": {
    "upper": 1690.50,
    "middle": 1675.20,
    "lower": 1659.90
  }
}
```

### 2.5 Keyword expander (`scripts/keyword_expander.py`)
- **Purpose**: generate news search keywords from stock code + optional topic.

**Usage:**
```bash
python3 keyword_expander.py --code <stock_code> [--topic <text>] [--topic-en <text>] [--extra "a,b,c"]
```

**Parameters:**
- `--code` (required): Stock code (6-digit format, auto-normalizes)
- `--topic` (optional): Chinese or mixed topic text
- `--topic-en` (optional): English topic text (AI-provided translation)
- `--extra` (optional): Comma-separated extra keywords

**Examples:**
```bash
# Basic keywords only (stock code + generic terms)
python3 keyword_expander.py --code 600519

# With Chinese topic
python3 keyword_expander.py --code 600519 --topic "财报,业绩"

# With English topic (AI translation)
python3 keyword_expander.py --code 600519 --topic-en "earnings,revenue"

# Combined with extra keywords
python3 keyword_expander.py --code 600519 --topic "并购" --extra "重组,资产"
```

**Output (JSON):**
```json
{
  "keywords": [
    "600519",
    "600519 股票",
    "600519 公司",
    "财报",
    "600519 财报",
    "600519 相关 财报",
    "业绩",
    "600519 业绩",
    "600519 相关 业绩"
  ]
}
```

### 2.6 News fetcher (`scripts/news_fetcher.py`)
- **Purpose**: fetch news items within the last 24 hours by keyword or hotspot feeds.

**Usage:**
```bash
# Keyword search mode
python3 news_fetcher.py --mode keyword --keyword "<single_keyword>" --hours 24 --limit 30

# Multiple keywords
python3 news_fetcher.py --mode keyword --keywords "AAPL,Apple,iPhone" --hours 24 --limit 30

# Hotspot feeds mode
python3 news_fetcher.py --mode hot --hours 24 --limit 30
```

**Parameters:**
- `--mode` (optional): Search mode, either `keyword` or `hot` (default: `keyword`)
- `--keyword` (optional): Single keyword for search
- `--keywords` (optional): Comma-separated keywords for search
- `--hours` (optional): Time window in hours (default: `24`)
- `--limit` (optional): Max news items per keyword/feed (default: `30`)

**Note**: In `keyword` mode, either `--keyword` or `--keywords` must be provided.

**Examples:**
```bash
# Single keyword search (last 24 hours)
python3 news_fetcher.py --mode keyword --keyword "600519"

# Multiple keywords (comma-separated)
python3 news_fetcher.py --mode keyword --keywords "600519,贵州茅台,财报"

# Extended time window (7 days)
python3 news_fetcher.py --mode keyword --keywords "AAPL" --hours 168

# Hotspot feeds from predefined sources
python3 news_fetcher.py --mode hot --hours 12

# Custom limit
python3 news_fetcher.py --mode keyword --keywords "600519" --limit 50
```

**Hotspot feeds (when `--mode hot`):**
- Hacker News
- Reddit r/finance
- Reddit r/investing
- BBC Business
- CNBC
- Baidu Finance
- Baidu Stock

**Output (JSON):**
```json
{
  "items": [
    {
      "title": "Stock Market Hits Record High",
      "link": "https://example.com/article1",
      "source": "Google News",
      "time": "Tue, 05 Feb 2026 10:30:00 GMT"
    },
    {
      "title": "Corporate Earnings Report Released",
      "link": "https://example.com/article2",
      "source": "Baidu Finance",
      "time": "2026-02-05T08:15:00Z"
    }
  ],
  "count": 2
}
```

## 3. AI Usage Guide

### 3.1 Input Validation
- If input is a 6-digit stock code, proceed directly.
- If input is a stock name or keyword, call `stock_search.py` to resolve candidate codes.
- If multiple candidates are returned, ask the user to confirm the intended stock code.

### 3.2 Core Analysis Flow
1. Call `stock_quote.py` to get current price and basic data.
2. Call `stock_kline.py` to fetch K-line data.
3. Call `stock_indicators.py` to compute technical indicators.

### 3.3 News Search Trigger Conditions
Only trigger news search when the user explicitly or implicitly requests it:

**Explicit triggers**:
- "news", "消息", "资讯", "新闻"
- "events", "事件"
- "headlines", "头条"
- "situation", "情况"
- "combine news", "结合新闻"

**Implicit triggers**:
- "recent international situation", "recent macro environment"
- Any request implying context or background information

### 3.4 Keyword Generation Rules
- **With topic**: Generate keywords from `[stock_code] + [topic]`. Translate topic to English for English-centric sources via `--topic-en`.
- **Without topic** (generic news): Use `[stock_code] + generic finance terms`:
  - Examples: `"股票代码,财报,业绩,公告"` or `"股票代码,financial,earnings,announcement"`
  - Maximum 4-5 keywords per request.

### 3.5 News Script Invocation
- Use `--keywords` with a comma-separated list: `--keywords "AAPL,Apple,iPhone"`
- Do NOT concatenate keywords into a single phrase.

### 3.6 News Output Format
- Translate original English titles into Chinese.
- Provide a one-line Chinese summary for each news item.
- Include impact assessment (positive/negative/neutral).

### 3.7 Error Handling
- **Invalid stock code**: Inform the user and ask for a valid code.
- **Network/API failure**: Retry once, then inform the user of the issue and proceed with available data.
- **No news found**: State "No relevant news found in the past 24 hours" and continue with other sections.

### 3.8 Output Structure
Output Markdown including:
- Stock basics (quote data)
- Technical indicator analysis
- News list and impact (if triggered)

## 4. Technical Indicator Interpretation Rules

### 4.1 Trend Indicators (MA)
- **Bullish**: Short-term MA > Long-term MA (e.g., MA5 > MA20 > MA60)
- **Bearish**: Short-term MA < Long-term MA
- **Crossover**: Golden cross (MA5 crosses above MA20) = buy signal; Death cross = sell signal

### 4.2 Momentum Indicators (MACD, KDJ, RSI)
- **MACD**:
  - DIF > DEA: bullish
  - DIF < DEA: bearish
  - MACD > 0: upward momentum
  - MACD < 0: downward momentum
- **KDJ**:
  - K > D > J: overbought zone, potential pullback
  - K < D < J: oversold zone, potential rebound
  - J > 100 or J < 0: extreme overbought/oversold
- **RSI**:
  - RSI > 70: overbought
  - RSI < 30: oversold
  - RSI 50 as equilibrium

### 4.3 Volatility Indicators (BOLL)
- **Price position**:
  - Above upper band: strong uptrend, watch for pullback
  - Within bands: normal trading range
  - Below lower band: strong downtrend, watch for rebound
- **Band width**: Narrowing = consolidation; Widening = trend forming

## 5. Rating & Risk Assessment Rules

### 5.1 Rating System
Based on technical indicator consensus and news sentiment:

| Rating | Condition |
|--------|-----------|
| **买入 (Buy)** | - MA呈多头排列 (MA5 > MA20 > MA60) AND (MACD金叉 OR RSI < 30回升 OR 突破BOLL上轨) AND 无重大利空新闻 |
| **增持 (Accumulate)** | - 至少2个趋势/动能指标看涨 AND 无明确利空 OR 技术面偏强但存在不确定性 |
| **持有 (Hold)** | - 指标多空交织，方向不明 OR 震荡整理中 OR 等待突破信号 |
| **减持 (Reduce)** | - 至少2个趋势/动能指标看弱 OR 跌破关键支撑位 OR 存在潜在风险 |
| **卖出 (Sell)** | - MA呈空头排列 (MA5 < MA20 < MA60) AND (MACD死叉 OR RSI > 70回落 OR 跌破BOLL下轨) OR 重大利空新闻 |

**特殊情况**：
- 如果没有新闻数据，仅依据技术指标评级
- 如果有重大新闻事件，新闻权重 > 技术指标

### 5.2 Risk Note Generation
Always include relevant risk warnings based on:
- **Technical risks**: RSI超买/超卖、BOLL极端位置、量价背离
- **News risks**: 政策变化、业绩预警、法律诉讼、监管风险
- **Market risks**: 大盘走势、行业波动、汇率/利率影响

**Template for risk note**:
```
• [技术面风险描述]
• [新闻面风险描述，如无则省略]
• 投资有风险，以上分析仅供参考，不构成投资建议
```

## 6. Related Docs
- `SKILL_API.md`

## 7. Fixed Markdown Output Template (Research Style)
The AI must follow this structure and headings exactly.

### 7.1 Conditional Section Rules
- **Section 4 (资讯与影响)**: Only include if news search was triggered. If triggered but no news found, display: `| - | - | - | 过去24小时无相关新闻 | - | - |`

### 7.2 Output Template

```
# 股票分析报告｜{股票代码} {股票名称}

## 一、摘要
| 维度 | 内容 |
|---|---|
| 当前价格 | {price} |
| 当日涨跌 | {change}（{pct_change}%） |
| 评级 | {rating} |
| 操作建议 | {one_line_conclusion} |

## 二、行情与走势
| 指标 | 数值 |
|---|---|
| 开盘/最高/最低 | {open} / {high} / {low} |
| 昨收 | {prev_close} |
| 成交量 | {volume} |
| 成交额 | {amount} |

## 三、技术指标
### 3.1 趋势类
| 指标 | 数值 | 解读 |
|---|---|---|
| MA5/10/20 | {ma5} / {ma10} / {ma20} | {ma_note} |
| MA60/120 | {ma60} / {ma120} | {ma_long_note} |

### 3.2 动能类
| 指标 | 数值 | 解读 |
|---|---|---|
| MACD | DIF {dif}, DEA {dea}, MACD {macd} | {macd_note} |
| KDJ | K {k}, D {d}, J {j} | {kdj_note} |
| RSI | RSI6 {rsi6}, RSI12 {rsi12}, RSI24 {rsi24} | {rsi_note} |

### 3.3 波动类
| 指标 | 数值 | 解读 |
|---|---|---|
| BOLL | 上 {boll_upper} / 中 {boll_mid} / 下 {boll_lower} | {boll_note} |

## 四、资讯与影响
| 时间 | 来源 | 主题标签 | 标题 | 摘要 | 影响判断 |
|---|---|---|---|---|---|
| {time} | {source} | {topic_tag} | {title_cn} | {summary_cn} | {impact} |

## 五、综合判断
### 5.1 技术面总结
{technical_summary}

### 5.2 结论与风险提示
| 项目 | 内容 |
|---|---|
| 投资建议 | {investment_advice} |
| 风险提示 | {risk_note} |
```
