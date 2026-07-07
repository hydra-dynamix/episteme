# Project Meta-Analysis: Topology as Constraint-Based Temporal Motif Memory

## Executive Summary

The project has moved from a narrow topology-only falsification test into a working prototype and early LDGR corpus benchmark.

The strongest current claim is:

> Persistent recurrent topological motifs can act as an auxiliary constraint-based memory substrate: from partial topology, they retrieve bounded sets of structurally compatible future continuations, reducing downstream search space without using semantic labels, embeddings, gradients, or learned model weights.

This is **not** a claim that topology alone is a primary learning system, semantic abstraction mechanism, or final reasoning engine. The useful role is as an add-on retrieval/constraint layer that compresses the candidate continuation space for another system to score, reason over, or select from.

## Current Status

### Supported or partially supported findings

1. Simple unlabeled paths are too trivial and fail controls.
2. Nontrivial recurrence, branching, convergence, and repeated substructure give topology something meaningful to store.
3. Automorphism-aware controls are essential; automorphic equivalents should activate, not be treated as negatives.
4. Complete recurrent motif recognition passed hard length/node/degree-matched non-isomorphic controls.
5. One-step prediction is too weak because hard controls can share valid early prefixes.
6. Multi-step/full-suffix prediction rejects shared-prefix divergences in the hand-designed motif set.
7. Dense generated motif libraries create prefix ambiguity, falsifying universal exact prediction.
8. Set-valued retrieval is the better formulation: bounded suffix sets preserve the true continuation while compressing the search space.
9. At 100-150 synthetic motifs, bounded retrieval remains useful with low hard-control acceptance.
10. On available LDGR event logs, the prototype preserves true continuations for covered repeated motifs while trading coverage for large search reduction.

### Main boundary discovered

The system works best when evaluated as:

```text
partial topology -> bounded compatible continuation set -> downstream selector/reasoner
```

not as:

```text
partial topology -> unique future answer
```

## Major Experiment Progression

### 1. Minimal Path Topology

Outcome: `partially_supported_control_failures`

The path motif `A -> B -> C` canonicalized to a generic unlabeled path:

```text
0 -> 1 -> 2
```

This activated symbolically novel positives, but also activated shuffled and random controls. This showed simple paths contain insufficient discriminating topology.

### 2. Recurrent Topology

Motifs tested:

```text
A -> B -> A -> C -> A
A -> B -> D -> A -> C -> D -> A
A -> B -> A -> C -> A -> B -> A -> C
```

Outcome after automorphism-aware correction: `supported`

Key results:

- positives activated,
- length-matched paths rejected,
- degree-matched non-isomorphic controls rejected,
- random false activation remained below threshold.

The important methodological correction was recognizing that branch-swapped controls can be automorphic and should not be negatives under identity-free topology.

### 3. Motif Completion and Prediction

One-step completion produced partial support:

- clean positives predicted the correct next canonical state,
- invalid hand-authored completions were rejected,
- but degree-matched controls sometimes shared valid one-step prefixes.

Multi-step completion then produced a stronger supported result:

- degree-matched h1 acceptance: `0.133333`
- degree-matched h2 acceptance: `0.0`
- degree-matched full-suffix acceptance: `0.0`

Interpretation: local next-step prediction is ambiguous; full-suffix trajectory constraints are discriminative in the small motif set.

### 4. Generalized Generated Motif Suite

Outcome: `partially_supported_control_failures`

Across 50 generated motifs:

- positive full acceptance: `1.0`
- prefix-divergent full acceptance: `0.136564`
- degree-matched full acceptance: `0.190476`
- ambiguous-prefix rate: `0.905237`

This falsified the broad claim that dense motif libraries generally support exact future prediction from short prefixes. The missing condition was prefix identifiability.

### 5. Minimum Discriminative Prefix

Outcome: `falsified_identifiability_failed`

For 50 generated motifs:

- unique-identifiable motif rate: `0.70`
- mean observation fraction when unique: `0.677041`
- mean remaining prediction length when unique: `2.828571`
- control acceptance after unique prefix: `0.0`

Interpretation: uniqueness is powerful when achieved, but not guaranteed. Universal unique prediction is too brittle.

### 6. Set-Valued Prediction

Outcome: `supported`

Best operating point: suffix-set size `N=3`.

At N=3:

- coverage: `0.88`
- positive inclusion: `1.0`
- full-control acceptance: `0.0`
- mean suffix set size: `2.090909`
- mean remaining prediction length: `3.181818`
- compression factor: `23.913043x`

Interpretation: topology retrieves a compact set of possibilities rather than a single answer.

