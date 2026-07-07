"""Smoke test: prove the typed canonical signature behaves correctly on the
knowledge graph before building retrieval/controls/benchmark.

Shows three things the phase-0 toy could not:
  1. Two DIFFERENT contested claims (disjoint labels) collapse to the SAME
     typed signature -> identity-free motif consolidation is possible.
  2. A relabel (automorphic equivalent) is identical -> it is a positive,
     not a negative (the bug that made phase-0's control degenerate).
  3. A shuffle of walk steps gives a DIFFERENT signature -> order/topology
     is actually being used (not just set membership).
  4. validated_claim (a star) gets a different, weaker signature than the
     contested_claim diamond -> the predicted-weak control behaves as expected.
"""

from __future__ import annotations

import random

from graph_dataset import FAMILY_OF_CLAIM, build_graph, rooted_walk, walks_for
from signature import label_free_canonical_signature, typed_canonical_signature


def fmt_walk(walk):
    parts = []
    for node, et, direction in walk:
        tag = "" if et is None else f"-[{et}/{direction}]->"
        parts.append(f"{tag}{node}")
    return " ".join(parts)


def shuffled_walk(walk, seed):
    # keep root fixed; permute the rest (mimics the phase-0 shuffled control,
    # but on a walk where order carries topology)
    rng = random.Random(seed)
    rest = list(walk[1:])
    rng.shuffle(rest)
    return [walk[0]] + rest


def relabeled_walk(walk, mapping):
    return [(mapping.get(n, n), et, d) for (n, et, d) in walk]


def main():
    g = build_graph()
    walks = walks_for(g, FAMILY_OF_CLAIM.keys(), max_depth=2)

    print("=" * 78)
    print("SMOKE: typed canonical signatures on knowledge-graph walks")
    print("=" * 78)

    # 1. contested claims -> same typed signature?
    print("\n[1] contested_claim family: do K-001, K-002, K-003 share a signature?")
    sigs = {}
    for k in ["K-001", "K-002", "K-003"]:
        s = typed_canonical_signature(walks[k])
        sigs[k] = s.key()
        print(f"  {k} walk: {fmt_walk(walks[k])}")
        print(f"        node_trace={s.node_trace}")
        print(f"        typed_sig = {s.key()[:90]}...")
    same = sigs["K-001"] == sigs["K-002"] == sigs["K-003"]
    print(f"  -> identical typed signature across 3 disjoint claims? {same}")

    # 2. automorphic equivalent (relabel) is identical
    print("\n[2] automorphic equivalent (relabel K-001 nodes) must match K-001")
    mapping = {"K-001": "K-001p", "L-001": "L-001p", "L-002": "L-002p",
               "long_window_motifs": "m_prime", "true_inclusion": "met_prime",
               "coverage": "cov_prime", "topology_memory": "dom_prime",
               "passed": "v1", "failed": "v2"}
    relabeled = relabeled_walk(walks["K-001"], mapping)
    rs = typed_canonical_signature(relabeled)
    print(f"  K-001 sig == relabeled sig? {sigs['K-001'] == rs.key()}  (must be True)")

    # 3. shuffle differs
    print("\n[3] shuffled walk must NOT match (order/topology is used)")
    sh = shuffled_walk(walks["K-001"], seed=0)
    shs = typed_canonical_signature(sh)
    print(f"  K-001 sig == shuffled sig? {sigs['K-001'] == shs.key()}  (must be False)")

    # 4. validated_claim star vs contested diamond
    print("\n[4] validated_claim (star) vs contested_claim (diamond) signatures")
    for k in ["K-001", "K-004"]:
        s = typed_canonical_signature(walks[k])
        print(f"  {k} ({FAMILY_OF_CLAIM[k]}): node_count={s.node_count} "
              f"distinct_edges={len(s.typed_edges)} "
              f"recurrence={'YES' if len(set(s.node_trace)) < len(s.node_trace) else 'no'}")
    print("  -> star should have LESS recurrence than the diamond")

    # 5. typed vs label-free: do edge labels discriminate families?
    print("\n[5] typed signature vs label-free: do relation types discriminate?")
    print("  (label-free collapses SUPPORTS/WEAKENS/SUPERSEDED_BY all to '—')")
    print(f"  {'claim':6} {'family':18} {'typed_key':40} {'labelfree_key':40}")
    for k in FAMILY_OF_CLAIM:
        t = typed_canonical_signature(walks[k]).key()[:38]
        lf = label_free_canonical_signature(walks[k]).key()[:38]
        print(f"  {k:6} {FAMILY_OF_CLAIM[k]:18} {t:40} {lf:40}")

    # 6. label-free cross-family collision check (phase-8 preview)
    print("\n[6] label-free cross-family: do DIFFERENT families share shape?")
    lf_keys = {}
    for k in FAMILY_OF_CLAIM:
        lf_keys.setdefault(label_free_canonical_signature(walks[k]).key(), []).append(k)
    for key, members in lf_keys.items():
        fams = {FAMILY_OF_CLAIM[m] for m in members}
        flag = "  <-- shape shared across families" if len(fams) > 1 else ""
        print(f"  {FAMILY_OF_CLAIM[members[0]]:18} {members} {flag}")

    print("\n" + "=" * 78)
    print("If [1]=True, [2]=True, [3]=False -> the substrate port is sound.")
    print("Next: motif_memory.py (consolidation + set-valued retrieval) + controls.py.")
    print("=" * 78)


if __name__ == "__main__":
    main()
