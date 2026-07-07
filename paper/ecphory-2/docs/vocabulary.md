# Ecphory Evidence-Control Vocabulary

## Core Philosophy

Ecphory is an evidence-conditioned control architecture.

The objective is not to retrieve the "best" historical memory and reuse it. The
objective is to preserve a bounded body of relevant historical experience,
reconstruct it, derive query-specific evidence, interpret that evidence into
hypotheses, and validate any control claim empirically.

Memory supplies historical experience.

Evidence objects organize what can be interpreted.

Interpretation derives hypotheses and candidate controls.

Runtime monitors track whether an active candidate still matches the current
trajectory.

Validation determines reality.

---

# Canonical Hierarchy

Use this hierarchy when naming artifacts, reports, prompts, and boundaries.

Short form: `Episode -> Trace -> Signature -> Evidence neighborhood -> Hydrated memory -> Evidence object -> Interpretation -> Policy candidate -> Runtime monitor -> Validation`

```text
Episode
    ↓
Trace
    ↓
Signature
    ↓
Evidence neighborhood
    ↓
Hydrated memory
    ↓
Evidence object
    ↓
Interpretation
    ↓
Policy candidate
    ↓
Runtime monitor
    ↓
Validation
```

Each stage has a different authority. Do not jump from one level to another
without naming the boundary transition. In particular:

* a trace is not a policy;
* a signature is not evidence interpretation;
* an evidence neighborhood is not a ranked recommendation;
* hydrated memory is not an evidence object until query-specific fields are
  derived;
* an evidence object is not a policy candidate;
* an interpretation is not validation;
* a policy candidate is not deployable durable knowledge;
* a runtime monitor report is not a validation result.

Post-validation writeback may become durable knowledge or future episodes, but
that writeback is downstream of validation rather than a substitute for it.

---

# Run Vocabulary

Use precise nouns when discussing LDGR, experiments, and gameplay. Avoid bare
`run` unless the surrounding sentence already names the layer.

## LDGR work item

A durable task record in the LDGR ledger.

Example: `design-trajectory-memory-first-experiment`.

Use for planning, implementation, auditing, or validation tasks that may create
one or more artifacts.

## LDGR work run

One execution of an LDGR work item by an agent or human.

An LDGR work run can succeed by producing a plan, decision, observation, or
artifact. It is not evidence that an Orbit Wars experiment produced a behavioral
result.

Preferred wording:

```text
LDGR work run 2 completed successfully.
```

Avoid:

```text
The experiment run succeeded.
```

when only the LDGR task completed.

## Experiment execution

A concrete execution of an experimental protocol that produces empirical data,
such as decision traces, validation records, score deltas, or ablation results.

Use this when behavior was actually measured.

Preferred wording:

```text
The trajectory-memory ablation experiment execution produced held-out decision traces.
```

## Validation execution

A concrete empirical check with an explicit authority scope, such as Rust/Python
parity, heldout behavioral validation, or promotion-gate validation.

Use this when the result is pass, fail, or inconclusive for a declared
validation scope.

## Orbit Wars episode

One game instance in the environment.

An episode may contain many turns and decision traces. Do not call an episode a
run in research summaries.

## Turn

One environment step within an Orbit Wars episode.

## Trace

A reusable temporal projection derived from an episode or selected decision
window. A trace is not an LDGR work run, experiment execution, or validation
result.

## Result

Always name the layer:

- `LDGR work result`: task outcome, artifacts, observations, and next decision.
- `experiment result`: empirical measurements from an experiment execution.
- `validation result`: pass/fail/inconclusive judgment for a declared scope.
- `episode result`: game outcome, score delta, statuses, and rewards.

---

# Boundary Transitions

## Episode → Trace

Trace generation projects chronological episode records into reusable temporal
views. It may copy validation metadata for provenance and diagnostics, but it
must not convert resolved outcome labels into retrieval keys or pre-
interpretation selection keys.

## Trace → Signature

Signature refinement canonicalizes recurring temporal structure from traces.
Signatures are retrieval keys. They are not semantic conclusions and do not
carry policy authority.

## Signature → Evidence neighborhood

Signature lookup returns the natural evidence neighborhood for that signature.
Neighborhood boundedness should come from signature refinement and lookup, not
from top-k ranking, winner selection, or majority voting.

## Evidence neighborhood → Hydrated memory

Hydration reconstructs each neighborhood member into replayable historical
memory with provenance, raw turns/events, lifecycle state, and validation
metadata boundaries. Hydration answers what happened; it does not decide what it
means.

