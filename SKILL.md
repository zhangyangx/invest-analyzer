---
name: invest-analyzer
version: 1.0.0
description: 投资分析工具 - 行情、技术指标与新闻资讯
---

# 股票分析 Skill

## 一、工作流程

1. 用户输入股票代码或股票名称
2. AI 调用 scripts 目录下的脚本获取数据
3. AI 输出结构化的 Markdown 分析报告

## 二、脚本列表

### 2.1 股票搜索 (`scripts/stock_search.py`)

根据关键词搜索股票代码。

**用法：**
```bash
python3 stock_search.py <关键词> [--source auto|sina|tencent] [--limit N]
```

**参数：**
- `keyword`（必填）：股票名称或代码
- `--source`（可选）：`auto`（默认）、`sina`、`tencent`
- `--limit`（可选）：最大结果数，默认 10，最多 50

**示例：**
```bash
python3 stock_search.py 贵州茅台
python3 stock_search.py 茅台 --source sina
python3 stock_search.py 6005 --limit 5
```

**输出（JSON）：**
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

---

### 2.2 实时行情 (`scripts/stock_quote.py`)

获取当前价格、涨跌幅、成交量等实时数据。

**用法：**
```bash
python3 stock_quote.py <股票代码>
```

**参数：**
- `stock_code`（必填）：6 位股票代码
  - 支持格式：`600519`、`sh600519`、`sz000001`
  - 自动识别市场前缀（60/68 开头为 sh，其他为 sz）

**示例：**
```bash
python3 stock_quote.py 600519
python3 stock_quote.py sh600519
```

**输出（JSON）：**
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
  "pct_change": 0.60
}
```

---

### 2.3 K线数据 (`scripts/stock_kline.py`)

获取 K 线数据用于计算技术指标。

**用法：**
```bash
python3 stock_kline.py <股票代码> [周期] [数量]
```

**参数：**
- `stock_code`（必填）：股票代码
- `scale`（可选）：K 线周期，默认 `240`
  - 常用值：`5`=5分、`15`=15分、`60`=1小时、`240`=日线
- `count`（可选）：数据条数，默认 `120`

**示例：**
```bash
python3 stock_kline.py 600519
python3 stock_kline.py 600519 5 200
python3 stock_kline.py 600519 60 150
```

**输出（JSON）：**
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
    }
  ]
}
```

---

### 2.4 技术指标 (`scripts/stock_indicators.py`)

根据 K 线数据计算 MA/MACD/KDJ/RSI/BOLL 指标。

**用法：**
```bash
# 方法 1：从标准输入读取 K 线数据
python3 stock_kline.py 600519 | python3 stock_indicators.py

# 方法 2：从文件读取
python3 stock_indicators.py --file kline_data.json
```

**参数：**
- `--file <path>`（可选）：从文件读取 K 线 JSON

**输出（JSON）：**
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

---

### 2.5 关键词扩展 (`scripts/keyword_expander.py`)

根据股票名称和主题生成新闻搜索关键词。

**用法：**
```bash
python3 keyword_expander.py --name <股票名称> [--topic <文本>] [--topic-en <文本>]
```

**参数：**
- `--name`（必填）：股票名称
- `--topic`（可选）：中文主题
- `--topic-en`（可选）：英文主题（AI 翻译提供）
- `--extra`（可选）：额外关键词，逗号分隔

**示例：**
```bash
python3 keyword_expander.py --name 贵州茅台
python3 keyword_expander.py --name "贵州茅台" --topic "财报,业绩"
python3 keyword_expander.py --name "贵州茅台" --topic-en "earnings"
```

**输出（JSON）：**
```json
{
  "keywords": [
    "贵州茅台",
    "贵州茅台 股票",
    "贵州茅台 公司",
    "财报",
    "贵州茅台 财报"
  ]
}
```

---

### 2.6 新闻获取 (`scripts/news_fetcher.py`)

获取最近 24 小时内的相关新闻。

**用法：**
```bash
# 关键词搜索模式
python3 news_fetcher.py --mode keyword --keyword "<关键词>" --hours 24 --limit 30

# 多关键词搜索
python3 news_fetcher.py --mode keyword --keywords "AAPL,Apple,iPhone" --hours 24

# 热点源模式
python3 news_fetcher.py --mode hot --hours 24
```

**参数：**
- `--mode`（可选）：`keyword` 或 `hot`（热点源），默认 `keyword`
- `--keyword`（可选）：单个关键词
- `--keywords`（可选）：逗号分隔的多个关键词
- `--hours`（可选）：时间窗口（小时），默认 24
- `--limit`（可选）：最大新闻数，默认 30

