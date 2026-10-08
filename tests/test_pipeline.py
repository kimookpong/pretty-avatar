"""End-to-end checks of the pipeline on drawn-in-code characters.

    python3 -m unittest discover -s tests -v
"""
import base64
import io
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(REPO, 'skills', 'pretty-avatar', 'scripts')
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(REPO, 'scripts'))

import build  # noqa: E402
import generate  # noqa: E402
import samples  # noqa: E402
import screen  # noqa: E402
import sheets  # noqa: E402
import verify  # noqa: E402
from key import key  # noqa: E402

KUMA = next(c for c in samples.CAST if c.name == 'kuma')


def on(colour, image):
    """Flatten an RGBA image onto a solid colour, the way a model without alpha draws."""
    out = Image.new('RGBA', image.size, colour)
    out.alpha_composite(image)
    return out.convert('RGB')


def checkerboard(image, square=32):
    yy, xx = np.indices((image.height, image.width))
    board = np.where(((yy // square + xx // square) % 2)[..., None] == 0, 255, 204).repeat(3, axis=2)
    out = Image.fromarray(board.astype(np.uint8)).convert('RGBA')
    out.alpha_composite(image)
    return out.convert('RGB')


class Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.src = os.path.join(cls.tmp, 'characters')
        cls.dest = os.path.join(cls.tmp, 'avatars')
        # Jittered: every cell nudged and resized, the reactions sheet drawn 6% larger.
        samples.draw(KUMA, os.path.join(cls.src, 'kuma'), jitter=True)
        cls.result = build.build('kuma', cls.src, cls.dest, tile=240)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def test_builds_two_square_atlases(self):
        for path in self.result['outputs'].values():
            with Image.open(path) as image:
                self.assertEqual(image.size, (720, 720))
                self.assertEqual(image.mode, 'RGBA')

    def test_atlases_are_world_readable(self):
        for path in self.result['outputs'].values():
            self.assertEqual(os.stat(path).st_mode & 0o777, 0o644)

    def test_undoes_the_size_mismatch_between_sheets(self):
        self.assertAlmostEqual(self.result['scale_ratio'], 1 / 1.06, delta=0.02)

    def test_jittered_sheets_still_hold_still(self):
        report = verify.measure('kuma', self.dest)
        self.assertTrue(report['ok'], verify.describe(report))
        self.assertLess(report['jump'], verify.JUMP_LIMIT)

    def test_screen_passes_a_good_sheet(self):
        report = screen.screen(os.path.join(self.src, 'kuma', 'directions.png'))
        self.assertEqual(report['alpha'], 'ok')
        self.assertLess(report['spread'], screen.SPREAD_LIMIT)

    def test_screen_names_a_checkerboard(self):
        path = os.path.join(self.tmp, 'checker.png')
        with Image.open(os.path.join(self.src, 'kuma', 'directions.png')) as image:
            checkerboard(image.convert('RGBA')).save(path)
        self.assertEqual(screen.screen(path)['alpha'], 'checkerboard')

    def test_screen_names_a_white_background(self):
        path = os.path.join(self.tmp, 'white.png')
        with Image.open(os.path.join(self.src, 'kuma', 'directions.png')) as image:
            on('white', image.convert('RGBA')).save(path)
        self.assertEqual(screen.screen(path)['alpha'], 'opaque')

    def test_keys_out_green_and_keeps_the_character(self):
        with Image.open(os.path.join(self.src, 'kuma', 'directions.png')) as image:
            original = np.asarray(image.convert('RGBA'))
            green = np.asarray(on((0, 255, 0, 255), image.convert('RGBA')).convert('RGBA'))
        keyed, colour = key(green)
        self.assertEqual(list(colour), [0, 255, 0])
        solid = original[..., 3] == 255
        self.assertGreater((keyed[..., 3][solid] == 255).mean(), 0.97)
        self.assertGreater((keyed[..., 3][original[..., 3] == 0] == 0).mean(), 0.99)
        # No green fringe left on the edge pixels.
        edge = (keyed[..., 3] > 0) & (keyed[..., 3] < 255)
        rgb = keyed[..., :3][edge].astype(int)
        self.assertLess((rgb[:, 1] > rgb[:, [0, 2]].max(axis=1) + 30).mean(), 0.02)

    def test_drops_slivers_bleeding_in_from_a_neighbour(self):
        cell = np.zeros((100, 100, 4), dtype=np.float32)
        cell[40:80, 30:70] = 1          # the character
        cell[0:30, 95:100] = 1          # a sliver of the next cell
        cell[10:16, 45:51] = 1          # a floating heart: keep
        cleaned = sheets.clean(cell)
        self.assertEqual(cleaned[0:30, 95:100, 3].max(), 0)
        self.assertEqual(cleaned[10:16, 45:51, 3].min(), 1)
        self.assertEqual(cleaned[40:80, 30:70, 3].min(), 1)


class FakeImages:
    """Stands in for client.images: ignores the prompt and returns a drawn sheet, with or
    without alpha, recording what it was asked for."""

    def __init__(self, alpha):
        self.alpha = alpha
        self.calls = []

    def _respond(self, prompt, reactions, **options):
        self.calls.append({'prompt': prompt, **options})
        draw = samples.draw_reaction if reactions else samples.draw_direction
        cells = [draw(KUMA, n) for n in (samples.REACTIONS if reactions else samples.DIRECTIONS)]
        image = samples.sheet(cells)
        if not (self.alpha and options.get('background') == 'transparent'):
            image = on((0, 255, 0, 255), image) if options.get('background') == 'opaque' else checkerboard(image)
        buffer = io.BytesIO()
        image.save(buffer, 'PNG')
        item = types.SimpleNamespace(b64_json=base64.b64encode(buffer.getvalue()).decode())
        return types.SimpleNamespace(data=[item])

    def generate(self, prompt, model, **options):
        return self._respond(prompt, False, **options)

    def edit(self, image, prompt, model, **options):
        return self._respond(prompt, True, **options)


class Generate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_with(self, alpha):
        images = FakeImages(alpha)
        generate.generate('kuma', describe='a chibi bear', src=self.tmp,
                          api=types.SimpleNamespace(images=images))
        return images

    def test_transparent_route(self):
        images = self.run_with(alpha=True)
        self.assertEqual([c['background'] for c in images.calls], ['transparent', 'transparent'])
        for sheet_name in ('directions', 'reactions'):
            self.assertEqual(screen.screen(os.path.join(self.tmp, 'kuma', f'{sheet_name}.png'))['alpha'], 'ok')

    def test_falls_back_to_a_key_colour_without_alpha(self):
        images = self.run_with(alpha=False)
        # One failed transparent try, then both sheets on green.
        self.assertEqual([c['background'] for c in images.calls], ['transparent', 'opaque', 'opaque'])
        self.assertNotIn('transparen', images.calls[1]['prompt'].lower())
        self.assertIn('#00FF00', images.calls[1]['prompt'])
        for sheet_name in ('directions', 'reactions'):
            self.assertEqual(screen.screen(os.path.join(self.tmp, 'kuma', f'{sheet_name}.png'))['alpha'], 'ok')


class Orchestrator(unittest.TestCase):
    def test_rebuilds_existing_sheets(self):
        tmp = tempfile.mkdtemp()
        try:
            samples.draw(KUMA, os.path.join(tmp, 'characters', 'kuma'), jitter=True)
            result = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'avatar.py'), 'kuma', '--skip-generate'],
                                    cwd=tmp, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('<Pavatar name="kuma" />', result.stdout)
            self.assertTrue(os.path.exists(os.path.join(tmp, 'public', 'avatars', 'kuma-reactions.webp')))
        finally:
            shutil.rmtree(tmp)


class Docs(unittest.TestCase):
    def test_prompts_md_matches_prompts_py(self):
        import render_prompts
        with open(render_prompts.TARGET) as handle:
            self.assertEqual(handle.read(), render_prompts.render(),
                             'reference/prompts.md is stale: run scripts/render_prompts.py')


if __name__ == '__main__':
    unittest.main()
