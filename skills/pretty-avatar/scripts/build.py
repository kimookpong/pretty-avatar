"""Build a character's two source sheets into the two atlases the component reads.

    python build.py fox
    python build.py fox --src characters --dest public/avatars --tile 320

Reads  <src>/<name>/directions.png and reactions.png
Writes <dest>/<name>-directions.webp and <name>-reactions.webp

Every cell is cut out, cleaned, and placed so that the shoulders land in exactly the
same spot. Within a sheet only the position is corrected -- one scale for the whole
sheet, so the head never changes size as it turns. Between the sheets the scale is
matched too, because an image model asked to redraw a character almost always draws it
a little bigger or smaller, and that shows as a jump the moment the avatar is clicked.
"""
import argparse
import os
import sys
import tempfile

import numpy as np
from PIL import Image

import sheets

TILE = 320
# Where the bottom of the body lands, as a fraction of the tile.
BOTTOM = 0.95
# The tallest cell of the directions sheet fills this much of the tile, which leaves
# head-room for floating symbols like hearts and zzz.
FILL = 0.84
# Never let the widest cell come closer than this to the tile's sides.
SIDE_MARGIN = 0.03
# The reactions sheet may be rescaled this far to match the directions sheet. Further
# than that and it is a different drawing, which verify.py will say.
MATCH_RANGE = 0.20
# Bottom edge softening: the bust is cut off, and a short fade reads better than a
# hard line. As a fraction of the tile, ending at the bottom of the body.
FADE = 0.06
QUALITY = 90


def premultiply(cell):
    out = cell.copy()
    out[..., :3] *= out[..., 3:4]
    return out


def unpremultiply(cell):
    out = cell.copy()
    alpha = out[..., 3:4]
    out[..., :3] = np.where(alpha > 0, out[..., :3] / np.maximum(alpha, 1e-6), 0)
    return out


def resize(cell, scale):
    """Resample premultiplied, so dark fringes do not appear around soft edges."""
    height, width = cell.shape[:2]
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    channels = [Image.fromarray(channel).resize(size, Image.LANCZOS)
                for channel in np.moveaxis(premultiply(cell), 2, 0)]
    return unpremultiply(np.clip(np.stack([np.asarray(c) for c in channels], axis=2), 0, 1))


def place(cell, anchor, scale, tile):
    """Scale a cell and paste it so its shoulders sit at the tile's anchor point."""
    scaled = resize(cell, scale)
    out = np.zeros((tile, tile, 4), dtype=np.float32)
    x = round(tile / 2 - anchor.centre * scale)
    y = round(tile * BOTTOM - anchor.bottom * scale)
    height, width = scaled.shape[:2]
    top, left = max(0, y), max(0, x)
    bottom, right = min(tile, y + height), min(tile, x + width)
    if bottom > top and right > left:
        out[top:bottom, left:right] = scaled[top - y:bottom - y, left - x:right - x]
    return out


def fade(tile_image):
    tile = tile_image.shape[0]
    end = tile * BOTTOM
    start = end - tile * FADE
    rows = np.arange(tile, dtype=np.float32) + 0.5
    ramp = np.clip((end - rows) / (end - start), 0, 1)
    # Ease, so the fade does not read as a hard gradient band.
    ramp = ramp * ramp * (3 - 2 * ramp)
    out = tile_image.copy()
    out[..., 3] *= ramp[:, None]
    return out


def directions_scale(anchors, tile):
    tallest = max(a.bottom - a.top for a in anchors)
    widest = max(max(a.centre - a.left, a.right - a.centre) for a in anchors)
    return min(tile * FILL / tallest, tile * (0.5 - SIDE_MARGIN) / widest)


def overlap(a, b):
    union = (a | b).sum()
    return (a & b).sum() / union if union else 0.0


