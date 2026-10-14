"""Synthetic implementation fixtures, NOT model-behavior or comprehension evals.

No OCR, external services, or import-time rendering. Fixture artifacts go to --output-dir;
Matplotlib may also maintain its normal cache.
Requires the pinned optional renderer; arithmetic tests use only the standard library.
"""
import argparse
from collections import Counter
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
import itertools
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import tempfile

DPI = 100
FONT = 10.08  # 14 raster pixels at 100 dpi; never reduced for the 360 px view.
C, T, INK = '#b8c4d0', '#2c705f', '#202d38'
DEFAULT_OUTPUT = Path(__file__).resolve().parent / 'results' / 'rendered'
NUMBER = re.compile(r'[+−-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+−-]?\d+)?')


def load_renderer():
    """Import only when rendering is explicitly requested, never on module import."""
    global plt, Text, Bbox, to_rgba, ErrorbarContainer, LineCollection, MarkerStyle, Line2D, Rectangle
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.text import Text
        from matplotlib.container import ErrorbarContainer
        from matplotlib.collections import LineCollection
        from matplotlib.markers import MarkerStyle
        from matplotlib.lines import Line2D
        from matplotlib.patches import Rectangle
        from matplotlib.colors import to_rgba
        from matplotlib.transforms import Bbox
    except ImportError as exc:
        raise RuntimeError('Renderer dependencies missing. Install with: '
                           'python -m pip install -r evaluation/close-bars/requirements-render.txt') from exc
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': FONT,
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.spines.left': False, 'axes.spines.bottom': False,
        'axes.unicode_minus': True, 'savefig.facecolor': 'white'})
    return matplotlib.__version__


SOURCE = {
 'synthetic': True,
 'precision_semantics': 'Decimal places reported by these invented inputs, not measurement certainty.',
 'description':'Invented, compatible observations supplied only for local fixture checking. Intervals are invented 95% confidence intervals; no significance claim is made.',
 'positive': {'decimal_places': 1,'interval':{'type':'confidence interval','level':0.95,'synthetic':True}, 'unit':'%', 'groups':['Week 1','Week 2'], 'series':['Control','Test'],
  'values':['42.1','42.4','48.2','48.6'], 'low':['41.3','41.6','47.4','47.8'], 'high':['42.9','43.2','49.0','49.4']},
 'negative': {'decimal_places': 1,'interval':{'type':'confidence interval','level':0.95,'synthetic':True}, 'unit':'units', 'groups':['A control','A test','B control','B test'],
  'values':['-4.2','-4.4','-7.1','-7.3'], 'low':['-4.6','-4.8','-7.5','-7.7'], 'high':['-3.8','-4.0','-6.7','-6.9']},
 'rounding': {'decimal_places': 1,'unit':'s', 'groups':['Control','Test'], 'values':['51.2','51.4']},
 'dense': {'decimal_places': 1,'unit':'%', 'groups':list('ABCDEFGHIJ'),
  'control':['42.1','41.0','46.5','42.2','39.1','44.1','45.0','53.2','45.6','46.1'],
  'test':['42.4','41.3','46.8','42.3','39.4','44.2','45.3','53.6','45.8','46.3']}
}
# In-memory independent copy for checks; no source files written during import.
AUDIT_SOURCE = json.loads(json.dumps(SOURCE))


def decimal_delta(b, a):
    """Compute on reported inputs before any display rounding."""
    with localcontext() as ctx:
        ctx.prec = max(28, len(str(a)) + len(str(b)) + 10)
        return Decimal(b) - Decimal(a)


def relative_change(b, a):
    """Relative percent change; undefined for a zero reference (never divide)."""
    reference = Decimal(a)
    if reference == 0:
        return None
    return decimal_delta(b, a) / reference * 100


def format_number(value, places, signed=False):
    if places is None:
        raise ValueError('Source precision unavailable; do not invent decimal places')
    if not isinstance(places, int) or places < 0:
        raise ValueError('Decimal places must be a nonnegative integer')
    rounded = Decimal(value).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_EVEN)
    return format(rounded, f'{"+" if signed else ""}.{places}f').replace('-', '−')


def format_delta(b, a, places):
    return format_number(decimal_delta(b, a), places, signed=True)


def pct(v): return format_number(v, 1) + '%'
def sec(v): return format_number(v, 1) + ' s'
def signed(v): return format_number(v, 1, signed=True)


def num(text):
    match = NUMBER.search(text)
    return Decimal(match.group().replace('−', '-')) if match else None


def has_unit(label, unit):
    return re.search(NUMBER.pattern + r'\s*' + re.escape(unit) + r'(?!\w)', label) is not None


def value_issues(label, source_value, unit, places):
    """Check numeric fidelity, explicit sign, units, and supported decimal places."""
    issues = []
    parsed, source = num(label), Decimal(source_value)
    if parsed != source:
        issues.append('label_value_mismatch')
    if source < 0 and (parsed is None or parsed >= 0):
        issues.append('label_sign_mismatch')
    if unit and not has_unit(label, unit):
        issues.append('missing_unit')
    if places is None:
        issues.append('source_precision_unavailable')
    elif parsed is not None and -parsed.as_tuple().exponent > places:
        issues.append('unsupported_precision')
    return issues


def delta_issues(label, b, a, unit, places=1, direction='Test − control'):
    issues = []
    if num(label) != decimal_delta(b, a):
        issues.append('delta_mismatch')
    if direction not in label:
        issues.append('delta_direction_missing')
    if not has_unit(label, unit):
        issues.append('delta_unit_missing')
    precision_codes=value_issues(label,decimal_delta(b,a),'',places)
    issues.extend(code for code in precision_codes if code in ('source_precision_unavailable','unsupported_precision'))
    return issues


def tick_label_issues(label, location, unit):
    """Check these fixtures' plain numeric ticks, not arbitrary formatter syntax.

    Unlike value labels, tick decimals do not imply measurement precision. Bare
    numbers inherit the non-percent fixture's caption; percent ticks show %.
    """
    match = re.fullmatch(r'\s*(' + NUMBER.pattern + r')\s*(%|[A-Za-z]+)?\s*', label)
    if match is None:
        return ['numeric_tick_label_invalid']
    value = Decimal(match.group(1).replace('−', '-'))
    suffix = match.group(2) or ''
    issues = []
    if not math.isclose(float(value), float(location), rel_tol=1e-9, abs_tol=1e-9):
        issues.append('numeric_tick_value_mismatch')
    allowed_units = {'%'} if unit == '%' else {'', unit}
    if unit == 's':
        allowed_units.add('seconds')
    if suffix not in allowed_units:
        issues.append('numeric_tick_unit_mismatch')
    return issues


