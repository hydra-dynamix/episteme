"""Soft-scoring relaxation over typed walks.

Replaces exact prefix-consistency pruning (which had drop-stability interior =
0.0: deleting any interior evidence step renumbers the canonical trace and the
perturbed walk matches nothing) with a graded score.

score(candidate, evidence) =
    matched_required_structure   # how much of the evidence's structure the
                                 # candidate also contains (as subsequence, not
                                 # contiguous prefix)
  + typed_payload_support        # bonus when edge types also align
  - contradiction_penalty        # explicit edge-type clashes (SUPPORTS vs WEAKENS
                                 # on the same node transition)
  - missing_evidence_penalty     # evidence steps the candidate cannot account for

The crucial change from hard pruning: matching is now SUBSEQUENCE, not prefix.
Dropping an interior evidence step no longer breaks the match -- the remaining
steps still form a subsequence and score positively. This is what makes the
basin potentially stable under deletion.

This module measures the perturbation surface (drop/corrupt/noise), NOT a single
pass/fail. The result of interest is where the basin transitions, not whether
it holds at one perturbation.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field

from generator import Instance
from signature import label_free_canonical_signature, typed_canonical_signature


# ---------------------------------------------------------------------------
# signature views we score against
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SigView:
    """Precomputed views of a walk used by the scorer."""
    node_trace: tuple[int, ...]
    edge_label_trace: tuple[str, ...]      # "—" sentinel or "TYPE|dir"
    typed_edges: frozenset[tuple[int, str, int]]           # set of (a, label, b)
    typed_edge_counts: Counter               # (a, label, b) -> count
    node_count: int


def view(walk, *, typed: bool) -> SigView:
    sig = typed_canonical_signature(walk) if typed else label_free_canonical_signature(walk)
    return SigView(
        node_trace=sig.node_trace,
        edge_label_trace=sig.edge_label_trace,
        typed_edges=frozenset(sig.typed_edges),
        typed_edge_counts=Counter({(a, l, b): n for a, l, b, n in sig.typed_edge_counts}),
        node_count=sig.node_count,
    )


# ---------------------------------------------------------------------------
# matching primitives
# ---------------------------------------------------------------------------

def _is_subsequence(needle: Sequence, haystack: Sequence) -> tuple[bool, int]:
    """Longest-common-subsequence-style: how many needle items appear in order in haystack.

    Returns (matched_count, len(needle)). For our use, needle = evidence trace,
    haystack = candidate trace. We count how many evidence items can be matched
    in order. This is a subsequence match count, not contiguous.
    """
    if not needle:
        return True, 0
    it = iter(haystack)
    matched = 0
    for item in needle:
        for x in it:
            if x == item:
                matched += 1
                break
    return matched, len(needle)


def _best_alignment(evidence_nodes, candidate_nodes):
    """Greedy in-order alignment of evidence nodes onto candidate nodes.

    Returns dict evidence_position -> candidate_node_id (the canonical id each
    evidence position mapped to), plus the count aligned. Used to compute edge
    support and contradictions on the aligned subsequence.
    """
    alignment: dict[int, int] = {}
    cand_iter = enumerate(candidate_nodes)
    j, j_node = next(cand_iter, (None, None))
    for i, e_node in enumerate(evidence_nodes):
        while j is not None:
            if candidate_nodes[j] == e_node:
                alignment[i] = candidate_nodes[j]
                j, j_node = next(cand_iter, (None, None))
                break
            j, j_node = next(cand_iter, (None, None))
    return alignment


# ---------------------------------------------------------------------------
# scorer
# ---------------------------------------------------------------------------

@dataclass
class SoftScore:
    matched_structure: float
    typed_support: float
    contradiction: float
    missing_evidence: float
    total: float
    aligned_fraction: float       # fraction of evidence steps aligned


def score(candidate_view: SigView, evidence_view: SigView, *, weights: dict) -> SoftScore:
    """Score a candidate against evidence under the soft rule.

    weights keys: w_structure, w_typed, w_contradict, w_missing (all positive
    magnitudes; penalties subtracted).
    """
    e_nodes = evidence_view.node_trace
    c_nodes = candidate_view.node_trace
    # structure: how many evidence nodes align in order to candidate
    matched, total_e = _is_subsequence(e_nodes, c_nodes)
    aligned_frac = matched / total_e if total_e else 1.0
    structure_score = weights["w_structure"] * aligned_frac

    # typed support: among the aligned positions, how many evidence edges also
    # appear (same type, between aligned nodes) in the candidate's edge set?
    alignment = _best_alignment(e_nodes, c_nodes)
    typed_support = 0.0
    contradiction = 0.0
    e_edges_aligned = 0
    for i in range(1, len(e_nodes)):
        if i not in alignment or (i - 1) not in alignment:
            continue
        # the evidence edge between position i-1 and i
        e_lab = evidence_view.edge_label_trace[i] if i < len(evidence_view.edge_label_trace) else "—"
        if e_lab == "—":
            continue
        e_edges_aligned += 1
        a_node = alignment[i - 1]
        b_node = alignment[i]
        # does the candidate have this typed edge?
        cand_has = (a_node, e_lab, b_node) in candidate_view.typed_edges
        if cand_has:
            typed_support += weights["w_typed"]
        else:
            # contradiction: same (a,b) node pair but different label?
            pair_labels = {lab for (aa, lab, bb) in candidate_view.typed_edges
                           if aa == a_node and bb == b_node}
            if pair_labels and e_lab not in pair_labels:
                contradiction += weights["w_contradict"]

    # missing evidence penalty: evidence steps that did NOT align
    missing = total_e - matched
    missing_penalty = weights["w_missing"] * (missing / total_e if total_e else 0)

    total = structure_score + typed_support - contradiction - missing_penalty
    return SoftScore(
        matched_structure=round(structure_score, 4),
        typed_support=round(typed_support, 4),
        contradiction=round(contradiction, 4),
        missing_evidence=round(missing_penalty, 4),
        total=round(total, 4),
        aligned_fraction=round(aligned_frac, 4),
    )


# ---------------------------------------------------------------------------
# relaxation index (soft)
# ---------------------------------------------------------------------------

@dataclass
class SoftRelaxationIndex:
    weights: dict
    variant: str = "typed"   # which signature view to score against
    entries: list[dict] = field(default_factory=list)

    def add(self, inst: Instance) -> None:
        self.entries.append({
            "family": inst.family,
            "focal": inst.focal_node(),
            "view": view(inst.walk, typed=(self.variant == "typed")),
            "walk": inst.walk,
        })

    def add_all(self, insts: Sequence[Instance]) -> None:
        for inst in insts:
            self.add(inst)

    def relax(self, evidence_walk, top_k: int | None = None) -> dict:
        """Score all candidates against evidence; return ranked bundle."""
        e_view = view(evidence_walk, typed=(self.variant == "typed"))
        scored = []
        for e in self.entries:
            s = score(e["view"], e_view, weights=self.weights)
            scored.append({**s.__dict__, "family": e["family"], "focal": e["focal"]})
        scored.sort(key=lambda r: r["total"], reverse=True)
        if top_k:
            scored = scored[:top_k]
        # dominant family: the family holding the top score. We compare at the
        # FAMILY level, not instance level -- two instances of the same family
        # tying at the top is a confident dominant, not ambiguity. Ambiguity is
        # when two DIFFERENT families tie at the top.
        dominant = None
        if scored:
            top_score = scored[0]["total"]
            top_families = {r["family"] for r in scored if abs(r["total"] - top_score) < 1e-9}
            dominant = next(iter(top_families)) if len(top_families) == 1 else None
        fam_counts = Counter(r["family"] for r in scored[:self._bundle_size(scored)])
        return {
            "ranked": scored,
            "dominant_family": dominant,
            "top_score": scored[0]["total"] if scored else None,
            "score_gap": self._family_gap(scored),
            "family_counts": dict(fam_counts),
        }

    @staticmethod
    def _family_gap(scored) -> float | None:
        """Score gap between the top family and the best DIFFERENT family."""
        if len(scored) < 2:
            return None
        top_fam = scored[0]["family"]
        top_score = scored[0]["total"]
        for r in scored[1:]:
            if r["family"] != top_fam:
                return round(top_score - r["total"], 4)
        return None  # no different family present

    @staticmethod
    def _bundle_size(scored) -> int:
        """Bundle = candidates within a small score margin of the top (the basin)."""
        if not scored:
            return 0
        top = scored[0]["total"]
        # keep all within 10% of top, minimum 1
        threshold = top * 0.9 if top > 0 else top * 1.1
        n = 0
        for r in scored:
            if (top >= 0 and r["total"] >= threshold) or (top < 0 and r["total"] <= threshold):
                n += 1
            else:
                break
        return max(n, 1)
