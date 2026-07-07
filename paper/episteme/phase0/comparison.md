# Phase 0 toy semantic retrieval benchmark

Spine: program `relational-transition-memory-substrate` / branch `main` /
question `does-toy-evidence-narrowing-work` / option `compare-substrate-variants-on-toy-world` /
experiment `phase0-toy-semantic-retrieval` (mode=falsification).

## Hypothesis

Incremental evidence accumulation narrows the candidate set (>=3x reduction)
while preserving the correct target (top_3_recall >= 0.95,
false_elimination_rate <= 0.05), and an ordered/typed variant beats the
shuffled-order control.

## Setup

Dataset A toy semantic world, 7 targets (cat, dog, panther,
bear, wolf, crow, eagle) with overlapping attributes. For each held-out target
the evidence is its own canonical trace, fed token by token. Four variants:
unordered (set), ordered (value subsequence), typed (typed-edge subsequence),
shuffled (ordered matcher on a permuted sequence, averaged over
5 seeds). Evidence = target's own attributes = best-case
arrival order; this is the case a transition-trace substrate must handle and
the case the shuffled control is designed to break.

## Metrics by variant

| variant | top_1_recall | top_3_recall | candidate_set_reduction | false_elim_rate | monotonic_narrow | final_set_size | survival_rate |
|---|---|---|---|---|---|---|---|
| unordered | 1.000 | 1.000 | 6.34x | 0.000 | 1.000 | 1.14 | 1.000 |
| ordered | 1.000 | 1.000 | 6.34x | 0.000 | 1.000 | 1.14 | 1.000 |
| typed | 1.000 | 1.000 | 6.34x | 0.000 | 1.000 | 1.14 | 1.000 |
| shuffled | 0.000 | 0.000 | 0.00x | 0.720 | 1.000 | 0.00 | 0.280 |

## Phase-0 gate

Overall: **supported**

- PASS `top_3_recall_ordered_ge_0.95`
- PASS `candidate_set_reduction_ordered_ge_3x`
- PASS `false_elimination_rate_ordered_le_0.05`
- PASS `monotonic_narrowing_rate_ordered_ge_0.75`
- PASS `ordered_beats_shuffled`
- PASS `typed_beats_shuffled`
- PASS `ordered_or_typed_beats_shuffled`

Structured vs shuffled (reduction improvement / recall delta):
- ordered: n/a (shuffled degenerate) reduction gain, recall delta +1.000 -> beats shuffled: True
- typed:   n/a (shuffled degenerate) reduction gain, recall delta +1.000 -> beats shuffled: True

## Honest caveats (read before interpreting the pass)

**Order and type are inert on this toy.** Ordered == unordered == typed for
every target:
- ordered vs unordered: 0.0% reduction gain, recall delta +0.000 -> order_matters=False
- typed vs ordered: 0.0% reduction gain, recall delta +0.000 -> type_matters=False

Reason: the toy world has a globally consistent general->specific attribute
ordering, so two shared attributes always appear in the same relative order
across targets -- there are no order conflicts for sequence matching to
exploit. And every attribute value maps to exactly one relation type, so
typed-edge matching coincides with ordered value matching.

**The shuffled control is degenerate** (final_empty_rate=1.0,
degenerate=True): a random permutation is almost never a
subsequence of a strict canonical trace, so the matcher empties the candidate
set and eliminates the target. "Ordered beats shuffled" is therefore
*technically* true but reflects subsequence-matcher brittleness to permutation,
not that canonical order carries retrieval value.

**Net.** The phase-0 gate passes on its literal criteria (narrowing + survival
+ beats-shuffled), so the primary falsification condition is NOT triggered.
But this validates only the narrowing+survival mechanic on a controlled toy; it
does NOT validate that transition order or typing helps retrieval. Whether
order matters is inconclusive on this toy and is the queued next experiment.

## Shuffled control per-seed top line

| seed | top_3_recall | reduction | false_elim | monotonic |
|------|--------------|-----------|------------|-----------|
| 0 | 0.000 | 0.00x | 0.756 | 1.000 |
| 1 | 0.000 | 0.00x | 0.689 | 1.000 |
| 2 | 0.000 | 0.00x | 0.733 | 1.000 |
| 3 | 0.000 | 0.00x | 0.667 | 1.000 |
| 4 | 0.000 | 0.00x | 0.756 | 1.000 |

## Interpretation

Phase-0 gate SUPPORTED on the controlled toy semantic world: incremental evidence accumulation narrows the candidate set 6.34x for ordered (top_3_recall=1.00, false_elimination=0.000, monotonic=1.00), so the primary falsification condition (narrowing fails OR target eliminated too often) is NOT triggered. HOWEVER two honest caveats bound this result tightly: (1) order and type are INERT in this toy -- ordered == unordered == typed for every target (0.0% reduction gain of ordered over unordered, 0.0% of typed over ordered) because the toy world has a globally consistent general->specific attribute ordering with no order conflicts and every value carries one relation type; (2) the shuffled control is degenerate (final_empty_rate=1.00) -- a random permutation is almost never a subsequence of a strict canonical trace, so the matcher empties out and the target is eliminated, making 'ordered beats shuffled' technically true but a brittleness artifact, not evidence that canonical order carries retrieval value. NET: this validates the narrowing+survival mechanic on a controlled toy but does NOT validate transition structure; whether order/typing matters is inconclusive here and requires a conflict-rich dataset or adversarial arrival-order evidence.

## Limitations

- Evidence is the target's own canonical attributes (best-case arrival order).
  Real-world evidence is noisier and partial in a different way; that is a
  phase-6 (real Learning Records) concern, deliberately out of scope here.
- Ordered == unordered == typed in this toy (see Honest caveats). Order/type
  importance cannot be evaluated on Dataset A; queued as a phase-3 test on a
  conflict-rich dataset.
- Shuffled control collapses to empty candidate sets (degenerate); a
  non-degenerate order test requires evidence arrival orders that are wrong but
  still content-consistent, or a conflict-rich dataset.
- Ordered/typed metrics use canonical-order evidence and are therefore an upper
  bound on arrival-order robustness; phase 3 should add adversarial/deceptive
  evidence ordering.
