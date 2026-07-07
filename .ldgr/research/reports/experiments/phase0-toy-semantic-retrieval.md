# Experiment: Phase 0 toy semantic retrieval benchmark

Experiment: phase0-toy-semantic-retrieval
Branch: main
Program: relational-transition-memory-substrate
Phase: 0
Status: completed
Mode: falsification

Anchors: [Result](#result) | [Interpretation](#interpretation) | [Limitations](#limitations) | [Facts](#facts) | [Next Hypotheses](#next-hypotheses)

Hypothesis: Incremental evidence accumulation narrows the candidate set (>=3x reduction) while preserving the correct target (top_3_recall >= 0.95, false_elimination_rate <= 0.05), and an ordered/typed variant beats the shuffled-order control.
Setup: Build Dataset A toy semantic world in the research harness (research/substrate layout); run substrate eval for unordered, ordered, typed, and shuffled variants with incremental evidence retrieval.
Observation Goal: Measure candidate set size and target survival after each evidence step per variant, and whether ordering/typing beats the shuffled control.
Rationale: Smallest falsifiable test per the docs recommended first experiment; gates all later phases and LDGR integration.
Primary Metrics: top_3_recall
Secondary Metrics: candidate_set_reduction, false_elimination_rate, monotonic_narrowing_rate
Pass Criteria: ["top_3_recall >= 0.95 AND candidate_set_reduction >= 3x AND false_elimination_rate <= 0.05 AND monotonic_narrowing_rate >= 0.75 AND (ordered or typed beats shuffled control)."]
Fail Criteria: ["Toy data fails to narrow candidates, eliminates correct targets too often, or ordered/typed does not beat the shuffled control."]

## Runs
No runs recorded.

## Metrics
No metrics recorded.

## Artifacts
No artifacts recorded.

<a id="result"></a>
## Result
Phase 0 toy semantic retrieval benchmark on Dataset A (7 targets: cat, dog, panther, bear, wolf, crow, eagle). Incremental evidence retrieval over four variants: unordered (set), ordered (value subsequence), typed (typed-edge subsequence), shuffled (ordered matcher on permuted evidence, averaged over 5 seeds). Ordered: top_3_recall=1.00, candidate_set_reduction=6.34x, false_elimination_rate=0.000, monotonic_narrowing_rate=1.00, final_set_size=1.14, target_survival_rate=1.00. Unordered and typed are IDENTICAL to ordered on every target. Shuffled control is degenerate: top_3_recall=0.00, final_empty_rate=1.00 (collapses to empty candidate sets because a random permutation is almost never a subsequence of a strict canonical trace). Phase-0 gate PASSES on literal criteria; see interpretation for the tight bounds on what that pass actually means.


<a id="interpretation"></a>
## Interpretation
SUPPORTED on literal phase-0 criteria, but the support is narrow and bounded. The primary falsification condition ("evidence accumulation does not reliably narrow the candidate set, or eliminates the correct target too often") is NOT triggered: incremental evidence narrows 6.34x with perfect target survival and zero false eliminations. Two honest caveats, however, mean this validates only the narrowing+survival mechanic, NOT the transition-structure hypothesis itself: (1) Order and type are INERT on this toy -- ordered == unordered == typed for every target -- because the toy world has a globally consistent general->specific attribute ordering (no order conflicts for sequence matching to exploit) and every attribute value maps to exactly one relation type (so typed-edge matching coincides with ordered value matching). (2) The shuffled control is degenerate (final_empty_rate=1.00): a random permutation almost never satisfies a strict subsequence constraint, so the matcher empties out and eliminates the target, making "ordered beats shuffled" technically true but a subsequence-matcher brittleness artifact, not evidence that canonical order carries retrieval value. NET: does-evidence-narrowing-work = YES on a controlled toy; does-transition- order-or-typing-matter = INCONCLUSIVE and requires a conflict-rich dataset or adversarial arrival-order evidence. Claim delta: the "relational transition trace narrows candidates" half of the core hypothesis is supported; the "transition structure (order/type) beats simpler alternatives" half is untested.


<a id="limitations"></a>
## Limitations
(1) Evidence is each target's own canonical attributes (best-case arrival order); real-world evidence is noisier and partial, so arrival-order robustness is an upper bound here. (2) ordered == unordered == typed on this toy (verified identical per-target); order/type importance CANNOT be evaluated on Dataset A and needs a dataset where shared attributes appear in different relative order across targets. (3) Shuffled control is degenerate (collapses to empty sets); a non-degenerate order test needs content-consistent but wrong-ordered evidence or a conflict-rich dataset. (4) Typed-edge discrimination (phase 4, >=20% reduction) needs polymorphic values reused under different relation types; this toy assigns each value exactly one type. (5) 7 targets is a controlled toy; top_3_recall=1.0 is partly an artifact of small, cleanly-separable attribute sets; real-record phase-6 work is out of scope and gated.


Decision: continue
Confidence: medium
Allowed Next Steps: ["Build a conflict-rich dataset (shared attributes in different relative order across targets + >=1 value reused under different relation types) and run phase-3 order-importance + phase-4 type-importance with a non-degenerate shuffled control; pass = ordered beats unordered >=15% reduction AND typed beats ordered >=20%."]
Blocked Next Steps: ["Phase 6 real Learning Record retrieval and any LDGR/Episteme integration of the substrate; blocked until order-importance is resolved on a conflict-rich dataset and phase 5 contradiction metrics pass."]

<a id="facts"></a>
## Facts
No facts recorded.

<a id="next-hypotheses"></a>
## Next Hypotheses
No next hypotheses recorded.