## Five Follow-Up Iterations on Set-Valued Retrieval

A later five-iteration sequence explored set-valued retrieval and disambiguation.

1. **Passive suffix-set disambiguation**: additional observations reduced ambiguity but did not always collapse it.
   - mean set size: `2.090909 -> 1.409091` after one observation
   - eventual collapse: `0.795455`

2. **Active disambiguation**: active query selection improved collapse rate, but modestly.
   - passive collapse: `0.727273`
   - active collapse: `0.886364`
   - active-better rate: `0.159091`

3. **Motif density sensitivity**: ambiguity increases with library density.
   - ambiguity growth from 10 to 75 motifs: `0.354125`
   - N=3 at 75 motifs: coverage `0.813333`, control acceptance `0.0`

4. **Dense library set limits**: bounded sets still compress dense libraries.
   - 100 motifs, N=5: coverage `0.90`, compression `30.405405x`
   - 100 motifs, N=10: coverage `0.97`, compression `16.247906x`

5. **Dense set control specificity**: hard-control specificity remained good at 100 motifs.
   - N=5 control acceptance: `0.023256`
   - N=10 control acceptance: `0.025575`

## Auxiliary Constraint-Layer Prototype

Implemented prototype:

- `src/topology_constraint_memory.py`
- `examples/topology_constraint_memory_demo.py`
- `docs/topology_constraint_memory_interface.md`
- `docs/topology_constraint_memory_operating_modes.md`

Core API:

```python
memory.observe(sequence)
result = memory.query(partial_sequence, mode="balanced")
memory.record_query_outcome(result, "hit")
memory.update_from_confirmed_continuation(partial, continuation)
```

Operating modes:

- `conservative`: small candidate sets, more abstention.
- `balanced`: default.
- `exploratory`: larger candidate sets, more recall.
- `adaptive`: adjusts candidate bound from actual-use feedback.

Synthetic benchmark:

- 150 motifs
- 450 training sequences
- 131 queries
- true inclusion: `1.0`
- mean candidate set size: `3.396947`
- search reduction: `44.157303x`

Constraint-layer benchmark across synthetic library sizes:

| Library size | Preferred N | Coverage | Mean set size | Search reduction | True inclusion |
|---:|---:|---:|---:|---:|---:|
| 50 | 3 | 0.88 | 2.090909 | 23.913043x | 1.0 |
| 100 | 5 | 0.90 | 3.288889 | 30.405405x | 1.0 |
| 150 | 5 | 0.873333 | 3.396947 | 44.157303x | 1.0 |

## LDGR Corpus Benchmark

The prototype was applied to available local LDGR SQLite databases.

### Dataset discovery

The requested `/mnt/d`, `/mnt/e`, and `~/repos/benchmarks*` benchmark directories were not present in the runtime environment at the time of the initial scan. A scan of `/home/bakobi/repos` found 28 LDGR databases.

These were organized into:

```text
data/ldgr-benchmarks/
/mnt/nas/data/ldgr/benchmarks/
```

and uploaded privately to Hugging Face:

```text
Bakobiibizo/ldgr-benchmark-dbs
commit 79ce8aa2d09f4d331e533a0c7d2758574dd2e061
```

### Contamination audit

The collected dataset is **not benchmark-only**.

Composition:

- strict benchmark DBs: 1
- research/experiment DBs: 15
- general project/demo DBs: 12

The only strict `/research/benchmarks/` DB currently present had zero LDGR events/work items, so current LDGR scores should be described as **available local LDGR corpus** scores, not strict benchmark-only scores.

Filtered results with refined tokens, window `8..12`, stride `3`, max candidates `100`:

| Subset | DBs | Queries | Covered | True inclusion | Reduction |
|---|---:|---:|---:|---:|---:|
| all collected | 28 | 587 | 286 | 1.0 | 51.50x |
| strict benchmark | 1 | 0 | 0 | 0.0 | 0.0x |
| research experiments | 15 | 170 | 64 | 1.0 | 51.17x |
| HEU worktrees/campaigns | 12 | 146 | 77 | 1.0 | 13.68x |

## LDGR Tokenization and Configuration Findings

LDGR event logs were converted to temporal tokens. Coarse tokens use:

```text
entity_type:event_type
```

Refined content-safe tokens add categorical detail without raw content, for example:

```text
observation:add:failure
observation:add:constraint
observation:add:result
artifact:add:report
artifact:add:validator
decision:record:continue
run:end:pass
run:end:partial
```

No raw observation/artifact/decision text is injected into topology motifs.

Configuration sweep dimensions:

- token mode: `coarse`, `refined`
- window: `5..8`, `5..12`, `8..12`
- stride: `1`, `3`
- max candidates: `10`, `25`, `50`, `100`

Best practical coverage/high-precision configuration:

```text
token_mode=coarse
window=8..12
stride=3
max_candidates=100
```

Metrics:

- coverage: `0.508868`
- true inclusion: `1.0`
- mean candidate set size: `46.710456`
- search reduction: `53.808586x`

Best refined-token coverage configuration:

```text
token_mode=refined
window=8..12
stride=3
max_candidates=100
```

Metrics:

- coverage: `0.493955`
- true inclusion: `1.0`
- mean candidate set size: `45.395105`
- search reduction: `50.661943x`

Pattern:

- `8..12` event windows outperform shorter windows for coverage.
- `stride=3` gives more reusable motifs and better coverage.
- `stride=1` gives huge search reduction but low coverage.
- coarse tokens maximize reuse.
- refined tokens improve interpretability and remain competitive at higher candidate bounds.

## Pi Extension

Created project-local Pi extension:

```text
.pi/extensions/ldgr-topology.ts
```

It registers:

- `ldgr_topology_benchmark`
- `ldgr_topology_sweep`
- `/ldgr-topology-benchmark`

The extension is ready for `/reload` and interactive Pi smoke testing.

## Methodological Guardrails

The core topology experiments and prototype preserve these constraints:

- no machine learning models,
- no embeddings,
- no gradients,
- no LLMs inside the memory mechanism,
- identity-free canonicalization of event symbols,
- automorphism-aware controls,
- hard non-isomorphic controls where feasible,
- deterministic runs and stored artifacts.

The LDGR refined tokenizer does use broad human-readable categories, but not raw content. This makes LDGR motifs more interpretable while avoiding direct lexical/content matching.

## Current Limitations

- Strict benchmark-only LDGR data is not yet available locally; current scores are corpus-snapshot scores.
- LDGR coverage depends strongly on candidate bound and tokenization.
- Refined categorical tokenization is heuristic and should be iterated against larger LDGR datasets.
- The prototype is in-memory and scans consolidated motifs directly; large-scale use should add prefix indexing.
- Actual-use optimization is only partially implemented through operating-mode feedback counters.
- The system reduces candidate space but does not select final answers.
- No semantic reasoning, causal reasoning, or value estimation is performed by the topology layer.

## Best Current Interpretation

The project supports this narrow, useful claim:

> Persistent recurrent topological motifs can provide a model-free constraint memory that compresses future continuation search by retrieving bounded sets of structurally compatible possibilities. This is useful as an auxiliary layer for a downstream learner/reasoner, not as a standalone learning system.

## Final Corpus / Benchmark Update

The NAS corpus is now organized under:

```text
/mnt/nas/data/ldgr/benchmarks
```

with split folders:

```text
splits/benchmarks  # 128 DBs
splits/coding      # 94 DBs
splits/research    # 18 DBs
```

The current project LDGR database was added back into the research split. The initial benchmark-only rerun against `splits/benchmarks` used `window=8..12`, but the actual-use feedback simulation found a stronger long-window operating point:

```text
token_mode=refined
window=30..36
stride=6
max_candidates=100
coverage=1.0
true inclusion=1.0
mean candidate set size=11.522587
search reduction=554.910108x
utility/query=0.942387
```

This updates the main practical interpretation: topology recollection appears most useful for longer-horizon workflow-state recollection, not very short event continuation.

A minimal learned-ranker follow-up tested whether a dumb model can improve discrimination over topology-generated candidates:

```text
reports/dumb_learned_candidate_ranker.md
```

Summary:

- The model was a no-dependency online linear pairwise ranker with a learned abstention threshold.
- It did not replace the topology index; it only scored generated candidates.
- On refined tokens, learned thresholding slightly improved utility/query from `0.100679` to `0.103098`; no-threshold learning was worse.
- On `artifact_ext_refined`, learned thresholding improved utility/query from `0.098913` to `0.113953`, mostly by abstaining from false emits rather than improving top-1 recall.
- Conclusion: weak positive signal for learned discrimination/abstention, but not enough to justify heavy model training without richer features.

An outcome-weighted recollection follow-up tested whether success/failure/ambiguous outcomes should globally weight motif support:

```text
reports/outcome_weighted_recollection.md
```

Summary:

