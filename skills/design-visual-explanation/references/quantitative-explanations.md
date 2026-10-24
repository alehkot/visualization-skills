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

## Read stacked components between their boundaries

In an ordinary nonnegative additive stack, a component's amount is the difference between its upper and lower boundaries in axis units, not its upper boundary's value. An upper edge can rise while that component shrinks because the components below it grew. Identify the layer and both boundaries before describing its trend. For a zero-based stack covering the whole, the outer top edge represents the total; an interior boundary represents only the subtotal below it. Do not transfer either reading to one component.

For an invented two-period count, **A: 30 → 80** and **B: 50 → 40**, with A below B, B's upper edge rises **80 → 120**. Yet B falls **50 → 40**, or **20%**. “The total grew 50%” is true; “B grew 50%” is not. To explain B's change, use its component values, with associated labels, a separate series view, or another suitable comparison. Keep the stack when total and composition are the task; a shared baseline for every layer is not mandatory.

Preserve what thickness represents: a 100% stack shows shares, not original amounts, and cannot recover those amounts without totals. Centered or diverging stacks need their own stated offset and sign conventions; do not assume their top edge is the net total. Read calibrated values rather than treating raw pixel distances on a transformed axis as amounts. When source values or boundaries are unavailable, retain that limit instead of inventing a component change.

## Keep independent axes from implying a common comparison

Before overlaying quantities, identify each series' unit and axis. Independently chosen ranges can change which line appears higher, where connecting segments cross, and their apparent slopes without changing the data. Do not use those screen relationships to establish equality, overtaking, relative magnitude, or faster growth. Define whether growth means an absolute change or a relative change over the same period, and calculate it from compatible values.

Match the repair to the question: a shared scale for comparable magnitudes, aligned separate panels for distinct quantities, or a stated common-base index for relative change. An index removes original magnitude information; retain the base period and do not index a zero baseline or a measure for which ratios have no useful meaning. Do not silently change the question to make the lines comparable.

A secondary axis can be legitimate. A fixed unit conversion of one measure, such as Celsius to Fahrenheit, must map corresponding values to the same positions across the displayed range. For independent quantities retained to show timing, make series-to-axis association and units explicit and keep the conclusion within that task. Merely adding axis labels does not repair a false magnitude headline. Visual alignment alone establishes neither a statistical association nor causation; changing a positive linear display scale does not change the data's correlation coefficient.

## Worked example: a crossover made by the scale

An invented record gives **A: 40 then 60 orders** and **B: 900 then 700 orders**, over the same two months. With linear ranges **0–100 for A** and **0–1,000 for B**, their fractional heights above the bottom are **0.40 → 0.60** and **0.90 → 0.70**. Change only B's range to **0–2,000** and its heights become **0.45 → 0.35**: the connecting segments now cross, although A has fewer orders at both observations. Do not headline this “A overtook B.” A shared order scale or an explicit value comparison preserves the magnitude question; “A rose while B fell” describes the recorded changes. The segments do not establish what happened between the observations.

As a control, one temperature series with matched **0–100°C** and **32–212°F** axes has a fixed conversion, **°F = 1.8 × °C + 32**. Corresponding ticks, including **50°C = 122°F**, occupy the same positions. This is not two independently scaled series and does not need to be rejected for having a second axis.

## Keep successive percentage changes on their own bases

For a first-to-last change, distinguish consecutive period growth rates from additive contributions. When each rate describes the same comparable quantity relative to its immediately preceding value, combine the growth factors: **(1 + r₁) × (1 + r₂) × … − 1**, with rates written as fractions. Adding the percentages generally gives the wrong net change because their bases differ. For an ordinary unadjusted series, compatible first and last values also give **last / first − 1**, with a nonzero first value and a meaningful ratio interpretation.

Retain each rate's period and definition. Do not chain overlapping year-over-year rates or treat annualized rates as actual changes over their shorter reporting intervals. Missing periods, changed definitions, and rounded rates can prevent an exact reconstruction. Source-adjusted growth may deliberately differ from raw endpoint change; preserve that distinction rather than overriding the source method.

For an invented comparable activity index, **100 → 120 → 96** gives successive changes of **+20% and −20%**, but the last observation is **4% below the first**, not unchanged. A level view can show those three readings. An additive waterfall can instead use the **+20 and −24 index-point changes**; stacking +20% and −20% as if they shared the original base would give a false endpoint. A chart only comparing the two period rates may keep both correct labels without adding a net summary. Percentage-point changes in a percentage-valued series are additive differences, not these relative growth factors. Explicit contributions on a common reference can also add; retain that definition instead of relabeling them as consecutive growth rates.

