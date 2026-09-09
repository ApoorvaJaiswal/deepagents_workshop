"""Tools the buddy can call.

Two design rules worth calling out in the room:

1. Tool results are compact and ID-addressable. `search_sessions` returns one
   line per hit, not full abstracts. The agent asks for detail via `get_session`
   when it actually needs it. Dumping everything into every result is the
   fastest way to burn a context window.

2. Anything involving time arithmetic is done in Python, not by the model.
   `check_plan` is deterministic. Models are bad at "does 14:50-15:20 overlap
   13:30-14:00 and can I walk there in time", and they are confidently bad at it.
"""

try:
    from langchain.tools import tool
except ImportError:  # older layouts
    from langchain_core.tools import tool

from buddy import data


@tool
def list_program() -> str:
    """List the event days, tracks and stages. Call this first to orient yourself."""
    ev = data.event()
    lines = [f"{ev['name']} — {ev['venue']}, {ev['address']}"]
    for day in ev["dates"]:
        lines.append(f"  {day}: {ev['day_notes'][day]}")
    lines.append("Tracks: " + "; ".join(data.tracks()))
    lines.append("Stages: " + "; ".join(data.stages()))
    return "\n".join(lines)


@tool
def search_sessions(
    query: str = "",
    day: str = "",
    track: str = "",
    level: str = "",
    session_format: str = "",
    limit: int = 12,
) -> str:
    """Search the conference agenda.

    Args:
        query: free-text keywords matched against title, abstract, speaker and company.
        day: optional ISO date filter, one of 2026-09-23, 2026-09-24, 2026-09-25.
        track: optional exact track name (see list_program).
        level: optional one of beginner, intermediate, advanced.
        session_format: optional one of keynote, talk, panel, workshop, masterclass,
            live-coding, activity.
        limit: maximum results to return.

    Returns one compact line per session. Use get_session for full detail.
    """
    terms = [t for t in query.lower().split() if t]
    hits = []
    for s in data.sessions():
        if day and s["day"] != day:
            continue
        if track and s["track"].lower() != track.lower():
            continue
        if level and s["level"] != level:
            continue
        if session_format and s["format"] != session_format:
            continue

        haystack = " ".join(
            [
                s["title"],
                s["abstract"],
                s["track"],
                " ".join(p["name"] for p in s["speakers"]),
                " ".join(p["company"] for p in s["speakers"]),
            ]
        ).lower()

        score = sum(1 for t in terms if t in haystack)
        if terms and score == 0:
            continue
        hits.append((score, s))

    hits.sort(key=lambda h: (-h[0], h[1]["day"], h[1]["start"]))
    if not hits:
        return "No sessions matched. Try broader keywords or drop a filter."
    return "\n".join(data.one_line(s) for _, s in hits[:limit])


@tool
def get_session(session_id: str) -> str:
    """Get the full detail for one session, including abstract and speaker bios."""
    s = data.by_id(session_id)
    if not s:
        return f"No session with id {session_id}."
    speakers = "\n".join(
        f"  - {p['name']}, {p['title']} at {p['company']}" for p in s["speakers"]
    )
    return (
        f"{s['title']}\n"
        f"{s['day']} {s['start']}-{s['end']} | {s['stage']} | {s['format']} | {s['level']}\n"
        f"Track: {s['track']}\n"
        f"Speakers:\n{speakers}\n"
        f"Abstract: {s['abstract']}\n"
        f"URL: {s['url'] or 'n/a'}"
    )


@tool
def check_plan(session_ids: list[str]) -> str:
    """Validate a draft schedule for time conflicts and impossible transitions.

    Pass the session IDs you are considering. Returns any overlapping sessions and
    any back-to-back pairs where the gap is shorter than the walk between stages.
    Always run this before presenting a schedule to the user.
    """
    picked = []
    missing = []
    for sid in session_ids:
        s = data.by_id(sid)
        (picked if s else missing).append(s if s else sid)

    problems = []
    if missing:
        problems.append(f"Unknown session IDs: {', '.join(missing)}")

    picked.sort(key=lambda s: (s["day"], data.to_minutes(s["start"])))

    for i, a in enumerate(picked):
        for b in picked[i + 1 :]:
            if data.overlaps(a, b):
                problems.append(
                    f"OVERLAP: [{a['id']}] {a['start']}-{a['end']} and "
                    f"[{b['id']}] {b['start']}-{b['end']} on {a['day']}"
                )

    for a, b in zip(picked, picked[1:]):
        if a["day"] != b["day"] or data.overlaps(a, b):
            continue
        gap = data.to_minutes(b["start"]) - data.to_minutes(a["end"])
        walk = data.walk_minutes(a["stage"], b["stage"])
        if walk is not None and gap < walk:
            problems.append(
                f"TIGHT: [{a['id']}] ends {a['end']} in {a['stage']}, "
                f"[{b['id']}] starts {b['start']} in {b['stage']}. "
                f"Gap {gap} min, walk {walk} min."
            )

    if not problems:
        return f"Plan is feasible. {len(picked)} sessions, no overlaps, all transitions make it."
    return "Problems found:\n" + "\n".join(f"- {p}" for p in problems)


@tool
def walking_time(from_stage: str, to_stage: str) -> str:
    """How many minutes it takes to walk between two stages in the venue."""
    m = data.walk_minutes(from_stage, to_stage)
    if m is None:
        return f"No walk time known between {from_stage} and {to_stage}."
    return f"{from_stage} to {to_stage}: about {m} minutes."


# --- Tools with side effects. Used in step 04 to demonstrate approvals. ---


@tool
def send_message(to: str, body: str) -> str:
    """Send a networking message to another attendee or a speaker.

    This contacts a real human on the user's behalf. It cannot be undone.
    """
    return f"Message sent to {to}: {body[:80]}..."


@tool
def add_to_calendar(session_ids: list[str]) -> str:
    """Write the given sessions into the user's real calendar."""
    titles = [data.by_id(s)["title"] for s in session_ids if data.by_id(s)]
    return f"Added {len(titles)} events to calendar: {'; '.join(titles)}"


READ_ONLY_TOOLS = [
    list_program,
    search_sessions,
    get_session,
    check_plan,
    walking_time,
]

ACTION_TOOLS = [send_message, add_to_calendar]
