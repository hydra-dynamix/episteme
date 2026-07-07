"""Matcher ablation: greedy vs skip-capable alignment under canonical identity.

Representation is held fixed: canonical first-occurrence node ids + typed edge
payloads. Only the matcher changes.

Matchers:
  greedy        baseline bug: one unmatched inserted evidence node can exhaust
                the candidate iterator and make everything after it invisible.
  dp            LCS/edit-distance-style alignment; can skip unmatched evidence.
  bidirectional forward/backward skip heuristic; can skip unmatched evidence.
  bag_edges     control: typed edge-label multiset containment, no recurrence.

Metrics:
  perturbation surface: drop / corrupt / neutral noise stability
  polysemy disambiguation
  bundle reduction

Acceptance (not encoded as a gate): skip-capable alignment improves noise
stability without collapsing polysemy disambiguation or bundle reduction.
"""

from __future__ import annotations

import json
import os
import random
import statistics
from collections import Counter

from generator import build_generated_graph_with_polysemy
from matcher_relaxation import MatcherRelaxationIndex

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

WEIGHTS = {"w_structure": 1.0, "w_typed": 0.5, "w_contradict": 0.7,
           "w_missing": 1.0, "w_extraneous": 0.15}
MATCHERS = ("greedy", "dp", "bidirectional", "bag_edges")

TYPED_LABELS = ["SUPPORTS|in", "SUPPORTS|out", "WEAKENS|in", "WEAKENS|out",
                "CONTRADICTS|in", "CONTRADICTS|out", "USES_METHOD|out",
                "MEASURES|out", "MEASURES|in", "IN_DOMAIN|out", "IN_DOMAIN|in",
                "HAS_VERDICT|out", "SUPERSEDED_BY|out", "DERIVES_FROM|out"]


def drop_steps(walk, indices):
    return [walk[i] for i in range(len(walk)) if i == 0 or i not in indices]


def corrupt_steps(walk, indices, rng):
    out = list(walk)
    for i in indices:
        if i == 0:
            continue
        node, old_et, old_dir = out[i]
        choices = [x for x in TYPED_LABELS if x != f"{old_et}|{old_dir}"]
        et, direction = rng.choice(choices).split("|")
        out[i] = (node, et, direction)
    return out


def neutral_noise(walk, n, rng):
    out = list(walk)
    for k in range(n):
        node = f"F-neutral-{k}-{rng.randint(0, 999999)}"
        et, direction = rng.choice(["FOREIGN|in", "FOREIGN|out"]).split("|")
        pos = rng.randint(1, len(out))
        out.insert(pos, (node, et, direction))
    return out


def build_index(all_instances, matcher):
    idx = MatcherRelaxationIndex(matcher=matcher, weights=WEIGHTS)
    for _fam, insts in all_instances.items():
        for inst in insts[:-1]:
            idx.add(inst)
    return idx


def map_surface(idx, all_instances, n_magnitudes=4, seed=42):
    rng = random.Random(seed)
    out = {"drop": [], "corrupt": [], "noise": []}
    for fam in sorted(all_instances):
        if not fam.startswith("gen_"):
            continue
        walk = all_instances[fam][-1].walk
        base = idx.relax(walk)
        base_dom = base["dominant_family"]
        interior = list(range(1, len(walk) - 1))
        for mode in ("drop", "corrupt", "noise"):
            series = {"family": fam, "base_dom": base_dom, "points": []}
            for mag in range(0, n_magnitudes + 1):
                if mag == 0:
                    pw = walk
                elif mode == "drop":
                    if mag > len(interior):
                        break
                    pw = drop_steps(walk, rng.sample(interior, mag))
                elif mode == "corrupt":
                    if mag > len(interior):
                        break
                    pw = corrupt_steps(walk, rng.sample(interior, mag), rng)
                else:
                    pw = neutral_noise(walk, mag, rng)
                r = idx.relax(pw)
                series["points"].append({
                    "magnitude": mag,
                    "true_family_survived": r["dominant_family"] == fam,
                    "base_family_survived": base_dom is not None and r["dominant_family"] == base_dom,
                    "dominant": r["dominant_family"],
                    "top_score": r["top_score"],
                    "score_gap": r["score_gap"],
                    "bundle_size": r["bundle_size"],
                    "ambiguous": r["dominant_family"] is None,
                })
            out[mode].append(series)
    return out


