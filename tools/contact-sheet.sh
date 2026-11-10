#!/usr/bin/env bash
# contact-sheet.sh <clip.mp4> [fps=4] [columns=10] — one image of frames across the clip, beside it as <name>-sheet.jpg.
#   Four frames a second is enough to judge an action beat; two for talk.
set -euo pipefail
[ "${1:-}" = "-h" ] || [ $# -lt 1 ] && { sed -n 2,3p "$0" | sed 's/^# \{0,1\}//'; [ "${1:-}" = "-h" ]; exit $?; }
C="$1"; FPS="${2:-4}"; COLS="${3:-10}"
[ -f "$C" ] || { echo "contact-sheet: no such file: $C" >&2; exit 2; }
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$C")
ROWS=$(awk "BEGIN {r = int(($DUR * $FPS + $COLS - 1) / $COLS); print (r < 1 ? 1 : r)}")
OUT="${C%.*}-sheet.jpg"
ffmpeg -v error -y -i "$C" -vf "fps=$FPS,scale=130:-2,tile=${COLS}x${ROWS}" -frames:v 1 -q:v 3 "$OUT"
echo "$OUT"
