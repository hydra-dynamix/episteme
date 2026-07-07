"""Smoke for the generator: prove generated families consolidate and discriminate.

Checks (the things that must hold before retrieval is meaningful):
  A. Within a family: all K instances share the SAME typed signature
     (identity-free consolidation works on generated data).
  B. Across families: different skeletons have DIFFERENT typed signatures
     (families are actually discriminable, not all collapsed to one motif).
  C. Property diversity: the generated suite isn't all one shape (>=3 distinct
     property-sets among families).
  D. At least min_properties per skeleton (generator invariant).
  E. Graph is well-formed (every edge endpoint is a known node).
"""

from __future__ import annotations

from collections import Counter

from generator import build_generated_graph
from signature import typed_canonical_signature


def main():
    N_FAMILIES = 20
    INSTANCES = 3
    g, skeletons, instances = build_generated_graph(
        n_families=N_FAMILIES, instances_per=INSTANCES, seed=20260706
    )

    print("=" * 78)
    print(f"GENERATOR SMOKE: {N_FAMILIES} families x {INSTANCES} instances")
    print("=" * 78)

    # [A] within-family consolidation
    print("\n[A] within-family typed signature consolidation")
    within_ok = 0
    for family, insts in instances.items():
        sigs = set()
        for inst in insts:
            sigs.add(typed_canonical_signature(inst.walk).key())
        ok = len(sigs) == 1
        within_ok += ok
        if not ok or family in ("gen_000", "gen_001", "gen_002"):
            skel = skeletons[int(family.split("_")[1])]
            print(f"  {family}: properties={skel.properties} distinct_sigs={len(sigs)} ok={ok}")
            if not ok:
                for s in sigs:
                    print(f"      {s[:95]}")
    print(f"  -> {within_ok}/{N_FAMILIES} families consolidate (all instances share a signature)")
    # [B] across-family discrimination
    print("\n[B] across-family discrimination")
    family_sigs: dict[str, str] = {}
    for family, insts in instances.items():
        family_sigs[family] = typed_canonical_signature(insts[0].walk).key()
    distinct = len(set(family_sigs.values()))
    print(f"  -> {distinct}/{N_FAMILIES} distinct family signatures")
    collisions = [f for f, k in family_sigs.items() if list(family_sigs.values()).count(k) > 1]
    if collisions:
        # group colliding families
        by_key: dict[str, list[str]] = {}
        for f, k in family_sigs.items():
            by_key.setdefault(k, []).append(f)
        for k, fs in by_key.items():
            if len(fs) > 1:
                props = [skeletons[int(f.split('_')[1])].properties for f in fs]
                print(f"    COLLISION: {fs} properties={props}")

    # [C] property diversity
    print("\n[C] property diversity across generated skeletons")
    prop_sets = Counter(s.properties for s in skeletons)
    for props, n in prop_sets.most_common():
        print(f"  {n:3d}x  {','.join(props) if props else '(none)'}")
    print(f"  -> {len(prop_sets)} distinct property-sets")

    # [D] min properties invariant
    print("\n[D] generator invariant: every skeleton has >=2 properties")
    weak = [f"gen_{i:03d}" for i, s in enumerate(skeletons) if len(s.properties) < 2]
    print(f"  -> skeletons with <2 properties: {len(weak)} {weak[:5]}")

    # [E] graph well-formedness
    print("\n[E] graph well-formedness")
    bad = []
    for src, d in g.out_edges.items():
        if src not in g.nodes:
            bad.append(("src", src))
        for et, tgt in d:
            if tgt not in g.nodes:
                bad.append(("tgt", tgt))
    print(f"  -> nodes={len(g.nodes)} edges={sum(len(v) for v in g.out_edges.values())} bad_endpoints={len(bad)}")

    # verdict
    print("\n" + "=" * 78)
    verdict = (
        "PASS" if within_ok == N_FAMILIES and distinct >= N_FAMILIES * 0.8
        and len(prop_sets) >= 3 and not weak and not bad
        else "REVIEW"
    )
    print(f"VERDICT: {verdict}")
    print("  A within-family consolidation: " + ("ok" if within_ok == N_FAMILIES else f"{within_ok}/{N_FAMILIES}"))
    print(f"  B across-family discrimination: {distinct}/{N_FAMILIES} distinct")
    print(f"  C property diversity: {len(prop_sets)} sets")
    print(f"  D min-properties invariant: {'ok' if not weak else 'BROKEN'}")
    print(f"  E graph well-formed: {'ok' if not bad else 'BROKEN'}")
    print("=" * 78)


if __name__ == "__main__":
    main()
