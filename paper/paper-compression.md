# Candidate-Space Compression via Topological Signatures for Relational Data Retrieval

## Abstract

This paper describes a method of data retrieval using topological signatures to retrieve items that share relational structure. It does not claim to reason over the retrieved data, and it does not claim to be a robust or complete memory substrate. Its function is narrower and more concrete: **candidate-space compression**. Given a large store of relational items and a partial query, the method retrieves a bounded basin of compatible items and reduces the candidate set down to a small selection for downstream processing.

The core mechanism is canonical recurrence indexing: node identity is assigned by first-occurrence position in a walk, not by semantic label, and the resulting topological signature is used as the retrieval key. This label-free key is an empirical choice, not an aesthetic one. In the parent topology project, adding finer semantic/categorical detail as retrieval authority repeatedly fragmented otherwise reusable neighbourhoods; maximum categorical detail lowered utility, and the best first-pass retrieval stage was often the coarsest representation. Labels therefore belong after basin formation, as payload or filters, not as the first-pass key. From a partial signature, the method returns a bounded active set — a basin — rather than a single answer. On held-out retrieval this compresses the candidate space by 34× on synthetic families and 32× on LDGR project history, with true-item inclusion of 1.0. The compression is the contribution of this paper.

The core retrieval method is built into a logical progression of experimentally motivated refinements of a larger system. These refinements — typed relation labels, a DP/LCS matcher, and payload-graph projection — are layered on top of the compression core. They are reported because they were measured, not because they are the claim. They can be inferred, substituted, or bolted on after the fact; the compression mechanism stands on its own. A boundary remains: deletion of identity-establishing evidence is destructive to the basin. All results are on LDGR-derived workloads; whether the compression envelope generalises to code repositories, document collections, or knowledge graphs is the open test this paper does not close.

## 1. Introduction

Retrieval systems are usually scored on whether they return the right item first. There is a different, prior question that matters whenever downstream processing is expensive: *how many candidates must the downstream stage consider?* A retrieval method that returns a bounded set containing the right answer, and shrinks that set aggressively, is doing useful work even if it never ranks the right answer first. This is candidate-space compression.

This paper describes such a method for data with relational structure. It uses topological signatures — canonical recurrence patterns over relational walks — to retrieve a bounded basin of compatible items. The central design choice is negative: do not let semantic labels define the first retrieval neighbourhood. The parent topology experiments found that adding more label detail can fracture the recurrence basin and make retrieval less useful. The method therefore forms the basin first and lets labels/content act later. It does not reason over the retrieved data. It compresses.

### 1.1 The compression problem

We treat retrieval as compression, not selection. Given a store of relational items and a partial query, the method should return a small bounded set that contains the target, leaving final selection to a downstream stage. The load-bearing metric is therefore **bundle reduction** — the ratio of the full store to the retrieved basin — not top-1 accuracy. A method that returns the right answer inside a 3-item bundle from a 100-item store has compressed 33×; whether it ranked the target first is a separate, downstream question.

### 1.2 Organizing assumption

This work inherits, rather than proves, one assumption from prior lineage: the observable relational graph is a projection of stable structural basins, and retrieval should activate those basins rather than match labels directly. We adopt it as a design hypothesis. The contribution of this paper is not the projection thesis but the compression mechanism built on it, and the measured reduction that mechanism achieves. Identity, throughout, is established by recurrence position, not by concrete label. The empirical lesson from the lineage is that labels can be useful evidence but bad neighbourhood constructors: if they are injected too early, they split reusable basins into incidental variants.

### 1.3 Contribution

The contribution is a compression method: canonical recurrence signatures over relational walks retrieve bounded basins with strong reduction and perfect inclusion on held-out content. Three refinements were layered on during development — typed relation labels, a DP/LCS matcher, and payload-graph projection — and are reported because they were measured. They improve specific properties of the compression system but are not required for the core result, and the paper treats them as bolt-ons rather than co-equal contributions.

## 2. Background and Lineage

This work continues two prior projects.

