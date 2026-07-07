# Trajectory Memory Experimental Report

Date: 2026-07-06

Status: Batch report for the trajectory-memory, topology-prefix, evidence fixture, and internal-state prediction work completed so far.

## Vocabulary Boundary

This report uses the project vocabulary from `docs/vocabulary.md`.

- An LDGR work run is the research-work bookkeeping unit used to plan, implement, and document work.
- An experiment execution is a script/config/data execution that produces an empirical result.
- A validation execution is an experiment execution designed to test whether a behavior change holds under the intended trajectory-level target.
- An Orbit Wars episode is one simulated game/trajectory.
- A turn is one state/action transition inside an episode.
- A trace is a state-transition sequence signature.
- A result is an empirical output from an experiment or validation execution, not merely the successful completion of an LDGR work run.

All results below are offline retrieval, fixture, internal-state, or decision-ablation results unless explicitly labeled otherwise. We have not yet completed a behavioral Orbit Wars validation showing that this memory mechanism improves policy outcomes in live episodes.

## Research Objective

The working hypothesis is that temporal traces can act as non-semantic signatures for state-transition history. The traces should not carry semantics in the lookup key. Instead, a trace signature retrieves prior decision trees that made the same or similar transition decisions up to a point, producing a bundle of possible futures. Semantics may be attached to the retrieved evidence after lookup, then unpacked for interpretation, prediction, and control.

The target is not exact future event sequence reproduction. The target is trajectory-to-final-outcome prediction and, eventually, controllable behavior: state -> regime -> decision/action -> caused events -> next state -> outcome.

## Program Spine

The current program proceeded through these stages:

1. Establish a clean vocabulary and research boundary.
2. Define temporal traces as topology/signature lookup keys without semantic payload.
3. Generate trajectory-memory scenario records from Orbit Wars evidence.
4. Compare exact sequence, refined sequence, surface, and topology-prefix lookup.
5. Reproduce the original topology-style windowed prefix-to-suffix retrieval regime.
6. Select successful target futures instead of random futures.
7. Sweep refinement settings to trade recall against specificity.
8. Build a reusable evidence fixture that preserves successful and avoid-path evidence.
9. Build an internal-state prediction experiment that consumes retrieved evidence.
10. Interrogate sequence identity as a possible useful model feature rather than discard it as an undesired shortcut.
11. Add a configurable sequence-identity knob.
12. Run an offline decision ablation over predicted outcome probabilities.

## Primary Artifacts

- `docs/vocabulary.md`: run and result vocabulary.
- `docs/state-memory-trajectory.md`: initial trajectory-memory program notes.
- `docs/trajectory-memory-first-experiment.md`: first experiment design and lookup boundary.
- `docs/evidence-influenced-internal-state-experiment.md`: internal-state experiment design.
- `docs/sequence-identity-knob-case-study.md`: case study for the sequence-identity feature and invariant.
- `experiments/orbit_wars_self_play_evidence/scenario_families/trajectory_memory_v1.json`: trajectory-memory scenario family.
- `scripts/generate_trajectory_memory_scenarios.py`: candidate/scenario record generation.
- `scripts/run_sequence_signature_lookup_experiment.py`: sequence/surface/topology lookup comparisons.
- `scripts/evaluate_success_target_topology_retrieval.py`: successful-target topology retrieval.
- `scripts/run_windowed_topology_suffix_retrieval.py`: original topology-style windowed suffix retrieval.
- `scripts/sweep_windowed_topology_refinement_params.py`: refinement parameter sweep.
- `scripts/build_windowed_suffix_evidence_fixture.py`: reusable evidence fixture builder.
- `scripts/run_evidence_influenced_internal_state_experiment.py`: internal-state outcome prediction experiment.
- `scripts/run_internal_state_decision_ablation.py`: offline decision ablation over internal-state predictions.
- `results/trajectory-memory-fixtures/windowed_suffix_evidence`: reusable evidence fixture.

## Scenario Generation

`scripts/generate_trajectory_memory_scenarios.py` materialized 794 candidate records into:

- `results/trajectory-memory-scenarios/trajectory_memory_v1_candidate_records.jsonl`
- 8 scenario member records
- train/heldout split: 4 train and 4 heldout scenario members

Candidate rows include a `temporal_topology` structure containing:

- event symbols derived from feature bins as opaque symbols,
- `prefix_signature`,
- `full_window_signature`,
- `remaining_suffix_signature`,
- `remaining_suffix_symbols`,
- a lookup boundary at `temporal_topology.prefix_signature.key`.

The key boundary is important: semantic labels are not inserted into the lookup key. They are attached only after retrieval.

## Lookup Results

### Initial strict and surface comparisons

