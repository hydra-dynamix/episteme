# Prior Work: Topology Constraint Memory Findings

Source: `../topology` (sibling project).
Primary documents: `topology/reports/final_findings.md`, `topology/reports/meta_analysis.md`,
`topology/reports/two_stage_granularity_experiment.md`, `topology/design-principals-and-invariants.md`.

This is a condensed record of the topology project's load-bearing findings, kept here so the
episteme substrate does not silently re-derive or contradict them. The topology project is the
lineage that episteme's typed relational substrate builds on.

## Core Claim (as it ended)

> Persistent recurrent topological motifs are useful as an auxiliary, model-free constraint
> memory. They do not replace learning or reasoning, but they can retrieve bounded sets of
> structurally compatible workflow continuations and substantially reduce downstream search
> space.

This is framed as **recollection / candidate-space compression**, not semantic prediction.

## Methodological Guardrails (preserved throughout)

- no machine learning models, no embeddings, no gradients, no LLMs inside the memory mechanism,
- identity-free canonicalization of event symbols,
- automorphism-aware controls (branch-swapped equivalents activate, they are not negatives),
- hard non-isomorphic controls where feasible,
- deterministic runs and stored artifacts.

These guardrails are the reason the project could make defensible negative claims later.

## Experiment Progression (the load-bearing arc)

### 1. Simple paths fail
`A -> B -> C` canonicalized to a generic unlabeled path activated shuffled/random controls.
Simple paths carry insufficient discriminating topology.

### 2. Recurrent topology works
Motifs with branching, convergence, repeated substructure (`A -> B -> A -> C -> A`, etc.)
passed automorphism-aware controls: positives activated, length/degree-matched non-isomorphic
controls rejected, random false activation below threshold.

### 3. One-step prediction is ambiguous; multi-step/full-suffix prediction discriminates
- degree-matched h1 acceptance: `0.133`
- degree-matched h2 acceptance: `0.0`
- degree-matched full-suffix acceptance: `0.0`

### 4. Dense motif libraries falsify universal exact prediction
Across 50 generated motifs:
- positive full acceptance: `1.0`
- prefix-divergent full acceptance: `0.137`
- ambiguous-prefix rate: `0.905`

The missing condition was **prefix identifiability**.

### 5. Unique prefix identifiability is not guaranteed
- unique-identifiable motif rate: `0.70`
- mean observation fraction when unique: `0.677`
- control acceptance after unique prefix: `0.0`

Powerful when achieved, but not universal.

### 6. Set-valued retrieval is the right formulation
At suffix-set size `N=3`: coverage `0.88`, positive inclusion `1.0`, full-control acceptance `0.0`,
mean suffix set `2.09`, compression `23.9x`.

Topology retrieves a compact **set** of possibilities, not a single answer.

## Set-Valued Retrieval + Disambiguation (5-iteration follow-up)

1. **Passive disambiguation**: extra observations reduced ambiguity but did not always collapse it
   (`2.09 -> 1.41`, eventual collapse `0.795`).
2. **Active disambiguation** improved collapse modestly (passive `0.727` vs active `0.886`).
3. **Motif density sensitivity**: ambiguity grows with library density (`0.354` growth 10 -> 75).
4. **Dense library set limits**: bounded sets still compress (100 motifs, N=5 -> coverage `0.90`,
   compression `30.4x`).
5. **Hard-control specificity** held at 100 motifs (control acceptance `0.023` at N=5).

## LDGR Corpus Benchmark

Applied the prototype to real LDGR event logs. Refined tokens are content-safe categories, e.g.
`observation:add:failure`, `artifact:add:report`, `decision:record:continue` — no raw text.

Best practical result, after actual-use feedback found the original `8..12` window underpowered:

```text
token_mode=refined, window=30..36, stride=6, max_candidates=100, min_support=2
query_sequences: 4051
coverage:        1.0
true inclusion:  1.0
mean candidate:  11.52
search reduction:554.9x
utility/query:   0.9424
```

Interpretation: topology recollection is most useful as **longer-horizon workflow-state
recollection**, not very short local event continuation.

## Two-Stage Coarse-to-Fine Granularity (directly relevant to episteme)

Tested: stage 1 coarse topology preserves recall; stage 2 finer topology narrows candidates.

Best two-stage: `entity -> command_refined`, utility/query `0.689`, mean final set `2.85`.
Best single-stage: `coarse`, utility/query `0.686`, mean set `3.36`.

Gain was modest (long windows were already specific), but the pattern held and the **direction**
mattered:

```text
first pass: as recurrence-preserving as possible (entity, not coarse)
second pass: introduce fine categorical detail only after coarse compatibility
main improvement: candidate-set reduction, not false-answer elimination
```

Bound sweep: too-strict final bounds cause bad abstentions; bounds ~10-100 preserve hits while
narrowing.

## Representation Granularity

Finer detail is not automatically better. Maximum categorical detail **fragmented** motifs and
reduced utility. Repeated-only best was `entity` (`0.948`); mixed best was selective
`command_refined` (`0.732`); full_categorical fell to `0.691`.

Rule: coarse structural events + a small number of proven continuation-relevant categorical
refinements, not raw/maximal detail.

## Outcome-Weighting (negative result)

Global success/failure outcome weighting was **not supported**. Unweighted support was best at
every practical bound; success boosting worsened mean expected rank (`1.97 -> 2.10`).

Recommendation: do not globally weight the index; use outcome as a query-conditioned
filter/reranker instead.

## Learned Ranker (weak signal)

A dumb online linear pairwise ranker over topology candidates gave only weak signal. Gain came
mostly from abstaining on false emits, not better top-1 ranking. Conclusion: not enough to justify
heavy model training without richer cross-index and goal-conditioned features.

## Cost-Aware / Runtime

- Utility-optimal bound depends on downstream candidate cost: cost `0.005 -> bound 100`,
  `0.025 -> 35`, `0.1 -> 10`.
- Long-window results held across token modes (entity/coarse/refined all ~`0.94` utility).
- Prefix indexing preserved identical candidate sets and gave `72.5x` speedup.

## What the Topology Project Established and Did Not

Established:
- recurrent topology is a valid carrier for identity-free motif memory,
- set-valued retrieval compresses continuation search (hundreds of x),
- coarse-to-fine two-stage filtering reduces candidate sets without losing hits,
- long-window workflow-state recollection is the useful operating regime.

Did NOT establish:
- semantic understanding (deliberately out of scope),
- unique prediction from short prefixes (falsified),
- that the topology layer selects final answers (it does not; it compresses the space),
- typed-edge discrimination (left as the open phase-4 question that episteme picked up).

## Why This Matters for Episteme

The topology project ended with two open threads that episteme directly inherited:

1. **The typed-edge question.** Topology deliberately stripped relation types. Whether keeping
   relation types (SUPPORTS/WEAKENS/...) helps discrimination was never measured. Episteme's
   `typed_canonical_signature` ports the canonical mechanism and answers this: typed edges beat
   label-free topology on polysemy disambiguation (`1.0` vs `0.25`) and corrupt recovery
   (`0.69` vs `0.29`).

2. **Two-stage coarse-to-fine as the production pattern.** Topology validated it empirically.
   Episteme adopts it as the architecture: label-free topology coarse key -> typed/content
   payload fine discrimination.

The topological discipline — identity-free canonicalization, automorphism-aware controls,
set-valued retrieval, coarse-to-fine staging, and honest negative claims — is the methodological
base episteme continues to follow.
