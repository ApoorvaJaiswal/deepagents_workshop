"""Step 1 — Give the buddy the agenda.

    python steps/01_tools.py
    python steps/01_tools.py "I do platform engineering. What should I see on Thursday?"

WHAT'S NEW: the `tools=` argument.

An agent without tools is a chatbot with opinions about a conference it has
never heard of. Five functions turn it into something useful.

WATCH FOR: the agent calls list_program first to orient itself, then narrows
with search_sessions, then pulls detail with get_session only for the handful
it actually cares about. That progression is the whole point of returning
compact, ID-addressable results.

TRY THIS:
  - Ask something the data cannot answer ("where's the nearest coffee?") and
    watch how it behaves. This is where you'd add another tool.
  - Delete `check_plan` from the tools list and ask for a packed Thursday.
    Then put it back. Compare the schedules.

EXERCISE: add a `find_speaker(name)` tool that returns every session a person
is on, and see whether the model prefers it over search_sessions.
"""

from deepagents import create_deep_agent

from buddy import run
from buddy.config import MODEL, preflight
from buddy.tools import READ_ONLY_TOOLS

preflight()

SYSTEM_PROMPT = """You are a conference buddy for WeAreDevelopers World Congress
North America 2026 in San Jose.

You help one attendee get the most out of three days. Always ground your answers
in the agenda tools rather than guessing. If a session is not in the tools, say so.

When you recommend sessions, give the ID, the time, the stage and one line on why
it fits this particular person. Never recommend two sessions that clash without
saying which one you'd drop."""

agent = create_deep_agent(
    model=MODEL,
    tools=READ_ONLY_TOOLS,
    system_prompt=SYSTEM_PROMPT,
)

if __name__ == "__main__":
    run.run(
        agent,
        run.prompt_from_argv(
            "I'm a backend engineer who just started putting agents in production. "
            "What are the three most useful talks for me on Thursday?"
        ),
    )
