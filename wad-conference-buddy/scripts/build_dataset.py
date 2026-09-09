"""Build data/sessions.json for the workshop.

Two kinds of records:
  source="published"  -> real sessions taken from the public WeAreDevelopers agenda
  source="synthetic"  -> plausible filler so the agenda has enough density to plan against

Run `python scripts/fetch_sessions.py` to replace the whole file with live data.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.wearedevelopers.com/world-congress-north-america/agenda/sessions"

STAGES = [
    "Main Stage",
    "AI Stage",
    "Platform Stage",
    "Security Stage",
    "Builders Zone",
    "Workshop Room A",
    "Workshop Room B",
]

# Rough walk times in minutes between stages inside the McEnery Convention Center.
# Synthetic: replace with real floor-plan distances if the organisers publish them.
WALK_MINUTES = {
    ("Main Stage", "AI Stage"): 4,
    ("Main Stage", "Platform Stage"): 6,
    ("Main Stage", "Security Stage"): 7,
    ("Main Stage", "Builders Zone"): 5,
    ("Main Stage", "Workshop Room A"): 9,
    ("Main Stage", "Workshop Room B"): 10,
    ("AI Stage", "Platform Stage"): 3,
    ("AI Stage", "Security Stage"): 5,
    ("AI Stage", "Builders Zone"): 4,
    ("AI Stage", "Workshop Room A"): 8,
    ("AI Stage", "Workshop Room B"): 9,
    ("Platform Stage", "Security Stage"): 3,
    ("Platform Stage", "Builders Zone"): 6,
    ("Platform Stage", "Workshop Room A"): 7,
    ("Platform Stage", "Workshop Room B"): 7,
    ("Security Stage", "Builders Zone"): 7,
    ("Security Stage", "Workshop Room A"): 6,
    ("Security Stage", "Workshop Room B"): 6,
    ("Builders Zone", "Workshop Room A"): 5,
    ("Builders Zone", "Workshop Room B"): 6,
    ("Workshop Room A", "Workshop Room B"): 2,
}


def spk(name, title, company):
    return {"name": name, "title": title, "company": company}


PUBLISHED = [
    {
        "id": "1318895",
        "title": "Manufacturing trust: speed and safety in the age of agents",
        "day": "2026-09-24",
        "start": "09:45",
        "end": "10:15",
        "stage": "Main Stage",
        "track": "Agentic systems in production",
        "level": "intermediate",
        "format": "keynote",
        "speakers": [spk("Mark Cavage", "President and COO", "Docker")],
        "abstract": "How to move fast with agents without giving up on safety, from the perspective of a company shipping developer tooling at scale.",
        "slug": "manufacturing-trust-speed-and-safety-in-the-age-of-agents-1318895",
    },
    {
        "id": "1320523",
        "title": "Building the Agentic Software Factory",
        "day": "2026-09-24",
        "start": "11:00",
        "end": "11:30",
        "stage": "Main Stage",
        "track": "Agentic systems in production",
        "level": "intermediate",
        "format": "keynote",
        "speakers": [
            spk("Thomas Dohmke", "CEO and Co-founder", "Entire"),
            spk("Matan Grinberg", "CEO and Co-Founder", "Factory"),
        ],
        "abstract": "What changes when agents write, review and ship a meaningful share of your code, and what the delivery pipeline has to look like to absorb it.",
        "slug": "building-the-agentic-software-factory-1320523",
    },
    {
        "id": "1320455",
        "title": "The New Rules of Software Delivery",
        "day": "2026-09-24",
        "start": "10:20",
        "end": "10:50",
        "stage": "Platform Stage",
        "track": "Platforms, pipelines and developer experience",
        "level": "intermediate",
        "format": "talk",
        "speakers": [
            spk("Moritz Plassnig", "CEO", "CloudBees"),
            spk("AJ Aitken", "Senior VP Infrastructure and Platform Engineering", "Datavant"),
        ],
        "abstract": "Release flows, review loops and CI expectations when both humans and agents are opening pull requests.",
        "slug": "the-new-rules-of-software-delivery-1320455",
    },
    {
        "id": "1297425",
        "title": "Application-Defined Compute: Rethinking Infrastructure for AI Applications",
        "day": "2026-09-24",
        "start": "11:00",
        "end": "11:30",
        "stage": "Platform Stage",
        "track": "Cloud, scale and reliability",
        "level": "advanced",
        "format": "talk",
        "speakers": [spk("Anurag Goel", "CEO", "Render")],
        "abstract": "Why AI workloads break the assumptions baked into traditional application infrastructure, and what a better shape looks like.",
        "slug": "application-defined-compute-rethinking-infrastructure-for-ai-applications-1297425",
    },
    {
        "id": "1320525",
        "title": "Running AI-Written Software in Production",
        "day": "2026-09-24",
        "start": "14:50",
        "end": "15:20",
        "stage": "Main Stage",
        "track": "Quality and testing in a non-deterministic world",
        "level": "intermediate",
        "format": "panel",
        "speakers": [
            spk("Milin Desai", "CEO", "Sentry"),
            spk("Ivan Burazin", "Co-founder and CEO", "Daytona"),
            spk("Anurag Goel", "Founder and CEO", "Render"),
        ],
        "abstract": "Three founders on what actually breaks when AI-generated code reaches real users, and how observability and sandboxing have had to adapt.",
        "slug": "running-ai-written-software-in-production-1320525",
    },
    {
        "id": "1324348",
        "title": "The future of workforce, at high speed",
        "day": "2026-09-24",
        "start": "16:10",
        "end": "16:40",
        "stage": "Main Stage",
        "track": "Engineering leadership in a shifting stack",
        "level": "beginner",
        "format": "keynote",
        "speakers": [
            spk("Daniela Dimitrova", "VP IT and CIO", "Mercedes-Benz North America")
        ],
        "abstract": "How a large engineering organisation is reshaping teams and skills as AI moves into everyday development work.",
        "slug": "the-future-of-workforce-at-high-speed-1324348",
    },
    {
        "id": "1325673",
        "title": "How LinkedIn Turns AI Breakthroughs into member and customer value",
        "day": "2026-09-25",
        "start": "10:20",
        "end": "10:50",
        "stage": "Main Stage",
        "track": "Building with AI as a craft",
        "level": "intermediate",
        "format": "keynote",
        "speakers": [spk("Erran Berger", "CTO, LinkedIn Engineering", "LinkedIn")],
        "abstract": "The path from research result to shipped product feature at LinkedIn scale.",
        "slug": "how-linkedin-turns-ai-breakthroughs-into-member-and-customer-value-1325673",
    },
    {
        "id": "1309401",
        "title": "Govern the Runtime, Not the Agent: One Control Plane for Every Model, Every Harness",
        "day": "2026-09-25",
        "start": "11:00",
        "end": "11:30",
        "stage": "Platform Stage",
        "track": "Agentic systems in production",
        "level": "advanced",
        "format": "talk",
        "speakers": [spk("Tushar Jain", "CTO", "Docker")],
        "abstract": "An argument for putting governance at the runtime layer rather than trying to constrain each individual agent.",
        "slug": "govern-the-runtime-not-the-agent-one-control-plane-for-every-model-every-harness-1309401",
    },
    {
        "id": "1314857",
        "title": "From Simulation to Reality: Overcoming the Data Scarcity Crisis in Physical AI",
        "day": "2026-09-25",
        "start": "12:55",
        "end": "13:25",
        "stage": "AI Stage",
        "track": "Data, analytics and the AI training stack",
        "level": "advanced",
        "format": "talk",
        "speakers": [
            spk("Mitesh Patel", "Developer Advocate and Manager", "NVIDIA Corporation")
        ],
        "abstract": "Synthetic data pipelines for robotics and physical AI, and where simulation stops being good enough.",
        "slug": "from-simulation-to-reality-overcoming-the-data-scarcity-crisis-in-physical-ai-1314857",
    },
    {
        "id": "1304898",
        "title": "A Hands-On Developer Guide to Inference Engineering",
        "day": "2026-09-25",
        "start": "13:30",
        "end": "14:00",
        "stage": "AI Stage",
        "track": "Building with AI as a craft",
        "level": "advanced",
        "format": "talk",
        "speakers": [
            spk("Ankit Patel", "VP of Developer Ecosystem", "NVIDIA"),
            spk("Philip Kiely", "Special Projects", "Baseten"),
        ],
        "abstract": "Practical inference optimisation: batching, quantisation, latency budgets and the trade-offs that actually move the needle.",
        "slug": "a-hands-on-developer-guide-to-inference-engineering-1304898",
    },
    {
        "id": "1309397",
        "title": "One Boundary for the Agentic Era",
        "day": "2026-09-25",
        "start": "15:30",
        "end": "16:00",
        "stage": "Security Stage",
        "track": "Security and trust",
        "level": "intermediate",
        "format": "talk",
        "speakers": [spk("Mark Lechner", "CISO", "Docker")],
        "abstract": "Where to draw the trust boundary when agents act on behalf of users across tools and systems.",
        "slug": "one-boundary-for-the-agentic-era-1309397",
    },
    {
        "id": "1171269",
        "title": "Building Pragmatic AI: 10 AI Features Your Users Actually Want",
        "day": "2026-09-23",
        "start": "10:00",
        "end": "17:00",
        "stage": "Workshop Room A",
        "track": "Building with AI as a craft",
        "level": "beginner",
        "format": "workshop",
        "speakers": [
            spk("Jonathan \"J.\" Tower", "Founding Partner", "Trailhead Technology")
        ],
        "abstract": "A full-day workshop on shipping AI features people use, rather than features that demo well.",
        "slug": "building-pragmatic-ai-10-ai-features-your-users-actually-want-1171269",
    },
]

# Filler so each slot has real competition. Clearly marked as synthetic.
SYNTHETIC = [
    ("Evals That Survive Contact With Production", "2026-09-24", "09:45", "10:15", "AI Stage",
     "Quality and testing in a non-deterministic world", "intermediate", "talk",
     [("Priya Raman", "Staff ML Engineer", "Datadog")],
     "Building regression suites for LLM features when the output is never byte-identical twice."),
    ("Prompt Injection Is an Authorization Problem", "2026-09-24", "09:45", "10:15", "Security Stage",
     "Security and trust", "advanced", "talk",
     [("Daniel Okoye", "Principal Security Engineer", "Sysdig")],
     "Reframing injection defence around what the agent is allowed to do, not what it is allowed to read."),
    ("Context Engineering for Long-Running Agents", "2026-09-24", "10:20", "10:50", "AI Stage",
     "Agentic systems in production", "intermediate", "talk",
     [("Sofia Lindqvist", "AI Engineer", "Together AI")],
     "Summarisation, offloading and subagent isolation as a budget you actively manage."),
    ("Your Internal Platform Is a Product. Act Like It.", "2026-09-24", "11:40", "12:10", "Platform Stage",
     "Platforms, pipelines and developer experience", "beginner", "talk",
     [("Marcus Webb", "Principal Engineer", "Workday")],
     "Golden paths people opt into, and how to tell whether yours is one."),
    ("Debugging Agents With Traces, Not Print Statements", "2026-09-24", "11:40", "12:10", "AI Stage",
     "Agentic systems in production", "intermediate", "talk",
     [("Hannah Cho", "Developer Advocate", "Dash0")],
     "What to instrument in an agent loop and how to read the resulting trace."),
    ("WebAssembly Grew Up", "2026-09-24", "13:30", "14:00", "Platform Stage",
     "Modern languages and runtimes", "intermediate", "talk",
     [("Tomasz Nowak", "Systems Engineer", "Arm")],
     "Wasm outside the browser, from edge functions to plugin sandboxes."),
    ("Vector Databases Are Just Databases", "2026-09-24", "13:30", "14:00", "AI Stage",
     "Data, analytics and the AI training stack", "beginner", "talk",
     [("Rita Alvarez", "Data Engineer", "Box")],
     "Indexing, freshness and cost, minus the mystique."),
    ("On-Call for Nondeterministic Systems", "2026-09-24", "14:50", "15:20", "Platform Stage",
     "Cloud, scale and reliability", "advanced", "talk",
     [("James Whitfield", "SRE Lead", "PagerDuty")],
     "SLOs when half your critical path is a model you do not control."),
    ("Refactoring Legacy Code With Agents", "2026-09-24", "14:50", "15:20", "AI Stage",
     "Building with AI as a craft", "intermediate", "talk",
     [("Aisha Bello", "Sr. Software Engineer", "BNY")],
     "What worked on a twelve-year-old Java codebase, and what blew up."),
    ("Supply Chain Security for AI Dependencies", "2026-09-24", "16:10", "16:40", "Security Stage",
     "Security and trust", "intermediate", "talk",
     [("Erik Sandberg", "Security Engineer", "Docker")],
     "Model weights, prompt templates and MCP servers are all dependencies now."),
    ("Live Coding: An Agent That Reviews Its Own PRs", "2026-09-24", "16:10", "17:10", "Builders Zone",
     "Building with AI as a craft", "intermediate", "live-coding",
     [("Nina Petrova", "Sr. Staff Engineer", "Netlify")],
     "Built from an empty file on stage, failures included."),
    ("Cost Engineering for Token-Heavy Products", "2026-09-25", "09:45", "10:15", "AI Stage",
     "Cloud, scale and reliability", "intermediate", "talk",
     [("Oliver Brandt", "Engineering Manager", "You.com")],
     "Caching, routing and the unglamorous work of getting unit economics to close."),
    ("Testing What You Cannot Predict", "2026-09-25", "09:45", "10:15", "Security Stage",
     "Quality and testing in a non-deterministic world", "beginner", "talk",
     [("Grace Mendoza", "SDET", "Cypress.io")],
     "Replay traffic, synthetic users and property-based testing for AI features."),
    ("MCP in Anger: Six Months of Production Servers", "2026-09-25", "11:40", "12:10", "AI Stage",
     "Agentic systems in production", "advanced", "talk",
     [("Felix Adeyemi", "Platform Engineer", "Coinbase")],
     "Auth, rate limits, versioning and the failure modes nobody warns you about."),
    ("Rust for People Who Ship Python", "2026-09-25", "11:40", "12:10", "Platform Stage",
     "Modern languages and runtimes", "beginner", "talk",
     [("Clara Jensen", "Sr. Engineer", "Nx")],
     "Where a Rust extension pays for itself, and where it absolutely does not."),
    ("Hiring and Growing Engineers in an Agentic Org", "2026-09-25", "12:55", "13:25", "Main Stage",
     "Engineering leadership in a shifting stack", "beginner", "talk",
     [("Robert Mensah", "VP Engineering", "PwC")],
     "What junior work looks like when the boilerplate is already written."),
    ("Streaming Data Pipelines That Do Not Page You", "2026-09-25", "13:30", "14:00", "Platform Stage",
     "Data, analytics and the AI training stack", "advanced", "talk",
     [("Yuki Tanaka", "Analytics Engineer", "Stack Overflow")],
     "Contracts, lineage and backfills for pipelines feeding both dashboards and models."),
    ("Frontend in the Age of Generated UI", "2026-09-25", "14:20", "14:50", "Builders Zone",
     "Building with AI as a craft", "beginner", "talk",
     [("Lena Fischer", "Sr. Web Developer", "Sentry")],
     "Design systems as the constraint that keeps generated interfaces coherent."),
    ("Threat Modeling Agentic Workflows", "2026-09-25", "14:20", "14:50", "Security Stage",
     "Security and trust", "advanced", "talk",
     [("Samuel Reyes", "CISO", "Intuition Machines")],
     "A practical STRIDE-style walkthrough of a tool-using agent."),
    ("Closing Keynote: What We Actually Learned", "2026-09-25", "16:30", "17:15", "Main Stage",
     "Engineering leadership in a shifting stack", "beginner", "keynote",
     [("Angie Jones", "VP Developer Experience", "Agentic AI Foundation")],
     "Three days condensed into the handful of things worth taking home."),
    ("Workshop: Build a Deep Agent From Scratch", "2026-09-23", "13:00", "16:00", "Workshop Room B",
     "Agentic systems in production", "intermediate", "workshop",
     [("Workshop Host", "Instructor", "WeAreDevelopers")],
     "Hands-on session building an agent harness step by step. (This is the session you are sitting in.)"),
    ("Masterclass: Observability for LLM Applications", "2026-09-23", "10:00", "13:00", "Workshop Room B",
     "Quality and testing in a non-deterministic world", "intermediate", "masterclass",
     [("Christine Yen", "CEO and Co-Founder", "Honeycomb")],
     "Instrumenting, sampling and querying traces from model-backed services."),
    ("CODE100 Finals", "2026-09-24", "17:30", "19:00", "Main Stage",
     "Community", "beginner", "activity",
     [("CODE100", "Challenge", "WeAreDevelopers")],
     "The live coding challenge final. Loud, fast and worth watching even if you are not competing."),
    ("Official Congress Party", "2026-09-24", "20:00", "23:59", "Main Stage",
     "Community", "beginner", "activity",
     [("WeAreDevelopers", "Host", "WeAreDevelopers")],
     "The after-show. Plan your Friday morning accordingly."),
]


def build():
    sessions = []
    for s in PUBLISHED:
        sessions.append(
            {
                **s,
                "source": "published",
                "url": f"{BASE}/{s.pop('slug')}",
            }
        )
    for i, (title, day, start, end, stage, track, level, fmt, speakers, abstract) in enumerate(
        SYNTHETIC, start=1
    ):
        sessions.append(
            {
                "id": f"syn-{i:03d}",
                "title": title,
                "day": day,
                "start": start,
                "end": end,
                "stage": stage,
                "track": track,
                "level": level,
                "format": fmt,
                "speakers": [spk(*p) for p in speakers],
                "abstract": abstract,
                "source": "synthetic",
                "url": "",
            }
        )

    sessions.sort(key=lambda s: (s["day"], s["start"], s["stage"]))

    payload = {
        "event": {
            "name": "WeAreDevelopers World Congress North America 2026",
            "dates": ["2026-09-23", "2026-09-24", "2026-09-25"],
            "venue": "San Jose McEnery Convention Center",
            "address": "150 W San Carlos St, San Jose, CA",
            "timezone": "America/Los_Angeles",
            "day_notes": {
                "2026-09-23": "Day 0. Pre-check-in and badge pickup, workshops, masterclasses, satellite events, Tech Leaders Night.",
                "2026-09-24": "Day 1. Official opening, main program, tech expo, CODE100 finals, official Congress party.",
                "2026-09-25": "Day 2. Main program, tech expo, workshops, closing keynote.",
            },
        },
        "provenance": (
            "Sessions marked source='published' are from the public agenda. "
            "Sessions marked source='synthetic' were written for this workshop so the "
            "schedule has enough density to plan against. Stage names and walk times are "
            "synthetic. Run scripts/fetch_sessions.py to replace this with live data."
        ),
        "stages": STAGES,
        "walk_minutes": {f"{a}|{b}": m for (a, b), m in WALK_MINUTES.items()},
        "sessions": sessions,
    }

    out = ROOT / "data" / "sessions.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {out} ({len(sessions)} sessions)")


if __name__ == "__main__":
    build()
