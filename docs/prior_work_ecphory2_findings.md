# Prior Work: Ecphory-2 Findings (Pre-Run-46)

Source: `../ecphory-2` (sibling project).
Primary documents: `ecphory-2/docs/trajectory-vs-semantic-memory-architecture.md`,
`ecphory-2/docs/trajectory-memory-experimental-report.md`,
`ecphory-2/docs/unlabeled-constraint-basin-pilot.md`,
`ecphory-2/docs/promoted-dual-lookup-control-experiment.md`,
`ecphory-2/docs/dual-memory-semantic-neighborhood-pilot.md`.

This records the ecphory-2 findings up to and including run 46 that **align with episteme's
substrate** and with **multi-stage retrieval**. Ecphory-2 is the project that first split
trajectory memory from semantic memory and ran the unlabeled-constraint-basin line that episteme
generalizes.

## Two-System Architecture Decision (the bridge to episteme)

Ecphory-2's central architectural note (`trajectory-vs-semantic-memory-architecture.md`) decided:

> Trajectory memory and semantic memory should not be forced into one retrieval mechanism. They
> intersect and communicate, but they solve different lookup problems.

```text
trajectory memory:   past -> now -> retrieve plausible futures (identity-free temporal prefixes)
semantic memory:     observed constraints -> compatible graph -> candidate concepts (relational)
```

The crucial revision (after the unlabeled-basin pilot): **the semantic graph is a projection, not
the primitive memory object.** Concept identities are post-hoc names for stable basins; labels are
communication/evaluation payload, not the substrate's organizing key.

Working ontology that episteme inherits:

```text
constraint field
  -> local interactions
  -> stable attractor basins
  -> graph/neighborhood projection
  -> post-hoc concept labels
```

This is the exact thesis episteme packages as "the graph is a projection; the concept is a basin;
retrieval is relaxation, not lookup."

## Trajectory Memory Line (the multi-stage retrieval result)

`trajectory-memory-experimental-report.md` is the load-bearing multi-stage result.

### Lookup comparison (held-out candidates)

```text
method                       covered   coverage   largest neighborhood
strict sequence              17/385    0.044      3
transition feature sequence  64/385    0.166      18
surface                      83/385    0.216      19
topology prefix exact        15/385    0.039      4
```

Strict cumulative sequence was too narrow. Surface relaxation improved coverage but pulled broad
neighborhoods.

### Windowed topology suffix retrieval (the multi-stage regime)

Restored the topology project's sliding-window prefix->suffix pattern as stage 1, then applied
**post-lookup** refinement as stage 2:

```text
window=8..12, stride=3, prefix_fraction=0.5, min_support=1, success_delta=0.1
selected successful target windows: 287
covered: 252  (coverage 0.878)
successful evidence included on covered: 0.992
exact suffix included on covered:        0.444
mean candidate set size:                 43.6
mean successful futures:                 21.1
mean avoid futures:                      22.5
```

Longer prefix refinement (`prefix_fraction=0.8`) traded coverage for specificity:
coverage `0.878 -> 0.464`, exact-suffix `0.444 -> 0.766`, single-trace rate `0.048 -> 0.306`.

### Three operating modes (refinement sweep, 180 configs)

```text
mode                  window   pf   stride  cov      success   exact    set     refined  single-trace
high recall           8..12    0.5  1       0.913    1.0       0.576    131.3   61.3     0.018
balanced sharp        8..12    0.9  1       0.464    0.967     0.954    37.7    9.3      0.180
single-trace leaning  12..16   0.9  2       0.173    0.615     0.827    7.5     1.6      0.346
```

Decision: do not pick one setting globally. Preserve modes as a reusable fixture because different
questions need different evidence shapes. This is the multi-stage surface episteme later maps onto
its own coarse->fine bundle narrowing.

### Evidence fixture: success + avoid paths

The reusable fixture preserves **both** successful paths and avoid paths. Failures are not
contamination; they are negative evidence.

### Internal-state prediction (does evidence move the model?)

Evidence bundles moved an outcome prediction in interpretable directions:

```text
balanced sharp:  no_memory 0.515 (Brier 0.235) -> topology_evidence 0.601 (0.201)
                 positive_only 0.819 (0.047)  -> avoid_only 0.309 (0.512)
```

Avoid-path evidence reliably lowered success prediction. Sequence identity was a
**context-sensitive knob**: it helped balanced-sharp (`0.201 -> 0.130`) but hurt high-recall
(`0.096 -> 0.280`).

The program's established evidence path (episteme's direct ancestor):

```text
state-transition trace -> topology prefix lookup -> suffix evidence bundle
-> post-lookup semantic unpacking -> internal-state prediction -> offline decision proxy
```

## Unlabeled Constraint Basin Pilot (the semantic-memory result)

`unlabeled-constraint-basin-pilot.md` tested whether labels fragment retrieval.

```text
train records: 30, query records: 12, top_k: 5
query accuracy after lookup:        1.000
shuffled-label accuracy:            0.000
accuracy lift vs shuffled:          1.000
```

Basin formation used only anonymous constraint IDs and anonymous pairwise structure. Human labels
were revealed only after lookup.

```text
threshold   basin count   mean size   mean purity
0.25-0.35   4             7.5         0.75   (broad super-basins)
0.40        6             5.0         1.0    (perfect purity)  <- useful operating point
0.45-0.50   12            2.5         1.0
```

Conclusion: unlabeled constraint lookup recovers human concept labels above shuffled chance;
reusable basins emerge **without using human labels as lookup keys**; basin scale matters (broad
super-basins show cross-concept structural similarity; they are not failures).

