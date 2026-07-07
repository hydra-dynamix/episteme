# Outcome-Weighted Topology Recollection Experiment

## Question

Can topology recollection improve if motif support is weighted by workflow outcome?

Proposed intuition:

```text
successful patterns -> higher weight
failure/blocker patterns -> lower weight
ambiguous/partial patterns -> slightly higher than neutral
```

## Setup

Primary corpus:

```text
/mnt/nas/data/ldgr/benchmarks/splits/benchmarks
```

Primary configuration:

```text
token_mode=refined
window=30..36
stride=6
mixed repeated+novel workload
candidate_cost=0.005
```

Outcome classes were inferred only from categorical LDGR tokens:

```text
success:    run:end:pass, decision:record:validated, decision:record:completed
ambiguous:  run:end:partial, decision:record:inconclusive
failure:    run:end:fail
blocker:    decision:record:blocker
neutral:    no outcome token
```

Weight schemes:

| scheme | success | ambiguous | neutral | failure | blocker |
|---|---:|---:|---:|---:|---:|
| unweighted | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| success_boost | 1.75 | 1.15 | 1.0 | 0.5 | 0.75 |
| aggressive_success | 2.5 | 1.25 | 0.9 | 0.25 | 0.5 |
| failure_suppressed | 1.25 | 1.1 | 1.0 | 0.1 | 0.4 |

Raw outputs:

```text
results/outcome_weighted_recollection.json
results/outcome_weighted_recollection_followups.json
```

## Primary Result

On long-window benchmark mixed workload, outcome weighting did **not** improve over unweighted support.

Best utility by bound:

| bound | best scheme | utility/query | unweighted utility/query |
|---:|---|---:|---:|
| 1 | unweighted | 0.102469 | 0.102469 |
| 2 | unweighted | 0.544019 | 0.544019 |
| 3 | unweighted | 0.593090 | 0.593090 |
| 5 | unweighted | 0.657499 | 0.657499 |
| 10 | unweighted | 0.691225 | 0.691225 |
| 25 | unweighted | 0.702080 | 0.702080 |
| 100 | unweighted / weighted tie | 0.701932 | 0.701932 |

Outcome weighting generally pushed the expected suffix slightly lower in rank:

```text
unweighted mean expected rank:        1.974821
success_boost mean expected rank:     2.102197
aggressive_success mean expected rank:2.102197
failure_suppressed mean expected rank:2.101456
```

Top-1 hit rate also slightly worsened:

```text
unweighted:          0.491237
success_boost:       0.485065
aggressive_success:  0.485065
failure_suppressed:  0.485312
```

## Follow-up Checks

### Short benchmark windows: 8..12

Outcome weighting was mostly neutral/negative, with tiny gains only at larger bounds:

```text
bound 5:   success_boost -0.308812 vs unweighted -0.309210
bound 100: success_boost  0.007097 vs unweighted  0.006302
```

This is too small to be considered a meaningful win.

### Coding split, long windows

Unweighted was best at all checked bounds.

### Research split, long windows

Unweighted was best at all checked bounds, but the long-window research workload has very few repeated queries.

## Interpretation

The simple outcome-weighting hypothesis was not supported.

Likely reasons:

1. **Outcome labels are too coarse for local suffix ranking.**
   A window can contain a successful run outcome while still sharing structural continuations with failed or blocked traces.

2. **Successful outcomes dominate the corpus.**
   Benchmark long-window outcome distribution:

   ```text
   success:   62259
   blocker:   18659
   ambiguous: 14343
   neutral:    4326
   failure:    3217
   ```

   Weighting success mostly amplifies already common scaffolding rather than adding discriminative signal.

3. **Topology-only canonicalization ignores semantic cause.**
   Failures and successes can share the same structural prefix/suffix. Without more causal features, outcome weighting can rerank away from the held-out structural continuation.

4. **The tested weighting is global.**
   It does not condition on the current query's desired outcome. If the downstream agent is trying to recover from a failure, suppressing failure motifs may be wrong.

## Answer

Outcome weighting is a plausible product feature, but **not as a global default ranking multiplier**.

Current recommendation:

```text
Do not globally boost success and suppress failure in the base topology index.
```

Better use:

```text
query-conditioned outcome filters
```

Examples:

- If the current run is failing, retrieve failure-recovery motifs.
- If the current workflow is in validation, prefer patterns that end in pass/validated.
- If the downstream goal is exploration, include ambiguous/partial motifs.
- If the downstream goal is stable automation, suppress blocker/failure motifs only after preserving recall.

## Next Direction

If outcome weighting is revisited, test **goal-conditioned recollection** instead of global outcome weighting:

```text
query context: current_outcome_state + desired_outcome_state
ranking: motifs matching desired transition receive a boost
```

This would preserve failures as useful recovery examples instead of treating them as globally low-value patterns.
