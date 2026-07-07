"""Noise-taxonomy surface: separate three kinds of 'extra evidence'.

The v1 noise result (transition at magnitude 2) conflated three cases. This
benchmark distinguishes them explicitly:

  NEUTRAL_NOISE       : insert steps whose nodes/edges are NOT in any indexed
                        family's structure (truly foreign). Target: mostly ignored.
  COMPATIBLE_NOISE    : insert steps that duplicate existing structure (harmless
                        repetition). Target: ignored.
  COMPETING_BASIN     : insert steps taken from a DIFFERENT indexed family's walk
                        (activates a rival basin). Target: ambiguity rises before
                        collapse, not immediate collapse.

For each noise type, sweep magnitude and measure survival + score_gap +
bundle_size + (for competing) whether a second basin becomes co-dominant.

Compares v1 scorer (missing collapses extraneous) vs v2 (separate penalties).
"""

from __future__ import annotations

import json
import os
import random
import statistics
from collections import Counter

from generator import build_generated_graph_with_polysemy
from soft_relaxation import SoftRelaxationIndex as IdxV1
from soft_relaxation_v2 import SoftRelaxationIndexV2 as IdxV2

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

W1 = {"w_structure": 1.0, "w_typed": 0.5, "w_contradict": 0.7, "w_missing": 1.0}
W2 = {"w_structure": 1.0, "w_typed": 0.5, "w_contradict": 0.7,
      "w_missing": 1.0, "w_extraneous": 0.15}  # extraneous MUCH weaker than missing


# ---------------------------------------------------------------------------
# noise constructors (all insert into the evidence walk at random non-root positions)
# ---------------------------------------------------------------------------

def neutral_noise(walk, n, rng):
    """Insert n truly foreign steps: synthetic nodes with synthetic edges."""
    foreign_labels = ["FOREIGN|in", "FOREIGN|out"]
    out = list(walk)
    for k in range(n):
        # use a node id that won't collide: prefix with F
        node = f"F-foreign-{k}-{rng.randint(0,9999)}"
        lab = rng.choice(foreign_labels)
        et, direction = lab.split("|")
        pos = rng.randint(1, len(out))
        out.insert(pos, (node, et, direction))
    return out


def compatible_noise(walk, n, rng):
    """Insert n duplicated existing steps (harmless repetition)."""
    out = list(walk)
    for _ in range(n):
        donor_step = walk[rng.randint(1, len(walk) - 1)]
        pos = rng.randint(1, len(out))
        out.insert(pos, donor_step)
    return out


def competing_basin_noise(walk, n, rng, donor_walks, exclude_family_steps=None):
    """Insert n steps taken from OTHER families' walks (activates rivals)."""
    out = list(walk)
    donors = [w for w in donor_walks]  # all walks except the query's own family handled by caller
    for _ in range(n):
        donor = rng.choice(donors)
        step = donor[rng.randint(1, len(donor) - 1)]
        pos = rng.randint(1, len(out))
        out.insert(pos, step)
    return out


# ---------------------------------------------------------------------------
# surface map
# ---------------------------------------------------------------------------

