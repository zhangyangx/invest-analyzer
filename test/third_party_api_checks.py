#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Third-party API checks for invest-analyzer requirements.
No external dependencies.
"""

import json
import sys
import urllib.request
import xml.etree.ElementTree as ET

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        status = resp.getcode()
        data = resp.read()
        content_type = resp.headers.get("Content-Type", "")
    return status, data, content_type


def ok(result_list, name, detail=None):
    result_list.append({"name": name, "ok": True, "detail": detail or ""})


def fail(result_list, name, detail):
    result_list.append({"name": name, "ok": False, "detail": detail})


def parse_rss_items(xml_text):
    try:
        root = ET.fromstring(xml_text)
    except Exception as exc:
        return [], f"XML parse error: {exc}"

    items = root.findall(".//item")
    if not items:
        items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

    parsed = []
    for item in items:
        title = ""
        for elem in ["title", "{http://www.w3.org/2005/Atom}title"]:
            el = item.find(elem)
            if el is not None and el.text:
                title = el.text.strip()
                break
        time_text = ""
        for elem in ["pubDate", "date", "{http://www.w3.org/2005/Atom}published", "{http://purl.org/dc/elements/1.1/}date"]:
            el = item.find(elem)
            if el is not None and el.text:
                time_text = el.text.strip()
                break
        parsed.append({"title": title, "time": time_text})

    return parsed, ""


def test_tencent_quote(results):
    symbol = "sh600519"
    url = f"https://qt.gtimg.cn/q={symbol}"
    try:
        status, data, _ = fetch(url)
        if status != 200:
            return fail(results, "Tencent quote", f"HTTP {status}")
        text = data.decode("gbk", errors="ignore")
        if f"v_{symbol}=" not in text:
            return fail(results, "Tencent quote", "Missing symbol marker")
        fields = text.split("~")
        if len(fields) < 10:
            return fail(results, "Tencent quote", "Too few fields")
        return ok(results, "Tencent quote", f"fields: {len(fields)}")
    except Exception as exc:
        return fail(results, "Tencent quote", f"Exception: {exc}")


def test_sina_kline(results):
    url = (
        "http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
        "CN_MarketData.getKLineData?symbol=sh600519&scale=240&ma=no&datalen=10"
    )
    try:
        status, data, _ = fetch(url)
        if status != 200:
            return fail(results, "Sina kline", f"HTTP {status}")
        text = data.decode("utf-8", errors="ignore").strip()
        if not text:
            return fail(results, "Sina kline", "Empty response")
        payload = json.loads(text)
        if isinstance(payload, list) and len(payload) > 0:
            return ok(results, "Sina kline", f"items: {len(payload)}")
        return fail(results, "Sina kline", "Unexpected payload")
    except Exception as exc:
        return fail(results, "Sina kline", f"Exception: {exc}")


def test_rss_source(results, name, url, require_time=True):
    try:
        status, data, content_type = fetch(url)
        if status != 200:
            return fail(results, name, f"HTTP {status}")
        if "xml" not in content_type and "rss" not in content_type:
            # Some feeds don't set content-type properly; still try parse
            pass
        text = data.decode("utf-8", errors="ignore")
        items, err = parse_rss_items(text)
        if err:
            return fail(results, name, err)
        if not items:
            return fail(results, name, "No items")
        if require_time:
            if not any(i.get("time") for i in items):
                return fail(results, name, "Missing time fields")
        return ok(results, name, f"items: {len(items)}")
    except Exception as exc:
        return fail(results, name, f"Exception: {exc}")


def main():
    results = []

    test_tencent_quote(results)
    test_sina_kline(results)

    # News/RSS sources
    test_rss_source(results, "Google News RSS search", "https://news.google.com/rss/search?q=China+stock&hl=en-US&gl=US&ceid=US:en")
    test_rss_source(results, "Hacker News RSS", "https://hnrss.org/frontpage")
    test_rss_source(results, "Reddit r/finance RSS", "https://www.reddit.com/r/finance/.rss")
    test_rss_source(results, "Reddit r/investing RSS", "https://www.reddit.com/r/investing/.rss")
    test_rss_source(results, "BBC Business RSS", "https://feeds.bbci.co.uk/news/business/rss.xml")
    test_rss_source(results, "CNBC RSS", "https://www.cnbc.com/id/10000664/device/rss/rss.html")
    test_rss_source(results, "Baidu Finance RSS", "https://news.baidu.com/n?cmd=1&class=finannews&tn=rss&sub=0")
    test_rss_source(results, "Baidu Stock RSS", "https://news.baidu.com/n?cmd=1&class=stock&tn=rss&sub=0")

    # Summary
    print("Third-party API checks")
    print("=" * 80)
    ok_count = 0
    for r in results:
        status = "PASS" if r["ok"] else "FAIL"
        print(f"{status:<5} | {r['name']:<28} | {r['detail']}")
        if r["ok"]:
            ok_count += 1
    print("=" * 80)
    print(f"Total: {len(results)}, Pass: {ok_count}, Fail: {len(results) - ok_count}")

    # Non-zero exit if any failed
    if ok_count != len(results):
        sys.exit(2)


if __name__ == "__main__":
    main()