## Make close comparisons readable

When close bars and coarse ticks leave needed values or differences to estimation, specify source-backed labels near the relevant bar ends, clearly associated with category and series. Keep the zero baseline for magnitude bars; finer ticks alone may not resolve the task.

Use consistent units and enough supported precision to preserve the relevant distinction. Compute differences before display rounding when underlying values are available. Do not invent digits from rounded sources or call their difference exact. For “by how much?”, consider a signed difference with its direction and unit explicit. Percentage-point differences are not relative percentage changes; a relative change needs an explicit, nonzero reference. A descriptive gap alone establishes neither significance nor practical importance.

At the intended size, reserve room for labels without colliding with neighbors, uncertainty marks, or plot boundaries. For crowded displays, prefer selected comparison labels or an associated value table over tiny text. Preserve needed values in requested static and nonvisual versions. Broad-pattern tasks and displays with adequate associated values do not require every mark labeled.

## Separate subgroup performance from population mix

When a comparison could depend on changing subgroup composition, keep three questions separate: what happened across the observed population, what happened within comparable subgroups, and what a comparison under a specified common mix would show. A higher overall rate need not mean higher rates in each subgroup; a subgroup advantage need not imply a higher observed overall rate.

For compatible, mutually exclusive groups covering the stated population, recover the overall proportion as total events divided by total eligible observations. Retain supplied subgroup numerators and denominators alongside their percentages. The denominator shares are the weights; an unweighted mean of subgroup percentages answers a different question unless the denominators are equal. Check that group definitions and coverage match across the compared periods or options. Compatible subgroup proportions and their denominator shares can also determine the pooled proportion without absolute counts. Overlapping groups, missing weights, or rounded rates alone may prevent reconstructing a precise total.

When the task needs the explanation for an aggregate/subgroup disagreement, align the same subgroup rows across the compared options, retain their counts and rates, and show the overall row separately. Make unequal denominator shares visible with labeled counts, a companion composition view, or another explicit cue. Do not silently replace the reported overall rate with the average subgroup rate. A correctly scoped overall summary remains valid for its own question; do not force subgroup detail into every summary.

A common-mix comparison is optional and requires stated, justified weights applied to the same groups on both sides. Label it as standardized to that mix, distinct from observed totals. Do not invent a missing subgroup rate or give an empty subgroup a zero rate. A numerical reversal does not establish cause, and splitting by more variables is not automatically a better causal analysis. Explain the descriptive pattern; defer causal attribution when the source does not justify the grouping or adjustment.

## Worked example: higher in each group, lower overall

An invented delivery record compares two services during the same period. “On time” uses the same definition, and the two route groups partition each service's deliveries.

| Route group | Service A on time / deliveries | Service B on time / deliveries |
| --- | ---: | ---: |
| Local | 9/10 = 90% | 80/100 = 80% |
| Remote | 60/100 = 60% | 5/10 = 50% |
| Overall | 69/110 ≈ 62.7% | 85/110 ≈ 77.3% |

A has the higher rate in both route groups, but most of A's deliveries are remote while most of B's are local. For “Why do the rankings disagree?”, propose aligned subgroup rows with the counts above, plus an overall row and the contrasting route mix. The overall percentages are weighted by **10/110 and 100/110** for A, in the opposite order for B. Averaging the two subgroup rates would give **75% and 65%**, not the observed overall percentages.

For a specifically requested illustrative 50/50 local/remote mix, those **75% and 65%** are valid standardized comparisons; label the assumed mix rather than claiming either was observed. For “What share of each service's actual deliveries arrived on time?”, **62.7% versus 77.3%** is the relevant descriptive answer. Neither view alone proves that changing service would cause a delivery to be on time.

## Do not pool medians or percentiles by averaging them

Distinguish a percentile of all observations from a summary of group percentiles. A median or 95th percentile is a position in an ordered distribution, not an additive quantity. Neither an unweighted average nor an average weighted by group counts generally recovers the pooled percentile. The denominator-weighting rule for proportions above must not be transferred to percentiles.

For a requested overall percentile, use compatible underlying observations or a distribution representation that supports combining them. Preserve units, coverage, observation weights, and the source's percentile definition; do not double-count overlapping groups. A combined histogram can support an estimate, but its resolution and estimation method limit precision. When only group percentiles and counts are supplied, do not invent a pooled value. Show the available group values with their scope, or identify the distribution data needed for the requested total. A separately supplied overall percentile need not be discarded merely because its raw data is unavailable.

## Worked example: medians do not combine like means

