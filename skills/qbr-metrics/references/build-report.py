#!/usr/bin/env python3
"""Build the qbr-metrics report from the raw pull JSON.

Usage: build-report.py START END OUT_DIR
Reads OUT_DIR/raw-{wp,youtube,luma,sheet,commonroom}.json (any may be missing) plus the optional
topics.json, context.json, stoplight.json, insights.md and cost.json. Writes OUT_DIR/report.html,
report.md and metrics.json. Standard library only; charts are inline SVG on a white page.
"""
import html
import json
import os
import re
import statistics
import sys
from datetime import timedelta

sys.path.insert(0, os.path.dirname(__file__))
import qbrlib as q  # noqa: E402

ORANGE, GREEN, TEXT, DIM, GRID, PREV = "#FF6C37", "#2E9E6B", "#1A1D21", "#5F6670", "#E5E7EB", "#9AA1AB"
SOURCES = {"wp": "Blog", "youtube": "YouTube", "luma": "Luma", "sheet": "Meetup sheet", "linkedin": "LinkedIn", "mailchimp": "Mailchimp", "commonroom": "Common Room", "community": "Owned community"}
KIND_COLOR = {"release": "#FF6C37", "industry": "#3B5BDB", "campaign": "#7C3AED"}
KIND_LABEL = {"release": "Postman release", "industry": "Industry news", "campaign": "Paid campaign"}
STATUS_COLOR = {"green": "#6BFA4A", "amber": "#F2A23A", "red": "#E5392B", "gray": "#D5D8DD"}
FULL_WEEKS = 0   # set in main(): complete buckets (7-day weeks, or days for short periods) in the period
BUCKET = 7       # set in main(): bucket size in days
MARKERS = []     # set in main(): context events for the chart overlay
PERIOD_START = None


def esc(s):
    return html.escape(str(s))


def n(v, digits=0):
    return "n/a" if v is None else f"{v:,.{digits}f}"


def usd(v, digits=0):
    return "n/a" if v is None else f"${v:,.{digits}f}"


def pc_text(p):
    return "n/a" if p is None else f"{'+' if p > 0 else ''}{p:.1f}%"


def delta(pct, invert=False):
    """Delta badge. invert=True colors an increase as bad (for cost)."""
    if pct is None:
        return '<span class="delta na">n/a</span>'
    up = pct > 0
    good = (not up) if invert else up
    arrow = "▲" if up else ("▼" if pct < 0 else "■")
    cls = "flat" if pct == 0 else ("up" if good else "down")
    return f'<span class="delta {cls}">{arrow} {abs(pct):.1f}%</span>'


def tile(label, cur, prev=None, pct=None, note=None, digits=0, suffix="", prefix="", invert=False):
    prev_html = f'<div class="prev">vs {prefix}{n(prev, digits)}{suffix}</div>' if prev is not None else ""
    note_html = f'<div class="note">{esc(note)}</div>' if note else ""
    return (f'<div class="tile"><div class="tl">{esc(label)}</div><div class="tv">{prefix}{n(cur, digits)}{suffix}</div>'
            f'{delta(pct, invert)}{prev_html}{note_html}</div>')


def na_tile(label, reason):
    return (f'<div class="tile na-tile"><div class="tl">{esc(label)}</div><div class="tv dim">Not available</div>'
            f'<div class="note">{esc(reason)}</div></div>')


