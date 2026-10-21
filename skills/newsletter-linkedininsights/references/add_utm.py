"""
UTM tagging for the Postman Developer Digest (LinkedIn newsletter).

Usage:
    python3 add_utm.py "<url>" "<YYYY-MM>" "<section-slug>"

Example:
    python3 add_utm.py "https://blog.postman.com/introducing-postman-ai/" "2026-10" "product-updates"

Section slugs: product-updates | events | liftoff | youtube | hero | webinar

"hero" is for the hero block's own link only, and "webinar" is for the
sub-hero webinar callout's own link only (see the Hero highlight and Output
format sections of SKILL.md) — a hero item or webinar that also has a normal
section listing gets two tagged links: "hero"/"webinar" on the above-the-fold
callout, its usual section slug on the section listing.
"""

import sys
from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse

VALID_SECTIONS = {"product-updates", "events", "liftoff", "youtube", "hero", "webinar"}


def add_utm(url: str, campaign_month: str, section_slug: str) -> str:
    if section_slug not in VALID_SECTIONS:
        raise ValueError(f"section_slug must be one of {VALID_SECTIONS}, got {section_slug!r}")

    parts = urlparse(url)
    query = dict(parse_qsl(parts.query))
    query.update({
        "utm_source": "linkedin",
        "utm_medium": "social",
        "utm_campaign": f"dev-digest-{campaign_month}",
        "utm_content": section_slug,
    })
    new_parts = parts._replace(query=urlencode(query))
    return urlunparse(new_parts)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    url, month, section = sys.argv[1], sys.argv[2], sys.argv[3]
    print(add_utm(url, month, section))
