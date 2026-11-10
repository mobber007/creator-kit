---
name: post
description: "Getting a finished piece out: caption, hashtags, cover, schedule, and the posting log. Use for 'write the caption', 'get this ready to post', 'plan this week's posts', 'what did we post'."
---

# Post

Posting is outward and permanent: **nothing goes out without the owner's yes on that exact piece**, and a comment or
post once live is final. Prepare everything; the owner presses the button, or says "post it" for this one piece.

## Ready to post means

- the file passed `reel-check` and the owner picked it
- captions read and corrected (`.srt` beside the video)
- a cover frame or picture at the platform's shape (`uv run tools/frame.py`)
- the caption: the first line is the hook (it shows before "more"), then one or two lines, then at most five
  hashtags that a real viewer would search. No claims the piece does not back; disclose paid partnerships
  (#ad or the platform's own label) every time.
- other people in it have agreed to be posted; no minors' faces without their guardian's yes

## The posting log

One line per post in `numbers/posts.tsv`:

```
date	platform	piece	link	caption_first_line	paid	notes
```

The log is what the numbers are joined against later. Fill the link once it is live.

## A week's plan

A table in `plans/<date>-week.md`: day · platform · piece · status (idea, written, shot, checked, ready, posted).
Repeat what the numbers say earns (skill `numbers`), close to the original; one experiment a week, named as one.
