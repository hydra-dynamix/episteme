# Generalized Multi-Step Trajectory Prediction Analysis

## Summary

This experiment attempted to generalize the previous supported hand-designed motif result to a generated suite of recurrent temporal motifs with set-valued predictions over all stored motifs sharing a prefix.

Outcome: **partially_supported_control_failures**.

The positive cases all passed: generated motifs predicted their own held-out suffixes at h1, h2, and full horizons. However, the broader suite exposed a major failure mode: prefix ambiguity dominated the generated motif population. Because many generated motifs share the same canonical early prefixes, set-valued prediction became too broad and accepted too many non-isomorphic controls.

This is a valuable falsification result. The earlier claim does not automatically generalize from a small separated motif set to a dense generated motif library without additional disambiguation or longer/contextual prefixes.

## Scale

- Motifs generated: 50
- Total evaluated cases: 401
- Training support per motif: 3 symbolic instances
- Compression ratio: 3.0

Generated motif property counts:

| Property | Count |
|---|---:|
| recurrence | 50 |
| branch | 48 |
| convergence | 43 |
| repeated subtrace | 33 |
| loop closure | 5 |

## Metrics

| Metric | Observed |
|---|---:|
| Positive h1 acceptance | 1.0 |
| Positive h2 acceptance | 1.0 |
| Positive full acceptance | 1.0 |
| Prefix-divergent h1 acceptance | 0.942731 |
| Prefix-divergent h2 acceptance | 0.713656 |
| Prefix-divergent full acceptance | 0.136564 |
| Degree-matched h1 acceptance | 0.678571 |
| Degree-matched h2 acceptance | 0.488095 |
| Degree-matched full acceptance | 0.190476 |
| Divergence-localization accuracy | 0.528634 |
| Ambiguous-prefix rate | 0.905237 |
| Compression ratio | 3.0 |

## Criteria Outcome

Passed:

- Positive full acceptance >= 0.98.
- Positive h1/h2 acceptance >= 0.98.
- Compression ratio >= 3.0.

Failed:

- Prefix-divergent full acceptance <= 0.01.
- Degree-matched full acceptance <= 0.01.
- Divergence-localization accuracy >= 0.95.
- Ambiguous-prefix rate <= 0.10.

## Interpretation

The generated suite disproves the overly broad version of the claim:

> A stored recurrent motif library generally constrains future trajectory well under short ambiguous prefixes.

That is not supported. In a dense generated motif set, many motifs share canonical prefixes, so a set-valued predictor often has many possible suffixes. This increases full-suffix false acceptance for non-isomorphic controls.

The narrower claim from the previous experiment still stands:

> For a small motif set with sufficiently discriminative prefixes, stored recurrent motifs can constrain multi-step future topological trajectory.

The generalized result identifies a missing condition: **prefix identifiability**. Future-trajectory prediction depends not only on motif storage, but also on whether the observed prefix uniquely or narrowly identifies a stored motif family.

## Methodological Importance

This is the expected kind of failure for a falsification-oriented program. The generated experiment did not simply confirm the hand-designed result. It found the boundary where the effect weakens:

```text
small separated motif set -> supported
large dense motif set with ambiguous prefixes -> control failures
```

That boundary is scientifically useful because it suggests the next mechanism to test: adaptive prefix length or uncertainty-aware prediction.

## Recommended Follow-Up

Do not add semantics or labels. Instead test whether topology alone can recover specificity by requiring sufficient prefix information.

Next experiment:

1. For each generated motif, compute the minimum discriminative prefix length: the shortest prefix whose predicted suffix set has size <= N, ideally 1.
2. Evaluate h1/h2/full prediction at fixed prefix lengths versus minimum-discriminative-prefix lengths.
3. Report an accuracy/coverage tradeoff:
   - short prefixes: high coverage, high ambiguity;
   - longer prefixes: lower ambiguity, potentially higher specificity.
4. Treat ambiguous predictions explicitly as uncertainty, not as incorrect single predictions.

This would test a more precise hypothesis:

> Recurrent motif memory constrains future trajectory when the observed prefix contains enough topology to identify a sufficiently small suffix set.

## Validation

Latest validation command:

```text
dev run py_check
```

Observed:

- Ruff format check passed.
- Ruff lint passed.
- Mypy passed.
- Pytest passed: `16 passed`.
- `uv run python src/generalized_trajectory_experiment.py` regenerated deterministic generalized results.
