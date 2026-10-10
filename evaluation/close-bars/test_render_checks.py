"""Implementation checks, not tests of model behavior or reader comprehension.

python -m unittest discover -s evaluation/close-bars -p 'test_render_checks.py' -v
Pure checks work with the standard library; render checks explicitly skip without
Matplotlib. The full render_fixtures.py CLI requires its renderer and never skips.
"""
from decimal import Decimal, DivisionByZero, localcontext
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


class RenderChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            fixtures.load_renderer()
        except RuntimeError as error:
            raise unittest.SkipTest(str(error)) from error

    def codes_after_mutation(self, generator, mutate, **options):
        audit = fixtures.audit

        def audit_mutated(*args, **kwargs):
            arguments = inspect.signature(audit).bind(*args, **kwargs).arguments
            mutate(arguments)
            return audit(**arguments)

        with patch.object(fixtures, 'audit', side_effect=audit_mutated):
            result = generator(360, **options)
        return {issue['code'] for issue in result['issues']}

    def test_repaired_and_deliberately_bad_fixtures(self):
        expected_codes = {
            'rounding_bad': {'label_value_mismatch'},
            'dense_bad_every_label': {'text_collision'},
            'positive_bad_baseline': {'nonzero_bar_baseline', 'zero_outside_plot'},
            'positive_bad_geometry': {'bar_value_mismatch', 'endpoint_pixel_mismatch'},
            'positive_bad_uncertainty': {'label_uncertainty_collision'},
            'positive_bad_labelswap': {'label_value_mismatch'},
            'positive_bad_tickscale': {'numeric_tick_value_mismatch'},
            'negative_bad_clipping': {'text_clipped'},
        }
        with tempfile.TemporaryDirectory() as directory:
            results = fixtures.run_fixtures(directory)
            self.assertEqual(sum(r['status'] == 'PASS' for r in results), 8)
            controls = [r for r in results if r['expected_failure_codes']]
            self.assertEqual(len(controls), 10)
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
            with self.subTest(generator=generator.__name__):
                def hide(arguments):
                    arguments['fig'].texts[1].set_visible(False)
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

    def test_png_dimension_mismatch_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(fixtures, 'png_dimensions', return_value=(360, 409)):
                result = fixtures.negative(360, output_dir=directory)
        self.assertIn('png_dimension_mismatch', {issue['code'] for issue in result['issues']})
        self.assertEqual(result['status'], 'UNEXPECTED_FAILURE')


if __name__ == '__main__':
    unittest.main()
