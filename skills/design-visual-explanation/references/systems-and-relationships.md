# Systems and relationships

Use this reference for conditional processes, states, dependencies, membership, causal explanations, or feedback. Establish what a connection means before selecting its appearance.

## Preserve the kind of relationship

For each consequential relationship, identify its endpoints, direction if any, meaning, and condition. This can remain ordinary prose in the brief; no graph schema is required. Distinguish assertions made by the source from hypotheses or your organizing choices.

| Relationship | Preserve | Common accidental claim |
| --- | --- | --- |
| Sequence | Known before/after order; unknown or overlapping intervals | Earlier means causes; equal spacing means equal duration. |
| Dependency | What requires what, and for which outcome | A prerequisite is sufficient to guarantee success. |
| Transfer | What moves, from where to where, through which boundary | Every connecting line carries the same substance or amount. |
| State change | Starting state, event/guard, resulting state | Every drawn path happens, or an omitted path is impossible. |
| Membership | Whether an item may belong to multiple groups | Enclosure means exclusive ownership or physical containment. |
| Causality | Supported mechanism, direction, scope, competing accounts | Association or convenient placement proves a causal mechanism. |

The same arrow can serve several purposes only when its meaning remains recoverable in context. Direct relationship labels often suffice; different shapes or line styles are optional ways to reduce ambiguity, not requirements in themselves.

## Make conditions executable in the reader's mind

Check a normal case and a case at the boundary of the rule. Ask what the depicted logic would let the reader conclude, then compare that conclusion with the source.

- Separate **all required** conditions from **any sufficient** alternatives. A chain through two conditions usually suggests both are required; parallel branches may imply a choice. Label the intended logic when layout alone would be ambiguous.
- Preserve an exception's scope. An exception to one prerequisite does not automatically waive the others.
- Show priority when overlapping rules give different outcomes and the source specifies which wins. If priority is not supplied, mark the unresolved conflict rather than inventing an order.
- Keep “may,” “must,” “only if,” and “if” distinct. Shorter labels must not turn possibility into certainty or reverse a one-way implication.
- Avoid presenting a selection of paths as exhaustive unless that is established. A caption such as “selected examples” changes what absence means.

For a process, identify the actor responsible for a step only if responsibility matters and is known. For a state model, distinguish stable states from actions. For a dependency map, do not impose chronological order merely to make a left-to-right story.

## Explain waiting and incomplete execution

When the question is why work waits, identify the competing arrivals, the shared resource, what can wait, and the condition for proceeding. Distinguish work waiting from work being served. A count of queued items, a simultaneous occupancy limit, and a processing rate describe different quantities; retain their units and observation periods. Converging arrows alone establish neither overload nor a particular waiting time. Show rejection, expiry, or priority only when supported; do not invent an ordered queue where service order is unknown.

For example, an invented repair desk has six jobs waiting and two benches. This supports a view of waiting work and limited simultaneous workspaces, but not a claim that two jobs finish each hour. Completion time needs further evidence about service duration and how the benches are used. If only the shared dependency is known, a labeled convergence is enough; fabricated queue slots would imply an observed backlog.

When comparing executions of a procedure, match the same checks across cases and retain each check's recorded outcome. A failed check, a deliberately bypassed check, a check never reached after an earlier stop, and an unknown result are different states. Use these distinctions only where the evidence supplies them. Mark the earliest established difference relevant to the outcome, without assuming that it proves the sole cause. If rule order or applicability differs, make that difference explicit rather than forcing a false row-by-row equivalence.

For lifecycle explanations, preserve a consequential pause or retry with its trigger and return destination. Distinguish cancellation, failure, and completion when the source does. A retry is not necessarily a restart, and a successful example does not establish that interruption is impossible.

## Represent feedback and abstraction without inventing behavior

In a causal-loop explanation, specify how changing one variable affects another, all else held as described, and where a delayed effect changes interpretation. “Positive” and “negative” link polarity describe direction of change, not desirable and undesirable outcomes. A loop's polarity does not by itself establish timing, magnitude, stability, or a forecast.

Only use feedback notation if the evidence supports a causal account. A static ownership map does not become a dynamic model because its connections form a cycle. Qualitative arrows do not warrant quantitative widths or simulated trajectories.

Across overview and detail views, keep the identity of an expanded entity explicit and preserve any connection crossing its boundary that matters to the question. A higher-level summary can omit internal detail, but should not change who connects to whom. Omit irrelevant machinery without claiming that the visible elements are the entire real system.

## Worked example: a one-way condition

In an invented archive, the source says: “A visitor may enter the study room only if their booking is confirmed and a steward is present. A confirmed booking alone does not guarantee entry.”

The brief should retain both requirements and the lack of a guarantee. One suitable representation places **confirmed booking** and **steward present** beside the **entry requirements** statement, with an explicit **both required; not a guarantee** qualification. Another is a small condition table. Neither should end in an unconditional “Enter” outcome on the evidence given.

If a later source instead supplies a complete policy—“Enter when both hold; otherwise wait”—a decision flow can encode those outcomes. That is a change in source support, not a cosmetic improvement.

Counterexample to drawing every dependency: a study-room access explanation need not show the archive's payroll process. The test is whether omission changes the answer to the stated access question, not whether the omitted dependency exists somewhere in the organization.

## Basis and limits

- [Tversky, Visualizing Thought](https://doi.org/10.1111/j.1756-8765.2010.01113.x) discusses how spatial arrangement and marks convey meaning, including the ambiguity of arrows. It does not prescribe one notation for all relationships.
- [Cascade Institute, Causal Loop Diagrams handbook](https://cascadeinstitute.org/wp-content/uploads/2024/06/Causal-Loop-Diagrams-Handbook-June-27-2024.pdf) supplies conventions for qualitative causal-loop modeling. Those conventions do not prove the links in an arbitrary source.
- [arc42, Building block view](https://docs.arc42.org/section-5/) illustrates scoped decomposition and selective detail; [C4 notation guidance](https://c4model.com/diagrams/notation) remains notation independent. These are software-architecture practices, adapted here only where their structural reasoning fits.

The condition checks and archive example are original operational guidance, not a claim of measured comprehension improvement.
