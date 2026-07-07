# experimental program: relational transition memory substrate

## purpose

Test whether knowledge can be represented as relational transition traces where evidence accumulation narrows possible trajectories toward relevant concepts, claims, or learning records.

The goal is not to build the final system.

The goal is to determine whether this idea is real, useful, and better than simpler alternatives.

## core hypothesis

A memory substrate built from relational transition traces can retrieve relevant knowledge by accumulating partial evidence and narrowing the active candidate trajectory field.

In plain terms:

```text
evidence arrives
  ↓
compatible traces activate
  ↓
incompatible traces fall away
  ↓
candidate set narrows
  ↓
relevant claim / concept / learning record emerges
```

## primary falsification condition

The substrate fails if evidence accumulation does not reliably narrow the candidate set while preserving the correct target.

More directly:

```text
If adding evidence does not improve retrieval specificity,
or if it eliminates the correct target too often,
the transition substrate is not working.
```

---

# phase 0: dataset construction

Create a small controlled dataset before using real research records.

## dataset A: toy semantic world

Use simple objects with attributes.

Example:

```text
cat:
  animal
  mammal
  fur
  tail
  whiskers
  four_paws
  predator

dog:
  animal
  mammal
  fur
  tail
  four_paws
  pack_animal

crow:
  animal
  bird
  black
  wings
  beak
  two_legs

panther:
  animal
  mammal
  black
  fur
  tail
  four_paws
  predator
```

Purpose:

Test whether partial evidence narrows candidate trajectories.

## dataset B: synthetic research records

Create fake but structured learning records.

Example:

```text
L-001:
  domain: topology_memory
  method: long_window_motifs
  metric: true_inclusion
  result: passed
  supports: K-001

L-002:
  domain: topology_memory
  method: short_window_motifs
  metric: coverage
  result: failed
  weakens: K-002
```

Purpose:

Test claim retrieval before dealing with messy real LDGR data.

## dataset C: real research records

Use distilled Learning Records from actual experiments.

Purpose:

Test whether the system survives real ambiguity, overlap, contradiction, and stale claims.

---

# phase 1: representation variants

Build three competing substrate variants.

## variant A: unordered neighborhood

Evidence is treated as a set.

```text
{animal, black, tail, whiskers}
```

No order. No typed transitions.

This is the baseline.

## variant B: ordered transition traces

Evidence is treated as sequence.

```text
animal → black → tail → whiskers
```

Order matters.

## variant C: typed ordered transition traces

Evidence is treated as typed relational movement.

```text
animal
  HAS_COLOR → black
  HAS_ATTRIBUTE → tail
  HAS_ATTRIBUTE → whiskers
```

Order and edge type matter.

## variant D: shuffled-order control

Same evidence as B/C, but order is randomized.

Purpose:

Tests whether apparent benefit comes from content alone rather than transition structure.

## variant E: random topology control

Same number of nodes and edges, but randomized relations.

Purpose:

Tests whether retrieval depends on meaningful relational structure.

---

# phase 2: first retrieval test

## question

Does evidence accumulation narrow the candidate field?

## procedure

For each held-out target:

1. Hide the target label.
2. Feed evidence one token/edge at a time.
3. Record active candidate set after each step.
4. Check whether the correct target remains in the set.
5. Check whether the candidate set shrinks.

Example:

```text
input 1: animal
candidates: cat, dog, panther, crow, bear

input 2: black
candidates: cat, panther, crow, bear

input 3: whiskers
candidates: cat

target: cat
```

## metrics

```text
top_k_recall
candidate_set_size
candidate_set_reduction
rank_of_target
target_survival_rate
monotonic_narrowing_rate
false_elimination_rate
```

## pass threshold

Initial toy pass:

```text
top_3_recall >= 0.95
candidate_set_reduction >= 3x
false_elimination_rate <= 0.05
monotonic_narrowing_rate >= 0.75
```

If it cannot pass toy data, stop.

---

# phase 3: order importance test

## question

Does sequence matter?

## procedure

Compare:

```text
unordered graph
ordered trace
typed ordered trace
shuffled ordered trace
```

Use the same targets and evidence.

## pass condition for order

Ordered traces matter only if:

```text
ordered_trace beats unordered_neighborhood
and ordered_trace beats shuffled_order_control
```

Suggested threshold:

```text
>= 15% candidate set reduction improvement
with no meaningful recall loss
```

If ordered traces do not beat unordered traces, sequence probably does not matter for this substrate.

That is not fatal. It means the system should be graph-neighborhood based, not trajectory based.

---

# phase 4: typed edge test

## question

Do semantic relation types improve retrieval?

## procedure

Compare:

```text
ordered untyped:
  topology → long_window → true_inclusion → pass

typed:
  DOMAIN → topology
  METHOD → long_window
  METRIC → true_inclusion
  VERDICT → pass
```

## pass condition

Typed edges matter only if they improve specificity or contradiction handling.

Suggested threshold:

```text
typed_edges reduce candidate set size by >= 20%
without lowering top_k_recall by more than 3%
```

If typed edges do not help, avoid overengineering semantic labels.

---

# phase 5: contradiction and uncertainty test

## question

Can the substrate preserve competing trajectories instead of collapsing to one answer?

## procedure

Create records like:

