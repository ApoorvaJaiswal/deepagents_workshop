"""Builds conference_buddy.ipynb.

Kept as a generator so the notebook stays diffable and regenerable. Edit here,
run `python scripts/build_notebook.py`, commit both.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CELLS = []


def md(text: str):
    CELLS.append(
        {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(True)}
    )


def code(text: str):
    CELLS.append(
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": text.strip("\n").splitlines(True),
        }
    )


# ───────────────────────────── Intro ─────────────────────────────

md("""
# Conference Buddy

### Building agents with `deepagents` — WeAreDevelopers World Congress North America 2026

You are going to build an agent that plans your three days at this conference,
using the actual agenda, in four steps.

| | Adds | The one thing it teaches |
|---|---|---|
| **1** | The agenda | `tools=` — and how to shape what a tool returns |
| **2** | A plan that persists | `backend=` and `TodoListMiddleware` |
| **3** | Specialist scouts | `subagents=` and context isolation |
| **4** | Trust | `memory=` and `interrupt_on=` |

Run the cells in order. Each section works on its own and each one ends with a
cell for you to break things in.

**The conference:** Sept 23–25 2026, San Jose McEnery Convention Center.
Day 0 is workshops and check-in, Day 1 adds the main program and the party,
Day 2 runs through the closing keynote.
""")

md("""
---
## 0. Setup

**In Codespaces:** dependencies and the dataset are already installed. Pick the
kernel *Conference Buddy (Python 3.11)* in the top right, then run the two cells
below — the first will detect the existing install and skip.

**Anywhere else:** run both cells. You'll be prompted for an API key if one isn't
already in your environment.

If the third cell prints a sentence about agent harnesses, you're ready.
""")

code("""
# In Codespaces this is already done — the cell detects that and skips.
try:
    import deepagents, langchain
    print("Dependencies already installed. Skipping.")
except ImportError:
    %pip install -q "deepagents>=0.7" "langchain>=1.0" "langchain-anthropic>=1.0" python-dotenv
    print("Installed. If imports fail below, restart the kernel and re-run.")

# Different provider? Add one of:
#   langchain-openai        langchain-google-genai        langchain-ollama
""")

code("""
import os, sys, subprocess
from pathlib import Path

IN_CODESPACES = os.environ.get("CODESPACES") == "true"

# Get the workshop package + dataset. In Codespaces and local clones this is a
# no-op; in Colab it fetches the repo.
if not Path("buddy").exists():
    subprocess.run(
        ["git", "clone", "--depth", "1",
         "https://github.com/YOUR-ORG/wad-conference-buddy.git", "_repo"],
        check=True,
    )
    for item in Path("_repo").iterdir():
        if item.name != ".git":
            item.rename(Path(item.name))

sys.path.insert(0, ".")

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

# Pick your model. Any provider works.
MODEL = os.environ.get("BUDDY_MODEL", "anthropic:claude-sonnet-4-6")

KEY_FOR = {
    "anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY",
    "google_genai": "GOOGLE_API_KEY", "openrouter": "OPENROUTER_API_KEY",
}
key_name = KEY_FOR.get(MODEL.split(":")[0])
if key_name and not os.environ.get(key_name):
    # Codespace secrets and .env files land in os.environ, so we only reach
    # this prompt if neither was set.
    from getpass import getpass
    os.environ[key_name] = getpass(f"{key_name}: ")

if not Path("data/sessions.json").exists():
    subprocess.run([sys.executable, "scripts/build_dataset.py"], check=True)

from buddy import data, nb
nb.reset_workspace()

print(f"Environment: {'GitHub Codespaces' if IN_CODESPACES else 'local / hosted'}")
print(f"Model:       {MODEL}")
print(f"Sessions:    {len(data.sessions())} across {len(data.event()['dates'])} days")
print(f"Tracks:      {len(data.tracks())}")
""")

code("""
from deepagents import create_deep_agent

smoke = create_deep_agent(model=MODEL, system_prompt="Be brief.")
nb.run(smoke, "In one sentence: what is an agent harness?")
""")

# ───────────────────────────── Step 1 ─────────────────────────────

md("""
---
# 1. Give it the agenda  ·  ~15 min

An agent with no tools is a chatbot with opinions about a conference it has never
heard of. Five functions fix that.

The interesting part is not that tools exist. It's **what they return**.

Two rules baked into the code below:

