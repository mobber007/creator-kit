#!/usr/bin/env bash
# pace.sh <clip.mp4> — movement per second, to find the slow spots (cut frames left out).
#   prints: mean <m> | <second 0> <second 1> ...   A second under about 4 in an action reel reads as dead.
set -euo pipefail
[ "${1:-}" = "-h" ] || [ $# -ne 1 ] && { sed -n 2,3p "$0" | sed 's/^# \{0,1\}//'; [ "${1:-}" = "-h" ]; exit $?; }
[ -f "$1" ] || { echo "pace: no such file: $1" >&2; exit 2; }
ffmpeg -hide_banner -i "$1" -vf "tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-" -f null - 2>/dev/null \
 | awk '/pts_time/ {match($0, /pts_time:[0-9.]+/); t = substr($0, RSTART + 9, RLENGTH - 9)}
        /YAVG/ {split($0, a, "="); v = a[2]; s = int(t); if (v < 40) {sum[s] += v; n[s]++; all += v; na++; if (s > last) last = s}}
        END {if (!na) {print "pace: no frames read"; exit 1}
             printf "mean %.2f |", all / na; for (i = 0; i <= last; i++) printf " %4.1f", (n[i] ? sum[i] / n[i] : 0); printf "\n"}'
