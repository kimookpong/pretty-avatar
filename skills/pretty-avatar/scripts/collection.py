"""Prepare prompts and track/build the 60-preset collection without calling an image API.

    python collection.py prepare
    python collection.py status
    python collection.py build --id animal-tiger

Source sheets live in characters/<preset-id>/. Manifest and prompts live in
characters/collection/. Only validated atlases are copied into public/avatars/.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import shutil
import time

import catalog
import prompts


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    fd, staging = tempfile.mkstemp(dir=path.parent, suffix='.json')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(data)
        os.chmod(staging, 0o644)
        os.replace(staging, path)
    finally:
        if os.path.exists(staging):
            os.remove(staging)


def prepare(root):
    folder = root / 'characters' / 'collection'
    manifest_path = folder / 'manifest.json'
    previous = {}
    if manifest_path.exists():
        previous = {row['id']: row for row in json.loads(manifest_path.read_text())['characters']}
    records = []
    for item in catalog.entries():
        source = root / 'characters' / item['id']
        source.mkdir(parents=True, exist_ok=True)
        for kind, render in [('directions', prompts.directions), ('reactions', prompts.reactions)]:
            (source / f'{kind}-prompt.txt').write_text(render(item['description']) + '\n', encoding='utf-8')
        row = {**item, 'style': 'colour', 'status': 'pending', 'visual_review': False}
        row.update({k: v for k, v in previous.get(item['id'], {}).items()
                    if k in ['status', 'visual_review', 'report', 'problem', 'source_hashes']})
        records.append(row)
    manifest = {'version': 1, 'characters': records}
    write_json(manifest_path, manifest)
    return manifest



def save_record(path, row):
    """Merge this character's result without losing another build's progress."""
    lock = path.with_suffix('.lock')
    deadline = time.monotonic() + 10
    while True:
        try:
            lock.mkdir()
            break
        except FileExistsError:
            if time.monotonic() > deadline:
                raise RuntimeError(f'Manifest is locked: {lock}')
            time.sleep(0.05)
    try:
        latest = json.loads(path.read_text(encoding='utf-8'))
        latest['characters'] = [row if item['id'] == row['id'] else item for item in latest['characters']]
        write_json(path, latest)
    finally:
        lock.rmdir()


def build_one(root, row, visual_reviewed=False):
    import build
    import screen
    import verify
    source = root / 'characters' / row['id']
    hashes = {kind: hashlib.sha256((source / f'{kind}.png').read_bytes()).hexdigest()
              for kind in ['directions', 'reactions']}
    row['visual_review'] = visual_reviewed or (bool(row.get('visual_review')) and row.get('source_hashes') == hashes)
    row['source_hashes'] = hashes
    for kind in ['directions', 'reactions']:
        result = screen.screen(str(source / f'{kind}.png'), check_spread=kind == 'directions')
        if result['alpha'] != 'ok':
            raise ValueError(f'{kind}: expected genuine alpha, got {result["alpha"]}')
        if kind == 'directions' and (result.get('spread') is None or result['spread'] > screen.SPREAD_LIMIT):
            raise ValueError(f'{kind}: shoulder spread {result.get("spread")} exceeds {screen.SPREAD_LIMIT}')
    # A failed verification must never overwrite the public version.
    destination = root / 'public' / 'avatars'
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='pretty-avatar-') as stage:
        build.build(row['id'], str(root / 'characters'), stage)
        report = verify.measure(row['id'], stage)
        row['report'] = report
        if not report['ok']:
            raise ValueError(verify.describe(report))
        for kind in ['directions', 'reactions']:
            target = destination / f'{row["id"]}-{kind}.webp'
            fd, temp = tempfile.mkstemp(dir=destination, suffix='.webp')
            os.close(fd)
            try:
                shutil.copyfile(Path(stage) / target.name, temp)
                os.chmod(temp, 0o644)
                os.replace(temp, target)
            finally:
                if os.path.exists(temp):
                    os.remove(temp)
    row['status'] = 'verified' if row.get('visual_review') else 'needs-visual-review'
    row.pop('problem', None)
    write_json(destination / f'{row["id"]}.json', row)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'status', 'build'])
    parser.add_argument('--root', type=Path, default=Path(os.environ.get('PRETTY_AVATAR_ROOT', os.getcwd())))
    parser.add_argument('--id', help='One preset id; omit to build all available sources')
    parser.add_argument('--visual-reviewed', action='store_true', help='Record completed human/agent visual inspection')
    args = parser.parse_args()
    if args.visual_reviewed and not args.id:
        parser.error('--visual-reviewed requires --id for an individually inspected character')
    if args.id:
        try:
            catalog.preset(args.id)
        except ValueError as error:
            parser.error(str(error))
    path = args.root / 'characters' / 'collection' / 'manifest.json'
    if args.command == 'prepare' or not path.exists():
        manifest = prepare(args.root)
    else:
        manifest = json.loads(path.read_text(encoding='utf-8'))
    failed = False
    if args.command == 'build':
        for row in manifest['characters']:
            if args.id and row['id'] != args.id:
                continue
            source = args.root / 'characters' / row['id']
            if not all((source / f'{kind}.png').exists() for kind in ['directions', 'reactions']):
                if args.id:
                    row['problem'] = 'Both source sheets are required'
                    failed = True
                continue
            try:
                build_one(args.root, row, visual_reviewed=args.visual_reviewed)
            except (ValueError, FileNotFoundError) as error:
                row['status'] = 'failed'
                row['problem'] = str(error)
                failed = True
            save_record(path, row)
            print(f"{row['id']}: {row['status']}" + (f" — {row['problem']}" if row.get('problem') else ''))
        manifest = json.loads(path.read_text(encoding='utf-8'))
    counts = {}
    for row in manifest['characters']:
        counts[row['status']] = counts.get(row['status'], 0) + 1
    print(json.dumps(counts, ensure_ascii=False))
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
