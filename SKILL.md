---
name: invest-analyzer
version: 2.0.0
description: 投资分析工具 - 行情、技术指标
---

# 股票分析 Skill

## 一、工作流程

1. 用户输入股票代码或名称
2. AI 调用 `scripts/` 下脚本获取数据
3. AI 输出 Markdown 分析报告（**必须包含日线 + 5分钟双周期分析**）

## 二、脚本列表

### 2.1 股票搜索 (`stock_search.py`)

```bash
python3 stock_search.py <关键词> [--source auto|sina|tencent] [--limit N]
```

输出 `items[]`：`name, code, symbol, market, type`。多结果时需用户确认。

### 2.2 实时行情 (`stock_quote.py`)

```bash
python3 stock_quote.py <股票代码>  # 支持 600519 / sh600519 / sz000001
```

输出：`name, code, symbol, current, prev_close, open, high, low, volume, amount, change, pct_change`

### 2.3 K线数据 (`stock_kline.py`)

```bash
python3 stock_kline.py <股票代码> [scale] [count]  # 默认 scale=240, count=120
```

| scale | 含义 | 用途 |
|-------|------|------|
| 5 | 5分钟 | 日内短线 |
| 15 | 15分钟 | 短线参考 |
| 60 | 60分钟 | 日内波段 |
| 240 | 日K（默认） | 中长期趋势 |

输出 `klines[]`：`open, high, low, close, volume`（均为字符串）

### 2.4 技术指标 (`stock_indicators.py`)

```bash
python3 stock_kline.py 600519 5 200 | python3 stock_indicators.py   # 管道输入
python3 stock_indicators.py --file kline.json                      # 文件输入
```

各指标输出 `history`（序列）+ `current`（当前值）：

| 指标 | 输出字段 |
|------|----------|
| MA | MA5, MA10, MA20, MA60, MA120 |
| MACD | DIF, DEA, MACD |
| KDJ | K, D, J |
| RSI | RSI6, RSI12, RSI24（Wilder smoothing） |
| BOLL | upper, middle, lower |
| volume | history, current |
| VOL_MA | VOL_MA5, VOL_MA10, VOL_MA20 |
| OBV | history, current（能量潮，量价背离检测） |
| PCT_CHANGE | history, current（每根K线涨跌幅%） |

### 2.5 技术面评级 (`stock_technical_analysis.py`)

```bash
python3 stock_technical_analysis.py --file technical_payload.json
```

- 输入：`{quote: {...}, daily: {klines, indicators}, intraday: {klines, indicators}}`
- 输出：`technical_rating, technical_score, daily: {bias, score}, intraday: {bias, score}, bullish_signals[], bearish_signals[], one_line_conclusion`

### 2.6 一键技术快照 (`stock_technical_snapshot.py`) ← 主入口，优先使用

```bash
python3 stock_technical_snapshot.py 600519 [--daily-count 120] [--intraday-count 200]
```

一次调用聚合 quote + 双周期 K线 + 指标 + 技术评级。**优先调用此脚本，失败再分步调用 2.1-2.5。**

## 三、AI 使用指南

### 3.1 输入处理

- 6位数字代码 → 直接使用
- 股票名称/关键词 → `stock_search.py` 查询，多结果时确认

### 3.2 核心流程

```
用户输入 → stock_search.py（若非代码）
         → stock_technical_snapshot.py（主入口）
         → 若失败则分步：quote → kline|indicators × 2 → technical_analysis
         → 输出 Markdown 报告
```

### 3.3 错误处理

- 无效代码：提示重新输入
- API 失败：重试一次，失败后告知并继续

## 四、技术指标解读规则

### 4.1 MA（趋势）

- **多头排列**：MA5 > MA20 > MA60 → 看涨；**空头排列**：短期 < 长期 → 看跌
- **金叉**：MA5 上穿 MA20（history 序列中从低变高）→ 买入信号
- **死叉**：MA5 下穿 MA20 → 卖出信号
- 价 > MA5 短期强势；> MA20 中期强势；< MA60 中期偏弱
- 斜率变大趋势加速，变小趋势减缓

### 4.2 MACD（动能）

- DIF > DEA / MACD > 0 → 看涨；反之看跌
- **金叉**：DIF 上穿 DEA → 买入；**死叉**：DIF 下穿 DEA → 卖出
- **顶背离**：价新高 DIF 未新高 → 看跌；**底背离**：价新低 DIF 未新低 → 看涨

### 4.3 KDJ（超买超卖）

- K > D 看涨；K < D 看跌
- K > 80 超买风险区；K < 20 超卖机会区
- J > 100 极端超买（警惕回调）；J < 0 极端超卖（可能反弹）
- K-D 差值扩大 → 趋势强化

### 4.4 RSI（强弱）

- \> 70 超买；< 30 超卖；50 多空分界；30-70 正常波动
- 顶背离看跌；底背离看涨

### 4.5 BOLL（波动）

- 上轨上方 → 强势突破，注意回调；中轨附近 → 震荡；下轨下方 → 弱势，关注反弹
- 带宽 = (上轨 - 下轨) / 中轨 × 100%；收窄 → 即将突破；扩张 → 趋势形成

### 4.6 量价关系

