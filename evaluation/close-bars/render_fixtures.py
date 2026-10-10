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
from pathlib import Path
import re
import struct
import sys

DPI = 100
FONT = 10.08  # 14 raster pixels at 100 dpi; never reduced for the 360 px view.
C, T, INK = '#b8c4d0', '#2c705f', '#202d38'
DEFAULT_OUTPUT = Path(__file__).resolve().parent / 'results' / 'rendered'
NUMBER = re.compile(r'[+−-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+−-]?\d+)?')


def load_renderer():
    """Import only when rendering is explicitly requested, never on module import."""
    global plt, Text, Bbox, to_rgba
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.text import Text
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


def audit(fig,name,width,height,kind,bars,labels,intervals=(),deltas=(),table=(),selected=None,expected_fail=(),output_dir=None,context=()):
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
            texts.append((t,box))
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
    for bar,axis,orient,declared_value in bars:
        source_value=expected_by_bar.get(id(bar),declared_value)
        if declared_value!=source_value: issue('bar_source_mismatch',{'declared':declared_value,'source':source_value})
        if not artist_visible(bar): issue('bar_not_visible',source_value)
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
    interval_rects=[]
    for axis,orient,x,lo,hi in intervals:
        if orient=='v':
            xp,yl=axis.transData.transform((x,lo)); _,yh=axis.transData.transform((x,hi))
            ib=Bbox.from_extents(xp-5,yl-1,xp+5,yh+1)
        else:
            xl,yp=axis.transData.transform((lo,x)); xh,_=axis.transData.transform((hi,x))
            ib=Bbox.from_extents(xl-1,yp-5,xh+1,yp+5)
        interval_rects.append(ib)
    for artist,source_value,unit,associated_bar in labels:
        if not artist_visible(artist): continue
        lb=artist.get_window_extent(renderer)
        for ib in interval_rects:
            if rect_intersects(lb,ib): issue('label_uncertainty_collision',{'label':artist.get_text(),'source':source_value})
        # Outside labels must also avoid unrelated bars at the inspected size.
        for bar,axis,orient,value in bars:
            if rect_intersects(lb,bar.get_window_extent(renderer)):
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
    ax.grid(axis='y',color='#e3e7eb'); ax.axhline(0,color=INK,lw=1)
    xs=[0,.85,2.15,3]; source=SOURCE['positive']; bars=[]; labels=[]; intervals=[]; deltas=[]
    for i,(x,v,lo,hi) in enumerate(zip(xs,source['values'],source['low'],source['high'])):
        height=float(v); baseline=0
        if fault=='baseline': baseline=40; height-=40; ax.set_ylim(40,65)
        if fault=='geometry' and i==1: height+=3
        b=ax.bar(x,height,bottom=baseline,width=.64,color=C if i%2==0 else T,
                 edgecolor=INK,lw=.5,hatch=None if i%2==0 else '///')[0]
        bars.append((b,ax,'v',v))
        ax.errorbar(x,float(v),yerr=[[float(v)-float(lo)],[float(hi)-float(v)]],color=INK,capsize=3,lw=1,fmt='none')
        intervals.append((ax,'v',x,float(lo),float(hi)))
        target=float(v) if fault=='uncertainty' else float(hi)
        offset=(0,-7) if fault=='uncertainty' else (0,6)
        s=pct(v)
        if fault=='labelswap' and i<2: s=pct(source['values'][1-i])
        a=annotate(ax,x,target,s,offset)
        labels.append((a,v,'%',b))
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
        'labelswap':['label_value_mismatch']}.get(fault,[])
    return audit(fig,'positive'+('_bad_'+fault if fault else ''),width,H,'positive',bars,labels,intervals,deltas,expected_fail=expected,output_dir=output_dir,context=context)


def negative(width,fault=None,output_dir=None):
    H=410
    fig=setup(width,H,'Keep negative values signed','Illustrative change, in units')
    ax=axis_at(fig,93,101,width-117,203)
    ax.set_xlim(-11.8,.5); ax.set_ylim(-.65,3.65); ax.invert_yaxis()
    ax.set_xticks([-10,-5,0]); ax.grid(axis='x',color='#e3e7eb'); ax.axvline(0,color=INK,lw=1)
    source=SOURCE['negative']; bars=[]; labels=[]; intervals=[]
    for y,(v,lo,hi) in enumerate(zip(source['values'],source['low'],source['high'])):
        b=ax.barh(y,float(v),height=.58,color=C if y%2==0 else T,edgecolor=INK,lw=.5,hatch=None if y%2==0 else '///')[0]
        bars.append((b,ax,'h',v)); ax.errorbar(float(v),y,xerr=[[float(v)-float(lo)],[float(hi)-float(v)]],color=INK,capsize=3,lw=1,fmt='none')
        intervals.append((ax,'h',y,float(lo),float(hi)))
        s=str(Decimal(v)).replace('-','−')
        a=annotate(ax,float(lo),y,s,(-7,0),ha='right',va='center')
        labels.append((a,v,'',b))
    ax.set_yticks(range(4)); ax.set_yticklabels(source['groups'])
    note(fig,'Whiskers: synthetic 95% CI.\nSigns and zero baseline are retained.')
    if fault=='clipping': labels[0][0].set_position((-300,0))
    return audit(fig,'negative'+('_bad_clipping' if fault else ''),width,H,'negative',bars,labels,intervals,expected_fail=['text_clipped'] if fault else [],output_dir=output_dir)


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


def run_fixtures(output_dir):
    """Eight repaired cases and nine intentionally broken controls, at real sizes."""
    output_dir=validate_output_directory(output_dir)
    renderer_version=load_renderer()
    output_dir.mkdir(parents=True,exist_ok=True)
    (output_dir/'source_data.json').write_text(json.dumps(SOURCE,indent=2)+'\n')
    results=[]
    for width in (640,360):
        results.extend([positive(width,output_dir=output_dir),
                        negative(width,output_dir=output_dir),
                        rounding(width,bad=True,output_dir=output_dir),
                        rounding(width,output_dir=output_dir),
                        dense(width,output_dir=output_dir),
                        dense(width,bad=True,output_dir=output_dir)])
    for fault in ('baseline','geometry','uncertainty','labelswap'):
        results.append(positive(360,fault,output_dir=output_dir))
    results.append(negative(360,'clipping',output_dir=output_dir))
    for result in results:
        print(result['name'],result['width_px'],result['status'],
              sorted({issue['code'] for issue in result['issues']}))
    counts=dict(Counter(result['status'] for result in results))
    report={'scope':'Synthetic implementation fixtures; not model-behavior or comprehension evaluations.',
            'renderer':{'matplotlib':renderer_version,'backend':'Agg','dpi':DPI,'font':'DejaVu Sans'},
            'counts':counts,'results':results}
    (output_dir/'validation_results.json').write_text(json.dumps(report,indent=2,default=float)+'\n')
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
