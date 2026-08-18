#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Installation complete. Run the app with: python3 main.py"
