---
name: reel-check
description: "Checking rendered or filmed video before the owner sees it: file sanity, cuts, movement, loudness, a frame strip, pace per second, captions. Use after any render or shoot, for 'check this take', 'which take is best', 'add captions', 'why does it feel slow'."
---

# Reel check

Instruments measure; the owner's eye and ear decide. Never score your own takes as "good": report numbers and defects,
show the frames, and let the owner pick.

## Every take

```bash
tools/reel-check.sh work/<dir>/takes/<take>.mp4      # size, length, fps, audio, cuts, movement, loudness, strip
tools/pace.sh work/<dir>/takes/<take>.mp4            # movement per second: find the dead seconds
tools/contact-sheet.sh work/<dir>/takes/<take>.mp4 4 # four frames a second, for action
```

Then **look at the strip and the sheet** (open the image files). Find, per take:

- **text:** any lettering, sign, subtitle or caption the model painted in
- **drift:** a face on someone else's clothes, a costume change, a duplicated person, a sixth finger
- **the beat:** did the reveal, the leap, the crash actually happen, in the second the prompt gave it?
- **the end:** does it end where the prompt said, or settle into a still group shot?

Rough movement marks from our lab: locked camera ~1.8, handheld ~2.6, opening mid-run ~4.6, a good chase 8-10.
A second under about 4 in an action reel is a dead spot; look at what the prompt asked for there.

## Show the owner

A short table: take · length · cuts · movement · the one defect you saw. Then the sheets and the clips. Say what you
cannot judge from stills: smoothness at full speed, lip-sync, whether a voice fits a face. That is the owner's watch.

## Captions

```bash
uv run tools/captions.py <take>.mp4 --words 7 --prompt "Names, Brand, slang" --burn
```

At most seven words a caption line, split on Whisper's word times, never across a pause. Read every line before
posting: Whisper mishears names and numbers. Fix the `.srt` by hand, then burn again with `--burn`.

## Pictures

```bash
uv run tools/frame.py photo.jpg --ratio 9:16 --mode blur   # stories/reels; 4:5 feed; 1:1 square; 16:9 YouTube
```

Every output is saved without EXIF: no GPS position leaves with the picture.