### 2.1 Topology constraint memory

The topology project established that identity-free recurrent temporal topology functions as an auxiliary constraint memory. Retrieval was formulated as set-valued: from a partial topology, retrieve a bounded set of structurally compatible continuations. On synthetic motifs it reached coverage 0.88, inclusion 1.0, and compression 23.9×; on real LDGR event logs, long-window workflow-state recollection reached coverage 1.0 with 554× reduction. That compression result — not the topology layer's discrimination — is the direct ancestor of this paper. Topology also validated a coarse-to-fine two-stage filtering strategy as the production pattern.

Critically, topology also exposed a counterintuitive failure mode: adding semantic or categorical detail to the retrieval representation can break the neighbourhood apart. In the representation-granularity sweep, `entity` tokens gave the best repeated-only utility (`0.947621`), while `phase_refined` and `full_categorical` fragmented repeated motifs and reduced utility (`0.908520` repeated-only; `0.690758` on the mixed workload for `full_categorical`). A two-stage experiment then clarified the remedy: use an entity/coarse first pass to preserve recall, and apply selected command/artifact refinements only after the broad basin is formed. That result is central here. Labels are payload and filters; topology is the compression key.

### 2.2 Ecphory-2: the projection thesis and a ceiling

Ecphory-2 split trajectory memory (identity-free temporal prefix → plausible futures) from semantic memory (constraints → compatible neighbourhoods) and established the projection-vs-substrate thesis the compression method inherits. At run 46 it also established a ceiling: synthetic relaxation dynamics could not beat a plain label-overlap index on any broad metric. The compression method in this paper does not contest that ceiling on discrimination; it reports compression, which the ceiling did not measure against.

## 3. The Core: Topological Signature Compression

This section is the paper. Everything after it is bolt-on.

### 3.1 The compression pipeline

**Figure 1.** The compression pipeline. The core is stages 1–3: canonical recurrence signatures retrieve a bounded basin. Stages 4–6 are refinement bolt-ons that improve specific properties; they can be substituted without touching the compression core.

```text
                    ┌──────────────────────────────┐
                    │       stored memory          │
                    │  (relational items as walks) │
                    └──────────────┬───────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         │  CORE — STAGE 1   canonical recurrence signature  │  identity by
         │                    node ids = first-occurrence     │  position,
         │                    in the walk                     │  not label
         └─────────────────────────┬─────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         │  CORE — STAGE 2   topological signature key       │  the retrieval
         │                    (label-free, recurrence-only)  │  key
         └─────────────────────────┬─────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         │  CORE — STAGE 3   retrieve bounded basin          │  candidate-space
         │                    (discrete prefix-consistency   │  compression
         │                     pruning)                      │  ← THE RESULT
         └─────────────────────────┬─────────────────────────┘
                                   │
                    ─────────────── ┴ ───────────────
                      below: refinement bolt-ons
                    ─────────────── ┬ ───────────────
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         │  BOLT-ON — STAGE 4   typed payload projection     │  improves
         │                       (keep relation labels)      │  discrimination
         └─────────────────────────┬─────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         │  BOLT-ON — STAGE 5   DP/LCS alignment             │  improves
         │                       (skip-capable matcher)      │  noise robustness
         └─────────────────────────┬─────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         │  BOLT-ON — STAGE 6   payload-graph projection     │  improves
         │                       (match internal connections)│  refinement
         └─────────────────────────────────────────────────────┘
```

The boundary between core and bolt-on is hard by design. The compression result (§3.4) holds with stages 1–3 alone; stages 4–6 each improve one property and can be removed or substituted without disabling compression. This separation is also what prevents semantic detail from fracturing the first-pass neighbourhood: the basin is retrieved before labels/content are allowed to refine it.

### 3.2 Canonical recurrence signatures

Node identity is established by recurrence position, not by concrete label. A walk through a relational item is canonicalised by assigning each node an integer id at its first occurrence. The core signature keeps the recurrence shape that determines neighbourhood membership; labels and richer content are not allowed to define the first-pass basin. Two items with different concrete labels but the same recurrence shape can therefore produce the same retrieval key. This is the topological key the compression core indexes.

