# Install creator-kit on this machine

You are an AI agent (Claude Code, Codex or Gemini CLI) setting up a fresh machine for a creator, **the owner**, who
runs their business from it. Follow these steps in order. Run each command yourself; stop only where a step says to.

Rules while you install:

- **Never type a password, and never run `sudo` yourself.** When a step needs one, give the owner the exact command
  to paste into their own terminal, then wait until they say it is done.
- Ask before anything that costs money or signs into an account.
- If a step fails twice, stop, show the owner the error, and ask. Do not try workarounds that weaken security.
- At the end, report what is installed, what is not, and why.

## 1 · Find out where you are

```bash
uname -sm; sw_vers 2>/dev/null || cat /etc/os-release 2>/dev/null | head -3
```

- **macOS** (Apple Silicon or Intel): go on.
- **Linux** (Debian or Ubuntu): use the `apt` lines below.
- **Windows:** this kit runs inside WSL (Ubuntu). Ask the owner to install it (`wsl --install` in an
  administrator PowerShell, then restart), open Ubuntu, start a new agent session there, and begin again.

## 2 · System tools

**macOS.** Check for Homebrew: `brew --version`. If it is missing, Homebrew's installer needs the owner's password, so
give them this to paste into Terminal, and wait:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

(It prints two `eval` lines at the end for Apple Silicon; they must run them too.) Then, yourself:

```bash
brew install git ffmpeg jq uv yt-dlp imagemagick exiftool node gh
```

**Linux.** Give the owner this line to paste (it needs their password):

```bash
sudo apt update && sudo apt install -y git ffmpeg jq imagemagick libimage-exiftool-perl nodejs npm curl
```

Then, yourself: `curl -LsSf https://astral.sh/uv/install.sh | sh` (uv, the Python manager), and
`uv tool install yt-dlp`.

Check: `ffmpeg -version | head -1 && uv --version && git --version`.

## 3 · The kit

Clone it where the owner wants their workspace; the default is a folder named `creator` in their home:

```bash
git clone https://github.com/mobber007/creator-kit.git ~/creator
cd ~/creator
uv sync
```

`uv sync` builds the kit's own Python (3.12) with Pillow, NumPy, pandas and faster-whisper, inside `~/creator/.venv`.
It never touches the system Python. Python tools run as `uv run tools/<tool>.py`.

## 4 · Prove it works

```bash
tools/doctor.sh --selftest
```

Every required line must say `ok` and the last line must say `ready`. Optional tools may be missing. Then fetch the
speech model once (about 150 MB), so captions work offline later:

```bash
ffmpeg -v error -f lavfi -i "sine=frequency=300:duration=2" /tmp/ck-tone.wav -y && uv run tools/captions.py /tmp/ck-tone.wav --model base; rm -f /tmp/ck-tone.wav /tmp/ck-tone.srt
```

(A tone has no words: zero caption lines is the right answer.)

## 5 · Make the agent find the rules and skills

Inside `~/creator` they are already wired: `CLAUDE.md` and `GEMINI.md` load `AGENTS.md`, Codex reads `AGENTS.md`
itself, and `.claude/skills` and `.agents/skills` point at `skills/`. So the owner starts their agent **in
`~/creator`**:

```bash
cd ~/creator && claude      # or: codex   or: gemini
```

Check that the skills are seen: ask your own harness to list its skills, or look for `reel-write` in its skill list.

## 6 · Meet the owner

Ask the owner these, one at a time, and write each answer as a memory file (AGENTS.md § Memory, type `user`), with
one line for each in `memory/MEMORY.md`:

1. What do you make, and on which platforms (Instagram, TikTok, YouTube, Facebook, a website)?
2. Where does the money come from (ad revenue, sponsors, affiliate links, products, services)?
3. Which AI video or image tools do you use, if any (Google Flow, Veo, Gemini, others)?
4. What takes you the most time each week?

Then create the folders the owner's work lives in (git-ignored, they stay on this machine):

```bash
mkdir -p work numbers
```

If they use paid APIs, tell them the key goes in `~/creator/.env` as `NAME=value` (the names are in `.env.example`),
typed by them, never pasted into the chat.

## 7 · Report

Tell the owner, in plain words:

- what is installed (the `doctor.sh` output), and anything missing with the reason
- how to start: `cd ~/creator && claude` (or codex)
- three things to try first:
  - "Check this video: `<path>`" (skill `reel-check`)
  - "Write a 15-second chase reel about `<idea>`" (skill `reel-write`)
  - "Here is my YouTube or Instagram export; why did my earnings drop?" (skill `numbers`)
- how to update later: `cd ~/creator && git pull && uv sync`
