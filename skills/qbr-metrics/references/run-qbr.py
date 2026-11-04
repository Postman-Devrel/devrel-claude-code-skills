#!/usr/bin/env python3
"""Run every qbr-metrics pull in parallel, then build the report.

Usage: run-qbr.py (START END | FY27-Q3 | 2026-09 | 2026-W41) [--only=wp,youtube,luma,sheet,linkedin,mailchimp,commonroom] [--rebuild] [--direction=PATH] [--no-drive]
  --find-previous-direction  print the path of the latest earlier period's direction.md that has text, and stop
  --no-drive  do not copy report.pdf to the shared Google Drive folder (also: DRIVE_QBR_FOLDER_ID=off)
  --direction=PATH  install a direction.md the team already wrote (an existing one with text is kept as direction.previous.md)
  --rebuild  skip the pulls and rebuild the report from existing raw-*.json files

Output goes to qbr-output/{START}_to_{END}/ under the current directory: report.html, report.pdf (needs Chrome), report.md and the data files.
A source that fails is recorded in errors.json and shown as "not connected";
the rest of the report still builds. Progress goes to stderr.
"""
import json
import os
import subprocess
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = {"wp": "pull-wp.py", "youtube": "pull-youtube.py", "luma": "pull-luma.py", "sheet": "pull-sheet.py", "linkedin": "pull-linkedin.py", "mailchimp": "pull-mailchimp.py", "commonroom": "pull-commonroom.py", "community": "pull-community.py", "liftoff": "pull-liftoff.py"}


def pull(key, start, end, out_dir, errors):
    proc = subprocess.run([sys.executable, os.path.join(HERE, SCRIPTS[key]), start, end],
                          capture_output=True, text=True)
    sys.stderr.write(proc.stderr)
    if proc.returncode != 0 or not proc.stdout.strip():
        errors[key] = (proc.stderr.strip().splitlines() or ["pull failed"])[-1][:300]
        print(f"[{key}] FAILED: {errors[key]}", file=sys.stderr)
        return
    with open(os.path.join(out_dir, f"raw-{key}.json"), "w") as f:
        f.write(proc.stdout)
    print(f"[{key}] done", file=sys.stderr)


DIRECTION_TEMPLATE = '# Where we are going\n\n<!--\nWrite this file in your own words. Whatever you put under a heading appears in the report\'s "Where we are going"\nchapter exactly as written. Headings you leave empty are skipped, and the whole chapter is skipped until there is\nsome text. Comments like this one are never shown. Markdown works: **bold**, - bullets, and | tables |.\nAdd a line "Status: DRAFT" to show a draft banner.\n\nBaselines from the latest run, for reference only (copy what you want to use):\n- Median views per blog post, and median organic views per video: see the Reach per piece section\n- Luma events held, registered and attended: see the Events chapter\n- Webinars, newsletters and LinkedIn reshares: see the Channels chapter\n- Accounts reached and industry mix: see the Accounts chapter\n\nExample table:\n| Program | What | Owner | Success measure |\n|---|---|---|---|\n| Monthly webinars | One a month | name | Registrants and viewers |\n-->\n\n## Trends we are responding to\n\n## Programs and bets\n\n## Targets for next quarter\n\n## Asks and decisions needed\n\n## Risks and dependencies\n'


def ensure_direction_template(out_dir):
    """Create an empty direction.md for the team to fill in. An existing file is never touched."""
    path = os.path.join(out_dir, "direction.md")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(DIRECTION_TEMPLATE)
        print(f"[direction] created an empty template at {path}; the report adds a chapter once it has text", file=sys.stderr)


def direction_has_text(text):
    """True if direction.md holds anything beyond comments, the title and empty headings."""
    import re
    body = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return any(l.strip() and not l.startswith("#") and not l.lower().startswith("status:") for l in body.splitlines())


def install_direction(out_dir, src):
    """Copy a direction.md the team already wrote into the output folder. A different existing file with text is
    kept as direction.previous.md first, so nothing the team wrote is lost."""
    import shutil
    src = os.path.abspath(os.path.expanduser(src))
    dst = os.path.abspath(os.path.join(out_dir, "direction.md"))
    if not os.path.isfile(src):
        sys.exit(f"--direction: no file at {src}")
    if src == dst:
        return
    new = open(src).read()
    if os.path.exists(dst):
        old = open(dst).read()
        if old == new:
            return
        if direction_has_text(old):
            shutil.copy2(dst, os.path.join(out_dir, "direction.previous.md"))
            print("[direction] the existing direction.md had text; kept as direction.previous.md", file=sys.stderr)
    shutil.copy2(src, dst)
    print(f"[direction] installed {src}", file=sys.stderr)


def previous_direction(start, base="qbr-output"):
    """Path of the most recent earlier period's direction.md that has text, or None.
    Looks at folders named START_to_END whose END is before `start` (a date)."""
    import re
    best = None
    if not os.path.isdir(base):
        return None
    for name in os.listdir(base):
        m = re.fullmatch(r"(\d{4}-\d{2}-\d{2})_to_(\d{4}-\d{2}-\d{2})", name)
        path = os.path.join(base, name, "direction.md")
        if m and m.group(2) < str(start) and os.path.isfile(path) and direction_has_text(open(path).read()):
            if best is None or m.group(2) > best[0]:
                best = (m.group(2), path)
    return os.path.abspath(best[1]) if best else None


