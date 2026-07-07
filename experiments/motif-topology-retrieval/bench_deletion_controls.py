"""First-occurrence deletion controls.

Question: after DP/LCS repaired neutral-noise collapse, is remaining DROP
brittleness specifically caused by deleting identity-establishing first
occurrences in canonical numbering?

This is deliberately narrow. It does not redesign identity globally.

Representations / controls:

  canonical_first_occurrence
      Current canonical node ids: first occurrence gets next id. Fixed DP/LCS
      matcher. Expected failure: deleting first occurrence of a recurring node
      can renumber later nodes.

  anchored_recurring
      Narrow control: recurring nodes (labels with count >1 in this walk) are
      assigned ids BEFORE singleton nodes, in first-occurrence order among
      recurring nodes. Singleton nodes are assigned after them. This should make
      recurring identities stable against deletion/insertion of singleton
      identity-establishing evidence, without using concrete labels as keys.

  edge_sequence
      Ordered typed-edge sequence LCS. Keeps order, gives up node recurrence.

  bag_edges
      Typed-edge multiset containment. Gives up order and recurrence. Control.

Metrics:
  - clean heldout accuracy / bundle reduction
  - polysemy both-active and +1 disambiguation
  - one-step deletion survival by category:
      first_recurring_occurrence, repeat_occurrence, singleton_occurrence
  - random drop surface magnitude 0..4
"""

from __future__ import annotations

import json
import os
import random
import statistics
from collections import Counter
from dataclasses import dataclass
from typing import Literal

from generator import Instance, build_generated_graph_with_polysemy
from matcher_relaxation import SigView, score
from signature import typed_canonical_signature

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

WEIGHTS = {"w_structure": 1.0, "w_typed": 0.5, "w_contradict": 0.7,
           "w_missing": 1.0, "w_extraneous": 0.15}
REGIMES = ("canonical_first_occurrence", "anchored_recurring", "edge_sequence", "bag_edges")


# ---------------------------------------------------------------------------
# signatures/views
# ---------------------------------------------------------------------------

def _edge_label(et, direction):
    if et is None:
        return "—"
    return f"{et}|{direction}"


def _view_from_trace(node_trace, edge_label_trace) -> SigView:
    transitions = list(zip(node_trace[:-1], edge_label_trace[1:], node_trace[1:], strict=False))
    edge_counter = Counter((a, lab, b) for a, lab, b in transitions if lab != "—")
    edge_bag = Counter(lab for lab in edge_label_trace[1:] if lab != "—")
    return SigView(
        node_trace=tuple(node_trace),
        edge_label_trace=tuple(edge_label_trace),
        typed_edges=frozenset(edge_counter),
        typed_edge_counts=tuple(sorted((a, lab, b, n) for (a, lab, b), n in edge_counter.items())),
        node_set=frozenset(set(node_trace)),
        edge_bag=tuple(sorted(edge_bag.items())),
    )


def canonical_view(walk) -> SigView:
    sig = typed_canonical_signature(walk)
    edge_bag = Counter(lab for lab in sig.edge_label_trace[1:] if lab != "—")
    return SigView(
        node_trace=sig.node_trace,
        edge_label_trace=sig.edge_label_trace,
        typed_edges=frozenset(sig.typed_edges),
        typed_edge_counts=sig.typed_edge_counts,
        node_set=frozenset(range(sig.node_count)),
        edge_bag=tuple(sorted(edge_bag.items())),
    )


def anchored_recurring_view(walk) -> SigView:
    """Assign recurring nodes first, then singleton nodes.

    This is a narrow first-occurrence-renumbering control. It anchors recurring
    identities against singleton deletion/insertion, but still derives ids from
    anonymous within-walk structure/order, not from concrete labels.
    """
    labels = [step[0] for step in walk]
    counts = Counter(labels)
    first_pos = {}
    for i, node in enumerate(labels):
        first_pos.setdefault(node, i)
    recurring = sorted([n for n, c in counts.items() if c > 1], key=lambda n: first_pos[n])
    singleton = sorted([n for n, c in counts.items() if c == 1], key=lambda n: first_pos[n])
    ids = {node: i for i, node in enumerate(recurring + singleton)}
    node_trace = [ids[n] for n in labels]
    edge_label_trace = [_edge_label(step[1], step[2]) if i > 0 else "—" for i, step in enumerate(walk)]
    return _view_from_trace(node_trace, edge_label_trace)


