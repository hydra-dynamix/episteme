# Contract Validation Report

Validates that the paper's seed graph constitutes a **complete contract**: every
structural invariant holds, every obligation is semantically satisfied by the
realized content, and every load-bearing claim is protected by an obligation.

Method: refactory's `graph.invariants.check()` for structure; deterministic
content checks for semantic satisfaction; reference-set analysis for coverage.

## Verdict

```text
CONTRACT COMPLETE: YES
  structural invariants: PASS (v0 seed and v28 realized)
  obligation references:  ALL RESOLVE
  semantic satisfaction:  7/7 obligations satisfied by realized content
  claim coverage:         10/10 load-bearing claims protected
```

## 1. Structural invariants

`check()` passes on both the seed (v0) and the fully realized graph (v28):
- root exists; every child reference resolves
- leaves have no children; every node has at most one parent
- no cycles; all nodes reachable from root
- every obligation-referenced node exists
- every realization targets a leaf

## 2. Obligation reference integrity

All 7 obligations reference only live nodes:

```text
oblg-contrib-payoff          setup_payoff            -> {intro-contributions, substrate, results, boundary}
oblg-typed-claim-support     claim_support           -> {res-typed, results}
oblg-boundary-honesty        custom                  -> {res-deletion, res-behavioral, bnd-deletion}
oblg-ceiling-escape-support  claim_support           -> {res-payload, results}
oblg-matcher-vs-rep          setup_payoff            -> {sub-matcher, res-matcher}
oblg-lineage-accuracy        terminology_consistency -> {bg-open, lineage}
oblg-setvalued-support       claim_support           -> {res-setvalued, results}   [added during validation]
```

## 3. Semantic satisfaction (realized content honors each predicate)

| obligation | kind | check | result |
|---|---|---|---|
| contrib-payoff | setup_payoff | all 5 contributions developed in payoff regions | ✓ |
| typed-claim-support | claim_support | cites 1.0/0.25 polysemy, 0.69/0.29 corrupt | ✓ |
| boundary-honesty | custom | both isolated (0.5) and behavioral (0.86) numbers present; not framed as solved | ✓ |
| ceiling-escape-support | claim_support | cites node_bag 0.0 vs content_graph 0.7969 | ✓ |
| matcher-vs-rep | setup_payoff | cites transition 2→3, polysemy 1.0, reduction 34× | ✓ |
| lineage-accuracy | terminology_consistency | "run 46" + ceiling/falsification + label-overlap index | ✓ |
| setvalued-support | claim_support | cites inclusion 1.0, reduction 32×/36× | ✓ |

Note on boundary-honesty: an initial substring check flagged "solved", but the
hit was "re**solved**" in the phrase *"leaving the tradeoff as a mapped parameter
rather than a resolved constraint"* — which honors the obligation by explicitly
refusing to call the boundary solved.

## 4. Claim coverage (gap analysis)

Every load-bearing factual claim is protected by at least one obligation:

```text
res-typed              <- oblg-typed-claim-support
res-setvalued          <- oblg-setvalued-support      [gap found and closed during validation]
res-matcher            <- oblg-matcher-vs-rep
res-deletion           <- oblg-boundary-honesty
res-behavioral         <- oblg-boundary-honesty
res-payload            <- oblg-ceiling-escape-support
bg-open                <- oblg-lineage-accuracy
intro-contributions    <- oblg-contrib-payoff
bnd-deletion           <- oblg-boundary-honesty
sub-matcher            <- oblg-matcher-vs-rep
```

## Gap found and closed

The initial contract (6 obligations) had **one coverage gap**: `res-setvalued`
(the set-valued-retrieval-generalizes claim: inclusion 1.0, reduction 36×/32×,
ambiguity retention 1.0) was unprotected. This is contribution #2's evidence and
a headline result, so the gap was material.

Closed by adding `oblg-setvalued-support` (claim_support on `res-setvalued`)
via refactory's `AddObligation` mutation (v27 → v28), then re-validated. The
portable `seed.json` was synced to include the 7th obligation.

## What this validates

The contract is complete in the sense refactory's model intends:
- the **structure** is sound (invariants hold),
- the **claims are backed** (every load-bearing number lives under an obligation),
- the **content honors the predicates** (every obligation is satisfied by the realized text),
- and the **honesty constraints hold** (the deletion boundary is not framed as either solved or fatal; the run-46 ceiling is described as the specific falsification it was).

It does not validate rhetorical quality, novelty, or correctness of the underlying
experiments — only that the paper's graph contract is internally complete and
faithful to its evidence.
