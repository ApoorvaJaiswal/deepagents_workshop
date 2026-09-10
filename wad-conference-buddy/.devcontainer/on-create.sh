#!/usr/bin/env bash
# Baked into the prebuild image. Put slow things here.
set -euo pipefail

echo "Installing dependencies..."
pip install --upgrade pip --quiet
pip install --quiet -e ".[all-providers]" jupyterlab ipykernel

echo "Building the conference dataset..."
python scripts/build_dataset.py

mkdir -p workspace

# NOTE: deliberately NOT registering a custom-named kernel. The notebook's
# metadata asks for "python3"; a differently-named kernelspec makes VS Code
# stop and prompt instead of auto-selecting. One interpreter, one kernel.
python -m ipykernel install --sys-prefix --name python3 \
    --display-name "Python 3.11" >/dev/null 2>&1 || true

echo "Dependencies installed."