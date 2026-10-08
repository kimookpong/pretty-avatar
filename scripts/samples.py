"""Draw the sample cast and build it into public/avatars.

    python3 scripts/samples.py            draw and build every sample
    python3 scripts/samples.py mochi      just one
    python3 scripts/samples.py --jitter   misplace every cell, the way an image model does,
                                          to exercise the alignment (the tests use this)

The samples are drawn in code rather than by an image model, so the demo page and the
tests work without an API key. Their source sheets go to characters/, which is not
committed; the built atlases in public/avatars are.
"""
import argparse
import math
import os
import random
import subprocess
import sys
from dataclasses import dataclass, field

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, 'skills', 'pretty-avatar', 'scripts')

CELL = 342          # three of these make a 1026px sheet, about what an image model returns
SUPER = 3           # drawn this many times larger, then reduced, for smooth edges
LINE = '#3b2a2a'
EYE = '#2b1d1d'
WHITE = '#ffffff'

# Where the face's features move for each head direction: (x, y), -1..1.
TURNS = {
    'up-left': (-1, -1), 'up': (0, -1), 'up-right': (1, -1),
    'left': (-1, 0), 'center': (0, 0), 'right': (1, 0),
    'down-left': (-1, 1), 'down': (0, 1), 'down-right': (1, 1),
}


@dataclass
class Character:
    name: str
    fur: str
    shade: str
    belly: str
    inner: str
    shirt: str
    collar: str
    ears: str                       # cat, bear, bunny, frog, panda, chick
    blush: str = '#ff9fae'
    extras: list = field(default_factory=list)  # whiskers, muzzle, patches, tuft, beak


CAST = [
    Character('mochi', fur='#f6a55a', shade='#e0873a', belly='#fff1df', inner='#ffc7c7',
              shirt='#7ec4cf', collar='#5aa7b4', ears='cat', extras=['whiskers', 'stripes']),
    Character('kuma', fur='#a8754f', shade='#8a5a39', belly='#f4dcc0', inner='#e9b48f',
              shirt='#f2c14e', collar='#d9a530', ears='bear', extras=['muzzle']),
    Character('usagi', fur='#fbf6f3', shade='#e6d9d2', belly='#ffffff', inner='#ffc2d1',
              shirt='#b9a3e3', collar='#9a82cf', ears='bunny', extras=['muzzle']),
    Character('kaeru', fur='#8fd18a', shade='#6cb567', belly='#e6f7c9', inner='#e6f7c9',
              shirt='#f48c8c', collar='#de6b6b', ears='frog', blush='#ff8f9c'),
    Character('pan', fur='#fbfbfb', shade='#e2e2e2', belly='#ffffff', inner='#3a3a3a',
              shirt='#9ad0a0', collar='#76b67e', ears='panda', extras=['patches']),
    Character('piyo', fur='#ffd84d', shade='#f2bd2b', belly='#fff3b8', inner='#ffd84d',
              shirt='#8fb8ef', collar='#6d9be0', ears='chick', extras=['tuft', 'beak']),
]


