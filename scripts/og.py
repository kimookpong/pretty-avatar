"""Make public/favicon.png and public/og.png from the built sample atlases.

    python3 scripts/og.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AVATARS = os.path.join(ROOT, 'public', 'avatars')
PAPER = '#fbf7f1'
INK = '#2b2220'


def cell(name, kind, index):
    with Image.open(os.path.join(AVATARS, f'{name}-{kind}.webp')) as image:
        image = image.convert('RGBA')
        size = image.width // 3
        row, col = divmod(index, 3)
        return image.crop((col * size, row * size, (col + 1) * size, (row + 1) * size))


def font(size):
    for path in ('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
                 '/System/Library/Fonts/Menlo.ttc'):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def main():
    cell('mochi', 'directions', 4).resize((192, 192), Image.LANCZOS).save(os.path.join(ROOT, 'public', 'favicon.png'))

    og = Image.new('RGBA', (1200, 630), PAPER)
    faces = [('mochi', 'directions', 5), ('kuma', 'reactions', 1), ('usagi', 'directions', 3),
             ('kaeru', 'reactions', 4), ('pan', 'reactions', 8), ('piyo', 'directions', 7)]
    for i, (name, kind, index) in enumerate(faces):
        face = cell(name, kind, index).resize((190, 190), Image.LANCZOS)
        og.alpha_composite(face, (30 + i * 192, 300))
    draw = ImageDraw.Draw(og)
    draw.text((70, 90), '/pretty-avatar', font=font(84), fill=INK)
    draw.text((74, 200), 'follows the cursor. reacts when poked.', font=font(34), fill='#6f625d')
    og.convert('RGB').save(os.path.join(ROOT, 'public', 'og.png'), optimize=True)


if __name__ == '__main__':
    main()
