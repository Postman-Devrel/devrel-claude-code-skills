#!/usr/bin/env python3
"""Print a hackathon share page (HTML) to PDF with headless Chrome.

Usage: render-pdf.py <input.html> <output.pdf>

Finds Chrome the same way the qbr-metrics skill does (set CHROME_PATH to override).
Letter size and margins come from the @page rule in the HTML. Exits 1 if Chrome is missing or the PDF was not written.
"""
import os
import subprocess
import sys


def find_chrome():
    for c in (os.environ.get("CHROME_PATH"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              "/Applications/Chromium.app/Contents/MacOS/Chromium", "google-chrome", "chromium", "chromium-browser"):
        if c and (os.path.exists(c) or subprocess.run(["which", c], capture_output=True).returncode == 0):
            return c
    return None


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    chrome = find_chrome()
    if not chrome:
        sys.exit("Chrome not found. Install Google Chrome or set CHROME_PATH.")
    r = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=6000",
                        f"--print-to-pdf={out}", "file://" + src], capture_output=True, text=True, timeout=180)
    if not os.path.exists(out):
        sys.exit("PDF failed: " + r.stderr[-300:])
    print(out)


if __name__ == "__main__":
    main()