def edge_sequence(walk) -> tuple[str, ...]:
    return tuple(_edge_label(et, direction) for _node, et, direction in walk[1:])


def edge_bag(walk) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(Counter(edge_sequence(walk)).items()))


def lcs_len(a: tuple, b: tuple) -> int:
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            dp[i][j] = 1 + dp[i + 1][j + 1] if a[i] == b[j] else max(dp[i + 1][j], dp[i][j + 1])
    return dp[0][0]


# ---------------------------------------------------------------------------
# index/scoring
# ---------------------------------------------------------------------------

@dataclass
class Entry:
    family: str
    focal: str
    payload: object
    walk: list


class DeletionControlIndex:
    def __init__(self, regime: str):
        self.regime = regime
        self.entries: list[Entry] = []

    def _payload(self, walk):
        if self.regime == "canonical_first_occurrence":
            return canonical_view(walk)
        if self.regime == "anchored_recurring":
            return anchored_recurring_view(walk)
        if self.regime == "edge_sequence":
            return edge_sequence(walk)
        if self.regime == "bag_edges":
            return edge_bag(walk)
        raise ValueError(self.regime)

    def add(self, inst: Instance):
        self.entries.append(Entry(inst.family, inst.focal_node(), self._payload(inst.walk), inst.walk))

    def _score(self, cand_payload, ev_payload) -> float:
        if self.regime in ("canonical_first_occurrence", "anchored_recurring"):
            return score(cand_payload, ev_payload, matcher="dp", weights=WEIGHTS).total
        if self.regime == "edge_sequence":
            ev = ev_payload
            cand = cand_payload
            return round(lcs_len(ev, cand) / len(ev), 4) if ev else 1.0
        if self.regime == "bag_edges":
            cand = Counter(dict(cand_payload))
            ev = Counter(dict(ev_payload))
            denom = sum(ev.values())
            covered = sum(min(cand[k], ev[k]) for k in ev)
            return round(covered / denom, 4) if denom else 1.0
        raise ValueError(self.regime)

    def relax(self, walk) -> dict:
        ev = self._payload(walk)
        scored = []
        for ent in self.entries:
            total = self._score(ent.payload, ev)
            scored.append({"family": ent.family, "focal": ent.focal, "total": total})
        scored.sort(key=lambda r: r["total"], reverse=True)
        dom = None
        if scored:
            top = scored[0]["total"]
            fams = {r["family"] for r in scored if abs(r["total"] - top) < 1e-9}
            dom = next(iter(fams)) if len(fams) == 1 else None
        b = bundle(scored)
        gap = None
        if len(scored) > 1:
            top_fam = scored[0]["family"]
            for r in scored[1:]:
                if r["family"] != top_fam:
                    gap = round(scored[0]["total"] - r["total"], 4)
                    break
        return {
            "dominant_family": dom,
            "top_score": scored[0]["total"] if scored else None,
            "score_gap": gap,
            "bundle_size": len(b),
            "family_counts": dict(Counter(r["family"] for r in b)),
            "ranked": scored,
        }


def bundle(scored, frac=0.9):
    if not scored:
        return []
    top = scored[0]["total"]
    threshold = top * frac if top > 0 else top * (2 - frac)
    out = []
    for r in scored:
        if (top >= 0 and r["total"] >= threshold) or (top < 0 and r["total"] <= threshold):
            out.append(r)
        else:
            break
    return out or scored[:1]


def build_index(all_instances, regime):
    idx = DeletionControlIndex(regime)
    for _fam, insts in all_instances.items():
        for inst in insts[:-1]:
            idx.add(inst)
    return idx


# ---------------------------------------------------------------------------
# deletion analysis
# ---------------------------------------------------------------------------

