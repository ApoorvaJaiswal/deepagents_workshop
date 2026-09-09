#!/usr/bin/env bash
# Runs once when the codespace is created (or baked in, if you enable prebuilds).
set -euo pipefail

echo "Installing dependencies..."
pip install --upgrade pip --quiet
pip install --quiet -e ".[all-providers]" jupyterlab ipykernel

echo "Building the conference dataset..."
python scripts/build_dataset.py

# Register a kernel with a name attendees will recognise in the notebook picker.
python -m ipykernel install --user --name conference-buddy \
    --display-name "Conference Buddy (Python 3.11)" >/dev/null

mkdir -p workspace

# Warn early rather than at cell 3.
MODEL="${BUDDY_MODEL:-anthropic:claude-sonnet-4-6}"
PROVIDER="${MODEL%%:*}"
case "$PROVIDER" in
    anthropic)    KEY_VAR="ANTHROPIC_API_KEY" ;;
    openai)       KEY_VAR="OPENAI_API_KEY" ;;
    google_genai) KEY_VAR="GOOGLE_API_KEY" ;;
    *)            KEY_VAR="" ;;
esac

if [ -n "$KEY_VAR" ] && [ -z "${!KEY_VAR:-}" ]; then
    cat <<EOF

  ⚠  $KEY_VAR is not set.

     Either add it as a Codespace secret
       github.com/settings/codespaces  →  New secret  →  scope it to this repo
     then rebuild the container, or just let the notebook prompt you for it.

     The notebook falls back to getpass, so you are not blocked either way.

EOF
fi

echo "Setup complete."