An invented record supplies all waits in minutes from two nonoverlapping desks in the same period: **A: 1, 2, 3** and **B: 10, 20, 30, 40, 50**. Define the median as the middle ordered value, averaging the two central values for an even count. The desk medians are **2 and 30**. Their unweighted average is **16**; weighting by counts gives **(3 × 2 + 5 × 30) / 8 = 19.5**. Neither is the pooled median: the eight ordered waits have central values **10 and 20**, giving **15 minutes**. For an all-waits question, label that pooled value and its population, optionally retaining the desk values separately.

A control chart comparing **each desk's median** can validly show 2 and 30 without an overall value. An explicitly requested average of desk medians is also a different, legitimate summary, not the median across all waits. If B instead had waits **4, 5, 30, 40, 50**, its count and median would be unchanged, but the pooled median would be **4.5 minutes**. Counts and medians alone therefore do not determine the answer. Keep the stated median convention; do not impose it on every source's percentile calculation.

## Preserve histogram bin widths and density

For a histogram on a linear numeric axis, retain the source's bin boundaries and say whether height represents count, share, or density. With unequal bin widths, raw count heights give wider intervals extra area unrelated to their counts. When area is meant to represent count or share, use count divided by bin width, or count divided by both the represented population size and bin width. Label the vertical units accordingly, such as “observations per minute” or “probability density per minute.” Density height is not the probability of that interval; height times width gives its count or share. A probability density can exceed one.

Keep the distinction between “which interval contains more observations?” and “where are observations more concentrated per unit?” A table or equal-width categorical bars labeled with the original intervals can answer the first without claiming a continuous density shape. Equal-width count histograms are also legitimate. Do not prescribe density for every count comparison or treat these alternatives as defective merely because their heights are counts.

Do not split supplied grouped counts into new bins without evidence for the split. Preserve endpoint inclusion, coverage, excluded observations, and the population used for normalization where relevant. Density calculations require positive finite widths, and probability normalization also requires a nonzero represented total; do not invent values for unknown or open-ended widths. The height-times-width check here assumes linear coordinates; transformed axes need an explicit account of which variable the density describes rather than a screen-area shortcut.

## Worked example: equal counts, unequal intervals

An invented record of **40 waits** reports **20 in [0, 10) minutes** and **20 in [10, 30] minutes**. Brackets include an endpoint and parentheses exclude it. For a numeric-axis histogram whose area represents count, use heights **2 and 1 observations per minute**, respectively. Each rectangle then has area 20. Probability-density heights are **0.05 and 0.025 per minute**, giving shares 0.5 and 0.5 after multiplying by widths 10 and 20. Equal count heights across these unequal widths would give the second interval twice the area despite equal counts.

For “How many waits fell in each reported interval?”, a table showing **20 and 20** is sufficient. Do not invent the counts for 10–20 and 20–30 minutes to force equal-width bins. The grouped record does not reveal that split or the individual wait times.

## Preserve variation and uncertainty

Determine whether an interval describes variation among observations, uncertainty about a parameter, or a range of future outcomes. These answer different questions. Name the interval type and level when supplied; otherwise retain the source's wording and flag the missing definition. Do not relabel an unexplained range as a confidence interval.

Show the distribution when its shape, tails, or subgroups are necessary to the question. A mean is not a typical individual in every distribution. Conversely, a simple labeled estimate can suffice when the task only asks for that reported estimate and no stronger inference is invited.

When comparing estimates, a visually larger center is not by itself an established difference in the underlying populations. An interval-overlap shortcut is not a substitute for the relevant comparison or statistical analysis. Keep limitations near a headline that would otherwise imply certainty.

If uncertainty is absent from the source, identify that limitation rather than fabricating error bars or declaring the value false.

## Separate totals to date from activity in each period

Establish whether a time series records activity during each interval, a running total since a stated start, a rolling-window summary, or a point-in-time balance. Preserve that meaning in labels and the headline. A rising cumulative total does not establish rising daily activity: positive additions can shrink while the total continues upward. Use totals to date for accumulated progress and period amounts or rates for the pace question; neither view is universally preferable.

For a compatible running total, subtract the earlier boundary value from the later one to recover the amount added over that interval. Retain the start boundary, end boundary, and source definition. Do not assume the first displayed value began at zero, add cumulative snapshots together as if they were disjoint periods, or treat a multi-day difference as one day's activity. When the question concerns pace across unequal durations, a supported amount divided by elapsed time gives an interval-average rate, not the unobserved daily pattern.

