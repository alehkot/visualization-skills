# Quantitative review

Use this reference when a finding depends on a number, scale, plotted mark, aggregation, comparison, or expression of uncertainty. Distinguish an incorrect value from an incorrect encoding and an unsupported inference.

## Verify the quantity being compared

Trace consequential values to their source when supplied. Check units, population, denominator, period, aggregation, and whether the value is observed, estimated, projected, or a target. A correct transcription can still support a false comparison if the contexts differ.

Recompute a consequential transformation when the inputs support it. A percentage-point difference and a relative percentage change answer different questions. Averaging group percentages without the required weights may change the total. Do not calculate an apparently precise correction from missing or rounded inputs.

Check whether the headline makes a stronger claim than the values. A higher total need not imply a higher individual rate; a higher sample average need not imply every individual improved. Report the specific unsupported inference rather than demanding a particular replacement chart.

## Check which group a percentage is about

Read a consequential conditional percentage as “Among [reference group], what share [has the property]?” Compare the source's reference group, the artifact's labels and highlighted marks, and the group named in its headline. Reversing the property and reference group generally changes the denominator even when the numerator stays the same.

When supplied joint counts or compatible rates determine the requested ratio, reconstruct its numerator and full denominator. Include every relevant subgroup, not only the successful, selected, or highlighted branch. Check row versus column totals in a table and which parent group a branch percentage refers to. If the denominator is zero, the share is undefined; do not accept or repair it to 0%.

Do not assume that the reverse conditional determines the requested share. If the evidence leaves that share unresolved, identify the missing support and distinguish an unverified value from one the evidence rules out. A known empty intersection can refute a claimed positive share; replacing it with 0% also requires a known nonempty denominator. Otherwise, do not invent a replacement percentage or declare an independently supported label false. An explicitly hypothetical “per 1,000” population is a legitimate explanatory device when the supplied rates support it. It must not be presented as an observed sample or add unsupported precision. A correctly scoped conditional percentage does not need its reverse displayed unless the reader's task requires it.

## Inspect marks independently of labels

For an actual rendering, compare mark positions and extents with the stated scale. Use a clear view or available geometry when needed. Do not invent exact pixel measurements from a fuzzy screenshot.

| Encoding | Check | Avoid a false alarm |
| --- | --- | --- |
| Bar length | Baseline, direction, proportional extent, negative values | A clearly identified interval or range bar is not necessarily a magnitude-from-zero bar. |
| Points or lines | Axis mapping, time spacing, missing intervals, connections | A clearly labeled restricted range is not inherently misleading. |
| Area or volume | Which dimension represents the number | A categorical icon need not have a quantitative area relationship. |
| Multiple panels | Comparable units, scales, ordering, and time windows | Different scales can be intentional for within-panel shape, provided cross-panel magnitude is not implied. |
| Partitioned or flow displays | Defined whole, overlaps, accounting boundaries, known quantities | A qualitative flow need not have measured widths if it does not claim to encode amounts. |

A nonzero origin can distort magnitude bars even when the tick labels are correct. But a blanket “start every axis at zero” repair can conceal meaningful variation in an appropriate line or dot display. Identify what the encoding asks the reader to compare.

A break, inset, transformation, or schematic view needs enough disclosure to support its intended use. Disclosure is not a universal cure: a small footnote cannot make a prominently false ratio true.

## Check the inference across independent axes

Identify which series uses each axis, its units and range, and whether the axes are independent or linked by a fixed conversion. Correctly plotted points on their own axes can still invite an invalid cross-series comparison. Check a claim of equality, overtaking, relative magnitude, or faster growth against the actual values and intended measure of change, not screen height, crossings, or line angle. Independent ranges can change those visual relationships. Positive linear rescaling does not change the underlying correlation coefficient; visual overlap alone is not a statistical or causal analysis.

Tie a finding to the affected claim or required reader judgment rather than rejecting every second axis. A shared scale may repair comparable magnitudes; separate aligned panels may preserve timing for distinct quantities. A common-base index can answer relative change if its baseline and ratio interpretation are valid, but cannot preserve the original magnitude question. Explicit units and series-to-axis labels help association; they do not make a contradicted headline true.

Accept a correctly linked conversion axis, such as Celsius/Fahrenheit, when corresponding values occupy the same positions. An independent-axis display scoped to timing can also be legitimate without claims about cross-series height or slope. If source values or axis mappings are unavailable, state what cannot be checked; do not invent ranges or report measured geometry from an unrendered brief.

## Worked example: correct points, false overtaking

