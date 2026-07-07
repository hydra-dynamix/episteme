# Recurrence-Sensitive Memory: A Typed Relational Substrate for Basin Retrieval

## Abstract

This paper describes a recurrence-sensitive memory substrate that retrieves recorded relational structure; it does not reason over it. Its job is candidate-space compression: from partial structure, retrieve a bounded basin of compatible items and refine it for a downstream selector.

The substrate is built as one logical progression of four falsifiable refinements. First, canonical recurrence indexing — node identity by first-occurrence position, not label — retrieves bounded basins rather than single answers. Second, adding typed relation labels to that index sharpens a discrimination that pure topology cannot provide: polysemy disambiguation rises from 0.25 to 1.0. Third, when neutral noise collapsed retrieval, an identity-regime smoke test attributed the failure to the *matcher*, not the *representation*; replacing a greedy with a DP/LCS alignment moved the noise transition from magnitude 2 to 3 without touching identity. Fourth, storing the semantic connections inside each keyed motif as a payload graph then escapes the flat node-bag ceiling: same-node rewired decoys (identical node sets and relation-label multisets, different connections) defeat node-bag matching (top-1 0.0) but not content-graph matching (top-1 1.0 on structured queries).

On LDGR project history used as memory content, the substrate reaches clean retrieval 1.0 with 32× bundle reduction. A real boundary remains: deletion of identity-establishing evidence is destructive in isolation, but realistic redundant queries survive it (0.86 with first-recurring deletion on plausible queries). All results so far are on LDGR-derived workloads; whether the operating envelope holds on code repositories, document collections, or knowledge graphs is the open test this paper does not close.

## 1. Introduction

A pattern keeps recurring across domains. You give a model a complex task; at small scale a single prompt suffices. At medium scale you decompose into a tree of subtasks. At large scale the tree alone fails — children lack cross-context, setups never pay off, terminology drifts. You patch with cross-cutting constraints, and the tree has quietly become a graph.

This observation, inherited from prior work on graph-reasoning systems, motivates a sharper question for *memory*: can a substrate retrieve reusable structure from the *relational shape* of recorded knowledge, rather than from the labels attached to it? And if it can, can stored semantic connections refine a broad retrieval beyond flat token overlap?

### 1.1 The question

We ask whether a label-free substrate can retrieve reusable basins from relational structure, and whether semantic connections stored *inside* a keyed motif can refine a broad bundle beyond flat node/token overlap. We frame this as retrieval and compression, not semantic prediction. The substrate should activate broad basins and narrow them with typed projection; it should not match tokens directly.

### 1.2 Organizing assumption: the graph is a projection, the concept is a basin

This work inherits, rather than proves, one organizing assumption from ecphory-2: the relational graph is a projection of stable basins, labels are payload rather than key, and retrieval is relaxation rather than lookup. We adopt it as a design hypothesis and spend the rest of the paper measuring where a substrate built on it holds and where it breaks. The contribution of this paper is not the projection thesis itself but the typed-relational substrate built on top of it, and the measured boundaries of that substrate under perturbation. Identity, throughout, is established by recurrence position, not by concrete label.

### 1.3 Contributions

1. We port the canonical topology mechanism to a **typed** relational graph and answer whether relation types beat label-free topology. They do: typed edges sharpen polysemy disambiguation from 0.25 to 1.0 and corrupt stability from 0.29 to 0.69.
2. We diagnose that neutral-noise collapse was a **matcher** failure, not a representation failure, and repair it with DP/LCS alignment — moving the noise transition from magnitude 2 to 3 without touching identity.
3. We measure a real **deletion boundary**: first-occurrence deletion is destructive in isolation (0.5 survival) but behaviorally often tolerable (0.86 on plausible redundant queries).
4. We show **payload-graph refinement** beats flat overlap exactly where flat overlap should fail: same-node rewired decoys defeat node-bag matching but not content-graph matching.
5. We validate the whole substrate on **real LDGR project history** as memory content: 32 items, clean retrieval 1.0, 32× reduction.

## 2. Background and Lineage

This work continues two prior projects. Its claims are continuations of specific results from each, not isolated work.

### 2.1 Topology constraint memory