1. **Compact and ID-addressable.** `search_sessions` returns one line per hit.
   The agent pulls full detail with `get_session` only for the handful it cares
   about. Returning everything on every search is the fastest way to burn a
   context window.

2. **Arithmetic happens in Python.** `check_plan` is deterministic. Models are
   bad at *"does 14:50–15:20 overlap 13:30–14:00, and can I walk between those
   rooms in five minutes"* — and they are **confidently** bad at it.
""")

code("""
from langchain.tools import tool
from buddy import data


@tool
def list_program() -> str:
    \"\"\"List the event days, tracks and stages. Call this first to orient yourself.\"\"\"
    ev = data.event()
    lines = [f"{ev['name']} — {ev['venue']}, {ev['address']}"]
    for day in ev["dates"]:
        lines.append(f"  {day}: {ev['day_notes'][day]}")
    lines.append("Tracks: " + "; ".join(data.tracks()))
    lines.append("Stages: " + "; ".join(data.stages()))
    return "\\n".join(lines)


@tool
def search_sessions(query: str = "", day: str = "", track: str = "",
                    level: str = "", session_format: str = "", limit: int = 12) -> str:
    \"\"\"Search the conference agenda.

    Args:
        query: keywords matched against title, abstract, speaker and company.
        day: ISO date, one of 2026-09-23, 2026-09-24, 2026-09-25.
        track: exact track name (see list_program).
        level: beginner, intermediate or advanced.
        session_format: keynote, talk, panel, workshop, masterclass, live-coding, activity.
        limit: maximum results.

    Returns one compact line per session. Use get_session for full detail.
    \"\"\"
    terms = [t for t in query.lower().split() if t]
    hits = []
    for s in data.sessions():
        if day and s["day"] != day: continue
        if track and s["track"].lower() != track.lower(): continue
        if level and s["level"] != level: continue
        if session_format and s["format"] != session_format: continue

        haystack = " ".join([
            s["title"], s["abstract"], s["track"],
            " ".join(p["name"] for p in s["speakers"]),
            " ".join(p["company"] for p in s["speakers"]),
        ]).lower()

        score = sum(1 for t in terms if t in haystack)
        if terms and score == 0: continue
        hits.append((score, s))

    hits.sort(key=lambda h: (-h[0], h[1]["day"], h[1]["start"]))
    if not hits:
        return "No sessions matched. Try broader keywords or drop a filter."
    return "\\n".join(data.one_line(s) for _, s in hits[:limit])


@tool
def get_session(session_id: str) -> str:
    \"\"\"Get full detail for one session: abstract, speakers, stage, URL.\"\"\"
    s = data.by_id(session_id)
    if not s:
        return f"No session with id {session_id}."
    speakers = "\\n".join(f"  - {p['name']}, {p['title']} at {p['company']}" for p in s["speakers"])
    return (f"{s['title']}\\n{s['day']} {s['start']}-{s['end']} | {s['stage']} | "
            f"{s['format']} | {s['level']}\\nTrack: {s['track']}\\nSpeakers:\\n{speakers}\\n"
            f"Abstract: {s['abstract']}\\nURL: {s['url'] or 'n/a'}")


@tool
def walking_time(from_stage: str, to_stage: str) -> str:
    \"\"\"Minutes needed to walk between two stages in the venue.\"\"\"
    m = data.walk_minutes(from_stage, to_stage)
    return f"{from_stage} to {to_stage}: about {m} minutes." if m is not None \\
        else f"No walk time known between {from_stage} and {to_stage}."


@tool
def check_plan(session_ids: list[str]) -> str:
    \"\"\"Validate a draft schedule for time conflicts and impossible transitions.

    Returns overlapping sessions, and back-to-back pairs where the gap is shorter
    than the walk between stages. Always run this before presenting a schedule.
    \"\"\"
    picked, missing = [], []
    for sid in session_ids:
        s = data.by_id(sid)
        (picked if s else missing).append(s if s else sid)

    problems = [f"Unknown session IDs: {', '.join(missing)}"] if missing else []
    picked.sort(key=lambda s: (s["day"], data.to_minutes(s["start"])))

    for i, a in enumerate(picked):
        for b in picked[i + 1:]:
            if data.overlaps(a, b):
                problems.append(f"OVERLAP: [{a['id']}] {a['start']}-{a['end']} and "
                                f"[{b['id']}] {b['start']}-{b['end']} on {a['day']}")

    for a, b in zip(picked, picked[1:]):
        if a["day"] != b["day"] or data.overlaps(a, b): continue
        gap = data.to_minutes(b["start"]) - data.to_minutes(a["end"])
        walk = data.walk_minutes(a["stage"], b["stage"])
        if walk is not None and gap < walk:
            problems.append(f"TIGHT: [{a['id']}] ends {a['end']} in {a['stage']}, "
                            f"[{b['id']}] starts {b['start']} in {b['stage']}. "
                            f"Gap {gap} min, walk {walk} min.")

    if not problems:
        return f"Plan is feasible. {len(picked)} sessions, no overlaps, all transitions make it."
    return "Problems found:\\n" + "\\n".join(f"- {p}" for p in problems)


