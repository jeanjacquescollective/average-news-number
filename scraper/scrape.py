"""Find new VRT NWS articles, count the numbers in them and update the daily stats.

Run it as often as you like: every article is processed exactly once.

    python scraper/scrape.py                     # normal run
    python scraper/scrape.py --since 2026-10-01  # first run only: start the history earlier
"""

import argparse
import datetime as dt
import json
import re
import statistics
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from numextract import extract_numbers

BASE = "https://www.vrt.be/vrtnws/nl/"
FEED_URL = "https://www.vrt.be/vrtnws/nl.rss.articles.xml"
SITEMAP_URL = "https://www.vrt.be/vrtnws/nl.sitemap.article.{year}.{week:02d}.xml"
USER_AGENT = "average-news-number/1.0 (hobby project counting numbers in news articles)"
REQUEST_DELAY = 1.0  # seconds between requests, to be polite

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "state.json"
SUMMARY_FILE = DATA / "summary.json"

MAX_NEW_AGE_DAYS = 30      # anything published longer ago is not "new"
SEEN_RETENTION_DAYS = 45   # must stay above MAX_NEW_AGE_DAYS
MAX_FAILURES = 6           # give up on an article after this many failed runs

LINK_RE = re.compile(r"(?:https://www\.vrt\.be)?/vrtnws/nl/((?:\d{4}/\d{2}/\d{2}|liveblog)/[^/\"'?#\s\\<>]+)")
DATED_KEY_RE = re.compile(r"^(\d{4})/(\d{2})/(\d{2})/")
ATOM = {"a": "http://www.w3.org/2005/Atom"}

try:
    from zoneinfo import ZoneInfo
    BRUSSELS = ZoneInfo("Europe/Brussels")
except Exception:  # no tzdata available (e.g. some Windows Pythons)
    BRUSSELS = None


def log(*args):
    print(*args, file=sys.stderr, flush=True)


# --- time ---------------------------------------------------------------------

def _last_sunday(year, month):
    last = dt.date(year, month + 1, 1) - dt.timedelta(days=1)
    return last - dt.timedelta(days=(last.weekday() + 1) % 7)


def to_brussels(moment):
    """Convert an aware datetime to Belgian local time."""
    if BRUSSELS:
        return moment.astimezone(BRUSSELS)
    utc = moment.astimezone(dt.timezone.utc)
    dst_start = dt.datetime.combine(_last_sunday(utc.year, 3), dt.time(1), dt.timezone.utc)
    dst_end = dt.datetime.combine(_last_sunday(utc.year, 10), dt.time(1), dt.timezone.utc)
    hours = 2 if dst_start <= utc < dst_end else 1
    return utc.astimezone(dt.timezone(dt.timedelta(hours=hours)))


def parse_time(value):
    if not value:
        return None
    try:
        moment = dt.datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=dt.timezone.utc)
    return to_brussels(moment)


def key_date(key):
    m = DATED_KEY_RE.match(key)
    return dt.date(int(m[1]), int(m[2]), int(m[3])) if m else None


# --- http ---------------------------------------------------------------------

_last_request = 0.0


def fetch(url):
    """GET a URL as text. Returns None on 404, raises on other errors."""
    global _last_request
    wait = REQUEST_DELAY - (time.monotonic() - _last_request)
    if wait > 0:
        time.sleep(wait)
    _last_request = time.monotonic()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "nl"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if attempt == 2 or e.code < 500:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(5 * (attempt + 1))


# --- html -> text -------------------------------------------------------------

