# Ambiguous Constraint Basin Stability Experiment

Date: 2026-07-06

Starting checkpoint: `docs/constraint-field-semantic-memory-directive.md`

## Purpose

Stress the constraint-field semantic substrate with harder cases:

- ambiguous surface tokens,
- context resolution,
- continuous refinement,
- held-out composition,
- perturbation and basin transition boundaries.

The key correction during the run was that a tied basin is not automatically a
transition. A tie can be a stable ambiguity state whose best downstream action
is to hold rather than force resolution.

## Boundary

The substrate uses anonymous constraints and local support links.

Human basin labels are evaluation payload after relaxation. Surface tokens such
as `bat`, `bank`, and `seal` weakly activate multiple candidate basins but are
not concept nodes.

The experiment execution is:

```text
active constraints
-> local support relaxation
-> stabilized basin set
-> post-hoc label evaluation
-> downstream decision policy for ties
```

## Experiment Execution

Command:

```text
uv run python scripts/run_ambiguous_constraint_basin_stability.py
```

Artifacts:

- Script: `scripts/run_ambiguous_constraint_basin_stability.py`
- Report: `results/ambiguous-constraint-basin-stability/report.json`
- Ambiguity records: `results/ambiguous-constraint-basin-stability/ambiguity_records.jsonl`
- Context records: `results/ambiguous-constraint-basin-stability/context_resolution_records.jsonl`
- Refinement records: `results/ambiguous-constraint-basin-stability/continuous_refinement_records.jsonl`
- Composition records: `results/ambiguous-constraint-basin-stability/composition_records.jsonl`
- Perturbation records: `results/ambiguous-constraint-basin-stability/perturbation_records.jsonl`

## Results

Summary:

| Metric | Value |
| --- | ---: |
| Ambiguous surface multi-basin rate | 1.000000 |
| Context resolution accuracy | 1.000000 |
| Continuous refinement final accuracy | 1.000000 |
| Composition success rate | 1.000000 |
| Mean first additive ambiguity count | 1.000000 |
| Mean first additive transition count | null |
| Mean first replacement ambiguity count | 1.000000 |
| Mean first replacement transition count | 3.000000 |
| Tie-policy expected utility on ties | 0.700000 |
| Forced-choice expected utility on ties | 0.466667 |
| Tie-policy lift vs forced choice | 0.233333 |

## Interpretation

The projection hypothesis survived this harder toy test:

- bare ambiguous tokens activated multiple candidate basins,
- context constraints resolved the surface ambiguity,
- incremental evidence moved the active basin toward the expected attractor,
- held-out compositions such as `black_cat` and `river_bank` composed without
  requiring memorized composition labels,
- perturbation produced measurable ambiguity and later transition boundaries.

The important methodological result is the tie correction.

The earlier metric treated:

```text
target basin tied with competitor basin
```

as a transition. That was a forced-choice classifier prior.

The corrected experiment separates:

```text
stable ambiguity
```

from:

```text
true transition
```

In this toy substrate, additive competitor evidence created ambiguity at one
competitor constraint but did not create a true transition. Replacement evidence
created ambiguity at one competitor constraint and true transition at three
competitor constraints.

When tied states were evaluated as decision states, a hold/no-op policy beat
forced choice by `+0.233333` expected utility.

## Decision

Do not treat ties as failures by default.

Future semantic-memory experiments must report tied-basin states separately and
evaluate downstream policy options:

- hold/no-op,
- request more evidence,
- continue gathering context,
- force choice only when the task requires it.

This is now part of the anti-prior guardrail for this research line. A single
label is not always the correct internal state.

## Next Work

The next mechanism experiment should learn or fit the tie policy instead of
hand-coding hold/no-op utility.

It should also test noisier support fields where ambiguity may be useful,
harmful, or unstable depending on the downstream task.
