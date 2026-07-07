# Evidence Collection — Episteme Recurrence-Sensitive Memory Substrate

This directory collects all evidence referenced by the episteme paper. Every claim
in `final_synthesis.md` points to specific files here. Provenance is preserved:
each file is labeled by which project produced it.

## Provenance Map

```text
episteme/      — this project (the paper's subject)
  code/          all experiment implementations (reproducible)
  results/       raw JSON outputs (primary evidence)
  reports/       human-readable analysis derived from results
  ldgr_history/  LDGR project observations/artifacts used as memory content
  phase0/        the phase-0 toy semantic retrieval benchmark
topology/      — parent project (identity-free recurrent topology memory)
  reports/       findings and meta-analysis
  source/        canonical experiment implementations (the ports episteme inherits)
ecphory-2/     — parent project (trajectory vs semantic memory split)
  docs/          architecture decisions and experimental reports
  results/       raw JSON including the run-46 ceiling experiments
```

## Claim → Evidence Map

Each numbered claim lists: the claim, the supporting files, and the headline metric.

### Lineage claims

#### C0. Identity-free recurrent topology is a valid constraint memory.
- evidence: `topology/reports/meta_analysis.md`, `topology/reports/final_findings.md`
- code: `topology/source/recurrence_topology_experiment.py`, `topology/source/set_valued_prediction_experiment.py`
- metric: set-valued retrieval N=3, coverage 0.88, inclusion 1.0, compression 23.9x

#### C1. Coarse-to-fine two-stage filtering is the production pattern.
- evidence: `topology/reports/two_stage_granularity_experiment.md`
- code: `topology/source/two_stage_granularity_experiment.py`
- metric: entity→command_refined, utility 0.689, mean final set 2.85 vs single-stage coarse 3.36

#### C2. The typed-edge question was left open (topology phase 4).
- evidence: `topology/reports/meta_analysis.md` (section "Methodological Guardrails": topology deliberately strips relation types)

#### C3. Trajectory and semantic memory are distinct retrieval problems; the graph is a projection of basins.
- evidence: `ecphory-2/docs/trajectory-vs-semantic-memory-architecture.md`

#### C4. Unlabeled constraint basins recover human labels above shuffled chance.
- evidence: `ecphory-2/results/unlabeled-constraint-basin-pilot.json`, `ecphory-2/docs/unlabeled-constraint-basin-pilot.md`
- metric: query accuracy 1.0 vs shuffled 0.0; basin purity 1.0 at threshold 0.40

#### C5. Agreement-gated dual lookup beats naive union.
- evidence: `ecphory-2/results/promoted-dual-lookup-control.json`, `ecphory-2/docs/promoted-dual-lookup-control-experiment.md`
- metric: agreement-gated 1.0 vs naive union 0.567 (worse than labeled-only 0.700)

#### C6. Run-46 ceiling: synthetic relaxation could not beat a label-overlap index.
- evidence: `ecphory-2/results/scale-local-dynamics-vs-index-retrieval.json`, `ecphory-2/results/scale-trajectory-to-semantic-basin-bridge.json`
- metric: `any_broad_metric_win_for_relax: False`; relaxation's only unique act is reconstructive completion, not retrieval advantage

### Episteme core claims

