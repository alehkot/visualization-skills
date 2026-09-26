# Quantitative review

Use this reference when a finding depends on a number, scale, plotted mark, aggregation, comparison, or expression of uncertainty. Distinguish an incorrect value from an incorrect encoding and an unsupported inference.

## Verify the quantity being compared

Trace consequential values to their source when supplied. Check units, population, denominator, period, aggregation, and whether the value is observed, estimated, projected, or a target. A correct transcription can still support a false comparison if the contexts differ.

Recompute a consequential transformation when the inputs support it. A percentage-point difference and a relative percentage change answer different questions. Averaging group percentages without the required weights may change the total. Do not calculate an apparently precise correction from missing or rounded inputs.

Check whether the headline makes a stronger claim than the values. A higher total need not imply a higher individual rate; a higher sample average need not imply every individual improved. Report the specific unsupported inference rather than demanding a particular replacement chart.

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

## Check uncertainty and aggregation without inventing analysis

Identify what an interval means before judging it: spread among observations, uncertainty about a parameter, or predicted future variation. The label should match the source. An unexplained range is not automatically a confidence interval; missing interval metadata is a verification limit unless the artifact makes a conflicting claim.

Do not infer significance solely from whether two separate error bars overlap. Evaluate the comparison the source actually supplies. If a forecast is displayed as an observed outcome, or a best estimate as a guarantee, identify that overstatement directly.

Check whether aggregation hides information required for the question: changing subgroup composition, paired changes, skew, or a relevant tail. Do not demand raw data on every summary chart. A faithful summary can be sufficient for a summary question; detailed analysis may be needed for a different inference.

Missing data should not silently become zero. A connecting segment may indicate interpolation, a modeled trajectory, or merely a link between observations. Read the stated convention before alleging a false observation.

## Worked example: inconsistent units

An invented rainfall table reports **North: 12 mm** and **South: 1.5 cm** for the same day. A written bar-chart brief specifies a common axis labeled millimeters, with endpoints **12** and **1.5**, while retaining the original source values in the captions.

The South endpoint is inconsistent with the declared axis: 1.5 cm is 15 mm. Correct captions do not fix that encoding. A minimal repair is to specify an endpoint of 15 on the millimeter axis and label the value consistently. No new measurement or statistical claim is necessary.

A control version uses a table with an explicit unit beside each value and makes no numeric ranking claim. It preserves the source correctly. Converting both values to one unit could make comparison easier, but the mixed-unit table is not automatically a factual defect. If a rendered version is unavailable, do not claim its labels overlap or its bars have measured lengths.

## Return a bounded finding

Name the location, affected comparison, supporting source or internal arithmetic, and smallest repair. Preserve uncertainty and source precision in replacement wording. If the necessary denominator or definition is unavailable, explain what would resolve the concern; do not substitute an invented value.

Accept legitimate conventions and summaries when no material mismatch is established. A preference for dots over bars is not itself evidence that the existing explanation fails.

## Basis and limits

- [Heer and Bostock, Crowdsourcing Graphical Perception](https://idl.uw.edu/papers/crowdsourcing-graphical-perception) studies particular comparison judgments, not an all-purpose ranking of finished charts.
- [Wilke, Proportional ink](https://clauswilke.com/dataviz/proportional-ink.html) and [Visualizing uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html) provide authored guidance on quantitative marks and uncertainty displays.
- [Munzner's nested validation model](https://www.cs.ubc.ca/labs/imager/tr/2009/NestedModel/) motivates separating data/task assumptions from representation and implementation checks.

The inspection procedure and rainfall example are original applications. A passed inspection does not establish statistical validity of an unavailable analysis or measured reader comprehension.