def delete_step(walk, i):
    return [step for j, step in enumerate(walk) if j != i]


def deletion_category(walk, i) -> str:
    labels = [s[0] for s in walk]
    node = labels[i]
    first = labels.index(node) == i
    total = labels.count(node)
    if first and total > 1:
        return "first_recurring_occurrence"
    if total > 1:
        return "repeat_occurrence"
    return "singleton_occurrence"


def heldout_metrics(idx, all_instances):
    correct, bundles = [], []
    for fam in sorted(all_instances):
        if not fam.startswith("gen_"):
            continue
        r = idx.relax(all_instances[fam][-1].walk)
        correct.append(r["dominant_family"] == fam)
        bundles.append(r["bundle_size"])
    mean_bundle = statistics.fmean(bundles) if bundles else 0.0
    return {
        "heldout_accuracy": round(statistics.fmean(correct), 4) if correct else None,
        "mean_bundle": round(mean_bundle, 4),
        "bundle_reduction": round(len(idx.entries) / mean_bundle, 4) if mean_bundle else 0.0,
    }


def polysemy_metrics(idx, all_instances, polysemy_meta):
    both, disamb, rows = [], [], []
    for pair_id, (fa, fb, share_k) in enumerate(polysemy_meta):
        walk_a = all_instances[fa][-1].walk
        r_shared = idx.relax(walk_a[:share_k])
        r_plus = idx.relax(walk_a[:min(share_k + 1, len(walk_a))])
        fams = set(r_shared["family_counts"])
        ba = fa in fams and fb in fams
        di = r_plus["dominant_family"] == fa
        both.append(ba); disamb.append(di)
        rows.append({"pair_id": pair_id, "family_a": fa, "family_b": fb, "share_k": share_k,
                     "both_active_on_shared": ba, "correct_after_plus_one": di,
                     "dominant_after_plus_one": r_plus["dominant_family"],
                     "shared_bundle_size": r_shared["bundle_size"]})
    return {
        "both_active_rate": round(statistics.fmean(both), 4) if both else None,
        "disambiguation_rate": round(statistics.fmean(disamb), 4) if disamb else None,
        "rows": rows,
    }


def one_step_drop_by_category(idx, all_instances):
    by_cat = {}
    rows = []
    for fam in sorted(all_instances):
        if not fam.startswith("gen_"):
            continue
        walk = all_instances[fam][-1].walk
        for i in range(1, len(walk) - 1):
            cat = deletion_category(walk, i)
            r = idx.relax(delete_step(walk, i))
            survived = r["dominant_family"] == fam
            by_cat.setdefault(cat, []).append(survived)
            rows.append({"family": fam, "deleted_step": i, "category": cat,
                         "survived": survived, "dominant": r["dominant_family"],
                         "bundle_size": r["bundle_size"], "score_gap": r["score_gap"]})
    return {
        "summary": {cat: round(statistics.fmean(vals), 4) for cat, vals in sorted(by_cat.items())},
        "counts": {cat: len(vals) for cat, vals in sorted(by_cat.items())},
        "rows": rows,
    }


def random_drop_surface(idx, all_instances, n_magnitudes=4, seed=42):
    rng = random.Random(seed)
    series = []
    for fam in sorted(all_instances):
        if not fam.startswith("gen_"):
            continue
        walk = all_instances[fam][-1].walk
        interior = list(range(1, len(walk) - 1))
        pts = []
        for mag in range(n_magnitudes + 1):
            if mag == 0:
                pw = walk
            else:
                if mag > len(interior):
                    break
                pw = delete_step_many(walk, rng.sample(interior, mag))
            r = idx.relax(pw)
            pts.append({"magnitude": mag, "survived": r["dominant_family"] == fam,
                        "dominant": r["dominant_family"], "bundle_size": r["bundle_size"],
                        "score_gap": r["score_gap"]})
        series.append({"family": fam, "points": pts})
    by_mag = {}
    for s in series:
        for p in s["points"]:
            by_mag.setdefault(p["magnitude"], []).append(p["survived"])
    summary = {str(m): round(statistics.fmean(vals), 4) for m, vals in sorted(by_mag.items())}
    transition = None
    for m in sorted(by_mag):
        if statistics.fmean(by_mag[m]) < 0.5:
            transition = m
            break
    return {"summary": summary, "transition": transition, "series": series}


