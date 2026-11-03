"""Shared helpers for the qbr-metrics pull scripts. Standard library only."""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta


def load_settings_env():
    """Fill missing env vars from Claude Code settings files (highest precedence first)."""
    for path in (".claude/settings.local.json", ".claude/settings.json",
                 "~/.claude/settings.local.json", "~/.claude/settings.json"):
        try:
            with open(os.path.expanduser(path)) as f:
                env = json.load(f).get("env", {})
        except (OSError, ValueError):
            continue
        for key, value in env.items():
            if isinstance(value, str) and not os.environ.get(key):
                os.environ[key] = value


def d(s):
    return date.fromisoformat(s) if isinstance(s, str) else s


FISCAL_STARTS = (2, 5, 8, 11)  # fiscal quarters start Feb 1, May 1, Aug 1, Nov 1 (FY27 = Feb 2026 to Jan 2027)


def fiscal_quarter_bounds(day):
    """First and last day of the fiscal quarter containing `day` (Q1 Feb-Apr, Q2 May-Jul, Q3 Aug-Oct, Q4 Nov-Jan)."""
    day = d(day)
    starts = [date(day.year, m, 1) for m in FISCAL_STARTS] + [date(day.year - 1, 11, 1)]
    start = max(s for s in starts if s <= day)
    nxt = date(start.year + (start.month + 2) // 12, (start.month + 2) % 12 + 1, 1)
    return start, nxt - timedelta(days=1)


def fiscal_label(start):
    """FY27-Q3 for a fiscal quarter starting `start`. The fiscal year is named for the year it ends in."""
    start = d(start)
    return f"FY{(start.year + 1) % 100:02d}-Q{FISCAL_STARTS.index(start.month) + 1}"


def month_bounds(day):
    day = d(day)
    nxt = date(day.year + (day.month // 12), day.month % 12 + 1, 1)
    return date(day.year, day.month, 1), nxt - timedelta(days=1)


def period_kind(start, end):
    """'quarter' (a whole fiscal quarter), 'month' (a whole calendar month), 'week' (7 days) or 'custom'."""
    start, end = d(start), d(end)
    if fiscal_quarter_bounds(start) == (start, end):
        return "quarter"
    if month_bounds(start) == (start, end):
        return "month"
    if (end - start).days == 6:
        return "week"
    return "custom"


def period_label(start, end):
    start, end = d(start), d(end)
    kind = period_kind(start, end)
    if kind == "quarter":
        return f"{fiscal_label(start)} (fiscal quarter, {start:%b %-d} to {end:%b %-d, %Y})"
    if kind == "month":
        return f"{start:%B %Y} (month)"
    if kind == "week":
        return f"Week of {start:%b %-d, %Y}"
    return f"{start} to {end}"


def periods(start, end):
    """Return (current, previous) as (start, end) date tuples.

    A whole fiscal quarter compares with the prior fiscal quarter, a whole calendar month with the prior
    month, a 7-day week with the prior 7 days. Any other range compares with the same-length window that
    ends the day before the start.
    """
    start, end = d(start), d(end)
    kind = period_kind(start, end)
    if kind == "quarter":
        prev_start, prev_end = fiscal_quarter_bounds(start - timedelta(days=1))
    elif kind == "month":
        prev_start, prev_end = month_bounds(start - timedelta(days=1))
    else:
        days = (end - start).days + 1
        prev_end = start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=days - 1)
    return (start, end), (prev_start, prev_end)


def resolve_period(args):
    """Turn command-line arguments into (start, end) dates.

    Accepts two dates; FY27-Q3 (also Q3-FY27); a month as 2026-09; or an ISO week as 2026-W41.
    A bare 'Q3' is rejected because it needs a fiscal year.
    """
    import re
    if len(args) == 2:
        return d(args[0]), d(args[1])
    if len(args) == 1:
        a = args[0].strip()
        m = re.fullmatch(r"(?i)(?:FY(\d{2})[- ]?Q([1-4])|Q([1-4])[- ]?FY(\d{2}))", a)
        if m:
            fy, qn = int(m.group(1) or m.group(4)), int(m.group(2) or m.group(3))
            start_month = FISCAL_STARTS[qn - 1]
            return fiscal_quarter_bounds(date(2000 + fy - 1, start_month, 1))
        m = re.fullmatch(r"(\d{4})-(\d{2})", a)
        if m:
            return month_bounds(date(int(m.group(1)), int(m.group(2)), 1))
        m = re.fullmatch(r"(?i)(\d{4})-W(\d{2})", a)
        if m:
            return date.fromisocalendar(int(m.group(1)), int(m.group(2)), 1), date.fromisocalendar(int(m.group(1)), int(m.group(2)), 7)
        if re.fullmatch(r"(?i)Q[1-4]", a):
            raise SystemExit("A quarter needs its fiscal year, for example FY27-Q3 (Aug 1 to Oct 31, 2026).")
    raise SystemExit("Give two dates (YYYY-MM-DD YYYY-MM-DD), a fiscal quarter (FY27-Q3), a month (2026-09) or an ISO week (2026-W41).")


def pct_change(cur, prev):
    if cur is None or prev in (None, 0):
        return None
    return round((cur - prev) / prev * 100, 1)


def bucket_days(start, end):
    """Chart bucket size: daily points for a period of 14 days or less (a week), 7-day buckets otherwise."""
    return 1 if (d(end) - d(start)).days + 1 <= 14 else 7


def weekly(daily, start, end):
    """Sum a {iso_date: value} dict into buckets starting at `start` (7-day buckets, or daily for short periods)."""
    start, end = d(start), d(end)
    b = bucket_days(start, end)
    n = (end - start).days + 1
    out = [0] * ((n + b - 1) // b)
    for i in range(n):
        out[i // b] += daily.get((start + timedelta(days=i)).isoformat(), 0) or 0
    return out


def http_json(url, headers=None, data=None, timeout=60, retries=6):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers or {}, data=body)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                payload = json.loads(raw)
            except ValueError:
                payload = {"raw": raw[:300].decode(errors="replace")}
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(min(60, 3 * 2 ** attempt))
                last = (e.code, payload)
                continue
            return e.code, payload
        except (urllib.error.URLError, TimeoutError) as e:
            last = (0, {"error": str(e)})
            time.sleep(2 ** attempt)
    return last


def log(msg):
    print(msg, file=sys.stderr, flush=True)


INDUSTRY_GROUPS = [  # first match wins; order matters (specific before general)
    ("IT services and consulting", ("it services", "it consulting", "managed services")),
    ("Software and internet", ("computer and network security", "data infrastructure", "artificial intelligence", "blockchain", "software",
                               "internet", "technology", "data processing", "saas", "cloud", "information")),
    ("Financial services", ("financial", "bank", "insurance", "fintech", "capital markets", "investment", "payment", "mortgage",
                            "venture capital", "private equity")),
    ("Education", ("education", "e-learning", "university", "academic", "school", "training and coaching")),
    ("Healthcare and life sciences", ("health", "medical", "pharma", "biotech", "hospital", "life sciences", "wellness")),
    ("Telecom and hardware", ("telecom", "semiconductor", "electronic", "hardware", "networking", "wireless", "communications")),
    ("Media, marketing and entertainment", ("media", "entertainment", "gaming", "games", "publishing", "broadcast", "advertising",
                                            "marketing", "spectator sports", "design")),
    ("Retail, consumer and hospitality", ("retail", "e-commerce", "ecommerce", "consumer", "wholesale", "apparel", "restaurant", "hotel",
                                          "travel", "airline", "food and beverage", "sporting goods", "leisure")),
    ("Government and non-profit", ("government", "non-profit", "nonprofit", "public", "civic", "international trade")),
    ("Manufacturing, energy, construction and real estate", ("manufactur", "automotive", "industrial", "energy", "oil", "aerospace",
                                                              "logistics", "transport", "utilities", "environmental", "construction",
                                                              "civil engineering", "real estate")),
    ("Professional and business services", ("consulting", "business services", "professional services", "staffing", "outsourc", "management",
                                            "research", "accounting", "human resource", "employment services", "legal", "law practice",
                                            "events services")),
]


def industry_group(label):
    """Map a raw industry label to a broad group. Missing label is Unknown; no match is Other."""
    if not label:
        return "Unknown"
    low = label.lower()
    for group, keys in INDUSTRY_GROUPS:
        if any(k in low for k in keys):
            return group
    return "Other"


def google_access_token(scope):
    """Access token for the Google service account named by GOOGLE_APPLICATION_CREDENTIALS (JWT signed with openssl).
    Returns (token, service_account_email). The key is read, never printed."""
    import base64
    import subprocess
    import tempfile
    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    try:
        with open(os.path.expanduser(path)) as f:
            sa = json.load(f)
    except (OSError, ValueError):
        sys.exit("GOOGLE_APPLICATION_CREDENTIALS is not set or does not point to a service account key file")
    now = int(time.time())
    b64 = lambda x: base64.urlsafe_b64encode(x if isinstance(x, bytes) else x.encode()).rstrip(b"=").decode()  # noqa: E731
    msg = b64(json.dumps({"alg": "RS256", "typ": "JWT"})) + "." + b64(json.dumps(
        {"iss": sa["client_email"], "scope": scope, "aud": "https://oauth2.googleapis.com/token", "iat": now, "exp": now + 3600}))
    with tempfile.NamedTemporaryFile("w", suffix=".pem", delete=False) as kf:
        kf.write(sa["private_key"])
        key_path = kf.name
    try:
        sig = subprocess.run(["openssl", "dgst", "-sha256", "-sign", key_path], input=msg.encode(), capture_output=True).stdout
    finally:
        os.unlink(key_path)
    status, body = http_json("https://oauth2.googleapis.com/token", data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                                                                         "assertion": msg + "." + b64(sig)}, retries=1)
    if status != 200 or "access_token" not in body:
        sys.exit(f"Google token request failed: HTTP {status} {str(body)[:160]}")
    return body["access_token"], sa["client_email"]
