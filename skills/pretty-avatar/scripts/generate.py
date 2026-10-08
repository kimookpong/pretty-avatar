"""Draw a character's two source sheets with the OpenAI Images API.

    python generate.py fox --describe "a chibi fox with orange fur and a cream muzzle"
    python generate.py me --reference ~/photo.jpg
    python generate.py fox --only reactions     # redraw just the expressions sheet

Writes characters/<name>/directions.png and reactions.png. Needs OPENAI_API_KEY and
`pip install openai`. The model is gpt-image-1 unless PRETTY_AVATAR_MODEL says otherwise.

The directions sheet is drawn first. The expressions sheet is then drawn through the
edits endpoint with the directions sheet attached, so the model copies real pixels
instead of re-imagining the character from words -- the two sheets agreeing is what
stops the avatar jumping when it is clicked.
"""
import argparse
import base64
import io
import os
import re
import sys

import numpy as np
from PIL import Image

import prompts
from key import key_file

DEFAULT_MODEL = 'gpt-image-1'


def pick_key(describe):
    """Green, unless the character is green itself."""
    return 'magenta' if re.search(r'green|lime|emerald|olive|mint|frog|leaf', describe or '', re.I) else 'green'


def has_alpha(data):
    image = Image.open(io.BytesIO(data))
    return 'A' in image.mode and (np.asarray(image.convert('RGBA'))[..., 3] < 10).mean() > 0.05


def draw(api, model, prompt, reference=None, transparent=True):
    """One image as PNG bytes. Transparency is an option on the call, not something a
    prompt can ask for: without background='transparent', no wording gives alpha."""
    extra = {'background': 'transparent' if transparent else 'opaque', 'size': '1024x1024'}

    def call(**options):
        if reference:
            with open(reference, 'rb') as handle:
                return api.images.edit(model=model, image=[handle], prompt=prompt, **options)
        return api.images.generate(model=model, prompt=prompt, **options)

    try:
        result = call(**extra)
    except Exception as problem:  # an older or other model may refuse the background option
        if 'background' not in str(problem):
            raise
        print(f'  {model} does not take a background option')
        result = call(size='1024x1024')
    item = result.data[0]
    if getattr(item, 'b64_json', None):
        return base64.b64decode(item.b64_json)
    sys.exit(f'{model} returned a URL rather than image data; use a gpt-image model')


def sheet(api, model, path, prompt_for, describe, reference=None, key=None):
    """Draw one sheet. Tries for real transparency first; when the model gives none,
    redraws on a flat key colour and keys it out. Returns the key used, if any, so the
    second sheet can take the same route."""
    if not key:
        data = draw(api, model, prompt_for(None), reference)
        if has_alpha(data):
            with open(path, 'wb') as handle:
                handle.write(data)
            print(f'  {os.path.basename(path)}  {len(data) // 1024} KB, transparent')
            return None
        key = pick_key(describe)
        print(f'  no alpha came back, redrawing on {key} to key it out')

    data = draw(api, model, prompt_for(key), reference, transparent=False)
    with open(path, 'wb') as handle:
        handle.write(data)
    try:
        report = key_file(path, in_place=True) or 'already transparent'
    except ValueError as problem:
        sys.exit(f'{os.path.basename(path)} cannot be used: {problem}')
    print(f'  {os.path.basename(path)}  {report}')
    return key


def client():
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit('The openai package is missing. Run: pip install openai')
    if not os.environ.get('OPENAI_API_KEY'):
        sys.exit('OPENAI_API_KEY is not set.')
    return OpenAI()


def generate(name, describe='', reference=None, style='colour', only=None, key=None, src=None, api=None):
    folder = os.path.join(src or os.path.join(os.getcwd(), 'characters'), name)
    os.makedirs(folder, exist_ok=True)
    directions = os.path.join(folder, 'directions.png')
    reactions = os.path.join(folder, 'reactions.png')
    api = api or client()
    model = os.environ.get('PRETTY_AVATAR_MODEL', DEFAULT_MODEL)

    if only != 'reactions':
        if reference:
            key = sheet(api, model, directions, lambda k: prompts.from_photo(describe, style, k),
                        describe, os.path.expanduser(reference), key)
        else:
            key = sheet(api, model, directions, lambda k: prompts.directions(describe, style, k),
                        describe, None, key)

    if only != 'directions':
        if not os.path.exists(directions):
            sys.exit(f'{directions} is missing: draw the directions sheet first.')
        # Same route as the first sheet: the two have to end up the same kind of image.
        sheet(api, model, reactions, lambda k: prompts.reactions(describe, style, k), describe, directions, key)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('name')
    parser.add_argument('--describe', default='', help='one sentence: colours and two or three features')
    parser.add_argument('--reference', help='a photo or drawing to redraw')
    parser.add_argument('--style', default='colour', choices=sorted(prompts.STYLES))
    parser.add_argument('--only', choices=['directions', 'reactions'])
    parser.add_argument('--key', choices=sorted(prompts.KEYS),
                        help='skip transparency and draw on this colour, for a model without alpha')
    args = parser.parse_args()
    if not args.describe and not args.reference:
        sys.exit('Give --describe, --reference, or both.')
    root = os.environ.get('PRETTY_AVATAR_ROOT', os.getcwd())
    generate(args.name, args.describe, args.reference, args.style, args.only, args.key,
             os.path.join(root, 'characters'))


if __name__ == '__main__':
    main()
