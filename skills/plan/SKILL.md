---
name: plan
description: "Writing a plan file for a change with more than one step: goal, risk, verify, success criteria, a log, in plans/."
---

# Plan

A plan is one Markdown file in `plans/`, named `YYYY-MM-DD-<slug>.md`. Any agent can read it and pick the work up
where another left it.

## The file

```markdown
---
goal: "<the owner's words>" (<who>, <YYYY-MM-DD>)
risk: low | medium | high
verify: <one command that is green when the work is right>
---
# <title>

- [ ] <a success criterion: what is true once this item is done>
- [ ] Acceptance: <what the owner will see>

## Log
- <YYYY-MM-DD HH:MM> item <n> done <commit> | red: <why> | dead end: <what failed, and why it looked right>
```

## Writing it

- **Success criteria, not steps.** Each item says what will be true, checkable by `verify` or by looking.
- **Small items, one commit each.** A plan past about ten items is two plans.
- **`verify`** is a test, a lint or a check script for what the plan touches, fast enough to run after every item.
  When none exists, the first item writes one. For media work it can be a tool: `tools/reel-check.sh out.mp4`.
- **`risk`:** `high` when it touches money, accounts, secrets or anything public; `medium` when it changes how other
  things behave; `low` otherwise.
- Show the plan to the owner and wait for "go" or "loop", unless they already said so.
