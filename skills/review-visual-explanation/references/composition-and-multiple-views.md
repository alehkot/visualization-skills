# Reviewing composition and multiple views

Use this reference when arrangement, grouping, emphasis, or movement between views may obstruct the reader's task. Establish the particular obstacle before suggesting a different layout.

## Trace an actual reading operation

Identify what the reader needs to find, compare, follow, or explain. Trace the required evidence in the supplied artifact. Name the step that fails: an unlabeled correspondence, a decisive caveat detached from its claim, a comparison value unavailable in the current view, or a connection obscured at the inspected scale.

Distinguish difficulty inferred from an observable feature from a measured reader outcome. “The two values are on mutually exclusive screens, requiring recall during comparison” describes the arrangement and its requirement. “Readers will forget the first value” predicts behavior that has not been measured.

Do not call all separated information a material defect. A stable index, familiar key, or clearly linked reference can serve repeated lookup well. The review should explain why the separation obstructs this requested task and whether surrounding context already resolves it.

## Check what the composition asserts

| Feature | Inspect for meaning | Legitimate counterexample |
| --- | --- | --- |
| Grouping or enclosure | Is the inferred membership, responsibility, or scope supported? | A boundary explicitly marking ownership carries useful information. |
| Alignment | Are adjacent values or rows actually comparable? | A labeled layout can deliberately place incomparable views together for context. |
| Prominence | Does emphasis create an unsupported conclusion or change an encoded value? | Attention can be directed to an uncertain result while uncertainty remains clear. |
| Reading order | Does sequence imply chronology, dependence, or certainty not supported? | An indexed reference can support many entry points without one narrative path. |
| Repetition | Does a repeated label preserve identity or merely add clutter? | Repeated identifiers can prevent cross-view matching errors. |
| Density | Which needed label, relation, or distinction is actually unrecoverable? | A dense expert reference can still support its intended lookup task. |

Visual uniformity and variation are both tools. Neither a grid of equal panels nor an asymmetric composition establishes quality by itself. Avoid turning an aesthetic preference into an information-fidelity finding.

## Follow correspondence across views

Track a consequential entity from overview to detail, or from one state to another. Check its identifier, relevant attributes, and relationships. If order, viewpoint, or scale changes, inspect how the artifact makes the correspondence recoverable.

Panel-specific legends can legitimately change a visual encoding, but the explanation must not imply that the same cue means the same thing when it does not. Identify a concrete contradiction or matching problem; do not require all views to use identical forms.

For comparison tasks, examine the evidence the reader must integrate, including uncertainties and exceptions. Splitting the artifact can remove irrelevant detail, or it can hide exactly the evidence needed for the comparison. Judge the effect on the operation, not the number of panels.

Check a headline and its primary view independently of optional detail. If a claim becomes false without a hidden qualification, restoring the qualification is often a smaller repair than rebuilding the whole explanation.

## Verify claimed changes between snapshots

Check whether a claimed addition, removal, replacement, relocation, or changed connection follows from the supplied snapshots and their scope. A renamed entity can retain its identity; the same label can also be reused for a replacement. Do not settle that question from appearance alone. For a changed connection, compare the actual endpoints and meaning. Rerouting a schematic line around a label is not a change in the subject when path geometry carries no subject meaning; a changed physical route can matter even if its endpoints stay the same.

Match any change summary against the views in both directions: is each stated change visible or otherwise explicitly supported, and does a consequential depicted difference go unexplained? An omitted entity is not necessarily removed from the real system. Different cropping, abstraction, or incomplete source coverage may explain its absence. Report an unsupported removal claim as such; do not repair it by asserting the entity still exists.

Treat rearrangement as a finding only when it contradicts the declared encoding or obstructs a necessary match. Two independently arranged panels with clear identities can be valid. Conversely, a legend that defines position as physical location makes an unexplained position change consequential. A before/after comparison alone cannot verify a claimed transition sequence or uninterrupted operation between the snapshots.

## Check whether snapshot totals support member flows