```text
K-001 supported by L-001
K-001 weakened by L-002
K-001 contradicted by L-003
K-001 superseded by K-004
```

Feed partial evidence related to K-001.

Expected retrieval should return a neighborhood:

```text
accepted claims
supporting records
weakening records
contradictions
supersessions
```

Not just one winner.

## metrics

```text
conflict_recall
supersession_recall
support_vs_contradiction_separation
neighborhood_completeness
```

## pass threshold

```text
conflict_recall >= 0.9
supersession_recall >= 0.9
```

If contradictions disappear, the substrate is unsafe for research memory.

---

# phase 6: learning record retrieval test

## question

Can real research Learning Records be retrieved from partial task evidence?

## procedure

Use real Learning Records.

For each record:

1. Remove the target ID.
2. Feed partial concepts, metrics, methods, and claim relationships.
3. Retrieve candidates.
4. Measure whether the correct Learning Record and affected Claim appear.

Example input:

```text
topology memory
long window
true inclusion
candidate reduction
```

Expected:

```text
L-actual-use-long-window-result
K-topology-memory-retrieval-specificity
related conflicts or supersessions
```

## metrics

```text
learning_record_top_1
learning_record_top_5
claim_top_5
candidate_set_size
retrieval_latency_ms
hydration_cost
```

## pass threshold

```text
learning_record_top_5 >= 0.85
claim_top_5 >= 0.9
median_latency <= 50ms on local machine
candidate_set_reduction >= 10x
```

---

# phase 7: comparison against boring baselines

Do not trust the substrate unless it beats simple alternatives.

Compare against:

```text
SQLite keyword search
SQLite concept-tag join
BM25
vector embeddings if available
simple graph traversal
```

The substrate only matters if it wins on at least one important axis:

```text
better recall
better narrowing
better contradiction recall
better explanation
lower latency
better structural generalization
```

If SQLite tags beat it, use SQLite tags.

---

# phase 8: structural generalization test

## question

Can the substrate retrieve by relational shape rather than exact labels?

Example:

```text
A supports B using method C
X supports Y using method Z
```

These should be structurally similar even if the concepts differ.

## procedure

Create held-out records with different labels but same transition topology.

Query with partial transition structure.

## metrics

```text
structural_match_recall
lexical_independence
false_structural_match_rate
```

## pass threshold

```text
structural_match_recall >= 0.75
false_structural_match_rate <= 0.2
```

If it passes, this is where the substrate becomes more interesting than ordinary search.

---

# phase 9: mutation / update test

## question

Can new Learning Records update the substrate without retraining?

## procedure

1. Build substrate from initial records.
2. Measure retrieval.
3. Add new validated Learning Records.
4. Rebuild or incrementally update.
5. Measure whether relevant retrieval changes correctly.

Expected:

```text
new support strengthens claim neighborhood
new contradiction surfaces conflict
new supersession redirects retrieval
```

## pass condition

```text
updates are reflected deterministically
old provenance remains available
retrieval changes are explainable
```

---

# phase 10: authority test

## question

Can the substrate act as authoritative knowledge state?

This is the dangerous question.

It can only be authoritative if:

```text
state transitions are deterministic
state is replayable from logs
all transitions trace to validated Learning Records
contradictions are preserved
supersessions are preserved
retrieval never mutates accepted history
```

## pass condition

Delete the compiled substrate.

Replay from event logs and Learning Records.

The rebuilt substrate must produce equivalent retrieval results.

Suggested threshold:

```text
top_5 overlap >= 0.98
claim status equivalence = 1.0
conflict equivalence = 1.0
```

If replay cannot reproduce the state, it cannot be authoritative.

---

# minimal implementation plan

Build this in the research harness, not LDGR.

## module layout

```text
research/
  substrate/
    datasets/
    traces/
    indexes/
    retrieval/
    experiments/
    reports/
```

## first commands

```text
substrate build --dataset toy
substrate eval --variant unordered
substrate eval --variant ordered
substrate eval --variant typed
substrate compare
substrate report
```

## first artifact outputs

```text
results.json
candidate_traces.json
retrieval_steps.json
comparison.md
failure_cases.md
```

---

# kill criteria

Stop or redesign if any of these happen:

```text
toy data fails
candidate sets do not narrow
correct targets are eliminated too often
ordered traces do not beat shuffled controls
typed edges add complexity without improvement
real records perform worse than SQLite tags
contradictions collapse into single winners
replay does not reproduce retrieval state
```

---

# success criteria

The substrate is worth integrating into Episteme only if it demonstrates:

```text
1. evidence accumulation narrows candidate trajectories
2. correct claims survive narrowing
3. contradictions remain visible
4. retrieval is fast
5. results are replayable
6. relational structure beats at least one simple baseline
7. the system retrieves neighborhoods, not just single winners
```

---

# recommended first experiment

Start with the smallest falsifiable test:

```text
toy semantic world
unordered vs ordered vs typed vs shuffled
incremental evidence retrieval
candidate narrowing measurement
```

Acceptance criteria:

```text
top_3_recall >= 0.95
false_elimination_rate <= 0.05
candidate_set_reduction >= 3x
ordered or typed variant must beat shuffled control
```

If that fails, the substrate idea is probably not ready.

If that passes, move to synthetic Learning Records.

Do not touch LDGR integration until phase 6 passes.
