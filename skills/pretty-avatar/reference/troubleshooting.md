# Troubleshooting

What each check measures, what its failure looks like on the page, and what to do.

## The checks

**Shoulder spread** (`screen.py`, directions sheet). How much the shoulders change width
between the nine cells. The body is supposed to be drawn once and reused while only the
head turns. Over 8% means the model redrew the body in every cell -- usually turning it
along with the head -- and the avatar will wobble as it follows the cursor. Position is
not counted: where each drawing sits in its cell is exactly what `build.py` corrects.
Width is not corrected, because one scale is used for the whole sheet so the head never
changes size as it turns. *Fix:* redraw the directions sheet.

**Jump** (`verify.py`). How far the chest and shoulders move, in rendered px at 140px,
when one cell replaces another -- within a sheet as the head turns, and between sheets
when it is clicked. Over 2px reads as a jolt. *Fix:* usually the expressions sheet is
redrawn at a different place or angle; redraw it (`--only reactions`).

**Palette** (`verify.py`). How much of each expression's colour matches the resting face.
Below 25% the expressions sheet is a different drawing -- other colours, lost markings --
and the character changes when clicked. The samples score above 90%; an AI-drawn pair
usually lands between 40% and 85%. *Fix:* redraw the expressions sheet, and say the
colours and markings again in the description.

**Width** (`verify.py`). How much the shoulders change width between the two sheets
after `build.py` has matched their scale. Over 10% the body swells or shrinks on click.
*Fix:* the shoulders are hidden (by hair, a scarf) so there is nothing to match on --
describe the character with the shoulders visible.

## Alignment, briefly

`build.py` cuts each sheet into nine cells and cleans them: noise is cleared, and any
shape touching a cell edge that is not the character itself is removed -- that is a
sliver of the next cell bleeding in. The character is the largest shape; floating hearts
and zzz are kept because they do not touch an edge.

Each cell is then placed so that the middle of the bottom of the shoulders lands at the
same point of the tile. The directions sheet gets one scale, sized so the tallest cell
fits with room above for floating symbols. The expressions sheet gets its own scale,
started from the ratio of shoulder widths and refined by searching for the scale at which
its chest and shoulders cover the directions sheet's best -- image models redraw the
second sheet a few percent larger or smaller almost every time.

## Problems the checks cannot see

**Mirrored head turns.** The left cell must face the viewer's left. A sheet sometimes
comes back mirrored and passes every check while looking away from the cursor. Swap the
first and last columns of the source sheet and rebuild:

```bash
python3 - characters/<name>/directions.png <<'PY'
import sys; from PIL import Image
path = sys.argv[1]; im = Image.open(path); w, h = im.size; c = w // 3
left, right = im.crop((0, 0, c, h)), im.crop((w - c, 0, w, h))
im.paste(right, (0, 0)); im.paste(left, (w - c, 0)); im.save(path)
PY
python3 <skill-dir>/scripts/avatar.py <name> --skip-generate
```

**Expressions in the wrong cells.** The component expects the order in
`reference/prompts.md`: blink, heart, sparkle, surprised, starstruck, bashful, sleepy,
dizzy, grin. A model sometimes swaps two. Redraw, or reorder the cells by hand.

**The character is cropped at the top.** A tall hat or ears that reach the cell edge are
kept, but anything touching the edge is cut flat. Ask for the character smaller in the
cell ("about 65% of the cell tall").

**A white halo on a dark page.** The sheet was drawn on white and keyed. White cannot be
keyed cleanly; redraw with the transparent option or the green key prompt.