#### C7. Typed edges carry discriminating information beyond pure topology.
- evidence: `episteme/results/basin_results.json`, `episteme/reports/findings.md`
- code: `episteme/code/signature.py` (typed_canonical_signature vs label_free), `episteme/code/bench_relaxation.py`
- metric: polysemy disambiguation typed 1.0 vs labelfree 0.25; corrupt stability typed 0.69 vs 0.29
- this answers C2 (topology's open phase-4 question)

#### C8. Set-valued basin retrieval generalizes to typed content.
- evidence: `episteme/results/basin_results.json`, `episteme/results/bench_twostage` (two-stage report in `episteme/reports/findings.md`)
- code: `episteme/code/relaxation.py`, `episteme/code/bench_twostage.py`
- metric: held-out inclusion 1.0, bundle reduction 36x (synthetic)

#### C9. Noise collapse was a matcher failure, not a representation failure.
- evidence (diagnosis correction): `episteme/code/smoke_identity.py`, `episteme/results/` (no separate JSON; see `episteme/reports/findings.md` "Later Correction" section)
- evidence (ablation): `episteme/results/matcher_ablation_results.json`
- code: `episteme/code/identity_regimes.py`, `episteme/code/matcher_relaxation.py`, `episteme/code/bench_matcher_ablation.py`
- metric: identity smoke showed canonical stable to insertion 9/9, role_payload(local) worse (0/9, 4/9); greedy noise@1 0.60 → DP/LCS 0.75

#### C10. DP/LCS skip-capable alignment repairs neutral-noise collapse without touching identity.
- evidence: `episteme/results/dp_lcs_surface_results.json`, `episteme/reports/dp_lcs_surface_report.md`
- code: `episteme/code/matcher_relaxation.py` (align_dp), `episteme/code/bench_dp_lcs_surface.py`
- metric: noise transition greedy mag 2 → DP/LCS mag 3; polysemy 1.0 unchanged; reduction 34x unchanged

#### C11. Deletion brittleness is a narrow identity boundary (first-occurrence renumbering).
- evidence: `episteme/results/deletion_controls_results.json`, `episteme/reports/deletion_controls_report.md`
- code: `episteme/code/bench_deletion_controls.py`
- metric: canonical first-recurring deletion 0.5, repeat deletion 1.0; anchored_recurring REJECTED (polysemy 1.0→0.43); edge_sequence/bag robust but lose polysemy (0.86/0.57)

#### C12. Behavioral relevance: the deletion boundary is often tolerable on real content.
- evidence: `episteme/results/behavioral_relevance_results.json`, `episteme/reports/behavioral_relevance_report.md`
- code: `episteme/code/bench_behavioral_relevance.py`
- memory content: `episteme/ldgr_history/observations.jsonl`, `episteme/ldgr_history/artifacts.jsonl`
- metric: clean 1.0/32x; plausible survival 0.8884 (0.8644 with first-rec deletion); control/adversarial 0.4479

#### C13. Payload-graph refinement beats flat overlap where flat overlap should fail.
- evidence: `episteme/results/payload_graph_refinement_results.json`, `episteme/reports/payload_graph_refinement_report.md`
- code: `episteme/code/bench_payload_graph_refinement.py`
- metric: same-node rewired decoys — node_bag top1 0.0 (decoys tie), content_graph top1 0.7969 aggregate / 1.0 on core+partial+noisy
- this continues C6 (ecphory-2's run-46 escape generalizes)

## Reproduction

All episteme experiments run from `experiments/motif-topology-retrieval/`:

```bash
# smokes (fast, verify mechanisms)
python3 smoke.py
python3 smoke_generator.py
python3 smoke_relaxation.py
python3 smoke_identity.py        # C9 diagnosis correction
python3 smoke_matcher.py         # C9 matcher mechanism

# benchmarks (produce the result JSONs)
python3 bench_relaxation.py              # C7, C8
python3 bench_twostage.py                # C8 two-stage
python3 bench_noise_taxonomy.py          # C9 precursor
python3 bench_matcher_ablation.py        # C9 ablation
python3 bench_dp_lcs_surface.py          # C10
python3 bench_deletion_controls.py       # C11
python3 bench_behavioral_relevance.py    # C12
python3 bench_payload_graph_refinement.py # C13
```

Seed for all experiments: `20260706`. Corpus: `build_generated_graph_with_polysemy(n_disjoint_families=20, n_polysemy_bases=10, instances_per=3)` for synthetic; LDGR project history (17 observations, 40 artifacts) for behavioral/payload-graph.

## File Inventory

```text
episteme/
  code/        19 Python files (signature, relaxation, matchers, 8 benchmarks, smokes, generator)
  results/     11 JSON result files (primary evidence)
  reports/     9 markdown reports + program doc
  ldgr_history/  observations.jsonl, artifacts.jsonl, manifest.json
  phase0/      10 files (toy benchmark)

topology/
  reports/     12 markdown reports + design principles
  source/      7 Python files (the ports episteme inherits)

ecphory-2/
  docs/        8 architecture/experiment docs
  results/     7 JSON reports + trajectory-memory-lookup multi-stage results
```

## Frozen State

```text
GitHub:   https://github.com/hydra-dynamix/episteme
Hugging Face: https://huggingface.co/datasets/Bakobiibizo/episteme-evidence
```