### 3.3 Why labels are not the key

The label-free key is the counterintuitive part. One might expect semantic labels to make retrieval better by adding information. In these experiments they often did the opposite when used too early: they reduced recurrence density, split equivalent workflow neighbourhoods into incidental variants, and lowered utility. Topology's granularity sweep measured this directly. Coarser `entity` tokens gave the best repeated-only utility (`0.947621`), while adding all available categorical detail produced the worst tested mixed-workload utility (`0.690758`). Global outcome labels also failed as a default ranking signal: unweighted support beat success/failure weighting across practical bounds.

The rule that follows is architectural: semantic information is not banned, but it is not retrieval authority. First retrieve the broad basin with recurrence topology; then let selected, recurrent, continuation-relevant labels refine or rank the candidates. This is why the paper treats typed labels and payload graphs as bolt-ons. They are useful after neighbourhood formation, but dangerous as the mechanism that forms the neighbourhood.

### 3.4 Bounded basin retrieval — the compression result

Retrieval is a basin-finding process driven by discrete prefix-consistency pruning. From a partial query signature, the method returns the bounded active set of items whose signatures remain consistent with the query prefix — not a single answer. The substrate indexes on instances 0..k−2 of each family and queries instance k−1 (held-out), so the compression is measured on structurally novel items.

**This is the load-bearing result of the paper:**

| content | store size | retrieved basin | reduction | inclusion |
|---|---|---|---|---|
| synthetic families (20 disjoint + polysemy) | 68 | 2 | 34× | 1.0 |
| LDGR project history (32 items) | 32 | 1.0 | 32× | 1.0 |
| topology synthetic motifs (150) | 450 | 3.4 | 44× | 1.0 |
| topology LDGR event logs (long window) | ~6400 | 11.5 | 555× | 1.0 |

On every content type tested, the compression core retrieves a small bounded basin containing the target while eliminating the overwhelming majority of the store. The basin is a compact set, not a single answer — by design, since the method's job is to compress for a downstream selector.

## 4. Refinement Bolt-Ons

The three refinements below were layered on the compression core during development. Each improves one property. None is required for the compression result in §3.4, and the paper reports them because they were measured, not because they are co-equal with compression.

### 4.1 Typed relation labels (bolt-on: improves discrimination)

The compression core's first-pass signature is label-free. A typed variant can then keep edge labels as `relation_type|traversal_direction` to sharpen discrimination inside the retrieved basin. On polysemy — prefix-shared divergent families — typed disambiguation reaches 1.0 versus 0.25 label-free; on corrupt stability, 0.69 versus 0.29. This closes topology's open phase-4 question without reversing its main lesson: labels help when they refine a basin, but they should not be allowed to fracture the initial neighbourhood. Bundle reduction is unchanged.

### 4.2 DP/LCS alignment (bolt-on: improves noise robustness)

The original greedy single-pass subsequence matcher had a deterministic failure mode: one unmatched inserted evidence node exhausted the candidate iterator and later evidence could not recover. An identity-regime smoke test attributed this to the *matcher*, not the *representation* — canonical identity is stable to insertion (9/9) and repeat-deletion (8/9). Replacing the greedy matcher with DP/LCS edit-distance alignment moved the neutral-noise transition from magnitude 2 to 3. Crucially, compression (34×) and polysemy (1.0) were unchanged: this is a matcher swap, leaving the compression core untouched. The matcher is an isolated, replaceable component.

### 4.3 Payload-graph projection (bolt-on: improves refinement)

Semantic/content connections can be stored *inside* each keyed motif as a payload graph and projected after basin retrieval. This is a refinement layer, not a key. It escapes the flat node-bag ceiling: same-node rewired decoys (identical node sets and relation-label multisets, different connections) defeat node-bag matching (top-1 0.0) but not content-graph matching (top-1 1.0 on structured queries). This is interesting but it is a refinement of what happens *after* compression; the compression result in §3.4 does not depend on it.