For a Sankey, alluvial view, or switching claim, trace consequential links to joint evidence connecting the categories: matched observations, a transition table, or supported origin–destination amounts. Correct category totals at both ends generally do not verify each band; accept a flow uniquely determined by the supplied constraints rather than demanding more data automatically. Net change is not gross movement; unchanged totals do not prove unchanged membership. Check population and category correspondence, including entrants, exits, and unmatched records when relevant. Do not force unrelated cross-sectional samples into a tracked cohort.

If separate snapshot totals leave a flow unresolved, flag a claim that this flow was observed as unsupported rather than asserting a particular alternative flow is true. A smaller repair may retain the valid totals in a composition comparison and remove the unsupported switching claim. A visibly labeled modeled scenario may be legitimate when its assumptions and purpose are supported; do not mislabel its estimates as observations or reject it merely for being estimated. Joint aggregate counts can validate flows without exposing individual identities. A snapshot-only chart does not need transition data for a snapshot-only question.

An invented fixed cohort has **100 members** in mutually exclusive, exhaustive categories A and B, with **A: 60, B: 40** initially and **A: 40, B: 60** later. A brief draws **20 A→B** and all other members staying, claiming “Only 20 members switched.” Those totals also permit **60 A→B and 40 B→A**, with nobody staying. Thus the claimed flow is not determined by the supplied margins; the correct statement is that B's net count increased by 20, not that exactly 20 people switched. Do not replace the drawn flows with the second possible table as a correction. If the source separately supplies **40 A→A, 20 A→B, 0 B→A, 40 B→B**, the original flow and switching claim are supported. Without a rendering, these are evidence checks, not measured band-width or layout defects.

## Worked example: position loses identity

An invented soil-pit explanation shows **P** on the left and **Q** on the right in an overview. A detail panel sorts the same pits by depth, with **Q** on the left and **P** on the right. The caption says “The left pit contains the ash layer,” but provides no panel name or pit identifier. The source assigns the ash layer to **Q**.

The finding concerns the ambiguous referent in this multi-view explanation. Relabel the caption “Pit Q contains the ash layer” and clearly associate it with Q's detail. Reordering every panel is unnecessary if the identifiers make matching clear.

A control version already names Q in the caption and labels both details. Sorting by depth is then a legitimate choice. Do not report the order change alone as a defect or claim that readers necessarily confuse it.

If only the written brief is supplied, these specified relationships can be reviewed. Whether the rendered identifiers are too small, crossed by leaders, or clipped remains uninspected.

## Repair without erasing useful structure

Keep a boundary if it carries membership. Keep a repeated identifier if it anchors correspondence. Keep an exception beside the rule it modifies. Do not repair a dense view by deleting evidence needed for the requested inference.

Prefer a local change—an explicit label, aligned comparison, moved qualification, or restored relationship—when it addresses the problem. Suggest a new form only when the current structure cannot support the task with a smaller change. For material-only reviews, omit speculative improvements and stylistic alternatives.

## Basis and limits

- [ggalluvial’s data-format documentation](https://corybrunson.github.io/ggalluvial/articles/ggalluvial.html) describes joint/cohort data for alluvial paths. [D3 Sankey’s link contract](https://github.com/d3/d3-sankey#sankey_links) specifies each flow’s source, target, and quantity. These motivate evidence checks, not a mandated tool or an evaluation of this skill. The two transition possibilities are original arithmetic controls.

- [Green and Blackwell, Cognitive Dimensions tutorial](https://www.cl.cam.ac.uk/~afb21/CognitiveDimensions/CDtutorial.pdf) treats visibility and other properties as activity-dependent tradeoffs, not automatic defects.
- [Tversky, Visualizing Thought](https://doi.org/10.1111/j.1756-8765.2010.01113.x) discusses how arrangement and marks convey meanings.
- [Impeccable's layout reference](https://github.com/pbakaus/impeccable/blob/9d715cc4f5564a990ca8345abfdd5df6dc9b41c8/skill/reference/layout.md) provides practitioner inspiration for task-sensitive composition. This review does not adopt fixed item limits, cognitive-load scores, or issue quotas.

The diagnostic procedure and soil-pit example are original applications. Observable arrangement is evidence about the artifact, not a measurement of comprehension.
