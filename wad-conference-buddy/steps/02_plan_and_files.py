"""Step 2 — Make it plan, and make the plan survive.

    python steps/02_plan_and_files.py
    ls workspace/

WHAT'S NEW: two things, both one line each.

  backend=FilesystemBackend(...)   the agent's files land in ./workspace on disk
  middleware=[TodoListMiddleware()] the agent gets a write_todos tool

ON PLANNING BEING OPT-IN: in deepagents 0.7 task planning stopped being on by
default. Earlier tutorials show it appearing for free. It doesn't anymore, and
that is a fair example of why you pin versions and read changelogs for a library
moving this fast.

WHY IT MATTERS HERE: "plan my three days" is not one question. It is nine or ten
searches, a conflict check, and three files. Without todos the model tends to
answer the first third of the request thoroughly and then drift. With todos it
keeps a checklist and works through it.

WATCH FOR:
  - write_todos appearing early, then again as items flip to completed
  - write_file calls landing in ./workspace, which you can open in your editor
  - run it twice; the second run can read what the first one wrote

TRY THIS: comment out the middleware line and run the same prompt. Compare how
much of the request actually gets done.
"""

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import TodoListMiddleware

from buddy import run
from buddy.config import MODEL, WORKSPACE, preflight
from buddy.tools import READ_ONLY_TOOLS

preflight()

SYSTEM_PROMPT = """You are a conference buddy for WeAreDevelopers World Congress
North America 2026 in San Jose (Sept 23-25, San Jose McEnery Convention Center).

You have a filesystem. Use it as your working memory, not just as output:

  /profile.md        what you know about this attendee
  /plan/day1.md      Wednesday Sept 23
  /plan/day2.md      Thursday Sept 24
  /plan/day3.md      Friday Sept 25
  /notes/            anything they tell you during the event

Before answering anything about the attendee, check whether /profile.md exists
and read it. When you learn something durable about them, write it there.

When you build a schedule:
  1. Break the work into todos first.
  2. Search the agenda per day and per interest, not in one giant query.
  3. Run check_plan on your picks before you write anything down.
  4. Write one file per day. Each entry gets: time, ID, title, stage, one line
     on why it fits, and a named backup session for that slot.
  5. Only then summarise for the user, briefly. The detail lives in the files."""

agent = create_deep_agent(
    model=MODEL,
    tools=READ_ONLY_TOOLS,
    system_prompt=SYSTEM_PROMPT,
    backend=FilesystemBackend(root_dir=str(WORKSPACE), virtual_mode=True),
    middleware=[TodoListMiddleware()],
)

if __name__ == "__main__":
    run.run(
        agent,
        run.prompt_from_argv(
            "I'm a senior backend engineer at a mid-size fintech. We're about to put "
            "our first agentic feature in front of customers and I'm nervous about "
            "evals and security. I'd rather go deep than broad, I hate crowds, and "
            "I'm going to the party on Thursday so Friday morning should be gentle. "
            "Build me a plan for all three days."
        ),
    )
    print(f"\nNow look in {WORKSPACE}")