def match_scale(directions, reactions, base, tile):
    """Scale for the reactions sheet that makes its chest and shoulders cover the
    directions sheet's best. Starts from the ratio of shoulder widths and searches
    around it, since a shoulder width alone is thrown off by hair or a collar."""
    reference = sheets.lower_band(place(directions[4][0], directions[4][1], base, tile))
    widths = np.median([a.width for _, a in directions]) / np.median([a.width for _, a in reactions])
    guess = base * widths
    low, high = base * (1 - MATCH_RANGE), base * (1 + MATCH_RANGE)
    best, best_score = np.clip(guess, low, high), -1.0
    for scale in np.linspace(guess * 0.92, guess * 1.08, 17):
        if not low <= scale <= high:
            continue
        score = np.mean([overlap(reference, sheets.lower_band(place(cell, anchor, scale, tile)))
                         for cell, anchor in reactions])
        if score > best_score:
            best, best_score = scale, score
    return float(best)


def atlas(tiles, tile):
    out = np.zeros((tile * 3, tile * 3, 4), dtype=np.float32)
    for index, image in enumerate(tiles):
        row, col = divmod(index, 3)
        out[row * tile:(row + 1) * tile, col * tile:(col + 1) * tile] = image
    return Image.fromarray((out * 255).round().clip(0, 255).astype(np.uint8), 'RGBA')


def fit_pair(directions, reactions, base, matched, tile):
    """Keep floating symbols inside tiles while preserving the matched body ratio."""
    factor = 1.0
    for cells, scale in ((directions, base), (reactions, matched)):
        for cell, anchor in cells:
            ys, xs = np.nonzero(cell[..., 3] > 0.01)
            if not len(xs):
                continue
            for extent, space in (
                (anchor.centre - xs.min(), tile * (0.5 - SIDE_MARGIN)),
                (xs.max() + 1 - anchor.centre, tile * (0.5 - SIDE_MARGIN)),
                (anchor.bottom - ys.min(), tile * (BOTTOM - 0.02)),
            ):
                if extent > 0:
                    factor = min(factor, space / (extent * scale))
    return base * factor, matched * factor


def save(image, path):
    """Write next to the target and rename over it, so a page never loads half a file."""
    folder = os.path.dirname(path) or '.'
    os.makedirs(folder, exist_ok=True)
    handle, temp = tempfile.mkstemp(suffix='.webp', dir=folder)
    os.close(handle)
    try:
        image.save(temp, 'WEBP', quality=QUALITY, method=4)
        # mkstemp makes the file private (0600); a web server must be able to read it.
        os.chmod(temp, 0o644)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.remove(temp)


def prepare(path):
    out = []
    for cell in sheets.cells(sheets.load(path)):
        cell = sheets.clean(cell)
        out.append((cell, sheets.anchor(cell)))
    return out


def build(name, src, dest, tile=TILE):
    folder = os.path.join(src, name)
    directions = prepare(os.path.join(folder, 'directions.png'))
    reactions = prepare(os.path.join(folder, 'reactions.png'))

    base = directions_scale([a for _, a in directions], tile)
    matched = match_scale(directions, reactions, base, tile)
    base, matched = fit_pair(directions, reactions, base, matched, tile)

    outputs = {}
    for kind, cells, scale in (('directions', directions, base), ('reactions', reactions, matched)):
        tiles = [fade(place(cell, anchor, scale, tile)) for cell, anchor in cells]
        path = os.path.join(dest, f'{name}-{kind}.webp')
        save(atlas(tiles, tile), path)
        outputs[kind] = path
    return {'outputs': outputs, 'scale': base, 'reactions_scale': matched,
            'scale_ratio': matched / base}


def main():
    root = os.environ.get('PRETTY_AVATAR_ROOT', os.getcwd())
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('name')
    parser.add_argument('--src', default=os.path.join(root, 'characters'))
    parser.add_argument('--dest', default=os.path.join(root, 'public', 'avatars'))
    parser.add_argument('--tile', type=int, default=TILE)
    args = parser.parse_args()
    try:
        result = build(args.name, args.src, args.dest, args.tile)
    except (FileNotFoundError, ValueError) as problem:
        sys.exit(f'{args.name}: {problem}')
    print(f'built {args.name} (reactions rescaled x{result["scale_ratio"]:.3f} to match)')
    for path in result['outputs'].values():
        print(f'  {path}  {os.path.getsize(path) // 1024} KB')


if __name__ == '__main__':
    main()
