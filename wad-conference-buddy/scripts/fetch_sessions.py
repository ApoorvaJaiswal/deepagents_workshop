"""Refresh data/sessions.json from the live WeAreDevelopers feed.

The conference site publishes a markdown version of the agenda, which is what
their own "discuss the program with your agent" buttons point at:

    https://www.wearedevelopers.com/events/world-congress-2026-north-america/sessions.md?all=true

VERIFY THE SHAPE BEFORE THE WORKSHOP. This parser is written against a markdown
feed whose exact layout may change. Run it once, eyeball the output, and adjust
`parse()` if the headings differ. If anything looks off, fall back to
`python scripts/build_dataset.py`, which needs no network at all.

Do not make the live fetch a hard dependency of the workshop. Conference wifi
with 10,000 developers on it is not a thing you want in your critical path.
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEED = "https://www.wearedevelopers.com/events/world-congress-2026-north-america/sessions.md?all=true"


def fetch(url: str = FEED) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "wad-workshop/0.1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


def parse(markdown: str) -> list[dict]:
    """Best-effort parse. Expect to adjust this once you see the real feed."""
    sessions = []
    blocks = re.split(r"\n(?=#{1,3}\s)", markdown)
    for block in blocks:
        title_match = re.match(r"#{1,3}\s+(.+)", block)
        if not title_match:
            continue
        title = title_match.group(1).strip()

        date = re.search(r"(20\d{2}-\d{2}-\d{2})", block)
        times = re.findall(r"\b(\d{1,2}:\d{2}\s*(?:AM|PM)?)\b", block, re.IGNORECASE)
        url = re.search(r"https?://\S+", block)

        sessions.append(
            {
                "title": title,
                "day": date.group(1) if date else "",
                "start": times[0] if times else "",
                "end": times[1] if len(times) > 1 else "",
                "url": url.group(0).rstrip(")") if url else "",
                "raw": block.strip()[:2000],
                "source": "live",
            }
        )
    return sessions


if __name__ == "__main__":
    try:
        raw = fetch()
    except Exception as exc:
        sys.exit(
            f"Could not fetch the feed: {exc}\n"
            f"Fall back to: python scripts/build_dataset.py"
        )

    parsed = parse(raw)
    out = ROOT / "data" / "sessions.live.json"
    out.write_text(json.dumps(parsed, indent=2) + "\n")
    print(f"Fetched {len(parsed)} blocks -> {out}")
    print("Inspect it, then reshape into data/sessions.json to match build_dataset.py output.")