AGENDA_TOOLS = [list_program, search_sessions, get_session, walking_time, check_plan]
print(f"{len(AGENDA_TOOLS)} tools defined")
""")

md("""
### Test the tools before you spend a token

Tools are ordinary functions. Debug them without the model in the loop — it's
faster and free. Both of these session IDs are real sessions from the published
agenda, and they genuinely don't work back to back:
""")

code("""
print(search_sessions.invoke({"query": "agents security", "day": "2026-09-25"}))
print()
print(check_plan.invoke({"session_ids": ["1318895", "1320455"]}))
""")

md("""
Five minutes between them, six minutes of walking. That's the kind of thing that
ruins a morning, and the kind of thing a language model will cheerfully tell you
is fine.

Now hand the tools to an agent:
""")

code("""
SYSTEM_PROMPT = \"\"\"You are a conference buddy for WeAreDevelopers World Congress
North America 2026 in San Jose.

You help one attendee get the most out of three days. Ground every answer in the
agenda tools rather than guessing. If something isn't in the tools, say so.

When you recommend sessions, give the ID, the time, the stage, and one line on why
it fits this particular person. Never recommend two sessions that clash without
saying which one you'd drop.\"\"\"

buddy_v1 = create_deep_agent(
    model=MODEL,
    tools=AGENDA_TOOLS,
    system_prompt=SYSTEM_PROMPT,
)

nb.run(buddy_v1,
    "I'm a backend engineer who just started putting agents in production. "
    "What are the three most useful talks for me on Thursday?")
""")

md("""
**Watch the trace.** It orients with `list_program`, narrows with `search_sessions`,
then pulls detail on only the few it shortlisted. That progression is what the
compact-return rule buys you.

### Your turn

- Ask something the data can't answer — *"where's the nearest coffee?"* — and see
  how it behaves. That gap is where your next tool goes.
- Remove `check_plan` from `AGENDA_TOOLS`, rebuild the agent, and ask for a packed
  Thursday. Put it back. Compare.
- **Exercise:** write `find_speaker(name)` returning every session a person is on.
  Does the model prefer it over `search_sessions`?
""")

code("""
# Your experiments here.
""")

# ───────────────────────────── Step 2 ─────────────────────────────

md("""
---
# 2. Make it plan, and make the plan survive  ·  ~15 min

Two new arguments, one line each.

```python
backend=FilesystemBackend(...)      # the agent's files land in ./workspace, on disk
middleware=[TodoListMiddleware()]   # the agent gets a write_todos tool
```

**Planning is opt-in now.** In `deepagents` 0.7 task planning stopped being on by
default. Older tutorials show `write_todos` appearing for free; it doesn't
anymore. Fair warning about a library moving this fast — pin your versions.

**Why it matters here.** *"Plan my three days"* isn't one question. It's ten
searches, a conflict check, and three files. Without todos the model tends to
answer the first third thoroughly and then drift.
""")

code("""
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import TodoListMiddleware

PLANNER_PROMPT = \"\"\"You are a conference buddy for WeAreDevelopers World Congress
North America 2026 (Sept 23-25, San Jose McEnery Convention Center).

You have a filesystem. Use it as working memory, not just as output:

  /profile.md    what you know about this attendee
  /plan/day1.md  Wednesday Sept 23
  /plan/day2.md  Thursday Sept 24
  /plan/day3.md  Friday Sept 25
  /notes/        anything they tell you during the event

Before answering anything about the attendee, check whether /profile.md exists and
read it. When you learn something durable about them, write it there.

When you build a schedule:
  1. Break the work into todos first.
  2. Search per day and per interest, not in one giant query.
  3. Run check_plan on your picks before writing anything down.
  4. Write one file per day. Each entry: time, ID, title, stage, one line on why it
     fits, and a named backup session for that slot.
  5. Only then summarise for the user, briefly. The detail lives in the files.\"\"\"