An invented brief supplies **A: 40 then 60 orders**, **B: 900 then 700 orders**, linear axes **0–100 for A** and **0–2,000 for B**, and the headline “A overtook B.” The specified fractional heights are **0.40 → 0.60** for A and **0.45 → 0.35** for B. Their connecting segments cross, but **40 < 900** and **60 < 700**: the headline is contradicted at the supplied observations. With B's maximum instead **1,000**, its heights are **0.90 → 0.70** and the segments no longer cross. Identify the scale-dependent inference; do not claim the underlying observations or correlation changed.

A repair can use a shared order scale and source-backed values for the magnitude comparison. The control claim “A rose while B fell” is supported by these two observations. Neither version establishes intermediate-month values. Another control is one temperature series with correctly matched **0–100°C** and **32–212°F** scales, including **50°C = 122°F**. Its second axis is a conversion, not an independent-scale defect. With no rendering, these are checks of the supplied specification, not evidence of actual tick placement or legibility.

## Check whether a close comparison can be read

For values or small differences the task requires, check whether labels, ticks, or associated content let the reader recover them. Coarse ticks and absent direct labels are not intrinsically defective: broad-pattern reading or an adequate table may need no repair.

If the comparison is left to estimation, suggest source-backed labels near the relevant bar ends or a directed, unit-labeled difference. Check source precision, rounding that hides the gap, and percentage points versus relative percent. Do not infer exact values from pixels or add unsupported digits. Correct labels do not cure truncated magnitude bars or establish significance.

On supplied renderings, check label association, collisions, clipping, and conflicts with uncertainty marks at the intended size. Selective labels or an associated table may avoid crowding. Do not claim placement or legibility defects from an unrendered brief.

## Check subgroup comparisons and the overall mix

When the headline crosses between overall and subgroup rates, compare like-defined groups and recover the reported overall proportions where compatible counts, or subgroup proportions with denominator shares, permit it. For mutually exclusive groups covering the stated population, the overall proportion is the sum of events divided by the sum of eligible observations. Its weights are denominator shares, not equal weights by default. Check excluded groups, overlapping membership, changed definitions, and incompatible periods before declaring a total wrong.

Inspect both subgroup rates and their denominator shares when explaining an aggregate/subgroup reversal. A true overall increase can coexist with decreases in every subgroup; a truthful overall summary is not an arithmetic error just because its subgroup ranking differs. Flag the unsupported leap, such as “each group improved” or “the service caused the improvement,” rather than replacing a correct total or requiring disaggregation for an unrelated lookup task.

For a common-mix comparison, verify that both sides use the same stated, justified weights and that the chart distinguishes standardized values from observed rates. Missing required weights or subgroup rates are verification limits, not permission to invent weights, impute an empty group's rate as zero, or calculate a precise replacement from rounded labels. A reversal alone does not determine which grouping supports a causal claim. Do not prescribe automatic adjustment for every available variable.

## Worked example: an increase that no subgroup shares

An invented support record uses the same two exhaustive request types and the same resolution definition in both weeks:

| Request type | Week 1 resolved / requests | Week 2 resolved / requests |
| --- | ---: | ---: |
| Routine | 9/10 = 90% | 80/100 = 80% |
| Complex | 60/100 = 60% | 5/10 = 50% |
| Overall | 69/110 ≈ 62.7% | 85/110 ≈ 77.3% |

A brief labels the overall rates correctly but headlines them “Resolution improved for both request types.” That headline is contradicted: both type-specific rates fell by **10 percentage points**, while the mix shifted toward routine requests. A repair preserves the actual overall increase, aligns the two request-type rows and their denominators, and states the distinction. Without a rendering, do not claim measured mark or layout defects.

A control headline, “A larger share of this week's actual requests was resolved,” with the correct overall values and no subgroup or causal claim, is supported. If the request is to compare at a stated illustrative 50/50 mix, **75% then 65%** is valid only as a separately labeled standardized comparison. If only the overall rates are supplied, a reversal within subgroups is not established and must not be invented.

## Check histogram height against bin width

For a numeric-axis histogram, inspect the bin boundaries, axis units, and stated meaning of height and area together. On linear axes, count density times bin width should recover the bin count; probability density times bin width should recover its share of the stated population. Unequal-width bins with raw count heights can distort an area-based distribution comparison. Distinguish a wrong geometry or density label from a correct count answering a different question.

Do not reject a density merely because its height exceeds one or its heights do not sum to one. Check the areas and normalization population instead. Equal-width count histograms, clearly categorical interval-count bars, and count tables can be valid for their stated tasks. A wider interval can contain more observations while having lower average concentration per unit; neither fact establishes an individual-level pattern within that interval.

When widths, counts, or the normalization population are unavailable, state the verification limit instead of inventing corrected heights. Do not repair grouped data by assuming how observations divide across new boundaries. Check excluded ranges and endpoint conventions where they affect the claim. For transformed axes, establish the variable and measure being represented before applying an area test; the linear-coordinate rule is not a screen-pixel test on logarithmic axes.

