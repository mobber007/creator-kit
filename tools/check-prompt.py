#!/usr/bin/env python3
"""check-prompt.py — the gate on a video prompt, before a credit is spent.

  check-prompt.py <prompt.txt|prompt.json>    prints BLOCK and WARN lines; exit 1 on any BLOCK
  check-prompt.py --selftest

BLOCK = a defect a render has already shown us, or one that costs a whole take. WARN = worth a second look.
Every rule is in skills/reel-write/SKILL.md, with why. The check never rules on the story: the owner does.
"""
from __future__ import annotations
import re, sys

BLOCK_RULES = [
    ("blood", r"\bblood\w*|\bbleed\w*|\bwound\w*", "blood or wounds fail silently, even inside a negative list: leave the word out"),
    ("weapon", r"\b(?:guns?|knife|knives|pistols?|rifles?|swords?)\b", "a weapon in the scene is refused; name weapons only in the Avoid line"),
    ("fame", r"\b(?:famous|celebrity|prominent|superstar|world-renowned)\b", "anything implying fame is refused as 'prominent people'"),
    ("gold-watch", r"\bgold watch\b", "a gold watch has drawn refusals"),
    ("she-is", r"""(?:says|:)\s*[{"“]?\s*She is\b""", "a line opening 'She is' failed audio generation"),
    ("child-danger", r"\b(?:child|kid|boy|girl|toddler|\d{1,2}-year-old)\b[^.]{0,80}\b(?:crash|fall|chase|danger|hurt|fight|thrown|run(?:s|ning)? from)\b",
     "a child in harm's way is refused: recast the part as an adult"),
]
WARN_RULES = [
    ("slow-motion", r"\bslow[- ]motion\b", "Omni 1.2 already drifts slow; keep slow motion only if you want it"),
    ("punch", r"\bpunch\w*|\bslap\w*|\bstrik(?:e|es|ing)\b", "blows render as a fist placed and held; write displacement (thrown, slid, burst)"),
    ("text-surface", r"\b(?:sign|menu|poster|badge|name ?tag|jersey|newspaper|screen|logo|banner|billboard)s?\b(?<!on-screen)",
     "a surface that can carry text will print garbage on it: say it carries none, or cut it"),
]
TIMECODE = re.compile(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*s\b")
LINE = re.compile(r"""\{([^}]*)\}|"line"\s*:\s*"([^"]*)\"""")


NEGATIVE = re.compile(r"""^\s*"?(?:avoid|negative)\b.*$|\b(?:no|without|never)\b[^.;\n]*""", re.I | re.M)
ALWAYS = {"blood"}           # these fail even inside a negative list


def check(text: str) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    low = text.lower()
    body = NEGATIVE.sub("", text)        # what the scene asks for, without the lists of what to leave out
    for code, rx, why in BLOCK_RULES:
        m = re.search(rx, text if code in ALWAYS else body, re.I)
        if m: out.append(("BLOCK", code, f"{why} (found: {m.group(0)!r})"))
    for code, rx, why in WARN_RULES:
        m = re.search(rx, body, re.I)
        if m: out.append(("WARN", code, f"{why} (found: {m.group(0)!r})"))
    for m in LINE.finditer(text):
        line = (m.group(1) or m.group(2) or "").strip()
        if "'" in line or "’" in line:
            out.append(("WARN", "apostrophe", f"Omni slurs apostrophes in lines: {line!r}"))
    negatives = " ".join(m.group(0) for m in NEGATIVE.finditer(text)).lower()
    if "music" not in negatives: out.append(("WARN", "music", "say 'no music' in the sound paragraph or the model may score it"))
    if not re.search(r"subtitles|on-screen text", negatives): out.append(("BLOCK", "text", "say 'no subtitles, no on-screen text': models print captions"))
    one_take = re.search(r"one continuous (?:handheld )?shot|no cuts", low)
    spans = [(float(a), float(b)) for a, b in TIMECODE.findall(text)]
    if not spans and not one_take and '"cut"' not in text:
        out.append(("WARN", "timecodes", "no shot times and no 'one continuous shot': the action tends to end early"))
    for a, b in spans:
        if b <= a: out.append(("BLOCK", "time-order", f"shot {a}-{b}s ends before it starts"))
        elif b - a < 1.5 and not one_take: out.append(("WARN", "short-shot", f"shot {a}-{b}s is under 1.5 s: it reads as a montage"))
    for (a1, b1), (a2, _) in zip(spans, spans[1:]):
        if abs(a2 - b1) > 0.01: out.append(("WARN", "time-gap", f"shot ending {b1}s is followed by one starting {a2}s"))
    words = len(text.split())
    if words > 750: out.append(("WARN", "length", f"{words} words; our longest clean renders ran about 650"))
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 1 or argv[0] in ("-h", "--help"):
        print(__doc__.strip()); return 0 if argv[:1] in (["-h"], ["--help"]) else 2
    if argv[0] == "--selftest": return selftest()
    try: text = open(argv[0], encoding="utf-8").read()
    except OSError as e: print(f"check-prompt: {e}", file=sys.stderr); return 2
    found = check(text)
    for level, code, why in found: print(f"{level} {code}: {why}")
    blocks = sum(1 for f in found if f[0] == "BLOCK")
    print(f"{blocks} BLOCK, {len(found) - blocks} WARN")
    return 1 if blocks else 0


def selftest() -> int:
    good = ("Pacing: full real-time speed.\nShot 1 | 0-2s: a woman sprints. Dialogue: none.\n"
            "Shot 2 | 2-4s: she vaults a cart. The runner says: {Still too slow.}\n"
            "Audio: footsteps. No music, no subtitles, no on-screen text.\nAvoid: weapons, logos.")
    cases = {
        "good passes": (good, set()),
        "blood blocks": (good + " Avoid: blood.", {"blood"}),
        "fame blocks": (good.replace("a woman", "a famous singer"), {"fame"}),
        "no text rule blocks": (good.replace("no subtitles, no on-screen text", "quiet"), {"text"}),
        "child in danger blocks": (good.replace("a woman sprints", "a 9-year-old girl runs from a crash"), {"child-danger"}),
        "she-is blocks": (good.replace("{Still too slow.}", "{She is mine.}"), {"she-is"}),
        "backwards time blocks": (good.replace("2-4s", "4-2s"), {"time-order"}),
    }
    bad = 0
    for name, (text, want) in cases.items():
        got = {c for lvl, c, _ in check(text) if lvl == "BLOCK"}
        ok = got == want
        bad += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f": blocks {sorted(got)}, want {sorted(want)}"))
    warns = {c for _, c, _ in check(good.replace("{Still too slow.}", "{Don't stop.}").replace("vaults a cart", "vaults a cart in slow motion"))}
    for w in ("apostrophe", "slow-motion"):
        ok = w in warns; bad += not ok; print(f"{'ok  ' if ok else 'FAIL'} warns {w}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