The topology project established that identity-free recurrent temporal topology functions as an auxiliary constraint memory. Retrieval was formulated as set-valued: from a partial topology, retrieve a bounded set of structurally compatible continuations. On synthetic motifs it reached coverage 0.88, inclusion 1.0, and compression 23.9×; on real LDGR event logs, long-window workflow-state recollection reached coverage 1.0 with 554× reduction. A coarse-to-fine two-stage filtering strategy was validated empirically as the production pattern.

Critically, topology enforced a deliberate invariant: relation types were stripped, reducing all connections to undirected topological neighbours. Whether preserving relation types would improve discrimination was left open — never measured. That open question is the first thing this paper closes.

### 2.2 Ecphory-2: trajectory vs semantic memory

Ecphory-2 split trajectory memory (identity-free temporal prefix → plausible futures) from semantic memory (constraints → compatible neighbourhoods) and established the **projection-vs-substrate thesis**: the graph is a projection of stable basins; labels are payload, not the organising key. An unlabeled-constraint-basin pilot showed anonymous constraints recover human labels above shuffled chance (query accuracy 1.0 vs shuffled 0.0). An agreement-gated dual lookup beat naive union (1.0 vs 0.567 utility), establishing that projections should not be unioned blindly.

### 2.3 The run-46 ceiling

At run 46, ecphory-2 falsified the hypothesis that local relaxation dynamics beat a plain 1-NN label-overlap index. Across every broad metric, relaxation failed to surpass the index; its only unique act was reconstructive completion, not retrieval advantage. The single escape appeared under strong noise, where the unlabeled semantic channel secured a unique win. This is the ceiling this paper must escape — and the escape must be measurable on cases where flat overlap *should* lose.

## 3. The Substrate

**Figure 1.** The retrieval pipeline, end to end. Stages 1–2 are the label-free coarse key; stages 3–4 are the typed/content refinement layer. The matcher (stage 5) is replaceable without touching the representation, which is what the noise-collapse diagnosis (§4.3) exploited.

```text
                    ┌──────────────────────────────┐
                    │       stored memory          │
                    │  (typed relational graphs)   │
                    └──────────────┬───────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              │  STAGE 1  canonical recurrence signature │  (identity by
              │           node ids = first-occurrence    │   position,
              │           edge labels kept as type|dir   │   not label)
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              │  STAGE 2  label-free coarse index        │  (broad basin;
              │           retrieve basin                │   recurrence
              │           (bounded active set)          │   only)
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              │  STAGE 3  unpack typed payload graph     │  (relations +
              │           per candidate                 │   content)
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              │  STAGE 4  payload-graph projection       │  (refinement,
              │           match against target graph    │   not a key)
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              │  STAGE 5  DP/LCS alignment               │  (matcher;
              │           (skip-capable, repairable)    │   replaceable)
              └────────────────────┬────────────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              │  STAGE 6  candidate ranking             │
              │           (fine discrimination)         │
              └─────────────────────────────────────────┘
```

This is ecphory-2's trajectory-memory pipeline (trace → topology prefix → suffix bundle → post-lookup semantic unpacking → refinement) realised on a typed relational graph, with topology's coarse→fine two-stage pattern as the production shape.

### 3.1 Architecture

The frozen architecture, reading Figure 1 top to bottom: a canonical label-free topology index (stages 1–2) performs broad basin retrieval; a typed/content payload projection (stages 3–4) narrows it; a DP/LCS alignment (stage 5) supplies skip-capable matching; fine discrimination (stage 6) ranks the survivors. The boundary between coarse key (label-free) and refinement layer (typed/content) is hard by design, and the matcher is an isolated replaceable component — a property the noise-collapse diagnosis in §4.3 depends on.

### 3.2 Typed canonical signatures

Node identity is established by recurrence position, not by concrete label. We define two signatures. `label_free_canonical_signature` collapses all edge labels to a uniform marker, retaining only skeletal connectivity and the first-occurrence node ordering — this mirrors topology's original mechanism. `typed_canonical_signature` preserves the same node canonicalisation but keeps edge labels as `relation_type|traversal_direction`, mapping the signature onto a coloured directed graph.

The comparison between these two is itself scientific content: does keeping relation types beat label-free topology? The typed form supplies the discrimination that the label-free form lacks. Where two subgraphs share geometric similarity but differ in semantic role, only the typed signature can separate them.

### 3.3 Basin retrieval by relaxation

Retrieval is a basin-finding process driven by discrete prefix-consistency pruning, not a collapse to a single answer. The substrate indexes on instances 0..k−2 of each family and queries instance k−1 (held-out). Because the substrate compresses the candidate space for downstream selection, the load-bearing metric is **bundle reduction**, not top-1 accuracy.

