"""Take a character from a description to a verified avatar.

    python avatar.py fox --describe "a chibi fox with orange fur and a cream muzzle"
    python avatar.py me --reference ~/photo.jpg --style pastel
    python avatar.py fox --skip-generate        # rebuild sheets already in characters/fox

Runs generate -> screen -> build -> verify, and redraws whichever sheet failed. Stops at
the two atlases; putting <Pavatar /> on a page is left to the agent, which can see where
the project serves static files and where its header lives.

The retry loop is the point. An image model returns an unusable sheet often enough
that generating once and handing over whatever came back makes jumpy avatars, and both
failures it catches -- a body redrawn in every cell, and two sheets drawn at different
sizes -- are invisible in a thumbnail.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build  # noqa: E402
import screen  # noqa: E402
import verify  # noqa: E402
from key import key_file  # noqa: E402
from prompts import STYLES  # noqa: E402


def check(path, sheet_name):
    """None when the sheet is usable, else what is wrong with it. Keys out a flat key
    colour on the way, so a hand-drawn sheet on green just works."""
    report = screen.screen(path, check_spread=sheet_name == 'directions')
    if report['alpha'] == 'key':
        print(f'  {sheet_name}: {key_file(path, in_place=True)}')
        report = screen.screen(path, check_spread=sheet_name == 'directions')
    print(f'  {sheet_name}: alpha {report["alpha"]}' +
          (f', shoulder spread {report["spread"] * 100:.1f}%' if report.get('spread') is not None else ''))
    if report['alpha'] == 'checkerboard':
        return ('it has a painted checkerboard instead of transparency: the image tool was not '
                'asked for a transparent background (an option on the call, not words in the prompt)')
    if report['alpha'] != 'ok':
        return 'it has an opaque background, which cannot be removed'
    if sheet_name == 'directions' and (report.get('spread') is None or report['spread'] > screen.SPREAD_LIMIT):
        return 'the body is a different size in different cells'
    return None


def problem_with(report):
    if report['jump'] > verify.JUMP_LIMIT:
        return f'the body moves {report["jump"]:.1f}px between cells, so the avatar would visibly jump'
    if report['width'] > verify.WIDTH_LIMIT:
        return f'the shoulders change width by {report["width"] * 100:.0f}% between the sheets'
    return (f'the expressions sheet only matches the colours {report["palette"] * 100:.0f}%, so the '
            f'character would look different when clicked')


def main():
    root = os.environ.get('PRETTY_AVATAR_ROOT', os.getcwd())
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('name')
    parser.add_argument('--describe', default='')
    parser.add_argument('--preset', help='Generation preset id from catalog.py --list')
    parser.add_argument('--reference', help='a photo or drawing to redraw')
    parser.add_argument('--style', default='colour', choices=sorted(STYLES))
    parser.add_argument('--only', choices=['directions', 'reactions'],
                        help='on the first pass, redraw just this sheet')
    parser.add_argument('--key', choices=['green', 'magenta'],
                        help='draw on a key colour from the start, for a model without alpha')
    parser.add_argument('--skip-generate', action='store_true', help='use the sheets already on disk')
    parser.add_argument('--src', default=os.path.join(root, 'characters'))
    parser.add_argument('--dest', default=os.path.join(root, 'public', 'avatars'))
    parser.add_argument('--retries', type=int, default=2)
    args = parser.parse_args()

    if args.preset:
        from catalog import preset
        try:
            selected = preset(args.preset)
        except ValueError as error:
            parser.error(str(error))
        args.describe = selected['description'] + ('. Additional details: ' + args.describe if args.describe else '')

    if not args.skip_generate and not args.describe and not args.reference:
        sys.exit('Give --describe or --reference, or --skip-generate to rebuild existing sheets.')

    folder = os.path.join(args.src, args.name)
    only = args.only
    for attempt in range(args.retries + 1):
        last = args.skip_generate or attempt == args.retries
        if not args.skip_generate:
            import generate
            print(f'drawing {args.name}' + (f' (attempt {attempt + 1})' if attempt else ''))
            generate.generate(args.name, args.describe, args.reference, args.style, only, args.key, args.src)

        print('screening')
        fault = check(os.path.join(folder, 'directions.png'), 'directions')
        if fault:
            if last:
                sys.exit(f'{args.name}: the DIRECTIONS sheet is unusable -- {fault}. Redraw it.')
            print(f'  -> {fault}; redrawing both sheets')
            only = None
            continue
        fault = check(os.path.join(folder, 'reactions.png'), 'reactions')
        if fault:
            if last:
                sys.exit(f'{args.name}: the EXPRESSIONS sheet is unusable -- {fault}. Redraw it.')
            print(f'  -> {fault}; redrawing the expressions sheet')
            only = 'reactions'
            continue

        print('building')
        build.build(args.name, args.src, args.dest)
        report = verify.measure(args.name, args.dest)
        print(verify.describe(report))
        if report['ok']:
            print(f'\n{args.name} is ready:')
            print(f'  {os.path.join(args.dest, args.name)}-directions.webp')
            print(f'  {os.path.join(args.dest, args.name)}-reactions.webp')
            print(f'Next: put <Pavatar name="{args.name}" /> on the page (SKILL.md, "Put it on the page").')
            return

        fault = problem_with(report)
        if last:
            sys.exit(f'{args.name}: {fault}. The expressions sheet is usually the one at fault: redraw '
                     f'it (--only reactions), or describe hair that does not cover the shoulders.')
        print(f'  -> {fault}; redrawing the expressions sheet')
        only = 'reactions'


if __name__ == '__main__':
    main()