## Worked example: more observations, lower concentration

An invented source gives **10 arrivals in [0, 5) minutes** and **15 in [5, 20] minutes**. A brief specifies a linear-axis histogram with those widths, count heights **10 and 15**, and the headline “Arrivals are more concentrated per minute from 5 to 20 minutes.” The headline is contradicted by the grouped rates: **10/5 = 2** versus **15/15 = 1 arrival per minute**. For a density comparison, use those heights and name the vertical unit. Their areas recover counts **10 and 15**; the second interval still contains more arrivals overall.

A control table headed “Arrivals in each interval” with **10 and 15**, and no concentration claim, needs no density repair. If only grouped counts are known without interval widths, the concentration comparison remains unverified. Without a rendering, inspect the specified numbers and mapping rather than claiming measured bar geometry.

## Check uncertainty and aggregation without inventing analysis

Identify what an interval means before judging it: spread among observations, uncertainty about a parameter, or predicted future variation. The label should match the source. An unexplained range is not automatically a confidence interval; missing interval metadata is a verification limit unless the artifact makes a conflicting claim.

Do not infer significance solely from whether two separate error bars overlap. Evaluate the comparison the source actually supplies. If a forecast is displayed as an observed outcome, or a best estimate as a guarantee, identify that overstatement directly.

Check whether aggregation hides information required for the question: changing subgroup composition, paired changes, skew, or a relevant tail. Do not demand raw data on every summary chart. A faithful summary can be sufficient for a summary question; detailed analysis may be needed for a different inference.

## Check missingness without inventing observations

Compare the artifact’s coverage with source-established categories and observation schedules. Check both empty values and entirely absent records. A missing timestamp can disappear when remaining points are connected or equally spaced, and an omitted bar can look like an observed zero. Report the specific loss of meaning when the task needs that distinction; preserve true zero values and the source’s status definitions. Unknown blank codes are a verification limit, not automatically zero or missing. Irregular observation dates alone do not establish missing scheduled readings, and an unspecified cause remains unknown.

Read the marks together with their stated convention. A connector may merely join observations, or represent interpolation or a modeled trajectory. Do not demand a break when the source-supported convention and context already preserve the distinction. Conversely, flag an imputed point presented as observed or a line that claims measurements across a known unobserved interval. Recommend explicit status wording, restored time/category context, or a distinct labeled estimate as appropriate, rather than inventing values or enforcing one visual treatment. Preserve isolated observations when a repair breaks their connecting segments.

Check conclusions and derived summaries too: a mean over available records must not silently become a mean over the whole requested period. Missing data can leave a claim unverified without proving its value false. Preserve a valid available-case summary when its scope and denominator answer the question. Without a rendering, review these specified meanings rather than asserting unseen gap visibility or label placement.

## Worked example: a zero-shaped absence

An invented brief specifies monthly counts **May: 8, June: not reported, July: 0**, but draws no bar for either June or July and gives neither a status label nor accompanying values. Readers must distinguish a recorded zero from no report. Keep July’s zero and add an explicit June “not reported” indication, retaining all three months. Do not replace June with 0 or infer its missingness cause.

A control brief already labels both statuses in an associated table and makes no stronger coverage claim. It needs no duplicate marks solely to satisfy a gap rule. If only the artifact is supplied without a source or stated schedule, an absent month is not by itself proof that a record was lost.

## Worked example: inconsistent units

An invented rainfall table reports **North: 12 mm** and **South: 1.5 cm** for the same day. A written bar-chart brief specifies a common axis labeled millimeters, with endpoints **12** and **1.5**, while retaining the original source values in the captions.

The South endpoint is inconsistent with the declared axis: 1.5 cm is 15 mm. Correct captions do not fix that encoding. A minimal repair is to specify an endpoint of 15 on the millimeter axis and label the value consistently. No new measurement or statistical claim is necessary.

A control version uses a table with an explicit unit beside each value and makes no numeric ranking claim. It preserves the source correctly. Converting both values to one unit could make comparison easier, but the mixed-unit table is not automatically a factual defect. If a rendered version is unavailable, do not claim its labels overlap or its bars have measured lengths.

## Worked example: a gap hidden by labels

An invented static-chart brief asks readers to retrieve **control: 51.2 seconds** and **test: 51.4 seconds**, but specifies zero-based bars, 10-second ticks, “51 s” labels, and no accompanying values. Restore “51.2 s” and “51.4 s” at the corresponding bar ends. A control version with an adequate associated value table needs no duplicate labels. Actual placement remains untested without the rendering.

## Worked example: a correct percentage answering the wrong question