The first lookup experiments compared increasingly relaxed signatures over heldout candidates:

| Method | Covered heldout | Coverage | Largest train neighborhood | Mean future transition shapes |
| --- | ---: | ---: | ---: | ---: |
| Strict sequence | 17 / 385 | 0.044156 | 3 | 2.235294 |
| Transition feature sequence | 64 / 385 | 0.166234 | 18 | 3.359375 |
| Surface | 83 / 385 | 0.215584 | 19 | 5.819277 |
| Topology prefix exact | 15 / 385 | 0.038961 | 4 | 2.466667 |

Interpretation: strict cumulative sequence matching was too narrow. Surface relaxation improved coverage but pulled broader neighborhoods. Exact topology-prefix matching remained narrow because it was not yet using the original topology experiment's windowed prefix-to-suffix regime.

### Original topology comparison

The prior topology experiment's best practical regime used:

- `token_mode=refined`
- `window=8..12`
- `stride=3`
- `max_candidates=100`
- `min_support=2`

Its reported metrics were:

- queries: 2772
- covered: 855
- coverage: 0.308442
- true inclusion on covered queries: 1.0
- mean candidate set size: 51.187135

The important correction is that the 100% figure was inclusion on covered queries, not 100% global coverage.

## Successful Target Selection

Randomly selecting futures is not meaningful for this program. We shifted target selection toward futures that result in success.

For the success-target exact topology-prefix retrieval, success was defined post-lookup by:

- `remaining_turns > 0`
- `advantage_delta_to_window_end >= threshold`
- `final_window_regime == AHEAD`

At `success_delta=0.1`:

- selected successful heldout target suffixes: 183
- covered exact topology-prefix targets: 15
- coverage: 0.081967
- successful evidence included on covered: 15 / 15 = 1.0
- exact suffix included on covered: 0 / 15 = 0.0
- mean candidate set size: 2.466667
- mean non-successful futures: 0.0

Sensitivity by success threshold:

| Success delta | Covered | Successful evidence on covered | Exact suffix on covered | Mean non-successful futures |
| ---: | ---: | ---: | ---: | ---: |
| 0.05 | 15 | 1.0 | 0.0 | 0.0 |
| 0.10 | 15 | 1.0 | 0.0 | 0.0 |
| 0.20 | 15 | 1.0 | 0.0 | 0.0 |
| 0.30 | 15 | 1.0 | 0.0 | 0.4 |
| 0.50 | 15 | 0.8 | 0.0 | 1.0 |

Interpretation: exact trace matching has low coverage, but when it fires under this success-target filter it returns clean successful evidence. It does not reproduce the exact suffix, which is acceptable because exact suffix reproduction is not the primary target.

## Windowed Topology Suffix Retrieval

We then restored the original topology lookup pattern as the first retrieval step: sliding windows, prefix match, suffix evidence retrieval. This changed the behavior substantially.

Base configuration:

- `window=8..12`
- `stride=3`
- `prefix_fraction=0.5`
- `min_support=1`
- `success_delta=0.1`

Results:

- selected successful target windows: 287
- covered: 252
- coverage: 0.878049
- successful evidence included on covered: 250 / 252 = 0.992063
- exact suffix included on covered: 112 / 252 = 0.444444
- mean candidate set size: 43.599206
- mean successful futures: 21.107143
- mean avoid futures: 22.492063
- single successful trace rate on covered: 0.047619

Longer prefix refinement:

- `prefix_fraction=0.8`
- selected successful target windows: 267
- covered: 124
- coverage: 0.464419
- successful evidence included on covered: 0.967742
- exact suffix included on covered: 0.766129
- mean candidate set size: 24.637097
- mean successful futures: 7.758065
- mean avoid futures: 16.879032
- single successful trace rate: 0.306452

Interpretation: the restored topology regime pulls broad evidence well. Increasing prefix length trades coverage for specificity and smaller bundles. The returned object is usually a bundle, not a single trace.

## Refinement Sweep

`scripts/sweep_windowed_topology_refinement_params.py` evaluated 180 configurations. All useful configurations fit into one of three operating modes:

| Mode | Window | Prefix fraction | Stride | Support | Success delta | Coverage | Success evidence on covered | Exact suffix on covered | Mean candidate set | Mean success-refined set | Single success trace |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| High recall | 8..12 | 0.5 | 1 | 1 | 0.1 | 0.912992 | 1.0 | 0.575718 | 131.295039 | 61.339426 | 0.018277 |
| Balanced sharp | 8..12 | 0.9 | 1 | 1 | 0.2 | 0.463526 | 0.967213 | 0.954098 | 37.701639 | 9.334426 | 0.180328 |
| Single-trace leaning | 12..16 | 0.9 | 2 | 1 | 0.2 | 0.173333 | 0.615385 | 0.826923 | 7.538462 | 1.576923 | 0.346154 |

