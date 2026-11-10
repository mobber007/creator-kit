---
name: numbers
description: "Reading the business numbers: views, reach, RPM, earnings, sponsorship rates, from platform exports (CSV). Use for 'why did RPM drop', 'which posts earn', 'what should I post more of', 'how did this month go'."
---

# Numbers

Every figure you report names the export it came from and the dates it covers. Exports go in `numbers/` as
downloaded, never edited; derived tables go beside them with the command that made them.

## Rules that cost us a wrong answer

- **A rate that moves is usually a mix that moved.** Before saying "we are paid less", split the change with
  `tools/rate-split.py`: how much came from *which posts got the views* (mix) and how much from *what each kind earns*
  (rate). Group by post, or bucket posts by kind. Grouping by something coarse (a whole site, a whole account)
  hides the mix inside it and calls everything "rate".
  Example from our own sites: RPM halved in a week; every ordinary post earned *more*, while obituary-style news
  posts (which advertisers avoid) took three quarters of the views at a third of the rate.
- **Hold the story constant.** Before calling something a platform, page or format effect, compare the same post or
  the same story in both places. A "site that pays double" was its stories, not the site.
- **Judge by money a click (or a view), not by RPM alone.** Short posts can top RPM and still earn less a visitor.
- **Data lands late.** Ad revenue arrives one to three days behind, sometimes weeks for estimates. Check the export's
  last complete day; never read a missing day as a zero.
- **Small numbers wobble.** Under a few thousand views a group's rate is noise. Say so instead of ranking it.
- **Check a finding on two random halves** of the posts before acting on it. A pattern that holds on only one half is
  noise.

## The usual reads

```bash
uv run tools/rate-split.py numbers/<export>.csv --date Date --split 2026-11-02 \
  --money "Estimated earnings" --views Views --group Title --bucket 'news=dies|dead|passed away'
```

Then say it in plain words: the rate went from X to Y; this much was mix, this much was rate; the posts behind it;
what is not known yet (late data, small groups). Recommend, don't decide: the owner decides what to post.