An invented survey covers **200 visitors**: **50 attended a workshop**, of whom **40 are local**, and **150 did not**, of whom **60 are local**. A brief shows the correct workshop-group value, **40/50 = 80%**, but labels it “80% of local visitors attended the workshop.”

The label reverses the condition. The local-visitor denominator is **40 + 60 = 100**, so the supported share for that label is **40/100 = 40%**. If the task asks about local visitors' attendance, repair the value and specify the local-visitor comparison group. If the task asks where workshop attendees live, keep 80% and repair the wording to “80% of workshop attendees were local.” The reader's question determines which repair fits.

A control brief already uses the latter wording and clearly associates 40/50 with the workshop group. It has no reversal defect. If the source instead supplies only the 40-of-50 workshop count, a claimed share of all local visitors remains unverified; missing information alone does not establish that it is 40%.

## Return a bounded finding

Name the location, affected comparison, supporting source or internal arithmetic, and smallest repair. Preserve uncertainty and source precision in replacement wording. If the necessary denominator or definition is unavailable, explain what would resolve the concern; do not substitute an invented value.

Accept legitimate conventions and summaries when no material mismatch is established. A preference for dots over bars is not itself evidence that the existing explanation fails.

## Basis and limits

- [ONS's dual-axis critique](https://digitalblog.ons.gov.uk/2019/07/03/dueling-with-axis-the-problems-with-dual-axis-charts/) motivates checking claims separately from faithful point plotting. [Datawrapper's guide](https://www.datawrapper.de/blog/dual-axis-charts-guide) discusses alternatives and valid uses; [Matplotlib's secondary-axis examples](https://matplotlib.org/stable/gallery/subplots_axes_and_figures/secondary_axis.html) show linked conversions. These are guidance and implementation examples, not a behavioral evaluation of this reviewer. The order-series and temperature controls are original arithmetic illustrations.

- [Pearl, Understanding Simpson's Paradox](https://ftp.cs.ucla.edu/pub/stat_ser/r414.pdf) motivates keeping association reversal separate from causal interpretation. [CDC's age-adjustment definition](https://www.cdc.gov/nchs/hus/sources-definitions/age-adjustment.htm) illustrates explicitly weighted standardization. The support-record example is original; these sources do not validate this reviewer or make disaggregation a universal repair.

- [NIST's histogram guidance](https://www.itl.nist.gov/div898/handbook/eda/section3/eda33e.htm) describes the normalization choices. [NumPy's histogram documentation](https://numpy.org/doc/stable/reference/generated/numpy.histogram.html) distinguishes density's unit integral from the sum of heights and documents explicit bin edges. These support the quantitative checks, not a universal plotting convention or a behavioral evaluation of this skill.

- [Song and Szafir, Where’s My Data?](https://cmci.colorado.edu/visualab/papers/song_VIS_2018.pdf) evaluates missing-data displays and imputation in synthetic time-series tasks. The observed tradeoffs motivate checking what missingness communicates, not prescribing one universally superior encoding.
- [D3’s line documentation](https://d3js.org/d3-shape/line#line_defined) explains how supplied undefined points can terminate segments; absent rows need separate consideration. This is implementation evidence, not an evaluation of this review skill.

- [data.europa.eu, Grids versus data labels](https://data.europa.eu/apps/data-visualisation-guide/grids-versus-data-labels-in-bar-charts) recommends end-of-bar values for direct lookup. [ONS rounding guidance](https://service-manual.ons.gov.uk/content/numbers/rounding) balances readability with task-relevant precision. These are authored guidance, not tests of this skill or rules to label every mark.
- [Heer and Bostock, Crowdsourcing Graphical Perception](https://idl.uw.edu/papers/crowdsourcing-graphical-perception) studies particular comparison judgments, not an all-purpose ranking of finished charts.
- [Wilke, Proportional ink](https://clauswilke.com/dataviz/proportional-ink.html) and [Visualizing uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html) provide authored guidance on quantitative marks and uncertainty displays.
- [Munzner's nested validation model](https://www.cs.ubc.ca/labs/imager/tr/2009/NestedModel/) motivates separating data/task assumptions from representation and implementation checks.
- [Böcherer-Linder and Eichler, How to Improve Performance in Bayesian Inference Tasks](https://pmc.ncbi.nlm.nih.gov/articles/PMC6401595/) studies visual representations of sets and subsets in undergraduate calculation tasks. It informs the reference-group check, not a requirement to use one chart type or a measured benefit of this review skill.

The inspection procedures, rainfall, close-bar, visitor, support-record, arrival-interval, and missing-month examples are original applications. A passed inspection does not establish statistical validity of an unavailable analysis or measured reader comprehension.
