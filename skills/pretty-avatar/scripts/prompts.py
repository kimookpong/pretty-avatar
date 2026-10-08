"""The prompts that draw a character's two sheets. reference/prompts.md is the same text
for people pasting them into a chat UI by hand; keep the two in step.

Three things decide whether a sheet is usable, and every prompt repeats them:
  - a portrait bust (head and shoulders), so nothing is clipped at a cell edge
  - the body drawn once and reused in every cell, so the avatar does not wobble
  - wide margins, so cells do not bleed into each other
"""

STYLES = {
    'colour': ('Cute kawaii sticker illustration: clean confident dark outlines, big shiny eyes '
               'with a white catchlight, rosy cheek blush, and soft warm colours with two or three '
               'tones each -- a lighter muzzle or belly, a gently shaded edge. Friendly, rounded '
               'and full of small charming details. Not photorealistic, no glossy 3D render.'),
    'ink': ('Black pen-and-ink illustration on nothing. Confident varied line weight, shading '
            'only by hatching and stippling, no colour and no grey fills. Big eyes with the '
            'catchlight left blank. Crisp, high contrast, storybook charm.'),
    'pastel': ('Soft pastel kawaii illustration: thin warm-brown outlines, gentle pastel colours, '
               'very light shading, sparkly eyes and a dreamy, cosy feel, like a stationery sticker.'),
    'watercolour': ('Loose watercolour illustration: soft washes that bleed slightly at the edges, '
                    'visible paper texture inside the shapes, a thin pencil outline, and the same '
                    'cute big-headed proportions. Keep every edge of the character clean so the '
                    'background stays empty.'),
    'pixel': ('16-bit pixel art: chunky visible square pixels on a strict grid, a small limited '
              'palette, a one-pixel dark outline, hard-edged dithering and no anti-aliasing at '
              'all. Readable at a small size, like a classic console sprite.'),
    'clay': ('Cute claymation look: soft matte modelling-clay surfaces with subtle fingerprint '
             'texture, rounded chunky forms and gentle soft shadows on the character only. '
             'Toy-like and warm, not glossy.'),
}

KEYS = {
    'green': ((0, 255, 0), 'pure bright green (#00FF00)'),
    'magenta': ((255, 0, 255), 'pure magenta (#FF00FF)'),
}

GRID = """LAYOUT: a 3 by 3 grid of nine equal square cells, {background}. One drawing per cell, centred in it. The same character, at the same size, in every cell.

FRAMING: a portrait bust -- head, neck and the top of the shoulders. No arms, no hands, nothing below the chest. The shoulders are the lowest thing in each cell.

PROPORTIONS: chibi. A big head, with shoulders about two thirds of the head's width. The body is small but clearly there; never a floating head.

THE BODY IS DRAWN ONCE: the neck, chest and shoulders are the exact same shape, size and position in all nine cells and always face the viewer. Only the head moves.

MARGINS: every drawing sits wholly inside its cell, about 75% of the cell tall, with clear empty space on all four sides and below the shoulders. Nothing touches or crosses a cell edge. If it does not fit, draw everything smaller -- equally in every cell."""

DIRECTIONS_ORDER = """Row 1: looking up-left, up, up-right.
Row 2: looking left, straight at the viewer, right.
Row 3: looking down-left, down, down-right.
Turn the whole head, not only the eyes: looking left moves the face and nose to the left and shows more of the right side of the head. "Left" means the viewer's left."""

EXPRESSIONS = """1. Eyes closed as happy upward arcs (^ ^). Gentle smile.
2. Same closed arcs, and one small red heart floating beside the head.
3. Same closed arcs, and three small yellow four-point sparkles around the head.
4. Surprised: eyes wide and round, mouth a small round "o".
5. Starstruck: both eyes are yellow stars, big open smile.
6. Bashful: eyes closed, strong pink blush with little lines, tiny smile.
7. Sleepy: eyes closed as relaxed downward curves, small blue "z z z" floating above.
8. Dizzy: both eyes are spirals, wobbly wavy mouth.
9. Delighted: eyes closed arcs, mouth wide open in a big happy grin."""


def background(key):
    if key:
        return f'on one flat {KEYS[key][1]} background that fills the whole image'
    return 'on a fully transparent background'


def ending(key):
    if key:
        # Never mention transparency on this route: a model that cannot give alpha answers
        # the word by painting a grey checkerboard, which cannot be removed.
        return (f'The background is one flat, even {KEYS[key][1]} from edge to edge, with no '
                'gradient, pattern, shadow or grid lines. No text, no labels, no borders.')
    return 'No background, no text, no labels, no borders, no grid lines, no drop shadows.'


def directions(describe, style='colour', key=None):
    return f"""A 3x3 sprite sheet of {describe}. {STYLES[style]}

This sheet shows NINE HEAD DIRECTIONS. The face keeps the same calm, friendly expression in every cell; only the way the head is turned changes.

{GRID.format(background=background(key))}

{DIRECTIONS_ORDER}

No hearts, sparkles, letters or other floating symbols.
{ending(key)}"""


def reactions(describe, style='colour', key=None):
    same = f' The character is {describe}.' if describe else ''
    look = f' Keep the attached sheet\'s {style} style exactly.' if style != 'colour' else ''
    on = f' Draw it on the same flat {KEYS[key][1]} background as described below.' if key else ''
    return f"""The attached image is a 3x3 sheet of one character's head directions. Draw the MATCHING EXPRESSIONS sheet for exactly the same character.{same}{look}{on}

Copy the character exactly: the same colours, markings, outfit, line weight and proportions. Do not restyle or simplify it.

Every cell faces straight at the viewer. Only the face changes, plus a small floating symbol in three cells.

MATCH THE ATTACHED SHEET'S SIZE AND POSITION: the chest and shoulders are the same drawing, the same width and the same distance from the bottom of the cell as in the attached sheet, in all nine cells. If they do not line up the avatar visibly jumps when clicked.

{GRID.format(background=background(key))}

Symbols stay inside the cell too, clear of every edge.

The nine expressions, left to right, top to bottom:
{EXPRESSIONS}

{ending(key)}"""


def from_photo(describe, style='colour', key=None):
    extra = f' They are {describe}.' if describe else ''
    return f"""The attached image shows a person or character. Redraw them as a 3x3 sprite sheet of NINE HEAD DIRECTIONS, as a cute chibi cartoon -- not a portrait.

Throw away the photo's realism, lighting and proportions. Use a big head, very large friendly eyes, a simple nose and mouth and soft blush. Keep only what makes them recognisable: hair shape and colour, facial hair, glasses, skin tone, and the colour of their top.{extra} {STYLES[style]}

The face keeps the same calm, friendly expression in every cell; only the way the head is turned changes.

{GRID.format(background=background(key))}

{DIRECTIONS_ORDER}

No hearts, sparkles, letters or other floating symbols.
{ending(key)}"""
