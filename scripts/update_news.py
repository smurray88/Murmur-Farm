#!/usr/bin/env python3
"""Fetch the latest Murmur Farm, Blofeld and Warrant news into data/news.json.

Runs once a day on GitHub (see .github/workflows/update-news.yml), so the
News & Results section stays current with no manual updates. Uses only the
Python standard library.
"""
import email.utils
import html
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "news.json"
KEEP = 20

GOOGLE = "https://news.google.com/rss/search?hl=en-US&gl=US&ceid=US:en&q="
FEEDS = [
    GOOGLE + urllib.parse.quote('"Murmur Farm"'),
    GOOGLE + urllib.parse.quote('"Blofeld" (stakes OR Laurel OR sire OR filly OR colt OR gelding OR Maryland)'),
    GOOGLE + urllib.parse.quote('"by Blofeld"'),
    GOOGLE + urllib.parse.quote('"Warrant" (stallion OR sire OR "Murmur Farm" OR "by Warrant") thoroughbred'),
    "https://www.theracingbiz.com/tag/blofeld/feed/",
    "https://www.theracingbiz.com/tag/murmur-farm/feed/",
    "https://www.theracingbiz.com/tag/warrant/feed/",
]

# An item must mention one of our names...
NAMES = re.compile(r"\b(murmur farm|blofeld|warrant)\b", re.I)
# ...and look like horse racing (filters out James Bond and legal "warrant" news).
RACING = re.compile(
    r"\b(stakes|laurel|pimlico|timonium|parx|penn national|delaware park|charles town|"
    r"saratoga|belmont|sire|stallion|stud|foal|filly|colt|gelding|mare|maiden|"
    r"thoroughbred|racing|derby|juvenile|maryland million|furlong|breeders|"
    r"grade [1-3i]+|g[1-3]|stands? at|murmur farm|bloodstock|yearling|weanling)\b", re.I)
# "Warrant" alone is a common word, so it also needs a stallion-specific hint.
WARRANT_ONLY = re.compile(r"\bwarrant\b", re.I)
WARRANT_HINT = re.compile(r"\b(murmur|by warrant|warrant \(|sire|stallion|constitution)\b", re.I)


def clean(text):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    return re.sub(r"\s+", " ", text).strip()


def parse_date(text):
    if not text:
        return None
    try:
        d = email.utils.parsedate_to_datetime(text)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).strftime("%Y-%m-%d")


def parse_feed(xml_bytes, feed_url=""):
    items = []
    root = ET.fromstring(xml_bytes)
    for it in root.iter("item"):
        title = clean(it.findtext("title"))
        link = (it.findtext("link") or "").strip()
        desc = clean(it.findtext("description"))
        date = parse_date(it.findtext("pubDate"))
        src_el = it.find("source")
        source = clean(src_el.text) if src_el is not None and src_el.text else ""
        # Google News titles end with " - Source"
        if "news.google.com" in feed_url and " - " in title:
            head, tail = title.rsplit(" - ", 1)
            if not source or tail == source:
                title, source = head, source or tail
        if not source:
            source = urllib.parse.urlparse(feed_url or link).netloc.replace("www.", "")
            source = {"theracingbiz.com": "The Racing Biz"}.get(source, source)
        if title and link and date:
            items.append({"title": title, "url": link, "source": source, "date": date, "_text": title + " " + desc})
    return items


def relevant(item):
    text = item["_text"]
    if not NAMES.search(text) or not RACING.search(text):
        return False
    only_warrant = WARRANT_ONLY.search(text) and not re.search(r"murmur farm|blofeld", text, re.I)
    if only_warrant and not WARRANT_HINT.search(text):
        return False
    return True


def key(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())[:80]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (MurmurFarmNewsBot)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def merge(existing, fresh):
    seen, out = set(), []
    for item in sorted(existing + fresh, key=lambda i: i["date"], reverse=True):
        k = key(item["title"])
        if k in seen:
            continue
        seen.add(k)
        out.append({f: item[f] for f in ("title", "url", "source", "date")})
    return out[:KEEP]


def main():
    existing = json.loads(OUT.read_text()) if OUT.exists() else []
    fresh = []
    for url in FEEDS:
        try:
            got = [i for i in parse_feed(fetch(url), url) if relevant(i)]
            print(f"{len(got):3d} relevant  {url}")
            fresh += got
        except Exception as e:  # one bad feed shouldn't stop the rest
            print(f"  skipped  {url}  ({e})", file=sys.stderr)
    items = merge(existing, fresh)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(items)} items saved to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
