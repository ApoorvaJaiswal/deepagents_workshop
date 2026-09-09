"""Plain-Python access to the conference dataset. No LLM involved."""

import json
from datetime import datetime
from functools import lru_cache

from buddy.config import DATA_FILE


@lru_cache(maxsize=1)
def _load() -> dict:
    return json.loads(DATA_FILE.read_text())


def event() -> dict:
    return _load()["event"]


def sessions() -> list[dict]:
    return _load()["sessions"]


def stages() -> list[str]:
    return _load()["stages"]


def tracks() -> list[str]:
    return sorted({s["track"] for s in sessions()})


def by_id(session_id: str) -> dict | None:
    return next((s for s in sessions() if s["id"] == session_id), None)


def walk_minutes(a: str, b: str) -> int | None:
    if a == b:
        return 0
    table = _load()["walk_minutes"]
    return table.get(f"{a}|{b}") or table.get(f"{b}|{a}")


def to_minutes(hhmm: str) -> int:
    t = datetime.strptime(hhmm, "%H:%M")
    return t.hour * 60 + t.minute


def overlaps(a: dict, b: dict) -> bool:
    if a["day"] != b["day"]:
        return False
    return to_minutes(a["start"]) < to_minutes(b["end"]) and to_minutes(b["start"]) < to_minutes(
        a["end"]
    )


def speaker_names(session: dict) -> str:
    return ", ".join(s["name"] for s in session["speakers"])


def one_line(session: dict) -> str:
    """Compact representation. Tool results should be scannable, not exhaustive."""
    return (
        f"[{session['id']}] {session['day']} {session['start']}-{session['end']} "
        f"| {session['stage']} | {session['format']}/{session['level']} "
        f"| {session['title']} — {speaker_names(session)}"
    )