def text_clipping_issues(artist, renderer):
    """Conservatively bound text clipping; path bounds cannot prove containment."""
    if not artist.get_clip_on():
        return []
    issues = []
    bounds = artist.get_window_extent(renderer)
    clip_box = artist.get_clip_box()
    if clip_box is not None and not valid_text_clip_box(clip_box):
        issues.append('clip_box_unsupported')
    elif clip_box is not None and not (
            clip_box.x0 <= bounds.x0 + 0.5 and clip_box.y0 <= bounds.y0 + 0.5
            and clip_box.x1 >= bounds.x1 - 0.5 and clip_box.y1 >= bounds.y1 - 0.5):
        issues.append('clipped')
    clip_path, _ = artist.get_transformed_clip_path_and_affine()
    if clip_path is not None:
        issues.append('clip_path_unsupported')
    return issues


def valid_text_clip_box(box):
    return (all(math.isfinite(float(value)) for value in box.extents)
            and box.x0 <= box.x1 and box.y0 <= box.y1)


def text_collision_bounds(artist, bounds, canvas):
    """Conservative visible bounds, not a glyph-coverage or occlusion test."""
    if artist.get_clip_on():
        clip_path, _ = artist.get_transformed_clip_path_and_affine()
        if clip_path is not None:
            return None  # The audit rejects the path; do not invent visible ink.
        clip_box = artist.get_clip_box()
        if clip_box is not None:
            if not valid_text_clip_box(clip_box):
                return None
            bounds = Bbox.intersection(bounds, clip_box)
    if bounds is not None:
        bounds = Bbox.intersection(bounds, canvas)
    if bounds is None or bounds.width <= 0 or bounds.height <= 0:
        return None
    return bounds


def numeric_axis_issues(axis, orientation, unit, visible_texts, renderer):
    """Audit drawn tick text for the fixtures' linear, unscaled numeric axes.

    Major tick spacing is flexible, with at least two distinct in-range ticks.
    Unlabeled minor ticks and ticks outside the view are not drawn labels.
    Separate formatter offsets/scientific multipliers and arbitrary tick-label
    clip paths are explicitly unsupported.
    """
    dimension = axis.yaxis if orientation == 'v' else axis.xaxis
    limits = axis.get_ylim() if orientation == 'v' else axis.get_xlim()
    issues = []
    if not axis.axison or not axis.get_visible() or not dimension.get_visible():
        return [('numeric_axis_not_visible', orientation)]
    if dimension.get_scale() != 'linear':
        issues.append(('numeric_axis_scale_unsupported', dimension.get_scale()))
    offset = dimension.get_offset_text()
    if artist_visible(offset):
        issues.append(('numeric_axis_offset_unsupported', offset.get_text()))
    in_view = lambda tick: min(limits) - 1e-9 <= tick.get_loc() <= max(limits) + 1e-9
    major = [tick for tick in dimension.get_major_ticks() if in_view(tick)]
    if len({tick.get_loc() for tick in major}) < 2:
        issues.append(('numeric_tick_count_mismatch', {'minimum': 2, 'actual': len(major)}))
    inherited_units = False
    for ticks, required in ((major, True), (dimension.get_minor_ticks(), False)):
        for tick in ticks:
            if not in_view(tick):
                continue
            labels = [label for label in (tick.label1, tick.label2)
                      if tick.get_visible() and artist_visible(label)]
            if required and not labels:
                issues.append(('numeric_tick_not_visible', float(tick.get_loc())))
            for label in labels:
                for code in text_clipping_issues(label, renderer):
                    issues.append(('numeric_tick_' + code, float(tick.get_loc())))
                coordinate = 1 if orientation == 'v' else 0
                position = label.get_transform().transform(label.get_position())[coordinate]
                point = (0, tick.get_loc()) if orientation == 'v' else (tick.get_loc(), 0)
                expected_position = axis.transData.transform(point)[coordinate]
                if not math.isclose(position, expected_position, abs_tol=0.1, rel_tol=0):
                    issues.append(('numeric_tick_position_mismatch', float(tick.get_loc())))
                text = label.get_text()
                for code in tick_label_issues(text, tick.get_loc(), unit):
                    issues.append((code, {'label': text, 'location': float(tick.get_loc())}))
                if re.fullmatch(r'\s*' + NUMBER.pattern + r'\s*', text):
                    inherited_units = True
    # These known captions supply the units for the otherwise bare numeric ticks.
    caption = {'units': 'Illustrative change, in units',
               's': 'Illustrative elapsed time, in seconds'}.get(unit)
    if inherited_units and caption and not any(
            artist.get_text() == caption and not text_clipping_issues(artist, renderer)
            for artist in visible_texts):
        issues.append(('numeric_axis_unit_context_missing', caption))
    return issues


def png_dimensions(path):
    """Read actual saved PNG dimensions without an OCR or image-reader dependency."""
    with Path(path).open('rb') as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise ValueError('Not a PNG with an IHDR header')
    return struct.unpack('>II', header[16:24])


def setup(width,height,title,subtitle):
    # Round upward by one float ULP so 410/100 does not rasterize as 409 px.
    fig=plt.figure(figsize=(math.nextafter(width/DPI, math.inf),
                            math.nextafter(height/DPI, math.inf)),dpi=DPI,facecolor='white')
    fig.text(24/width,1-22/height,title,fontsize=13.68,weight='bold',va='top',color=INK)
    fig.text(24/width,1-60/height,subtitle,fontsize=FONT,va='top',color=INK,linespacing=1.35)
    return fig

def axis_at(fig,left,bottom,width,height):
    W,H=fig.get_size_inches()*DPI
    ax=fig.add_axes([left/W,bottom/H,width/W,height/H])
    ax.tick_params(length=0,pad=7,labelsize=FONT,colors=INK)
    ax.set_axisbelow(True)
    return ax

