"""Smoke: prove the edit-stability property differs across regimes.

The whole branch thesis rests on this: under CANONICAL, inserting a foreign
node renumbers every subsequent node's id. Under ROLE_PAYLOAD, it does not
(the existing nodes' incident structure is unchanged). Under LABEL, ids are
trivially stable but that's label-key (leakage). BAG_OF_EDGES has no node ids.

We verify by:
  1. Take a walk, compute ids under each regime.
  2. Insert a foreign node at position 3.
  3. Recompute ids.
  4. Count how many EXISTING (pre-insertion) nodes kept their identity.

CANONICAL should show massive id churn after the insertion point.
ROLE_PAYLOAD should show ~0 churn (existing nodes keep their structural role).
LABEL shows 0 churn (trivially) but that's because it IS the label.
"""

from __future__ import annotations

import importlib.util, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

gen = _load("generator", os.path.join(HERE, "generator.py"))
identity = _load("identity_regimes", os.path.join(HERE, "identity_regimes.py"))


def ids_stable_under_insertion(walk, regime, insert_pos, foreign_step):
    """Return (n_before, n_kept_id) for nodes that existed before insertion.

    IMPORTANT: 'kept' means the node's id at its ORIGINAL position is preserved
    in the perturbed trace at the corresponding position. We compare position-by-
    position (skipping the inserted slot) so that trace alignment -- not just
    'does the id appear somewhere' -- is what's measured. This is what actually
    matters for subsequence matching downstream.
    """
    ids_before = identity.assign_identities(walk, regime)
    perturbed = walk[:insert_pos] + [foreign_step] + walk[insert_pos:]
    ids_after = identity.assign_identities(perturbed, regime)
    # position-by-position: for each original position i, the perturbed position
    # is i if i < insert_pos, else i+1. Compare ids at those aligned positions.
    kept = 0
    total = 0
    for i in range(len(walk)):
        total += 1
        j = i if i < insert_pos else i + 1  # skip the inserted slot
        if ids_before[i] == ids_after[j]:
            kept += 1
    return kept, total, ids_before, ids_after


def main():
    g, skels, insts, poly, _ = gen.build_generated_graph_with_polysemy(
        n_disjoint_families=5, n_polysemy_bases=3, instances_per=3, seed=20260706)
    walk = insts["gen_000"][0].walk
    print(f"base walk: {len(walk)} steps, labels: {[s[0] for s in walk][:6]}...")
    foreign = ("F-foreign-X", "FOREIGN", "in")

    print("\nEDIT-STABILITY: insert foreign node at position 3")
    print(f"{'regime':<14} {'ids_kept':>10} {'/':>4} {'total':>6}  {'ids_before':<30} {'ids_after':<30}")
    for regime in ("canonical", "label", "role_payload"):
        kept, total, ib, ia = ids_stable_under_insertion(walk, regime, 3, foreign)
        flag = "STABLE" if kept == total else f"CHURN ({total-kept} changed)"
        print(f"  {regime:<12} {kept:>10} / {total:<4}   {str(ib[:8]):<30} {str(ia[:9]):<30} [{flag}]")

    print("\nThis is the root cause made visible:")
    print("  CANONICAL     : ids after insertion are totally different -> matcher fails")
    print("  LABEL         : ids stable but identity = label (leakage)")
    print("  ROLE_PAYLOAD  : ids stable AND identity = structural role (the goal)")

    # also show: do role_payload identities collide across DIFFERENT labels?
    print("\nIDENTITY PURITY (role_payload): do different labels share ids?")
    all_walks_labels = [(insts[f][i].walk, insts[f][i].focal_node())
                        for f in insts for i in range(len(insts[f]))]
    leak = identity.label_leakage(all_walks_labels[:60])
    for k, v in leak.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