Check resets, corrections, and changes in coverage before interpreting differences as new events. A negative difference can reflect a revision or a legitimately signed net measure; do not silently clamp it to zero. A changing rolling-window total is not a running total, and a balance change is not necessarily gross inflow. If the definitions or required boundary values are missing, state what cannot be recovered rather than inventing period values.

## Worked example: a rising total with slowing additions

An invented campaign records cumulative registrations since launch at the same daily closing time: **day 0: 0, day 1: 60, day 2: 100, day 3: 120**. The compatible, unrevised record implies **60, 40, and 20 new registrations** in the three daily intervals. For “Is daily registration increasing?”, show those interval values and say it decreased over these days. The fact that the cumulative curve rises does not by itself answer that question. Summing its four snapshots to **280** would count earlier registrations repeatedly, not recover campaign registrations.

For “How many registrations have accumulated by day 3?”, the correctly labeled **120 since launch** is sufficient; do not force a daily view. If only day 1's **60** and day 3's **120** are available, the difference establishes **60 over two days**, averaging **30 per day**, but does not establish **30 on each day**. If the series instead reports current active members or the last seven days' registrations, do not apply the running-total interpretation without the relevant accounting or window definition.

## Preserve missingness as part of the evidence

Keep observed zero, unavailable observations, and source-supplied estimates distinct. Preserve the source’s meaning for blanks or status codes; do not assign one when it is unknown. Establish the relevant categories or expected observation schedule from the source; missing records may omit a category or timestamp altogether, not merely contain an empty value. Retain their place in a requested complete comparison instead of silently closing the gap. Do not infer a failed observation from irregular spacing alone: event-driven sampling and periods outside the stated coverage can be legitimate. Preserve actual time spacing when elapsed time matters.

Make the missingness recoverable in the proposed display or clearly associated text. An absent bar can look like a measured zero; use a clearly associated “not available” label, status row, or another explicit distinction rather than inventing a height. For a line, distinguish observed points from a connector across unobserved time. A gap, an annotated connector, or a separate estimate can suit different tasks; do not mandate breaks everywhere. If the source supplies imputed values, identify them and their method when known without presenting them as observations. Do not fill gaps just to make a smooth chart or invent why data is missing. Keep isolated observations recoverable when no line segment connects them.

Scope conclusions and derived summaries to the available evidence. An average of available observations is not automatically the full-period average; preserve its denominator and coverage when used. Missingness need not invalidate a correctly scoped reported value. Avoid a headline that implies complete coverage when missing observations could change its answer.

## Worked example: a missing reading is not a zero

An invented daily record specifies **Monday: 12 visits, Tuesday: unavailable after a logging failure, Wednesday: 0 visits, Thursday: 18 visits**. A complete daily comparison should retain Tuesday with “not available” and Wednesday with “0”; neither deleting Tuesday nor drawing both as unlabeled zero-height bars preserves that distinction. If a line is chosen, keep the daily spacing and distinguish any bridge over Tuesday from measured values. The available-day mean is **10 visits over three recorded days**, not an established four-day mean.

A control source records only irregular inspection dates and specifies no daily schedule. Keep those dates; do not manufacture missing daily observations or diagnose a logging failure. A captioned line that only joins recorded inspections can be legitimate when it does not claim measurements between them.

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