Decision: do not choose one setting globally. Preserve modes as a reusable fixture because different questions require different evidence shapes.

## Evidence Fixture

The reusable fixture is rooted at:

`results/trajectory-memory-fixtures/windowed_suffix_evidence`

The fixture preserves both successful paths and avoid paths. Failures are not treated as contamination. They are evidence for paths to avoid.

| Mode | Objects | Coverage | Mean total evidence | Mean successful paths | Mean avoid paths | Aggregate successful-path weight | Exact target suffix bundle rate | Pure successful bundle rate | Single successful path rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| High recall | 766 | 0.912992 | 131.295039 | 61.339426 | 69.955614 | 0.467188 | 0.575718 | 0.263708 | 0.018277 |
| Balanced sharp | 305 | 0.463526 | 37.701639 | 9.334426 | 28.367213 | 0.247587 | 0.954098 | 0.396721 | 0.180328 |
| Single-trace leaning | 52 | 0.173333 | 7.538462 | 1.576923 | 5.961538 | 0.209184 | 0.826923 | 0.461538 | 0.346154 |

Interpretation: high recall is useful when we want broad evidence coverage. Balanced sharp is the best default for precise evidence bundles. Single-trace leaning is a narrow diagnostic mode, not a general retrieval setting.

## Internal-State Prediction

The internal-state experiment tests whether evidence can influence a model's prediction of final outcome. The target is trajectory outcome class, not exact future event sequence.

Variants:

- `no_memory`: state-only baseline.
- `topology_evidence`: uses retrieved evidence summary.
- `shuffled_evidence`: evidence control with evidence shuffled away from the original query.
- `positive_only`: only successful evidence branch.
- `avoid_only`: only avoid-path evidence branch.
- `sequence_identity_probe`: optional post-lookup exact-suffix support feature.

At `--sequence-identity probe`, the main topology model ignores exact suffix support while the probe reports what happens when that feature is added.

### Prediction results

| Mode | Variant | Mean prediction | Brier |
| --- | --- | ---: | ---: |
| Balanced sharp | no_memory | 0.515210 | 0.235252 |
| Balanced sharp | topology_evidence | 0.600727 | 0.200610 |
| Balanced sharp | shuffled_evidence | 0.601120 | 0.203470 |
| Balanced sharp | positive_only | 0.818655 | 0.047106 |
| Balanced sharp | avoid_only | 0.309489 | 0.511927 |
| Balanced sharp | sequence_identity_probe | 0.730941 | 0.129670 |
| High recall | no_memory | 0.503609 | 0.247223 |
| High recall | topology_evidence | 0.739057 | 0.095971 |
| High recall | shuffled_evidence | 0.734205 | 0.103395 |
| High recall | positive_only | 0.941547 | 0.009261 |
| High recall | avoid_only | 0.206655 | 0.664055 |
| High recall | sequence_identity_probe | 0.518300 | 0.279901 |
| Single-trace leaning | no_memory | 0.521284 | 0.229260 |
| Single-trace leaning | topology_evidence | 0.510376 | 0.284008 |
| Single-trace leaning | shuffled_evidence | 0.510658 | 0.285638 |
| Single-trace leaning | positive_only | 0.662608 | 0.131057 |
| Single-trace leaning | avoid_only | 0.386207 | 0.399356 |
| Single-trace leaning | sequence_identity_probe | 0.585732 | 0.244494 |

Observed sequence-identity lift versus topology evidence:

- Balanced sharp: +0.130214 prediction lift, Brier improves from 0.200610 to 0.129670.
- High recall: -0.220757 prediction lift, Brier worsens from 0.095971 to 0.279901.
- Single-trace leaning: +0.075356 prediction lift, Brier improves from 0.284008 to 0.244494.

Interpretation: evidence can influence internal-state prediction. Avoid-path evidence reliably lowers prediction in this success-target fixture. Sequence identity is not globally good or globally bad; it is a context-sensitive knob.

Important limitation: the fixture is success-target selected. Current Brier values are useful for comparing internal-state features inside this fixture, but they are not yet full classifier validation over balanced success and failure targets.

## Sequence Identity Knob

The exact sequence identity feature initially looked like an undesired shortcut. Under the project invariant, we did not discard it on that basis. We interrogated it as an optimization feature.

The resulting knob:

- `disabled`: omit exact suffix support entirely.
- `probe`: keep the main model pure and report exact-suffix support as a separate probe.
- `enabled`: include exact suffix support in `topology_evidence`.
- `auto`: enable where it improves the selected mode and disable where it hurts.