buddy_v2 = create_deep_agent(
    model=MODEL,
    tools=AGENDA_TOOLS,
    system_prompt=PLANNER_PROMPT,
    backend=FilesystemBackend(root_dir="workspace", virtual_mode=True),
    middleware=[TodoListMiddleware()],
)
print("built")
""")

md("""
This next cell is the slow one — it's doing real work across three days.
Good moment to look at the `workspace/` folder in the file browser while it runs.
""")

code("""
state = nb.run(buddy_v2,
    "I'm a senior backend engineer at a mid-size fintech. We're about to put our "
    "first agentic feature in front of customers and I'm nervous about evals and "
    "security. I'd rather go deep than broad, I hate crowds, and I'm going to the "
    "party on Thursday so Friday morning should be gentle. "
    "Build me a plan for all three days.",
    show_tool_results=False)
""")

code("""
nb.show_todos(state)
""")

code("""
nb.show_workspace()
""")

md("""
Those files are on disk. Re-run the agent cell with a follow-up — *"actually I'll
skip Wednesday entirely"* — and it reads what it wrote before instead of starting
over.

### Your turn

- Comment out the `middleware=[...]` line, rebuild, run the same prompt. How much
  of the request actually gets done?
- Swap `FilesystemBackend` for the default `StateBackend` (just delete the
  `backend=` line). The plan still gets built — where does it go?
- **Exercise:** ask it to write `/notes/` entries during a session, then produce a
  trip report from them.
""")

code("""
# Your experiments here.
""")

# ───────────────────────────── Step 3 ─────────────────────────────

md("""
---
# 3. Delegate to specialists  ·  ~15 min

A subagent is a plain dict. It gets its own context window, its own system prompt,
and its own subset of tools. The supervisor calls it through the built-in `task`
tool and only ever sees its **final message**.

**Why this matters:** the session scout burns twenty tool results narrowing down a
track. Without isolation all twenty land in the supervisor's context and stay
there for the rest of the conversation. With it, the supervisor gets back six
lines. That's the difference between an agent that stays sharp over ninety minutes
and one that gets progressively vaguer.

**Note the tool split.** `logistics-scout` doesn't get `check_plan` — it has no
business building schedules. Giving each subagent the smallest useful toolset is
most of what makes them reliable.
""")

code("""
session_scout = {
    "name": "session-scout",
    "description": (
        "Finds and shortlists sessions for one day or one topic. Give it the "
        "attendee's interests and constraints. Returns a ranked shortlist with IDs, "
        "times and reasons. Use this instead of searching the agenda yourself."
    ),
    "system_prompt": \"\"\"You find sessions. You are thorough where the supervisor
cannot afford to be: search several phrasings, check adjacent tracks, pull detail on
anything promising.

Return at most eight sessions. For each: ID, day, time, stage, title, and one
sentence on why it fits. Add a short 'skipped' line naming anything obvious you
deliberately left out and why.

Your final message is the only thing the supervisor sees. Do not describe your
search process. Just report the shortlist.\"\"\",
    "tools": [list_program, search_sessions, get_session],
}

logistics_scout = {
    "name": "logistics-scout",
    "description": (
        "Answers venue and timing questions: walk times between stages, whether a "
        "transition is realistic, what happens on which day. Does not build schedules."
    ),
    "system_prompt": \"\"\"You answer practical questions about moving around the San Jose
McEnery Convention Center and about how the three days are structured.

Be concrete and short. If you don't have the data, say so plainly rather than
estimating. Never invent a walk time.\"\"\",
    "tools": [list_program, walking_time, get_session],
}

SUPERVISOR_PROMPT = \"\"\"You are the conference buddy for WeAreDevelopers World Congress
North America 2026. You coordinate; you do not do the digging yourself.

Delegate agenda research to session-scout, one task per day or per theme, and launch
them together when they are independent. Delegate venue and timing questions to
logistics-scout.

You keep: the attendee's profile, the final decisions, conflict checking via
check_plan, and the files under /plan/ and /profile.md.

Never write a schedule you have not run through check_plan.\"\"\"

