# Quantitative explanations

Use this reference when quantities, comparisons, distributions, or uncertainty determine the reader's conclusion. Establish what the numbers mean before selecting their visual encoding.

## Define the comparison before the chart

For each consequential quantity, identify the measure, unit, population, time basis, aggregation, and denominator where applicable. Record whether it is an observation, estimate, forecast, target, or example. These distinctions need not become a verbose data dictionary in the output, but they must survive the handoff.

Check that compared values answer the same question. Total activity and activity per participant are both legitimate measures; neither is interchangeable with the other. A change in total can reflect a changed population as well as a changed rate. Different periods or measurement definitions may prevent a direct ranking.

If the task asks for a derived quantity, compute it only from compatible inputs and label the derivation. Do not infer missing counts from rounded percentages when several counts could fit. A source's approximation should not become a more precise label because the chart has room for decimals.

## Keep the direction of conditional percentages

Restate a consequential conditional percentage as “Among [reference group], what share [has the property]?” Match that reference group to the reader's question and the proposed headline. “Among faulty parts, the share flagged” and “among flagged parts, the share faulty” refer to the same intersection but different denominators; one percentage does not in general answer both questions.

When the requested direction differs from a supplied percentage, identify the intersection that forms the numerator and the complete reference group that forms the denominator. Use compatible joint counts or rates with enough information to determine that ratio. A count table with explicit row and column totals, or a subset view that brings the required groups together, can make the operation visible. Do not force a particular form or a complete table when a labeled fraction already answers the question.

If the supplied information does not determine the requested ratio, name the missing information rather than reusing the reverse percentage. Do not combine incompatible populations, periods, or category definitions to fill the gap. When rates support an illustrative “per 1,000” explanation, label that population as hypothetical, preserve source precision, and do not present it as an observed sample size. A zero denominator makes the conditional share undefined, not zero.

## Choose an encoding for the required judgment

| Reader needs to see | Candidate structure | Preserve or check |
| --- | --- | --- |
| Rank or compare magnitudes | Aligned dots or bars | Shared units and scale; sort only when meaningful order is not lost. |
| Retrieve exact values | Table or directly labeled marks | Appropriate precision and enough context to interpret each value. |
| Follow change over time | Lines, points, or interval summaries | Actual time spacing, gaps, changing definitions, and observed versus projected segments. |
| Compare variation | Raw points, distributions, quantiles, interval summaries | What each mark summarizes and what detail aggregation removes. |
| Compare paired observations | Connected pairs or change values | Which observations belong together; marginal summaries alone may hide individual change. |
| Show parts of a whole | Partitioned bars, fractions, table | A defined whole, compatible units, and exclusive parts if the display implies a partition. |

Aligned positions often suit precise comparisons. That does not make every other form a defect: a part-to-whole view can answer a different question, and a small table may serve exact lookup better than a chart.

When bar length encodes magnitude, define a meaningful zero baseline. A truncated bar silently changes the represented ratio. A dot plot or line chart may use a restricted range when clearly labeled and appropriate to the task; “all axes start at zero” is not a general rule. Logarithmic scales need explicit labeling and a reason tied to relative or multiplicative differences.

Do not use area, volume, or width casually for emphasis when it also appears to encode a number. If area carries value, doubling a symbol's radius quadruples its area. A qualitative flow should not acquire unsupported quantitative widths. Keep decorative emphasis separate from measured magnitude.

## Make close comparisons readable

When close bars and coarse ticks leave needed values or differences to estimation, specify source-backed labels near the relevant bar ends, clearly associated with category and series. Keep the zero baseline for magnitude bars; finer ticks alone may not resolve the task.

Use consistent units and enough supported precision to preserve the relevant distinction. Compute differences before display rounding when underlying values are available. Do not invent digits from rounded sources or call their difference exact. For “by how much?”, consider a signed difference with its direction and unit explicit. Percentage-point differences are not relative percentage changes; a relative change needs an explicit, nonzero reference. A descriptive gap alone establishes neither significance nor practical importance.

At the intended size, reserve room for labels without colliding with neighbors, uncertainty marks, or plot boundaries. For crowded displays, prefer selected comparison labels or an associated value table over tiny text. Preserve needed values in requested static and nonvisual versions. Broad-pattern tasks and displays with adequate associated values do not require every mark labeled.

## Preserve variation and uncertainty

Determine whether an interval describes variation among observations, uncertainty about a parameter, or a range of future outcomes. These answer different questions. Name the interval type and level when supplied; otherwise retain the source's wording and flag the missing definition. Do not relabel an unexplained range as a confidence interval.

