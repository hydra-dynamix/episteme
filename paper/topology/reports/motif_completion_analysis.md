# Motif Completion / Prediction Analysis

## Summary

This experiment tested the next capability beyond complete-motif detection: whether a consolidated recurrent motif can predict the next canonical topological state from a partial symbolically novel trace.

Outcome: **partially_supported_control_failures**.

The result supports a narrow completion capability for clean positive cases: all positive partial traces predicted the correct next canonical state, all valid completions were accepted, all hand-authored invalid completions were rejected, path controls received no prediction, and automorphic-equivalent prediction passed. However, generated degree-matched non-isomorphic controls exceeded the predeclared acceptance threshold. This prevents classifying motif completion as supported under the current criteria.

## Observer / Implementer Separation

- Observer predeclaration: `docs/motif_completion_experimental_design.md`
- Implementation: `src/motif_completion_experiment.py`
- Raw output: `results/motif_completion_experiment_results.json`
- Validation tests: `tests/test_motif_completion_experiment.py`

The observer-level criteria were written before interpreting the result. The implementation then produced deterministic outputs evaluated against those criteria.

## Hypothesis Tested

A consolidated recurrent temporal motif can induce predictions over future canonical states/transitions for symbolically novel partial traces that match the motif prefix, while rejecting invalid completions and non-isomorphic controls.

## Prediction Rule

A partial trace is canonicalized by first occurrence. If the canonical partial trace is a prefix of a consolidated motif trace, the stored motif predicts the next canonical node.

The prediction can be:

- `NEW`: the next state should be a previously unseen canonical node.
- an existing canonical ID, e.g. `1`: the next state should return to an already observed node.

## Key Positive Results

| Case | Partial | Prediction | Valid completion | Accepted |
|---|---|---:|---|---:|
| recurrence loop | `X -> Y -> X -> ?` | `NEW` | `X -> Y -> X -> Z` | yes |
| branch-converge loop | `X -> Y -> Z -> X -> ?` | `NEW` | `X -> Y -> Z -> X -> W` | yes |
| repeated substructure | `X -> Y -> X -> Z -> X -> ?` | existing node `1` | `X -> Y -> X -> Z -> X -> Y` | yes |

Positive top-1 prediction accuracy: `1.0`.
Positive valid completion acceptance rate: `1.0`.

## Controls

Passed controls:

- Hand-authored invalid completions were rejected: acceptance rate `0.0`.
- Length-matched path controls received no prediction: prediction rate `0.0`.
- Automorphic-equivalent prediction passed: accuracy `1.0`.
- Compression ratio remained `3.0`.

Failed control:

- Degree-matched non-isomorphic control acceptance rate was `0.133333`, above the predeclared `<= 0.05` threshold.

Two generated controls were accepted as one-step completions:

1. `completion_branch_converge_loop_degree_matched_non_isomorphic_004_completion_probe`
2. `completion_repeated_substructure_degree_matched_non_isomorphic_003_completion_probe`

## Interpretation

This is a meaningful but not fully supported result.

The experiment demonstrates that stored recurrent motifs can do more than complete-template detection in clean cases: they can produce the correct next canonical state for partial symbolically novel traces. This is the first evidence in the project for:

```text
persistent motif -> constrained future behavior
```

However, the degree-matched control failure shows that **one-step prefix prediction is weaker than full motif recognition**. A full non-isomorphic control can share a valid motif prefix and even a valid next transition before diverging later. In that case, accepting the immediate next state is not necessarily wrong locally, but it is insufficient to prove robust predictive memory under the predeclared criterion.

The failure suggests the current predictor answers:

> Is this next step consistent with at least one stored motif prefix?

It does not yet answer:

> Does the partial trajectory commit to a future continuation that remains discriminative against hard non-isomorphic controls?

## Outcome Against Predeclared Criteria

| Criterion | Observed | Pass |
|---|---:|---:|
| Positive top-1 prediction accuracy == 1.0 | 1.0 | yes |
| Positive valid completion acceptance rate == 1.0 | 1.0 | yes |
| Automorphic prediction accuracy == 1.0 | 1.0 | yes |
| Invalid completion acceptance rate == 0.0 | 0.0 | yes |
| Degree-matched control acceptance rate <= 0.05 | 0.133333 | no |
| Path control prediction rate == 0.0 | 0.0 | yes |
| Compression ratio >= 3.0 | 3.0 | yes |

Final classification: **partially_supported_control_failures**.

## Recommended Follow-Up

The next experiment should test multi-step completion horizons and discriminative commitment:

1. Given a partial trace, predict not only the next node but the remaining canonical suffix.
2. Score whether controls that share the next step diverge at later predicted steps.
3. Measure prediction accuracy by horizon: 1-step, 2-step, full suffix.
4. Include degree-matched non-isomorphic controls specifically selected to share early prefixes.

This would distinguish local prefix consistency from genuine motif-induced future trajectory prediction.

## Validation

Latest validation command:

```text
dev run py_check
```

Observed:

- Ruff format check passed.
- Ruff lint passed.
- Mypy passed.
- Pytest passed: `10 passed`.
- `uv run python src/motif_completion_experiment.py` regenerated deterministic results.
