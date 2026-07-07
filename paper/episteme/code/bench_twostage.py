"""Two-stage retrieval: topology recall + typed unpack.

Architecture:
  STORAGE KEY   = label-free canonical signature (identity-free, edge-types
                  collapsed). This is the basin. Coarse, broad.
  PAYLOAD       = the typed canonical signature (edge types kept), stored
                  per motif but NOT part of the key.
  RETRIEVAL     = coarse match on topology -> bundle B_coarse.
                  Then unpack stored typed signatures within B_coarse and
                  re-match on typed prefix -> B_fine.

The semantic edge labels never participate in the coarse index. They are a
projection you unpack on demand. (Branch thesis: the graph is a projection;
the concept is a basin.)

Measure: does this recover the typed disambiguation (which pure-labelfree lost,
0.25) while keeping the index label-free and inclusion at 1.0?
"""

from __future__ import annotations

import json
import os
import statistics
from collections import Counter

from generator import build_generated_graph_with_polysemy
from signature import label_free_canonical_signature, typed_canonical_signature
from generator import Instance

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def _prefix(sig, length):
    return sig.node_trace[:length], sig.edge_label_trace[:length]


class TwoStageIndex:
    def __init__(self):
        self.entries: list[dict] = []  # {family, typed_sig, labelfree_sig, inst}

    def add(self, inst: Instance) -> None:
        self.entries.append({
            "family": inst.family,
            "focal": inst.focal_node(),
            "typed_sig": typed_canonical_signature(inst.walk),
            "labelfree_sig": label_free_canonical_signature(inst.walk),
            "walk": inst.walk,
        })

    def relax(self, walk, length: int | None = None) -> dict:
        """Two-stage: topology coarse -> typed fine."""
        if length is None:
            length = len(walk)
        q_typed = typed_canonical_signature(walk)
        q_lf = label_free_canonical_signature(walk)
        q_lf_node, _ = _prefix(q_lf, length)
        q_typed_node, q_typed_edge = _prefix(q_typed, length)

        # STAGE 1: coarse topology recall (label-free)
        coarse = []
        for e in self.entries:
            lf_node, _ = _prefix(e["labelfree_sig"], length)
            if lf_node == q_lf_node:
                coarse.append(e)

        # STAGE 2: unpack typed payload, refine
        fine = []
        for e in coarse:
            t_node, t_edge = _prefix(e["typed_sig"], length)
            if t_node == q_typed_node and t_edge == q_typed_edge:
                fine.append(e)

        return {
            "length": length,
            "coarse_n": len(coarse),
            "fine_n": len(fine),
            "coarse_families": dict(Counter(e["family"] for e in coarse)),
            "fine_families": dict(Counter(e["family"] for e in fine)),
            "fine_dominant": self._dom(fine),
            "coarse_dominant": self._dom(coarse),
        }

    @staticmethod
    def _dom(entries):
        if not entries:
            return None
        c = Counter(e["family"] for e in entries)
        top = c.most_common(1)[0][1]
        tied = [f for f, n in c.items() if n == top]
        return None if len(tied) > 1 else tied[0]


def main():
    print("building data...")
    g, skeletons, all_instances, polysemy_meta, _ = build_generated_graph_with_polysemy(
        n_disjoint_families=20, n_polysemy_bases=10, instances_per=3, seed=20260706)
    idx = TwoStageIndex()
    for fam, insts in all_instances.items():
        for inst in insts[:-1]:
            idx.add(inst)
    n_idx = len(idx.entries)

    print(f"\nTWO-STAGE: topology recall (coarse) -> typed unpack (fine)")
    print(f"indexed: {n_idx} instances, {len(set(e['family'] for e in idx.entries))} families\n")

    # held-out retrieval
    print("HELD-OUT RETRIEVAL:")
    inclusions, coarse_sizes, fine_sizes = [], [], []
    for fam in sorted(all_instances):
        if not fam.startswith("gen_"):
            continue
        held = all_instances[fam][-1]
        r = idx.relax(held.walk)
        inc = fam in r["fine_families"]
        inclusions.append(inc)
        coarse_sizes.append(r["coarse_n"])
        fine_sizes.append(r["fine_n"])
    print(f"  inclusion_rate (fine): {round(statistics.fmean(inclusions), 4)}")
    print(f"  mean coarse bundle:   {round(statistics.fmean(coarse_sizes), 3)}")
    print(f"  mean fine bundle:     {round(statistics.fmean(fine_sizes), 3)}")
    print(f"  coarse reduction:     {round(n_idx/statistics.fmean(coarse_sizes), 2)}x")
    print(f"  fine reduction:       {round(n_idx/statistics.fmean(fine_sizes), 2)}x")

    # polysemy
    print("\nPOLYSEMY (the real test):")
    both_active, disambiguate = [], []
    for i, (fa, fb, share_k) in enumerate(polysemy_meta):
        walk_a = all_instances[fa][-1].walk
        r_share = idx.relax(walk_a, length=share_k)
        r_p1 = idx.relax(walk_a, length=min(share_k + 1, len(walk_a)))
        ba = fa in r_share["coarse_families"] and fb in r_share["coarse_families"]
        di = r_p1["fine_dominant"] == fa
        both_active.append(ba)
        disambiguate.append(di)
        print(f"  pair {i}: share_k={share_k} "
              f"coarse_shared={r_share['coarse_n']:>2} fine_shared={r_share['fine_n']:>2} "
              f"both_active(coarse)={ba} dom_after_+1(fine)={r_p1['fine_dominant']} correct={di}")
    print(f"\n  both_active_rate:    {round(statistics.fmean(both_active), 4)}")
    print(f"  disambiguation_rate: {round(statistics.fmean(disambiguate), 4)}")

    # comparison table
    print("\n" + "=" * 56)
    print("COMPARISON (pure-typed | pure-labelfree | two-stage)")
    print("=" * 56)
    print(f"  {'metric':<24} {'typed':>8} {'labelfree':>10} {'two-stage':>10}")
    print(f"  {'inclusion':<24} {'1.0':>8} {'1.0':>10} {round(statistics.fmean(inclusions),3):>10}")
    print(f"  {'bundle reduction':<24} {'36.0':>8} {'24.5':>10} {round(n_idx/statistics.fmean(fine_sizes),1):>10}")
    print(f"  {'polysemy disambig':<24} {'0.875':>8} {'0.25':>10} {round(statistics.fmean(disambiguate),3):>10}")
    print(f"  {'coarse recall':<24} {'-':>8} {'-':>10} {round(statistics.fmean(coarse_sizes),2):>10}")


if __name__ == "__main__":
    main()
