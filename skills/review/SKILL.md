---
name: review
description: "Reviewing a finished plan before it ships, when its risk asks: hostile input, failure paths, secrets, boundaries, the plan's acceptance."
---

# Review

Run in a fresh session (another harness when you can), with the plan file and its diff (`git diff <base>..HEAD`).
Report each finding with `file:line` and an input that breaks it:

- **Hostile input:** empty, huge, whitespace, unicode, a path with `..`, a symlink out of bounds, a filename with
  spaces or quotes.
- **Failure paths:** a dependency down, a nonzero exit, a partial write, a timeout. Is each reported, not swallowed
  or recorded as a success?
- **Secrets and personal data:** never logged, never in an error, never written to a file, a prompt or a commit.
- **Boundaries:** a file outside the allowed folder, another person's data, anything that goes public.
- **The plan's acceptance:** true as written?

The verdict is "ship" or the findings to fix first. Wording is not a finding.
