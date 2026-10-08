"""Write reference/prompts.md from prompts.py, so the prompts people paste by hand are
the same ones the API route sends.

    python render_prompts.py           write it
    python render_prompts.py --check   fail if it is out of date
"""
import os
import sys

import prompts

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(os.path.dirname(HERE), 'reference', 'prompts.md')
DESCRIBE = '<DESCRIPTION>'


def block(text):
    return f'```\n{text}\n```'


def render():
    styles = '\n'.join(f'- **{name}** -- {text}' for name, text in prompts.STYLES.items())
    return f"""# Prompts

Generated from `scripts/prompts.py` by `scripts/render_prompts.py` -- edit those, not this.

Replace `{DESCRIBE}` with one sentence naming the colours and two or three features, e.g.
"a chibi fox with warm orange fur, a cream muzzle and dark ear tips". The style paragraph
in each prompt is the default `colour` one; swap in another from *Styles* below, in both
prompts for the same character.

## With transparency

For a tool that can return a transparent background. Turn that option on -- the words
alone will not do it.

### DIRECTIONS

{block(prompts.directions(DESCRIBE))}

### EXPRESSIONS

Attach the directions sheet as a reference image.

{block(prompts.reactions(DESCRIBE))}

### REFERENCE (from a photo)

Attach the photo. Use instead of DIRECTIONS, then EXPRESSIONS as usual.

{block(prompts.from_photo(''))}

## With a key colour

For a tool that cannot return transparency. These never mention it -- asking for
transparency from such a tool gets a painted checkerboard. Remove the green afterwards
with `scripts/key.py`, or let `scripts/avatar.py` do it. If the character is green
itself, replace the green with `pure magenta (#FF00FF)`.

### DIRECTIONS (key colour)

{block(prompts.directions(DESCRIBE, key='green'))}

### EXPRESSIONS (key colour)

{block(prompts.reactions(DESCRIBE, key='green'))}

## Styles

{styles}
"""


if __name__ == '__main__':
    text = render()
    if '--check' in sys.argv:
        with open(TARGET) as handle:
            if handle.read() != text:
                sys.exit('reference/prompts.md is stale. Run: python render_prompts.py')
    else:
        with open(TARGET, 'w') as handle:
            handle.write(text)
