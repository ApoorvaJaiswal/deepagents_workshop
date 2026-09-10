#!/usr/bin/env bash
#
# Runs every time you attach. Tells you in four lines whether this codespace is
# actually ready, instead of letting you find out at cell 3.

if [ -x .venv/bin/python ]; then PY="$(pwd)/.venv/bin/python"; else PY="$(command -v python3 || command -v python)"; fi
ok() { printf "  \033[32m✓\033[0m %s\n" "$1"; }
no() { printf "  \033[31m✗\033[0m %s\n" "$1"; FAILED=1; }

echo ""
echo "  ╭──────────────────────────────────────────────────────────────╮"
echo "  │  Conference Buddy — building agents with deepagents          │"
echo "  │  WeAreDevelopers World Congress North America 2026           │"
echo "  ╰──────────────────────────────────────────────────────────────╯"
echo ""

FAILED=0

[ -n "$PY" ] && ok "Python: $PY" || no "no Python found"
"$PY" -c "import ipykernel" 2>/dev/null \
    && ok "Jupyter kernel available" || no "ipykernel missing — notebook cannot run"
"$PY" -c "import deepagents" 2>/dev/null \
    && ok "deepagents installed" || no "deepagents missing"
[ -f data/sessions.json ] \
    && ok "dataset ready ($("$PY" -c 'import json;print(len(json.load(open("data/sessions.json"))["sessions"]))' 2>/dev/null) sessions)" \
    || no "data/sessions.json missing"

MODEL="${BUDDY_MODEL:-anthropic:claude-sonnet-4-6}"
case "${MODEL%%:*}" in
    anthropic)    KEY_VAR="ANTHROPIC_API_KEY" ;;
    openai)       KEY_VAR="OPENAI_API_KEY" ;;
    google_genai) KEY_VAR="GOOGLE_API_KEY" ;;
    *)            KEY_VAR="" ;;
esac
if [ -z "$KEY_VAR" ] || [ -n "${!KEY_VAR:-}" ]; then
    ok "API key present ($MODEL)"
else
    printf "  \033[33m!\033[0m %s\n" "$KEY_VAR not set — the notebook will prompt you (that's fine)"
fi

echo ""
if [ "$FAILED" = "1" ]; then
    echo "  Something is missing. Repair it with:"
    echo ""
    echo "      bash .devcontainer/setup.sh"
    echo ""
    echo "  Still broken? Send your instructor:  cat /tmp/buddy-setup.log"
else
    echo "  Ready. Open conference_buddy.ipynb and run the cells."
fi
echo ""