**热点源包括：** Hacker News、Reddit 财经板块、BBC Business、CNBC、百度财经等

**输出（JSON）：**
```json
{
  "items": [
    {
      "title": "Stock Market Hits Record High",
      "link": "https://example.com/article1",
      "source": "Google News",
      "time": "Tue, 05 Feb 2026 10:30:00 GMT"
    }
  ],
  "count": 1
}
```

## 三、AI 使用指南

### 3.1 输入验证
- 6 位数字股票代码 → 直接处理
- 股票名称或关键词 → 调用 `stock_search.py` 解析
- 多个搜索结果 → 询问用户确认

### 3.2 核心分析流程
1. 调用 `stock_quote.py` 获取实时行情
2. 调用 `stock_kline.py` 获取 K 线数据
3. 调用 `stock_indicators.py` 计算技术指标

### 3.3 新闻搜索触发条件

仅在用户明确或隐式要求时触发新闻搜索：

**明确触发词：**
- 新闻、消息、资讯、事件、头条、情况

**隐式触发：**
- 询问最近国际形势、宏观环境、背景信息等

### 3.4 关键词生成规则
- 使用 `keyword_expander.py --name <股票名称>` 生成搜索关键词
- **有主题**：添加 `--topic <主题>` 或 `--topic-en <英文主题>`
- **无主题**：脚本自动生成股票名称+通用财经词汇的组合
- 每次请求最多 4-5 个关键词

### 3.5 新闻输出要求
- 英文标题翻译成中文
- 每条新闻提供一行中文摘要
- 标注影响判断（正面/负面/中性）

### 3.6 错误处理
- **无效股票代码**：提示用户并要求重新输入
- **网络/API 失败**：重试一次，失败后告知用户并继续使用已有数据
- **无新闻**：显示"过去 24 小时无相关新闻"并继续其他部分

## 四、技术指标解读规则

### 4.1 趋势指标（MA）
- **多头排列**：短期 MA > 长期 MA（MA5 > MA20 > MA60），看涨
- **空头排列**：短期 MA < 长期 MA，看跌
- **金叉**：MA5 上穿 MA20，买入信号
- **死叉**：MA5 下穿 MA20，卖出信号

### 4.2 动能指标（MACD、KDJ、RSI）
- **MACD**：
  - DIF > DEA：看涨
  - DIF < DEA：看跌
  - MACD > 0：上涨动能
  - MACD < 0：下跌动能
- **KDJ**：
  - K > D > J：超买区，可能回调
  - K < D < J：超卖区，可能反弹
  - J > 100 或 J < 0：极端超买/超卖
- **RSI**：
  - RSI > 70：超买
  - RSI < 30：超卖
  - RSI 50 为平衡点

### 4.3 波动指标（BOLL）
- **价格位置**：
  - 上轨上方：强势上涨，注意回调
  - 轨道内：正常震荡
  - 下轨下方：强势下跌，关注反弹
- **带宽**：收窄=盘整；扩张=趋势形成

## 五、评级与风险评估

### 5.1 评级标准

基于技术指标共识和新闻情绪：

| 评级 | 条件 |
|------|------|
| **买入** | MA 多头排列 AND（MACD 金叉 OR RSI 超卖回升 OR 突破 BOLL 上轨）AND 无重大利空 |
| **增持** | 至少 2 个趋势/动能指标看涨 AND 无明确利空 |
| **持有** | 指标多空交织，方向不明或震荡整理 |
| **减持** | 至少 2 个趋势/动能指标看弱 OR 跌破关键支撑 |
| **卖出** | MA 空头排列 AND（MACD 死叉 OR RSI 超买回落 OR 跌破 BOLL 下轨）OR 重大利空 |

**注：** 重大新闻事件权重 > 技术指标

### 5.2 风险提示
根据以下因素生成相关风险提示：
- **技术面风险**：RSI 超买/超卖、BOLL 极端位置、量价背离
- **新闻面风险**：政策变化、业绩预警、法律诉讼、监管风险
- **市场风险**：大盘走势、行业波动、汇率/利率影响

## 六、输出模板

AI 必须严格按以下结构输出 Markdown 报告：

```markdown
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

**注：** 第四部分「资讯与影响」仅在触发新闻搜索时包含。如触发但无新闻，显示：`| - | - | - | 过去24小时无相关新闻 | - | - |`
