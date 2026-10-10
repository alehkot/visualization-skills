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

## Check whether a close comparison can be read

For values or small differences the task requires, check whether labels, ticks, or associated content let the reader recover them. Coarse ticks and absent direct labels are not intrinsically defective: broad-pattern reading or an adequate table may need no repair.

If the comparison is left to estimation, suggest source-backed labels near the relevant bar ends or a directed, unit-labeled difference. Check source precision, rounding that hides the gap, and percentage points versus relative percent. Do not infer exact values from pixels or add unsupported digits. Correct labels do not cure truncated magnitude bars or establish significance.

On supplied renderings, check label association, collisions, clipping, and conflicts with uncertainty marks at the intended size. Selective labels or an associated table may avoid crowding. Do not claim placement or legibility defects from an unrendered brief.

## Check uncertainty and aggregation without inventing analysis

Identify what an interval means before judging it: spread among observations, uncertainty about a parameter, or predicted future variation. The label should match the source. An unexplained range is not automatically a confidence interval; missing interval metadata is a verification limit unless the artifact makes a conflicting claim.

Do not infer significance solely from whether two separate error bars overlap. Evaluate the comparison the source actually supplies. If a forecast is displayed as an observed outcome, or a best estimate as a guarantee, identify that overstatement directly.

Check whether aggregation hides information required for the question: changing subgroup composition, paired changes, skew, or a relevant tail. Do not demand raw data on every summary chart. A faithful summary can be sufficient for a summary question; detailed analysis may be needed for a different inference.

Missing data should not silently become zero. A connecting segment may indicate interpolation, a modeled trajectory, or merely a link between observations. Read the stated convention before alleging a false observation.

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

- [data.europa.eu, Grids versus data labels](https://data.europa.eu/apps/data-visualisation-guide/grids-versus-data-labels-in-bar-charts) recommends end-of-bar values for direct lookup. [ONS rounding guidance](https://service-manual.ons.gov.uk/content/numbers/rounding) balances readability with task-relevant precision. These are authored guidance, not tests of this skill or rules to label every mark.
- [Heer and Bostock, Crowdsourcing Graphical Perception](https://idl.uw.edu/papers/crowdsourcing-graphical-perception) studies particular comparison judgments, not an all-purpose ranking of finished charts.
- [Wilke, Proportional ink](https://clauswilke.com/dataviz/proportional-ink.html) and [Visualizing uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html) provide authored guidance on quantitative marks and uncertainty displays.
- [Munzner's nested validation model](https://www.cs.ubc.ca/labs/imager/tr/2009/NestedModel/) motivates separating data/task assumptions from representation and implementation checks.
- [Böcherer-Linder and Eichler, How to Improve Performance in Bayesian Inference Tasks](https://pmc.ncbi.nlm.nih.gov/articles/PMC6401595/) studies visual representations of sets and subsets in undergraduate calculation tasks. It informs the reference-group check, not a requirement to use one chart type or a measured benefit of this review skill.

The inspection procedures, rainfall, close-bar, and visitor examples are original applications. A passed inspection does not establish statistical validity of an unavailable analysis or measured reader comprehension.
