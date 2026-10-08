"""Shared geometry for the pipeline: cutting a 3x3 sheet into cells, cleaning each cell,
and finding the anchor that every cell is aligned on.

The anchor is the shoulders. The head turns and the face changes, but the body is meant
to be drawn once and reused, so its bottom edge and its width are the most stable thing
in every cell -- and the thing a viewer notices first if it moves when the avatar is
clicked.
"""
from dataclasses import dataclass

import numpy as np
from PIL import Image
from scipy import ndimage

# Alpha at or above this counts as part of the drawing when finding shapes.
SOLID = 64
# Alpha below this is treated as background noise and cleared.
NOISE = 12
# How far up from the bottom of the body the shoulder width is measured, as a fraction
# of the cell. Thin enough to stay below the chin when the head turns down.
SHOULDER_BAND = 0.06


@dataclass
class Anchor:
    centre: float  # x of the middle of the shoulders
    bottom: float  # y of the lowest row of the body
    width: float   # shoulder width
    top: float     # y of the highest row of the body (ears, hair and all)
    left: float
    right: float


def load(path):
    """An RGBA float array, 0..1."""
    with Image.open(path) as image:
        return np.asarray(image.convert('RGBA'), dtype=np.float32) / 255.0


def cells(sheet):
    """The nine cells of a 3x3 sheet, left to right, top to bottom. Works on sheets whose
    size does not divide by three, which image models return as often as not."""
    height, width = sheet.shape[:2]
    rows = [round(i * height / 3) for i in range(4)]
    cols = [round(i * width / 3) for i in range(4)]
    return [sheet[rows[r]:rows[r + 1], cols[c]:cols[c + 1]].copy() for r in range(3) for c in range(3)]


def components(cell):
    labels, count = ndimage.label(cell[..., 3] >= SOLID / 255.0, structure=np.ones((3, 3)))
    sizes = ndimage.sum(np.ones_like(labels), labels, range(1, count + 1)) if count else np.array([])
    return labels, sizes


def clean(cell):
    """Clear background noise and anything that leaked in from a neighbouring cell.

    A character drawn too large spills a sliver into the next cell. That sliver touches
    the cell's edge, while the character itself and its floating symbols (hearts, zzz)
    do not, so every shape touching an edge is dropped -- except the character, which is
    kept even if it touches, so that a slightly cramped drawing is not erased.
    """
    cell = cell.copy()
    cell[cell[..., 3] < NOISE / 255.0] = 0
    labels, sizes = components(cell)
    if not len(sizes):
        return cell
    main = int(np.argmax(sizes)) + 1
    edge = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    for label in edge:
        if label and label != main:
            # Grow the region a little so the soft fringe around it goes too.
            region = ndimage.binary_dilation(labels == label, iterations=2)
            cell[region & (labels != main)] = 0
    return cell


def body(cell):
    """Mask of the character's own shape: the largest connected blob."""
    labels, sizes = components(cell)
    if not len(sizes):
        return np.zeros(cell.shape[:2], dtype=bool)
    return ndimage.binary_fill_holes(labels == int(np.argmax(sizes)) + 1)


def anchor(cell):
    mask = body(cell)
    ys, xs = np.nonzero(mask)
    if not len(ys):
        raise ValueError('a cell is empty')
    bottom = ys.max()
    band = max(2, round(SHOULDER_BAND * cell.shape[0]))
    rows = mask[bottom - band:bottom - band // 2 + 1]
    cols = np.nonzero(rows.any(axis=0))[0]
    return Anchor(centre=(cols.min() + cols.max() + 1) / 2, bottom=float(bottom + 1),
                  width=float(cols.max() - cols.min() + 1), top=float(ys.min()),
                  left=float(xs.min()), right=float(xs.max() + 1))


def lower_band(cell, fraction=0.25):
    """The bottom part of the body -- chest and shoulders -- which must not move between
    any two cells of either sheet."""
    mask = body(cell)
    ys = np.nonzero(mask.any(axis=1))[0]
    if not len(ys):
        return mask
    cut = ys.max() + 1 - max(4, round((ys.max() + 1 - ys.min()) * fraction))
    out = np.zeros_like(mask)
    out[cut:] = mask[cut:]
    return out