### 3.4 DP/LCS alignment as the repair layer

The original greedy single-pass subsequence matcher had a deterministic failure mode: one unmatched inserted evidence node exhausted the candidate iterator, and later evidence could not recover. We replace it with DP/LCS edit-distance alignment, which can skip unmatched evidence and candidate nodes optimally. This is strictly a matcher-layer repair; identity is left untouched.

### 3.5 Payload-graph projection refinement

Semantic/content connections are stored *inside* the keyed motif as a payload graph. After coarse basin retrieval, each candidate payload graph is projected and matched against the target payload graph's topology and relations. This is a second-stage refinement, not a key. It is not reducible to node/token overlap: a rewired decoy with the same nodes and same relation-label multiset but different connections is indistinguishable to node-bag matching but distinguishable to content-graph matching.

## 4. Results

### 4.1 Typed edges carry information topology does not

On polysemy — prefix-shared divergent families (the bat/bank construction) — typed disambiguation reaches 1.0 while label-free drops to 0.25. Under corrupt perturbation, typed stability is 0.69 versus 0.29 label-free. Keeping relation types helps precisely when the task requires distinguishing structurally similar neighbourhoods. This closes topology's open phase-4 question.

### 4.2 Set-valued retrieval generalizes to typed content

Held-out inclusion is 1.0; bundle reduction is 36× on synthetic families and 32× on LDGR historical content. Polysemy ambiguity retention is 1.0: shared prefixes activate multiple basins rather than collapsing to one. The basin retrieves a compact set, not a single answer — consistent with both parent projects.

### 4.3 Noise collapse was a matcher failure

An identity-regime smoke test falsified the initial diagnosis that noise collapse was a representation failure. Canonical identity is stable to insertion (9/9) and repeat-deletion (8/9), brittle only to first-occurrence deletion (4/9). A walk-local `role_payload` identity — the proposed fix — was *worse* (0/9, 0/9, 4/9): walk-local incident structure changes whenever a neighbour is inserted or deleted.

Matcher ablation isolated the real cause. Greedy neutral-noise survival collapses at magnitude 2; DP/LCS extends the transition to magnitude 3. Crucially, polysemy (1.0) and reduction (34×) are unchanged across matchers. The repair altered only the navigation strategy; the typed relational constraints and basin compression governing identity continued with identical fidelity.

### 4.4 Deletion brittleness is a narrow identity boundary

Canonical first-recurring deletion survival is 0.5; repeat deletion is 1.0. The proposed `anchored_recurring` fix is **rejected**: it does not repair the target failure and damages polysemy (1.0 → 0.43). Edge-sequence and bag-of-edges controls are deletion-robust but lose polysemy (0.86 and 0.57). The tradeoff is real: recurrence identity preserves discrimination but depends on identity-establishing evidence.

### 4.5 Behavioral relevance on LDGR history

We used the project's own LDGR history as memory content: 32 items drawn from observations, artifact descriptions, and report chunks, stratified by topic. The clean baseline is valid: accuracy 1.0, reduction 32×. On plausible partial/noisy queries, survival is 0.8884 — and 0.8644 *with* first-recurring deletion, versus 0.8970 without. On control/adversarial queries, survival drops to 0.4479. The boundary is behaviorally often tolerable because realistic redundant queries retain enough typed recurrence evidence to recover.

### 4.6 Payload-graph refinement beats flat overlap

The decisive control is a same-node rewired decoy pool: each decoy has the same nodes and the same relation-label multiset as its paired real item, but different connections. Aggregate results on the real-plus-decoy pool:

```text
scorer              top-1    bundle   reduction
coarse_only         0.0      64.0     1×
node_bag            0.0      3.41     27.25×    (decoys tie)
relation_topology   0.0      64.0     1×
content_graph       0.7969   1.70     54.5×
```

Per-mode, `content_graph` reaches 1.0 top-1 with 64× reduction on core, partial, and noisy queries; only the deliberately underdetermined topic+mechanism query stays broad (0.1875). This is the escape from ecphory-2's run-46 ceiling, made clean: flat overlap deadlocks on rewired graphs while refined payloads resolve connection-weighted pathways.

## 5. Boundaries

### 5.1 Operating envelope

