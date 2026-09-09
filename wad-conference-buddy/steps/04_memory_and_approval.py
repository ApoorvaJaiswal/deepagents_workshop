"""Step 4 — It remembers you, and it asks before it acts.

    python steps/04_memory_and_approval.py
    cat workspace/AGENTS.md          # after the first run
    python steps/04_memory_and_approval.py "Message Tushar Jain about his governance talk"

WHAT'S NEW: two parameters, and one loop you have to write yourself.

  memory=["/AGENTS.md"]   loaded into context on every run, and the agent can
                          edit it. This is different from the files in step 2:
                          those are read on demand, this is always present.

  interrupt_on={...}      the agent pauses before calling these tools and hands
                          control back to you. Needs a checkpointer, because
                          pausing means the state has to live somewhere.

WHY BOTH IN ONE STEP: they are the two halves of trust. Memory is what lets the
agent stop asking you the same questions. Approvals are what stop it from acting
on those assumptions unsupervised. An agent with memory and no gates is the one
that emails your CTO at 2am.

NOTE THE ASYMMETRY: check_plan and search_sessions are not gated. Reading is
cheap and reversible. send_message contacts a human being and cannot be undone.
Gate on consequences, not on how impressive the tool sounds.

WATCH FOR:
  - the interrupt payload: it contains action_requests with the exact arguments,
    so you are approving a specific message, not a vague intention
  - rejecting, and seeing the agent adapt rather than crash
  - run it twice and notice the second run already knows who you are

EXERCISE: change send_message to {"allowed_decisions": ["approve", "reject"]} so
the text cannot be edited at approval time, and decide which you'd actually ship.
"""

import shutil

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain.agents.middleware import TodoListMiddleware
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from buddy import run
from buddy.config import MODEL, REPO_ROOT, WORKSPACE, preflight
from buddy.tools import ACTION_TOOLS, READ_ONLY_TOOLS

preflight()

# memory= expects the file to already exist in the backend before the agent is built.
MEMORY_FILE = WORKSPACE / "AGENTS.md"
if not MEMORY_FILE.exists():
    shutil.copy(REPO_ROOT / "seed" / "AGENTS.md", MEMORY_FILE)

SYSTEM_PROMPT = """You are the conference buddy for WeAreDevelopers World Congress
North America 2026 in San Jose.

/AGENTS.md holds what you know about this attendee and is always in your context.
When you learn something durable about them (role, interests, constraints,
preferences), update that file with edit_file. Keep it tight; it is loaded on
every run, so it should be a profile, not a transcript. Transient things like
session notes go in /notes/ instead.

You can contact people on the attendee's behalf. Before you do, draft the message
and let the approval step show it to them. Write messages that sound like the
attendee, not like a template: specific, short, and referencing something real
from the session."""

CHECKPOINTER = MemorySaver()

agent = create_deep_agent(
    model=MODEL,
    tools=READ_ONLY_TOOLS + ACTION_TOOLS,
    system_prompt=SYSTEM_PROMPT,
    memory=["/AGENTS.md"],
    backend=FilesystemBackend(root_dir=str(WORKSPACE), virtual_mode=True),
    middleware=[TodoListMiddleware()],
    interrupt_on={
        "send_message": True,       # approve / edit / reject
        "add_to_calendar": True,
        # everything else runs unattended
    },
    checkpointer=CHECKPOINTER,
)


def describe(request: dict) -> str:
    name = request.get("name", "?")
    args = request.get("arguments") or request.get("args") or {}
    lines = [f"\n  TOOL: {name}"]
    for key, value in args.items():
        text = str(value)
        lines.append(f"    {key}: {text}")
    return "\n".join(lines)


def ask_human(interrupts) -> Command:
    """Show the pending tool calls and collect one decision per request."""
    decisions = []
    for itr in interrupts:
        value = getattr(itr, "value", itr)
        requests = (value or {}).get("action_requests", [])
        for request in requests:
            print("\n" + "=" * 60)
            print("  APPROVAL NEEDED")
            print(describe(request))
            print("=" * 60)
            choice = input("  [a]pprove / [r]eject / [e]dit body: ").strip().lower()

            if choice.startswith("r"):
                reason = input("  reason (optional): ").strip()
                decisions.append(
                    {"type": "reject", "message": reason or "Rejected by the user."}
                )
            elif choice.startswith("e"):
                new_body = input("  new body: ").strip()
                args = dict(request.get("arguments") or request.get("args") or {})
                args["body"] = new_body
                decisions.append(
                    {"type": "edit", "args": {"name": request["name"], "arguments": args}}
                )
            else:
                decisions.append({"type": "approve"})

    return Command(resume={"decisions": decisions})


def run_with_approvals(prompt: str, thread: str = "workshop-04") -> None:
    config = {"configurable": {"thread_id": thread}}
    state = run.run(agent, prompt, config=config)

    # Keep resuming for as long as the agent keeps pausing.
    while state and state.get("__interrupt__"):
        command = ask_human(state["__interrupt__"])
        state = None
        for chunk in agent.stream(command, config=config, stream_mode="values"):
            state = chunk
            msg = chunk["messages"][-1]
            if msg.__class__.__name__ == "AIMessage":
                for call in getattr(msg, "tool_calls", []) or []:
                    print(f"  → {call['name']}")
                body = run._text(msg.content).strip()
                if body:
                    print(f"\nBuddy: {body}\n")


if __name__ == "__main__":
    run_with_approvals(
        run.prompt_from_argv(
            "I'm a staff engineer at a healthcare company, I care about agent "
            "security and evals, and I'm hoping to move into a platform role. "
            "Remember that. Then find the one speaker I should most talk to and "
            "send them a short note asking for ten minutes."
        )
    )
    print(f"\nCheck {MEMORY_FILE} to see what it remembered.")
