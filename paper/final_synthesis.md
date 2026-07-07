# Final Synthesis: Episteme Recurrence-Sensitive Memory Substrate

This is the closing document for the episteme substrate phase. It situates episteme's results in
the lineage of its two parent projects (topology, ecphory-2), states the frozen claim, and names
what each project contributed and where episteme advanced.

Companion documents:
- `docs/prior_work_topology_findings.md` — topology project findings.
- `docs/prior_work_ecphory2_findings.md` — ecphory-2 findings up to run 46.
- `experiments/motif-topology-retrieval/operating_envelope_report.md` — the packaged envelope.
- `experiments/motif-topology-retrieval/findings.md` — the full measurement log.

## The Three-Project Lineage

```text
topology (parent)
  identity-free recurrent temporal topology as constraint memory
  set-valued retrieval; coarse->fine two-stage filtering
  ended on: "typed-edge question open; two-stage is the production pattern"

ecphory-2 (parent)
  split trajectory memory (prefix/future) from semantic memory (constraint/basin)
  "the graph is a projection; the concept is a basin; labels are payload"
  ended on run 46: synthetic relaxation could not beat a label-overlap index
                    (the ceiling), except under strong noise

episteme (this project)
  ports the canonical topology mechanism to a TYPED relational graph
  generalizes the unlabeled-constraint basin to LDGR historical content
  tests whether recurrence + typed projection beats flat overlap
  exactly where flat overlap should fail
```

## Frozen Architecture

```text
canonical label-free topology index
  -> broad basin retrieval
  -> typed/content payload projection
  -> DP/LCS alignment
  -> fine discrimination
```

