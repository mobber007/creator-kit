#!/usr/bin/env bash
# doctor.sh [--selftest] — is this machine ready? Lists each tool the kit needs, found or missing, with its version.
#   --selftest also renders a 4-second test clip and runs every tool on it, and each tool's own selftest.
# Exit 1 when anything required is missing or a selftest fails.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; FAIL=0
[ "${1:-}" = "-h" ] && { sed -n 2,4p "$0" | sed 's/^# \{0,1\}//'; exit 0; }
need() { # need <name> <command that prints a version> [optional]
  if out=$(eval "$2" 2>/dev/null | head -1) && [ -n "$out" ]; then printf "  ok       %-14s %s\n" "$1" "$out"
  elif [ "${3:-}" = optional ]; then printf "  missing  %-14s (optional)\n" "$1"
  else printf "  MISSING  %-14s\n" "$1"; FAIL=1; fi
}
echo "required:"
need git        "git --version"
need python3    "python3 -c 'import sys; print(sys.version.split()[0])'"
need ffmpeg     "ffmpeg -version | sed 's/ Copyright.*//'"
need ffprobe    "ffprobe -version | sed 's/ Copyright.*//'"
need uv         "uv --version"
PY="uv run --project $(dirname "$HERE") python"     # the kit's own environment (pyproject.toml), made by `uv sync`
need pillow     "$PY -c 'import PIL; print(PIL.__version__)'"
need whisper    "$PY -c 'import faster_whisper; print(\"faster-whisper\", faster_whisper.__version__)'"
need pandas     "$PY -c 'import pandas; print(pandas.__version__)'"
need jq         "jq --version"
echo "optional:"
need yt-dlp     "yt-dlp --version" optional
need imagemagick "magick -version" optional
need exiftool   "exiftool -ver" optional
need node       "node --version" optional
need gh         "gh --version" optional
need claude     "claude --version" optional
need codex      "codex --version" optional
if [ "${1:-}" = "--selftest" ]; then
  echo "selftest:"
  T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
  ffmpeg -v error -f lavfi -i "testsrc2=size=360x640:rate=24:duration=4" -f lavfi -i "sine=frequency=440:duration=4" \
    -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest "$T/test.mp4" || { echo "  FAIL could not render a test clip"; exit 1; }
  run() { local n; for a in "$@"; do case "$a" in *.sh|*.py) n=$(basename "$a");; esac; done
    if out=$("$@" 2>&1); then echo "  ok   $n · $(echo "$out" | tail -1)"; else echo "  FAIL $*"; echo "$out" | sed 's/^/       /'; FAIL=1; fi; }
  run bash "$HERE/reel-check.sh" "$T/test.mp4"
  run bash "$HERE/pace.sh" "$T/test.mp4"
  run bash "$HERE/contact-sheet.sh" "$T/test.mp4"
  run $PY "$HERE/check-prompt.py" --selftest
  run $PY "$HERE/captions.py" --selftest
  run $PY "$HERE/frame.py" --selftest
  run $PY "$HERE/rate-split.py" --selftest
fi
[ $FAIL = 0 ] && echo "ready" || echo "not ready: install what is MISSING or fix what FAILed (INSTALL.md)"
exit $FAIL