def delete_step_many(walk, indices):
    drop = set(indices)
    return [s for i, s in enumerate(walk) if i not in drop]


def render_report(results):
    lines = [
        "# First-Occurrence Deletion Controls", "",
        "Fixed DP/LCS for trace regimes. This tests whether drop brittleness is specifically first-occurrence canonical renumbering.", "",
        "## Clean / Polysemy / Drop Summary", "",
        "| regime | heldout | bundle | reduction | polysemy | first-rec drop | repeat drop | singleton drop | random drop T |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for reg in REGIMES:
        h = results[reg]["heldout"]
        p = results[reg]["polysemy"]
        d = results[reg]["one_step_drop"]["summary"]
        surf = results[reg]["random_drop_surface"]
        lines.append(
            f"| {reg} | {h['heldout_accuracy']} | {h['mean_bundle']} | {h['bundle_reduction']} | "
            f"{p['disambiguation_rate']} | {d.get('first_recurring_occurrence', '—')} | "
            f"{d.get('repeat_occurrence', '—')} | {d.get('singleton_occurrence', '—')} | {surf['transition']} |"
        )
    lines += ["", "## Random Drop Surface", ""]
    mags = sorted(set(int(m) for reg in REGIMES for m in results[reg]["random_drop_surface"]["summary"]))
    lines += ["| magnitude | " + " | ".join(REGIMES) + " |",
              "|---:|" + "---:|" * len(REGIMES)]
    for m in mags:
        vals = [results[reg]["random_drop_surface"]["summary"].get(str(m), "—") for reg in REGIMES]
        lines.append(f"| {m} | " + " | ".join(str(v) for v in vals) + " |")
    lines += ["", "## Interpretation", "",
              "If anchored_recurring improves first-recurring-occurrence deletion while preserving polysemy/reduction, the cause is confirmed as first-occurrence canonical renumbering and a narrow anchor may be viable. If only edge_sequence/bag improves, deletion robustness is available by giving up recurrence shape. If none improves without tradeoffs, deletion of identity-establishing evidence is a true destructive perturbation for this substrate." ]
    return "\n".join(lines) + "\n"


def main():
    print("building data...")
    _, _, all_instances, polysemy_meta, _ = build_generated_graph_with_polysemy(
        n_disjoint_families=20, n_polysemy_bases=10, instances_per=3, seed=20260706)
    results = {}
    print("\nFIRST-OCCURRENCE DELETION CONTROLS")
    print("=" * 86)
    for reg in REGIMES:
        idx = build_index(all_instances, reg)
        h = heldout_metrics(idx, all_instances)
        p = polysemy_metrics(idx, all_instances, polysemy_meta)
        d = one_step_drop_by_category(idx, all_instances)
        surf = random_drop_surface(idx, all_instances, n_magnitudes=4, seed=42)
        results[reg] = {"heldout": h, "polysemy": p, "one_step_drop": d,
                        "random_drop_surface": surf}
        print(f"\n--- {reg} ---")
        print("heldout:", h)
        print("polysemy:", {k: v for k, v in p.items() if k != "rows"})
        print("one-step drop:", d["summary"], "counts:", d["counts"])
        print("random drop:", surf["summary"], "transition:", surf["transition"])

    out = {"experiment": "first-occurrence-deletion-controls",
           "branch": "first-occurrence-deletion-control",
           "weights": WEIGHTS,
           "regimes": REGIMES,
           "comparison": results}
    json_path = os.path.join(OUT_DIR, "deletion_controls_results.json")
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2)
    md_path = os.path.join(OUT_DIR, "deletion_controls_report.md")
    with open(md_path, "w") as f:
        f.write(render_report(results))
    print(f"\nwrote {os.path.basename(json_path)}")
    print(f"wrote {os.path.basename(md_path)}")


if __name__ == "__main__":
    main()