def line_chart(title, series, start=None, labels=None, markers=True, height=240, note=None):
    """series: list of (name, values, color, dashed). Weekly buckets from `start`, or explicit x `labels`."""
    width, pl, pr, pt, pb = 640, 76, 16, 50, 34
    if BUCKET == 1:
        title = title.replace("per week", "per day")
    if FULL_WEEKS and labels is None:
        series = [(nm, v[:FULL_WEEKS], c, ds) for nm, v, c, ds in series]
    length = max(len(v) for _, v, _, _ in series)
    ymax = max((max(v) if v else 0) for _, v, _, _ in series) or 1
    step = 10 ** (len(str(int(ymax))) - 1)
    ymax = ((int(ymax) // step) + 1) * step
    w, h = width - pl - pr, height - pt - pb

    def px(i):
        return pl + (w * i / (length - 1) if length > 1 else w / 2)

    def py(val):
        return pt + h - (h * val / ymax)

    parts = []
    for k in range(5):
        y = pt + h - h * k / 4
        parts.append(f'<line x1="{pl}" y1="{y:.1f}" x2="{width - pr}" y2="{y:.1f}" stroke="{GRID}"/>'
                     f'<text x="{pl - 8}" y="{y + 4:.1f}" fill="{DIM}" font-size="11" text-anchor="end">{ymax * k / 4:,.0f}</text>')
    tick_every = max(1, length // 6)
    for i in range(0, length, tick_every):
        lab = labels[i] if labels else (q.d(start) + timedelta(days=BUCKET * i)).strftime("%b %-d")
        parts.append(f'<text x="{px(i):.1f}" y="{height - 10}" fill="{DIM}" font-size="11" text-anchor="middle">{esc(lab)}</text>')
    if markers and MARKERS and labels is None and PERIOD_START:
        rows_used = [[], [], []]  # stagger overlapping marker badges across three rows
        for num, ev in MARKERS:
            pos = (q.d(ev["date"]) - PERIOD_START).days / BUCKET
            if not 0 <= pos <= length - 1:
                continue
            x = px(pos)
            row = next((r for r in range(3) if all(abs(x - u) >= 16 for u in rows_used[r])), 2)
            rows_used[row].append(x)
            cy = 11 + row * 15
            col = KIND_COLOR.get(ev["kind"], DIM)
            parts.append(f'<line x1="{x:.1f}" y1="{cy + 7}" x2="{x:.1f}" y2="{pt + h}" stroke="{col}" stroke-width="1" stroke-dasharray="2 3" opacity="0.35"/>'
                         f'<circle cx="{x:.1f}" cy="{cy}" r="7" fill="{col}"/>'
                         f'<text x="{x:.1f}" y="{cy + 3.3}" fill="#fff" font-size="9" font-weight="700" text-anchor="middle">{num}</text>')
    legend = []
    for name, vals, color, dashed in series:
        pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(vals))
        dash = ' stroke-dasharray="5 4" opacity="0.7"' if dashed else ""
        parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.4" stroke-linejoin="round" points="{pts}"{dash}/>')
        legend.append(f'<span class="lg"><i style="background:{color};{"opacity:.7" if dashed else ""}"></i>{esc(name)}</span>')
    cap_note = f'<div class="foot">{esc(note)}</div>' if note else ""
    return (f'<figure class="chart"><figcaption>{esc(title)}</figcaption>'
            f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">{"".join(parts)}</svg>'
            f'<div class="legend">{"".join(legend)}</div>{cap_note}</figure>')


def hbars(rows, total=None, color=ORANGE):
    """Horizontal bar list. rows: [(label, value)]."""
    top = max((v for _, v in rows), default=1) or 1
    out = []
    for lab, v in rows:
        share = f" ({v / total * 100:.0f}%)" if total else ""
        out.append(f'<div class="hb"><div class="hbl">{esc(lab)}</div><div class="hbt"><span style="width:{v / top * 100:.1f}%;background:{color}"></span></div>'
                   f'<div class="hbv">{n(v)}{share}</div></div>')
    return "".join(out)


def stack_bar(label, paid, organic, fmt_label):
    total = (paid or 0) + (organic or 0)
    pp = (paid / total * 100) if total else 0
    return (f'<div class="sb"><div class="sbl">{esc(label)} <b>{esc(fmt_label)}</b></div>'
            f'<div class="bar"><span class="paid" style="width:{pp:.1f}%"></span><span class="org" style="width:{100 - pp:.1f}%"></span></div>'
            f'<div class="sbn">Paid {n(paid)} ({pp:.0f}%) · Organic {n(organic)}</div></div>')


def _bold(s):
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


def md_to_html(text):
    """Small markdown subset: ### and ## headings (rendered as h3), bullets, **bold**, pipe tables, paragraphs."""
    out, in_list, table = [], False, []

    def flush_table():
        nonlocal table
        if not table:
            return
        rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in table]
        rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
        if rows:
            head, body_rows = rows[0], rows[1:]
            th = "".join(f"<th>{esc(c)}</th>" for c in head)
            tr = "".join("<tr>" + "".join("<td>" + _bold(esc(c)) + "</td>" for c in r) + "</tr>" for r in body_rows)
            out.append(f"<table class=\"mdt\"><tr>{th}</tr>{tr}</table>")
        table = []

    for line in text.splitlines():
        if line.lstrip().startswith("|"):
            if in_list:
                out.append("</ul>")
                in_list = False
            table.append(line)
            continue
        flush_table()
        line = esc(line)
        line = _bold(line)
        if line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{line[2:]}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if line.startswith("### "):
            out.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "):
            out.append(f"<h3>{line[3:]}</h3>")
        elif line.strip():
            out.append(f"<p>{line}</p>")
    flush_table()
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


INSIGHT_KEYS = [("are we amplifying", "reach"), ("paid vs organic", "youtube"), ("topics, style", "topics"), ("news, releases", "context"),
                ("meetups", "sheet"), ("new channels", "channels"), ("newsletters", "newsletters"), ("accounts influenced", "commonroom"),
                ("not covered", "limits")]


def split_insights(md):
    """Split insights.md on ### headings into {section key: markdown}. Unrecognised headings go to 'other'."""
    out, cur, buf = {}, None, []

    def flush():
        if cur is not None and buf:
            out[cur] = out.get(cur, "") + "\n".join(buf).strip() + "\n"
    for line in (md or "").splitlines():
        if line.startswith("### "):
            flush()
            buf = []
            low = line[4:].lower()
            cur = next((k for needle, k in INSIGHT_KEYS if needle in low), "other")
            if cur == "other":
                buf.append(line)  # keep the heading so an unmapped block still reads sensibly
        else:
            buf.append(line)
    flush()
    return out


def with_rec(section_html, recs, key, ins=None):
    parts = ""
    if ins and ins.get(key):
        parts += f'<div class="ins"><h3>Insights</h3>{md_to_html(ins[key])}</div>'
    text = (recs or {}).get(key)
    if text:
        parts += f'<div class="rec"><strong>Recommendation.</strong> {esc(text)}</div>'
    if not parts:
        return section_html
    i = section_html.rfind("</section>")
    return section_html[:i] + parts + section_html[i:] if i >= 0 else section_html + parts


def load(out_dir, name):
    try:
        with open(os.path.join(out_dir, name)) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def load_text(out_dir, name):
    try:
        with open(os.path.join(out_dir, name)) as f:
            return f.read().strip()
    except OSError:
        return ""


# ---------------------------------------------------------------- reach per piece

def _reach(values):
    v = sorted((x or 0) for x in values)[::-1]
    total = sum(v)
    return {"pieces": len(v), "median": statistics.median(v) if v else None, "total": total,
            "top3_views": sum(v[:3]), "top3_share": round(sum(v[:3]) / total * 100, 1) if total else None,
            "under_100": sum(1 for x in v if x < 100)}


def reach_stats(d, tp):
    """Reach per piece for blog posts and DevRel videos, current and previous. Videos exclude paid ad creatives,
    localized duplicates and event recordings, and use organic views."""
    out = {}
    if d["wp"]:
        out["blog"] = {per: _reach(p["views_in_period"] for p in d["wp"][per]["published"]) for per in ("current", "previous")}
    if tp:
        out["video"] = {per: _reach(i["metric"] for i in tp[per]["video"]["items"] if not i["excluded"]) for per in ("current", "previous")}
        out["ad_organic"] = {per: sum((i["metric"] or 0) for i in tp[per]["video"]["items"]
                                      if (i["excluded"] or "").startswith("paid ad creative")) for per in ("current", "previous")}
    if d["wp"]:
        out["blog_new_share"] = {per: round(sum((p["views_in_period"] or 0) for p in d["wp"][per]["published"]) / d["wp"][per]["views"] * 100, 1)
                                 if d["wp"][per]["views"] else None for per in ("current", "previous")}
    yt = d["youtube"]
    if yt and tp and "video" in out:
        out["video_new_share"] = {}
        for per in ("current", "previous"):
            base = yt[per]["totals"]["organic_views"] - out["ad_organic"][per]
            out["video_new_share"][per] = round(out["video"][per]["total"] / base * 100, 1) if base > 0 else None
    if yt:
        out["youtube"] = {per: {"organic_share_pct": round(yt[per]["totals"]["organic_views"] / yt[per]["totals"]["views"] * 100, 1) if yt[per]["totals"]["views"] else None,
                                "net_subs": yt[per]["subscribers"]["net"]} for per in ("current", "previous")}
        out["youtube"]["subscribers_now"] = yt["subscribers_total_now"]
    return out


def reach_section(rs):
    rows = []

    def add(label, a, b, digits=0, suffix="", invert=False):
        rows.append(f'<tr><td>{esc(label)}</td><td class="r">{n(a, digits)}{suffix}</td><td class="r">{n(b, digits)}{suffix}</td>'
                    f'<td class="r">{delta(q.pct_change(a, b), invert)}</td></tr>')
    if "blog" in rs:
        c, p = rs["blog"]["current"], rs["blog"]["previous"]
        add("Blog: median views per post published", c["median"], p["median"])
        add("Blog: share of views on the top 3 posts", c["top3_share"], p["top3_share"], 1, "%", invert=True)
        add("Blog: posts under 100 views", c["under_100"], p["under_100"], invert=True)
    if "blog_new_share" in rs:
        add("Blog: share of views on posts published in the period", rs["blog_new_share"]["current"], rs["blog_new_share"]["previous"], 1, "%")
    if "video_new_share" in rs:
        add("Video: share of organic views on videos published in the period", rs["video_new_share"]["current"], rs["video_new_share"]["previous"], 1, "%")
    if "video" in rs:
        c, p = rs["video"]["current"], rs["video"]["previous"]
        add("Video: median organic views per DevRel video", c["median"], p["median"])
        add("Video: share of organic views on the top 3 videos", c["top3_share"], p["top3_share"], 1, "%", invert=True)
        add("Video: videos under 100 organic views", c["under_100"], p["under_100"], invert=True)
        subs = rs.get("youtube", {}).get("subscribers_now")
        if subs and c["median"] is not None and p["median"] is not None:
            add("Video: median organic views as % of subscribers", c["median"] / subs * 100, p["median"] / subs * 100, 2, "%")
    if "youtube" in rs:
        c, p = rs["youtube"]["current"], rs["youtube"]["previous"]
        add("YouTube: organic share of all views", c["organic_share_pct"], p["organic_share_pct"], 1, "%")
        if "video" in rs:
            add("YouTube: net new subscribers per DevRel video", c["net_subs"] / max(rs["video"]["current"]["pieces"], 1),
                p["net_subs"] / max(rs["video"]["previous"]["pieces"], 1), 1)
    return (f'<section><h2>Reach per piece</h2><p class="foot" style="margin-top:0">Totals can grow while the typical piece reaches few people. '
            f'These figures show how far each piece travels and how concentrated the views are. Blog views are views in the period on posts published in it. '
            f'Videos use organic views and exclude paid ad creatives, localized duplicates and event recordings.</p>'
            f'<table><tr><th></th><th class="r">This period</th><th class="r">Previous</th><th class="r">Change</th></tr>{"".join(rows)}</table></section>')


# ---------------------------------------------------------------- stoplight

def band(pct, kind):
    """Status band for a percent change. kind 'output': green at or above last period. kind 'result': green at +5% or better."""
    if pct is None:
        return None
    hi = 0 if kind == "output" else 5
    if pct >= hi:
        return "green"
    return "red" if pct <= -20 else "amber"


def blend(*bands):
    """One band from several that measure the same thing: all agree -> that band, any disagreement -> amber."""
    sig = {b for b in bands if b}
    return sig.pop() if len(sig) == 1 else ("amber" if sig else None)


def per_event(c, key):
    return c[key] / c["events"] if c["events"] else None


def status_cell(signals, override=None):
    """Return (css background, label). One status: solid. Two different: left-to-right gradient output to result."""
    if override:
        signals = [override] if isinstance(override, str) else list(override)
    sig = [s for s in signals if s]
    if not sig:
        return STATUS_COLOR["gray"], "Not enough data"
    if len(sig) == 1 or sig[0] == sig[-1]:
        return STATUS_COLOR[sig[0]], sig[0]
    return f"linear-gradient(90deg,{STATUS_COLOR[sig[0]]},{STATUS_COLOR[sig[-1]]})", f"{sig[0]} to {sig[-1]}"


def stoplight_rows(d, tp=None):
    rs = reach_stats(d, tp)
    wp, yt, lu, sh, cr = d["wp"], d["youtube"], d["luma"], d["sheet"], d["commonroom"]
    rows = []
    # Developers Reached
    if lu:
        c, p, ch = lu["current"], lu["previous"], lu["change"]
        note = (f"{n(c['registered'])} Luma registrations ({pc_text(ch['registered'])}) and {n(c['attended'])} attended ({pc_text(ch['attended'])}) "
                f"across {c['events']} events (previous {p['events']}). Attendance rate {n(c['attendance_rate_pct'], 1)}%. "
                f"New Luma subscribers {n(lu['contacts']['current']['new'])} ({pc_text(lu['contacts_change_new'])}).")
        if sh and sh["current"]["avg_rating"]:
            note += f" Average event rating {sh['current']['avg_rating']}/5."
        # How many events to hold is a planning choice, so fewer events alone never scores red: volume is capped at amber and the
        # result is judged per event (demand for each event) together with subscriber growth. A fall driven by volume reads amber.
        out = band(ch["events"], "output")
        out = "amber" if out == "red" else out
        reg_pe = q.pct_change(per_event(c, "registered"), per_event(p, "registered"))
        res = blend(band(reg_pe, "result"), band(lu["contacts_change_new"], "result"))
        if reg_pe is not None:
            note += (f" Registrations per event {n(per_event(c, 'registered'))} ({pc_text(reg_pe)} vs {n(per_event(p, 'registered'))}), "
                     f"so the fall in totals comes mostly from fewer events, while the slowdown in new subscribers is the signal to watch.")
        rows.append(("Developers Reached", [out, res], note))
    else:
        rows.append(("Developers Reached", [], "Luma is not connected."))
    # Accounts influenced
    if cr:
        m = cr["metrics"]
        note = (f"{n(m.get('accounts_influenced'))} accounts influenced among event attendees (as of today; "
                f"{n(m.get('company_coverage_pct'), 1)}% of attendees have a known company). "
                f"{n(m.get('tier1_share_of_accounts_pct'), 1)}% of accounts are Tier 1 and {n(m['economic_buyer_pct'], 1)}% of attendees are flagged as economic buyers.")
        sig = []
        if lu and "new_corporate_domains" in lu["contacts"]["current"]:
            cc, pc_ = lu["contacts"]["current"], lu["contacts"]["previous"]
            reach = q.pct_change(cc["corporate_domains_at_end"], pc_["corporate_domains_at_end"])
            note += (f" Corporate accounts reached through Luma: {n(cc['corporate_domains_at_end'])} ({pc_text(reach)} vs {n(pc_['corporate_domains_at_end'])}); "
                     f"new this period {n(cc['new_corporate_domains'])} ({pc_text(q.pct_change(cc['new_corporate_domains'], pc_['new_corporate_domains']))} vs {n(pc_['new_corporate_domains'])}).")
            sig = [band(reach, "result")]
        rows.append(("Accounts influenced", sig, note))
    else:
        rows.append(("Accounts influenced", [], "Common Room is not connected."))
    # Community engagement
    cm = d.get("community")
    if cm:
        c, p, ch = cm["current"], cm["previous"], cm["change"]
        note = (f"Discord community: {n(c['active_rate_pct'], 2)}% of {n(c['members_end'])} members active in a month "
                f"(average {n(c['active_members_avg'])} active members, {pc_text(ch['active_members_avg'])} vs {n(p['active_members_avg'])}). "
                f"{n(c['joins'])} joins ({pc_text(ch['joins'])}), net {n(c['net_members'])} members. "
                f"{n(c['help_topics'])} help topics, {n(c['answer_rate_pct'], 0)}% answered, with {n(c['staff_bot_replies'])} staff and bot replies. "
                f"Active members and joins are the result; the answer rate on help topics is the output the team controls.")
        rows.append(("Community Engagement Rate", [band(ch["answer_rate_pct"], "output"), blend(band(ch["active_members_avg"], "result"), band(ch["joins"], "result"))], note))
    else:
        rows.append(("Community Engagement Rate", [], "Not connected: the community dashboard MCP was not pulled."))
    # Blogs
    if wp:
        c, p, ch = wp["current"], wp["previous"], wp["change"]
        vpp = q.pct_change(c["views_per_published_post"], p["views_per_published_post"])
        note = (f"{c['posts_published']} blogs published ({pc_text(ch['posts_published'])} vs {p['posts_published']}). Blog views {n(c['views'])} ({pc_text(ch['views'])}); "
                f"views per post published {n(c['views_per_published_post'])} ({pc_text(vpp)}). Paid vs organic is not measurable on the blog.")
        if "blog" in rs:
            rc, rp = rs["blog"]["current"], rs["blog"]["previous"]
            note += f" Reach: median {n(rc['median'])} views per post ({pc_text(q.pct_change(rc['median'], rp['median']))} vs {n(rp['median'])})."
            if rc["top3_share"] is not None and rc["top3_share"] >= 50:
                adj = q.pct_change(c["views"] - rc["top3_views"], p["views"])
                note += f" The top 3 posts are {n(rc['top3_share'], 0)}% of views on posts published; without them blog views are {pc_text(adj)}."
        rows.append(("Blogs", [band(ch["posts_published"], "output"), band(ch["views"], "result")], note))
    else:
        rows.append(("Blogs", [], "Blog data is not connected."))
    # Video
    if yt:
        c, p, ch = yt["current"], yt["previous"], yt["change"]
        pub, ppub = len(c["videos"]), len(p["videos"])
        ads = 0
        if tp:  # score DevRel-produced content only: leave out paid ad creatives and localized duplicates
            def devrel(per):
                return sum(1 for v in tp[per]["video"]["items"] if not v["excluded"])  # same definition as Reach per piece
            ads = sum(1 for v in tp["current"]["video"]["items"] if (v["excluded"] or "").startswith("paid ad creative"))
            pub, ppub = devrel("current"), devrel("previous")
        out = q.pct_change(pub, ppub)
        extra = f" Not counted: {ads} paid ad creatives from the ad campaign, plus localized duplicates and event recordings." if ads else ""
        organic, p_organic = c["totals"]["organic_views"], p["totals"]["organic_views"]
        adnote = ""
        if "ad_organic" in rs and rs["ad_organic"]["current"]:
            organic, p_organic = organic - rs["ad_organic"]["current"], p_organic - rs["ad_organic"]["previous"]
            adnote = f" (excludes {n(rs['ad_organic']['current'])} organic views on the paid ad creatives)"
        res = q.pct_change(organic, p_organic)
        note = (f"{pub} DevRel videos published ({pc_text(out)} vs {ppub}).{extra} Organic views {n(organic)} ({pc_text(res)}){adnote}. "
                f"Total views {n(c['totals']['views'])} ({pc_text(ch['total.views'])}) because paid ad views moved {pc_text(ch['total.paid_views'])}; paid views are shown for context and are not scored.")
        if "video" in rs and "youtube" in rs:
            vc, vp = rs["video"]["current"], rs["video"]["previous"]
            subs = rs["youtube"]["subscribers_now"]
            note += (f" Reach: median {n(vc['median'])} organic views per video ({pc_text(q.pct_change(vc['median'], vp['median']))} vs {n(vp['median'])}), "
                     f"about {n(vc['median'] / subs * 100, 1)}% of subscribers; organic is {n(rs['youtube']['current']['organic_share_pct'], 1)}% of all YouTube views.")
        rows.append(("Video", [band(out, "output"), band(res, "result")], note))
    else:
        rows.append(("Video", [], "YouTube is not connected."))
    return rows


def stoplight_section(d, overrides, tp=None):
    body = []
    for name, signals, note in stoplight_rows(d, tp):
        ov = (overrides or {}).get("rows", {}).get(name, {})
        bg, label = status_cell(signals, ov.get("status"))
        if label == "Not enough data" and note.startswith("Not connected"):
            label = "Not connected"
        note = ov.get("note", note)
        body.append(f'<tr><td class="kpi">{esc(name)}</td><td class="status" style="background:{bg}" title="{esc(label)}"><span>{esc(label)}</span></td>'
                    f'<td class="notes">{esc(note)}</td></tr>')
    rules = ("Status rules, applied to the change against the previous period. Output signal (what the team produced): green at or above last period, "
             "amber down to -20%, red below that (fewer events held is capped at amber, because event volume is a planning choice). Result signal (what it achieved): green at +5% or better, amber from -20% to +5%, red at -20% or worse. "
             "Developers Reached judges the result per event, together with new subscriber growth; when those disagree it is amber. A solid cell means output and result agree; a gradient runs from output (left) to result (right). Grey means there is no data. "
             "The scoring covers what DevRel controls (events, content it creates and organic results); paid media is shown for context and is not scored. Accounts influenced uses growth in total corporate accounts reached through Luma (a proxy); the change in new accounts is in the note. Rows can be overridden by hand in stoplight.json.")
    return (f'<section class="stoplight"><h2>Quarter at a glance</h2><table class="sl"><tr><th>KPI / Activity</th><th>Status</th><th>Notes</th></tr>'
            f'{"".join(body)}</table><p class="foot">{esc(rules)}</p></section>')


# ---------------------------------------------------------------- sections

def blog_section(wp):
    c, p, ch = wp["current"], wp["previous"], wp["change"]
    tiles = "".join([
        tile("Posts published", c["posts_published"], p["posts_published"], ch["posts_published"]),
        tile("Blog views", c["views"], p["views"], ch["views"], note="All pages on blog.postman.com"),
        tile("Site views per post published", c["views_per_published_post"], p["views_per_published_post"],
             q.pct_change(c["views_per_published_post"], p["views_per_published_post"]), note="All blog views divided by posts published"),
        na_tile("Paid vs organic", "Jetpack UTM stats are blocked by the blog's plan; blog traffic is not split"),
    ])
    chart = line_chart("Blog views per week", [("This period", c["weekly_views"], ORANGE, False), ("Previous period", p["weekly_views"], PREV, True)], c["start"])
    rows = "".join(f'<tr><td><a href="{esc(t["url"])}">{esc(html.unescape(t["title"]))}</a></td><td class="r">{n(t["views"])}</td></tr>' for t in c["top_posts"])
    return (f'<section><h2>Blog</h2><div class="tiles">{tiles}</div>{chart}<h3>Top posts by views in the period</h3>'
            f'<table><tr><th>Post</th><th class="r">Views</th></tr>{rows}</table><p class="foot">{esc(c["top_posts_note"])}.</p></section>')


def youtube_section(yt):
    c, p, ch = yt["current"], yt["previous"], yt["change"]
    cl, cs, pl, ps = c["formats"]["long_form"], c["formats"]["shorts"], p["formats"]["long_form"], p["formats"]["shorts"]
    tiles = "".join([
        tile("Videos published", len(c["videos"]), len(p["videos"]), q.pct_change(len(c["videos"]), len(p["videos"]))),
        tile("Total views", c["totals"]["views"], p["totals"]["views"], ch["total.views"], note="Paid and organic combined"),
        tile("Organic views", c["totals"]["organic_views"], p["totals"]["organic_views"], ch["total.organic_views"]),
        tile("Paid views (ads)", c["totals"]["paid_views"], p["totals"]["paid_views"], ch["total.paid_views"]),
        tile("Watch time (hours)", round(c["totals"]["watch_minutes"] / 60), round(p["totals"]["watch_minutes"] / 60), ch["total.watch_minutes"]),
        tile("Net new subscribers", c["subscribers"]["net"], p["subscribers"]["net"], ch["subscribers_net"], note=f"{n(yt['subscribers_total_now'])} subscribers now"),
        na_tile("Impressions and CTR", "Not exposed by the YouTube Analytics API; available in YouTube Studio only"),
    ])
    org = line_chart("Organic views per week: Shorts vs long-form", [
        ("Shorts", cs["weekly_organic_views"], ORANGE, False), ("Long-form", cl["weekly_organic_views"], GREEN, False),
        ("Shorts (previous)", ps["weekly_organic_views"], ORANGE, True), ("Long-form (previous)", pl["weekly_organic_views"], GREEN, True)], c["start"])
    paid_c = [a + b for a, b in zip(cs["weekly_paid_views"], cl["weekly_paid_views"])]
    paid_p = [a + b for a, b in zip(ps["weekly_paid_views"], pl["weekly_paid_views"])]
    paid = line_chart("Paid (ad) views per week, all formats", [("This period", paid_c, ORANGE, False), ("Previous period", paid_p, PREV, True)], c["start"])
    subs = line_chart("Net new YouTube subscribers per week", [("This period", c["subscribers"]["weekly_net"], ORANGE, False),
                                                              ("Previous period", p["subscribers"]["weekly_net"], PREV, True)], c["start"])
    ad_rows = "".join(f'<tr><td>{esc(a["format"])}</td><td class="r">{n(a["views"])}</td></tr>' for a in c["paid_ad_formats"])
    src_rows = "".join(f'<tr><td>{esc(s["source"])}</td><td class="r">{n(s["views"])}</td></tr>' for s in c["traffic_sources"][:6])
    return (f'<section><h2>YouTube</h2><div class="tiles">{tiles}</div>{org}{paid}{subs}'
            f'<div class="two"><div><h3>Traffic sources</h3><table><tr><th>Source</th><th class="r">Views</th></tr>{src_rows}</table></div>'
            f'<div><h3>Paid ad formats</h3><table><tr><th>Format</th><th class="r">Views</th></tr>{ad_rows}</table></div></div>'
            f'<p class="foot">Paid is the ADVERTISING traffic source. Organic is total minus paid. Subscribers cannot be split by traffic source.</p></section>')


def compare_section(yt, tp=None):
    c, ch, vs = yt["current"], yt["change"], yt["current"]["video_summary"]
    cl, cs = c["formats"]["long_form"], c["formats"]["shorts"]

    def row(label, a, b, key=None, digits=0):
        da = delta(ch.get(f"shorts.{key}")) if key else ""
        db = delta(ch.get(f"long_form.{key}")) if key else ""
        return f'<tr><td>{esc(label)}</td><td class="r">{n(a, digits)} {da}</td><td class="r">{n(b, digits)} {db}</td></tr>'
    rows = "".join([
        row("Videos published", vs["shorts"]["published"], vs["long_form"]["published"]),
        row("Views", cs["views"], cl["views"], "views"), row("Organic views", cs["organic_views"], cl["organic_views"], "organic_views"),
        row("Watch minutes", cs["watch_minutes"], cl["watch_minutes"], "watch_minutes"),
        row("Avg view duration (s)", cs["avg_view_duration_s"], cl["avg_view_duration_s"], digits=1),
        row("Organic avg view duration (s)", cs["organic_avg_view_duration_s"], cl["organic_avg_view_duration_s"], digits=1),
        row("Subscribers gained", cs["subscribers_gained"], cl["subscribers_gained"], "subscribers_gained"),
        row("Median views per video", vs["shorts"]["median_views"], vs["long_form"]["median_views"]),
        row("Median organic views per video", vs["shorts"]["median_organic_views"], vs["long_form"]["median_organic_views"]),
    ])
    bars = "".join([stack_bar("Views", cs["paid_views"], cs["organic_views"], "Shorts"), stack_bar("Views", cl["paid_views"], cl["organic_views"], "Long-form"),
                    stack_bar("Watch minutes", cs["paid_watch_minutes"], cs["organic_watch_minutes"], "Shorts"),
                    stack_bar("Watch minutes", cl["paid_watch_minutes"], cl["organic_watch_minutes"], "Long-form")])
    tot, org = cs["views"] + cl["views"], cs["organic_views"] + cl["organic_views"]
    share = (f'<p class="foot">Shorts are {cs["views"] / tot * 100:.0f}% of total views and {cs["organic_views"] / org * 100:.0f}% of organic views.</p>') if tot and org else ""
    buckets = tp["current"]["video"]["by_length"] if tp else vs["by_length"]
    lrows = "".join(f'<tr><td>{esc(b["bucket"])}</td><td class="r">{b["pieces"]}</td><td class="r">{n(b["median_organic_views"]) if b["median_organic_views"] is not None else "too few"}</td></tr>'
                    for b in buckets)
    excl_note = (" Paid ad creatives, localized duplicates and event recordings are left out of the length table, so it describes organic content only."
                 if tp else "")
    ads = sum(1 for v in (tp or {}).get("current", {}).get("video", {}).get("excluded", []) if str(v["why"]).startswith("paid ad creative"))
    shorts_n = c["video_summary"]["shorts"]["published"]
    note = (f'<p class="warn" style="margin:0 0 14px">All {shorts_n} Shorts published this period are paid ad creatives, so the Shorts column describes ads, not content, '
            f'and the two formats are not like for like.</p>') if tp and shorts_n and ads >= shorts_n else ""
    return (f'<section><h2>Shorts vs long-form</h2>{note}<div class="legend top"><span class="lg"><i style="background:{ORANGE}"></i>Paid</span>'
            f'<span class="lg"><i style="background:{GREEN}"></i>Organic</span></div>{bars}'
            f'<table><tr><th></th><th class="r">Shorts</th><th class="r">Long-form</th></tr>{rows}</table>{share}'
            f'<h3>Organic views by video length (videos published in the period)</h3><table><tr><th>Length</th><th class="r">Videos</th><th class="r">Median organic views</th></tr>{lrows}</table>'
            f'<p class="foot">Percent changes are against the previous period. Live streams are excluded. Fewer than 3 videos in a bucket is shown as "too few".{esc(excl_note)}</p></section>')


def channels_rows(d, ci):
    """Rows for the Channels table: (channel, measure, current, previous, source/note, digits)."""
    ci = ci or {}
    rows = []
    lu, yt = d.get("luma"), d.get("youtube")
    if lu:
        c, p = lu["current"], lu["previous"]
        rows += [("Luma meetups", "Events held", c["events"], p["events"], "Luma API", 0),
                 ("Luma meetups", "Registered", c["registered"], p["registered"], "Luma API", 0),
                 ("Luma meetups", "Attended", c["attended"], p["attended"], "Luma API", 0)]
    if yt and yt["current"].get("live"):
        c, p = yt["current"]["live"], yt["previous"]["live"]
        rows += [("YouTube Live", "Streams started in the period", c["streams_started"], p["streams_started"], "YouTube Data API", 0),
                 ("YouTube Live", "Views on live content (includes replays and older archives)", c["views"], p["views"], "YouTube Analytics", 0),
                 ("YouTube Live", "Watch time (hours)", round(c["watch_minutes"] / 60), round(p["watch_minutes"] / 60), "YouTube Analytics", 0),
                 ("YouTube Live", "Subscribers gained", c["subscribers_gained"], p["subscribers_gained"], "YouTube Analytics", 0)]
    mc = d.get("mailchimp")
    if mc:
        c, p = mc["current"], mc["previous"]
        s_ = "Mailchimp Reports API"
        rows += [("Email newsletter (Mailchimp)", "Newsletters sent", c["newsletters"], None, s_, 0),
                 ("Email newsletter (Mailchimp)", "Emails sent", c["recipients"], None, s_, 0),
                 ("Email newsletter (Mailchimp)", "Unique opens (inflated by Apple Mail Privacy Protection)", c["unique_opens"], None, s_, 0),
                 ("Email newsletter (Mailchimp)", "Unique clickers", c["unique_clickers"], None, s_, 0),
                 ("Email newsletter (Mailchimp)", "Click rate (%)", c["click_rate_pct"], None, s_, 1),
                 ("Email newsletter (Mailchimp)", "Unsubscribes", c["unsubscribed"], None, s_, 0)]
    li = d.get("linkedin")
    if li:
        c, p = li["current"], li["previous"]

        def typ(per, kind, field):
            """Value for a content type, or None when LinkedIn lists no organic posts for that period (unavailable, not zero)."""
            if not per["available"]:
                return None
            return (per["types"].get(kind) or {}).get(field, 0)
        src = "LinkedIn Events API"
        ps_ = "LinkedIn post statistics (organic posts listed from " + str(li["organic_history_from"]) + ")"
        rows += [("LinkedIn Live webinars", "Webinars held", c["events"]["linkedin_live"], p["events"]["linkedin_live"], src, 0),
                 ("LinkedIn Live webinars", "Webinar posts", typ(c, "webinar", "posts"), typ(p, "webinar", "posts"), ps_, 0),
                 ("LinkedIn Live webinars", "Webinar post impressions", typ(c, "webinar", "impressions"), typ(p, "webinar", "impressions"), ps_, 0),
                 ("LinkedIn Live webinars", "Webinar post reactions and comments",
                  (typ(c, "webinar", "reactions") or 0) + (typ(c, "webinar", "comments") or 0) if c["available"] else None,
                  (typ(p, "webinar", "reactions") or 0) + (typ(p, "webinar", "comments") or 0) if p["available"] else None, ps_, 0),
                 ("LinkedIn Live webinars", "Registrants", None, None, "Not available from the LinkedIn API; enter from Event Manager in channels-input.json", 0),
                 ("LinkedIn Live webinars", "Viewers or attendees", None, None, "Not available from the LinkedIn API; enter from Event Manager in channels-input.json", 0),
                 ("LinkedIn newsletter", "Edition post impressions", typ(c, "newsletter", "impressions"), typ(p, "newsletter", "impressions"), ps_, 0),
                 ("LinkedIn newsletter", "Edition post reactions and comments",
                  (typ(c, "newsletter", "reactions") or 0) + (typ(c, "newsletter", "comments") or 0) if c["available"] else None,
                  (typ(p, "newsletter", "reactions") or 0) + (typ(p, "newsletter", "comments") or 0) if p["available"] else None, ps_, 0),
                 ("Reshared blog posts on LinkedIn", "Posts", typ(c, "blog_reshare", "posts"), typ(p, "blog_reshare", "posts"), ps_, 0),
                 ("Reshared blog posts on LinkedIn", "Impressions", typ(c, "blog_reshare", "impressions"), typ(p, "blog_reshare", "impressions"), ps_, 0),
                 ("Reshared blog posts on LinkedIn", "Clicks", typ(c, "blog_reshare", "clicks"), typ(p, "blog_reshare", "clicks"), ps_, 0)]
    spec = ([] if li else [("linkedin_live", "LinkedIn Live webinars", [("events", "Webinars held"), ("registrants", "Registrants"), ("viewers", "Viewers or attendees"), ("peak_viewers", "Peak concurrent viewers")])])
    spec += [("linkedin_newsletter", "LinkedIn newsletter", [("editions", "Editions published"), ("subscribers", "Subscribers"), ("article_views", "Article views")] + ([] if li else [("reactions", "Reactions"), ("comments", "Comments")]))]
    for key, name, measures in spec:
        entry = ci.get(key) or {}
        cur, prev = entry.get("current") or {}, entry.get("previous") or {}
        for field, label in measures:
            if field in cur or field in prev or not entry:
                rows.append((name, label, cur.get(field), prev.get(field), entry.get("source") or ("Not available from the Luma API; enter in channels-input.json" if key.startswith("luma") else "Not available from the LinkedIn API; enter from LinkedIn analytics in channels-input.json"), 0))
    order = ["Luma meetups", "YouTube Live", "LinkedIn Live webinars", "Email newsletter (Mailchimp)", "Luma newsletters", "LinkedIn newsletter", "Reshared blog posts on LinkedIn"]
    rows.sort(key=lambda r: order.index(r[0]) if r[0] in order else len(order))  # stable: groups meetups, webinars, newsletters, reshares
    return rows


def _stat(label, cur, prev, digits=0, suffix=""):
    """One headline number with a delta pill and a small this-vs-previous bar."""
    value = "n/a" if cur is None else f"{n(cur, digits)}{suffix}"
    pct = q.pct_change(cur, prev) if (cur is not None and prev not in (None, 0)) else None
    if prev is None:
        prev_txt = "no previous data"
    else:
        prev_txt = f"vs {n(prev, digits)}{suffix}"
    top = max([x for x in (cur, prev) if x], default=0)
    bars = ""
    if top and prev is not None and cur is not None:  # a bar pair only where there is something to compare
        bars = (f'<div class="mini"><span class="m-cur" style="width:{cur / top * 100:.0f}%"></span></div>'
                f'<div class="mini"><span class="m-prev" style="width:{prev / top * 100:.0f}%"></span></div>')
    return (f'<div class="cs"><div class="csl">{esc(label)}</div><div class="csv">{value}</div>'
            f'<div class="csd">{delta(pct) if pct is not None else ""}<span class="csp">{esc(prev_txt)}</span></div>{bars}</div>')


def channel_cards(d, ci):
    """Cards grouped by type. Each card: (group, name, status, stats, note)."""
    ci = ci or {}
    cards = []
    lu, yt, li, mc = d.get("luma"), d.get("youtube"), d.get("linkedin"), d.get("mailchimp")

    def status(cur, prev, manual=False):
        if cur is None or cur == 0:
            return ("Inactive", "inactive")
        if prev is None:
            return ("No previous data", "nodata")
        if prev == 0:
            return ("New this period", "new")
        return ("Established", "est")
    if lu:
        c, p = lu["current"], lu["previous"]
        cards.append(("Events and webinars", "Luma meetups", status(c["events"], p["events"]),
                      [("Events held", c["events"], p["events"]), ("Registered", c["registered"], p["registered"]), ("Attended", c["attended"], p["attended"])],
                      "Luma API. Events and registrations are down; the other channels below are new or recent."))
    if yt and yt["current"].get("live"):
        c, p = yt["current"]["live"], yt["previous"]["live"]
        cards.append(("Events and webinars", "YouTube Live", status(c["streams_started"], p["streams_started"]),
                      [("Live streams started", c["streams_started"], p["streams_started"]), ("Views on live content", c["views"], p["views"]),
                       ("Subscribers gained", c["subscribers_gained"], p["subscribers_gained"])],
                      "Views include replays and older archives. Streamed from Riverside to YouTube and LinkedIn, so the audiences may overlap."))
    if li:
        c, p = li["current"], li["previous"]
        g = lambda per, k, f: ((per["types"].get(k) or {}).get(f, 0) if per["available"] else None)  # noqa: E731
        rc = lambda per, k: (g(per, k, "reactions") or 0) + (g(per, k, "comments") or 0) if per["available"] else None  # noqa: E731
        cards.append(("Events and webinars", "LinkedIn Live webinars", status(c["events"]["linkedin_live"], p["events"]["linkedin_live"]),
                      [("Webinars held", c["events"]["linkedin_live"], p["events"]["linkedin_live"]), ("Webinar post impressions", g(c, "webinar", "impressions"), g(p, "webinar", "impressions")),
                       ("Reactions and comments", rc(c, "webinar"), rc(p, "webinar"))],
                      "Registrants and viewers are not in LinkedIn's API. Post statistics start Aug 24."))
    if mc:
        c, p = mc["current"], mc["previous"]
        cards.append(("Newsletters", "Mailchimp newsletter", ("Moved here from Luma", "nodata"),
                      [("Newsletters sent", c["newsletters"], None), ("Unique clickers", c["unique_clickers"], None), ("Click rate", c["click_rate_pct"], None, 1, "%")],
                      "Newsletters now go only through Mailchimp (first real send Oct 1), so there is no comparable previous period. Open rates are inflated by Apple Mail Privacy Protection, so clicks lead."))
    ni = ci.get("linkedin_newsletter") or {}
    if li or ni:
        nc, np_ = ni.get("current") or {}, ni.get("previous") or {}
        c, p = (li["current"], li["previous"]) if li else ({"available": False, "types": {}}, {"available": False, "types": {}})
        g = lambda per, k, f: ((per["types"].get(k) or {}).get(f, 0) if per["available"] else None)  # noqa: E731
        cards.append(("Newsletters", "LinkedIn newsletter", status(nc.get("editions"), np_.get("editions")),
                      [("Editions published", nc.get("editions"), np_.get("editions")), ("Edition post impressions", g(c, "newsletter", "impressions"), g(p, "newsletter", "impressions")),
                       ("Reactions and comments", ((g(c, "newsletter", "reactions") or 0) + (g(c, "newsletter", "comments") or 0)) if c["available"] else None, None)],
                      "Subscribers and article views are not available from LinkedIn's API."))
    if li:
        c, p = li["current"], li["previous"]
        g = lambda per, k, f: ((per["types"].get(k) or {}).get(f, 0) if per["available"] else None)  # noqa: E731
        cards.append(("Social reshares", "Reshared blog posts on LinkedIn", status(g(c, "blog_reshare", "posts"), g(p, "blog_reshare", "posts")),
                      [("Posts reshared", g(c, "blog_reshare", "posts"), g(p, "blog_reshare", "posts")), ("Impressions", g(c, "blog_reshare", "impressions"), g(p, "blog_reshare", "impressions")),
                       ("Link clicks", g(c, "blog_reshare", "clicks"), g(p, "blog_reshare", "clicks"))],
                      f"Organic posts are listed from {li['organic_history_from']}, so earlier periods have no data. Reshares with the link only in a comment are not counted."))
    return cards


def channels_section(d, ci):
    cards = channel_cards(d, ci)
    if not cards:
        return ""
    count = lambda cls: sum(1 for c in cards if c[2][1] == cls)  # noqa: E731
    chips = "".join(f'<span class="chip {cls}"><b>{k}</b> {esc(txt)}</span>' for k, cls, txt in [
        (len([c for c in cards if c[2][1] != "inactive"]), "all", "channels active this period"),
        (count("new"), "new", "new this period"), (count("est"), "est", "established"), (count("nodata"), "nodata", "with no previous-period data")] if k)
    out = []
    for group in ("Events and webinars", "Newsletters", "Social reshares"):
        gcards = [c for c in cards if c[0] == group]
        if not gcards:
            continue
        html_cards = "".join(
            f'<div class="chan"><div class="chan-h"><div class="chan-n">{esc(c[1])}</div><span class="badge {c[2][1]}">{esc(c[2][0])}</span></div>'
            f'<div class="stats">{"".join(_stat(*s) for s in c[3])}</div><div class="chan-note">{esc(c[4])}</div></div>' for c in gcards)
        out.append(f'<h3 class="grp">{esc(group)}</h3><div class="chan-grid">{html_cards}</div>')
    table = channels_rows(d, ci)
    body = []
    last = None
    for ch_, measure, cur, prev, src, dg in table:
        name_cell = esc(ch_) if ch_ != last else ""
        last = ch_
        body.append(f'<tr><td><strong>{name_cell}</strong></td><td>{esc(measure)}</td><td class="r">{n(cur, dg)}</td><td class="r">{n(prev, dg)}</td>'
                    f'<td class="r">{delta(q.pct_change(cur, prev))}</td><td class="src">{esc(src)}</td></tr>')
    notes = (ci or {}).get("notes") or []
    note_html = "".join(f'<p class="foot">{esc(t)}</p>' for t in notes)
    return (f'<section><h2>Channels</h2><p class="foot" style="margin-top:0">Where engagement comes from beyond Luma meetups. Each card shows three headline numbers, this period (orange bar) against the previous period (grey bar). '
            f'A blank value means the number is not available, not zero.</p><div class="chips">{chips}</div>{"".join(out)}'
            f'<details class="alltable"><summary>All measures, with sources</summary><table><tr><th>Channel</th><th>Measure</th><th class="r">This period</th><th class="r">Previous</th><th class="r">Change</th><th>Source</th></tr>{"".join(body)}</table></details>'
            f'<p class="foot">Webinars are produced in Riverside and streamed to YouTube and LinkedIn, so those audiences are not added together.</p>{note_html}</section>')


def direction_section(md):
    """'Where we are going': the team's own words from direction.md, shown as written.

    HTML comments are dropped, headings with nothing under them are skipped, and with no text at all the chapter is
    left out. A line 'Status: DRAFT' adds a banner. This file is written by people; nothing here is generated."""
    if not md:
        return ""
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    draft = bool(re.search(r"(?im)^status:\s*draft", md))
    md = re.sub(r"(?im)^status:.*\n?", "", md)
    blocks, head, lines = [], None, []
    for line in md.splitlines():
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            if lines:
                blocks.append((head, lines))
            head, lines = line, []
        elif line.strip():
            lines.append(line)
    if lines:
        blocks.append((head, lines))
    kept = ["\n".join(([h_] if h_ else []) + ["", *ls, ""]) for h_, ls in blocks]
    if not kept:
        return ""
    banner = '<p class="draft">Draft: the team is still writing this section.</p>' if draft else ""
    return f'<section><h2>Where we are going</h2>{banner}<div class="dir">{md_to_html(chr(10).join(kept))}</div></section>'


def mailchimp_section(mc):
    c, p = mc["current"], mc["previous"]
    rows = "".join(f'<tr><td>{esc(r["date"])}</td><td>{esc(r["subject"][:80])}</td><td class="r">{n(r["sent"])}</td><td class="r">{r["open_rate_pct"]}%</td>'
                   f'<td class="r">{n(r["unique_clickers"])} ({r["click_rate_pct"]}%)</td><td class="r">{n(r["unsubscribed"])}</td><td class="r">{n(r["bounces"])}</td></tr>' for r in c["campaigns"])
    tiles = "".join([
        tile("Newsletters sent", c["newsletters"]),
        tile("Emails sent", c["recipients"]),
        tile("Unique clickers", c["unique_clickers"], note=f"Click rate {n(c['click_rate_pct'], 1)}%"),
        tile("Unique opens", c["unique_opens"], note=f"Open rate {n(c['open_rate_pct'], 1)}% (inflated by Apple Mail Privacy Protection)"),
        tile("Unsubscribes", c["unsubscribed"]),
        tile("Audience size", mc["audience_members_now"], None, None, note="Subscribed now"),
    ])
    return (f'<section><h2>Newsletters (Mailchimp)</h2><div class="tiles">{tiles}</div>'
            f'<table><tr><th>Sent</th><th>Subject</th><th class="r">Emails</th><th class="r">Open rate</th><th class="r">Clickers</th><th class="r">Unsubscribed</th><th class="r">Bounces</th></tr>{rows}</table>'
            f'<p class="foot">Newsletters now go only through Mailchimp. The first real send was Oct 1 (Sep 29 was an 8-person test), so there is no comparable previous period; '
            f'earlier editions were sent another way and are not in this report. Test sends under {mc["scope"]["min_recipients"]} recipients are skipped ({c["tests_or_out_of_scope_skipped"]} this period).</p></section>')


def linkedin_section(li):
    c, p = li["current"], li["previous"]
    labels = {"blog_reshare": "Reshared blog posts", "newsletter": "Newsletter edition", "webinar": "Webinars and live sessions"}
    val = lambda per, k, f: n((per["types"].get(k) or {}).get(f, 0)) if per["available"] else "n/a"  # noqa: E731
    head = ('<tr><th>Content</th><th class="r">Posts</th><th class="r">Impressions</th><th class="r">Unique</th><th class="r">Clicks</th>'
            '<th class="r">Reactions</th><th class="r">Comments</th><th class="r">Shares</th></tr>')
    body = "".join(f'<tr><td>{esc(labels[k])}</td>' + "".join(f'<td class="r">{val(c, k, f)}</td>' for f in ("posts", "impressions", "unique_impressions", "clicks", "reactions", "comments", "shares")) + "</tr>"
                   for k in labels)
    prev = "".join(f'<tr><td>{esc(labels[k])}</td>' + "".join(f'<td class="r">{val(p, k, f)}</td>' for f in ("posts", "impressions", "unique_impressions", "clicks", "reactions", "comments", "shares")) + "</tr>"
                   for k in labels)
    tops = []
    for k in labels:
        rows_ = (c["types"].get(k) or {}).get("top", [])[:3]
        if rows_:
            items = "".join(f'<tr><td>{esc(r["day"])}</td><td>{esc(r["title"][:84])}</td><td class="r">{n(r["impressions"])}</td><td class="r">{n(r["reactions"])}</td><td class="r">{n(r["comments"])}</td></tr>' for r in rows_)
            tops.append(f'<h3>{esc(labels[k])}: top posts by impressions</h3><table><tr><th>Date</th><th>Post</th><th class="r">Impressions</th><th class="r">Reactions</th><th class="r">Comments</th></tr>{items}</table>')
    cov = (f'LinkedIn lists organic posts only from {li["organic_history_from"]}, so figures for this period cover {max(li["organic_history_from"], c["start"])} to {c["end"]}. '
           f'The previous period has no per-post data, so it shows n/a, not zero.')
    return (f'<section><h2>LinkedIn: reshared blog posts, newsletter and webinars</h2><p class="foot" style="margin-top:0">Scoped to the three kinds of DevRel content on the page. '
            f'Page-wide totals, ads and other posts are left out. {esc(cov)}</p>'
            f'<h3>This period</h3><table>{head}{body}</table><h3>Previous period</h3><table>{head}{prev}</table>{"".join(tops)}'
            f'<p class="foot">Posts are matched by rules: a blog reshare links to blog.postman.com (directly or through a lnkd.in link), a newsletter post references an edition or the Dev Digest, '
            f'and a webinar post references a live video or announces a webinar or live session. A blog post shared with the link only in a comment is not counted, so reshares are a floor. '
            f'{esc(li["not_available"])}</p></section>')


def paid_topics_section(tp):
    tv = tp["current"].get("top_videos")
    if not tv:
        return ""
    prev = {a["category"]: a for a in tp["previous"].get("top_videos", {}).get("by_category", [])}
    cat = "".join(f'<tr><td>{esc(a["category"])}</td><td class="r">{a["videos"]}</td><td class="r">{n(a["paid_views"])}</td><td class="r">{n(a["organic_views"])}</td>'
                  f'<td class="r">{n(a["paid_share_pct"], 0)}%</td></tr>' for a in tv["by_category"])
    top = "".join(f'<tr><td>{esc(r["title"][:62])}</td><td>{esc(r["published"])}</td><td>{esc(r["category"])}</td><td class="r">{n(r["paid_views"])}</td><td class="r">{n(r["organic_views"])}</td></tr>'
                  for r in sorted(tv["rows"], key=lambda r: -r["views"])[:12])
    return (f'<section><h2>Where paid and organic views go</h2><p class="foot" style="margin-top:0">The most-viewed videos in the period, whenever they were published, '
            f'with views split into paid (YouTube ads) and organic and grouped by topic. Ads on other platforms are not visible here.</p>'
            f'<h3>By topic</h3><table><tr><th>Topic</th><th class="r">Videos</th><th class="r">Paid views</th><th class="r">Organic views</th><th class="r">Paid share</th></tr>{cat}</table>'
            f'<h3>Top videos</h3><table><tr><th>Video</th><th>Published</th><th>Topic</th><th class="r">Paid</th><th class="r">Organic</th></tr>{top}</table></section>')


def geo_counts(event_list):
    def label(e, field):
        if e[field]:
            return f"{e['city']}, {e['country']}" if field == "city" else e["country"]
        return "Online" if e.get("location_type") == "online" else "Location not set in Luma"
    by_city, by_country = {}, {}
    for e in event_list:
        by_city[label(e, "city")] = by_city.get(label(e, "city"), 0) + 1
        by_country[label(e, "country")] = by_country.get(label(e, "country"), 0) + 1
    srt = lambda x: dict(sorted(x.items(), key=lambda kv: -kv[1]))  # noqa: E731
    return srt(by_city), srt(by_country)


def luma_section(lu, sh):
    c, p, ch, ct = lu["current"], lu["previous"], lu["change"], lu["contacts"]
    tiles = [tile("Events held", c["events"], p["events"], ch["events"]), tile("Registered", c["registered"], p["registered"], ch["registered"]),
             tile("Attended", c["attended"], p["attended"], ch["attended"]),
             tile("Attendance rate", c["attendance_rate_pct"], p["attendance_rate_pct"], q.pct_change(c["attendance_rate_pct"], p["attendance_rate_pct"]), digits=1, suffix="%"),
             tile("New Luma subscribers", ct["current"]["new"], ct["previous"]["new"], lu["contacts_change_new"], note=f"{n(ct['total_now'])} subscribers now (calendar contacts)")]
    if "new_corporate_domains" in ct["current"]:
        tiles.append(tile("New corporate accounts via Luma", ct["current"]["new_corporate_domains"], ct["previous"]["new_corporate_domains"], lu.get("new_domains_change"),
                          note="Corporate email domains first seen this period (proxy)"))
    if sh and sh["current"]["avg_rating"] is not None:
        sc, sp = sh["current"], sh["previous"]
        tiles.append(tile("Average event rating (out of 5)", sc["avg_rating"], sp["avg_rating"], q.pct_change(sc["avg_rating"], sp["avg_rating"]), digits=2,
                          note=f"{sc['events_rated']} rated events; attendee-weighted {sc['attendee_weighted_rating']}"))
    else:
        tiles.append(na_tile("Average event rating", "Meetup sheet is not connected"))
    chart = line_chart("New Luma subscribers per week", [("This period", ct["current"]["weekly_new"], ORANGE, False), ("Previous period", ct["previous"]["weekly_new"], PREV, True)], c["start"])
    by_city, by_country = geo_counts(c["event_list"])
    geo = "".join(f'<tr><td>{esc(k)}</td><td class="r">{v}</td></tr>' for k, v in by_city.items())
    ctry = "".join(f'<tr><td>{esc(k)}</td><td class="r">{v}</td></tr>' for k, v in by_country.items())
    ev = "".join(f'<tr><td>{esc(e["date"])}</td><td>{esc(e["name"])}</td><td>{esc(e["city"] or ("Online" if e.get("location_type") == "online" else "Not set"))}</td>'
                 f'<td class="r">{e["registered"]}</td><td class="r">{e["attended"]}</td></tr>' for e in c["event_list"])
    subs_chart = ""
    if sh and sh.get("luma_subscribers_by_month"):
        months = sorted(sh["luma_subscribers_by_month"])[-12:]
        subs_chart = line_chart("Luma subscribers at month end (team sheet)", [("Subscribers", [sh["luma_subscribers_by_month"][m] for m in months], ORANGE, False)],
                                labels=[m[2:] for m in months], markers=False, note="From the Luma Subscribers table in the meetup sheet. It tracks the calendar contact count.")
    return (f'<section><h2>Luma events and community</h2><div class="tiles">{"".join(tiles)}</div>{chart}{subs_chart}'
            f'<div class="two"><div><h3>Events by city</h3><table><tr><th>City</th><th class="r">Events</th></tr>{geo}</table></div>'
            f'<div><h3>Events by country</h3><table><tr><th>Country</th><th class="r">Events</th></tr>{ctry}</table></div></div>'
            f'<h3>Events (Luma API)</h3><table><tr><th>Date</th><th>Event</th><th>City</th><th class="r">Registered</th><th class="r">Attended</th></tr>{ev}</table>'
            f'<p class="foot">Geography is by event location. Attendee location is not available from Luma. Luma subscribers are the calendar contact count.</p></section>')


def sheet_section(sh):
    c, p, ch = sh["current"], sh["previous"], sh["change"]
    tiles = "".join([
        tile("Average rating (out of 5)", c["avg_rating"], p["avg_rating"], ch["avg_rating"], digits=2, note=f"{c['events_rated']} of {c['events_in_sheet']} events rated"),
        tile("Meetup spend", c["total_cost"], p["total_cost"], ch["total_cost"], prefix="$", invert=True, note=f"{c['events_with_cost']} events with a cost"),
        tile("Cost per attendee", c["cost_per_attendee"], p["cost_per_attendee"], ch["cost_per_attendee"], digits=2, prefix="$", invert=True,
             note="Events with a cost above $0 and attendance recorded"),
        tile("Zero-cost events", c["zero_cost_events"], p["zero_cost_events"], q.pct_change(c["zero_cost_events"], p["zero_cost_events"]), note="Listed at $0 (co-hosted or sponsored)"),
        tile("Events without data", c["events_without_data"], p["events_without_data"], None, note="No attendance recorded in the sheet"),
    ])
    region = "".join(f'<tr><td>{esc(r)}</td><td class="r">{g["events"]}</td><td class="r">{usd(g["cost"])}</td><td class="r">{usd(g["cost_per_attendee"])}</td></tr>' for r, g in c["by_region"].items())
    pregion = "".join(f'<tr><td>{esc(r)}</td><td class="r">{g["events"]}</td><td class="r">{usd(g["cost_per_attendee"])}</td></tr>' for r, g in p["by_region"].items())
    rows = []
    for e in sorted(c["events"], key=lambda e: e["date"]):
        cpa = (e["cost"] / e["attendees"]) if (e["cost"] and e["attendees"]) else None
        rows.append(f'<tr><td>{esc(e["date"])}</td><td>{esc(e["location"])}</td><td>{esc(e["type"])}</td><td class="r">{n(e["attendees"])}</td>'
                    f'<td class="r">{usd(e["cost"]) if e["cost"] is not None else "n/a"}</td><td class="r">{usd(cpa) if cpa else "n/a"}</td>'
                    f'<td class="r">{e["rating"] if e["rating"] is not None else "n/a"}</td></tr>')
    return (f'<section><h2>Meetup ratings and cost</h2><div class="tiles">{tiles}</div>'
            f'<div class="two"><div><h3>This period by region (events with a cost)</h3><table><tr><th>Region</th><th class="r">Events</th><th class="r">Spend</th><th class="r">Per attendee</th></tr>{region}</table></div>'
            f'<div><h3>Previous period by region</h3><table><tr><th>Region</th><th class="r">Events</th><th class="r">Per attendee</th></tr>{pregion}</table></div></div>'
            f'<h3>Events in the meetup sheet</h3><table><tr><th>Date</th><th>Location</th><th>Type</th><th class="r">Attendees</th><th class="r">Cost</th><th class="r">Per attendee</th><th class="r">Rating</th></tr>{"".join(rows)}</table>'
            f'<p class="foot">Source: the meetup sheet (cost, cost per attendee and rating columns). Blank cells mean not recorded and are excluded, not counted as zero. '
            f'Attendee counts in the sheet differ from Luma check-ins, so totals here will not match the Luma section.</p></section>')


def commonroom_section(cr):
    m, ch = cr["metrics"], cr["change"]
    prev = (cr.get("previous_snapshot") or {}).get("metrics") or {}
    tiles = [
        tile("Accounts influenced", m.get("accounts_influenced"), prev.get("accounts_influenced"), ch.get("accounts_influenced"),
             note=f"Distinct companies among event attendees; {n(m.get('company_coverage_pct'), 1)}% of attendees have a known company"),
        tile("Developers influenced", m["developers_influenced"], prev.get("developers_influenced"), ch.get("developers_influenced"), note="Contacts in the all-events-attended segment"),
        tile("Tier 1 accounts", m.get("tier1_accounts", m.get("organizations_influenced_tier1")), prev.get("tier1_accounts", prev.get("organizations_influenced_tier1")),
             ch.get("organizations_influenced_tier1"), note=f"{n(m.get('tier1_share_of_accounts_pct'), 1)}% of accounts influenced"),
        tile("Economic buyers among attendees", m["economic_buyer_pct"], prev.get("economic_buyer_pct"), ch.get("economic_buyer_pct"), digits=1, suffix="%",
             note=f"{n(m['economic_buyers_among_attendees'])} of {n(m['developers_influenced'])} contacts"),
        na_tile("Overall sentiment", "Room Overview is a UI report with no API aggregate"),
    ]
    groups = m.get("industry_breakdown") or {}
    if m.get("industry_labels"):
        regroup = {}
        for lab, cnt in m["industry_labels"].items():
            g = q.industry_group(lab)
            regroup[g] = regroup.get(g, 0) + cnt
        known = sum(regroup.values())
        unknown = max(0, (m.get("accounts_influenced") or 0) - known)
        if unknown:
            regroup["Industry not recorded"] = unknown
        groups = regroup
    ind = ""
    if groups:
        ordered = sorted(groups.items(), key=lambda kv: (kv[0] in ("Other", "Industry not recorded", "Unknown"), -kv[1]))
        ind = (f'<h3>Accounts influenced by industry</h3><div class="hbars">{hbars(ordered, total=sum(groups.values()))}</div>'
               f'<p class="foot">Grouped from the employer industry label on each attendee\'s current company. One count per account. '
               f'"Industry not recorded" and "Other" are accounts with no label or a label outside the groups.</p>')
    prev_note = (f"Compared with the snapshot {cr['previous_snapshot']['key']}." if cr.get("previous_snapshot") else
                 "No earlier snapshot exists, so there is no change figure yet. This run is saved as the baseline for the next one.")
    return (f'<section><h2>Common Room</h2><div class="tiles">{"".join(tiles)}</div>{ind}<p class="foot">{esc(cr["note"])} {esc(prev_note)}</p></section>')


def topics_section(tp):
    def table(period, kind, key, title):
        rows = []
        cur = tp["current"][kind][key]
        prev = {g["label"]: g for g in tp["previous"][kind][key]}
        for g in cur:
            pg = prev.get(g["label"])
            rows.append(f'<tr><td>{esc(g["label"])}</td><td class="r">{g["pieces"]}</td><td class="r">{n(g["median_metric"]) if g["ranked"] else "too few"}</td>'
                        f'<td class="r">{pg["pieces"] if pg else 0}</td><td class="r">{n(pg["median_metric"]) if pg and pg["ranked"] else "n/a"}</td></tr>')
        return (f'<h3>{esc(title)}</h3><table><tr><th></th><th class="r">Pieces</th><th class="r">Median {"views" if kind == "blog" else "organic views"}</th>'
                f'<th class="r">Prev pieces</th><th class="r">Prev median</th></tr>{"".join(rows)}</table>')
    excl = tp["current"]["video"]["excluded"]
    excl_note = (f' Excluded from video comparisons: {len(excl)} items (paid ad creatives, localized duplicates, event recordings).' if excl else "")
    return (f'<section><h2>Topics and content style</h2><p class="foot" style="margin-top:0">Each piece is tagged by keyword rules on its title (see classify-topics.py), one topic and one style per piece. '
            f'Blog metric: views in the period. Video metric: organic views.{esc(excl_note)}</p>'
            f'{table("c", "blog", "by_topic", "Blog posts by topic")}{table("c", "video", "by_topic", "Videos by topic")}'
            f'{table("c", "blog", "by_style", "Blog posts by style")}{table("c", "video", "by_style", "Videos by style")}'
            f'<p class="foot">A group with fewer than {tp["min_group"]} pieces is not ranked ("too few"). Topic medians are small samples; read them as direction, not proof.</p></section>')


def context_section(events):
    rows = []
    for num, ev in events:
        src = ev.get("source", "")
        link = f'<a href="{esc(src)}">source</a>' if src.startswith("http") else esc(src)
        rows.append(f'<tr><td><span class="mk" style="background:{KIND_COLOR.get(ev["kind"], DIM)}">{num}</span></td><td>{esc(ev["date"])}</td>'
                    f'<td>{esc(KIND_LABEL.get(ev["kind"], ev["kind"]))}</td><td>{esc(ev["label"])}</td><td>{link}</td></tr>')
    return (f'<section><h2>Releases, industry news and campaigns</h2><p class="foot" style="margin-top:0">Numbered markers on the weekly charts above. A marker shows what happened that week. It does not show cause. '
            f'Industry items come from web search of third-party roundups and the MCP specification posts; they are not verified against primary sources.</p>'
            f'<table><tr><th></th><th>Date</th><th>Type</th><th>Event</th><th>Source</th></tr>{"".join(rows)}</table></section>')


def community_section(cm):
    c, p, ch = cm["current"], cm["previous"], cm["change"]
    t = lambda label, k, **kw: tile(label, c[k], p[k], ch[k], **kw)  # noqa: E731
    tiles = "".join([
        t("Joins", "joins"), t("Net new members", "net_members", note=f"{n(c['members_end'])} members at the end"),
        tile("Active members per month", c["active_members_avg"], p["active_members_avg"], ch["active_members_avg"], digits=1, note="Average of the monthly counts"),
        tile("Active rate", c["active_rate_pct"], p["active_rate_pct"], ch["active_rate_pct"], digits=2, suffix="%", note="Active members divided by total members"),
        t("Help topics", "help_topics", note=f"{n(c['answer_rate_pct'], 0)}% answered"),
        t("Staff and bot replies", "staff_bot_replies"),
        tile("Retention", c["retention_pct"], p["retention_pct"], ch["retention_pct"], digits=2, suffix="%", note="Average monthly retention"),
        t("Event attendee roles granted", "event_roles_granted", note=f"{n(c['event_role_holders'])} members hold the role now"),
    ])
    lab = [f"Month {i}" for i in range(1, len(c["monthly"]) + 1)]
    ser = lambda key, name, colour: [(name, [m[key] for m in c["monthly"]], colour, False), (name + " (previous)", [m[key] for m in p["monthly"]], PREV, True)]  # noqa: E731
    charts = (line_chart("Joins per month", ser("joins", "Joins", ORANGE), labels=lab, markers=False)
              + line_chart("Active members per month", ser("active", "Active members", GREEN), labels=lab, markers=False))
    lift = ""
    if c["liftoff_cohort"]:
        lift = (f'<h3>Liftoff onboarding</h3><p class="foot" style="margin-top:0">{n(c["liftoff_cohort"])} members joined the World Explorer module '
                f'({pc_text(ch["liftoff_cohort"])} vs {n(p["liftoff_cohort"])}); {n(c["liftoff_started"])} started ({n(c["liftoff_start_rate_pct"], 1)}%) and '
                f'{n(c["liftoff_completed"])} completed it.</p>')
    return (f'<section><h2>Owned community</h2><p class="foot" style="margin-top:0">Discord, from the community dashboard. Whole calendar months: '
            f'{", ".join(c["months"])} against {", ".join(p["months"])}. Active members is a very small share of the community, so read it as a trend, not a level.</p>'
            f'<div class="tiles">{tiles}</div>{charts}{lift}</section>')


def cost_line(cost):
    if not cost or not cost.get("available"):
        return "Claude token usage and cost for this report: not available (session transcript not found)."
    t = cost["tokens"]
    writes = t["cache_write_5m"] + t["cache_write_1h"]
    money = f"about ${cost['cost_usd']:,.2f}" if cost.get("cost_usd") is not None else "dollar cost not estimated (model not in the price table)"
    model = ", ".join(sorted(m for m in cost["models"] if m))
    through = (cost.get("counted_through") or "")[:16].replace("T", " ")
    return (f"Produced with Claude ({model}): {n(cost['total_tokens'])} tokens ({n(t['input'])} input, {n(writes)} cache writes, {n(t['cache_read'])} cache reads, "
            f"{n(t['output'])} output), {money} at API list prices. Counts {cost['scope']}, through {through} UTC. Estimate only: main session, no sub-agents, not an invoice.")


def not_connected(key, errors):
    return f'<section><h2>{SOURCES[key]}</h2><p class="warn">Not connected: {esc(errors.get(key, "no data was pulled"))}</p></section>'


def build_md(d, start, end, insights, tp, ctx, rows_sl, cost, recs=None, ci=None, tldr=""):
    recs = recs or {}
    R = lambda k: ([f"**Recommendation:** {recs[k]}", ""] if recs.get(k) else [])  # noqa: E731
    wp, yt, lu, sh, cr = (d.get(k) for k in ("wp", "youtube", "luma", "sheet", "commonroom"))
    L = [f"# QBR metrics: {start} to {end}", ""] + (["## TL;DR", "", tldr.strip(), ""] if tldr else []) + ["## Quarter at a glance", "| KPI / Activity | Status | Notes |", "|---|---|---|"]
    for name, signals, note in rows_sl:
        _, label = status_cell(signals)
        L.append(f"| {name} | {label} | {note} |")
    L += [""] + R("stoplight")
    rs_ = reach_stats(d, tp)
    if "blog" in rs_ or "video" in rs_:
        L.append("## Reach per piece")
        for kind in ("blog", "video"):
            if kind in rs_:
                c_, p_ = rs_[kind]["current"], rs_[kind]["previous"]
                L.append(f"- {kind.capitalize()}: median {n(c_['median'])} (prev {n(p_['median'])}); top 3 are {n(c_['top3_share'], 1)}% of views (prev {n(p_['top3_share'], 1)}%); {c_['under_100']} pieces under 100 (prev {p_['under_100']})")
        L += [""] + R("reach")
    ch_rows = channels_rows(d, ci)
    if ch_rows:
        L += ["## Channels", "| Channel | Measure | This period | Previous | Source |", "|---|---|---|---|---|"]
        L += [f"| {c_} | {m_} | {n(a_, dg)} | {n(b_, dg)} | {s_} |" for c_, m_, a_, b_, s_, dg in ch_rows]
        L += [""] + R("channels")
    if wp:
        c, p, ch = wp["current"], wp["previous"], wp["change"]
        L += ["## Blog", f"- Posts published: {n(c['posts_published'])} (prev {n(p['posts_published'])}, {pc_text(ch['posts_published'])})",
              f"- Blog views: {n(c['views'])} (prev {n(p['views'])}, {pc_text(ch['views'])})", "- Paid vs organic: not available (Jetpack UTM blocked by plan)", ""] + R("blog")
    if yt:
        c, p, ch = yt["current"], yt["previous"], yt["change"]
        cl, cs = c["formats"]["long_form"], c["formats"]["shorts"]
        L += ["## YouTube", f"- Videos published: {len(c['videos'])} (prev {len(p['videos'])})",
              f"- Total views: {n(c['totals']['views'])} (prev {n(p['totals']['views'])}, {pc_text(ch['total.views'])})",
              f"- Organic views: {n(c['totals']['organic_views'])} (prev {n(p['totals']['organic_views'])}, {pc_text(ch['total.organic_views'])})",
              f"- Paid views: {n(c['totals']['paid_views'])} (prev {n(p['totals']['paid_views'])}, {pc_text(ch['total.paid_views'])})",
              f"- Net new subscribers: {n(c['subscribers']['net'])} (prev {n(p['subscribers']['net'])}); {n(yt['subscribers_total_now'])} now",
              "- Impressions and CTR: not available (YouTube Analytics API does not expose them)", ""] + R("youtube") + ["### Shorts vs long-form", "| | Shorts | Long-form |", "|---|---|---|",
              f"| Videos published | {c['video_summary']['shorts']['published']} | {c['video_summary']['long_form']['published']} |",
              f"| Views | {n(cs['views'])} ({pc_text(ch['shorts.views'])}) | {n(cl['views'])} ({pc_text(ch['long_form.views'])}) |",
              f"| Organic views | {n(cs['organic_views'])} ({pc_text(ch['shorts.organic_views'])}) | {n(cl['organic_views'])} ({pc_text(ch['long_form.organic_views'])}) |",
              f"| Paid share of views | {cs['paid_share_pct']}% | {cl['paid_share_pct']}% |", ""] + R("shorts_vs_long")
    if lu:
        c, p, ch = lu["current"], lu["previous"], lu["change"]
        by_city = geo_counts(c["event_list"])[0]
        L += ["## Luma", f"- Events: {c['events']} (prev {p['events']}, {pc_text(ch['events'])})",
              f"- Registered: {n(c['registered'])} (prev {n(p['registered'])}, {pc_text(ch['registered'])})",
              f"- Attended: {n(c['attended'])} (prev {n(p['attended'])}, {pc_text(ch['attended'])})",
              f"- New Luma subscribers: {n(lu['contacts']['current']['new'])} (prev {n(lu['contacts']['previous']['new'])}, {pc_text(lu['contacts_change_new'])})",
              "- Events by city: " + ", ".join(f"{k} ({v})" for k, v in by_city.items()), ""] + R("luma")
    if sh:
        c, p, ch = sh["current"], sh["previous"], sh["change"]
        L += ["## Meetup ratings and cost", f"- Average rating: {c['avg_rating']} (prev {p['avg_rating']}); {c['events_rated']} events rated",
              f"- Spend: {usd(c['total_cost'])} (prev {usd(p['total_cost'])}, {pc_text(ch['total_cost'])}) across {c['events_with_cost']} events with a cost",
              f"- Cost per attendee: {usd(c['cost_per_attendee'], 2)} (prev {usd(p['cost_per_attendee'], 2)}, {pc_text(ch['cost_per_attendee'])})",
              f"- Zero-cost events: {c['zero_cost_events']}; events without data: {c['events_without_data']}", ""] + R("sheet")
    mc_ = d.get("mailchimp")
    if mc_:
        c_, p_ = mc_["current"], mc_["previous"]
        L += ["## Newsletters (Mailchimp)", f"- Newsletters sent: {c_['newsletters']}; emails sent {n(c_['recipients'])} (newsletters moved to Mailchimp in October, so there is no comparable previous period)",
              f"- Unique clickers {n(c_['unique_clickers'])} ({n(c_['click_rate_pct'], 1)}%), unique opens {n(c_['unique_opens'])} ({n(c_['open_rate_pct'], 1)}%, inflated by Apple Mail Privacy Protection), unsubscribes {n(c_['unsubscribed'])}, bounces {n(c_['bounces'])}"]
        L += [f"  - {r['date']}: {r['subject'][:70]} ({n(r['sent'])} sent, {r['open_rate_pct']}% opens, {r['click_rate_pct']}% clicks)" for r in c_["campaigns"]]
        L += [""] + R("newsletters")
    li_ = d.get("linkedin")
    if li_:
        c_ = li_["current"]
        L += ["## LinkedIn: reshared blog posts, newsletter and webinars",
              f"Organic posts are listed from {li_['organic_history_from']}; the previous period has no per-post data (n/a, not zero)."]
        for k, lab in (("blog_reshare", "Reshared blog posts"), ("newsletter", "Newsletter edition"), ("webinar", "Webinars and live sessions")):
            t_ = (c_["types"].get(k) or {})
            L.append(f"- {lab}: {t_.get('posts', 0)} posts, {n(t_.get('impressions', 0))} impressions, {n(t_.get('clicks', 0))} clicks, {n(t_.get('reactions', 0))} reactions, {n(t_.get('comments', 0))} comments")
        L += [f"- LinkedIn Live webinars held: {c_['events']['linkedin_live']} (prev {li_['previous']['events']['linkedin_live']})", ""] + R("linkedin")
    if cr:
        m = cr["metrics"]
        L += ["## Common Room", f"- Accounts influenced: {n(m.get('accounts_influenced'))} ({n(m.get('company_coverage_pct'), 1)}% of attendees have a known company)",
              f"- Developers influenced: {n(m['developers_influenced'])}", f"- Tier 1 accounts: {n(m.get('tier1_accounts'))} ({n(m.get('tier1_share_of_accounts_pct'), 1)}% of accounts)",
              f"- Economic buyers among attendees: {m['economic_buyer_pct']}%", "- Sentiment: not available", f"- Note: {cr['note']}", ""] + R("commonroom")
    if tp:
        L.append("## Topics and content style")
        for kind, title in (("blog", "Blog posts by topic"), ("video", "Videos by topic")):
            L += [f"### {title}", "| Topic | Pieces | Median | Pieces (prev) | Median (prev) |", "|---|---|---|---|---|"]
            prev = {g["label"]: g for g in tp["previous"][kind]["by_topic"]}
            for g in tp["current"][kind]["by_topic"]:
                pg = prev.get(g["label"])
                L.append(f"| {g['label']} | {g['pieces']} | {n(g['median_metric']) if g['ranked'] else 'too few'} | {pg['pieces'] if pg else 0} | {n(pg['median_metric']) if pg and pg['ranked'] else 'n/a'} |")
            L.append("")
        L += R("topics")
    if ctx:
        L += ["## Releases, industry news and campaigns"] + [f"{i}. {e['date']} ({KIND_LABEL.get(e['kind'], e['kind'])}): {e['label']}" for i, e in ctx] + [""] + R("context")
    cm = d.get("community")
    if cm:
        c, p, ch = cm["current"], cm["previous"], cm["change"]
        L += ["## Owned community", "| Metric | This period | Previous | Change |", "|---|---:|---:|---:|"]
        for label, k in (("Joins", "joins"), ("Net new members", "net_members"), ("Active members per month (avg)", "active_members_avg"), ("Active rate %", "active_rate_pct"),
                         ("Help topics", "help_topics"), ("Answer rate %", "answer_rate_pct"), ("Staff and bot replies", "staff_bot_replies"),
                         ("Retention %", "retention_pct"), ("Event attendee roles granted", "event_roles_granted")):
            L.append(f"| {label} | {n(c[k], 2 if k.endswith('pct') else 0)} | {n(p[k], 2 if k.endswith('pct') else 0)} | {pc_text(ch[k])} |")
        L.append("")
    else:
        L += ["## Owned community", "Not connected.", ""]
    L += R("community")
    if insights:
        L += ["## Trend analysis and insights", insights, ""] + R("insights")
    L += ["---", cost_line(cost)]
    return "\n".join(L) + "\n"


CSS = f"""
:root{{--bg:#FFFFFF;--card:#FFFFFF;--tile:#F7F8FA;--border:#DADDE2;--orange:{ORANGE};--text:{TEXT};--dim:{DIM};--green:{GREEN}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:'Space Grotesk',system-ui,-apple-system,sans-serif;line-height:1.5}}
main{{max-width:1040px;margin:0 auto;padding:32px 16px 64px}}
header h1{{font-size:34px;margin:0 0 4px}}header p{{color:var(--dim);margin:0 0 24px;font-family:'JetBrains Mono',monospace;font-size:14px}}
header .kicker{{color:var(--orange);font-family:'JetBrains Mono',monospace;font-size:13px;letter-spacing:.08em;text-transform:uppercase;font-weight:600}}
section{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:22px;margin:0 0 20px}}
h2{{margin:0 0 14px;font-size:22px}}h3{{margin:20px 0 8px;font-size:15px;color:var(--dim);font-weight:600}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin-bottom:16px}}
.tile{{border:1px solid var(--border);border-radius:10px;padding:12px 14px;background:var(--tile)}}
.tl{{color:var(--dim);font-size:13px}}.tv{{font-size:28px;font-weight:700;font-family:'JetBrains Mono',monospace;margin:2px 0}}
.tv.dim{{font-size:17px;color:var(--dim)}}.prev,.note{{color:var(--dim);font-size:12px}}
.delta{{font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:600}}.delta.up{{color:#1F7A4F}}.delta.down{{color:#C2410C}}.delta.na,.delta.flat{{color:var(--dim)}}
.chart{{margin:12px 0 4px}}.chart figcaption{{color:var(--dim);font-size:13px;margin-bottom:4px;font-weight:600}}svg{{width:100%;height:auto;display:block}}
.legend{{display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:var(--dim);margin-top:2px}}.legend.top{{margin-bottom:10px}}
.lg i{{display:inline-block;width:14px;height:3px;margin-right:6px;vertical-align:middle;border-radius:2px}}
table{{width:100%;border-collapse:collapse;font-size:14px}}th,td{{padding:7px 8px;border-bottom:1px solid var(--border);text-align:left;vertical-align:top}}
th{{color:var(--dim);font-weight:600;font-size:12px}}.r{{text-align:right;font-family:'JetBrains Mono',monospace;white-space:nowrap}}a{{color:#C2410C}}
.two{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}}
.foot,.warn{{color:var(--dim);font-size:12.5px;margin:10px 0 0}}.warn{{color:#C2410C;font-size:14px}}
.sb{{margin:0 0 12px}}.sbl{{font-size:13px;color:var(--dim)}}.sbl b{{color:var(--text)}}
.bar{{display:flex;height:14px;border-radius:7px;overflow:hidden;background:var(--border);margin:3px 0}}
.bar .paid{{background:var(--orange)}}.bar .org{{background:var(--green)}}.sbn{{font-size:12px;color:var(--dim);font-family:'JetBrains Mono',monospace}}
.hb{{display:grid;grid-template-columns:230px 1fr 110px;gap:10px;align-items:center;margin:5px 0;font-size:13px}}
.hbt{{background:#EEF0F3;border-radius:4px;height:12px;overflow:hidden}}.hbt span{{display:block;height:100%}}.hbv{{font-family:'JetBrains Mono',monospace;font-size:12px;text-align:right}}
.insights p,.insights li{{font-size:15px}}.insights strong{{color:#C2410C}}
.stoplight{{border:2px solid #8B9099;padding:0;overflow:hidden}}.stoplight h2{{padding:16px 22px 0}}
table.sl{{font-size:15px}}table.sl th{{font-size:17px;color:var(--text);padding:12px 14px;border-bottom:1px solid #8B9099;border-top:1px solid #8B9099}}
table.sl td{{padding:12px 14px;border-bottom:1px solid #C9CDD3}}table.sl td.kpi{{width:19%;font-size:17px}}
table.sl td.status{{width:17%;text-align:center;color:#1A1D21;font-weight:700;text-transform:capitalize;font-size:13px;vertical-align:middle}}
table.sl td.notes{{width:64%}}.stoplight .foot{{padding:0 22px 16px}}
.chips{{display:flex;flex-wrap:wrap;gap:8px;margin:4px 0 6px}}.chip{{border:1px solid var(--border);border-radius:999px;padding:5px 12px;font-size:13px;background:var(--tile)}}
.chip b{{font-family:'JetBrains Mono',monospace;margin-right:4px}}.chip.new{{background:#FFF1EB;border-color:#FFC9B2;color:#9A3412}}.chip.est{{background:#EEF1F4}}.chip.nodata{{background:repeating-linear-gradient(45deg,#fff,#fff 5px,#F1F3F5 5px,#F1F3F5 10px)}}
h3.grp{{margin:22px 0 8px}}.chan-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:14px}}
.chan{{border:1px solid var(--border);border-radius:12px;padding:14px 16px;background:#fff;box-shadow:0 1px 2px rgba(20,23,26,.04)}}
.chan-h{{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;margin-bottom:10px}}.chan-n{{font-weight:700;font-size:16px}}
.badge{{font-size:11px;font-weight:700;padding:3px 9px;border-radius:999px;white-space:nowrap}}.badge.new{{background:#FFF1EB;color:#9A3412;border:1px solid #FFC9B2}}.badge.est{{background:#EEF1F4;color:#3B4450}}
.badge.nodata{{background:repeating-linear-gradient(45deg,#fff,#fff 4px,#EEF1F4 4px,#EEF1F4 8px);color:#3B4450;border:1px solid var(--border)}}.badge.inactive{{background:#F3F4F6;color:#6B7280}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}.cs{{min-width:0}}.csl{{font-size:11.5px;color:var(--dim);min-height:30px;line-height:1.25}}
.csv{{font-family:'JetBrains Mono',monospace;font-weight:700;font-size:21px}}.csd{{font-size:11.5px;display:flex;flex-direction:column;gap:1px}}.csp{{color:var(--dim)}}
.mini{{height:5px;background:#EEF0F3;border-radius:3px;margin-top:4px;overflow:hidden}}.m-cur{{display:block;height:100%;background:var(--orange)}}.m-prev{{display:block;height:100%;background:#B9BFC8}}
.chan-note{{margin-top:10px;font-size:12px;color:var(--dim);border-top:1px solid #EEF0F3;padding-top:8px}}
details.alltable{{margin-top:18px}}details.alltable summary{{cursor:pointer;color:var(--dim);font-size:13px;font-weight:600}}details.alltable table{{margin-top:8px}}

.tldr{{border:2px solid var(--border);border-left:6px solid var(--orange,#FF6C37);background:#fff;padding:16px 22px;margin:0 0 20px}}.tldr h2{{font-size:18px;margin:0 0 8px}}.tldr ol,.tldr ul{{margin:0;padding-left:22px}}.tldr li{{margin:8px 0;font-size:15px;line-height:1.45}}
.toc{{border:1px solid var(--border);border-radius:12px;padding:18px 22px;margin:0 0 20px;background:#fff}}.toc h2{{font-size:18px;margin:0 0 8px}}
.toc ol{{margin:0;padding-left:22px}}.toc li{{margin:6px 0;font-size:14px}}.toc li span{{display:block;color:var(--dim);font-size:13px}}
.ins{{margin-top:18px;padding:14px 18px;border:1px solid var(--border);border-radius:10px;background:#FAFAFB}}.ins h3{{margin:0 0 6px;color:var(--text);font-size:15px}}
.ins p,.ins li{{font-size:14.5px}}.ins ul{{margin:6px 0 0;padding-left:20px}}.ins li{{margin:6px 0}}.ins strong{{color:#C2410C}}
.draft{{background:#FFF6E5;border:1px solid #F2C879;border-radius:8px;padding:10px 14px;font-size:14px;color:#7A4B00;margin:0 0 14px}}
.dir h3{{margin:22px 0 6px;color:var(--text);font-size:16px}}.dir p,.dir li{{font-size:14.5px}}.dir ul{{padding-left:20px}}.dir li{{margin:6px 0}}
table.mdt td,table.mdt th{{font-size:13.5px}}
@page{{size:Letter;margin:.55in .5in .65in .5in;@bottom-center{{content:counter(page) " / " counter(pages);font-family:'Space Grotesk',Arial,sans-serif;font-size:10px;color:#6A7179}}}}
@media print{{body{{background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}}main{{max-width:none;padding:0}}
section{{break-inside:auto;border-radius:6px;margin:0 0 12px;padding:14px}}section[data-chapter]{{break-before:page}}
h2,h3{{break-after:avoid}}.tile,.chan,.rec,.ins,.cs,figure.chart,.sb,.hb,.toc,tr{{break-inside:avoid}}
header{{margin-bottom:8px}}.kicker{{font-size:11px}}.tiles{{grid-template-columns:repeat(3,1fr);gap:8px}}.chan-grid{{grid-template-columns:1fr 1fr}}.two{{grid-template-columns:1fr 1fr;gap:12px}}
.tv{{font-size:22px}}.csv{{font-size:17px}}details.alltable summary{{display:none}}.chart svg{{height:auto}}table{{font-size:12.5px}}th,td{{padding:5px 6px}}.rec{{break-before:avoid}}.chip{{font-size:12px}}}}
.src{{color:var(--dim);font-size:12px}}
.mk{{display:inline-block;min-width:20px;height:20px;border-radius:10px;color:#fff;font-size:11px;font-weight:700;text-align:center;line-height:20px;padding:0 5px}}
.rec{{margin-top:18px;padding:12px 14px;border-left:4px solid var(--orange);background:#FFF6F1;border-radius:0 8px 8px 0;font-size:14.5px}}.rec strong{{color:#C2410C}}
@media (max-width:620px){{.tv{{font-size:23px}}header h1{{font-size:26px}}.hb{{grid-template-columns:1fr}}table.sl td.status span{{display:none}}}}

"""


def main():
    global FULL_WEEKS, MARKERS, PERIOD_START, BUCKET
    start, end, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    errors = load(out_dir, "errors.json") or {}
    d = {k: load(out_dir, f"raw-{k}.json") for k in SOURCES}
    insights = ""
    try:
        with open(os.path.join(out_dir, "insights.md")) as f:
            insights = f.read().strip()
    except OSError:
        pass
    cost, tp, ctx_raw, overrides, ci = (load(out_dir, x) for x in ("cost.json", "topics.json", "context.json", "stoplight.json", "channels-input.json"))
    pj = load(out_dir, "period.json")
    cur, prev = q.periods(start, end)
    if pj:  # the windows the data was pulled for, even if the period rules have changed since
        cur, prev = (q.d(pj["start"]), q.d(pj["end"])), (q.d(pj["previous_start"]), q.d(pj["previous_end"]))
    label = (pj or {}).get("label") or q.period_label(start, end)
    PERIOD_START = cur[0]
    BUCKET = q.bucket_days(*cur)
    FULL_WEEKS = ((cur[1] - cur[0]).days + 1) // BUCKET
    events = sorted((ctx_raw or {}).get("events", []), key=lambda e: (e["date"], e["kind"]))
    MARKERS = [(i, e) for i, e in enumerate(events, 1)]
    rows_sl = stoplight_rows(d, tp)

    recs = load(out_dir, "recommendations.json") or {}
    ins = split_insights(insights)
    R = lambda html_, key: with_rec(html_, recs, key, ins)  # noqa: E731
    try:
        with open(os.path.join(out_dir, "direction.md")) as f:
            direction_md = f.read()
    except OSError:
        direction_md = ""
    tldr = load_text(out_dir, "tldr.md")
    sec = {"stoplight": R(stoplight_section(d, overrides, tp), "stoplight"), "reach": R(reach_section(reach_stats(d, tp)), "reach"),
           "channels": R(channels_section(d, ci), "channels"),
           "blog": R(blog_section(d["wp"]), "blog") if d["wp"] else not_connected("wp", errors),
           "luma": R(luma_section(d["luma"], d["sheet"]), "luma") if d["luma"] else not_connected("luma", errors),
           "commonroom": R(commonroom_section(d["commonroom"]), "commonroom") if d["commonroom"] else not_connected("commonroom", errors),
           "community": R(community_section(d["community"]), "community") if d["community"] else not_connected("community", errors), "direction": direction_section(direction_md)}
    if d.get("linkedin"):
        sec["linkedin"] = R(linkedin_section(d["linkedin"]), "linkedin")
    if d.get("mailchimp"):
        sec["newsletters"] = R(mailchimp_section(d["mailchimp"]), "newsletters")
    if d["youtube"]:
        sec["youtube"] = R(youtube_section(d["youtube"]), "youtube")
        sec["shorts_vs_long"] = R(compare_section(d["youtube"], tp), "shorts_vs_long")
        if tp and tp["current"].get("top_videos"):
            sec["paid_topics"] = R(paid_topics_section(tp), "paid_topics")
    else:
        sec["youtube"] = not_connected("youtube", errors)
    if d["sheet"]:
        sec["sheet"] = R(sheet_section(d["sheet"]), "sheet")
    if tp:
        sec["topics"] = R(topics_section(tp), "topics")
    if MARKERS:
        sec["context"] = R(context_section(MARKERS), "context")
    known = {k for _, k in INSIGHT_KEYS}
    if insights and not (set(ins) & known):  # an older insights.md with no recognised headings: show it whole
        limits_html = f'<section class="insights"><h2>Trend analysis and insights</h2>{md_to_html(insights)}</section>'
    else:
        extra = f'<h3>More insights</h3>{md_to_html(ins["other"])}' if ins.get("other") else ""
        limits_html = (f'<section><h2>What this report cannot see, and what to test next</h2><div class="ins"><h3>Not covered in this run</h3>'
                       f'{md_to_html(ins.get("limits", ""))}</div>{extra}</section>')
    sec["limits"] = R(limits_html, "insights")
    chapters = [("Summary", ["stoplight", "reach"]), ("Content", ["blog", "youtube", "shorts_vs_long", "paid_topics", "topics"]),
                ("Events and meetups", ["luma", "sheet"]), ("Channels", ["channels", "linkedin", "newsletters"]),
                ("Accounts and community", ["commonroom", "community"]), ("Context", ["context"]),
                ("Where we are going", ["direction"]), ("Limits and next tests", ["limits"])]
    body, toc = [], []
    for ci_, (cname, keys) in enumerate(chapters):
        present = [k for k in keys if sec.get(k)]
        if not present:
            continue
        titles = [re.sub(r"<[^>]+>", "", t) for k in present for t in re.findall(r"<h2>(.*?)</h2>", sec[k])]
        toc.append((cname, titles))
        for j, k in enumerate(present):
            html_ = sec[k]
            if j == 0:  # the first section of each chapter starts a new page when printed
                html_ = html_.replace("<section", f'<section data-chapter="{esc(cname)}"', 1)
            body.append(html_)
    toc_html = ('<nav class="toc"><h2>Contents</h2><ol>' + "".join(
        f'<li><strong>{esc(c)}</strong><span>{esc(" · ".join(t))}</span></li>' for c, t in toc) + "</ol></nav>")

    tldr_html = (f'<section class="tldr"><h2>TL;DR</h2>{md_to_html(tldr)}</section>' if tldr else "")

    def make_page(print_mode):
        inner = "".join(body)
        if print_mode:
            inner = inner.replace('<details class="alltable">', '<details class="alltable" open>')
        return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>QBR Metrics {start} to {end}</title><link rel="preconnect" href="https://fonts.googleapis.com">'
                f'<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">'
                f'<style>{CSS}</style></head><body><main><header><div class="kicker">Postman DevRel</div><h1>QBR metrics</h1>'
                f'<p>{esc(label)} · {cur[0]} to {cur[1]} · compared with {prev[0]} to {prev[1]}</p></header>{tldr_html}{toc_html}{inner}'
                f'<p class="foot">Charts show complete {"days" if BUCKET == 1 else "7-day weeks"} starting {cur[0]}; any trailing partial bucket is left out of the charts but included in every total.</p>'
                f'<p class="foot">{esc(cost_line(cost))}</p></main></body></html>')
    with open(os.path.join(out_dir, "report.html"), "w") as f:
        f.write(make_page(False))
    with open(os.path.join(out_dir, "report-print.html"), "w") as f:  # the same page with the detail tables open, used for the PDF
        f.write(make_page(True))
    with open(os.path.join(out_dir, "report.md"), "w") as f:
        f.write(build_md(d, start, end, insights, tp, MARKERS, rows_sl, cost, recs, ci, tldr))
    with open(os.path.join(out_dir, "metrics.json"), "w") as f:
        json.dump({"range": {"start": start, "end": end, "previous_start": str(prev[0]), "previous_end": str(prev[1])},
                   "sources": {k: ("ok" if d[k] else errors.get(k, "not pulled")) for k in SOURCES},
                   "stoplight": [{"kpi": n_, "signals": s, "note": t} for n_, s, t in rows_sl], "claude_cost": cost, "data": d}, f, indent=2)
    print(os.path.join(out_dir, "report.html"))


if __name__ == "__main__":
    main()
