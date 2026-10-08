"""Check a source sheet before building it.

    python screen.py characters/fox/directions.png [--json]

Answers the two questions that decide whether a sheet is worth building:

  alpha   does it have real transparency, and if not, can it be repaired?
          ok           real alpha channel
          key          drawn on a flat key colour; key.py can remove it
          checkerboard a painted grey-and-white checkerboard; redraw
          opaque       flattened onto white or a scene; redraw
  spread  how much the shoulder width changes between the nine cells. The body is meant to be
          drawn once and reused; a high spread means it was redrawn per cell, and no
          alignment can stop a body like that from wobbling.
"""
import argparse
import json
import sys

import numpy as np
from PIL import Image

import sheets
from key import key_colour

# The shoulders may change width this much between cells, as a fraction of the median
# width, before the sheet is called inconsistent.
SPREAD_LIMIT = 0.08


def checker_period(rgb):
    """Square size in px if the sheet's background is a painted grey/white checkerboard.

    Read along lines just inside the sheet's edges, which are background only: a
    character anywhere in the sample would throw off the two grey levels."""
    height, width = rgb.shape[:2]
    if min(height, width) < 64:
        return None
    light = rgb.astype(np.float32).mean(axis=2)
    saturation = rgb.max(axis=2).astype(np.int16) - rgb.min(axis=2)
    lines = [light[y] for y in (2, 6, height - 7, height - 3)] + \
            [light[:, x] for x in (2, 6, width - 7, width - 3)]
    sat = [saturation[y] for y in (2, 6, height - 7, height - 3)] + \
          [saturation[:, x] for x in (2, 6, width - 7, width - 3)]
    if np.median(np.concatenate(sat)) > 20:
        return None
    values = np.concatenate(lines)
    low, high = np.percentile(values, 5), np.percentile(values, 95)
    if not 8 < high - low < 120 or high < 150:
        return None
    periods = []
    for line in lines:
        flips = np.nonzero(np.diff((line > (low + high) / 2).astype(np.int8)))[0]
        runs = np.diff(flips)
        if len(runs) >= 3:
            periods.append(np.median(runs))
    if len(periods) < 4:
        return None
    periods = np.array(periods)
    period = np.median(periods)
    if 4 <= period <= 128 and (np.abs(periods - period) <= 2).mean() >= 0.75:
        return int(round(period))
    return None


def alpha_state(path):
    with Image.open(path) as image:
        has_alpha = 'A' in image.mode or 'transparency' in image.info
        rgba = np.asarray(image.convert('RGBA'))
    if has_alpha and (rgba[..., 3] < 10).mean() > 0.05:
        return 'ok', 'real alpha channel'
    rgb = rgba[..., :3]
    colour = key_colour(rgb.astype(np.float32))
    if colour is not None:
        hex_colour = '#' + ''.join(f'{round(c):02X}' for c in colour)
        return 'key', f'solid {hex_colour} background -- key.py can remove it'
    period = checker_period(rgb)
    if period:
        return 'checkerboard', f'painted checkerboard, {period}px squares -- redraw'
    return 'opaque', 'opaque background -- redraw'


def spread(path):
    """Worst change in shoulder width across the nine cells, as a fraction of the median.

    Position is not counted: where each drawing sits in its cell is what build.py
    corrects. Width is not, because one scale is applied to the whole sheet so the head
    never changes size as it turns."""
    widths = np.array([sheets.anchor(sheets.clean(cell)).width
                       for cell in sheets.cells(sheets.load(path))])
    return float((widths.max() - widths.min()) / np.median(widths))


def screen(path, check_spread=True):
    state, note = alpha_state(path)
    report = {'path': path, 'alpha': state, 'note': note}
    if state == 'ok' and check_spread:
        try:
            report['spread'] = round(spread(path), 4)
        except ValueError as problem:
            report['spread'] = None
            report['note'] = str(problem)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('path')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    report = screen(args.path)
    if args.json:
        print(json.dumps(report))
        return
    print(f'{args.path}')
    print(f'  alpha: {report["alpha"]} ({report["note"]})')
    if report.get('spread') is not None:
        verdict = 'ok' if report['spread'] <= SPREAD_LIMIT else 'TOO HIGH -- body redrawn per cell'
        print(f'  shoulder spread: {report["spread"] * 100:.1f}% ({verdict})')
    if report['alpha'] in ('checkerboard', 'opaque'):
        sys.exit(1)


if __name__ == '__main__':
    main()
