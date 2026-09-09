"""Step 0 — Does everything work?

Run this before the workshop starts:

    python steps/00_hello.py

You should see the agent answer in one turn without calling any tools. If this
works, your key and model are fine and you can follow along.
"""

from deepagents import create_deep_agent

from buddy import run
from buddy.config import MODEL, preflight

preflight()

agent = create_deep_agent(
    model=MODEL,
    system_prompt="You are a conference buddy. Be brief.",
)

if __name__ == "__main__":
    print(f"Model: {MODEL}")
    run.run(agent, "In one sentence, what is an agent harness?")
