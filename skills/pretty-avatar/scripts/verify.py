"""Measure whether a built avatar will hold still when it changes cells.

    python verify.py fox [--dest public/avatars] [--size 140] [--json]

Three numbers, each a failure you cannot see in a thumbnail:

  jump     how far the chest and shoulders move, in rendered px at --size, when any
           cell is swapped for any other. Above ~2px a click visibly shifts the avatar.
  palette  how closely each expression's colours match the resting face. Low means the
           reactions sheet is a different drawing, so the character changes on click.
  width    how much the shoulders change width between the two sheets. A uniform scale
           difference moves nothing but visibly swells or shrinks the body.
"""
import argparse
import json
import os
import sys

import numpy as np
from scipy import signal

import sheets

JUMP_LIMIT = 2.0
PALETTE_LIMIT = 0.25
WIDTH_LIMIT = 0.10
SEARCH = 16


def shift(reference, other):
    """The (dx, dy), within SEARCH px, that best lays `other` over `reference`."""
    height, width = reference.shape
    corr = signal.fftconvolve(reference.astype(np.float32), other[::-1, ::-1].astype(np.float32), mode='full')
    window = corr[height - 1 - SEARCH:height + SEARCH, width - 1 - SEARCH:width + SEARCH]
    # Ties go to the smallest move, so a featureless band does not invent a jump.
    dy, dx = np.indices(window.shape) - SEARCH
    best = np.lexsort(((dx ** 2 + dy ** 2).ravel(), -window.round(3).ravel()))[0]
    return int(dx.ravel()[best]), int(dy.ravel()[best])


def palette(cell):
    """Histogram of the opaque pixels' colours, 4 bits per channel."""
    opaque = cell[..., 3] > 0.8
    rgb = (cell[..., :3][opaque] * 15).round().astype(int)
    hist = np.bincount(rgb[:, 0] * 256 + rgb[:, 1] * 16 + rgb[:, 2], minlength=4096).astype(float)
    return hist / max(hist.sum(), 1)


def measure(name, dest, size=140):
    directions = [sheets.load(os.path.join(dest, f'{name}-directions.webp'))]
    reactions = [sheets.load(os.path.join(dest, f'{name}-reactions.webp'))]
    directions = sheets.cells(directions[0])
    reactions = sheets.cells(reactions[0])
    tile = directions[0].shape[0]
    px = size / tile

    rest = directions[4]
    band = sheets.lower_band(rest)
    jumps = {}
    for kind, group in (('directions', directions), ('reactions', reactions)):
        for index, cell in enumerate(group):
            dx, dy = shift(band, sheets.lower_band(cell))
            jumps[f'{kind}[{index}]'] = float(np.hypot(dx, dy) * px)

    rest_palette = palette(rest)
    matches = {f'reactions[{i}]': float(np.minimum(rest_palette, palette(cell)).sum())
               for i, cell in enumerate(reactions)}

    rest_width = sheets.anchor(rest).width
    widths = {f'reactions[{i}]': abs(sheets.anchor(cell).width - rest_width) / rest_width
              for i, cell in enumerate(reactions)}

    worst_jump = max(jumps, key=jumps.get)
    worst_match = min(matches, key=matches.get)
    worst_width = max(widths, key=widths.get)
    report = {
        'name': name,
        'jump': round(jumps[worst_jump], 2), 'jump_cell': worst_jump,
        'palette': round(matches[worst_match], 3), 'palette_cell': worst_match,
        'width': round(widths[worst_width], 3), 'width_cell': worst_width,
    }
    report['ok'] = (report['jump'] <= JUMP_LIMIT and report['palette'] >= PALETTE_LIMIT
                    and report['width'] <= WIDTH_LIMIT)
    return report


def describe(report):
    lines = [f'{report["name"]}:',
             f'  jump     {report["jump"]:.2f} rendered px (worst {report["jump_cell"]}, limit {JUMP_LIMIT})',
             f'  palette  {report["palette"] * 100:.0f}% match (weakest {report["palette_cell"]}, '
             f'limit {PALETTE_LIMIT * 100:.0f}%)',
             f'  width    {report["width"] * 100:.1f}% change (worst {report["width_cell"]}, '
             f'limit {WIDTH_LIMIT * 100:.0f}%)',
             f'  -> {"ok" if report["ok"] else "FAIL"}']
    return '\n'.join(lines)


def main():
    root = os.environ.get('PRETTY_AVATAR_ROOT', os.getcwd())
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('name')
    parser.add_argument('--dest', default=os.path.join(root, 'public', 'avatars'))
    parser.add_argument('--size', type=int, default=140, help='rendered size in px')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    report = measure(args.name, args.dest, args.size)
    print(json.dumps(report) if args.json else describe(report))
    if not report['ok']:
        sys.exit(1)


if __name__ == '__main__':
    main()
