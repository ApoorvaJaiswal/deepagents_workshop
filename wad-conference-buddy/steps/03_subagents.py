"""Step 3 — Delegate to specialists.

    python steps/03_subagents.py

WHAT'S NEW: `subagents=`, a list of plain dicts.

Each subagent is an ephemeral agent with its own context window, its own system
prompt, and its own subset of tools. The supervisor calls them through the
built-in `task` tool and only ever sees their final report.

WHY IT MATTERS: the session-scout burns twenty tool results narrowing down a
track. Without isolation, all twenty land in the supervisor's context and stay
there for the rest of the conversation. With isolation, the supervisor gets back
six lines. That is the difference between an agent that stays sharp over a long
session and one that gets progressively vaguer.

NOTE THE TOOL SPLIT: session-scout gets the agenda tools. logistics-scout does
not get check_plan, because it has no business building schedules. Giving each
subagent the smallest useful toolset is most of what makes them reliable.

WATCH FOR: the supervisor launching more than one task call in a single turn.
Independent subagents run concurrently.

TRY THIS: ask something that needs both scouts, like "plan Thursday around the
sessions I care about, and tell me where to eat between them."

EXERCISE: add a `people-scout` that finds speakers worth meeting given the
attendee's goals, and drafts an opener. Then look at step 04 for why that
subagent should not be allowed to send anything.
"""

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import TodoListMiddleware

from buddy import run
from buddy.config import MODEL, WORKSPACE, preflight
from buddy.tools import (
    check_plan,
    get_session,
    list_program,
    search_sessions,
    walking_time,
)

preflight()

session_scout = {
    "name": "session-scout",
    "description": (
        "Finds and shortlists sessions for one day or one topic. Give it the "
        "attendee's interests and constraints. Returns a ranked shortlist with "
        "IDs, times and reasons. Use this instead of searching the agenda yourself."
    ),
    "system_prompt": """You find sessions. You are thorough where the supervisor
cannot afford to be: search several phrasings, check adjacent tracks, pull detail
on anything promising.

Return at most eight sessions. For each: ID, day, time, stage, title, and one
sentence on why it fits. Add a short 'skipped' line naming anything obvious you
deliberately left out and why.

Your final message is the only thing the supervisor sees. Do not describe your
search process. Just report the shortlist.""",
    "tools": [list_program, search_sessions, get_session],
}

logistics_scout = {
    "name": "logistics-scout",
    "description": (
        "Answers venue and timing questions: walk times between stages, whether a "
        "transition is realistic, what happens on which day. Does not build schedules."
    ),
    "system_prompt": """You answer practical questions about moving around the
San Jose McEnery Convention Center and about how the three days are structured.

Be concrete and short. If you don't have the data, say so plainly rather than
estimating. Never invent a walk time.""",
    "tools": [list_program, walking_time, get_session],
}

SYSTEM_PROMPT = """You are the conference buddy for WeAreDevelopers World Congress
North America 2026. You coordinate; you do not do the digging yourself.

Delegate agenda research to session-scout, one task per day or per theme, and
launch them together when they are independent. Delegate venue and timing
questions to logistics-scout.

You keep: the attendee's profile, the final decisions, conflict checking via
check_plan, and the files under /plan/ and /profile.md.

Never write a schedule you have not run through check_plan."""

agent = create_deep_agent(
    model=MODEL,
    tools=[check_plan, list_program],
    system_prompt=SYSTEM_PROMPT,
    subagents=[session_scout, logistics_scout],
    backend=FilesystemBackend(root_dir=str(WORKSPACE), virtual_mode=True),
    middleware=[TodoListMiddleware()],
)

if __name__ == "__main__":
    run.run(
        agent,
        run.prompt_from_argv(
            "I lead a platform team. I want Thursday and Friday planned around "
            "agent governance, security and delivery pipelines. Keep my afternoons "
            "lighter, and tell me how tight each transition is."
        ),
    )