This is ecphory-2's trajectory-memory pipeline (`trace -> topology prefix -> suffix bundle ->
post-lookup semantic unpacking -> refinement`) realized on a typed relational graph with LDGR
historical content, with the topology project's coarse->fine two-stage pattern as the production
shape.

## What Episteme Established (measured)

### Typed edges carry information topology does not

The topology project deliberately stripped relation types and left it open whether keeping them
helps. Episteme answered it:

```text
polysemy disambiguation:   typed 1.0   vs label-free 0.25
corrupt recovery:          typed 0.69  vs label-free 0.29
```

Keeping relation types helps when the task is distinguishing structurally similar neighborhoods.

### Set-valued basin retrieval generalizes to typed content

Topology's set-valued retrieval (coverage 0.88, inclusion 1.0, compression 23.9x on synthetic
motifs) ported cleanly:

```text
held-out inclusion: 1.0
bundle reduction:   36x (synthetic), 32x (LDGR history)
polysemy ambiguity retention: 1.0
```

The basin retrieves a compact set, not a single answer — consistent with both parents.

### Noise collapse was a matcher failure, not a representation failure

Ecphory-2's run-46 ceiling showed relaxation reduces to index overlap. Episteme initially
misdiagnosed noise collapse as identity brittleness and built an identity-regime smoke that
**falsified its own premise**:

```text
canonical stability:  insertion 9/9, repeat-deletion 8/9, first-occ-deletion 4/9
role_payload(local):  0/9, 0/9, 4/9  (WORSE than canonical — falsified)
```

The real mechanism was the greedy matcher treating one inserted unmatched node as terminal failure.
DP/LCS skip-capable alignment repaired it without touching identity:

```text
noise transition: greedy mag 2 -> DP/LCS mag 3
polysemy:         1.0 unchanged
reduction:        34x unchanged
```

This is the methodological discipline the topology project mandated: the smoke found the bug in
the explanation, not just the code.

### Deletion brittleness is a real but narrow identity boundary

After matcher repair, drop remained brittle. Deletion controls isolated the cause:

```text
canonical first-recurring deletion: 0.5
canonical repeat deletion:          1.0
anchored_recurring (proposed fix):  REJECTED — damages polysemy 1.0 -> 0.43
edge_sequence / bag controls:       deletion-robust but lose polysemy (0.86 / 0.57)
```

Boundary: canonical recurrence identity preserves discrimination but depends on
identity-establishing evidence. This is a representation cost, not a scoring bug.

### Behavioral relevance: the boundary is often tolerable

The decisive test used LDGR project history as memory content (the project's own observations,
artifacts, reports). Stratified corpus, clean baseline valid:

```text
clean accuracy: 1.0, reduction 32x
plausible query survival:    0.8884
with first-rec deletion:     0.8644
without first-rec deletion:  0.8970
control/adversarial survival:0.4479
```

Updated boundary:

> first-occurrence deletion is a destructive perturbation in isolation, but realistic redundant
> memory queries often survive it.

### Payload-graph refinement beats flat overlap where flat overlap should fail

The final experiment stored semantic/content connections inside the keyed motif as a payload
graph, retrieved a broad bundle, then refined by projecting and matching the target payload graph.
Decisive control: same-node rewired decoys (same nodes + same relation-label multiset, different
connections).

```text
scorer              top1    bundle   reduction
coarse_only         0.0     64.0     1x
node_bag            0.0     3.41     27.25x   (same-node decoys tie)
relation_topology   0.0     64.0     1x
content_graph       0.7969  1.70     54.5x
```

Per-mode content_graph: core/partial/noisy all `1.0` top-1 with `64x` reduction; only the
deliberately underdetermined topic+mechanism query stays broad (`0.1875`).

This is the direct continuation of ecphory-2's run-46 thread: flat overlap (node_bag) is the
ceiling that rewired same-node decoys expose, and content-graph connections are what beats it.
The escape ecphory-2 only saw under strong noise, episteme sees cleanly whenever the query
contains actual internal semantic connections.

## What Each Project Contributed

| concern | topology | ecphory-2 | episteme |
|---|---|---|---|
| identity-free canonicalization | established | inherited | inherited |
| set-valued retrieval | established (synthetic) | inherited (trajectory) | ported to typed content |
| coarse->fine two-stage | validated empirically | inherited | adopted as architecture |
| typed-edge value | left open (phase 4) | inherited | **answered: typed helps** |
| trajectory vs semantic split | n/a | **established** | inherited |
| graph-as-projection thesis | n/a | **established** | built substrate on it |
| unlabeled basins recover labels | n/a | pilot (6 concepts) | **generalized to LDGR history** |
| agreement-gated refinement | n/a | **established (dual lookup)** | inherited (payload-graph gating) |
| relaxation vs index ceiling | n/a | falsified run 46 | **escape: content-graph beats node_bag** |
| matcher vs representation layer | n/a | conflated | **separated; DP/LCS repair** |
| deletion boundary relevance | n/a | n/a | **measured on real content** |

## The Defensible Claim

> A typed relational substrate supports identity-free basin consolidation and held-out retrieval
> with strong bundle reduction (32-36x). Typed edge labels carry discriminating information beyond
> pure topology. DP/LCS skip-capable alignment repairs neutral-noise matcher collapse without
> touching identity. Deletion of identity-establishing evidence is a real but narrow boundary
> whose behavioral relevance depends on query redundancy, not a universal failure. Stored
> semantic/content payload graphs refine broad bundles in a way that is not reducible to flat
> node/token overlap — same-node rewired decoys defeat node-bag matching but not content-graph
> matching.

This is recollection / candidate-space compression with typed projection and payload-graph
refinement, not semantic truth or general edit-distance memory.

## Honest Boundaries (carried forward from all three projects)

- Not a general edit-distance memory; adversarial/random deletion of identity-establishing
  evidence can destroy the basin.
- Not semantic understanding; the substrate retrieves recorded structure, it does not reason.
- Not scale-validated beyond a 32-item LDGR-history corpus.
- The two-stage gain over a single coarse stage is modest when long windows are already specific
  (topology's finding, re-confirmed).
- Flat node/token overlap remains a strong baseline; content-graph only clearly wins when the
  query carries actual internal connections, not when it is underdetermined.

## Frozen State

```text
GitHub:   https://github.com/hydra-dynamix/episteme        (main 1e6a71c)
          https://github.com/hydra-dynamix/episteme/tree/payload-graph-refinement (d4a35a2)
HF data:  https://huggingface.co/datasets/Bakobiibizo/episteme
```

## What Comes Next (not mechanism patching)

The substrate now has a believable operating envelope. Per the stop condition recorded in the
operating-envelope report, the next useful work is **integration/application testing**, not another
representation tweak:

1. Wire the substrate as a live retrieval surface over a growing LDGR corpus and measure
   coarse-bundle activation + payload-graph refinement on real incoming queries.
2. Test the agreement-gated dual path (ecphory-2's principle) at scale: when does labeled
   interpretation agree with the unlabeled basin, and where do they usefully disagree?
3. Probe whether content-graph refinement's escape from the node-bag ceiling generalizes beyond
   LDGR history to other structured content (code, documents, event logs).
4. Only revisit deletion identity work if an application proves the boundary is unacceptable under
   realistic workload.

Do not return to role_payload(local) identity (falsified). Do not adopt anchored_recurring
(rejected). Do not sweep weights to hide a mechanism (the discipline all three projects share).