Policy matrix:

| Mode | Disabled Brier | Probe main Brier | Enabled Brier | Auto Brier | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| Balanced sharp | 0.200610 | 0.200610 | 0.129670 | 0.129670 | enable or auto |
| High recall | 0.095971 | 0.095971 | 0.279901 | 0.095971 | disable or auto |
| Single-trace leaning | 0.284008 | 0.284008 | 0.244494 | 0.244494 | enable or auto |

Decision: `auto` is the pragmatic default for decision experiments. Use `disabled` for pure topology tests. Use `probe` for audits where we want to interrogate the feature without changing the main path.

## Offline Decision Ablation

The decision ablation converts internal-state predictions into an offline action proxy:

- prediction >= 0.6: `follow_memory`
- prediction <= 0.4: `avoid_memory`
- otherwise: `defer`

Current limitation: because the fixture is success-target selected, this measures follow/defer/avoid behavior on positive targets. It is not yet a complete classifier or policy validation.

Auto policy results:

| Mode | Variant | Follow | Avoid | Defer | Utility |
| --- | --- | ---: | ---: | ---: | ---: |
| Balanced sharp | topology_evidence auto | 0.763934 | 0.160656 | 0.075410 | 0.603279 |
| Balanced sharp | topology_evidence disabled | 0.636066 | 0.281967 | 0.081967 | 0.354098 |
| High recall | topology_evidence auto | 0.642298 | 0.001305 | 0.356397 | 0.640992 |
| High recall | forced sequence identity | degraded | degraded | n/a | 0.069191 |
| Single-trace leaning | topology_evidence auto | 0.557692 | 0.365385 | 0.076923 | 0.192308 |

Interpretation: evidence-driven internal-state changes can alter follow/avoid/defer decisions. The sequence-identity knob materially improves balanced-sharp decisions and materially harms high-recall decisions when forced on.

## Decisions Made

1. Temporal traces remain non-semantic lookup signatures.
2. Semantics attach after lookup, not before.
3. Exact suffix reproduction is not the target; final trajectory outcome prediction is the target.
4. Random futures are not meaningful targets for this program; target futures should be outcome-relevant.
5. The original topology-style windowed prefix-to-suffix lookup is the correct first-stage retrieval regime.
6. Refinement is a second-stage operating-mode choice, not a global replacement for broad topology lookup.
7. Retrieved evidence should preserve both successful paths and avoid paths.
8. Failures are negative evidence, not contamination.
9. Sequence identity is a useful controllable feature, not an automatic disqualifier.
10. The sequence-identity feature must remain configurable by experiment mode.
11. Current internal-state and decision results are offline evidence. They motivate behavioral validation but do not replace it.

## Interpretation

The program has established a workable evidence path:

state-transition trace -> topology prefix lookup -> suffix evidence bundle -> post-lookup semantic unpacking -> internal-state prediction -> offline decision proxy

The strongest result so far is that topology-style retrieval can pull successful evidence at high inclusion rates on covered queries, and the evidence bundle can move an internal-state outcome prediction in interpretable directions. Positive-only evidence increases success prediction; avoid-only evidence decreases it; mixed evidence produces mode-dependent predictions.

The most important mechanism result is not a single metric. It is the discovery of a controllable retrieval/prediction surface:

- high recall: broad evidence, useful for coverage and robust inclusion;
- balanced sharp: best current default for evidence precision and decision proxy;
- single-trace leaning: narrow diagnostic mode;
- sequence identity: optional feature that helps sharp modes and hurts high-recall mode.

This gives us knobs for experiment design rather than one brittle lookup recipe.

## Limitations

- The current fixture is success-target selected and not outcome-balanced.
- The decision ablation is offline and proxy-based.
- We have not yet shown live Orbit Wars behavioral improvement from evidence-conditioned memory.
- Shuffled evidence remains close to topology evidence in some modes, which means some signal may come from aggregate fixture distribution rather than query-specific evidence.
- Exact suffix identity can be useful, but it must be separated from pure topology experiments to avoid confusing the source of the effect.

## Recommended Next Experiment

Build an outcome-balanced target fixture with both success and failure targets, preserving the same topology-first lookup boundary:

1. Select target windows from both successful and failed final outcomes.
2. Keep lookup keys semantic-free.
3. Retrieve topology suffix evidence using the established modes.
4. Preserve successful and avoid evidence branches.
5. Evaluate internal-state prediction against balanced final-outcome labels.
6. Re-run the sequence-identity policy matrix.
7. Only after that, run a behavioral validation execution in Orbit Wars episodes to test whether evidence-conditioned control improves trajectory outcomes.

This next step directly addresses the main limitation of the current report while preserving the mechanism that now appears useful.