class TextExtractor(HTMLParser):
    """Plain text of an HTML fragment, one line per block element."""

    BLOCKS = {"p", "div", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote",
              "figcaption", "tr", "td", "th", "ul", "ol", "section", "article"}
    SKIP = {"script", "style", "noscript", "template", "svg"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skipping = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skipping += 1
        elif tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skipping = max(0, self.skipping - 1)
        elif tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skipping:
            self.parts.append(data)

    def text(self):
        lines = (re.sub(r"\s+", " ", line).strip() for line in "".join(self.parts).split("\n"))
        return "\n".join(line for line in lines if line)


def html_to_text(fragment):
    parser = TextExtractor()
    parser.feed(fragment)
    parser.close()
    return parser.text()


class ArticlePageParser(HTMLParser):
    """Fallback for full article pages: metadata plus the paragraphs inside <main>."""

    CAPTURE = {"p", "h2", "h3", "li", "blockquote"}
    END_MARKERS = {"Meer weten over", "Meest gelezen", "Lees ook"}
    SKIP = TextExtractor.SKIP

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.in_main = 0
        self.capturing = 0
        self.skipping = 0
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("property") and attrs.get("content"):
            self.meta.setdefault(attrs["property"], attrs["content"])
        elif tag == "main":
            self.in_main += 1
        elif tag in self.SKIP:
            self.skipping += 1
        elif tag in self.CAPTURE and self.in_main:
            if not self.capturing:
                self.chunks.append([])
            self.capturing += 1

    def handle_endtag(self, tag):
        if tag == "main":
            self.in_main = max(0, self.in_main - 1)
        elif tag in self.SKIP:
            self.skipping = max(0, self.skipping - 1)
        elif tag in self.CAPTURE and self.capturing:
            self.capturing -= 1

    def handle_data(self, data):
        if self.capturing and not self.skipping:
            self.chunks[-1].append(data)

    def text(self):
        lines = []
        for chunk in self.chunks:
            line = re.sub(r"\s+", " ", "".join(chunk)).strip()
            if line in self.END_MARKERS:
                break  # tags, the "most read" list (1 2 3 4 5) and related articles follow
            if line:
                lines.append(line)
        return "\n".join(lines)


# --- articles -----------------------------------------------------------------

def article_from_feed(key):
    """Every dated article has its own Atom feed with the full, clean article body."""
    xml = fetch(f"{BASE}{key}.rss.xml")
    if not xml:
        return None
    entry = ET.fromstring(xml).find("a:entry", ATOM)
    if entry is None:
        return None
    body = html_to_text(entry.findtext("a:content", "", ATOM))
    if not body:
        return None
    return {
        "id": entry.findtext("a:id", "", ATOM).rsplit("/", 1)[-1] or None,
        "title": entry.findtext("a:title", "", ATOM).strip(),
        "published": parse_time(entry.findtext("a:published", "", ATOM)),
        "body": body,
    }


def article_from_page(key):
    page = fetch(f"{BASE}{key}/")
    if not page:
        return None
    parser = ArticlePageParser()
    parser.feed(page)
    parser.close()
    title = re.sub(r"\s*\|\s*VRT NWS.*$", "", parser.meta.get("og:title", "")).strip()
    return {
        "id": None,
        "title": title,
        "published": parse_time(parser.meta.get("article:published_time")),
        "body": parser.text(),
    }


def fetch_article(key):
    article = article_from_feed(key) if key_date(key) else None
    return article or article_from_page(key)


# --- discovery ----------------------------------------------------------------

def iso_weeks(first, last):
    """(year, week) pairs of all ISO weeks touching first..last, oldest first."""
    weeks = []
    for offset in range((last - first).days + 1):
        year, week, _ = (first + dt.timedelta(days=offset)).isocalendar()
        if (year, week) not in weeks:
            weeks.append((year, week))
    return weeks


def discover(sitemap_weeks):
    """All article keys (paths below /vrtnws/nl/) linked from the overview pages."""
    sources = [FEED_URL, BASE + "net-binnen/", BASE]
    sources += [SITEMAP_URL.format(year=y, week=w) for y, w in sitemap_weeks]
    keys, working = set(), 0
    for url in sources:
        try:
            text = fetch(url)
        except Exception as e:
            log(f"! could not read {url}: {e}")
            continue
        if text is None:
            continue  # weekly sitemaps only exist once the week is over
        working += 1
        for m in LINK_RE.finditer(text):
            keys.add(m.group(1).removesuffix(".rss.xml"))
    if working == 0:
        raise SystemExit("No overview page could be read; is the site down?")
    return keys


# --- storage ------------------------------------------------------------------

def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8", newline="\n")


def day_path(day):
    return DATA / "days" / day[:4] / f"{day}.json"


def add_article(day, record):
    path = day_path(day)
    data = read_json(path, {"date": day, "articles": []})
    data["articles"].append(record)
    data["articles"].sort(key=lambda a: a["published"] or a["first_seen"])
    write_json(path, data)


def build_summary(tracking_start):
    days, updated_at = [], None
    for path in sorted((DATA / "days").glob("*/*.json")):
        day = read_json(path, None)
        refs = [
            {"v": n["v"], "t": n["t"], "title": a["title"], "url": a["url"]}
            for a in day["articles"] for n in a["numbers"]
        ]
        values = [r["v"] for r in refs]
        stats = {"date": day["date"], "articles": len(day["articles"]), "numbers": len(values)}
        if values:
            stats.update(
                mean=round(statistics.fmean(values), 4),
                median=statistics.median(values),
                min=min(refs, key=lambda r: r["v"]),
                max=max(refs, key=lambda r: r["v"]),
            )
        days.append(stats)
        for a in day["articles"]:
            updated_at = max(updated_at or a["first_seen"], a["first_seen"])
    write_json(SUMMARY_FILE, {
        "source": BASE,
        "timezone": "Europe/Brussels",
        "tracking_start": tracking_start,
        "updated_at": updated_at,
        "days": days,
    })


# --- main ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", type=dt.date.fromisoformat,
                        help="first run only: count articles published from this date (max 30 days back)")
    parser.add_argument("--limit", type=int, default=500, help="max articles to fetch in one run")
    args = parser.parse_args()

    now = to_brussels(dt.datetime.now(dt.timezone.utc)).replace(microsecond=0)
    today = now.date()
    oldest_new = today - dt.timedelta(days=MAX_NEW_AGE_DAYS)

    state = read_json(STATE_FILE, None)
    first_run = state is None
    if first_run:
        start = max(args.since or today, oldest_new)
        state = {"tracking_start": start.isoformat(), "seen": {}, "ids": {}, "failures": {}}
        log(f"First run: tracking articles published from {start}")
    elif args.since:
        log("! --since is ignored: tracking already started on " + state["tracking_start"])
    tracking_start = dt.date.fromisoformat(state["tracking_start"])
    seen, ids, failures = state["seen"], state["ids"], state["failures"]

    # Weekly sitemaps are a safety net for anything the overview pages no longer show.
    sitemap_from = tracking_start if first_run else max(tracking_start, today - dt.timedelta(days=8))
    keys = discover(iso_weeks(sitemap_from, today))

    def is_candidate(key):
        published = key_date(key)
        return key not in seen and (published is None or published >= max(tracking_start, oldest_new))

    candidates = sorted(filter(is_candidate, keys), reverse=True)
    log(f"{len(keys)} links found, {len(candidates)} not seen yet")

    added = 0
    for key in candidates[:args.limit]:
        try:
            article = fetch_article(key)
            if article is None:
                raise ValueError("no article content found")
        except Exception as e:
            failures[key] = failures.get(key, 0) + 1
            log(f"! {key}: {e} (attempt {failures[key]})")
            if failures[key] >= MAX_FAILURES:
                seen[key] = today.isoformat()
                del failures[key]
            continue
        failures.pop(key, None)
        seen[key] = today.isoformat()

        published = article["published"]
        day = published.date() if published else (key_date(key) or today)
        if day < max(tracking_start, oldest_new):
            continue  # an old article (or liveblog) that is still linked somewhere
        if article["id"]:
            if article["id"] in ids:
                continue  # same article under a new URL
            ids[article["id"]] = today.isoformat()

        numbers = extract_numbers(article["title"] + "\n" + article["body"])
        add_article(day.isoformat(), {
            "id": article["id"],
            "url": f"{BASE}{key}/",
            "title": article["title"],
            "published": published.isoformat() if published else None,
            "first_seen": now.isoformat(),
            "numbers": numbers,
        })
        added += 1
        log(f"+ {day} {len(numbers):3d} numbers  {article['title'][:80]}")

    cutoff = (today - dt.timedelta(days=SEEN_RETENTION_DAYS)).isoformat()
    state["seen"] = {k: v for k, v in sorted(seen.items()) if v >= cutoff}
    state["ids"] = {k: v for k, v in sorted(ids.items()) if v >= cutoff}
    state["failures"] = dict(sorted(failures.items()))
    write_json(STATE_FILE, state)
    build_summary(state["tracking_start"])
    log(f"Done: {added} new articles")


if __name__ == "__main__":
    main()