def map_noise_taxonomy(idx, instances_by_family, scorer_version: str, n_mag=4, seed=42):
    rng = random.Random(seed)
    # donor walks = all indexed walks (for competing-basin we'll exclude self below)
    all_indexed_walks = [inst.walk for fam in instances_by_family
                         for inst in instances_by_family[fam][:-1]]
    results = {"neutral": [], "compatible": [], "competing": []}

    for fam in sorted(instances_by_family):
        if not fam.startswith("gen_"):
            continue
        walk = instances_by_family[fam][-1].walk
        unperturbed = idx.relax(walk)
        base_dom = unperturbed["dominant_family"]
        if base_dom is None:
            continue
        # donors excluding this family's own walks
        donor_walks = [inst.walk for f in instances_by_family if f != fam
                       for inst in instances_by_family[f][:-1]]

        for mode in ("neutral", "compatible", "competing"):
            series = {"family": fam, "mode": mode, "base_dom": base_dom, "points": []}
            for mag in range(0, n_mag + 1):
                if mag == 0:
                    pw = walk
                elif mode == "neutral":
                    pw = neutral_noise(walk, mag, rng)
                elif mode == "compatible":
                    pw = compatible_noise(walk, mag, rng)
                else:
                    pw = competing_basin_noise(walk, mag, rng, donor_walks)
                r = idx.relax(pw)
                # for competing: did a second family become co-dominant (tie)?
                ranked = r["ranked"]
                top_score = ranked[0]["total"] if ranked else None
                tied_families = ({rk["family"] for rk in ranked
                                  if top_score is not None and abs(rk["total"] - top_score) < 1e-9}
                                 if ranked else set())
                co_dominant = len(tied_families) >= 2
                series["points"].append({
                    "magnitude": mag, "survived": r["dominant_family"] == base_dom,
                    "dominant": r["dominant_family"], "top_score": r["top_score"],
                    "score_gap": r["score_gap"], "bundle_size": len(r["family_counts"]),
                    "ambiguous": r["dominant_family"] is None, "co_dominant": co_dominant,
                    "tied_families": sorted(tied_families)[:4],
                })
            results[mode].append(series)
    return results


def summarize(surface) -> dict:
    out = {}
    for mode, series_list in surface.items():
        by_mag = {}
        for s in series_list:
            for pt in s["points"]:
                by_mag.setdefault(pt["magnitude"], {"survived": [], "co_dom": [], "gap": []})
                by_mag[pt["magnitude"]]["survived"].append(pt["survived"])
                by_mag[pt["magnitude"]]["co_dom"].append(pt["co_dominant"])
                if pt["score_gap"] is not None:
                    by_mag[pt["magnitude"]]["gap"].append(pt["score_gap"])
        out[mode] = {
            str(mag): {
                "survival": round(statistics.fmean(d["survived"]), 4) if d["survived"] else None,
                "co_dominant_rate": round(statistics.fmean(d["co_dom"]), 4) if d["co_dom"] else None,
                "mean_gap": round(statistics.fmean(d["gap"]), 4) if d["gap"] else None,
            }
            for mag, d in sorted(by_mag.items())
        }
    return out


def main():
    print("building data...")
    g, skeletons, all_instances, polysemy_meta, _ = build_generated_graph_with_polysemy(
        n_disjoint_families=20, n_polysemy_bases=10, instances_per=3, seed=20260706)

    print("\nNOISE TAXONOMY SURFACE")
    print("=" * 70)
    comparison = {}
    for version, IdxCls, weights, label in [("v1", IdxV1, W1, "v1 (extraneous=missing)"),
                                            ("v2", IdxV2, W2, "v2 (separate penalties)")]:
        idx = IdxCls(weights=weights, variant="typed")
        for fam, insts in all_instances.items():
            for inst in insts[:-1]:
                idx.add(inst)
        surface = map_noise_taxonomy(idx, all_instances, scorer_version=version)
        summary = summarize(surface)
        comparison[version] = {"surface": surface, "summary": summary}
        print(f"\n--- {label} ---")
        print(f"{'mag':<5} {'neutral_surv':>12} {'compat_surv':>12} {'compete_surv':>13} {'compete_coDom':>14}")
        all_mags = sorted(set(int(m) for mode in summary.values() for m in mode))
        for mag in all_mags:
            ns = summary["neutral"].get(str(mag), {}).get("survival", "—")
            cs = summary["compatible"].get(str(mag), {}).get("survival", "—")
            comp_s = summary["competing"].get(str(mag), {}).get("survival", "—")
            comp_cod = summary["competing"].get(str(mag), {}).get("co_dominant_rate", "—")
            print(f"{mag:<5} {str(ns):>12} {str(cs):>12} {str(comp_s):>13} {str(comp_cod):>14}")

    out = {"experiment": "noise-taxonomy-surface",
           "branch": "basin-depth-and-soft-relaxation",
           "weights_v1": W1, "weights_v2": W2,
           "comparison": comparison}
    with open(os.path.join(OUT_DIR, "noise_taxonomy_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote noise_taxonomy_results.json")


if __name__ == "__main__":
    main()
