"""List generation presets or print one description; no image calls or dependencies."""
import argparse
import json
from pathlib import Path

CATALOG = Path(__file__).resolve().parent.parent / 'reference' / 'catalog.json'

def entries():
    return json.loads(CATALOG.read_text(encoding='utf-8'))

def preset(identifier):
    for item in entries():
        if item['id'] == identifier:
            return item
    raise ValueError(f'Unknown preset: {identifier}. Run catalog.py --list.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('id', nargs='?')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--category', choices=['animal', 'human'])
    args = parser.parse_args()
    if args.list:
        for item in entries():
            if not args.category or item['category'] == args.category:
                print(f"{item['id']}: {item['label_th']}")
    elif args.id:
        try:
            print(preset(args.id)['description'])
        except ValueError as error:
            parser.error(str(error))
    else:
        parser.error('Choose an id or --list')