def text(ax,x,y,s,**kw): return ax.text(x,y,s,color=INK,fontsize=FONT,**kw)
def note(fig,s,y=18):
    W,H=fig.get_size_inches()*DPI
    return fig.text(24/W,y/H,s,fontsize=FONT,color=INK,va='bottom',linespacing=1.3)

def annotate(ax,x,y,s,offset=(0,6),ha='center',va='bottom'):
    return ax.annotate(s,(x,y),xytext=offset,textcoords='offset pixels',ha=ha,va=va,fontsize=FONT,color=INK)

def rect_intersects(a,b,minimum=0.5):
    return min(a.x1,b.x1)-max(a.x0,b.x0)>minimum and min(a.y1,b.y1)-max(a.y0,b.y0)>minimum

def artist_visible(artist):
    """Bounded visibility check: attached, shown, and nontransparent, including parents.

    This is not an OCR/contrast/occlusion test; rendered bounds are checked separately.
    """
    figure=artist.get_figure()
    if figure is None or not figure.get_visible() or not artist.get_visible():
        return False
    if artist.axes is not None and not artist.axes.get_visible():
        return False
    if artist.get_alpha()==0:
        return False
    if isinstance(artist,Text):
        return bool(artist.get_text().strip()) and to_rgba(artist.get_color(),artist.get_alpha())[3]>0
    return True


