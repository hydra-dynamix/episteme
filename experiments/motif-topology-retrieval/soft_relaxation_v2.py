"""Noise-taxonomy-aware soft scorer.

Diagnosis (verified): the v1 scorer treated extra unmatched evidence as 'missing
evidence' because _is_subsequence aligned-fraction dropped when foreign nodes
were inserted, AND the missing-evidence penalty fired on the unaligned count.
Result: the true family's score collapsed 5.0 -> 0.55 under 2 noise items even
though nothing was contradicted. Extra evidence was scored as bad evidence.

Fix: separate three distinct failure modes with distinct penalties.

Per evidence step, classify it as one of:
  ALIGNED      : the candidate can account for this step (node + edge match in order)
  MISSING      : the evidence step COULD have aligned (its node is in the
                 candidate's node set) but didn't -- genuinely missing structure.
                 Penalize at w_missing (the candidate lacks evidence-relevant structure).
  EXTRANEOUS   : the evidence step's node is NOT in the candidate's node set --
                 irrelevant to this candidate. Penalize weakly at w_extraneous,
                 UNLESS it activates a competing basin (handled separately).

Contradiction stays: same (a,b) node pair, different edge label.

Target behavior:
  drop                 -> graceful degradation (mostly MISSING)
  corrupt              -> contradiction-sensitive degradation (CONTRADICTION)
  neutral noise        -> mostly ignored (EXTRANEOUS, weak)
  competing-basin noise-> ambiguity rises before collapse (EXTRANEOUS that aligns
                          a rival better than the current dominant)
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from generator import Instance
from signature import typed_canonical_signature


@dataclass(frozen=True)
class SigView:
    node_trace: tuple[int, ...]
    edge_label_trace: tuple[str, ...]
    typed_edges: frozenset[tuple[int, str, int]]
    node_set: frozenset[int]


def view(walk, *, typed: bool) -> SigView:
    sig = typed_canonical_signature(walk)  # typed always; labelfree collapses labels in scorer if needed
    return SigView(
        node_trace=sig.node_trace,
        edge_label_trace=sig.edge_label_trace,
        typed_edges=frozenset(sig.typed_edges),
        node_set=frozenset(range(sig.node_count)),
    )


@dataclass
class SoftScoreV2:
    aligned: int
    missing: int           # could-have-aligned but didn't
    extraneous: int        # node not in candidate at all
    contradiction: float
    structure_score: float
    typed_support: float
    missing_penalty: float
    extraneous_penalty: float
    contradict_penalty: float
    total: float


def score_v2(candidate_view: SigView, evidence_view: SigView, *, weights: dict) -> SoftScoreV2:
    """Score candidate against evidence with the three-way evidence classification."""
    e_nodes = evidence_view.node_trace
    e_edges = evidence_view.edge_label_trace
    c_nodes = candidate_view.node_trace

    # greedy in-order alignment of evidence nodes onto candidate nodes
    aligned_positions: dict[int, int] = {}  # evidence_pos -> cand_node_id
    j = 0
    for i, e_node in enumerate(e_nodes):
        while j < len(c_nodes):
            if c_nodes[j] == e_node:
                aligned_positions[i] = c_nodes[j]
                j += 1
                break
            j += 1

    aligned = len(aligned_positions)
    # classify each UNALIGNED evidence position
    missing = 0
    extraneous = 0
    for i, e_node in enumerate(e_nodes):
        if i in aligned_positions:
            continue
        if e_node in candidate_view.node_set:   # wait -- node_set is canonical; this is post-canonicalization
            # the canonical id IS in the candidate's id range but didn't align in order
            missing += 1
        else:
            extraneous += 1

    # NOTE: node ids are canonical (first-occurrence) per walk, so "in node_set"
    # is comparing canonical ids across two independently-canonicalized walks.
    # A foreign node CAN collide in id with a candidate node by coincidence
    # (both walks have a node 2). That's a real ambiguity we accept; the
    # edge-label check below refines it. The classification is approximate but
    # distinguishes 'structurally similar region' from 'totally foreign'.

    # typed support + contradiction over aligned positions
    typed_support = 0.0
    contradiction = 0.0
    for i in range(1, len(e_nodes)):
        if i not in aligned_positions or (i - 1) not in aligned_positions:
            continue
        e_lab = e_edges[i] if i < len(e_edges) else "—"
        if e_lab == "—":
            continue
        a, b = aligned_positions[i - 1], aligned_positions[i]
        if (a, e_lab, b) in candidate_view.typed_edges:
            typed_support += weights["w_typed"]
        else:
            pair_labels = {lab for (aa, lab, bb) in candidate_view.typed_edges if aa == a and bb == b}
            if pair_labels and e_lab not in pair_labels:
                contradiction += weights["w_contradict"]

    total_e = len(e_nodes)
    aligned_frac = aligned / total_e if total_e else 1.0

    structure_score = weights["w_structure"] * aligned_frac
    missing_penalty = weights["w_missing"] * (missing / total_e if total_e else 0)
    extraneous_penalty = weights["w_extraneous"] * (extraneous / total_e if total_e else 0)
    contradict_penalty = contradiction  # already weighted per-edge above

    total = structure_score + typed_support - missing_penalty - extraneous_penalty - contradict_penalty

    return SoftScoreV2(
        aligned=aligned, missing=missing, extraneous=extraneous, contradiction=contradiction,
        structure_score=round(structure_score, 4), typed_support=round(typed_support, 4),
        missing_penalty=round(missing_penalty, 4), extraneous_penalty=round(extraneous_penalty, 4),
        contradict_penalty=round(contradict_penalty, 4), total=round(total, 4),
    )


@dataclass
class SoftRelaxationIndexV2:
    weights: dict
    variant: str = "typed"
    entries: list[dict] = None

    def __post_init__(self):
        if self.entries is None:
            self.entries = []

    def add(self, inst: Instance) -> None:
        self.entries.append({
            "family": inst.family, "focal": inst.focal_node(),
            "view": view(inst.walk, typed=(self.variant == "typed")), "walk": inst.walk,
        })

    def add_all(self, insts: Sequence[Instance]) -> None:
        for inst in insts:
            self.add(inst)

    def relax(self, evidence_walk) -> dict:
        e_view = view(evidence_walk, typed=(self.variant == "typed"))
        scored = []
        for e in self.entries:
            s = score_v2(e["view"], e_view, weights=self.weights)
            scored.append({**s.__dict__, "family": e["family"], "focal": e["focal"]})
        scored.sort(key=lambda r: r["total"], reverse=True)
        dominant = None
        if scored:
            top_score = scored[0]["total"]
            top_families = {r["family"] for r in scored if abs(r["total"] - top_score) < 1e-9}
            dominant = next(iter(top_families)) if len(top_families) == 1 else None
        # family gap: top family vs best different family
        gap = None
        if len(scored) >= 2:
            top_fam = scored[0]["family"]
            for r in scored[1:]:
                if r["family"] != top_fam:
                    gap = round(scored[0]["total"] - r["total"], 4)
                    break
        return {
            "ranked": scored, "dominant_family": dominant,
            "top_score": scored[0]["total"] if scored else None,
            "score_gap": gap,
            "family_counts": dict(Counter(r["family"] for r in scored[:self._bundle(scored)])),
        }

    @staticmethod
    def _bundle(scored) -> int:
        if not scored:
            return 0
        top = scored[0]["total"]
        threshold = top * 0.9 if top > 0 else top * 1.1
        n = 0
        for r in scored:
            if (top >= 0 and r["total"] >= threshold) or (top < 0 and r["total"] <= threshold):
                n += 1
            else:
                break
        return max(n, 1)