def upload_drive(out_dir, start, end):
    """Copy report.pdf to the shared Drive folder as devrel-qbr-{start}_to_{end}.pdf. Never fails the run."""
    if "--no-drive" in sys.argv or os.environ.get("DRIVE_QBR_FOLDER_ID", "").lower() == "off":
        return
    if not os.path.exists(os.path.join(out_dir, "report.pdf")):
        print("[drive] skipped: there is no report.pdf to copy", file=sys.stderr)
        return
    r = subprocess.run([sys.executable, os.path.join(HERE, "upload-drive.py"), out_dir, start, end], capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        info = json.loads(r.stdout.strip().splitlines()[-1])
        print(f"[drive] {'updated' if info.get('updated_existing') else 'copied'} {info['name']} via {info.get('method', 'the Drive API')}: {info.get('link')}", file=sys.stderr)
    else:
        print("[drive] not copied: " + (r.stderr.strip().splitlines() or ["unknown error"])[-1][:400], file=sys.stderr)


def find_chrome():
    for c in (os.environ.get("CHROME_PATH"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium", "google-chrome", "chromium", "chromium-browser"):
        if c and (os.path.exists(c) or subprocess.run(["which", c], capture_output=True).returncode == 0):
            return c
    return None


def export_pdf(out_dir):
    """Print report-print.html to report.pdf with headless Chrome. Skipped, with a note, if no Chrome is found."""
    src = os.path.abspath(os.path.join(out_dir, "report-print.html"))
    out = os.path.abspath(os.path.join(out_dir, "report.pdf"))
    chrome = find_chrome()
    if not chrome or not os.path.exists(src):
        print("[pdf] skipped: Chrome not found (set CHROME_PATH to enable the PDF export)", file=sys.stderr)
        return
    r = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=6000",
                        f"--print-to-pdf={out}", "file://" + src], capture_output=True, text=True, timeout=180)
    print(f"[pdf] {out}" if os.path.exists(out) else f"[pdf] failed: {r.stderr[-200:]}", file=sys.stderr)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    sys.path.insert(0, HERE)
    import qbrlib
    start_d, end_d = qbrlib.resolve_period(args)
    start, end = str(start_d), str(end_d)
    if "--find-previous-direction" in sys.argv:  # prints the path, or nothing, and stops
        p = previous_direction(start)
        print(p or "")
        return
    only = None
    for a in sys.argv[1:]:
        if a.startswith("--only"):
            only = a.split("=", 1)[1].split(",") if "=" in a else None
    out_dir = os.path.join("qbr-output", f"{start}_to_{end}")
    os.makedirs(out_dir, exist_ok=True)
    if "--rebuild" not in sys.argv:
        if end_d > __import__("datetime").date.today():
            sys.exit(f"The end date {end} is in the future. Pick a period that has finished.")
        cur, prev = qbrlib.periods(start_d, end_d)
        with open(os.path.join(out_dir, "period.json"), "w") as f:
            json.dump({"start": start, "end": end, "previous_start": str(prev[0]), "previous_end": str(prev[1]),
                       "kind": qbrlib.period_kind(start_d, end_d), "label": qbrlib.period_label(start_d, end_d),
                       "run_since": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}, f, indent=2)
    errors = {}
    if "--rebuild" not in sys.argv:
        threads = [threading.Thread(target=pull, args=(k, start, end, out_dir, errors))
                   for k in SCRIPTS if only is None or k in only]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        with open(os.path.join(out_dir, "errors.json"), "w") as f:
            json.dump(errors, f, indent=2)
    for a in sys.argv[1:]:
        if a.startswith("--direction="):
            install_direction(out_dir, a.split("=", 1)[1])
    ensure_direction_template(out_dir)
    # Tag pieces by topic and style (needs the blog and YouTube pulls).
    if all(os.path.exists(os.path.join(out_dir, f"raw-{k}.json")) for k in ("wp", "youtube")):
        subprocess.run([sys.executable, os.path.join(HERE, "classify-topics.py"), out_dir], capture_output=True, text=True)
    # Refresh the token and cost estimate for the Claude session that produced the report.
    # Set QBR_RUN_SINCE (ISO timestamp) to count only the work since a run began.
    cost_cmd = [sys.executable, os.path.join(HERE, "session-cost.py"), out_dir]
    run_since = os.environ.get("QBR_RUN_SINCE")
    if not run_since:  # default to when this period's pulls started, so the footer is the cost of the run
        try:
            with open(os.path.join(out_dir, "period.json")) as f:
                run_since = json.load(f).get("run_since")
        except (OSError, ValueError):
            run_since = None
    if run_since:
        cost_cmd += ["--since", run_since]
    subprocess.run(cost_cmd, capture_output=True, text=True)
    result = subprocess.run([sys.executable, os.path.join(HERE, "build-report.py"), start, end, out_dir],
                            capture_output=True, text=True)
    sys.stderr.write(result.stderr)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit("report build failed")
    print(result.stdout.strip())
    export_pdf(out_dir)
    upload_drive(out_dir, start, end)


if __name__ == "__main__":
    main()
