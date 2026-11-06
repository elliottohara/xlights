#!/bin/sh
set -eu
url=http://127.0.0.1:8795/
until curl --max-time 3 -fsS "$url" >/dev/null; do sleep 1; done
exec chromium --ozone-platform=wayland --disable-gpu --password-store=basic \
  --kiosk --no-first-run --user-data-dir="$HOME/.config/yard-chromium-clean" "$url"
