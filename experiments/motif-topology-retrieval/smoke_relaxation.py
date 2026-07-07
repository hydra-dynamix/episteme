"""Behavioral smoke: does discrete relaxation behave like the basin thesis needs?

Shows two things before any metrics are built:
  POLYSEMY (bat/bank): for a prefix-shared pair (poly_A, poly_B):
    - shared prefix evidence  -> BOTH basins active (ambiguity held, not collapsed)
    - +1 disambiguating step  -> correct basin dominates
    - missing that step        -> ambiguity remains (no hallucinated certainty)
  PERTURBATION (basin depth): for a clean disjoint family, drop each evidence
    step in turn; does the dominant family survive? (the falsification criterion)

This is the data-behavior check. If polysemy collapses early or basins flip on a
one-item drop, the substrate is too shallow and we stop before measuring.
"""

from __future__ import annotations

from generator import build_generated_graph_with_polysemy
from relaxation import RelaxationIndex


def run_polysemy_demo(instances, pairs, idx: RelaxationIndex) -> None:
    print("=" * 78)
    print("POLYSEMY DEMO: does relaxation hold ambiguity then disambiguate?")
    print("=" * 78)
    if not pairs:
        print("  (no polysemy pairs generated; skip)")
        return
    fa, fb, share_k = pairs[0]
    inst_a = instances[fa][0]
    inst_b = instances[fb][0]
    print(f"\npair: {fa} <-> {fb}  shared_prefix_len={share_k}")
    print(f"  A walk focal={inst_a.focal_node()}")
    print(f"  B walk focal={inst_b.focal_node()}")

    # evidence = A's walk. Test at shared prefix, then +1, then full.
    walk_a = inst_a.walk
    print(f"\n  evidence growth (querying A's walk, indexed on all families):")
    print(f"  {'evidence_len':>12} {'n_active':>9} {'n_families':>11} {'dominant':>10}  note")
    for length in [share_k, share_k + 1, share_k + 2, len(walk_a)]:
        length = min(length, len(walk_a))
        st = idx.relax(walk_a, length=length)
        note = ""
        if length == share_k:
            note = "<-- shared prefix: expect BOTH A and B active (ambiguous)"
        elif length <= share_k + 2:
            note = "<-- disambiguating step: expect A to dominate"
        else:
            note = "<-- full evidence: expect A only"
        dom = st.dominant_family or "(tied)"
        print(f"  {length:>12} {st.n_active:>9} {st.n_distinct_families:>11} {dom:>10}  {note}")
        if st.n_distinct_families <= 6:
            print(f"              families: {dict(st.family_counts)}")

    # missing-suffix: query at share_k+1 should leave >=2 active if ambiguous
    st_share = idx.relax(walk_a, length=share_k)
    print(f"\n  missing-disambiguator check (evidence_len={share_k}):")
    print(f"    n_distinct_families={st_share.n_distinct_families} "
          f"(expect >=2 for a real polysemy pair; =2 here = {fa}+{fb})")
    held = fa in dict(st_share.family_counts) and fb in dict(st_share.family_counts)
    print(f"    both pair members active on shared prefix? {held}  (must be True)")


def run_perturbation_demo(instances, idx: RelaxationIndex) -> None:
    print("\n" + "=" * 78)
    print("PERTURBATION DEMO: basin stability under one-item evidence removal")
    print("=" * 78)
    # pick a disjoint family
    family = "gen_000"
    if family not in instances:
        print(f"  ({family} not present; skip)")
        return
    inst = instances[family][0]
    walk = inst.walk
    print(f"\nfamily={family} focal={inst.focal_node()} walk_len={len(walk)}")
    full = idx.relax(walk)
    print(f"  full-evidence dominant family: {full.dominant_family} "
          f"(n_active={full.n_active}, n_families={full.n_distinct_families})")
    stab = idx.basin_stability(walk)
    print(f"\n  basin stability under one-item removal:")
    print(f"    base_family={stab['base_family']}  "
          f"stability_rate={stab['stability_rate']}  "
          f"({stab['n_survived']}/{stab['n_droppable_steps']} steps survived)")
    print(f"    per-step:")
    for r in stab["per_step"]:
        flag = "OK " if r["survived"] else "FLIP"
        print(f"      drop step {r['dropped_step']:>2}: dominant={r['dominant_after'] or '(tied)':>10} "
              f"n_active={r['n_active_after']:>3} n_fam={r['n_families_after']}  [{flag}]")


def main():
    print("building data (disjoint families + polysemy pairs)...")
    g, disjoint_skel, instances, polysemy_meta, _ = build_generated_graph_with_polysemy(
        n_disjoint_families=15, n_polysemy_bases=8, instances_per=3, seed=20260706,
    )
    print(f"  families: {len(disjoint_skel)} disjoint + {len(polysemy_meta)} polysemy pairs")
    print(f"  total instances indexed: {sum(len(v) for v in instances.values())}")

    idx = RelaxationIndex(variant="typed")
    for fam_insts in instances.values():
        idx.add_all(fam_insts)

    run_polysemy_demo(instances, polysemy_meta, idx)
    run_perturbation_demo(instances, idx)

    print("\n" + "=" * 78)
    print("If POLYSEMY shows >=2 active on the shared prefix AND A dominates after")
    print("the disambiguator, and PERTURBATION shows most steps survive, the")
    print("relaxation behaves like the basin thesis. Next: metrics (steps 4-5).")
    print("=" * 78)


if __name__ == "__main__":
    main()