class Pen:
    """ImageDraw in cell units: 0..1 across the cell, drawn SUPER times larger."""

    def __init__(self):
        self.size = CELL * SUPER
        self.image = Image.new('RGBA', (self.size, self.size), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.line = max(1, round(0.011 * self.size))

    def p(self, x, y):
        return (x * self.size, y * self.size)

    def box(self, cx, cy, rx, ry):
        return [*self.p(cx - rx, cy - ry), *self.p(cx + rx, cy + ry)]

    def ellipse(self, cx, cy, rx, ry, fill, outline=LINE, width=None):
        self.draw.ellipse(self.box(cx, cy, rx, ry), fill=fill, outline=outline,
                          width=self.line if width is None else width)

    def polygon(self, points, fill, outline=LINE):
        pts = [self.p(x, y) for x, y in points]
        self.draw.polygon(pts, fill=fill)
        if outline:
            self.draw.line(pts + [pts[0]], fill=outline, width=self.line, joint='curve')

    def arc(self, cx, cy, rx, ry, start, end, colour=EYE, width=None):
        self.draw.arc(self.box(cx, cy, rx, ry), start, end, fill=colour,
                      width=round((width or 0.014) * self.size))

    def lines(self, points, colour=EYE, width=0.012):
        self.draw.line([self.p(x, y) for x, y in points], fill=colour,
                       width=round(width * self.size), joint='curve')

    def done(self):
        return self.image.resize((CELL, CELL), Image.LANCZOS)


def heart(pen, cx, cy, r, colour='#ff4d6d'):
    pen.ellipse(cx - r * 0.5, cy - r * 0.2, r * 0.55, r * 0.55, colour, outline=None)
    pen.ellipse(cx + r * 0.5, cy - r * 0.2, r * 0.55, r * 0.55, colour, outline=None)
    pen.polygon([(cx - r * 1.02, cy - r * 0.05), (cx + r * 1.02, cy - r * 0.05), (cx, cy + r * 1.05)],
                colour, outline=None)


def star(pen, cx, cy, r, colour='#ffcf33', points=5, inner=0.45, outline=None):
    pts = []
    for i in range(points * 2):
        radius = r if i % 2 == 0 else r * inner
        angle = -math.pi / 2 + i * math.pi / points
        pts.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
    pen.polygon(pts, colour, outline=outline)


def spiral(pen, cx, cy, r):
    pts = []
    for i in range(60):
        t = i / 59
        angle = t * math.pi * 4
        pts.append((cx + math.cos(angle) * r * t, cy + math.sin(angle) * r * t))
    pen.lines(pts, width=0.009)


def zed(pen, x, y, s, colour='#6f8fe8'):
    pen.lines([(x, y), (x + s, y), (x, y + s), (x + s, y + s)], colour=colour, width=0.011)


def body(pen, c):
    """Drawn once and identical in every cell: this is what the pipeline aligns on."""
    pen.draw.pieslice(pen.box(0.5, 0.95, 0.25, 0.25), 180, 360, fill=c.shirt, outline=LINE, width=pen.line)
    pen.draw.rectangle([*pen.p(0.24, 0.86), *pen.p(0.76, 0.96)], fill=(0, 0, 0, 0))
    pen.lines([(0.258, 0.86), (0.742, 0.86)], colour=LINE, width=0.011)
    # The collar overlaps the chin in every direction, so head and body are one shape.
    pen.ellipse(0.5, 0.7, 0.1, 0.04, c.collar)


def ears(pen, c, hx, hy, tx):
    ex = tx * 0.02
    if c.ears == 'cat':
        for side in (-1, 1):
            base = 0.5 + hx + side * 0.16 + ex
            pen.polygon([(base - 0.085, 0.33 + hy), (base + side * 0.03, 0.135 + hy), (base + 0.085, 0.33 + hy)], c.fur)
            pen.polygon([(base - 0.045, 0.3 + hy), (base + side * 0.022, 0.19 + hy), (base + 0.045, 0.3 + hy)],
                        c.inner, outline=None)
    elif c.ears == 'bear':
        for side in (-1, 1):
            pen.ellipse(0.5 + hx + side * 0.205 + ex, 0.26 + hy, 0.072, 0.07, c.fur)
            pen.ellipse(0.5 + hx + side * 0.205 + ex, 0.265 + hy, 0.038, 0.036, c.inner, outline=None)
    elif c.ears == 'panda':
        for side in (-1, 1):
            pen.ellipse(0.5 + hx + side * 0.2 + ex, 0.265 + hy, 0.068, 0.065, '#3a3a3a')
    elif c.ears == 'bunny':
        for side in (-1, 1):
            cx = 0.5 + hx + side * 0.09 + ex * 1.5
            pen.ellipse(cx, 0.19 + hy, 0.055, 0.135, c.fur)
            pen.ellipse(cx, 0.2 + hy, 0.026, 0.1, c.inner, outline=None)
    elif c.ears == 'frog':
        for side in (-1, 1):
            pen.ellipse(0.5 + hx + side * 0.13 + ex, 0.29 + hy, 0.085, 0.08, c.fur)


def head(pen, c, hx, hy):
    pen.ellipse(0.5 + hx, 0.47 + hy, 0.27, 0.235, c.fur)
    if 'stripes' in c.extras:
        for dx in (-0.045, 0, 0.045):
            pen.lines([(0.5 + hx + dx, 0.245 + hy), (0.5 + hx + dx * 1.2, 0.3 + hy)], colour=c.shade, width=0.016)
    if 'tuft' in c.extras:
        pen.lines([(0.5 + hx, 0.24 + hy), (0.49 + hx, 0.18 + hy), (0.52 + hx, 0.16 + hy)], colour=LINE, width=0.012)


def face_base(pen, c, fx, fy):
    if 'patches' in c.extras:
        for side in (-1, 1):
            pen.ellipse(0.5 + fx + side * 0.09, 0.465 + fy, 0.06, 0.07, '#3a3a3a', outline=None)
    if 'muzzle' in c.extras:
        pen.ellipse(0.5 + fx, 0.545 + fy, 0.085, 0.06, c.belly, outline=None)
    if 'whiskers' in c.extras:
        for side in (-1, 1):
            for dy in (-0.012, 0.014):
                x0 = 0.5 + fx + side * 0.17
                pen.lines([(x0, 0.535 + fy + dy), (x0 + side * 0.075, 0.53 + fy + dy * 1.8)], colour=LINE, width=0.006)


def blush(pen, c, fx, fy, strong=False):
    r = 0.045 if strong else 0.036
    for side in (-1, 1):
        pen.ellipse(0.5 + fx + side * 0.155, 0.535 + fy, r, r * 0.62, c.blush, outline=None)
    if strong:
        for side in (-1, 1):
            x = 0.5 + fx + side * 0.155
            for dx in (-0.018, 0, 0.018):
                pen.lines([(x + dx + 0.006, 0.522 + fy), (x + dx - 0.006, 0.548 + fy)], colour='#e86a7f', width=0.005)


def open_eyes(pen, c, fx, fy, size=1.0):
    for side in (-1, 1):
        x = 0.5 + fx + side * 0.09
        dark = '#ffffff' if c.ears == 'panda' else EYE
        colour = EYE if c.ears != 'panda' else '#1d1d1d'
        pen.ellipse(x, 0.47 + fy, 0.03 * size, 0.036 * size, colour, outline=dark if c.ears == 'panda' else None,
                    width=round(0.004 * pen.size))
        pen.ellipse(x - 0.009 * size, 0.457 + fy, 0.011 * size, 0.012 * size, WHITE, outline=None)


def closed_eyes(pen, c, fx, fy, sleepy=False):
    colour = '#f5f5f5' if c.ears == 'panda' else EYE
    for side in (-1, 1):
        x = 0.5 + fx + side * 0.09
        if sleepy:
            pen.arc(x, 0.46 + fy, 0.032, 0.022, 20, 160, colour)
        else:
            pen.arc(x, 0.485 + fy, 0.032, 0.03, 200, 340, colour)


def mouth(pen, c, fx, fy, kind='smile'):
    x, y = 0.5 + fx, 0.545 + fy
    if 'beak' in c.extras and kind in ('smile', 'small'):
        pen.polygon([(x - 0.03, y - 0.012), (x + 0.03, y - 0.012), (x, y + 0.022)], '#ff9b3d')
        return
    if kind == 'smile':
        pen.arc(x - 0.016, y - 0.006, 0.016, 0.014, 10, 170, LINE, width=0.009)
        pen.arc(x + 0.016, y - 0.006, 0.016, 0.014, 10, 170, LINE, width=0.009)
    elif kind == 'o':
        pen.ellipse(x, y + 0.01, 0.022, 0.027, '#7a2e3a')
    elif kind == 'grin':
        pen.draw.pieslice(pen.box(x, y - 0.005, 0.05, 0.05), 0, 180, fill='#7a2e3a', outline=LINE, width=pen.line)
        pen.ellipse(x, y + 0.03, 0.022, 0.012, '#ff8ea0', outline=None)
    elif kind == 'wavy':
        pts = [(x - 0.04 + i * 0.01, y + 0.01 + 0.008 * math.sin(i * 1.6)) for i in range(9)]
        pen.lines(pts, colour=LINE, width=0.008)
    elif kind == 'small':
        pen.arc(x, y - 0.004, 0.018, 0.012, 20, 160, LINE, width=0.008)


def draw_direction(c, direction):
    tx, ty = TURNS[direction]
    hx, hy = tx * 0.03, ty * 0.022       # the head shifts a little
    fx, fy = tx * 0.1, ty * 0.07         # the face shifts a lot, which is what reads as turning
    pen = Pen()
    body(pen, c)
    ears(pen, c, hx, hy, tx)
    head(pen, c, hx, hy)
    face_base(pen, c, fx, fy)
    blush(pen, c, fx, fy)
    open_eyes(pen, c, fx, fy)
    mouth(pen, c, fx, fy)
    return pen.done()


def draw_reaction(c, reaction):
    pen = Pen()
    body(pen, c)
    ears(pen, c, 0, 0, 0)
    head(pen, c, 0, 0)
    face_base(pen, c, 0, 0)
    blush(pen, c, 0, 0, strong=reaction == 'bashful')
    if reaction in ('blink', 'heart', 'sparkle', 'bashful', 'grin'):
        closed_eyes(pen, c, 0, 0)
    elif reaction == 'sleepy':
        closed_eyes(pen, c, 0, 0, sleepy=True)
    elif reaction == 'surprised':
        open_eyes(pen, c, 0, 0, size=1.35)
    elif reaction == 'starstruck':
        for side in (-1, 1):
            star(pen, 0.5 + side * 0.09, 0.47, 0.048, outline=LINE)
    elif reaction == 'dizzy':
        for side in (-1, 1):
            spiral(pen, 0.5 + side * 0.09, 0.47, 0.036)
    mouth(pen, c, 0, 0, {'surprised': 'o', 'starstruck': 'grin', 'grin': 'grin', 'dizzy': 'wavy',
                          'bashful': 'small', 'sleepy': 'small'}.get(reaction, 'smile'))
    if reaction == 'heart':
        heart(pen, 0.79, 0.15, 0.05)
    elif reaction == 'sparkle':
        star(pen, 0.2, 0.17, 0.04, points=4, inner=0.35)
        star(pen, 0.8, 0.13, 0.05, points=4, inner=0.35)
        star(pen, 0.86, 0.3, 0.03, points=4, inner=0.35)
    elif reaction == 'sleepy':
        zed(pen, 0.74, 0.2, 0.035)
        zed(pen, 0.81, 0.12, 0.027)
        zed(pen, 0.865, 0.06, 0.02)
    return pen.done()


DIRECTIONS = ['up-left', 'up', 'up-right', 'left', 'center', 'right', 'down-left', 'down', 'down-right']
REACTIONS = ['blink', 'heart', 'sparkle', 'surprised', 'starstruck', 'bashful', 'sleepy', 'dizzy', 'grin']


def sheet(cells, jitter=None, scale=1.0):
    """Lay nine cells out on a 3x3 sheet. With jitter, every cell is nudged and resized a
    little, the way an image model never quite places a drawing in the same spot."""
    out = Image.new('RGBA', (CELL * 3, CELL * 3), (0, 0, 0, 0))
    for index, cell in enumerate(cells):
        size = CELL
        dx = dy = 0
        if jitter:
            size = round(CELL * scale * jitter.uniform(0.985, 1.015))
            dx, dy = jitter.randint(-8, 8), jitter.randint(-8, 8)
        elif scale != 1.0:
            size = round(CELL * scale)
        cell = cell.resize((size, size), Image.LANCZOS) if size != CELL else cell
        row, col = divmod(index, 3)
        x = col * CELL + (CELL - size) // 2 + dx
        y = row * CELL + (CELL - size) // 2 + dy
        out.alpha_composite(cell, (x, y)) if x >= 0 and y >= 0 else out.paste(cell, (x, y), cell)
    return out


def draw(character, folder, jitter=False):
    os.makedirs(folder, exist_ok=True)
    rng = random.Random(character.name) if jitter else None
    sheet([draw_direction(character, d) for d in DIRECTIONS], rng).save(os.path.join(folder, 'directions.png'))
    # An image model redraws the second sheet a little larger or smaller than the first.
    sheet([draw_reaction(character, r) for r in REACTIONS], rng, scale=1.06 if jitter else 1.0) \
        .save(os.path.join(folder, 'reactions.png'))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('names', nargs='*')
    parser.add_argument('--jitter', action='store_true')
    parser.add_argument('--src', default=os.path.join(ROOT, 'characters'))
    parser.add_argument('--dest', default=os.path.join(ROOT, 'public', 'avatars'))
    parser.add_argument('--no-build', action='store_true')
    args = parser.parse_args()

    cast = [c for c in CAST if not args.names or c.name in args.names]
    for character in cast:
        draw(character, os.path.join(args.src, character.name), args.jitter)
        if args.no_build:
            continue
        for step in (['build.py', character.name, '--src', args.src, '--dest', args.dest],
                     ['verify.py', character.name, '--dest', args.dest]):
            result = subprocess.run([sys.executable, os.path.join(SCRIPTS, step[0]), *step[1:]])
            if result.returncode:
                sys.exit(f'{character.name}: {step[0]} failed')


if __name__ == '__main__':
    main()