- Global outcome weighting was not supported.
- On the primary long-window mixed workload, unweighted support was best across practical bounds.
- At bound 25, unweighted utility/query was `0.702080`; success/failure weighting variants were `0.701486`.
- Success boosting worsened mean expected rank from `1.974821` to `2.102197`.
- Recommendation: use outcome as a query-conditioned filter/reranker, not as a global support multiplier.

A two-stage granularity follow-up tested whether a coarse recall pass followed by a fine filter can narrow the field:

```text
reports/two_stage_granularity_experiment.md
```

Summary:

- Best two-stage strategy was `entity -> command_refined` with utility/query `0.688795` and mean final candidate set `2.846763`.
- Best single-stage baseline was `coarse` with utility/query `0.686217` and mean set `3.362502`.
- The gain was modest but positive: two-stage filtering reduced candidate set size without losing hits.
- Practical rule: use entity/coarse first-pass recall, then command/artifact fine filters with cost-aware candidate bounds.

A representation granularity follow-up answered whether finer-grained detail helps encoding:

```text
reports/representation_granularity_sweep.md
```

Summary:

- Finer detail is not automatically better; maximum categorical detail fragmented motifs and lowered utility.
- Repeated-only best utility was `entity` at `0.947621`.
- Mixed repeated+novel best utility was selective `command_refined` at `0.732154`, followed by `artifact_ext_refined` at `0.730578`; baseline refined was `0.727191`; full categorical fell to `0.690758`.
- Practical rule: use coarse structural events plus targeted continuation-relevant categorical refinements, not raw/maximal detail.

A later cost-aware/runtime follow-up answered the remaining research questions:

```text
reports/cost_aware_adaptive_retrieval.md
```

Summary:

- Mixed repeated+novel workload remained positive: utility/query `0.729371` at bound `100` with 4051 hits, 227 false answers, and 773 good abstentions.
- Cost-aware adaptation selected the oracle bound in tested regimes: cost `0.005 -> 100`, `0.025 -> 35`, `0.1 -> 10`.
- Long-window results held across token modes: entity/coarse/refined all reached coverage `1.0` with utility/query around `0.94` on repeated-only workload.
- Prefix indexing preserved identical candidate sets and gave `72.549046x` speedup on a 1000-query sample.
- Pi extension smoke passed and wrote the expected long-window benchmark result.

A concise final synthesis is available in:

```text
reports/final_findings.md
```

## Final Claim Review and Operator Guidance

The final claim map and operations handoff for the research program are now recorded in:

```text
docs/research_program/claim_review_final.md
docs/research_program/operator_guide.md
```

These documents satisfy the final review requirements by linking supported, falsified, inconclusive, and speculative claims to primary evidence artifacts and decision gates (`req.01`), documenting operator commands/corpora/artifacts/provenance workflow (`req.02`), and listing remaining unknowns, unavailable baselines, and out-of-scope claims (`req.03`). Manual claim-link verification is recorded in the claim review (`test.02`); raw `results/*.json` and `results/*.jsonl` remain the primary evidence and are not replaced by this summary.

## Recommended Next Work

1. **Split and relabel LDGR dataset manifests**
   - `strict_benchmark`
   - `research_experiment`
   - `project_workflow`
   - `all_corpus`

2. **Smoke-test the Pi extension**
   - load with `/reload`,
   - run `ldgr_topology_benchmark`,
   - verify runtime integration.

3. **Actual-use feedback simulation**
   - compare conservative, balanced, exploratory, and adaptive modes on downstream utility,
   - optimize from selected/hit/miss/abstention outcomes rather than offline replay only.

4. **Relationship-aware LDGR tokenization**
   - add lifecycle/run/artifact/observation context without raw content leakage,
   - compare against current best coarse/refined configurations.

5. **Scale with the NAS dataset**
   - incorporate additional LDGR DBs pushed to `/mnt/nas/data/ldgr/benchmarks`,
   - regenerate manifests and split reports.

## Validation Evidence

Latest validation command:

```text
dev run py_check
```

Recent observed state:

- Ruff format passed.
- Ruff lint passed.
- Mypy passed.
- Pytest passed: `44 passed` after operating-mode interface work.
- Earlier benchmark expansions passed up to `41` tests for LDGR benchmarking and `38` tests for the synthetic prototype benchmark.

Key reproducible commands:

```bash
uv run python src/recurrence_topology_experiment.py
uv run python src/multi_step_completion_experiment.py
uv run python src/set_valued_prediction_experiment.py
uv run python src/constraint_layer_search_reduction_experiment.py
uv run python src/ldgr_dataset_benchmark.py --token-mode refined --min-len 8 --max-len 12 --stride 3 --max-candidates 100
uv run python src/ldgr_configuration_sweep.py
```
