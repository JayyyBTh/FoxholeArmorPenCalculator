#!/usr/bin/env bash
set -euo pipefail

OWNER="JayyyBTh"
REPO="FoxholeArmorPenCalculator"

echo "[start] Installing Python deps…"
pip install --no-cache-dir -r requirements.txt

echo "[start] Fetching latest calc_cli from GitHub releases…"
LATEST_URL=$(curl -s https://api.github.com/repos/$OWNER/$REPO/releases/latest \
  | grep browser_download_url | grep calc_cli | cut -d '"' -f 4)

if [ -z "${LATEST_URL:-}" ]; then
  echo "No release asset found. Did the workflow run at least once?"
  exit 1
fi

curl -L "$LATEST_URL" -o calc_cli
chmod +x calc_cli

echo "[start] Starting bot…"
python bot.py
