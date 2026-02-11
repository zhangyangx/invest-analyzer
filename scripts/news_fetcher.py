#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
News fetcher script.
Supports keyword search (Google News RSS) and hotspot feeds (RSS list).
Output: JSON list of {title, link, source, time}
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

HOT_FEEDS = [
    ("Hacker News", "https://hnrss.org/frontpage"),
    ("Reddit Finance", "https://www.reddit.com/r/finance/.rss"),
    ("Reddit Investing", "https://www.reddit.com/r/investing/.rss"),
    ("BBC Business", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("CNBC", "https://www.cnbc.com/id/10000664/device/rss/rss.html"),
    ("Baidu Finance", "https://news.baidu.com/n?cmd=1&class=finannews&tn=rss&sub=0"),
    ("Baidu Stock", "https://news.baidu.com/n?cmd=1&class=stock&tn=rss&sub=0"),
]

DEFAULT_CONFIG = {
    "max_items": 30,
    "timezone": "+08:00",
}


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return DEFAULT_CONFIG.copy()
        merged = DEFAULT_CONFIG.copy()
        merged.update(data)
        return merged
    except Exception:
        return DEFAULT_CONFIG.copy()


def parse_tz_offset(offset: str) -> timezone:
    text = (offset or "").strip()
    if not text:
        return timezone.utc
    if text.upper() in {"UTC", "Z"}:
        return timezone.utc
    sign = 1
    if text[0] == "-":
        sign = -1
    text = text.lstrip("+-")
    parts = text.split(":")
    try:
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
    except Exception:
        return timezone.utc
    delta = timedelta(hours=hours, minutes=minutes) * sign
    return timezone(delta)


def fetch(url, timeout=15, retries=1):
    """Fetch URL with retry logic."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read(), resp.headers.get("Content-Type", "")
        except Exception as e:
            last_error = e
            if attempt < retries:
                continue  # Retry
    raise last_error


def parse_time(text: str):
    if not text:
        return None
    text = text.strip()
    # RFC 2822
    try:
        return parsedate_to_datetime(text)
    except Exception:
        pass
    # ISO 8601 (e.g., 2026-02-05T10:34:49.000Z)
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.fromisoformat(text)
    except Exception:
        pass
    # Date only
    try:
        return datetime.strptime(text[:10], "%Y-%m-%d")
    except Exception:
        return None


def get_text(item, candidates):
    for elem in candidates:
        el = item.find(elem)
        if el is not None and el.text:
            return el.text.strip()
    return ""


def get_link(item):
    link_elem = item.find("link")
    if link_elem is None:
        link_elem = item.find("{http://www.w3.org/2005/Atom}link")
    if link_elem is None:
        return ""
    if link_elem.text:
        return link_elem.text.strip()
    return link_elem.get("href", "").strip()


def parse_rss(xml_text: str, source: str, limit: int, tz_local: timezone):
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return []

    items = root.findall(".//item")
    if not items:
        items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

    results = []
    for item in items[:limit]:
        title = get_text(item, ["title", "{http://www.w3.org/2005/Atom}title"])
        link = get_link(item)
        time_text = get_text(
            item,
            ["pubDate", "date", "{http://www.w3.org/2005/Atom}published", "{http://purl.org/dc/elements/1.1/}date"],
        )

        dt = parse_time(time_text)
        if dt:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            dt = dt.astimezone(tz_local)
        results.append({
            "title": title,
            "link": link,
            "source": source,
            "time": dt.strftime("%Y-%m-%d %H:%M:%S %z") if dt else "",
            "_dt": dt.isoformat() if dt else "",
        })

    return results


def filter_by_hours(items, hours, tz_local: timezone):
    if hours <= 0:
        return items
    cutoff = datetime.now(tz_local) - timedelta(hours=hours)
    filtered = []
    for it in items:
        dt = it.get("_dt")
        if not dt:
            continue
        try:
            dt_obj = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        except Exception:
            continue
        if dt_obj >= cutoff:
            filtered.append(it)
    return filtered


def fetch_keyword_news(keyword: str, limit: int, tz_local: timezone):
    query = urllib.parse.quote(keyword)
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    data, _ = fetch(url)
    return parse_rss(data.decode("utf-8", errors="ignore"), "Google News", limit, tz_local)


def fetch_hot_feeds(limit: int, tz_local: timezone):
    results = []
    per_feed = max(5, min(20, limit // max(1, len(HOT_FEEDS))))
    for name, url in HOT_FEEDS:
        try:
            data, _ = fetch(url)
            results.extend(parse_rss(data.decode("utf-8", errors="ignore"), name, per_feed, tz_local))
        except Exception as e:
            # Log error but continue with other feeds
            print(f"[WARN] Failed to fetch {name}: {e}", file=sys.stderr)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", type=str, default="")
    parser.add_argument("--keywords", type=str, default="")
    parser.add_argument("--hours", type=int, default=24)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--mode", type=str, choices=["keyword", "hot"], default="keyword")
    args = parser.parse_args()

    if args.mode == "keyword" and not args.keyword and not args.keywords:
        print(json.dumps({"error": "missing_keyword"}, ensure_ascii=False))
        sys.exit(2)
    if args.hours < 0:
        print(json.dumps({"error": "invalid_hours"}, ensure_ascii=False))
        sys.exit(2)
    if args.limit is not None and args.limit <= 0:
        print(json.dumps({"error": "invalid_limit"}, ensure_ascii=False))
        sys.exit(2)

    try:
        config = load_config()
        tz_local = parse_tz_offset(config.get("timezone"))
        config_limit = int(config.get("max_items") or DEFAULT_CONFIG["max_items"])
        if config_limit <= 0:
            config_limit = DEFAULT_CONFIG["max_items"]
        final_limit = args.limit if args.limit is not None else config_limit
        # Fetch a bit more to tolerate dedupe/time filtering, then trim to final limit.
        base_limit = max(final_limit, config_limit)

        if args.mode == "keyword":
            terms = []
            if args.keywords:
                terms = [t.strip() for t in args.keywords.split(",") if t.strip()]
            elif args.keyword:
                terms = [args.keyword.strip()]

            items = []
            for t in terms:
                items.extend(fetch_keyword_news(t, base_limit, tz_local))
            # dedupe by title+link
            seen = set()
            deduped = []
            for it in items:
                key = f"{it.get('title','')}|{it.get('link','')}"
                if key in seen:
                    continue
                seen.add(key)
                deduped.append(it)
            items = deduped
        else:
            items = fetch_hot_feeds(base_limit, tz_local)

        items = filter_by_hours(items, args.hours, tz_local)

        # Sort by time descending (newest first)
        items.sort(key=lambda x: x.get("_dt") or "", reverse=True)

        # Cap final results by user limit (or config default when user omits --limit)
        items = items[:final_limit]

        # remove helper field
        for it in items:
            it.pop("_dt", None)

        print(json.dumps({"items": items, "count": len(items)}, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({"error": "request_failed", "detail": str(exc)}, ensure_ascii=False))
        sys.exit(3)


if __name__ == "__main__":
    main()
