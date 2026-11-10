---
name: reel-write
description: "Writing a short vertical AI video (a reel, 8-15 s, 9:16) for Google Flow's Omni or Veo models, or any text-to-video model: pick the form (talk, natural, octane), fill its template, check it, price it, ask. Use for 'write a reel', 'make a video prompt', 'remake this reel', 'action reel', 'chase scene'."
---

# Reel: writing the prompt

One scene, one generation, nothing stitched. The prompt is the whole production: cast, camera, cuts, lines and sound.
Everything here was measured on Google Flow (Omni 1.1 and 1.2 Flash, 2025-2026) by rendering, measuring and judging
blind. A model update can move any of it: when a rule stops holding, test it and fix this file.

## 0 · Before writing

- Save the brief in `work/<date>-<slug>/brief.md`: what the reel is for, where it goes, the one feeling it leaves.
- Remaking someone's reel: write a shot table of the source (time, framing, what happens, the line), then a two-column
  **delta**: what you keep (beats, escalation, the shape of the ending) and what you change (place, people, every
  object, every line). A remake that keeps the words is a copy.
- Price it before shooting and ask the owner (credits cost money). Read the live price from the tool, never from here.

## 1 · Pick the form

| form | use it for | template |
|---|---|---|
| **talk** | drama, a confrontation, a reveal; lines carry it | `templates/talk-10s.txt` |
| **natural** | "looks real", phone footage, family scenes | `templates/natural-15s.txt` |
| **octane** | chases, runs, stunts, vehicles, things bursting | `templates/octane-15s.txt` |

Fist fights read badly on these models (a punch renders as a fist placed and held). For action, write **displacement**:
bodies thrown, carts overturned, crates bursting, a bike airborne. That is what renders.

## 2 · Rules that hold on every form

- **Plain natural language beats JSON**, except the talk form, where a JSON with each line bound to its cut is the
  steadiest (see the template).
- **One face per shot that speaks.** A line binds to the mouth alone on screen; in a two-shot it can come out of the
  wrong mouth. Silent shots may hold everyone.
- **Never put character names in the prompt.** A name gets printed on a badge, an apron or a sign. Describe people by
  age, build and one garment ("the man in the grey suit"). Names live only in your caption.
- **No text anywhere.** Models render lettering as garbage. Every reveal is an object or an arrival, never a word.
  Every garment that could carry a print says it carries none.
- **Timecode the shots** (`Shot 3 | 4-6s:`). The model follows the times almost to the second. Without times the
  action finishes in five seconds and the rest is dead air. Shots of 1.7-3.4 s; under 1.5 s reads as a trailer montage.
- **Open mid-action, no establishing shot.** The first frame is already running. It is the single largest motion lever.
- **Say how many cuts, or say "one continuous shot, no cuts".** The model cuts by default.
- **Sound is one paragraph: the dialogue, then the natural sounds** (footsteps, fabric, the door, rain). Sound words
  elsewhere in the prompt do nothing. End with: no music, no subtitles, no on-screen text.
- **Lines:** short, no apostrophes on Omni. Leave a beat between lines and keep the last line alone; the limit is
  spacing, not word count (about 2.5 words a second).
- **Men's voices:** write "a dry, low man's voice". A loud, beaming man's line often comes back in a woman's voice.
- **Adults only in harm's way.** A child in danger is refused; recast the part as an adult. Never upload a photo of a
  child to any model.
- **Words that fail silently:** "blood" (even in a negative list), a gold watch, anything implying fame ("the famous",
  "prominent"), a line that opens "She is". Leave them out; `tools/check-prompt.py` flags them.
- **Impact, never injury.** No wounds, weapons or blood. A shove, a grab, a throw to the ground render and pass.

## 3 · Pacing (Omni 1.2 drifts slow)

Omni 1.2 turns sluggish, slow-motion-looking, unless the prompt sets the tempo:

1. A pacing line: "everything happens at full real-time speed, normal 1x playback speed in every shot; fast, crisp,
   urgent movement; every shot starts already in motion and cuts away while still moving."
2. Speed words on every beat: sprints, bursts, slams, whips, in one quick move.
3. Tempo in the sound: rapid pounding footsteps in a fast cadence, fast breathing, rising revs.
4. One through-line: one runner, one goal, one direction. Two parallel threads halve the speed of each.
5. No "slow motion" anywhere unless you want it. In our lab every slow stretch was one the script asked for.
6. End in motion (the last line gasped mid-stride), not on a held standoff.

Check it after rendering: `tools/pace.sh take.mp4` prints movement per second; a second under about 4 is a dead spot.

## 4 · Check, price, ask, shoot

```bash
python3 tools/check-prompt.py work/<dir>/prompt.txt     # 0 BLOCK; read every WARN
```

Then state the cost (takes × price) and ask the owner. Shoot two takes of the same words: one flaw a take is normal
(a printed sign, a face drifting, a merged line). Two failed takes of one prompt → change the prompt; a third roll of
the same words is not a fix. A refusal or an "unusual activity" block: stop and tell the owner.

Then the `reel-check` skill.