def summarize_surface(surface):
    summary = {}
    for mode, series_list in surface.items():
        by_mag = {}
        for s in series_list:
            for pt in s["points"]:
                d = by_mag.setdefault(pt["magnitude"], {"true": [], "base": [], "bundle": [], "gap": []})
                d["true"].append(pt["true_family_survived"])
                d["base"].append(pt["base_family_survived"])
                d["bundle"].append(pt["bundle_size"])
                if pt["score_gap"] is not None:
                    d["gap"].append(pt["score_gap"])
        summary[mode] = {
            str(m): {
                "true_family_survival": round(statistics.fmean(d["true"]), 4) if d["true"] else None,
                "base_family_survival": round(statistics.fmean(d["base"]), 4) if d["base"] else None,
                "mean_bundle_size": round(statistics.fmean(d["bundle"]), 4) if d["bundle"] else None,
                "mean_gap": round(statistics.fmean(d["gap"]), 4) if d["gap"] else None,
            }
            for m, d in sorted(by_mag.items())
        }
    return summary


def heldout_bundle_metrics(idx, all_instances):
    n_indexed = len(idx.entries)
    correct, bundles = [], []
    for fam in sorted(all_instances):
        if not fam.startswith("gen_"):
            continue
        r = idx.relax(all_instances[fam][-1].walk)
        correct.append(r["dominant_family"] == fam)
        bundles.append(r["bundle_size"])
    mean_bundle = statistics.fmean(bundles) if bundles else 0.0
    return {
        "heldout_dominant_accuracy": round(statistics.fmean(correct), 4) if correct else None,
        "mean_bundle_size": round(mean_bundle, 4),
        "bundle_reduction": round(n_indexed / mean_bundle, 4) if mean_bundle else 0.0,
    }


def polysemy_metrics(idx, all_instances, polysemy_meta):
    rows = []
    both_active, disambig, shared_bundle = [], [], []
    for pair_id, (fa, fb, share_k) in enumerate(polysemy_meta):
        walk_a = all_instances[fa][-1].walk
        r_shared = idx.relax(walk_a[:share_k])
        r_plus = idx.relax(walk_a[:min(share_k + 1, len(walk_a))])
        shared_fams = set(r_shared["family_counts"])
        ba = fa in shared_fams and fb in shared_fams
        di = r_plus["dominant_family"] == fa
        both_active.append(ba)
        disambig.append(di)
        shared_bundle.append(r_shared["bundle_size"])
        rows.append({
            "pair_id": pair_id, "family_a": fa, "family_b": fb, "share_k": share_k,
            "both_active_on_shared": ba,
            "dominant_after_plus_one": r_plus["dominant_family"],
            "correct_after_plus_one": di,
            "shared_bundle_size": r_shared["bundle_size"],
        })
    return {
        "both_active_rate": round(statistics.fmean(both_active), 4) if both_active else None,
        "disambiguation_rate": round(statistics.fmean(disambig), 4) if disambig else None,
        "mean_shared_bundle_size": round(statistics.fmean(shared_bundle), 4) if shared_bundle else None,
        "rows": rows,
    }


def main():
    print("building data...")
    _, _, all_instances, polysemy_meta, _ = build_generated_graph_with_polysemy(
        n_disjoint_families=20, n_polysemy_bases=10, instances_per=3, seed=20260706)

    comparison = {}
    print("\nMATCHER ABLATION: canonical identity held fixed")
    print("=" * 78)
    for matcher in MATCHERS:
        print(f"\n--- {matcher} ---")
        idx = build_index(all_instances, matcher)
        surface = map_surface(idx, all_instances, n_magnitudes=4, seed=42)
        summary = summarize_surface(surface)
        heldout = heldout_bundle_metrics(idx, all_instances)
        poly = polysemy_metrics(idx, all_instances, polysemy_meta)
        comparison[matcher] = {
            "surface": surface, "surface_summary": summary,
            "heldout": heldout, "polysemy": poly,
        }
        print("heldout:", heldout)
        print("polysemy:", {k: v for k, v in poly.items() if k != "rows"})
        print(f"{'mag':<5} {'drop':>8} {'corrupt':>8} {'noise':>8}")
        mags = sorted(set(int(m) for mode in summary.values() for m in mode))
        for mag in mags:
            d = summary["drop"].get(str(mag), {}).get("true_family_survival", "—")
            c = summary["corrupt"].get(str(mag), {}).get("true_family_survival", "—")
            n = summary["noise"].get(str(mag), {}).get("true_family_survival", "—")
            print(f"{mag:<5} {str(d):>8} {str(c):>8} {str(n):>8}")

    out = {
        "experiment": "noise-collapse-matcher-ablation",
        "branch": "noise-collapse-matcher-ablation",
        "weights": WEIGHTS,
        "matchers": MATCHERS,
        "comparison": comparison,
    }
    path = os.path.join(OUT_DIR, "matcher_ablation_results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote {os.path.basename(path)}")


if __name__ == "__main__":
    main()
