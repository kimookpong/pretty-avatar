"""Collection state and publishing checks; no image generation requests."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'skills' / 'pretty-avatar' / 'scripts'))
sys.path.insert(0, str(REPO / 'scripts'))
import catalog
import collection
import samples


class Collection(unittest.TestCase):
    def test_catalog_has_unique_balanced_presets(self):
        items = catalog.entries()
        self.assertEqual(len({item['id'] for item in items}), 60)
        for category in ['animal', 'human']:
            self.assertEqual(sum(item['category'] == category for item in items), 30)
        with self.assertRaises(ValueError):
            catalog.preset('../missing')

    def test_prepare_preserves_completed_state(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = collection.prepare(root)
            manifest['characters'][0].update(status='verified', visual_review=True, source_hashes={'directions': 'd', 'reactions': 'r'})
            collection.write_json(root / 'characters/collection/manifest.json', manifest)
            resumed = collection.prepare(root)
            self.assertEqual(resumed['characters'][0]['status'], 'verified')
            self.assertTrue(resumed['characters'][0]['visual_review'])
            self.assertEqual(resumed['characters'][0]['source_hashes'], {'directions': 'd', 'reactions': 'r'})
            self.assertEqual(len(list((root / 'characters').glob('*/directions-prompt.txt'))), 60)

    def test_save_record_merges_latest_progress(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = collection.prepare(root)
            path = root / 'characters/collection/manifest.json'
            first, second = [row.copy() for row in manifest['characters'][:2]]
            first['status'] = second['status'] = 'verified'
            collection.save_record(path, first)
            collection.save_record(path, second)
            saved = json.loads(path.read_text())['characters']
            self.assertEqual([row['status'] for row in saved[:2]], ['verified', 'verified'])

    def test_failed_verification_keeps_public_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            row = catalog.preset('animal-bear').copy()
            kuma = next(item for item in samples.CAST if item.name == 'kuma')
            samples.draw(kuma, str(root / 'characters' / row['id']))
            target = root / 'public/avatars' / (row['id'] + '-directions.webp')
            target.parent.mkdir(parents=True)
            target.write_bytes(b'previous published version')
            with patch('verify.measure', return_value={'ok': False}), patch('verify.describe', return_value='failed'):
                with self.assertRaises(ValueError):
                    collection.build_one(root, row)
            self.assertEqual(target.read_bytes(), b'previous published version')
            self.assertFalse(target.with_name(row['id'] + '.json').exists())


if __name__ == '__main__':
    unittest.main()
