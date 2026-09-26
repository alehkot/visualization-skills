# Quantitative explanations

Use this reference when quantities, comparisons, distributions, or uncertainty determine the reader's conclusion. Establish what the numbers mean before selecting their visual encoding.

## Define the comparison before the chart

For each consequential quantity, identify the measure, unit, population, time basis, aggregation, and denominator where applicable. Record whether it is an observation, estimate, forecast, target, or example. These distinctions need not become a verbose data dictionary in the output, but they must survive the handoff.

Check that compared values answer the same question. Total activity and activity per participant are both legitimate measures; neither is interchangeable with the other. A change in total can reflect a changed population as well as a changed rate. Different periods or measurement definitions may prevent a direct ranking.

If the task asks for a derived quantity, compute it only from compatible inputs and label the derivation. Do not infer missing counts from rounded percentages when several counts could fit. A source's approximation should not become a more precise label because the chart has room for decimals.

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

## Preserve variation and uncertainty

Determine whether an interval describes variation among observations, uncertainty about a parameter, or a range of future outcomes. These answer different questions. Name the interval type and level when supplied; otherwise retain the source's wording and flag the missing definition. Do not relabel an unexplained range as a confidence interval.

Show the distribution when its shape, tails, or subgroups are necessary to the question. A mean is not a typical individual in every distribution. Conversely, a simple labeled estimate can suffice when the task only asks for that reported estimate and no stronger inference is invited.

When comparing estimates, a visually larger center is not by itself an established difference in the underlying populations. An interval-overlap shortcut is not a substitute for the relevant comparison or statistical analysis. Keep limitations near a headline that would otherwise imply certainty.

Missing observations are not zero. If a line spans unobserved periods, explain whether the segment merely connects observations or represents a model. If uncertainty is absent from the source, identify that limitation rather than fabricating error bars or declaring the value false.

## Worked example: rate versus count

Invented survey results show that **18 of 60** visitors used an audio guide in the morning, versus **12 of 20** in the afternoon.

For “When was uptake higher?”, the relevant comparison is **30% versus 60%**, with the counts retained. Recommend two aligned rate marks and labels “18/60 visitors” and “12/20 visitors.” A headline can say “A larger share used the guide in the afternoon in this survey.” The sample does not by itself establish a persistent time-of-day effect.

For “When were more guides used?”, the relevant values are **18 versus 12**. A count chart is correct. It becomes misleading only if the explanation uses that count comparison to claim a higher uptake rate. The form follows the question, not a blanket preference for normalization.

## Basis and limits

- [Heer and Bostock, Crowdsourcing Graphical Perception](https://idl.uw.edu/papers/crowdsourcing-graphical-perception) studies specific perceptual judgments. Use its results to inform comparable tasks, not to certify whole-chart understanding.
- [Wilke, Proportional ink](https://clauswilke.com/dataviz/proportional-ink.html) discusses how filled marks imply magnitude. [Visualizing uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html) distinguishes uncertainty displays and their interpretation. These are authored textbook guidance, not evaluations of this skill.
- [Hullman, Why Authors Don't Visualize Uncertainty](https://mucollective.northwestern.edu/project/2019-value-of-uncertainty-vis) investigates practitioner reasoning and barriers; it does not establish that every chart needs the same uncertainty display.

The survey and decision procedure are original teaching material. They do not replace statistical analysis when a requested inference requires it.