The substrate works for clean LDGR-history retrieval, broad topical basin activation, typed/mechanism disambiguation, plausible incomplete queries, plausible single omissions, and neutral noise after DP/LCS repair. It is weak on broad random partial notes, adversarial deletion of identity-establishing evidence, and deletion robustness when recurrence-sensitive discrimination must be preserved.

### 5.2 What is not claimed

We do not claim perfect noise stability, general edit-distance memory, robustness to broad random deletion, robustness to adversarial removal of identity-establishing evidence, scale beyond a 32-item corpus, or semantic truth. The substrate retrieves recorded structure; it does not reason.

### 5.3 The deletion boundary

First-occurrence deletion is a destructive perturbation in isolation, but realistic redundant memory queries often survive it. The relevance of the boundary depends on query behaviour, not a universal failure. This is a representation cost of canonical recurrence identity, not a scoring bug.

## 6. Position in the Lineage

| concern | topology | ecphory-2 | episteme |
|---|---|---|---|
| identity-free canonicalization | established | inherited | inherited |
| set-valued retrieval | established (synthetic) | inherited (trajectory) | ported to typed content |
| coarse→fine two-stage | validated empirically | inherited | adopted as architecture |
| typed-edge value | left open (phase 4) | inherited | **answered: typed helps** |
| trajectory/semantic split | n/a | established | inherited |
| projection thesis | n/a | established | built substrate on it |
| unlabeled basins recover labels | n/a | pilot (6 concepts) | **generalized to LDGR history** |
| agreement-gated refinement | n/a | established | inherited |
| relaxation vs index ceiling | n/a | falsified (run 46) | **escape: content-graph beats node-bag** |
| matcher vs representation | n/a | conflated | **separated; DP/LCS repair** |
| deletion boundary relevance | n/a | n/a | **measured on real content** |

Threads closed: topology's typed-edge question (answered); ecphory-2's run-46 ceiling (escaped on content-graph refinement). Threads opened: does the content-graph escape generalise beyond LDGR history to code, documents, event logs; does agreement-gated dual lookup scale; can the substrate serve as a live retrieval surface. The next step is integration and application testing, not more mechanism patching.

## 7. Discussion

The substrate is a believable operating envelope for recurrence-sensitive basin retrieval with typed projection. The content-graph escape from the node-bag ceiling suggests value in storing connections *inside* the motif rather than only at the key. The two-stage coarse→fine pattern generalises across domains — workflow events, game trajectories, relational concepts.

### 7.1 Limitations

The 32-item LDGR-history corpus is small; numbers are point estimates without bootstrap confidence intervals. The two-stage gain over a single coarse stage is modest when long windows are already specific (topology's finding, re-confirmed). Flat node/token overlap remains a strong baseline; content-graph only clearly wins when the query carries actual internal connections. Most importantly, *every* result in this paper is measured on LDGR-derived workloads — the substrate was designed and debugged against that content. Whether the operating envelope is a property of the representation or a property of LDGR-shaped workloads can only be settled by testing on domains that did not participate in developing the substrate: code repositories, document collections, and external knowledge graphs. That is the discriminating next experiment, and this paper does not close it.

### 7.2 Methodological note

The identity-regime smoke falsified the project's own premise *before* a benchmark was built on it — preventing a redesign of the representation around a false diagnosis. This is the discipline all three projects share: when an optimisation appears, do not call it cheating and remove it; interrogate the signal and expose it as a controllable mechanism. A correctly recorded failure is more valuable than an incorrectly reported success.

## 8. Conclusion

A typed relational substrate supports identity-free basin consolidation and held-out retrieval with strong bundle reduction. Typed edge labels carry discriminating information beyond pure topology. DP/LCS alignment repairs neutral-noise matcher collapse without touching identity. Deletion of identity-establishing evidence is a real but narrow boundary whose relevance depends on query redundancy. Stored payload graphs refine broad bundles in a way not reducible to flat node/token overlap. With mechanistic validation established, the next step is integration and application testing under realistic workloads, not more mechanism patching.

## Reproducibility

All experiments run from `experiments/motif-topology-retrieval/` with seed `20260706`. Code, raw result JSON, reports, and the LDGR history used as memory content are archived:

```text
GitHub:   https://github.com/hydra-dynamix/episteme
HF data:  https://huggingface.co/datasets/Bakobiibizo/episteme-evidence
```

The evidence collection includes a claim-to-evidence map (claims C0–C13) linking each statement above to its source file and metric.
