# creator-kit

A small, plain-text way of working for a creator and their AI agent: how to think (one file), what to do (seven
skills), and the tools to check the work (nine short scripts). It runs in any agent that reads `AGENTS.md` and Agent
Skills: Claude Code, Codex, Gemini CLI.

No framework, no server, no database. Every file is short enough to read top to bottom, and you should.

## Install

Open a fresh Claude Code or Codex session on the new machine and give it [`INSTALL.md`](INSTALL.md):

```
Read https://raw.githubusercontent.com/OWNER/creator-kit/master/INSTALL.md and follow it.
```

It installs ffmpeg, Python (through uv), Pillow, faster-whisper and the rest, puts the skills where the agent finds
them, and proves it all works with `tools/doctor.sh --selftest`.

## What is here

| file | what it is |
|---|---|
| [`AGENTS.md`](AGENTS.md) | how the agent works: ask, plan or loop; the floor it never crosses; how it speaks; memory; where files go |
| [`skills/plan`](skills/plan/SKILL.md), [`loop`](skills/loop/SKILL.md), [`review`](skills/review/SKILL.md) | a change in more than one step: write success criteria, run them one at a time, review before shipping |
| [`skills/reel-write`](skills/reel-write/SKILL.md) | writing short AI video prompts (Google Flow's Omni and Veo, or any text-to-video model), with three templates |
| [`skills/reel-check`](skills/reel-check/SKILL.md) | checking a take: cuts, movement, pace per second, frame strips, captions, pictures |
| [`skills/numbers`](skills/numbers/SKILL.md) | reading the business: why a rate moved, which posts earn, what is noise |
| [`skills/post`](skills/post/SKILL.md) | getting a piece out: caption, cover, the posting log, a week's plan |
| [`tools/`](tools) | `reel-check.sh` · `pace.sh` · `contact-sheet.sh` · `check-prompt.py` · `captions.py` · `frame.py` · `rate-split.py` · `doctor.sh` · `scan-private.sh` |

Your own material (`work/`, `numbers/`, `memory/`, `plans/`, `.env`, every video) is git-ignored: it stays on your
machine. Pull updates to the kit with `git pull`; your files are untouched.

## Where the rules come from

Every rule in the reel skills was paid for: rendered, measured with these tools, and judged blind, over a few hundred
takes since September 2026. Models change; when a rule stops holding, test it and fix the file. That is the whole method.

## License

MIT.
