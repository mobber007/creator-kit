---
name: loop
description: "Running a plan to its end, one item per pass: do it, verify, commit, tick, log; stop on red twice or a question."
---

# Loop

## One pass

1. Read the plan whole, and the last few commits (`git log -5`).
2. Take the first unchecked item.
3. Do it: the smallest change that makes it true.
4. Run the plan's `verify`. Green: commit, tick the box with the short hash, add one log line (time from `date`).
5. Red: fix once, verify again. Red twice: log the dead end (what failed, and why you believed it would work), leave
   the box unticked, stop, and ask the owner.

## Rules

- Never edit or delete a test to turn `verify` green. Never stack a fix on a red.
- Anything outward (a post, a send, a purchase, a public push) waits for the owner's word, even inside a loop.
- After the last item: run `review` when `risk` asks for it, then tell the owner what shipped and what did not.
- Headless, any harness: one pass per run (`claude -p`, `codex exec`) until the plan is done or stops.
