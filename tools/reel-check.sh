#!/usr/bin/env bash
# reel-check.sh <clip.mp4> — one take's numbers, and a frame strip for the eye.
#   size · length · fps · audio · hard cuts · movement · loudness · strip (<clip dir>/_check/<name>-strip.png)
# Movement = mean inter-frame luma difference (ffmpeg tblend=difference → signalstats YAVG), cut frames left out.
# Rough marks from our lab: locked-off camera ~1.8 · handheld ~2.6 · opening mid-run ~4.6 · a good chase 8-10.
# Instruments measure; the owner's eye and ear decide.
set -euo pipefail
[ "${1:-}" = "-h" ] || [ $# -ne 1 ] && { sed -n 2,6p "$0" | sed 's/^# \{0,1\}//'; [ "${1:-}" = "-h" ]; exit $?; }
C="$1"; [ -f "$C" ] || { echo "reel-check: no such file: $C" >&2; exit 2; }
D="$(cd "$(dirname "$C")" && pwd)"; N="$(basename "${C%.*}")"
probe() { ffprobe -v error "$@" -of csv=p=0 "$C"; }
DUR=$(probe -show_entries format=duration)
echo "== $N"
echo "video:    $(probe -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate | tr ',' ' ') · ${DUR}s"
A=$(probe -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels | tr ',' ' '); echo "audio:    ${A:-none}"
echo -n "cuts at:  "
{ ffmpeg -hide_banner -i "$C" -filter:v "select='gt(scene,0.12)',showinfo" -f null - 2>&1 | grep -o "pts_time:[0-9.]*" || true; } \
  | cut -d: -f2 | awk '{printf "%.2f ", $1; n++} END {printf "(%d)\n", n}'
echo -n "movement: "
ffmpeg -hide_banner -i "$C" -vf "tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-" -f null - 2>/dev/null \
  | grep -o "YAVG=[0-9.]*" | cut -d= -f2 | awk '$1<40 {s+=$1; n++} END {if (n) printf "%.2f\n", s/n; else print "n/a"}'
echo -n "loudness: "
{ ffmpeg -hide_banner -i "$C" -af volumedetect -f null - 2>&1 | grep -o "mean_volume: [-0-9.]* dB" || echo "no audio"; }
mkdir -p "$D/_check"
if awk "BEGIN {exit !($DUR > 12)}"; then FPS=1; ROWS=$(awk "BEGIN {print int(($DUR + 9) / 10)}"); else FPS=2; ROWS=2; fi
ffmpeg -v error -y -i "$C" -vf "fps=$FPS,scale=180:-2,tile=10x$ROWS" -frames:v 1 "$D/_check/$N-strip.png"
echo "strip:    $D/_check/$N-strip.png ($FPS fps)"
