# Operating Envelope: Recurrence-Sensitive Historical Memory Substrate

## Frozen Substrate Claim

```text
canonical label-free topology index
  -> broad basin retrieval
  -> typed/content payload projection
  -> DP/LCS alignment
  -> fine discrimination
```

This substrate is not a general edit-distance memory. It is a recurrence-sensitive basin retriever with typed/content projection.

## Headline Result: LDGR Historical Memory Content

The decisive test used actual LDGR project history as memory content:

- LDGR observations
- artifact descriptions
- report chunks

The corpus was stratified by topic to avoid one recent deletion report dominating the benchmark.

```text
memory items: 32
clean accuracy: 1.0
mean fine bundle: 1.0
bundle reduction: 32x
```

So the benchmark is a valid memory-retrieval test, not merely an encoding failure.

## Two-Stage Behavior

The best headline is the topic polysemy probe:

```text
shared topical inclusion:   1.0
+mechanism disambiguation:  0.9231
bundle:                     5.58 -> 1.15
```

Interpretation:

```text
shared topic evidence activates a broad basin bundle
mechanism/content payload projection narrows the bundle
```

That is the intended architecture in miniature.

## Plausible Partial Queries

Behaviorally plausible modes included:

- prefix/incomplete recall
- prefix plus neutral noise
- salient summary
- single evidence omission

Results:

```text
n:                                  224
first-recurring deletion incidence: 0.2634
survival:                           0.8884
survival with first-rec deletion:   0.8644
survival without first-rec deletion:0.8970
mean fine bundle:                   1.1071
```

So identity-establishing deletion is harmful, but not usually fatal under plausible historical-memory query formation.

## Control / Adversarial Partial Queries

Control modes included broad random partial notes and explicit first-recurring deletion.

```text
n:                                  96
first-recurring deletion incidence: 0.9583
survival:                           0.4479
```

This confirms the weak point remains real: adversarial/random deletion of identity-establishing evidence can destroy the basin.

## Updated Boundary Statement

Earlier boundary:

> first-occurrence deletion breaks the substrate

Updated boundary:

> first-occurrence deletion is a destructive perturbation in isolation, but realistic redundant memory queries often survive it.

## Mechanism History

### Noise collapse

Initial noise collapse was not a representation failure. It was a matcher failure.

```text
cause: greedy single-pass alignment treated one inserted unmatched node as terminal
repair: DP/LCS skip-capable alignment
result: noise transition improved 2 -> 3 without damaging polysemy/reduction
```

### Deletion brittleness

Deletion controls showed the tradeoff:

```text
canonical recurrence:
  strong polysemy / discrimination
  weaker first-occurrence deletion

edge_sequence / bag_edges:
  deletion robust
  weaker polysemy / discrimination
```

Anchored recurring identity was rejected because it did not repair deletion and damaged polysemy.

### Behavioral relevance

LDGR-history memory content showed the synthetic deletion boundary is often tolerable under realistic redundant queries.

## What This Supports

Supported within this operating envelope:

```text
label-free topology can serve as a broad basin index
stored typed/content payloads can narrow and disambiguate
DP/LCS alignment repairs neutral-noise matcher collapse
LDGR historical findings can be retrieved under plausible partial/noisy queries
recurrence-sensitive discrimination remains useful beyond bag/edge controls
```

## What This Does Not Claim

Does not claim:

```text
perfect noise stability
general edit-distance memory
robustness to broad random deletion
robustness to adversarial removal of identity-establishing evidence
scale beyond the current small LDGR-history corpus
semantic truth, only retrieval over recorded historical findings
```

## Current Operating Envelope

```text
works:
  clean LDGR-history retrieval
  broad topical basin activation
  typed/mechanism disambiguation
  plausible incomplete queries
  plausible single omissions
  some neutral noise after DP/LCS repair

weak:
  broad random partial notes
  adversarial deletion of identity-establishing evidence
  deletion robustness if recurrence-sensitive discrimination must be preserved
```

## Stop Conditions for This Phase

Do not continue mechanism patching inside this substrate until a downstream task shows the operating envelope is insufficient.

The next useful work is integration/application testing, not another representation tweak.
