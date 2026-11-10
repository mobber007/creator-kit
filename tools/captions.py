#!/usr/bin/env python3
"""captions.py — captions from speech: Whisper's word times → short SRT lines, optionally burned into the video.

  captions.py <clip.mp4> [--words 7] [--model small] [--language en] [--prompt "names, slang"] [--burn]
  captions.py --selftest

Writes <clip>.srt (and <clip>-captioned.mp4 with --burn). Lines are split by word times, never by sentence length:
at most --words words, and a new line at every pause over 0.6 s, so a caption never hangs across a silence.
--prompt gives Whisper the spelling of names and slang it would otherwise guess.
Needs faster-whisper (in the kit's environment: uv sync) and ffmpeg; the model downloads once, on first use. Read every caption before posting: Whisper mishears.
"""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

GAP = 0.6


def stamp(t: float) -> str:
    ms = int(round(max(t, 0) * 1000))
    h, ms = divmod(ms, 3_600_000); m, ms = divmod(ms, 60_000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def group(words: list[dict], most: int) -> list[tuple[float, float, str]]:
    """Words ({word,start,end}) → caption lines: at most `most` words, broken at every pause over GAP."""
    lines, cur = [], []
    for w in words:
        if cur and (len(cur) >= most or w["start"] - cur[-1]["end"] > GAP):
            lines.append(cur); cur = []
        cur.append(w)
    if cur: lines.append(cur)
    return [(ln[0]["start"], ln[-1]["end"], " ".join(w["word"].strip() for w in ln)) for ln in lines]


def srt(lines: list[tuple[float, float, str]]) -> str:
    return "".join(f"{i}\n{stamp(a)} --> {stamp(b)}\n{t}\n\n" for i, (a, b, t) in enumerate(lines, 1))


def transcribe(clip: Path, model: str, language: str | None, prompt: str | None) -> list[dict]:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("captions: faster-whisper is missing; run it as `uv run tools/captions.py` after `uv sync`")
    import numpy as np
    # ffmpeg decodes the audio (mono, 16 kHz float), so no Python video library has to agree with faster-whisper's
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(clip), "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, dtype=np.float32)
    if not audio.size: sys.exit(f"captions: no audio in {clip}")
    segments, _ = WhisperModel(model, device="cpu", compute_type="int8").transcribe(
        audio, word_timestamps=True, language=language, initial_prompt=prompt)
    return [{"word": w.word, "start": w.start, "end": w.end} for seg in segments for w in (seg.words or [])]


def burn(clip: Path, subs: Path) -> Path:
    out = clip.with_name(clip.stem + "-captioned.mp4")
    style = "FontName=Arial,FontSize=14,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Alignment=2,MarginV=60"
    path = str(subs).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-vf", f"subtitles='{path}':force_style='{style}'",
                    "-c:a", "copy", str(out)], check=True)
    return out


def selftest() -> int:
    w = lambda t, a, b: {"word": t, "start": a, "end": b}
    words = [w(" one", 0, .3), w(" two", .3, .6), w(" three", .6, .9), w(" four", 2.0, 2.3), w(" five", 2.3, 2.6)]
    got = group(words, 2)
    cases = {
        "breaks at the word limit": got[0][2] == "one two",
        "breaks at a pause": [g[2] for g in got] == ["one two", "three", "four five"],
        "srt times": stamp(3661.5) == "01:01:01,500" and "00:00:02,000 --> 00:00:02,600" in srt(got),
    }
    for name, ok in cases.items(): print(f"{'ok  ' if ok else 'FAIL'} {name}")
    return 0 if all(cases.values()) else 1


def main() -> int:
    if sys.argv[1:] == ["--selftest"]: return selftest()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("clip", type=Path)
    ap.add_argument("--words", type=int, default=7)
    ap.add_argument("--model", default="small", help="tiny, base, small, medium, large-v3 (bigger = slower, better)")
    ap.add_argument("--language", default=None)
    ap.add_argument("--prompt", default=None)
    ap.add_argument("--burn", action="store_true")
    a = ap.parse_args()
    if not a.clip.is_file(): print(f"captions: no such file: {a.clip}", file=sys.stderr); return 2
    if a.words < 1: print("captions: --words must be 1 or more", file=sys.stderr); return 2
    lines = group(transcribe(a.clip, a.model, a.language, a.prompt), a.words)
    subs = a.clip.with_suffix(".srt"); subs.write_text(srt(lines), encoding="utf-8")
    print(f"{subs} ({len(lines)} lines)")
    if a.burn: print(burn(a.clip, subs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
