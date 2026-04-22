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
  Presenter (this mac)  :  http://localhost:${PORT}/
  Phone (same Wi-Fi)    :  http://${LAN_IP:-<lan-ip>}:${PORT}/
  Stop                  :  Ctrl+C
================================================================

The QR code on the title slide encodes the phone URL with a
peer-id query param; scan it from your phone, tap a button,
the slide moves. Keyboard arrows still work as a fallback.

EOF

cd "$DIR"
exec python3 -m http.server "$PORT" --bind 0.0.0.0
