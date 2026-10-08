"""Remove a solid key-colour background (green or magenta) from a sheet.

    python key.py characters/fox/directions.png --in-place
    python key.py sheet.png --out keyed.png

For image tools that cannot return an alpha channel. The sheet is drawn on a flat,
saturated colour that no character uses, and this turns that colour into transparency,
with a soft edge and the colour's spill pulled out of the outline.

White, grey and black are never key colours: the character's own highlights and
outlines would be cut out with them.
"""
import argparse
import sys

import numpy as np
from PIL import Image

# Distance in RGB (0..255 per channel) from the key colour. Below INNER a pixel is pure
# background; above OUTER it is pure character; between the two it is the soft edge.
INNER = 60
OUTER = 140
# A background has to be at least this saturated (max - min channel) to count as a key.
MIN_SATURATION = 140


def border(rgb, width=6):
    return np.concatenate([rgb[:width].reshape(-1, 3), rgb[-width:].reshape(-1, 3),
                           rgb[:, :width].reshape(-1, 3), rgb[:, -width:].reshape(-1, 3)])


def key_colour(rgb):
    """The background colour if the sheet's border is one flat saturated colour."""
    edge = border(rgb)
    colour = np.median(edge, axis=0)
    flat = (np.abs(edge - colour).max(axis=1) < 40).mean()
    if flat < 0.9 or colour.max() - colour.min() < MIN_SATURATION:
        return None
    return colour


def key(rgba):
    """Key out the background of an RGBA uint8 array. Returns (array, colour)."""
    rgb = rgba[..., :3].astype(np.float32)
    colour = key_colour(rgb)
    if colour is None:
        raise ValueError('the background is not one flat saturated colour, so there is nothing '
                         'to key out (white, grey and checkerboard backgrounds cannot be keyed)')

    distance = np.sqrt(((rgb - colour) ** 2).sum(axis=2))
    alpha = np.clip((distance - INNER) / (OUTER - INNER), 0, 1)

    # Spill: the key colour bleeds into the soft edge and tints the outline. In the key
    # colour's strong channels, cap edge pixels at the level of their weakest such
    # channel's partner -- green on a green key is capped at max(red, blue).
    strong = colour > colour.mean()
    weak = ~strong
    if weak.any():
        ceiling = rgb[..., weak].max(axis=2, keepdims=True)
        edge = (alpha < 1)[..., None] & strong[None, None, :]
        rgb = np.where(edge, np.minimum(rgb, ceiling), rgb)

    out = np.dstack([rgb, alpha * 255]).round().clip(0, 255).astype(np.uint8)
    out[alpha == 0] = 0
    return out, colour


def key_file(path, in_place=False, out=None):
    """Key a file. Returns a one-line report, or None when it already had alpha."""
    with Image.open(path) as image:
        rgba = np.asarray(image.convert('RGBA'))
        had_alpha = 'A' in image.mode and (rgba[..., 3] < 10).mean() > 0.05
    if had_alpha:
        return None
    keyed, colour = key(rgba)
    target = path if in_place else (out or path.rsplit('.', 1)[0] + '-keyed.png')
    Image.fromarray(keyed, 'RGBA').save(target)
    hex_colour = '#' + ''.join(f'{round(c):02X}' for c in colour)
    clear = (keyed[..., 3] == 0).mean() * 100
    return f'keyed out {hex_colour} ({clear:.0f}% transparent) -> {target}'


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('path')
    parser.add_argument('--in-place', action='store_true')
    parser.add_argument('--out')
    args = parser.parse_args()
    try:
        report = key_file(args.path, args.in_place, args.out)
    except ValueError as problem:
        sys.exit(f'{args.path}: {problem}')
    print(report or f'{args.path} already has an alpha channel, nothing to key')


if __name__ == '__main__':
    main()