- 量增价涨（健康上涨）/ 量增价跌（抛压加重）/ 量缩价涨（上涨乏力）/ 量缩价跌（空头衰竭）
- 量价背离（价创新高/低但量未配合）→ 警惕反转
- 放量 = 成交量 > 5日均量；缩量 = < 5日均量

### 4.7 量价形态信号

| 信号 | 方向 | 含义 |
|------|------|------|
| `volume_stagnation` | 空 | 放量滞涨：量比>1.5，价格几乎不动 |
| `mild_volume_stagnation` | 空 | 温和放量滞涨：量比>1.2，涨跌幅<0.3% |
| `obv_bearish_divergence` | 空 | OBV顶背离：价新高但OBV未新高 |
| `obv_bullish_divergence` | 多 | OBV底背离：价新低但OBV未新低 |
| `shrinking_volume_rise` | 空 | 缩量上涨：价涨量缩，动能不足 |
| `volume_breakout` | 多 | 放量突破：量比>2且上穿MA20 |
| `pullback_ma{N}_support` | 多 | 回踩均线支撑：价贴近MA且MA上升，缩量加分 |
| `pullback_boll_mid_support` | 多 | 回踩BOLL中轨支撑 |
| `ma{N}_breakdown` | 空 | 均线支撑破位：价跌破此前支撑的均线 |

### 4.8 日内分析

- 阳线（收>开）多头占优；阴线（收<开）空头占优
- 振幅 = (最高-最低)/昨收 × 100%；>5% 剧烈，2-5% 正常，<2% 窄幅

## 五、评级标准

| 评级 | 条件 |
|------|------|
| **买入** | 日线+5分钟同时偏多，MA多头 AND（MACD金叉 OR RSI超卖回升 OR BOLL上轨放量 OR OBV底背离 OR 放量突破） |
| **增持** | 日线偏多 + 5分钟偏多/震荡 |
| **持有** | 多空交织，方向不明 |
| **减持** | 日线偏弱 + 5分钟偏弱/震荡 |
| **卖出** | 日线+5分钟同时偏弱，MA空头 AND（MACD死叉 OR RSI超买回落 OR BOLL下轨放量 OR OBV顶背离 OR 放量滞涨） |

- `bias`：score >= 3 为 bullish，<= -3 为 bearish，其余 neutral
- 背离信号优先于单一指标；量价配合验证信号有效性

## 六、输出模板

严格按以下结构输出，**必须包含日线（scale=240）和5分钟（scale=5）双周期分析**：

```markdown
# 股票分析报告｜{code} {name}

## 一、摘要
| 维度 | 内容 |
|---|---|
| 当前价格 | {price} |
| 当日涨跌 | {change}（{pct_change}%） |
| 技术评级 | {rating} |
| 操作建议 | {one_line_conclusion} |

## 二、行情概览
| 指标 | 数值 |
|---|---|
| 开盘/最高/最低 | {open} / {high} / {low} |
| 昨收 | {prev_close} |
| 成交量/额 | {volume} / {amount} |
| 振幅 | {amplitude}% |

## 三、日线技术分析（scale=240）
### 趋势类
| 指标 | 数值 | 解读 |
|---|---|---|
| MA5/10/20 | {ma5} / {ma10} / {ma20} | {ma_note} |
| MA60/120 | {ma60} / {ma120} | {ma_long_note} |

### 动能类
| 指标 | 数值 | 解读 |
|---|---|---|
| MACD | DIF {dif}, DEA {dea}, MACD {macd} | {macd_note} |
| KDJ | K {k}, D {d}, J {j} | {kdj_note} |
| RSI | RSI6 {rsi6}, RSI12 {rsi12}, RSI24 {rsi24} | {rsi_note} |

### 波动类
| 指标 | 数值 | 解读 |
|---|---|---|
| BOLL | 上 {upper} / 中 {mid} / 下 {lower} | {boll_note} |

### 量价
| 指标 | 数值 | 解读 |
|---|---|---|
| 成交量 | {volume} | {volume_note} |

## 四、5分钟短线分析（scale=5）
### 趋势类
| 指标 | 数值 | 解读 |
|---|---|---|
| MA5/10/20 | {5m_ma5} / {5m_ma10} / {5m_ma20} | {5m_ma_note} |

### 动能类
| 指标 | 数值 | 解读 |
|---|---|---|
| MACD | DIF {5m_dif}, DEA {5m_dea}, MACD {5m_macd} | {5m_macd_note} |
| KDJ | K {5m_k}, D {5m_d}, J {5m_j} | {5m_kdj_note} |
| RSI | RSI6 {5m_rsi6}, RSI12 {5m_rsi12} | {5m_rsi_note} |

### 波动类
| 指标 | 数值 | 解读 |
|---|---|---|
| BOLL | 上 {5m_upper} / 中 {5m_mid} / 下 {5m_lower} | {5m_boll_note} |

### 日内走势解读
{intraday_analysis}

## 五、综合判断
### 技术面总结
{technical_summary}

### 结论与风险提示
| 项目 | 内容 |
|---|---|
| 综合建议 | {结合评级、双周期趋势、量价配合给出操作建议} |
| 风险提示 | {技术面风险 + 市场风险} |
```