def bar_artist_issues(fig, bar, axis, orientation, source_value):
    """Audit these fixtures' filled, axis-aligned rectangular bars in display space.

    Raw Rectangle dimensions alone do not establish the rendered baseline or
    extent. Bounds describe the actual visible fill, not edge strokes, contrast,
    occlusion, or the semantic association with a category/series.
    """
    issues = []
    detail = {'source': source_value, 'orientation': orientation}
    def problem(code):
        issues.append(('bar_' + code, detail))

    attached = (artist_visible(bar) and axis in fig.axes and bar.axes is axis
                and bar in axis.patches)
    if not attached:
        problem('not_visible')
    if (not isinstance(bar, Rectangle) or bar.get_path_effects() or bar.get_animated()
            or bar.get_sketch_params() is not None or bar.get_agg_filter() is not None
            or not bar.get_transform().is_affine):
        problem('artist_unsupported')
        return issues, None
    path = bar.get_path()
    # Rectangle's standard unit path, before its patch and artist transforms.
    if (path.vertices.tolist() != [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
            or path.codes is None or path.codes.tolist() != [1, 2, 2, 2, 79]):
        problem('artist_unsupported')
        return issues, None
    points = bar.get_transform().transform(path.vertices[:4])
    if not all(math.isfinite(float(v)) for point in points for v in point):
        problem('artist_unsupported')
        return issues, None
    coordinate = 1 if orientation == 'v' else 0
    cross = 1 - coordinate
    base_indices, tip_indices = ((0, 1), (3, 2)) if orientation == 'v' else ((0, 3), (1, 2))
    base, tip = points[list(base_indices)], points[list(tip_indices)]
    close = lambda a, b: math.isclose(float(a), float(b), abs_tol=0.1, rel_tol=0)
    # Fail closed for rotation/shear, rather than interpreting a bounding box as
    # the rectangle's value edge. Cross-axis position is intentionally not graded.
    if (not close(base[0][coordinate], base[1][coordinate])
            or not close(tip[0][coordinate], tip[1][coordinate])
            or any(not close(a[cross], b[cross]) for a, b in zip(base, tip))):
        problem('artist_unsupported')
        return issues, None
    zero_point = axis.transData.transform((0, 0))[coordinate]
    value_point = axis.transData.transform((0, float(source_value)) if orientation == 'v'
                                          else (float(source_value), 0))[coordinate]
    # A reflection can reverse path winding without changing the filled bar.
    # Identify the zero/value edges by their numeric direction, not vertex order.
    if (tip[0][coordinate] - base[0][coordinate]) * (value_point - zero_point) < 0:
        base, tip = tip, base
    if any(not close(point[coordinate], zero_point) for point in base):
        problem('baseline_pixel_mismatch')
    if any(not close(point[coordinate], value_point) for point in tip):
        problem('extent_pixel_mismatch')
    face = bar.get_facecolor()
    fill_visible = (bar.get_fill() and math.isfinite(float(face[3])) and face[3] > 0
                    and abs(float(base[0][cross] - base[1][cross])) > 0
                    and abs(float(base[0][coordinate] - tip[0][coordinate])) > 0)
    if not fill_visible:
        problem('fill_not_visible')
    bounds = Bbox.from_extents(min(p[0] for p in points), min(p[1] for p in points),
                              max(p[0] for p in points), max(p[1] for p in points))
    clips = [fig.bbox]  # The canvas clips even when artist clipping is disabled.
    if bar.get_clip_on():
        clip_path, _ = bar.get_transformed_clip_path_and_affine()
        if clip_path is not None:
            problem('clip_path_unsupported')
            return issues, None
        if bar.get_clip_box() is not None:
            clips.append(bar.get_clip_box())
    for clip in clips:
        if (not all(math.isfinite(float(v)) for v in clip.extents)
                or clip.x1 < clip.x0 or clip.y1 < clip.y0):
            problem('clip_box_unsupported')
            return issues, None
        if not (clip.x0 <= bounds.x0 + 0.5 and clip.y0 <= bounds.y0 + 0.5
                and clip.x1 >= bounds.x1 - 0.5 and clip.y1 >= bounds.y1 - 0.5):
            problem('clipped')
        bounds = Bbox.intersection(bounds, clip)
        if bounds is None:
            return issues, None
    return issues, bounds if attached and fill_visible else None


def uncertainty_issues(fig, kind, bars, source):
    """Inspect these fixtures' actual capped, solid, single-segment error bars.

    Source intervals are independent of renderer metadata. Bounds come from the
    attached stem/cap artists in display coordinates, never from source endpoints.
    This is a conservative artist-geometry audit, not a pixel/occlusion analysis.
    Unsupported custom shapes/effects/offsets fail closed instead of certifying ink.
    """
    if kind not in ('positive', 'negative'):
        return [], []
    issues, rectangles = [], []
    axis = fig.axes[0]
    vertical = kind == 'positive'
    orientation = 1 if vertical else 0
    cross = 1 - orientation
    expected = []
    for (bar, _, _, _), lo, hi in zip(bars, source['low'], source['high']):
        center = (bar.get_x() + bar.get_width() / 2 if vertical
                  else bar.get_y() + bar.get_height() / 2)
        points = [(center, float(v)) if vertical else (float(v), center) for v in (lo, hi)]
        expected.append(axis.transData.transform(points))
    containers = [container for ax in fig.axes for container in ax.containers
                  if isinstance(container, ErrorbarContainer)]
    if len(containers) != len(source['values']):
        issues.append(('uncertainty_count_mismatch', {'expected': len(source['values']),
                                                     'actual': len(containers)}))
    tracked = {artist for container in containers for artist in container.lines[2]}
    if any(isinstance(artist, LineCollection) and artist not in tracked
           for ax in fig.axes for artist in ax.collections):
        issues.append(('uncertainty_artist_unsupported', 'unregistered line collection'))

    def problem(code, detail):
        issues.append(('uncertainty_' + code, detail))

    def custom_paint(artist):
        return (artist.get_path_effects() or artist.get_animated()
                or artist.get_sketch_params() is not None or artist.get_agg_filter() is not None)

    def finite_points(points, count):
        return len(points) == count and all(len(p) == 2 and all(math.isfinite(float(v)) for v in p)
                                           for p in points)

    def same_points(actual, wanted):
        return any(all(math.isclose(float(a), float(b), abs_tol=0.1, rel_tol=0)
                       for p, q in zip(actual, order) for a, b in zip(p, q))
                   for order in (wanted, wanted[::-1]))

    def record_bounds(artist, points, padding, detail):
        bounds = Bbox.from_extents(min(p[0] for p in points) - padding,
                                   min(p[1] for p in points) - padding,
                                   max(p[0] for p in points) + padding,
                                   max(p[1] for p in points) + padding)
        # The canvas always clips output, even when artist clipping is disabled.
        clip_boxes = [fig.bbox]
        if artist.get_clip_on():
            path, _ = artist.get_transformed_clip_path_and_affine()
            if path is not None:
                problem('clip_path_unsupported', detail)
                return  # No invented collision bounds for an unknown visible portion.
            if artist.get_clip_box() is not None:
                clip_boxes.append(artist.get_clip_box())
        for clip in clip_boxes:
            if not (clip.x0 <= bounds.x0 + 0.5 and clip.y0 <= bounds.y0 + 0.5
                    and clip.x1 >= bounds.x1 - 0.5 and clip.y1 >= bounds.y1 - 0.5):
                problem('clipped', detail)
            bounds = Bbox.intersection(bounds, clip)
            if bounds is None:
                return
        rectangles.append(bounds)

    matched = []
    for index, container in enumerate(containers):
        data_line, caps, stems = container.lines
        if (data_line is not None or len(caps) != 2 or len(stems) != 1
                or container.has_xerr != (not vertical) or container.has_yerr != vertical
                or any(not isinstance(cap, Line2D) for cap in caps)):
            problem('artist_unsupported', {'interval': index, 'reason': 'expected two caps and one stem'})
            continue
        stem = stems[0]
        if not isinstance(stem, LineCollection):
            problem('artist_unsupported', {'interval': index, 'reason': 'stem is not a LineCollection'})
            continue
        artists = [stem, *caps]
        for artist in artists:
            if not artist_visible(artist) or artist.axes is not axis or artist not in axis.get_children():
                problem('not_visible', {'interval': index, 'part': 'stem' if artist is stem else 'cap'})
            if custom_paint(artist):
                problem('artist_unsupported', {'interval': index, 'reason': 'custom paint or animated artist'})
        segments = stem.get_segments()
        offsets = stem.get_offset_transform().transform(stem.get_offsets())
        if (len(segments) != 1 or not finite_points(segments[0], 2)
                or not finite_points(offsets, 1) or any(float(v) != 0 for v in offsets[0])
                or not stem.get_transform().is_affine
                or any(dashes is not None for _, dashes in stem.get_linestyle())):
            problem('artist_unsupported', {'interval': index, 'reason': 'stem shape, offsets, transform or dashes'})
            continue
        points = stem.get_transform().transform(segments[0])
        if not finite_points(points, 2):
            problem('artist_unsupported', {'interval': index, 'reason': 'nonfinite transformed stem'})
            continue
        # Discover association geometrically, so reordering containers is harmless.
        slot = min(range(len(expected)), key=lambda i: abs(
            sum(p[cross] for p in points) / 2 - expected[i][0][cross])) if expected else None
        if slot is None or not same_points(points, expected[slot]):
            problem('geometry_mismatch', {'interval': index, 'part': 'stem', 'bar_index': slot})
        if slot is not None:
            matched.append(slot)
        widths, colors = stem.get_linewidths(), stem.get_edgecolors()
        stem_ink = (len(widths) == 1 and math.isfinite(float(widths[0])) and widths[0] > 0
                    and len(colors) == 1 and colors[0][3] > 0)
        if not stem_ink:
            problem('not_visible', {'interval': index, 'part': 'stem stroke'})
        if stem_ink and artist_visible(stem) and stem.axes is axis and not custom_paint(stem):
            record_bounds(stem, points, float(widths[0]) * fig.dpi / 144,
                          {'interval': index, 'part': 'stem'})
        cap_centers = []
        for cap in caps:
            marker = '_' if vertical else '|'
            # Pinned Matplotlib stores the full MarkerStyle privately; get_marker()
            # alone loses custom marker transforms (for example a rotated cap).
            standard = MarkerStyle(marker)
            actual_marker = cap._marker.get_path().transformed(cap._marker.get_transform())
            standard_marker = standard.get_path().transformed(standard.get_transform())
            standard_shape = (actual_marker.vertices.shape == standard_marker.vertices.shape
                              and (abs(actual_marker.vertices - standard_marker.vertices) < 1e-12).all())
            if (not isinstance(cap.get_marker(), str) or cap.get_marker() != marker or not standard_shape or cap.get_markevery() is not None
                    or cap.get_linestyle() not in ('None', 'none', '', ' ')
                    or not cap.get_transform().is_affine):
                problem('artist_unsupported', {'interval': index, 'reason': 'cap marker, line or transform'})
                continue
            centers = cap.get_transform().transform(cap.get_xydata())
            if not finite_points(centers, 1):
                problem('artist_unsupported', {'interval': index, 'reason': 'expected one finite cap point'})
                continue
            cap_centers.append(centers[0])
            size, edge = cap.get_markersize(), cap.get_markeredgewidth()
            cap_ink = (math.isfinite(size) and size > 0 and math.isfinite(edge) and edge > 0
                       and to_rgba(cap.get_markeredgecolor(), cap.get_alpha())[3] > 0)
            if not cap_ink:
                problem('not_visible', {'interval': index, 'part': 'cap stroke'})
            if cap_ink and artist_visible(cap) and cap.axes is axis and not custom_paint(cap):
                ends = [list(centers[0]), list(centers[0])]
                ends[0][cross] -= size * fig.dpi / 144
                ends[1][cross] += size * fig.dpi / 144
                record_bounds(cap, ends, edge * fig.dpi / 144,
                              {'interval': index, 'part': 'cap'})
        if len(cap_centers) == 2 and slot is not None and not same_points(cap_centers, expected[slot]):
            problem('geometry_mismatch', {'interval': index, 'part': 'caps', 'bar_index': slot})
    if sorted(matched) != list(range(len(source['values']))):
        problem('association_mismatch', {'bar_indices': matched})
    return issues, rectangles


def audit(fig,name,width,height,kind,bars,labels,deltas=(),table=(),selected=None,expected_fail=(),output_dir=None,context=()):
    """Inspect rendered extents plus geometry/source agreement; retain negative controls."""
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    W,H=fig.canvas.get_width_height()
    issues=[]; checks=[]
    def issue(code,detail): issues.append({'code':code,'detail':detail})
    if (W,H) != (width,height):
        issue('canvas_dimension_mismatch',{'actual':[W,H],'requested':[width,height]})
    # Rendered, raster-space text bounding boxes include ticks, titles, notes and tables.
    texts=[]
    text_bounds={}
    canvas=Bbox.from_bounds(0,0,W,H)
    # Matplotlib retains visible Text objects for out-of-range ticks it does not draw.
    # Exclude those from the raster-space audit rather than alleging off-canvas ink.
    undrawn_tick_labels=set()
    for axis in fig.axes:
        for dimension,limits in [(axis.xaxis,axis.get_xlim()),(axis.yaxis,axis.get_ylim())]:
            for tick in dimension.get_major_ticks()+dimension.get_minor_ticks():
                if not min(limits)-1e-9 <= tick.get_loc() <= max(limits)+1e-9:
                    undrawn_tick_labels.update([tick.label1,tick.label2])
    for t in fig.findobj(match=Text):
        if artist_visible(t) and t not in undrawn_tick_labels:
            box=t.get_window_extent(renderer)
            for code in text_clipping_issues(t, renderer):
                issue('text_'+code, {'text':t.get_text()})
            visible_box=text_collision_bounds(t, box, canvas)
            if visible_box is not None:
                texts.append((t,visible_box))
                text_bounds[t]=visible_box
            if box.x0 < -0.5 or box.y0 < -0.5 or box.x1 > W+0.5 or box.y1 > H+0.5:
                issue('text_clipped',{'text':t.get_text(),'bbox':list(map(float,box.extents))})
            px=t.get_fontsize()*DPI/72
            if px < 13.9: issue('small_type',{'text':t.get_text(),'px':px})
    for (a,ab),(b,bb) in itertools.combinations(texts,2):
        if rect_intersects(ab,bb):
            issue('text_collision',{'a':a.get_text(),'b':b.get_text(),
                'intersection_px':[round(min(ab.x1,bb.x1)-max(ab.x0,bb.x0),2),round(min(ab.y1,bb.y1)-max(ab.y0,bb.y0),2)]})
    # Compare against the independent source copy, not artist-supplied metadata.
    source=AUDIT_SOURCE[kind]
    source_values=source['control']+source['test'] if kind=='dense' else source['values']
    axis=fig.axes[0]
    for code, detail in numeric_axis_issues(axis, 'h' if kind=='negative' else 'v',
                                          source['unit'], [t for t, _ in texts], renderer):
        issue(code, detail)
    categories=axis.get_yticklabels() if kind=='negative' else axis.get_xticklabels()
    expected_categories=source['series']*len(source['groups']) if kind=='positive' else source['groups']
    if [artist.get_text() for artist in categories]!=expected_categories:
        issue('category_label_mismatch',{'expected':expected_categories})
    if not axis.get_visible() or any(not artist_visible(artist) for artist in categories):
        issue('category_not_visible',expected_categories)
    expected_context=source['groups'] if kind=='positive' else []
    if kind=='dense':
        expected_context=['Solid: control   Hatched: test','Group','Control','Test','Δ pp',
                          'Δ pp = test − control, percentage points.']
    if len(context)!=len(expected_context): issue('context_count_mismatch',{'expected':len(expected_context)})
    for artist,expected in zip(context,expected_context):
        if not artist_visible(artist): issue('context_not_visible',expected)
        if artist.get_text()!=expected:
            issue('context_label_mismatch',{'expected':expected,'actual':artist.get_text()})
    if len(bars)!=len(source_values): issue('bar_count_mismatch',{'count':len(bars)})
    expected_by_bar={id(record[0]):value for record,value in zip(bars,source_values)}
    max_endpoint_error=0
    bar_fill_bounds=[]
    for bar,axis,orient,declared_value in bars:
        source_value=expected_by_bar.get(id(bar),declared_value)
        if declared_value!=source_value: issue('bar_source_mismatch',{'declared':declared_value,'source':source_value})
        bar_issues, fill_bounds = bar_artist_issues(fig, bar, axis, orient, source_value)
        for code, detail in bar_issues:
            issue(code, detail)
        if fill_bounds is not None:
            bar_fill_bounds.append((fill_bounds, source_value))
        actual=bar.get_height() if orient=='v' else bar.get_width()
        base=bar.get_y() if orient=='v' else bar.get_x()
        if not math.isclose(base,0,abs_tol=1e-9): issue('nonzero_bar_baseline',{'baseline':base,'value':source_value})
        if not math.isclose(actual,float(source_value),abs_tol=1e-9): issue('bar_value_mismatch',{'bar_extent':actual,'source':source_value})
        if actual * float(source_value) < 0: issue('bar_sign_mismatch',{'extent':actual,'source':source_value})
        bbox=bar.get_window_extent(renderer)
        if orient=='v':
            expected=axis.transData.transform((bar.get_x(),float(source_value)))[1]
            actual_end=bbox.y1 if actual>=0 else bbox.y0
            lims=axis.get_ylim()
        else:
            expected=axis.transData.transform((float(source_value),bar.get_y()))[0]
            actual_end=bbox.x1 if actual>=0 else bbox.x0
            lims=axis.get_xlim()
        error=abs(expected-actual_end); max_endpoint_error=max(max_endpoint_error,error)
        if error>0.1: issue('endpoint_pixel_mismatch',{'error_px':error,'source':source_value})
        if not min(lims)<=0<=max(lims): issue('zero_outside_plot',{'limits':list(lims)})
        if not min(lims)<=float(source_value)<=max(lims): issue('bar_outside_plot',{'source':source_value,'limits':list(lims)})
    label_numbers=[]
    if kind!='dense' and len(labels)!=len(source_values): issue('label_count_mismatch',{'count':len(labels)})
    for artist,declared_value,unit,associated_bar in labels:
        source_value=expected_by_bar.get(id(associated_bar),declared_value)
        if declared_value!=source_value: issue('label_source_mismatch',{'declared':declared_value,'source':source_value})
        visible=artist_visible(artist)
        if not visible: issue('label_not_visible',artist.get_text())
        expected_unit=source['unit']
        if kind=='negative' and not unit:
            expected_unit=''  # These horizontal labels inherit the subtitle's unit.
            if not any('units' in artist.get_text() for artist,_ in texts): issue('unit_context_missing','units')
        elif unit!=expected_unit: issue('label_unit_mismatch',{'declared':unit,'source':expected_unit})
        label_numbers.append(str(num(artist.get_text())))
        for code in value_issues(artist.get_text(),source_value,expected_unit,source['decimal_places']):
            issue(code,{'label':artist.get_text(),'source':source_value})
        if not visible: continue  # Removed annotations have no axes transform to measure.
        # Check the link to the intended mark independently of its printed number.
        matches=[record for record in bars if record[0] is associated_bar]
        if len(matches)!=1 or matches[0][3]!=source_value:
            issue('label_association_mismatch',artist.get_text())
        else:
            _,axis,orient,_=matches[0]
            lb=artist.get_window_extent(renderer)
            bb=associated_bar.get_window_extent(renderer)
            label_center=(lb.x0+lb.x1)/2 if orient=='v' else (lb.y0+lb.y1)/2
            bar_center=(bb.x0+bb.x1)/2 if orient=='v' else (bb.y0+bb.y1)/2
            if abs(label_center-bar_center)>2:
                issue('label_association_mismatch',{'label':artist.get_text(),'offset_px':abs(label_center-bar_center)})
    expected_delta_count=len(source['groups']) if kind=='positive' else int(name=='rounding_repaired')
    if len(deltas)!=expected_delta_count:
        issue('delta_count_mismatch',{'expected':expected_delta_count,'actual':len(deltas)})
    for index,(artist,b,a,unit) in enumerate(deltas):
        if 2*index+1>=len(source_values): continue  # Count mismatch already reported.
        if not artist_visible(artist): issue('delta_not_visible',artist.get_text())
        expected_a,expected_b=source_values[2*index:2*index+2]
        if (a,b)!=(expected_a,expected_b): issue('delta_source_mismatch',{'a':a,'b':b})
        expected_unit='pp' if source['unit']=='%' else source['unit']
        for code in delta_issues(artist.get_text(),expected_b,expected_a,expected_unit,source['decimal_places']):
            issue(code,{'label':artist.get_text(),'expected':str(decimal_delta(b,a))})
    interval_issues, interval_rects = uncertainty_issues(fig, kind, bars, source)
    for code, detail in interval_issues:
        issue(code, detail)
    for artist,source_value,unit,associated_bar in labels:
        if not artist_visible(artist): continue
        lb=text_bounds.get(artist)
        if lb is None: continue
        for ib in interval_rects:
            if rect_intersects(lb,ib): issue('label_uncertainty_collision',{'label':artist.get_text(),'source':source_value})
        # Outside labels must also avoid unrelated bars at the inspected size.
        for bounds,value in bar_fill_bounds:
            if rect_intersects(lb,bounds):
                issue('label_bar_collision',{'label':artist.get_text(),'bar_source':value})
    for row_index,(row,expected) in enumerate(table):
        for cell_index,artist in enumerate(row):
            if not artist_visible(artist):
                issue('table_cell_not_visible',{'row':row_index,'column':cell_index,'text':artist.get_text()})
        observed=[t.get_text() for t in row]
        if observed!=expected: issue('table_value_mismatch',{'observed':observed,'expected':expected})
    if kind=='dense':
        source=AUDIT_SOURCE['dense']
        expected_rows=[[group,pct(cv),pct(tv),format_delta(tv,cv,source['decimal_places'])]
                       for group,cv,tv in zip(source['groups'],source['control'],source['test'])]
        observed_rows=[[t.get_text() for t in row] for row,_ in table]
        if len(observed_rows)!=len(expected_rows): issue('incomplete_table',{'rows':len(table)})
        if observed_rows!=expected_rows: issue('table_value_mismatch',{'expected_rows':expected_rows})
        if selected is not None:
            expected_bars=[bars[len(source['groups'])+i][0] for i in selected if len(source['groups'])+i<len(bars)]
            observed_bars=[record[3] for record in labels]
            if observed_bars!=expected_bars:
                issue('selected_labels_mismatch',{'expected_indices':selected,'observed_count':len(labels)})
            checks.append(f'{len(labels)} selected endpoint labels and {len(table)} complete exact-value rows')
    path=None
    saved_size=None
    if output_dir is not None:
        path=Path(output_dir)/f'{name}_{width}.png'
        fig.savefig(path,dpi=DPI)  # Never bbox_inches=tight: preserve requested dimensions.
        saved_size=png_dimensions(path)
        if saved_size!=(width,height):
            issue('png_dimension_mismatch',{'actual':list(saved_size),'requested':[width,height]})
    codes=set(i['code'] for i in issues)
    missing=set(expected_fail)-codes
    if expected_fail:
        status='EXPECTED_FAILURE_DETECTED' if not missing else 'NEGATIVE_CONTROL_MISSED'
    else: status='PASS' if not issues else 'UNEXPECTED_FAILURE'
    result={'name':name,'width_px':W,'height_px':H,'requested_size_px':[width,height],
      'png_size_px':list(saved_size) if saved_size else None,'status':status,'kind':kind,
      'text_count':len(texts),'min_text_px':min((t.get_fontsize()*DPI/72 for t,b in texts),default=None),
      'max_endpoint_error_px':max_endpoint_error,'issues':issues,
      'expected_failure_codes':list(expected_fail),'missing_failure_codes':sorted(missing),
      'label_numbers':label_numbers,'checks':checks,'image':str(path) if path else None}
    # Retain exact text and measured bounds for later review.
    result['text_bounds']=[{'text':t.get_text(),'bounds_px':[round(float(n),2) for n in b.extents]} for t,b in texts]
    plt.close(fig)
    return result


def positive(width,fault=None,output_dir=None):
    H=470
    fig=setup(width,H,'Close response rates','Illustrative; same measure and period')
    ax=axis_at(fig,53,140,width-77,240)
    ax.set_ylim(0,65); ax.set_xlim(-0.6,3.6)
    ax.set_yticks(range(0,61,10)); ax.set_yticklabels([f'{v}%' for v in range(0,61,10)])
    if fault=='tickscale': ax.set_yticklabels([f'{v}%' for v in range(7)])
    ax.grid(axis='y',color='#e3e7eb'); ax.axhline(0,color=INK,lw=1)
    xs=[0,.85,2.15,3]; source=SOURCE['positive']; bars=[]; labels=[]; deltas=[]
    for i,(x,v,lo,hi) in enumerate(zip(xs,source['values'],source['low'],source['high'])):
        height=float(v); baseline=0
        if fault=='baseline': baseline=40; height-=40; ax.set_ylim(40,65)
        if fault=='geometry' and i==1: height+=3
        b=ax.bar(x,height,bottom=baseline,width=.64,color=C if i%2==0 else T,
                 edgecolor=INK,lw=.5,hatch=None if i%2==0 else '///')[0]
        bars.append((b,ax,'v',v))
        ax.errorbar(x,float(v),yerr=[[float(v)-float(lo)],[float(hi)-float(v)]],color=INK,capsize=3,lw=1,fmt='none')
        target=float(v) if fault=='uncertainty' else float(hi)
        offset=(0,-7) if fault=='uncertainty' else (0,6)
        s=pct(v)
        if fault=='labelswap' and i<2: s=pct(source['values'][1-i])
        a=annotate(ax,x,target,s,offset)
        labels.append((a,v,'%',b))
    if fault == 'missing_uncertainty':
        for container in list(ax.containers):
            if isinstance(container, ErrorbarContainer):
                container.remove()
    ax.set_xticks(xs); ax.set_xticklabels(['Control','Test','Control','Test'])
    context=[text(ax,x,-.16,group,ha='center',va='top',clip_on=False,transform=ax.get_xaxis_transform())
             for x,group in zip([.425,2.575],source['groups'])]
    for j,x in enumerate([.425,2.575]):
        a,b=source['values'][2*j:2*j+2]
        d=text(ax,x,59,f'Test − control\n{signed(decimal_delta(b,a))} pp',ha='center',va='center',linespacing=1.3)
        deltas.append((d,b,a,'pp'))
    note(fig,'pp = percentage points\nWhiskers: synthetic 95% CI.\nNo significance claim.')
    expected={'baseline':['nonzero_bar_baseline','zero_outside_plot'],
        'geometry':['bar_value_mismatch','endpoint_pixel_mismatch'],
        'uncertainty':['label_uncertainty_collision'],
        'labelswap':['label_value_mismatch'],
        'tickscale':['numeric_tick_value_mismatch'],
        'missing_uncertainty':['uncertainty_count_mismatch']}.get(fault,[])
    return audit(fig,'positive'+('_bad_'+fault if fault else ''),width,H,'positive',bars,labels,deltas,expected_fail=expected,output_dir=output_dir,context=context)


def negative(width,fault=None,output_dir=None):
    H=410
    fig=setup(width,H,'Keep negative values signed','Illustrative change, in units')
    ax=axis_at(fig,93,101,width-117,203)
    ax.set_xlim(-11.8,.5); ax.set_ylim(-.65,3.65); ax.invert_yaxis()
    ax.set_xticks([-10,-5,0]); ax.grid(axis='x',color='#e3e7eb'); ax.axvline(0,color=INK,lw=1)
    source=SOURCE['negative']; bars=[]; labels=[]
    for y,(v,lo,hi) in enumerate(zip(source['values'],source['low'],source['high'])):
        b=ax.barh(y,float(v),height=.58,color=C if y%2==0 else T,edgecolor=INK,lw=.5,hatch=None if y%2==0 else '///')[0]
        bars.append((b,ax,'h',v)); ax.errorbar(float(v),y,xerr=[[float(v)-float(lo)],[float(hi)-float(v)]],color=INK,capsize=3,lw=1,fmt='none')
        s=str(Decimal(v)).replace('-','−')
        a=annotate(ax,float(lo),y,s,(-7,0),ha='right',va='center')
        labels.append((a,v,'',b))
    ax.set_yticks(range(4)); ax.set_yticklabels(source['groups'])
    note(fig,'Whiskers: synthetic 95% CI.\nSigns and zero baseline are retained.')
    if fault=='clipping': labels[0][0].set_position((-300,0))
    return audit(fig,'negative'+('_bad_clipping' if fault else ''),width,H,'negative',bars,labels,expected_fail=['text_clipped'] if fault else [],output_dir=output_dir)


def rounding(width,bad=False,output_dir=None):
    H=410
    fig=setup(width,H,'Rounding hides the difference' if bad else 'Preserve reported precision','Illustrative elapsed time, in seconds')
    ax=axis_at(fig,51,83,width-76,224); ax.set_ylim(0,70); ax.set_xlim(-.7,1.7)
    ax.set_yticks(range(0,71,10)); ax.grid(axis='y',color='#e3e7eb'); ax.axhline(0,color=INK,lw=1)
    bars=[]; labels=[]; source=SOURCE['rounding']
    for x,v in enumerate(source['values']):
        b=ax.bar(x,float(v),width=.56,color=C if x==0 else T,edgecolor=INK,lw=.5,hatch=None if x==0 else '///')[0]
        bars.append((b,ax,'v',v)); a=annotate(ax,x,float(v),'51 s' if bad else sec(v)); labels.append((a,v,'s',b))
    ax.set_xticks([0,1]); ax.set_xticklabels(source['groups'])
    deltas=[]
    if bad: note(fig,'Requested values cannot be recovered.\nThis is a deliberate failing fixture.')
    else:
        a=note(fig,'Test − control: +0.2 s\nDifference computed before display rounding.')
        deltas=[(a,source['values'][1],source['values'][0],'s')]
    return audit(fig,'rounding_bad' if bad else 'rounding_repaired',width,H,'rounding',bars,labels,deltas=deltas,expected_fail=['label_value_mismatch'] if bad else [],output_dir=output_dir)


def dense(width,bad=False,output_dir=None):
    H=675
    fig=setup(width,H,'Exact lookup, fewer labels','Illustrative rates; common period')
    ax=axis_at(fig,52,354,width-76,210); ax.set_ylim(0,65); ax.set_xlim(-.65,9.65)
    ax.set_yticks(range(0,61,10)); ax.set_yticklabels([f'{i}%' for i in range(0,61,10)])
    ax.grid(axis='y',color='#e3e7eb'); ax.axhline(0,color=INK,lw=1)
    source=SOURCE['dense']; bars=[]; labels=[]
    for j,(series,offset,color,hatch) in enumerate([('control',-.19,C,None),('test',.19,T,'///')]):
        for i,v in enumerate(source[series]):
            x=i+offset; b=ax.bar(x,float(v),width=.34,color=color,edgecolor=INK,lw=.45,hatch=hatch)[0]
            bars.append((b,ax,'v',v))
            if bad or (series=='test' and i in [2,7]):
                a=annotate(ax,x,float(v),pct(v)); labels.append((a,v,'%',b))
    ax.set_xticks(range(10)); ax.set_xticklabels(source['groups'])
    # Explicit order and glyphs supply series association, independent of colors.
    context=[fig.text(24/width,310/H,'Solid: control   Hatched: test',fontsize=FONT,color=INK)]
    fig.text(24/width,287/H,'Selected test labels; all values below.' if not bad else 'Every bar label added at fixed text size.',fontsize=FONT,color=INK)
    cols=[24, width*.43, width*.64, width-24]
    aligns=['left','right','right','right']; table=[]
    for col,ha,s in zip(cols,aligns,['Group','Control','Test','Δ pp']):
        context.append(fig.text(col/width,254/H,s,ha=ha,fontsize=FONT,weight='bold',color=INK))
    for i,g in enumerate(source['groups']):
        cv,tv=source['control'][i],source['test'][i]; delta=signed(decimal_delta(tv,cv))
        values=[g,pct(cv),pct(tv),delta]; row=[]
        for col,ha,s in zip(cols,aligns,values):
            row.append(fig.text(col/width,(229-i*21)/H,s,ha=ha,fontsize=FONT,color=INK))
        # The audit also reconstructs all rows from its independent source copy.
        expected=[g,pct(source['control'][i]),pct(source['test'][i]),signed(decimal_delta(source['test'][i],source['control'][i]))]
        table.append((row,expected))
    context.append(note(fig,'Δ pp = test − control, percentage points.',y=10))
    return audit(fig,'dense_bad_every_label' if bad else 'dense_selected_with_table',width,H,'dense',bars,labels,table=table,selected=None if bad else [2,7],expected_fail=['text_collision'] if bad else [],output_dir=output_dir,context=context)



def validate_output_directory(path):
    """Keep generated files out of tracked source and the installable skill payload."""
    output=Path(path).expanduser().resolve()
    repository=Path(__file__).resolve().parents[2]
    results=DEFAULT_OUTPUT.parent.resolve()
    if output.is_relative_to(repository) and not output.is_relative_to(results):
        raise ValueError('Write outside the repository or inside evaluation/close-bars/results/')
    return output


def write_report(path, report):
    """Publish complete JSON, never a partially serialized final report."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                dir=path.parent, prefix='.validation-results-', suffix='.tmp',
                delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(report, stream, indent=2, default=float)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def run_fixtures(output_dir):
    """Eight repaired cases and eleven intentionally broken controls, at real sizes."""
    output_dir=validate_output_directory(output_dir)
    renderer_version=load_renderer()
    output_dir.mkdir(parents=True,exist_ok=True)
    report_path = output_dir / 'validation_results.json'
    # Reruns overwrite gallery files in place. Invalidate the old verdict first,
    # so an interrupted run cannot leave it certifying new or mixed artifacts.
    report_path.unlink(missing_ok=True)
    (output_dir/'source_data.json').write_text(json.dumps(SOURCE,indent=2)+'\n')
    results=[]
    for width in (640,360):
        results.extend([positive(width,output_dir=output_dir),
                        negative(width,output_dir=output_dir),
                        rounding(width,bad=True,output_dir=output_dir),
                        rounding(width,output_dir=output_dir),
                        dense(width,output_dir=output_dir),
                        dense(width,bad=True,output_dir=output_dir)])
    for fault in ('baseline','geometry','uncertainty','labelswap','tickscale','missing_uncertainty'):
        results.append(positive(360,fault,output_dir=output_dir))
    results.append(negative(360,'clipping',output_dir=output_dir))
    for result in results:
        print(result['name'],result['width_px'],result['status'],
              sorted({issue['code'] for issue in result['issues']}))
    counts=dict(Counter(result['status'] for result in results))
    report={'scope':'Synthetic implementation fixtures; not model-behavior or comprehension evaluations.',
            'renderer':{'matplotlib':renderer_version,'backend':'Agg','dpi':DPI,'font':'DejaVu Sans'},
            'counts':counts,'results':results}
    write_report(report_path, report)
    print(json.dumps(counts,indent=2))
    return results


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=DEFAULT_OUTPUT,
                        help='Generated PNGs and JSON (default: evaluation/close-bars/results/rendered)')
    args=parser.parse_args(argv)
    try:
        results=run_fixtures(args.output_dir)
    except (OSError,ValueError,RuntimeError) as exc:
        parser.exit(2,f'{exc}\n')
    return int(any(result['status'] not in ('PASS','EXPECTED_FAILURE_DETECTED') for result in results))


if __name__=='__main__':
    sys.exit(main())