- [D3 stack documentation](https://d3js.org/d3-shape/stack) defines layer boundaries and distinguishes stack offsets. [Datawrapper's area-chart guidance](https://www.datawrapper.de/academy/what-to-consider-when-creating-area-charts) discusses total/composition and individual-series tasks. The two-period example is original arithmetic, not measured model behavior or reader comprehension; neither tool is required.

- [BLS percent-change guidance](https://www.bls.gov/cpi/factsheets/calculating-percent-changes.htm) distinguishes endpoint change from the sum of monthly rates. [Bank of England growth-rate documentation](https://www.bankofengland.co.uk/statistics/details/further-details-about-changes-flows-growth-rates-data) compounds successive rates and explains why adjusted growth can differ from raw endpoint changes. The activity-index example is original arithmetic, not a model or reader-comprehension evaluation.

- [Prometheus histogram and summary guidance](https://prometheus.io/docs/practices/histograms/) documents why averaging precomputed quantiles does not generally recover a service-wide percentile and distinguishes histogram estimates. [NIST's percentile reference](https://www.itl.nist.gov/div898/handbook/prc/section2/prc262.htm) describes ordered observations and differing percentile conventions. The desk-wait counterexamples are original arithmetic controls, not a model-behavior or reader-comprehension evaluation.

- [ONS's December 2025 public-finance bulletin](https://www.ons.gov.uk/economy/governmentpublicsectorandtaxes/publicsectorfinance/bulletins/publicsectorfinances/december2025) distinguishes a month's borrowing from the cumulative financial-year amount and compares matched periods. [WHO's case-dashboard notes](https://data.who.int/dashboards/COVID19/cases?n=c) document reporting intervals and retrospective corrections that can produce spikes or negative values. These are real reporting examples motivating the distinction, not evaluations of this skill or a requirement to use either domain's chart format.

- [ONS's dual-axis examples](https://digitalblog.ons.gov.uk/2019/07/03/dueling-with-axis-the-problems-with-dual-axis-charts/) demonstrate misleading magnitude and growth readings. [Datawrapper's dual-axis guide](https://www.datawrapper.de/blog/dual-axis-charts-guide) discusses task-sensitive alternatives and legitimate uses. [Matplotlib's secondary-axis documentation](https://matplotlib.org/stable/gallery/subplots_axes_and_figures/secondary_axis.html) distinguishes linked conversions from independent scales. These motivate the checks; they do not evaluate this skill or require a plotting library.

- [Pearl, Understanding Simpson's Paradox](https://ftp.cs.ucla.edu/pub/stat_ser/r414.pdf) separates association reversal from causal interpretation; it does not license automatic subgroup adjustment. [CDC's age-adjustment definition](https://www.cdc.gov/nchs/hus/sources-definitions/age-adjustment.htm) illustrates a common reference distribution and why standardized rates must be distinguished from observed rates. The delivery example is an original arithmetic illustration, not a causal or reader-comprehension study.

- [NIST's histogram guidance](https://www.itl.nist.gov/div898/handbook/eda/section3/eda33e.htm) distinguishes count, relative-frequency, and area-normalized displays. [Matplotlib's histogram normalization examples](https://matplotlib.org/stable/gallery/statistics/histogram_normalization.html) illustrate the unequal-bin-width problem. These support the arithmetic and encoding distinction, not a measured improvement in this skill or a required renderer.

- [Song and Szafir, Where’s My Data?](https://cmci.colorado.edu/visualab/papers/song_VIS_2018.pdf) studies missing-data and imputation displays in synthetic time-series averaging and trend tasks. It shows tradeoffs between interpretation and perceived data quality, not a universally best gap treatment or validation of these skills.
- [Matplotlib’s missing-value example](https://matplotlib.org/stable/gallery/lines_bars_and_markers/masked_demo.html) illustrates that deleting points can leave a continuous line while masked values can break it. This implementation example motivates an explicit semantic handoff; it does not require that renderer or prove reader comprehension.

- [data.europa.eu, Grids versus data labels](https://data.europa.eu/apps/data-visualisation-guide/grids-versus-data-labels-in-bar-charts) recommends end-of-bar values for direct lookup. [ONS rounding guidance](https://service-manual.ons.gov.uk/content/numbers/rounding) balances readability with task-relevant precision. These are authored guidance, not tests of this skill or rules to label every mark.
- [Srinivasan et al., What's the Difference?](https://www.microsoft.com/en-us/research/wp-content/uploads/2018/01/paper2869-camera-ready.pdf) evaluates explicit difference encodings in two-series bar comparisons. It motivates reducing mental subtraction, but did not compare textual annotations; a signed difference label here is a local application, not a proven best format.
- [Heer and Bostock, Crowdsourcing Graphical Perception](https://idl.uw.edu/papers/crowdsourcing-graphical-perception) studies specific perceptual judgments. Use its results to inform comparable tasks, not to certify whole-chart understanding.
- [Wilke, Proportional ink](https://clauswilke.com/dataviz/proportional-ink.html) discusses how filled marks imply magnitude. [Visualizing uncertainty](https://clauswilke.com/dataviz/visualizing-uncertainty.html) distinguishes uncertainty displays and their interpretation. These are authored textbook guidance, not evaluations of this skill.
- [Hullman, Why Authors Don't Visualize Uncertainty](https://mucollective.northwestern.edu/project/2019-value-of-uncertainty-vis) investigates practitioner reasoning and barriers; it does not establish that every chart needs the same uncertainty display.
- [Böcherer-Linder and Eichler, How to Improve Performance in Bayesian Inference Tasks](https://pmc.ncbi.nlm.nih.gov/articles/PMC6401595/) compares five visualizations in calculation tasks with undergraduate students. It motivates exposing the relevant sets and subsets; it does not establish a universally best format or validate this skill.

The survey, close-bar, inspection, delivery, wait-interval, daily-record, campaign-registration, order-series, and temperature examples, and decision procedures are original teaching material. They do not replace statistical analysis when a requested inference requires it.