## 5. Boundaries

### 5.1 Operating envelope

The compression core works for clean retrieval, broad basin activation, plausible incomplete queries, and plausible single omissions. It is weak on broad random partial notes and on adversarial deletion of identity-establishing evidence.

### 5.2 What is not claimed

This is a compression method, not a memory substrate. We do not claim it reasons, that it is robust to arbitrary perturbation, that it scales beyond the corpora tested, or that it returns semantic truth. It retrieves recorded relational structure into a small bounded set; a downstream stage does the rest.

### 5.3 The deletion boundary

First-occurrence deletion is a destructive perturbation in isolation (0.5 survival), but realistic redundant queries survive it (0.86 with first-recurring deletion on plausible queries). The boundary's relevance depends on query behaviour. This is a property of canonical recurrence identity, not a defect to be tuned away.

## 6. Position in the Lineage

| concern | topology | ecphory-2 | this paper |
|---|---|---|---|
| identity-free canonicalization | established | inherited | inherited |
| **set-valued compression** | **established (the ancestor)** | inherited | **ported to typed relational content** |
| coarse→fine two-stage | validated | inherited | adopted |
| labels as payload, not first-pass key | granularity sweep: maximum detail fragmented motifs | inherited | central design rule |
| typed-edge value | left open | inherited | measured (bolt-on) |
| matcher replaceability | n/a | conflated | separated (bolt-on) |
| payload-graph refinement | n/a | n/a | measured (bolt-on) |
| deletion boundary | n/a | n/a | measured |

The spine of this paper is the second row: set-valued compression, which topology established and this paper ports to typed relational content. The label/payload row explains why the compression key remains recurrence-first even though typed refinements are later useful. The rows below it are bolt-ons.

## 7. Discussion

The compression result is the contribution. Across synthetic families, LDGR project history, and topology's earlier event-log corpora, canonical recurrence signatures retrieve a small bounded basin containing the target while compressing the candidate space by one to two orders of magnitude. That is useful wherever downstream selection is expensive.

The bolt-ons each improve one axis — discrimination, noise robustness, refinement — and can be adopted or substituted per use case. The clean separation between compression core and refinement layer is itself a finding. It preserves the recurrence density needed for compression, prevents early labels from fracturing the neighbourhood, allowed the noise-collapse failure to be diagnosed as a matcher bug rather than a representation bug, and lets the compression result stand without depending on any single refinement.

### 7.1 Limitations

The 32-item LDGR-history corpus is small; numbers are point estimates without bootstrap confidence intervals. Most importantly, *every* result is measured on LDGR-derived workloads — the compression method was developed against that content. Whether the compression envelope is a property of canonical recurrence signatures or a property of LDGR-shaped structure can only be settled by testing on domains that did not participate in developing the method: code repositories, document collections, external knowledge graphs. That is the discriminating next experiment, and this paper does not close it.

## 8. Conclusion

This paper describes a candidate-space compression method. Canonical recurrence signatures retrieve bounded basins of relationally compatible items, reducing the candidate space by 32–34× on the content tested while maintaining perfect target inclusion. The key design lesson is that semantic labels are poor first-pass neighbourhood constructors: added too early, they fragment the basin the system needs to compress. They are useful later as payload, filters, or ranking evidence. The method does not reason over retrieved data and does not claim to be a complete memory substrate. Three refinements — typed labels, DP/LCS matching, payload-graph projection — were layered on during development and improve specific properties, but the compression result stands on its own. The open test is whether the envelope generalises to domains that did not shape the method.

## Reproducibility

All experiments run from `experiments/motif-topology-retrieval/` with seed `20260706`. Code, raw result JSON, reports, and the LDGR history used as memory content are archived:

```text
GitHub:   https://github.com/hydra-dynamix/episteme
HF data:  https://huggingface.co/datasets/Bakobiibizo/episteme-evidence
```

The evidence collection includes a claim-to-evidence map (claims C0–C13) linking each statement above to its source file and metric.