buddy_v3 = create_deep_agent(
    model=MODEL,
    tools=[list_program, check_plan],          # the supervisor's own toolset is tiny
    system_prompt=SUPERVISOR_PROMPT,
    subagents=[session_scout, logistics_scout],
    backend=FilesystemBackend(root_dir="workspace", virtual_mode=True),
    middleware=[TodoListMiddleware()],
)
print("built")
""")

code("""
nb.run(buddy_v3,
    "I lead a platform team. I want Thursday and Friday planned around agent "
    "governance, security and delivery pipelines. Keep my afternoons lighter, and "
    "tell me how tight each transition is.",
    show_tool_results=False)
""")

md("""
**Look for two `task` calls in a single turn.** Independent subagents run
concurrently. Also notice how little comes back from each one relative to the work
it did.

### Your turn

- Ask something needing both scouts: *"plan Thursday around the sessions I care
  about, and tell me where to eat between them."*
- Give `session-scout` the `check_plan` tool too. Does the supervisor stop checking?
- **Exercise:** add a `people-scout` that finds speakers worth meeting and drafts an
  opener. Then read section 4 for why that subagent must not be allowed to send it.
""")

code("""
# Your experiments here.
""")

# ───────────────────────────── Step 4 ─────────────────────────────

md("""
---
# 4. It remembers you, and it asks before it acts  ·  ~15 min

Two parameters, and one loop you have to write yourself.

```python
memory=["/AGENTS.md"]   # always in context, and the agent can edit it
interrupt_on={...}      # pause before these tools and hand control back
```

`memory` is different from the files in section 2: those are read on demand, this
is present on every single turn. Keep it a profile, not a transcript.

**These two belong together.** Memory is what lets the agent stop asking you the
same questions. Approvals are what stop it acting on those assumptions
unsupervised. An agent with memory and no gates is the one that emails your CTO at
2am.

**Note the asymmetry.** `search_sessions` isn't gated — reading is cheap and
reversible. `send_message` contacts a human being and can't be undone. Gate on
consequences, not on how impressive the tool sounds.
""")

code("""
import shutil
from pathlib import Path

# Tools with real-world consequences (stubbed here, but pretend they aren't).
@tool
def send_message(to: str, body: str) -> str:
    \"\"\"Send a networking message to an attendee or speaker. Cannot be undone.\"\"\"
    return f"Message sent to {to}."


@tool
def add_to_calendar(session_ids: list[str]) -> str:
    \"\"\"Write the given sessions into the user's real calendar.\"\"\"
    titles = [data.by_id(s)["title"] for s in session_ids if data.by_id(s)]
    return f"Added {len(titles)} events: {'; '.join(titles)}"


# memory= expects the file to exist in the backend before the agent is built.
Path("workspace").mkdir(exist_ok=True)
if not Path("workspace/AGENTS.md").exists():
    shutil.copy("seed/AGENTS.md", "workspace/AGENTS.md")

print(Path("workspace/AGENTS.md").read_text())
""")

code("""
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

TRUSTED_PROMPT = \"\"\"You are the conference buddy for WeAreDevelopers World Congress
North America 2026 in San Jose.

/AGENTS.md holds what you know about this attendee and is always in your context.
When you learn something durable about them — role, interests, constraints,
preferences — update that file with edit_file. Keep it tight; it loads on every run,
so it should be a profile, not a transcript. Transient things go in /notes/ instead.

You can contact people on the attendee's behalf. Draft the message and let the
approval step show it to them. Write like the attendee would: specific, short, and
referencing something real from the session.\"\"\"

buddy_v4 = create_deep_agent(
    model=MODEL,
    tools=AGENDA_TOOLS + [send_message, add_to_calendar],
    system_prompt=TRUSTED_PROMPT,
    memory=["/AGENTS.md"],
    backend=FilesystemBackend(root_dir="workspace", virtual_mode=True),
    middleware=[TodoListMiddleware()],
    interrupt_on={
        "send_message": True,      # approve / edit / reject
        "add_to_calendar": True,
        # everything else runs unattended
    },
    checkpointer=MemorySaver(),     # required: pausing means state must live somewhere
)
print("built")
""")

md("""
The interrupt loop is yours to write. `deepagents` pauses the graph and hands you
the pending tool calls with their exact arguments — you're approving a *specific
message*, not a vague intention. How you present that is a product decision:
""")

code("""
def ask_human(interrupts) -> Command:
    \"\"\"Show pending tool calls, collect one decision each.\"\"\"
    decisions = []
    for itr in interrupts:
        value = getattr(itr, "value", itr)
        for request in (value or {}).get("action_requests", []):
            args = request.get("arguments") or request.get("args") or {}
            print("\\n" + "=" * 62)
            print(f"  APPROVAL NEEDED → {request.get('name')}")
            for k, v in args.items():
                print(f"    {k}: {v}")
            print("=" * 62)

            choice = input("  [a]pprove / [r]eject / [e]dit body: ").strip().lower()
            if choice.startswith("r"):
                reason = input("  reason (optional): ").strip()
                decisions.append({"type": "reject",
                                  "message": reason or "Rejected by the user."})
            elif choice.startswith("e"):
                args = dict(args)
                args["body"] = input("  new body: ").strip()
                decisions.append({"type": "edit",
                                  "args": {"name": request["name"], "arguments": args}})
            else:
                decisions.append({"type": "approve"})
    return Command(resume={"decisions": decisions})