This is the result episteme generalizes from a 6-concept toy to a 32-item LDGR-history corpus.

## Promoted Dual Lookup (the agreement-gated result)

`promoted-dual-lookup-control-experiment.md` promoted the unlabeled basin into the control loop
alongside labeled semantic lookup.

```text
policy                                  mean utility
no semantic perturbation                0.533
labeled semantic lookup                 0.700
unlabeled basin lookup                  1.000
naive labeled+unlabeled union           0.567   <- worse than labeled-only
agreement-gated dual lookup             1.000
oracle                                  1.000
```

The decisive result is not "unlabeled wins." It is that **naive union fails**: broad labeled
concepts drown out post-hoc basin evidence. The useful dual path is **agreement-gated** — labeled
neighborhood AND unlabeled basin labels must agree. This is the multi-stage refinement principle:
do not union projections blindly; gate on agreement.

Non-monotonic top-k (top_k=5 dropped to `0.567` while neighbors were `1.0`) shows partial basin
retrieval can be worse than either narrow or broad retrieval.

## Dual Memory Semantic Neighborhood (the bridge composition)

`dual-memory-semantic-neighborhood-pilot.md` composed the substrates:

```text
trajectory motif -> semantic constraint set -> compatible semantic neighborhood
```

```text
trajectory motif accuracy:           1.0
semantic neighborhood recall:        1.0
mean top-score lift from trajectory: 0.0
mean top-margin lift:                0.111
```

Trajectory-derived constraints increased **margin** (a narrowing/confidence signal) but not recall
alone — because semantic lookup returns neighborhoods, and single top-concept recall is the wrong
primary metric. The right metric is neighborhood compatibility and narrowing.

## Ambiguous Constraint Basin Stability (the basin-dynamics result)

`ambiguous-constraint-basin-stability.md` measured basin dynamics the topology project never could:

```text
ambiguous_surface_multi_basin_rate:    1.0   (one surface token activates multiple basins)
context_resolution_accuracy:           1.0   (context resolves the ambiguity)
composition_success_rate:              1.0
continuous_refinement_final_accuracy:  1.0
forced_choice_mean_utility_on_ties:    0.467
tie_policy_mean_utility_on_ties:       0.700
tie_policy_lift_vs_forced_choice:      0.233
```

supports_projection_hypothesis: `True`.

This is the empirical seed of episteme's polysemy probe: a shared prefix activates multiple basins,
a disambiguating step collapses the ambiguity, and a tie/defer policy beats forced choice on ties.

## The Run-46 Ceiling (why the synthetic relaxation line closed)

Run 46 (`scale-local-dynamics-vs-index-retrieval`) falsified the hypothesis that local relaxation
dynamics beat a plain 1-NN index on the synthetic ambiguous/composition corpora.

```text
outcome: falsified
any_broad_metric_win_for_relax:        False
index_better_or_equal_at_every_cell:   True
relax_beats_index_composition:         False
relax_beats_index_context_top1:        False
relax_beats_index_tie_utility:         False
relax_better_at_any_fragmentation_cell:False
```

Decisive computed fact: `mean_active_size_on_bare = 1` for **both** mechanisms. A single bare
surface token is below threshold (0.5) and triggers no spreading, so relaxation reduces exactly to
index overlap on ambiguity queries. Relaxation's only unique act is **reconstructive completion**
(a generative closure), not a retrieval advantage; its only marginal retrieval effect (bleed-ties)
is harmful.

The ceiling was reframed properly: the index baseline **beats** relaxation on top-1 and ties it on
every broad metric. Not constructed-to-pass; computed via `active_size`.

Run 47 (`scale-trajectory-to-semantic-basin-bridge`) confirmed the ceiling held across regimes:

```text
control_relax_beats_best_index_any_regime:  False
control_semantic_unique_win_any_regime:     True  (only in lossy_strong)
```

So: the synthetic constraint-field relaxation line closed at run 46/47 (3rd independent negative).
A plain label-overlap index was the ceiling the relaxation substrate could not beat, except under
strong noise where the unlabeled semantic channel had a unique win.

## Why This Matters for Episteme

Ecphory-2 handed episteme four things:

1. **The projection-vs-substrate thesis.** The graph is a projection of stable basins; labels are
   payload. Episteme builds its entire substrate on this.

2. **The multi-stage evidence path.** `trace -> topology prefix lookup -> suffix evidence bundle
   -> post-lookup semantic unpacking -> refinement` is ecphory-2's trajectory-memory pipeline.
   Episteme's `label-free topology key -> broad bundle -> typed/content payload projection ->
   DP/LCS alignment -> fine discrimination` is the same shape on a different content domain.

3. **The agreement-gated refinement principle.** Naive union of projections fails; gated agreement
   works. Episteme's two-stage coarse->fine and payload-graph refinement both rely on narrowing,
   not union.

4. **The ceiling and its one escape.** Run 46/47 showed label-overlap index is the ceiling the
   synthetic relaxation substrate could not beat — except under strong noise, where the unlabeled
   semantic channel had a unique win. Episteme's job is to test whether that escape generalizes:
   whether recurrence + typed projection + payload-graph refinement can beat flat overlap exactly
   on the cases flat overlap loses (rewired same-node decoys, polysemy, identity-establishing
   deletion). Episteme's payload-graph result (same-node rewired decoys defeat node_bag but not
   content_graph) is a direct continuation of this thread.