Show the distribution when its shape, tails, or subgroups are necessary to the question. A mean is not a typical individual in every distribution. Conversely, a simple labeled estimate can suffice when the task only asks for that reported estimate and no stronger inference is invited.

When comparing estimates, a visually larger center is not by itself an established difference in the underlying populations. An interval-overlap shortcut is not a substitute for the relevant comparison or statistical analysis. Keep limitations near a headline that would otherwise imply certainty.

Missing observations are not zero. If a line spans unobserved periods, explain whether the segment merely connects observations or represents a model. If uncertainty is absent from the source, identify that limitation rather than fabricating error bars or declaring the value false.

## Worked example: rate versus count

Invented survey results show that **18 of 60** visitors used an audio guide in the morning, versus **12 of 20** in the afternoon.

For “When was uptake higher?”, the relevant comparison is **30% versus 60%**, with the counts retained. Recommend two aligned rate marks and labels “18/60 visitors” and “12/20 visitors.” A headline can say “A larger share used the guide in the afternoon in this survey.” The sample does not by itself establish a persistent time-of-day effect.

For “When were more guides used?”, the relevant values are **18 versus 12**. A count chart is correct. It becomes misleading only if the explanation uses that count comparison to claim a higher uptake rate. The form follows the question, not a blanket preference for normalization.

## Worked example: close test and control bars

An invented report gives comparable rates of **42.1% for control** and **42.4% for test**. With zero-based bars and 10-point ticks, label those reported values near the bar ends; if the task asks for the gap, add “Reported test − control difference: +0.3 percentage points.” Whole-percent labels would hide it. No uncertainty analysis is supplied, so do not claim a proven improvement.

## Worked example: which group does the percentage describe?

In an invented inspection of **1,000 parts**, **100 are faulty** and **900 are sound**. The inspection flags **90 faulty** and **90 sound** parts. These categories cover the same inspected batch.

| Actual condition | Flagged | Not flagged | Total |
| --- | ---: | ---: | ---: |
| Faulty | 90 | 10 | 100 |
| Sound | 90 | 810 | 900 |
| Total | 180 | 820 | 1,000 |

For “What share of faulty parts were flagged?”, use **90/100 = 90%**. For “What share of flagged parts were faulty?”, bring both flagged groups into the denominator: **90/(90 + 90) = 50%**. A brief for the second question can highlight the flagged column and label “90 of 180 flagged parts were faulty in this batch.” Showing only the 90 faulty parts as the reference group would omit half the denominator.

A correctly labeled explanation of the first question need not also teach the second. If only “90% of faulty parts were flagged” were supplied, it would not establish the share faulty among all flagged parts. Preserve that limit rather than inventing the sound-part counts.

## Basis and limits

- [data.europa.eu, Grids versus data labels](https://data.europa.eu/apps/data-visualisation-guide/grids-versus-data-labels-in-bar-charts) recommends end-of-bar values for direct lookup. [ONS rounding guidance](https://service-manual.ons.gov.uk/content/numbers/rounding) balances readability with task-relevant precision. These are authored guidance, not tests of this skill or rules to label every mark.
- [Srinivasan et al., What's the Difference?](https://www.microsoft.com/en-us/research/wp-content/uploads/2018/01/paper2869-camera-ready.pdf) evaluates explicit difference encodings in two-series bar comparisons. It motivates reducing mental subtraction, but did not compare textual annotations; a signed difference label here is a local application, not a proven best format.
- [Heer and Bostock, Crowdsourcing Graphical Perception](https://idl.uw.edu/papers/crowdsourcing-graphical-perception) studies specific perceptual judgments. Use its results to inform comparable tasks, not to certify whole-chart understanding.
- [Wilke, Proportional ink](https://clauswilke.com/dataviz/proportional-ink.html) discusses how filled marks imply magnitude. [Visualizing uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html) distinguishes uncertainty displays and their interpretation. These are authored textbook guidance, not evaluations of this skill.
- [Hullman, Why Authors Don't Visualize Uncertainty](https://mucollective.northwestern.edu/project/2019-value-of-uncertainty-vis) investigates practitioner reasoning and barriers; it does not establish that every chart needs the same uncertainty display.
- [Böcherer-Linder and Eichler, How to Improve Performance in Bayesian Inference Tasks](https://pmc.ncbi.nlm.nih.gov/articles/PMC6401595/) compares five visualizations in calculation tasks with undergraduate students. It motivates exposing the relevant sets and subsets; it does not establish a universally best format or validate this skill.

The survey, close-bar, and inspection examples, and decision procedures are original teaching material. They do not replace statistical analysis when a requested inference requires it.