## Hydrated memory → Evidence object

Evidence-object construction derives query-specific evidence fields from
hydrated memories. This is where support, contradiction, hazards, repairs,
restrictions, ambiguity, coverage, and provenance summaries become explicit.

## Evidence object → Interpretation

Interpretation examines evidence objects in context. It may produce decision
briefs, reconciliation views, action hypotheses, or policy-candidate synthesis inputs. It
must preserve uncertainty and provenance. It does not validate its own claims.

## Interpretation → Policy candidate

A policy candidate is a proposed control artifact compiled or selected from an
interpretation. It must retain its evidence sources, uncertainty, lifecycle
state, validation plan, and runtime guard boundary. It remains a hypothesis
until validation.

## Policy candidate → Runtime monitor

The runtime monitor tracks an active policy candidate or policy-library entry
against current traces/signatures and validated runtime guards. Generated prose,
watch cues, and unvalidated invalidation cues are report-only unless validation
promotes them into validated runtime guards.

## Runtime monitor → Validation

Validation is the empirical interaction with heldout data, simulation, or the
external environment. It records pass, fail, or inconclusive outcomes and keeps
failure cases as evidence for future episodes/traces.

---

# Terminology

## Episode

A chronological record of observed events.

Episodes represent history exactly as it occurred. They are immutable historical
observations rather than interpreted knowledge.

Compatibility note: older artifacts may say `raw episode`; in canonical prose,
use `episode` unless emphasizing immutability or unprocessed storage.

---

## Outcome Label Quarantine

Resolved outcome labels such as `win`, `loss`, `draw`, `winner`, `advantaged`,
and `disadvantaged` are validation metadata.

Episode and trace records should preserve the underlying scores, score diffs,
terminal rewards, terminal statuses, run exceptions, and label provenance. Those
fields document what happened at validation time.

Outcome labels must not be used as signature tokens, canonical signature-key
components, retrieval lookup keys, or pre-interpretation selection keys. They
may appear later as diagnostic coverage, continuation metadata, or validation
records, where they must remain explicitly labeled as validation metadata rather
than evidence authority.

---

## Trace

A reusable temporal projection derived from an episode.

A trace preserves enough chronological structure and provenance for later
signature refinement, lookup, hydration, and validation auditing.

Traces are refinement inputs, not interpretations or policy claims.

Compatibility note: current schemas and scripts often use `temporal-trace/v1`.
That schema name is compatible with the canonical term `trace`.

---

## Signature

A canonical representation of recurring temporal structure.

Signatures exist solely to support retrieval. They are retrieval keys rather
than semantic representations, policy triggers, outcome labels, or validation
claims.

Compatibility note: older docs may say `temporal signature` or `canonical
temporal signature`; in canonical hierarchy prose, use `signature` and mention
its temporal derivation only when the distinction matters.

---

## Signature Refinement

The offline process that transforms traces into signatures.

Refinement discovers recurring temporal structure while preserving provenance
and outcome-label quarantine.

---

## Evidence Neighborhood

The bounded collection of trace/history members retrieved for a signature.

The evidence neighborhood is not a ranked list and should not be interpreted as
nearest neighbors. Its purpose is to provide a bounded collection of relevant
historical experience for hydration and interpretation.

---

## Hydrated Memory

A retrieved neighborhood member reconstructed into a replayable historical
object.

A hydrated memory may contain:

* signature and trace provenance;
* replay or event trace;
* observations;
* validation metadata with quarantine boundaries;
* lifecycle state;
* neighboring signatures;
* references to related memories.

Hydration reconstructs historical experience. It does **not** determine what the
memory means for the current query.

Compatibility note: current schemas often use `hydrated-memory-object/v1`; that
is the artifact shape for canonical hydrated memory.

---

## Evidence Object

The query-specific structured workspace of evidence derived from hydrated
memory.

An evidence object is not the same thing as hydrated memory. It contains derived
fields for a particular question and should be discarded or versioned when that
question changes.

Typical evidence fields may include:

* derived claims;
* supporting observations;
* contradicting observations;
* repair observations;
* hazard observations;
* restriction observations;
* unresolved ambiguity;
* validation needs;
* provenance summary;
* coverage summary.

Compatibility note: current scripts and schemas may call this an `accumulated
evidence object` or `accumulated-evidence-object/v1`. Keep those schema names
stable for existing consumers, but use `evidence object` as the canonical
abstraction in prose.

---

## Evidence Field

A typed section within an evidence object.

Examples include:

* Supporting Evidence;
* Contradicting Evidence;
* Repair Evidence;
* Hazard Evidence;
* Restriction Evidence;
* Ambiguity Notes;
* Validation Needs.

Evidence fields are derived from historical replay. They are not stored directly
within episodes, traces, signatures, or hydrated memory.

---

## Interpretation

The process of examining evidence objects in the context of the current query.

Interpretation derives query-specific hypotheses from historical experience.
The same hydrated memory may support different evidence fields depending on the
question being asked.

Interpretation may produce:

* evidence reconciliation views;
* decision briefs;
* recommended arbitration inputs;
* policy-candidate synthesis inputs;
* candidate action hypotheses.

Interpretation does not modify memory and does not validate its own output.

---

## Evidence Reconciliation

The process of integrating evidence fields into an interpretation while
preserving mixed support, counter-support, hazards, repairs, restrictions,
ambiguity, and provenance.

Evidence reconciliation does not select a winner. It evaluates the interaction
between multiple forms of evidence and keeps contradiction visible when it
matters for validation or runtime safety.

Responsibilities include:

* claim extraction;
* support aggregation;
* contradiction analysis;
* repair integration;
* hazard assessment;
* restriction analysis;
* ambiguity estimation;
* hypothesis synthesis.

---

## Evidence Abstraction View

A non-destructive presentation or reconciliation view over canonical evidence.

An evidence abstraction view may group traces, select representatives, attach
recurrence weights, summarize feature ranges, or ask an interpreter to label
patterns. It exists to make an evidence neighborhood easier to inspect or to
support an evidence object/interpretation boundary. It does **not** replace the
canonical evidence neighborhood, hydrated memory, source memberships,
provenance, validation metadata, or trace digests.

Required preservation semantics:

* source neighborhoods remain canonical;
* member trace IDs, membership digests, and source artifact references remain
  inspectable;
* provenance summaries and validation metadata summaries travel with every
  group or presentation packet;
* representatives are examples, not substitutes for group members;
* recurrence weights are coverage metadata, not votes or authority;
* any omitted groups or prompt truncation must be counted and described;
* labels, merge hypotheses, and bins are descriptive/report-only unless later
  validation gives them authority.

Compatibility note: existing scripts and schemas may use names such as
`compression_boundary`, `compression_ratio`, `compressed_groups`, or
`temporal-signature-collapse/v1`. Keep those fields stable for current
consumers, but canonical prose should explain them as evidence abstraction views
or evidence reconciliation views rather than destructive data compression.

---

## Decision Brief

A compatibility output name for a structured interpretation artifact.

A decision brief summarizes the current interpretation of an evidence object.
It may contain a recommendation hypothesis, hazards, repairs, restrictions,
ambiguity, provenance, and validation needs. It is not itself a policy
candidate, runtime monitor report, or validation result.

---

## Policy Candidate

A proposed control artifact derived from interpretation.

Policy candidates may be compiled policy templates, selected policy-library
entries pending activation, or arbitration outputs. They must preserve their
evidence source, uncertainty, lifecycle state, guard boundary, and validation
plan.

A policy candidate remains unpromoted until validation supports promotion.

---

## Runtime Monitor

The cheap online boundary that compares current trajectory evidence with the
active policy candidate or policy-library entry.

A runtime monitor may compute current traces/signatures, report trajectory fit,
match report-only evidence cues, detect validated runtime guards, and request
arbitration or interpretation when an active candidate deviates.

The monitor does not perform broad historical reasoning every turn and does not
turn report-only cues into hard enforcement without validation provenance.

---

## Validation

The interaction with reality.

Validation determines whether an interpretation, policy candidate, runtime
guard, or deployed behavior was correct enough for its stated scope.

Validation is the only empirical authority within the architecture. Negative,
failed, and inconclusive validation results are first-class evidence.

Validation has two non-equivalent scopes:

* **Structural validity** checks that artifacts preserve the evidence-control
  boundary needed for later evaluation: provenance preservation, outcome-label
  quarantine, replay/hydration completeness, and evidence-abstraction or legacy
  compression membership preservation. A structural pass can authorize safe
  boundary crossing or inspection, but it does not validate a policy candidate,
  runtime guard, trajectory claim, or intervention outcome.
* **Behavioral validity** checks policy or runtime behavior against heldout
  data, simulation, or the external environment: policy generalization, runtime
  guard correctness, trajectory alignment, and intervention performance.
  Behavioral validation should cite structurally valid inputs, but its
  pass/fail/inconclusive outcome remains a separate empirical claim.

