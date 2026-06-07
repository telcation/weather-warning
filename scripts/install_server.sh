#!/usr/bin/env bash
set -euo pipefail
APP_DIR=/var/www/weather-warning-app
cd "$APP_DIR"
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
mkdir -p instance
