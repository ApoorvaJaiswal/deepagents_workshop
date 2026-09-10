#!/usr/bin/env bash
# Runs for every codespace, including ones restored from a prebuild. Keep it fast.
set -euo pipefail

# Prebuild images can predate a dependency bump; this is a no-op when current.
pip install --quiet -e ".[all-providers]" 2>/dev/null || true
[ -f data/sessions.json ] || python scripts/build_dataset.py
mkdir -p workspace

MODEL="${BUDDY_MODEL:-anthropic:claude-sonnet-4-6}"
case "${MODEL%%:*}" in
    anthropic)    KEY_VAR="ANTHROPIC_API_KEY" ;;
    openai)       KEY_VAR="OPENAI_API_KEY" ;;
    google_genai) KEY_VAR="GOOGLE_API_KEY" ;;
    *)            KEY_VAR="" ;;
esac

if [ -n "$KEY_VAR" ] && [ -z "${!KEY_VAR:-}" ]; then
    echo ""
    echo "  ⚠  $KEY_VAR is not set. The notebook will prompt you for it."
    echo "     To avoid the prompt: github.com/settings/codespaces → New secret"
    echo ""
fi