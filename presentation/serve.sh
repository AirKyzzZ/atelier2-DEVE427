#!/usr/bin/env bash
# Serve the presentation over HTTP so the phone (same Wi-Fi) can load the
# remote-control URL encoded in the title-slide QR code.
#
# Usage: ./serve.sh [PORT]
#   default PORT is 8080

set -euo pipefail

PORT="${1:-8080}"
DIR="$(cd "$(dirname "$0")" && pwd)"

# Pick the first non-loopback IPv4 on a UP interface.
LAN_IP="$(
  ipconfig getifaddr en0 2>/dev/null \
  || ipconfig getifaddr en1 2>/dev/null \
  || ifconfig | awk '/inet / && $2 != "127.0.0.1" { print $2; exit }'
)"

cat <<EOF
================================================================
  Taxonomy TMA · presentation server
================================================================
  Open on this mac       :  http://${LAN_IP:-<lan-ip>}:${PORT}/
  Phone (same Wi-Fi)     :  http://${LAN_IP:-<lan-ip>}:${PORT}/
  Fallback if no LAN IP  :  http://localhost:${PORT}/?lan=${LAN_IP:-<lan-ip>}
  Stop                   :  Ctrl+C
================================================================

IMPORTANT: Open the deck on this mac via the LAN IP above, NOT
localhost. A QR code rendered from a localhost URL is useless —
the phone would try to reach itself. If you're stuck on
localhost, append ?lan=<ip> to force the QR target.

Keyboard fallback always works: arrows, space, F for fullscreen.

EOF

# Try to open the right URL automatically when a LAN IP is known.
if [[ -n "${LAN_IP:-}" ]] && command -v open >/dev/null 2>&1; then
  (sleep 0.8 && open "http://${LAN_IP}:${PORT}/") &
fi

cd "$DIR"
exec python3 -m http.server "$PORT" --bind 0.0.0.0
