"""Implementation checks, not tests of model behavior or reader comprehension.

python -m unittest discover -s evaluation/close-bars -p 'test_render_checks.py' -v
Pure checks work with the standard library; render checks explicitly skip without
Matplotlib. The full render_fixtures.py CLI requires its renderer and never skips.
"""
from decimal import Decimal, DivisionByZero, localcontext
from contextlib import ExitStack, redirect_stdout
import io
import json
import inspect
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import render_fixtures as fixtures


class ArithmeticAndInputChecks(unittest.TestCase):
    def test_subtract_before_rounding(self):
        self.assertEqual(fixtures.decimal_delta('1.44', '1.36'), Decimal('.08'))
        self.assertEqual(fixtures.format_delta('1.44', '1.36', 1), '+0.1')
        # Premature rounding would incorrectly erase the difference.
        self.assertEqual(fixtures.format_number('1.44', 1),
                         fixtures.format_number('1.36', 1))

    def test_relative_zero_is_undefined_without_dividing(self):
        with localcontext() as context:
            context.traps[DivisionByZero] = True
            for baseline in ('0', '-0', '0.000'):
                self.assertIsNone(fixtures.relative_change('1', baseline))
        self.assertEqual(fixtures.relative_change('42.4', '40'), Decimal('6.00'))

    def test_unavailable_precision_is_not_invented(self):
        with self.assertRaisesRegex(ValueError, 'Source precision unavailable'):
            fixtures.format_number('42.1', None)
        self.assertIn('source_precision_unavailable',
                      fixtures.value_issues('42.1%', '42.1', '%', None))
        self.assertIn('unsupported_precision',
                      fixtures.value_issues('42.100%', '42.1', '%', 1))
        self.assertEqual(fixtures.value_issues('42.1%', '42.1', '%', 1), [])

    def test_sign_and_units(self):
        self.assertEqual(fixtures.num('−4.2 units'), Decimal('-4.2'))
        self.assertIn('label_sign_mismatch',
                      fixtures.value_issues('4.2 units', '-4.2', 'units', 1))
        self.assertIn('missing_unit', fixtures.value_issues('51.2 fps', '51.2', 's', 1))
        self.assertIn('missing_unit', fixtures.value_issues('42.1 pp', '42.1', '%', 1))
        self.assertIn('label_value_mismatch', fixtures.value_issues('N/A', '42.1', '%', 1))

    def test_delta_direction_and_units_are_specific(self):
        self.assertEqual(fixtures.delta_issues('Test − control: +0.3 pp', '42.4', '42.1', 'pp'), [])
        self.assertIn('delta_direction_missing',
                      fixtures.delta_issues('Control − test: +0.3 pp', '42.4', '42.1', 'pp'))
        self.assertIn('delta_unit_missing',
                      fixtures.delta_issues('Test − control: +0.3%', '42.4', '42.1', 'pp'))
        self.assertIn('delta_mismatch',
                      fixtures.delta_issues('Test − control: −0.3 pp', '42.4', '42.1', 'pp'))
        self.assertIn('unsupported_precision',
                      fixtures.delta_issues('Test − control: +0.300 pp', '42.4', '42.1', 'pp'))

    def test_tick_label_parser_allows_equivalent_numbers_without_source_precision_limit(self):
        for label in ('−10', '-10.000', '-1e1', ' -10 units '):
            with self.subTest(label=label):
                self.assertEqual(fixtures.tick_label_issues(label, -10, 'units'), [])
        self.assertEqual(fixtures.tick_label_issues('10.000 %', 10, '%'), [])
        self.assertEqual(fixtures.tick_label_issues('10 seconds', 10, 's'), [])
        self.assertEqual(fixtures.tick_label_issues('0.3%', 0.1 + 0.2, '%'), [])
        for label in ('10% / 100%', 'about 10%', 'NaN', '∞'):
            self.assertIn('numeric_tick_label_invalid', fixtures.tick_label_issues(label, 10, '%'))

    def test_png_header_reads_actual_dimensions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'header.png'
            path.write_bytes(b'\x89PNG\r\n\x1a\n' + struct.pack('>I', 13) + b'IHDR' + struct.pack('>II', 360, 410))
            self.assertEqual(fixtures.png_dimensions(path), (360, 410))
            path.write_bytes(b'not a png')
            with self.assertRaises(ValueError):
                fixtures.png_dimensions(path)

    def test_bbox_tolerance_ignores_touching_edges(self):
        box = lambda x0, x1: SimpleNamespace(x0=x0, x1=x1, y0=0, y1=10)
        self.assertFalse(fixtures.rect_intersects(box(0, 10), box(10, 20)))
        self.assertFalse(fixtures.rect_intersects(box(0, 10), box(9.5, 20)))
        self.assertTrue(fixtures.rect_intersects(box(0, 10), box(9, 20)))

    def test_output_guard_allows_results_and_external_directories_only(self):
        repository = Path(fixtures.__file__).resolve().parents[2]
        for path in (repository, repository / 'skills' / 'generated', Path(fixtures.__file__).parent):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'outside the repository'):
                fixtures.validate_output_directory(path)
        self.assertEqual(fixtures.validate_output_directory(fixtures.DEFAULT_OUTPUT), fixtures.DEFAULT_OUTPUT)
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(fixtures.validate_output_directory(directory), Path(directory).resolve())
            self.assertEqual(list(Path(directory).iterdir()), [])
        # CLI guard executes before dependency loading and never creates the directory.
        blocked = repository / 'skills' / 'render-check-output-must-not-exist'
        result = subprocess.run([sys.executable, '-B', '-S', fixtures.__file__, '--output-dir', str(blocked)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn('outside the repository', result.stderr)
        self.assertFalse(blocked.exists())

    def test_import_has_no_renderer_or_output_side_effects(self):
        script = str(Path(fixtures.__file__).resolve())
        code = f'import runpy,sys; runpy.run_path({script!r},run_name="fixture_import"); assert "matplotlib" not in sys.modules'
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, '-B', '-S', '-c', code], cwd=directory,
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, '')
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_full_cli_fails_clearly_without_renderer(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'not_created'
            result = subprocess.run([sys.executable, '-B', '-S', fixtures.__file__, '--output-dir', str(output)],
                                    env={**os.environ, 'PYTHONPATH': ''},
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn('Renderer dependencies missing', result.stderr)
            self.assertIn('requirements-render.txt', result.stderr)
            self.assertFalse(output.exists())


class ReportPublicationChecks(unittest.TestCase):
    """Exercise run lifecycle without optional rendering or a model service."""

    def fake_gallery(self, stack, mutate=None):
        stack.enter_context(patch.object(fixtures, 'load_renderer', return_value='test-renderer'))
        calls = []

        def generate(width, *args, **kwargs):
            calls.append(width)
            if mutate is not None:
                mutate(len(calls), kwargs['output_dir'])
            return {'name': 'test-fixture', 'width_px': width, 'status': 'PASS', 'issues': []}

        for name in ('positive', 'negative', 'rounding', 'dense'):
            stack.enter_context(patch.object(fixtures, name, side_effect=generate))
        stack.enter_context(redirect_stdout(io.StringIO()))
        return calls

    def seed_gallery(self, root):
        report = root / 'validation_results.json'
        report.write_text('{"counts": {"PASS": 8}}', encoding='utf-8')
        (root / 'source_data.json').write_text('previous source', encoding='utf-8')
        (root / 'previous.png').write_bytes(b'previous image')
        return report

    def test_interrupted_reruns_cannot_retain_previous_report(self):
        for error in (RuntimeError('renderer failed'), OSError('disk full'), KeyboardInterrupt()):
            for stop_at in (1, 7, 19):
                with self.subTest(error=type(error).__name__, stop_at=stop_at):
                    with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
                        root = Path(directory)
                        report = self.seed_gallery(root)

                        def interrupt(call, output):
                            self.assertFalse(report.exists())
                            (output / 'partial.png').write_bytes(b'new partial image')
                            if call == stop_at:
                                raise error

                        self.fake_gallery(stack, interrupt)
                        with self.assertRaises(type(error)):
                            fixtures.run_fixtures(root)
                        self.assertFalse(report.exists())
                        self.assertTrue((root / 'partial.png').exists())
                        self.assertEqual(json.loads((root / 'source_data.json').read_text()), fixtures.SOURCE)
                        self.assertEqual(list(root.glob('.validation-results-*.tmp')), [])

    def test_source_write_failure_invalidates_previous_report(self):
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            root = Path(directory)
            report = self.seed_gallery(root)
            calls = self.fake_gallery(stack)
            stack.enter_context(patch.object(Path, 'write_text', side_effect=OSError('source write failed')))
            with self.assertRaisesRegex(OSError, 'source write failed'):
                fixtures.run_fixtures(root)
            self.assertFalse(report.exists())
            self.assertEqual(calls, [])

    def test_unlink_failure_stops_before_modifying_gallery(self):
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            root = Path(directory)
            self.seed_gallery(root)
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            calls = self.fake_gallery(stack)
            stack.enter_context(patch.object(Path, 'unlink', side_effect=PermissionError('report locked')))
            with self.assertRaisesRegex(PermissionError, 'report locked'):
                fixtures.run_fixtures(root)
            self.assertEqual(calls, [])
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})

    def test_preflight_failures_preserve_previous_gallery(self):
        for target in ('validate_output_directory', 'load_renderer'):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.seed_gallery(root)
                before = {p.name: p.read_bytes() for p in root.iterdir()}
                with patch.object(fixtures, target, side_effect=RuntimeError('preflight failed')):
                    with self.assertRaisesRegex(RuntimeError, 'preflight failed'):
                        fixtures.run_fixtures(root)
                self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})

    def test_failed_report_serialization_leaves_no_published_or_temporary_report(self):
        for error in (OSError('report write failed'), KeyboardInterrupt()):
            with self.subTest(error=type(error).__name__), tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
                root = Path(directory)
                report = self.seed_gallery(root)
                self.fake_gallery(stack)

                def partial_dump(data, stream, **kwargs):
                    stream.write('{"counts":')
                    self.assertFalse(report.exists())
                    raise error

                stack.enter_context(patch.object(fixtures.json, 'dump', side_effect=partial_dump))
                with self.assertRaises(type(error)):
                    fixtures.run_fixtures(root)
                self.assertFalse(report.exists())
                self.assertEqual(list(root.glob('.validation-results-*.tmp')), [])

    def test_failed_report_publication_leaves_no_stale_verdict(self):
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            root = Path(directory)
            report = self.seed_gallery(root)
            self.fake_gallery(stack)
            stack.enter_context(patch.object(os, 'replace', side_effect=OSError('rename failed')))
            with self.assertRaisesRegex(OSError, 'rename failed'):
                fixtures.run_fixtures(root)
            self.assertFalse(report.exists())
            self.assertEqual(list(root.glob('.validation-results-*.tmp')), [])

    def test_complete_failing_evaluation_is_reported_with_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            root = Path(directory)
            report = self.seed_gallery(root)
            self.fake_gallery(stack)
            stack.enter_context(patch.object(fixtures, 'negative', return_value={
                'name': 'failed-fixture', 'width_px': 360, 'status': 'FAIL', 'issues': []}))
            self.assertEqual(fixtures.main(['--output-dir', str(root)]), 1)
            current = json.loads(report.read_text())
            self.assertEqual(current['counts'], {'PASS': 16, 'FAIL': 3})
            self.assertEqual(len(current['results']), 19)
            self.assertEqual(list(root.glob('.validation-results-*.tmp')), [])

    def test_successful_rerun_publishes_complete_current_report(self):
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            root = Path(directory)
            report = self.seed_gallery(root)
            self.fake_gallery(stack, lambda call, output: self.assertFalse(report.exists()))
            replace = os.replace

            def inspect_publication(source, destination):
                self.assertFalse(report.exists())
                self.assertEqual(source.parent, root)
                self.assertEqual(destination, report)
                pending = json.loads(source.read_text(encoding='utf-8'))
                self.assertEqual(pending['counts'], {'PASS': 19})
                self.assertEqual(len(pending['results']), 19)
                replace(source, destination)

            stack.enter_context(patch.object(os, 'replace', side_effect=inspect_publication))
            results = fixtures.run_fixtures(root)
            self.assertEqual(json.loads(report.read_text())['results'], results)
            self.assertEqual(list(root.glob('.validation-results-*.tmp')), [])


class RenderChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            fixtures.load_renderer()
        except RuntimeError as error:
            raise unittest.SkipTest(str(error)) from error

    def codes_after_mutation(self, generator, mutate, width=360, **options):
        audit = fixtures.audit

        def audit_mutated(*args, **kwargs):
            arguments = inspect.signature(audit).bind(*args, **kwargs).arguments
            mutate(arguments)
            return audit(**arguments)

        with patch.object(fixtures, 'audit', side_effect=audit_mutated):
            result = generator(width, **options)
        return {issue['code'] for issue in result['issues']}

    def test_endpoint_text_clipping_cannot_pass(self):
        from matplotlib.transforms import Bbox
        for generator in (fixtures.positive, fixtures.negative, fixtures.rounding, fixtures.dense):
            for width in (360, 640):
                for partial in (False, True):
                    with self.subTest(fixture=generator.__name__, width=width, partial=partial):
                        def mutate(arguments):
                            fig = arguments['fig']
                            fig.canvas.draw()
                            for artist, *_ in arguments['labels']:
                                box = artist.get_window_extent(fig.canvas.get_renderer())
                                artist.set_clip_on(True)
                                artist.set_clip_box(Bbox.from_extents(
                                    box.x0, box.y0, box.x0 + box.width / 2, box.y1)
                                    if partial else Bbox.from_bounds(0, 0, 1, 1))
                        self.assertIn('text_clipped', self.codes_after_mutation(generator, mutate, width))

    def test_clipping_required_category_context_delta_table_and_caption_is_detected(self):
        from matplotlib.transforms import Bbox
        targets = {
            'category': (fixtures.positive, lambda a: a['fig'].axes[0].get_xticklabels()[0]),
            'group': (fixtures.positive, lambda a: a['context'][0]),
            'delta': (fixtures.positive, lambda a: a['deltas'][0][0]),
            'table': (fixtures.dense, lambda a: a['table'][0][0][1]),
            'legend': (fixtures.dense, lambda a: a['context'][0]),
            'title': (fixtures.positive, lambda a: a['fig'].texts[0]),
            'caption': (fixtures.negative, lambda a: a['fig'].texts[-1]),
        }
        for role, (generator, select) in targets.items():
            for width in (360, 640):
                with self.subTest(role=role, width=width):
                    def mutate(arguments):
                        artist = select(arguments)
                        artist.set_clip_on(True)
                        artist.set_clip_box(Bbox.from_bounds(0, 0, 1, 1))
                    self.assertIn('text_clipped', self.codes_after_mutation(generator, mutate, width))

    def test_containing_or_inactive_text_clips_preserve_healthy_fixtures(self):
        from matplotlib.patches import Circle
        from matplotlib.transforms import Bbox
        for generator in (fixtures.positive, fixtures.negative, fixtures.rounding, fixtures.dense):
            for width in (360, 640):
                for mode in ('containing', 'disabled_box', 'disabled_path'):
                    with self.subTest(fixture=generator.__name__, width=width, mode=mode):
                        def mutate(arguments):
                            fig = arguments['fig']
                            fig.canvas.draw()
                            for artist in fig.findobj(match=fixtures.Text):
                                box = artist.get_window_extent(fig.canvas.get_renderer())
                                artist.set_clip_box(Bbox.from_extents(
                                    box.x0 - 1, box.y0 - 1, box.x1 + 1, box.y1 + 1)
                                    if mode == 'containing' else Bbox.from_bounds(0, 0, 1, 1))
                                if mode == 'disabled_path':
                                    artist.set_clip_path(Circle((0, 0), 1, transform=fig.transFigure))
                                artist.set_clip_on(mode == 'containing')
                        self.assertEqual(self.codes_after_mutation(generator, mutate, width), set())

    def test_active_nonrectangular_text_clips_are_explicitly_unsupported(self):
        from matplotlib.patches import Circle
        for width in (360, 640):
            def mutate(arguments):
                artist = arguments['labels'][0][0]
                artist.set_clip_path(Circle((0.5, 0.5), 2, transform=arguments['fig'].transFigure))
                artist.set_clip_on(True)
            with self.subTest(width=width):
                self.assertIn('text_clip_path_unsupported',
                              self.codes_after_mutation(fixtures.positive, mutate, width))

    def test_clipped_away_labels_cannot_supply_phantom_text_collisions(self):
        from matplotlib.transforms import Bbox
        for width in (360, 640):
            def mutate(arguments):
                for artist, *_ in arguments['labels']:
                    artist.set_clip_box(Bbox.from_bounds(0, 0, 1, 1))
                    artist.set_clip_on(True)
            with self.subTest(width=width):
                codes = self.codes_after_mutation(fixtures.dense, mutate, width, bad=True)
                self.assertIn('text_clipped', codes)
                self.assertNotIn('text_collision', codes)
                self.assertNotIn('label_bar_collision', codes)
                self.assertNotIn('label_uncertainty_collision', codes)

    def test_invalid_active_text_clip_boxes_are_unsupported(self):
        from matplotlib.transforms import Bbox
        # Avoid asking the native renderer to draw malformed clip rectangles.
        # These helper checks exercise the same validation used by the audit.
        fig = fixtures.plt.figure()
        try:
            artist = fig.text(0.5, 0.5, 'Label')
            fig.canvas.draw()
            artist.set_clip_on(True)
            for extents in ((10, 10, 0, 0), (0, 0, float('nan'), 1),
                            (0, 0, float('inf'), 1)):
                with self.subTest(extents=extents):
                    artist.set_clip_box(Bbox.from_extents(*extents))
                    self.assertIn('clip_box_unsupported',
                                  fixtures.text_clipping_issues(artist, fig.canvas.get_renderer()))
                    self.assertIsNone(fixtures.text_collision_bounds(
                        artist, Bbox.from_bounds(0, 0, 10, 10), fig.bbox))
        finally:
            fixtures.plt.close(fig)

    def test_text_collision_bounds_use_only_rectangular_visible_intersection(self):
        from matplotlib.patches import Circle
        from matplotlib.transforms import Bbox
        fig = fixtures.plt.figure()
        try:
            artist = fig.text(0.5, 0.5, 'Label')
            raw = Bbox.from_bounds(10, 10, 20, 20)
            canvas = Bbox.from_bounds(0, 0, 25, 25)
            artist.set_clip_box(Bbox.from_bounds(15, 5, 20, 15))
            artist.set_clip_on(True)
            self.assertEqual(tuple(fixtures.text_collision_bounds(artist, raw, canvas).extents),
                             (15, 10, 25, 20))
            artist.set_clip_box(Bbox.from_bounds(0, 0, 1, 1))
            self.assertIsNone(fixtures.text_collision_bounds(artist, raw, canvas))
            artist.set_clip_box(Bbox.from_bounds(10, 10, 0, 0))
            self.assertIsNone(fixtures.text_collision_bounds(artist, raw, canvas))
            artist.set_clip_path(Circle((0, 0), 1, transform=fig.transFigure))
            self.assertIsNone(fixtures.text_collision_bounds(artist, raw, canvas))
            artist.set_clip_on(False)
            self.assertEqual(tuple(fixtures.text_collision_bounds(artist, raw, canvas).extents),
                             (10, 10, 25, 25))
        finally:
            fixtures.plt.close(fig)

    def test_repaired_and_deliberately_bad_fixtures(self):
        expected_codes = {
            'rounding_bad': {'label_value_mismatch'},
            'dense_bad_every_label': {'text_collision'},
            'positive_bad_baseline': {'nonzero_bar_baseline', 'zero_outside_plot'},
            'positive_bad_geometry': {'bar_value_mismatch', 'endpoint_pixel_mismatch'},
            'positive_bad_uncertainty': {'label_uncertainty_collision'},
            'positive_bad_labelswap': {'label_value_mismatch'},
            'positive_bad_tickscale': {'numeric_tick_value_mismatch'},
            'positive_bad_missing_uncertainty': {'uncertainty_count_mismatch'},
            'negative_bad_clipping': {'text_clipped'},
        }
        with tempfile.TemporaryDirectory() as directory:
            results = fixtures.run_fixtures(directory)
            report = json.loads((Path(directory) / 'validation_results.json').read_text())
            self.assertEqual(report['results'], results)
            self.assertEqual(report['counts'], {'PASS': 8, 'EXPECTED_FAILURE_DETECTED': 11})
            self.assertEqual(sum(r['status'] == 'PASS' for r in results), 8)
            controls = [r for r in results if r['expected_failure_codes']]
            self.assertEqual(len(controls), 11)
            for result in results:
                with self.subTest(name=result['name'], width=result['width_px']):
                    self.assertIn(result['status'], ('PASS', 'EXPECTED_FAILURE_DETECTED'))
                    self.assertEqual(result['png_size_px'], result['requested_size_px'])
                    self.assertEqual(list(fixtures.png_dimensions(result['image'])), result['requested_size_px'])
                    codes = {issue['code'] for issue in result['issues']}
                    expected = expected_codes.get(result['name'], set())
                    self.assertEqual(set(result['expected_failure_codes']), expected)
                    self.assertTrue(expected <= codes)
                    if result['status'] == 'PASS':
                        self.assertEqual(result['issues'], [])

    def test_wrong_numeric_tick_magnitude_is_detected(self):
        for generator in (fixtures.positive, fixtures.dense, fixtures.rounding):
            with self.subTest(generator=generator.__name__):
                def corrupt(arguments):
                    axis = arguments['fig'].axes[0]
                    suffix = '%' if generator is not fixtures.rounding else ''
                    axis.set_yticklabels([f'{value / 10:g}{suffix}' for value in axis.get_yticks()])
                self.assertIn('numeric_tick_value_mismatch', self.codes_after_mutation(generator, corrupt))

    def test_numeric_label_anchor_must_match_tick_position(self):
        for generator in (fixtures.positive, fixtures.negative):
            with self.subTest(generator=generator.__name__):
                def move(arguments):
                    from matplotlib.transforms import Affine2D
                    axis = arguments['fig'].axes[0]
                    dimension = axis.xaxis if generator is fixtures.negative else axis.yaxis
                    label = dimension.get_major_ticks()[1].label1
                    shift = (8, 0) if generator is fixtures.negative else (0, 8)
                    label.set_transform(label.get_transform() + Affine2D().translate(*shift))
                self.assertIn('numeric_tick_position_mismatch', self.codes_after_mutation(generator, move))

    def test_wrong_negative_tick_sign_is_detected(self):
        def corrupt(arguments):
            axis = arguments['fig'].axes[0]
            axis.set_xticklabels([str(abs(value)) for value in axis.get_xticks()])
        self.assertIn('numeric_tick_value_mismatch', self.codes_after_mutation(fixtures.negative, corrupt))

    def test_numeric_tick_units_and_complete_text_are_checked(self):
        for suffix, code in (('', 'numeric_tick_unit_mismatch'),
                             (' pp', 'numeric_tick_unit_mismatch'),
                             ('% / 100%', 'numeric_tick_label_invalid'),
                             ('% approx', 'numeric_tick_label_invalid')):
            with self.subTest(suffix=suffix):
                def corrupt(arguments):
                    axis = arguments['fig'].axes[0]
                    axis.set_yticklabels([f'{value:g}{suffix}' for value in axis.get_yticks()])
                self.assertIn(code, self.codes_after_mutation(fixtures.positive, corrupt))

    def test_missing_numeric_ticks_and_labels_are_detected(self):
        for mode in ('none', 'blank', 'tick_hidden', 'hidden', 'alpha_zero', 'transparent_color'):
            with self.subTest(mode=mode):
                def hide(arguments):
                    axis = arguments['fig'].axes[0]
                    if mode == 'none':
                        axis.set_yticks([])
                    elif mode == 'blank':
                        axis.set_yticklabels([''] * len(axis.get_yticks()))
                    elif mode == 'tick_hidden':
                        for tick in axis.yaxis.get_major_ticks():
                            tick.set_visible(False)
                    else:
                        for label in axis.get_yticklabels():
                            self.make_invisible(label, mode)
                code = 'numeric_tick_count_mismatch' if mode == 'none' else 'numeric_tick_not_visible'
                self.assertIn(code, self.codes_after_mutation(fixtures.positive, hide))

    def test_clipped_numeric_tick_labels_cannot_pass(self):
        for mode in ('axes_patch', 'empty_box', 'partial_box', 'custom_path'):
            with self.subTest(mode=mode):
                def clip(arguments):
                    from matplotlib.patches import Circle
                    from matplotlib.transforms import Bbox
                    axis = arguments['fig'].axes[0]
                    arguments['fig'].canvas.draw()
                    renderer = arguments['fig'].canvas.get_renderer()
                    for label in axis.get_yticklabels():
                        label.set_clip_on(True)
                        if mode == 'axes_patch':
                            label.set_clip_path(axis.patch)
                        elif mode == 'empty_box':
                            label.set_clip_box(Bbox.from_bounds(0, 0, 0, 0))
                        elif mode == 'partial_box':
                            bounds = label.get_window_extent(renderer)
                            label.set_clip_box(Bbox.from_extents(bounds.x0, bounds.y0, bounds.x0 + 2, bounds.y1))
                        else:
                            label.set_clip_path(Circle((0.5, 0.5), 0.5, transform=axis.transAxes))
                code = 'numeric_tick_clip_path_unsupported' if mode == 'custom_path' else 'numeric_tick_clipped'
                self.assertIn(code, self.codes_after_mutation(fixtures.positive, clip))

    def test_nonclipping_or_containing_clip_boxes_are_valid(self):
        for clipping in (False, True):
            with self.subTest(clipping=clipping):
                def clip(arguments):
                    from matplotlib.transforms import Bbox
                    axis = arguments['fig'].axes[0]
                    for label in axis.get_yticklabels():
                        label.set_clip_box(arguments['fig'].bbox if clipping else Bbox.from_bounds(0, 0, 0, 0))
                        label.set_clip_on(clipping)
                self.assertEqual(self.codes_after_mutation(fixtures.positive, clip), set())

    def test_hidden_numeric_axis_is_detected(self):
        for mode in ('dimension', 'axis_off'):
            with self.subTest(mode=mode):
                def hide(arguments):
                    axis = arguments['fig'].axes[0]
                    if mode == 'dimension':
                        axis.yaxis.set_visible(False)
                    else:
                        axis.set_axis_off()
                self.assertIn('numeric_axis_not_visible', self.codes_after_mutation(fixtures.positive, hide))

    def test_both_visible_tick_label_sides_are_checked(self):
        # Axis.draw regenerates both texts. Corrupt the actual label2 setter so
        # the wrong side is already wrong when painted, not only after drawing.
        def corrupt(arguments):
            axis = arguments['fig'].axes[0]
            axis.tick_params(axis='y', labelright=True)
            label = axis.yaxis.get_major_ticks()[1].label2
            set_text = label.set_text
            label.set_text = lambda value: set_text('1%' if value == '10%' else value)
        self.assertIn('numeric_tick_value_mismatch', self.codes_after_mutation(fixtures.positive, corrupt))

    def test_valid_numeric_tick_representations_and_spacing(self):
        for generator in (fixtures.positive, fixtures.negative, fixtures.rounding, fixtures.dense):
            with self.subTest(generator=generator.__name__):
                def format_ticks(arguments):
                    from matplotlib.ticker import FuncFormatter
                    axis = arguments['fig'].axes[0]
                    dimension = axis.xaxis if generator is fixtures.negative else axis.yaxis
                    values = [-10, -5, 0] if generator is fixtures.negative else [0, 20, 40, 60]
                    dimension.set_ticks(values)
                    suffix = '%' if generator in (fixtures.positive, fixtures.dense) else ''
                    places = 0 if suffix else 1
                    dimension.set_major_formatter(FuncFormatter(lambda value, _: f'{value:.{places}f}{suffix}'))
                # Other geometry assertions remain active; changed spacing is valid.
                self.assertEqual(self.codes_after_mutation(generator, format_ticks), set())

    def test_out_of_view_numeric_tick_labels_are_ignored(self):
        def extra(arguments):
            axis = arguments['fig'].axes[0]
            axis.set_yticks([-100, 0, 10, 20, 30, 40, 50, 60, 100])
            axis.set_yticklabels(['wrong', '0%', '10%', '20%', '30%', '40%', '50%', '60%', 'wrong'])
            axis.set_ylim(0, 65)  # set_ticks expands limits; restore the intended view.
        self.assertEqual(self.codes_after_mutation(fixtures.positive, extra), set())

    def test_labeled_minor_ticks_are_checked_but_unlabeled_are_allowed(self):
        for bad in (False, True):
            with self.subTest(bad=bad):
                def minor(arguments):
                    axis = arguments['fig'].axes[0]
                    axis.set_yticks([5], minor=True)
                    if bad:
                        axis.set_yticklabels(['50%'], minor=True)
                codes = self.codes_after_mutation(fixtures.positive, minor)
                if bad:
                    self.assertIn('numeric_tick_value_mismatch', codes)
                else:
                    self.assertEqual(codes, set())

    def test_inherited_numeric_tick_units_need_visible_caption(self):
        for generator in (fixtures.negative, fixtures.rounding):
            for clipped in (False, True):
                with self.subTest(generator=generator.__name__, clipped=clipped):
                    def hide(arguments):
                        from matplotlib.transforms import Bbox
                        caption = arguments['fig'].texts[1]
                        if clipped:
                            caption.set_clip_on(True)
                            caption.set_clip_box(Bbox.from_bounds(0, 0, 0, 0))
                        else:
                            caption.set_visible(False)
                    self.assertIn('numeric_axis_unit_context_missing', self.codes_after_mutation(generator, hide))

    def test_separate_formatter_offset_and_nonlinear_scale_are_explicitly_unsupported(self):
        def offset(arguments):
            from matplotlib.ticker import FixedFormatter
            axis = arguments['fig'].axes[0]
            formatter = FixedFormatter([f'{value:g}%' for value in axis.get_yticks()])
            formatter.set_offset_string('×10')
            axis.yaxis.set_major_formatter(formatter)
        self.assertIn('numeric_axis_offset_unsupported', self.codes_after_mutation(fixtures.positive, offset))
        def scale(arguments):
            arguments['fig'].axes[0].set_yscale('symlog')
        self.assertIn('numeric_axis_scale_unsupported', self.codes_after_mutation(fixtures.positive, scale))

    def test_label_association_is_not_certified_by_correct_number(self):
        def move_label(arguments):
            arguments['labels'][0][0].set_position((45, 6))
        self.assertIn('label_association_mismatch', self.codes_after_mutation(fixtures.positive, move_label))

    def test_selected_labels_and_full_table_are_checked(self):
        def omit_label(arguments):
            arguments['labels'].pop()
        self.assertIn('selected_labels_mismatch', self.codes_after_mutation(fixtures.dense, omit_label))

        def omit_row(arguments):
            arguments['table'].pop()
        self.assertIn('incomplete_table', self.codes_after_mutation(fixtures.dense, omit_row))

        def corrupt_cell(arguments):
            arguments['table'][0][0][1].set_text('99.9%')
        self.assertIn('table_value_mismatch', self.codes_after_mutation(fixtures.dense, corrupt_cell))

    def test_geometry_sign_and_dimensions_are_checked(self):
        def flip_bar(arguments):
            arguments['bars'][0][0].set_width(4.2)
        self.assertIn('bar_sign_mismatch', self.codes_after_mutation(fixtures.negative, flip_bar))

        def resize(arguments):
            arguments['fig'].set_size_inches(3.7, 4.7)
        self.assertIn('canvas_dimension_mismatch', self.codes_after_mutation(fixtures.positive, resize))

    def test_source_and_unit_metadata_cannot_certify_wrong_artists(self):
        def corrupt_source(arguments):
            bar, axis, orientation, _ = arguments['bars'][0]
            bar.set_height(99)
            arguments['bars'][0] = (bar, axis, orientation, '99')
        codes = self.codes_after_mutation(fixtures.positive, corrupt_source)
        self.assertTrue({'bar_source_mismatch', 'bar_value_mismatch'} <= codes)

        def corrupt_unit(arguments):
            artist, value, _, bar = arguments['labels'][0]
            artist.set_text(value + ' pp')
            arguments['labels'][0] = (artist, value, 'pp', bar)
        self.assertIn('label_unit_mismatch', self.codes_after_mutation(fixtures.positive, corrupt_unit))

        def hide_label(arguments):
            arguments['labels'][0][0].set_visible(False)
        self.assertIn('label_not_visible', self.codes_after_mutation(fixtures.dense, hide_label))

    def test_one_and_all_table_cells_must_be_visible(self):
        for all_cells in (False, True):
            for mode in ('hidden', 'alpha_zero', 'transparent_color', 'removed'):
                with self.subTest(all_cells=all_cells, mode=mode):
                    def hide_cells(arguments):
                        cells = [cell for row, _ in arguments['table'] for cell in row]
                        for cell in cells if all_cells else cells[:1]:
                            self.make_invisible(cell, mode)
                    self.assertIn('table_cell_not_visible', self.codes_after_mutation(fixtures.dense, hide_cells))

    def test_one_and_all_delta_captions_must_be_visible(self):
        for all_captions in (False, True):
            for mode in ('hidden', 'alpha_zero', 'transparent_color', 'removed'):
                with self.subTest(all_captions=all_captions, mode=mode):
                    def hide_captions(arguments):
                        captions = [record[0] for record in arguments['deltas']]
                        for caption in captions if all_captions else captions[:1]:
                            self.make_invisible(caption, mode)
                    self.assertIn('delta_not_visible', self.codes_after_mutation(fixtures.positive, hide_captions))

    def test_one_and_all_delta_records_are_required(self):
        for generator in (fixtures.positive, fixtures.rounding):
            for all_records in (False, True):
                with self.subTest(generator=generator.__name__, all_records=all_records):
                    def omit_deltas(arguments):
                        records = arguments['deltas']
                        count = len(records) if all_records else 1
                        for artist, *_ in records[:count]:
                            artist.remove()
                        del records[:count]
                    self.assertIn('delta_count_mismatch', self.codes_after_mutation(generator, omit_deltas))

    def test_extra_delta_records_report_a_count_error(self):
        for generator in (fixtures.positive, fixtures.rounding):
            with self.subTest(generator=generator.__name__):
                def duplicate_delta(arguments):
                    arguments['deltas'].append(arguments['deltas'][-1])
                self.assertIn('delta_count_mismatch', self.codes_after_mutation(generator, duplicate_delta))

    def test_one_and_all_endpoint_labels_must_be_visible(self):
        for generator in (fixtures.positive, fixtures.dense):
            for all_labels in (False, True):
                for mode in ('hidden', 'alpha_zero', 'transparent_color', 'removed'):
                    with self.subTest(generator=generator.__name__, all_labels=all_labels, mode=mode):
                        def hide_labels(arguments):
                            labels = [record[0] for record in arguments['labels']]
                            for label in labels if all_labels else labels[:1]:
                                self.make_invisible(label, mode)
                        self.assertIn('label_not_visible', self.codes_after_mutation(generator, hide_labels))

    def test_hidden_parent_axes_and_figure_are_detected(self):
        def hide_axes(arguments):
            arguments['fig'].axes[0].set_visible(False)
        codes = self.codes_after_mutation(fixtures.positive, hide_axes)
        self.assertTrue({'bar_not_visible', 'label_not_visible', 'delta_not_visible'} <= codes)

        def hide_figure(arguments):
            arguments['fig'].set_visible(False)
        codes = self.codes_after_mutation(fixtures.dense, hide_figure)
        self.assertTrue({'bar_not_visible', 'label_not_visible', 'table_cell_not_visible'} <= codes)

    def test_source_category_labels_cannot_be_swapped(self):
        for generator in (fixtures.positive, fixtures.negative, fixtures.rounding, fixtures.dense):
            with self.subTest(generator=generator.__name__):
                def swap_categories(arguments):
                    axis = arguments['fig'].axes[0]
                    ticks = axis.get_yticklabels() if generator is fixtures.negative else axis.get_xticklabels()
                    labels = [tick.get_text() for tick in ticks]
                    labels[0], labels[1] = labels[1], labels[0]
                    setter = axis.set_yticklabels if generator is fixtures.negative else axis.set_xticklabels
                    setter(labels)
                self.assertIn('category_label_mismatch', self.codes_after_mutation(generator, swap_categories))

    def test_dense_headers_series_key_and_units_must_be_visible_and_correct(self):
        def swap_headers(arguments):
            headers = arguments['context']
            headers[2].set_text('Test')
            headers[3].set_text('Control')
        self.assertIn('context_label_mismatch', self.codes_after_mutation(fixtures.dense, swap_headers))
        for index in range(6):
            with self.subTest(context_index=index):
                def hide_context(arguments):
                    arguments['context'][index].set_visible(False)
                self.assertIn('context_not_visible', self.codes_after_mutation(fixtures.dense, hide_context))

    def test_invisible_bars_are_detected(self):
        def transparent_bar(arguments):
            arguments['bars'][0][0].set_alpha(0)
        self.assertIn('bar_not_visible', self.codes_after_mutation(fixtures.positive, transparent_bar))

    def test_transformed_bar_baselines_cannot_pass_with_correct_raw_dimensions(self):
        from matplotlib.transforms import Affine2D
        for generator in (fixtures.positive, fixtures.negative, fixtures.rounding, fixtures.dense):
            for width in (360, 640):
                with self.subTest(generator=generator.__name__, width=width):
                    def truncate(arguments):
                        for bar, axis, orientation, value in arguments['bars']:
                            # Keep the source endpoint, raw baseline, and raw
                            # extent unchanged; only the rendered length halves.
                            transform = (Affine2D().scale(1, .5).translate(0, float(value) / 2)
                                         if orientation == 'v' else
                                         Affine2D().scale(.5, 1).translate(float(value) / 2, 0))
                            bar.set_transform(transform + axis.transData)
                    codes = self.codes_after_mutation(generator, truncate, width=width)
                    self.assertIn('bar_baseline_pixel_mismatch', codes)
                    self.assertFalse({'nonzero_bar_baseline', 'bar_value_mismatch',
                                      'endpoint_pixel_mismatch', 'bar_extent_pixel_mismatch'} & codes)

    def test_transformed_bar_value_edges_are_checked(self):
        from matplotlib.transforms import Affine2D
        for generator in (fixtures.positive, fixtures.negative):
            with self.subTest(generator=generator.__name__):
                def shorten(arguments):
                    for bar, axis, orientation, _ in arguments['bars']:
                        transform = Affine2D().scale(1, .5) if orientation == 'v' else Affine2D().scale(.5, 1)
                        bar.set_transform(transform + axis.transData)
                codes = self.codes_after_mutation(generator, shorten)
                self.assertIn('bar_extent_pixel_mismatch', codes)
                self.assertNotIn('bar_baseline_pixel_mismatch', codes)

    def test_bar_fill_must_be_visible_and_have_nonzero_area(self):
        for generator in (fixtures.positive, fixtures.negative):
            for mode in ('transparent_face', 'no_fill', 'all_transparent', 'zero_cross_width', 'removed'):
                with self.subTest(generator=generator.__name__, mode=mode):
                    def mutate(arguments):
                        for bar, _, orientation, _ in arguments['bars']:
                            if mode == 'transparent_face':
                                bar.set_facecolor((0, 0, 0, 0))
                            elif mode == 'no_fill':
                                bar.set_fill(False)
                            elif mode == 'all_transparent':
                                bar.set_facecolor('none')
                                bar.set_edgecolor('none')
                                bar.set_hatch(None)
                            elif mode == 'zero_cross_width':
                                (bar.set_width if orientation == 'v' else bar.set_height)(0)
                            else:
                                bar.remove()
                    expected = 'bar_not_visible' if mode == 'removed' else 'bar_fill_not_visible'
                    self.assertIn(expected, self.codes_after_mutation(generator, mutate))

    def test_bar_rectangular_clips_and_canvas_are_checked(self):
        from matplotlib.transforms import Affine2D, Bbox
        for generator in (fixtures.positive, fixtures.negative):
            for mode in ('empty_clip', 'partial_clip', 'outside_canvas'):
                with self.subTest(generator=generator.__name__, mode=mode):
                    def mutate(arguments):
                        for bar, axis, orientation, _ in arguments['bars']:
                            if mode == 'empty_clip':
                                bar.set_clip_box(Bbox.from_bounds(0, 0, 1, 1))
                            elif mode == 'partial_clip':
                                bounds = bar.get_window_extent()
                                bar.set_clip_box(Bbox.from_extents(bounds.x0, bounds.y0,
                                                                  (bounds.x0 + bounds.x1) / 2, bounds.y1))
                            else:
                                # Move cross-axis only, keeping numeric endpoints
                                # intact, and disable artist clipping.
                                transform = Affine2D().translate(1000, 0) if orientation == 'v' else Affine2D().translate(0, 1000)
                                bar.set_transform(axis.transData + transform)
                                bar.set_clip_on(False)
                    self.assertIn('bar_clipped', self.codes_after_mutation(generator, mutate))

    def test_custom_bar_shapes_and_paint_are_explicitly_unsupported(self):
        from matplotlib.patches import Circle
        from matplotlib.path import Path as MplPath
        from matplotlib.transforms import Affine2D, Transform
        class NonAffineIdentity(Transform):
            input_dims = output_dims = 2
            def transform_non_affine(self, values):
                return values
        for generator in (fixtures.positive, fixtures.negative):
            for mode in ('clip_path', 'rotation', 'shear', 'custom_path', 'nonaffine',
                         'animated', 'sketch', 'path_effect', 'agg_filter'):
                with self.subTest(generator=generator.__name__, mode=mode):
                    def mutate(arguments):
                        bar, axis, _, _ = arguments['bars'][0]
                        if mode == 'clip_path':
                            bar.set_clip_path(Circle((0, 0), 1, transform=arguments['fig'].transFigure))
                        elif mode == 'rotation':
                            bar.set_angle(15)
                        elif mode == 'shear':
                            bar.set_transform(Affine2D().skew_deg(10, 10) + axis.transData)
                        elif mode == 'custom_path':
                            bar.get_path = lambda: MplPath([[0, 0], [1, 0], [.5, 1], [0, 0]], [1, 2, 2, 79])
                        elif mode == 'nonaffine':
                            bar.set_transform(NonAffineIdentity() + axis.transData)
                        elif mode == 'animated':
                            bar.set_animated(True)
                        elif mode == 'sketch':
                            bar.set_sketch_params(scale=15, length=10, randomness=1)
                        elif mode == 'path_effect':
                            from matplotlib.patheffects import Stroke
                            bar.set_path_effects([Stroke(linewidth=10)])
                        else:
                            bar.set_agg_filter(lambda image, dpi: (image, 0, 0))
                    expected = 'bar_clip_path_unsupported' if mode == 'clip_path' else 'bar_artist_unsupported'
                    self.assertIn(expected, self.codes_after_mutation(generator, mutate))

    def test_equivalent_bar_transforms_styles_and_clips_are_positive_controls(self):
        from matplotlib.patches import Circle
        from matplotlib.transforms import Affine2D, Bbox
        for generator in (fixtures.positive, fixtures.negative, fixtures.rounding, fixtures.dense):
            for width in (360, 640):
                for mode in ('equivalent_transform', 'reflected_transform', 'frozen_transform', 'style', 'containing_clip', 'disabled_clip'):
                    with self.subTest(generator=generator.__name__, width=width, mode=mode):
                        def mutate(arguments):
                            for bar, axis, orientation, value in arguments['bars']:
                                if mode == 'equivalent_transform':
                                    move = Affine2D().scale(2, 3).translate(7, 9)
                                    bar.set_transform(move + move.inverted() + axis.transData)
                                elif mode == 'reflected_transform':
                                    transform = (Affine2D().scale(1, -1).translate(0, float(value))
                                                 if orientation == 'v' else
                                                 Affine2D().scale(-1, 1).translate(float(value), 0))
                                    bar.set_transform(transform + axis.transData)
                                elif mode == 'frozen_transform':
                                    bar.set_transform(axis.transData.frozen())
                                elif mode == 'style':
                                    bar.set_facecolor('#654321')
                                    bar.set_alpha(.6)
                                    bar.set_edgecolor('none')
                                    bar.set_linewidth(0)
                                elif mode == 'containing_clip':
                                    bar.set_clip_box(arguments['fig'].bbox)
                                else:
                                    bar.set_clip_path(Circle((0, 0), 1, transform=arguments['fig'].transFigure))
                                    bar.set_clip_box(Bbox.from_bounds(0, 0, 1, 1))
                                    bar.set_clip_on(False)
                        self.assertEqual(self.codes_after_mutation(generator, mutate, width=width), set())

    def test_invisible_bars_do_not_produce_phantom_label_collisions(self):
        from matplotlib.transforms import Bbox
        for mode in ('visible', 'hidden', 'transparent', 'clipped'):
            with self.subTest(mode=mode):
                def mutate(arguments):
                    bar = arguments['bars'][0][0]
                    label = arguments['labels'][0][0]
                    label.set_position((0, -80))  # Deliberately place inside this bar.
                    if mode == 'hidden':
                        bar.set_visible(False)
                    elif mode == 'transparent':
                        bar.set_facecolor('none')
                        bar.set_edgecolor('none')
                        bar.set_hatch(None)
                    elif mode == 'clipped':
                        bar.set_clip_box(Bbox.from_bounds(0, 0, 1, 1))
                codes = self.codes_after_mutation(fixtures.rounding, mutate)
                self.assertEqual('label_bar_collision' in codes, mode == 'visible')

    @staticmethod
    def make_invisible(artist, mode):
        if mode == 'hidden':
            artist.set_visible(False)
        elif mode == 'alpha_zero':
            artist.set_alpha(0)
        elif mode == 'transparent_color':
            artist.set_color((0, 0, 0, 0))
        elif mode == 'removed':
            artist.remove()

    @staticmethod
    def errorbars(arguments):
        from matplotlib.container import ErrorbarContainer
        return [container for axis in arguments['fig'].axes for container in axis.containers
                if isinstance(container, ErrorbarContainer)]

    def test_missing_uncertainty_containers_and_registration_are_detected(self):
        for generator in (fixtures.positive, fixtures.negative):
            for all_intervals in (False, True):
                for mode in ('remove', 'unregister'):
                    with self.subTest(generator=generator.__name__, all_intervals=all_intervals, mode=mode):
                        def mutate(arguments):
                            errors = self.errorbars(arguments)
                            for error in errors if all_intervals else errors[:1]:
                                if mode == 'remove':
                                    error.remove()
                                else:
                                    arguments['fig'].axes[0].containers.remove(error)
                        codes = self.codes_after_mutation(generator, mutate)
                        self.assertIn('uncertainty_count_mismatch', codes)
                        if mode == 'unregister':
                            self.assertIn('uncertainty_artist_unsupported', codes)

    def test_actual_uncertainty_stems_and_caps_must_be_visible(self):
        for generator in (fixtures.positive, fixtures.negative):
            for part in ('stem', 'low_cap', 'high_cap'):
                for mode in ('hidden', 'alpha_zero', 'transparent_color', 'removed', 'zero_width', 'zero_size'):
                    if part == 'stem' and mode == 'zero_size':
                        continue
                    with self.subTest(generator=generator.__name__, part=part, mode=mode):
                        def mutate(arguments):
                            error = self.errorbars(arguments)[0]
                            artist = error.lines[2][0] if part == 'stem' else error.lines[1][part == 'high_cap']
                            if mode == 'zero_width':
                                (artist.set_linewidth if part == 'stem' else artist.set_markeredgewidth)(0)
                            elif mode == 'zero_size':
                                artist.set_markersize(0)
                            elif mode == 'transparent_color' and part != 'stem':
                                artist.set_markeredgecolor((0, 0, 0, 0))
                            else:
                                self.make_invisible(artist, mode)
                        self.assertIn('uncertainty_not_visible', self.codes_after_mutation(generator, mutate))

    def test_wrong_uncertainty_endpoints_associations_and_transforms_are_detected(self):
        from matplotlib.transforms import Affine2D
        for generator in (fixtures.positive, fixtures.negative):
            for part in ('stem', 'cap', 'stem_transform', 'cap_transform'):
                with self.subTest(generator=generator.__name__, part=part):
                    def mutate(arguments):
                        error = self.errorbars(arguments)[0]
                        artist = error.lines[2][0] if part.startswith('stem') else error.lines[1][0]
                        if part.endswith('transform'):
                            artist.set_transform(artist.get_transform() + Affine2D().translate(15, 15))
                        elif part == 'stem':
                            points = artist.get_segments()[0].copy()
                            points[0][1 if generator is fixtures.positive else 0] += 1
                            artist.set_segments([points])
                        else:
                            points = artist.get_xydata().copy()
                            points[0][1 if generator is fixtures.positive else 0] += 1
                            artist.set_data(points[:, 0], points[:, 1])
                    self.assertIn('uncertainty_geometry_mismatch', self.codes_after_mutation(generator, mutate))
            def duplicate_association(arguments):
                errors = self.errorbars(arguments)
                errors[1].lines[2][0].set_segments(errors[0].lines[2][0].get_segments())
            self.assertIn('uncertainty_association_mismatch', self.codes_after_mutation(generator, duplicate_association))

    def test_uncertainty_uses_independent_source_endpoints(self):
        import copy
        for generator in (fixtures.positive, fixtures.negative):
            altered = copy.deepcopy(fixtures.SOURCE)
            altered[generator.__name__]['low'][0] = str(Decimal(altered[generator.__name__]['low'][0]) - 1)
            with self.subTest(generator=generator.__name__), patch.object(fixtures, 'SOURCE', altered):
                self.assertIn('uncertainty_geometry_mismatch', self.codes_after_mutation(generator, lambda _: None))

    def test_removed_or_invisible_whiskers_do_not_create_phantom_collisions(self):
        for mode in ('remove', 'hidden', 'alpha_zero', 'transparent_color'):
            with self.subTest(mode=mode):
                def mutate(arguments):
                    for error in self.errorbars(arguments):
                        if mode == 'remove':
                            error.remove()
                        else:
                            for artist in (*error.lines[1], *error.lines[2]):
                                if mode == 'transparent_color' and artist in error.lines[1]:
                                    artist.set_markeredgecolor((0, 0, 0, 0))
                                else:
                                    self.make_invisible(artist, mode)
                codes = self.codes_after_mutation(fixtures.positive, mutate, fault='uncertainty')
                self.assertNotIn('label_uncertainty_collision', codes)
                self.assertTrue({'uncertainty_count_mismatch', 'uncertainty_not_visible'} & codes)

    def test_collisions_follow_displaced_actual_caps_and_stems(self):
        from matplotlib.transforms import IdentityTransform
        for generator in (fixtures.positive, fixtures.negative):
            for part in ('cap', 'stem'):
                with self.subTest(generator=generator.__name__, part=part):
                    def mutate(arguments):
                        fig = arguments['fig']
                        fig.canvas.draw()
                        box = arguments['labels'][0][0].get_window_extent(fig.canvas.get_renderer())
                        x, y = (box.x0 + box.x1) / 2, (box.y0 + box.y1) / 2
                        error = self.errorbars(arguments)[0]
                        if part == 'cap':
                            artist = error.lines[1][0]
                            artist.set_data([x], [y])
                        else:
                            artist = error.lines[2][0]
                            artist.set_segments([[(x, y - 2), (x, y + 2)]])
                        artist.set_transform(IdentityTransform())
                    codes = self.codes_after_mutation(generator, mutate)
                    self.assertTrue({'label_uncertainty_collision', 'uncertainty_geometry_mismatch'} <= codes)

    def test_uncertainty_clipping_and_unsupported_custom_artists_fail_explicitly(self):
        from matplotlib.patches import Circle
        from matplotlib.transforms import Affine2D, Bbox
        for generator in (fixtures.positive, fixtures.negative):
            for mode in ('clip_box', 'clip_path', 'offsets', 'offset_transform', 'dashes', 'marker', 'missing_cap', 'empty_stem', 'markevery', 'rotated_marker', 'animated', 'sketch', 'path_effect', 'agg_filter'):
                with self.subTest(generator=generator.__name__, mode=mode):
                    def mutate(arguments):
                        error = self.errorbars(arguments)[0]
                        stem = error.lines[2][0]
                        if mode == 'clip_box':
                            stem.set_clip_box(Bbox.from_extents(0, 0, 1, 1))
                        elif mode == 'clip_path':
                            stem.set_clip_path(Circle((0, 0), 1, transform=arguments['fig'].transFigure))
                        elif mode == 'offsets':
                            stem.set_offsets([[3, 0]])
                        elif mode == 'offset_transform':
                            stem.set_offset_transform(Affine2D().translate(3, 0))
                        elif mode == 'dashes':
                            stem.set_linestyle('--')
                        elif mode == 'marker':
                            error.lines[1][0].set_marker('o')
                        elif mode == 'markevery':
                            error.lines[1][0].set_markevery([])
                        elif mode == 'rotated_marker':
                            from matplotlib.markers import MarkerStyle
                            marker = '_' if generator is fixtures.positive else '|'
                            error.lines[1][0].set_marker(MarkerStyle(marker, transform=Affine2D().rotate_deg(90)))
                        elif mode == 'animated':
                            error.lines[1][0].set_animated(True)
                        elif mode == 'sketch':
                            stem.set_sketch_params(scale=15, length=10, randomness=1)
                        elif mode == 'path_effect':
                            from matplotlib.patheffects import Stroke
                            stem.set_path_effects([Stroke(linewidth=10)])
                        elif mode == 'agg_filter':
                            stem.set_agg_filter(lambda image, dpi: (image, 0, 0))
                        elif mode == 'missing_cap':
                            error.lines = (None, error.lines[1][:1], error.lines[2])
                        else:
                            stem.set_segments([])
                    expected = {'clip_box': 'uncertainty_clipped', 'clip_path': 'uncertainty_clip_path_unsupported'}.get(mode, 'uncertainty_artist_unsupported')
                    self.assertIn(expected, self.codes_after_mutation(generator, mutate))

    def test_extra_uncertainty_is_detected(self):
        def mutate(arguments):
            arguments['fig'].axes[0].errorbar(0, 42.1, yerr=0.8, capsize=3, fmt='none')
        self.assertIn('uncertainty_count_mismatch', self.codes_after_mutation(fixtures.positive, mutate))

    def test_equivalent_uncertainty_geometry_and_styles_are_positive_controls(self):
        from matplotlib.transforms import Affine2D
        for generator in (fixtures.positive, fixtures.negative):
            for width in (360, 640):
                for mode in ('reordered', 'style', 'equivalent_transform', 'containing_clip', 'disabled_clip'):
                    with self.subTest(generator=generator.__name__, width=width, mode=mode):
                        def mutate(arguments):
                            errors = self.errorbars(arguments)
                            if mode == 'reordered':
                                axis = arguments['fig'].axes[0]
                                for error in errors:
                                    axis.containers.remove(error)
                                axis.containers.extend(reversed(errors))
                                return
                            for error in errors:
                                for artist in (*error.lines[1], *error.lines[2]):
                                    if mode == 'style':
                                        artist.set_color('#654321')
                                        artist.set_alpha(.7)
                                        if artist in error.lines[1]:
                                            artist.set_markersize(7)
                                            artist.set_markeredgewidth(1.2)
                                        else:
                                            artist.set_linewidth(1.2)
                                    elif mode == 'equivalent_transform':
                                        if artist in error.lines[1]:
                                            points = artist.get_xydata() * 2
                                            artist.set_data(points[:, 0], points[:, 1])
                                        else:
                                            artist.set_segments([artist.get_segments()[0] * 2])
                                        artist.set_transform(Affine2D().scale(.5) + artist.get_transform())
                                    elif mode == 'containing_clip':
                                        artist.set_clip_box(arguments['fig'].bbox)
                                    else:
                                        artist.set_clip_on(False)
                        self.assertEqual(self.codes_after_mutation(generator, mutate, width=width), set())

    def test_png_dimension_mismatch_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(fixtures, 'png_dimensions', return_value=(360, 409)):
                result = fixtures.negative(360, output_dir=directory)
        self.assertIn('png_dimension_mismatch', {issue['code'] for issue in result['issues']})
        self.assertEqual(result['status'], 'UNEXPECTED_FAILURE')


if __name__ == '__main__':
    unittest.main()
