# Multi-Step Motif Completion Horizon Analysis

## Summary

This experiment tested whether the one-step completion failure was a local-prefix artifact by extending prediction to multi-step and full-suffix horizons.

Outcome: **supported** under the predeclared criteria.

The key result is that hard controls can share a valid first step, but they are rejected at longer horizons. Degree-matched non-isomorphic controls had `h1` acceptance `0.133333`, matching the previous one-step failure pattern, but `h2` and full-suffix acceptance both fell to `0.0`.

## Hypothesis Tested

Stored recurrent temporal motifs predict multi-step canonical suffixes for symbolically novel partial traces and reject degree-matched non-isomorphic controls that share early valid prefixes but diverge later.

## Metrics

| Metric | Observed |
|---|---:|
| Positive h1 acceptance | 1.0 |
| Positive h2 acceptance | 1.0 |
| Positive full-suffix acceptance | 1.0 |
| Degree-matched h1 acceptance | 0.133333 |
| Degree-matched h2 acceptance | 0.0 |
| Degree-matched full-suffix acceptance | 0.0 |
| Prefix-divergent h1 acceptance | 1.0 |
| Prefix-divergent h2 acceptance | 0.25 |
| Prefix-divergent full-suffix acceptance | 0.0 |
| Path prediction rate | 0.0 |
| Compression ratio | 3.0 |

## Interpretation

This resolves the main ambiguity from the one-step completion experiment. The previous hard-control failure was real, but it was specifically a one-step/local-prefix issue. Controls can share an immediately valid next transition without sharing the motif's future trajectory.

At full-suffix horizon, the stored motifs behave more like a constrained temporal memory:

```text
partial recurrent trace -> expected remaining canonical suffix
```

This is still not semantic abstraction or general reasoning. It is a narrower and defensible claim: identity-free recurrent motif memory can generate multi-step topological continuation expectations and reject non-isomorphic trajectories that diverge from those expectations.

## Validation

Latest validation command:

```text
dev run py_check
```

Observed:

- Ruff format check passed.
- Ruff lint passed.
- Mypy passed.
- Pytest passed: `13 passed`.
- `uv run python src/multi_step_completion_experiment.py` regenerated deterministic supported results.

## Recommended Next Work

The next useful test is robustness under missing or noisy observations:

1. Remove one observation from a motif prefix and ask whether completion remains possible.
2. Insert one spurious observation and measure rejection or recovery.
3. Compare exact-prefix prediction with a predeclared approximate-prefix scoring rule.

This would test whether the motif memory can tolerate realistic partial/noisy traces without collapsing into overactivation.