def run_with_approvals(prompt, thread="s4"):
    config = {"configurable": {"thread_id": thread}}
    state = nb.run(buddy_v4, prompt, config=config, show_tool_results=False)

    while state and state.get("__interrupt__"):          # it may pause more than once
        command = ask_human(state["__interrupt__"])
        state = None
        for chunk in buddy_v4.stream(command, config=config, stream_mode="values"):
            state = chunk
            msg = chunk["messages"][-1]
            if msg.__class__.__name__ == "AIMessage":
                for call in getattr(msg, "tool_calls", []) or []:
                    print(f"  → {call['name']}")
                body = nb.text_of(msg.content).strip()
                if body:
                    print(f"\\nBuddy: {body}\\n")
    return state
""")

md("""
When you run the next cell an input box appears — in Jupyter Lab it shows under
the cell, in Colab at the bottom. Try **rejecting** the first message and watch the
agent adapt instead of crashing.
""")

code("""
state = run_with_approvals(
    "I'm a staff engineer at a healthcare company, I care about agent security and "
    "evals, and I'm hoping to move into a platform role. Remember that. Then find "
    "the one speaker I should most talk to and send them a short note asking for "
    "ten minutes.")
""")

code("""
print(Path("workspace/AGENTS.md").read_text())
""")

md("""
It rewrote its own profile of you. Run the previous cell again with a different
question and notice it doesn't re-ask who you are.

### Your turn

- Change `send_message` to `{"allowed_decisions": ["approve", "reject"]}` so the
  text can't be edited at approval time. Which would you actually ship?
- Gate `write_file` instead. Annoying? That's the lesson.
- **Exercise:** add a `when` predicate so only messages to speakers need approval,
  and messages to yourself don't.
""")

code("""
# Your experiments here.
""")

# ───────────────────────────── Wrap ─────────────────────────────

md("""
---
## What you built

```python
create_deep_agent(
    model=...,
    tools=...,              # 1  what it can do
    backend=...,            # 2  what it remembers within a task
    middleware=[Todo...],   # 2  how it stays on track
    subagents=[...],        # 3  how it stays focused
    memory=[...],           # 4  what it remembers about you
    interrupt_on={...},     # 4  what it may not do alone
)
```

Everything else in the harness — summarization, context offloading, prompt caching,
the `task` tool — you got for free and never configured.

## Where to go next

Things that didn't fit in ninety minutes:

- **Skills.** `skills=["./skills/"]` with a `SKILL.md` per repeatable procedure —
  *build-my-schedule*, *write-the-trip-report* — plus templates alongside. Loaded
  progressively, so they cost nothing until needed. This is the one I'd do first.
- **MCP.** Swap the stubbed `add_to_calendar` for a real calendar MCP server.
  `tools=` takes MCP tools directly.
- **Tracing.** Set `LANGSMITH_TRACING=true` and re-run section 3 to see where the
  subagents actually spent their tokens.
- **Async subagents.** The scouts here are synchronous — the supervisor blocks. For
  a buddy that keeps working while you're sitting in a talk, that's the wrong shape.

## About the data

`data/sessions.json` mixes real published sessions (`source: "published"`) with
filler written for this workshop (`source: "synthetic"`) so the agenda is dense
enough to have genuine conflicts. Stage names and walk times are invented.
`scripts/fetch_sessions.py` pulls the live feed.

Now go build one for a conference you're actually attending.
""")

notebook = {
    "cells": CELLS,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

out = ROOT / "conference_buddy.ipynb"
out.write_text(json.dumps(notebook, indent=1) + "\n")
print(f"wrote {out} — {len(CELLS)} cells "
      f"({sum(1 for c in CELLS if c['cell_type'] == 'code')} code)")
