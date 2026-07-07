# Dual Memory Semantic Neighborhood Pilot

Date: 2026-07-06

Starting checkpoint: `docs/trajectory-vs-semantic-memory-architecture.md`

## Purpose

This pilot keeps the two memory substrates separate while making them composable:

```text
trajectory topology lookup
-> motif
-> semantic constraints
-> semantic neighborhood lookup
```

The goal is not to merge trajectory and semantic memory. The goal is to make trajectory motifs usable as post-lookup semantic constraints.

## Substrates

Trajectory memory:

- lookup key: identity-free temporal prefix topology,
- output: motif plus semantic constraints hydrated after lookup,
- question answered: what is probably happening?

Semantic memory:

- lookup key: unordered labeled constraints,
- output: compatible concept neighborhood,
- question answered: what does that mean?

## Experiment

Script:

`scripts/run_dual_memory_semantic_neighborhood_pilot.py`

Result:

`results/dual-memory-semantic-neighborhood/report.json`

The pilot contains three trajectory motifs:

- `enemy_expanding_left`
- `core_pressure`
- `economy_boom`

Each motif emits semantic constraints after trajectory lookup. Those constraints narrow the semantic query space.

## Results

| Metric | Value |
| --- | ---: |
| Query count | 3 |
| Trajectory motif accuracy | 1.000000 |
| Mean trajectory evidence count | 2.000000 |
| Semantic neighborhood expected-concept recall | 1.000000 |
| Baseline neighborhood recall without trajectory | 1.000000 |
| Mean top-score lift from trajectory constraints | 0.000000 |
| Mean top-margin lift from trajectory constraints | 0.111111 |

Important nuance:

- The trajectory stage works: motif accuracy is `1.0`.
- The semantic stage works as neighborhood retrieval: expected concepts are present in the compatible neighborhood.
- Baseline semantic-only constraints are broad enough to include expected concepts too, so recall alone does not show lift.
- Trajectory constraints increase top-score margin by `0.111111`, which is a narrowing/confidence signal.
- Single top-concept recall is not the right primary metric for semantic memory because semantic lookup returns neighborhoods, not one canonical path or one canonical winner.

## Interpretation

This pilot supports the desired structure:

```text
trajectory motif
-> semantic constraint set
-> compatible semantic neighborhood
```

It also confirms the architecture distinction:

- trajectory lookup should remain prefix/future oriented,
- semantic lookup should remain constraint/neighborhood oriented,
- the bridge should pass constraints after trajectory lookup.

The first semantic pilot should not be judged by whether one expected concept is ranked first. Semantic memory is not path retrieval. The better question is whether the retrieved neighborhood is compatible, useful, and narrowed by trajectory-derived constraints.

## Decision

Keep the dual-substrate structure.

Next semantic-memory work should improve the neighborhood objective, not collapse semantic memory into trajectory paths. Useful next metrics:

- neighborhood precision,
- neighborhood margin,
- constraint consistency,
- concept coverage at fixed neighborhood size,
- trajectory-derived narrowing versus broad semantic-only query.

The next implementation step should package the dual pipeline so either substrate can be run independently or composed:

1. trajectory motif lookup only,
2. semantic neighborhood lookup only,
3. trajectory motif -> semantic neighborhood narrowing.
