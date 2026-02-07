# 需求到接口映射
| 需求 | 主接口 | 备用接口 |
| --- | --- | --- |
| **股票基础行情**   （现价、涨跌、量价等） | 新浪行情接口 | 腾讯行情接口 |
| **股票搜索**   （按关键词） | 新浪搜索接口 | 腾讯搜索接口 |
| **K 线数据**   （技术指标计算所需原始数据） | 新浪 K 线接口 | - |
| **资讯获取**   （按关键词或热点，24 小时内） | Google News RSS   RSS 聚合源   百度 RSS | - |


# 接口清单与说明
## 实时行情
### 新浪行情接口
| 项目 | 说明 |
| --- | --- |
| **目的** | 获取股票当前价、涨跌幅、成交量等 |
| **请求方式** | `HTTPS GET` |
| **URL** | `https://hq.sinajs.cn/list={symbol}` |
| **关键参数** | `symbol` - 股票代码（如 `sh600519`） |
| **返回格式** | 文本格式（GBK 编码），以 `,` 分隔的字段数组 |
| **返回内容** | 现价、昨收、开盘、最高、最低、成交量等 |
| **适用需求** | 股票基本信息与实时行情 |


### 腾讯行情接口
| 项目 | 说明 |
| --- | --- |
| **目的** | 获取股票当前价、涨跌幅、成交量、买卖盘等 |
| **请求方式** | `HTTPS GET` |
| **URL** | `https://qt.gtimg.cn/q={symbol}` |
| **关键参数** | `symbol` - 股票代码（如 `sh600519`） |
| **返回格式** | 文本格式（GBK 编码），以 `~` 分隔的字段数组 |
| **返回内容** | 现价、昨收、开盘、最高、最低、成交量等 |
| **适用需求** | 股票基本信息与实时行情 |


## 股票搜索
### 新浪搜索接口
| 项目 | 说明 |
| --- | --- |
| **目的** | 按关键词搜索股票 |
| **请求方式** | `HTTPS GET` |
| **URL** | `https://suggest3.sinajs.cn/suggest/key={keyword}` |
| **关键参数** | `keyword` - 搜索关键词（如 `茅台`） |
| **返回格式** | 文本格式，包含 `suggestvalue` 字段 |
| **返回内容** | 每条记录使用 `,` 分隔，包含代码/类型/名称等 |
| **适用需求** | 搜索股票 |


### 腾讯搜索接口
| 项目 | 说明 |
| --- | --- |
| **目的** | 按关键词搜索股票 |
| **请求方式** | `HTTPS GET` |
| **URL** | `https://smartbox.gtimg.cn/s3/?v=2&t=all&c=1&q={keyword}` |
| **关键参数** | `keyword` - 搜索关键词（如 `茅台`） |
| **返回格式** | 文本格式，包含 `v_hint` 字段 |
| **返回内容** | 每条记录使用 `~` 分隔，包含市场/代码/名称等 |
| **适用需求** | 搜索股票 |


## K 线
### 新浪 K 线接口
| 项目 | 说明 |
| --- | --- |
| **目的** | 获取日内/日线 K 线数据，用于技术指标计算 |
| **请求方式** | `HTTP GET` |
| **URL** | `http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={symbol}&scale={scale}&ma=no&datalen={count}` |
| **关键参数** | `symbol` - 股票代码（如 `sh600519`）   `scale` - 时间粒度（5/15/30/60/240）   `datalen` - 数量 |
| **返回格式** | JSON 数组 |
| **返回内容** | 时间、开高低收与成交量 |
| **适用需求** | 技术指标所需的 K 线数据 |


## 资讯
### Google News RSS 搜索
| 项目 | 说明 |
| --- | --- |
| **目的** | 获取关键词相关资讯（可在逻辑层进行 24 小时筛选） |
| **请求方式** | `HTTPS GET` |
| **URL** | `https://news.google.com/rss/search?q={keyword}&hl=en-US&gl=US&ceid=US:en` |
| **返回格式** | RSS/XML 格式 |
| **返回内容** | `title`、`link`、`pubDate` |
| **适用需求** | 关键词资讯查询 |


### 资讯 RSS 聚合源
| 项目 | 说明 |
| --- | --- |
| **目的** | 获取热点/宏观资讯并进行 24 小时筛选 |
| **请求方式** | `HTTPS GET` |
| **URL** | • `https://hnrss.org/frontpage`   • `https://www.reddit.com/r/finance/.rss`   • `https://www.reddit.com/r/investing/.rss`   • `https://feeds.bbci.co.uk/news/business/rss.xml`   • `https://www.cnbc.com/id/10000664/device/rss/rss.html` |
| **返回格式** | RSS/XML 格式 |
| **返回内容** | `title`、`link`、`pubDate` |
| **适用需求** | 今日热点资讯查询 |


### 百度 RSS（国内财经/股票）
| 项目 | 说明 |
| --- | --- |
| **目的** | 国内财经与股票资讯来源 |
| **请求方式** | `HTTPS GET` |
| **URL** | • `https://news.baidu.com/n?cmd=1&class=finannews&tn=rss&sub=0`   • `https://news.baidu.com/n?cmd=1&class=stock&tn=rss&sub=0` |
| **返回格式** | RSS/XML 格式 |
| **返回内容** | `title`、`link`、`pubDate` |
| **适用需求** | 国内财经与股票资讯（24 小时筛选） |