Mixed validation artifacts must label which fields are structural checks and
which fields are behavioral checks. Generated JSON can use additive
`validation_authority` metadata for this boundary, but metadata is descriptive:
it does not promote a policy candidate or runtime guard by itself. Do not treat
provenance integrity, quarantine success, hydration completeness, membership
preservation, schema validity, monitor reports, or interpretation quality as
policy success unless a behavioral validation record supports that claim.

---

## Durable Knowledge

Validated outcomes and preserved failure cases that become part of future
episodes, traces, reports, or policy-library lifecycle metadata.

Durable knowledge is accumulated through validation rather than assumption. It
is downstream of validation, not a replacement for validation.

---

# Retrieval Vocabulary

Prefer:

* episode;
* trace;
* signature;
* evidence neighborhood;
* hydrated memory;
* retrieval affinity;
* historical record;
* replayable memory.

Avoid:

* nearest neighbor;
* candidate memory;
* winner;
* prediction;
* similarity match;
* top-k result.

---

# Evidence Vocabulary

Prefer:

* evidence object;
* evidence field;
* evidence abstraction view;
* evidence reconciliation view;
* supporting observation;
* contradicting observation;
* repair observation;
* hazard observation;
* restriction observation;
* ambiguity note;
* validation need;
* provenance summary.

These are derived during evidence-object construction and interpretation rather
than stored directly within episodes or signatures.

Compatibility note: `accumulated evidence object` remains an accepted schema and
file name for existing artifacts, but `evidence object` is the canonical
abstraction.

---

# Interpretation Vocabulary

Prefer:

* interpretation;
* evidence reconciliation;
* claim extraction;
* ambiguity estimation;
* hypothesis synthesis;
* decision brief;
* policy-candidate synthesis input.

Avoid:

* voting;
* classification;
* winner selection;
* validation by interpretation.

Interpretation derives hypotheses from evidence objects and preserves the
boundary to policy candidates and validation.

---

# Policy and Runtime Vocabulary

Prefer:

* policy candidate;
* compiled policy template;
* policy-library lifecycle state;
* runtime monitor;
* trajectory monitor report;
* validated runtime guard;
* report-only evidence cue;
* policy validation record.

Avoid:

* deployable policy before validation;
* validated guard without validation provenance;
* runtime success from a monitor report alone;
* policy promotion from interpretation alone.

---

# Review Vocabulary

Review should be triggered only when evidence-object fields cannot be cleanly
interpreted into a bounded hypothesis or when runtime monitoring detects a
boundary that requires arbitration.

Examples include:

* ambiguous evidence;
* insufficient separation;
* contested evidence;
* unresolved ambiguity;
* missing validation provenance;
* policy deviation without a validated guard or replacement candidate.

Conflicting historical experiences are expected. Review should occur only when
those experiences remain genuinely unresolved after reconciliation or materially
affect runtime safety.

---

# Trust Hierarchy

```text
Episode
    Historical observation

↓

Trace
    Reusable temporal projection

↓

Signature
    Retrieval key

↓

Evidence neighborhood
    Retrieved historical experience

↓

Hydrated memory
    Replayable historical memory

↓

Evidence object
    Query-specific evidence workspace

↓

Interpretation
    Reconciled hypothesis with provenance and uncertainty

↓

Policy candidate
    Proposed control artifact, not yet durable authority

↓

Runtime monitor
    Online trajectory/guard boundary

↓

Validation
    Empirical authority
```

---

# Relationship to Graphs

Graphs are not assumed to be the primitive representation.

Hydrated memory preserves explicit relationships. Those relationships
collectively form a relational substrate. Specific graph views may be projected
from this substrate for different purposes, including:

* retrieval projection;
* provenance projection;
* repair projection;
* hazard projection;
* continuation projection;
* dependency projection;
* runtime-monitor projection;
* validation projection.

Multiple graph projections may coexist without requiring a single canonical
graph.

---

# Fundamental Design Principle

The architecture is evidence-first and validation-governed.

Retrieval assembles relevant historical experience.

Hydration reconstructs replayable memory.

Evidence objects derive query-specific fields from that memory.

Interpretation reconciles those fields into hypotheses.

Policy candidates encode proposed control behavior.

Runtime monitors track whether active candidates still match observed
trajectory.

Validation determines whether any recommendation, policy candidate, guard, or
runtime behavior was correct.

The objective is not to retrieve the correct memory.

The objective is to produce falsifiable, provenance-preserving control
hypotheses from historical experience while keeping validation as the empirical
authority.
