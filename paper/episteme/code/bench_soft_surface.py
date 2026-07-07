"""Map the basin-depth perturbation surface under soft scoring.

Three perturbation modes on held-out instances:
  DROP    : remove one (then more) non-boundary evidence items
  CORRUPT : flip the edge label of one (then more) non-boundary items
  NOISE   : insert one (then more) irrelevant random evidence items

For each mode and magnitude we measure:
  survival          : does the dominant family match the unperturbed dominant?
  score_gap         : top score - runner-up score (basin sharpness)
  bundle_size       : how many candidates within 10% of top

The result of interest is the SURFACE (where the basin transitions), not a
single pass/fail. We do not optimize for 1.0.

Baseline: hard prefix-pruning had drop-stability interior = 0.0.
"""

from __future__ import annotations

import json
import os
import random
import statistics
from collections import Counter

from generator import build_generated_graph_with_polysemy
from soft_relaxation import SoftRelaxationIndex

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# soft-scoring weights (named, not tuned -- map the surface first)
DEFAULT_WEIGHTS = {
    "w_structure": 1.0,   # matched required structure (aligned fraction)
    "w_typed": 0.5,       # typed payload support per aligned edge
    "w_contradict": 0.7,  # penalty for same-pair-different-label
    "w_missing": 1.0,     # penalty per unaligned evidence step
}


# ---------------------------------------------------------------------------
# perturbations
# ---------------------------------------------------------------------------

def drop_steps(walk, indices):
    """Remove steps at given indices (keep root at 0)."""
    keep = [i for i in range(len(walk)) if i not in indices and not (i == 0)]
    keep = [0] + [i for i in range(1, len(walk)) if i not in indices]
    return [walk[i] for i in keep]


def corrupt_steps(walk, indices, rng):
    """Flip edge labels at given indices to a random different typed edge."""
    typed_labels = ["SUPPORTS|in", "SUPPORTS|out", "WEAKENS|in", "WEAKENS|out",
                    "CONTRADICTS|in", "CONTRADICTS|out", "USES_METHOD|out",
                    "MEASURES|out", "MEASURES|in", "IN_DOMAIN|out", "IN_DOMAIN|in",
                    "HAS_VERDICT|out", "SUPERSEDED_BY|out", "DERIVES_FROM|out"]
    out = list(walk)
    for i in indices:
        if i == 0:
            continue
        node, _et, _dir = out[i]
        new = rng.choice(typed_labels)
        et, direction = new.split("|")
        out[i] = (node, et, direction)
    return out


def add_noise(walk, n, rng, all_walks):
    """Insert n irrelevant evidence steps from other walks at random non-root positions."""
    out = list(walk)
    for _ in range(n):
        # pick a random step from a random other walk
        donor = rng.choice(all_walks)
        step = rng.choice(donor[1:])  # skip roots
        pos = rng.randint(1, len(out))
        out.insert(pos, step)
    return out


# ---------------------------------------------------------------------------
# surface map
# ---------------------------------------------------------------------------

def map_surface(idx, instances_by_family, n_magnitudes=4, seed=42):
    """For each disjoint family, map drop/corrupt/noise survival across magnitudes."""
    rng = random.Random(seed)
    all_walks = [inst.walk for insts in instances_by_family.values() for inst in insts]
    results = {"drop": [], "corrupt": [], "noise": []}

    for fam in sorted(instances_by_family):
        if not fam.startswith("gen_"):
            continue
        walk = instances_by_family[fam][-1].walk
        unperturbed = idx.relax(walk)
        base_dom = unperturbed["dominant_family"]
        if base_dom is None:
            continue  # skip if the unperturbed query is already ambiguous

        interior_indices = list(range(1, len(walk) - 1))  # non-boundary

        for mode in ("drop", "corrupt", "noise"):
            series = {"family": fam, "mode": mode, "base_dom": base_dom, "points": []}
            for mag in range(0, n_magnitudes + 1):
                if mag == 0:
                    perturbed_walk = walk
                else:
                    if mode == "drop":
                        if mag > len(interior_indices):
                            break
                        idxs = rng.sample(interior_indices, mag)
                        perturbed_walk = drop_steps(walk, idxs)
                    elif mode == "corrupt":
                        if mag > len(interior_indices):
                            break
                        idxs = rng.sample(interior_indices, mag)
                        perturbed_walk = corrupt_steps(walk, idxs, rng)
                    else:  # noise
                        perturbed_walk = add_noise(walk, mag, rng, all_walks)
                r = idx.relax(perturbed_walk)
                survived = r["dominant_family"] == base_dom
                series["points"].append({
                    "magnitude": mag,
                    "survived": survived,
                    "dominant": r["dominant_family"],
                    "top_score": r["top_score"],
                    "score_gap": r["score_gap"],
                    "bundle_size": len(r["family_counts"]),
                    "ambiguous": r["dominant_family"] is None,
                })
            results[mode].append(series)
    return results


def summarize_surface(surface) -> dict:
    """Aggregate survival rate per mode per magnitude."""
    summary = {}
    for mode, series_list in surface.items():
        by_mag = {}
        for series in series_list:
            for pt in series["points"]:
                by_mag.setdefault(pt["magnitude"], []).append(pt["survived"])
        summary[mode] = {
            str(mag): round(statistics.fmean(surv), 4) if surv else None
            for mag, surv in sorted(by_mag.items())
        }
    return summary


def find_phase_transition(surface) -> dict:
    """For each mode, the first magnitude where mean survival drops below 0.5."""
    transitions = {}
    for mode, series_list in surface.items():
        by_mag = {}
        for series in series_list:
            for pt in series["points"]:
                by_mag.setdefault(pt["magnitude"], []).append(pt["survived"])
        transition = None
        for mag in sorted(by_mag):
            rate = statistics.fmean(by_mag[mag]) if by_mag[mag] else 1.0
            if rate < 0.5:
                transition = mag
                break
        transitions[mode] = transition
    return transitions


def main():
    print("building data...")
    g, skeletons, all_instances, polysemy_meta, _ = build_generated_graph_with_polysemy(
        n_disjoint_families=20, n_polysemy_bases=10, instances_per=3, seed=20260706)

    idx = SoftRelaxationIndex(weights=DEFAULT_WEIGHTS, variant="typed")
    for fam, insts in all_instances.items():
        for inst in insts[:-1]:
            idx.add(inst)

    print(f"indexed: {len(idx.entries)} instances\n")
    print("mapping perturbation surface (drop/corrupt/noise, magnitudes 0..4)...\n")

    surface = map_surface(idx, all_instances, n_magnitudes=4, seed=42)
    summary = summarize_surface(surface)
    transitions = find_phase_transition(surface)

    # ---- print ----
    print("=" * 64)
    print("SOFT-SCORING PERTURBATION SURFACE (survival rate by magnitude)")
    print("=" * 64)
    print(f"{'magnitude':<10} {'drop':>8} {'corrupt':>8} {'noise':>8}")
    all_mags = sorted(set(int(m) for mode in summary.values() for m in mode))
    for mag in all_mags:
        d = summary["drop"].get(str(mag), "—")
        c = summary["corrupt"].get(str(mag), "—")
        n = summary["noise"].get(str(mag), "—")
        print(f"{mag:<10} {str(d):>8} {str(c):>8} {str(n):>8}")
    print()
    print("phase transition (first magnitude < 0.5 survival):")
    for mode, t in transitions.items():
        print(f"  {mode}: {t if t is not None else 'none (survives all tested)'}")
    print()
    print("baseline: hard prefix-pruning drop-stability interior = 0.0")

    # ---- write artifacts ----
    out = {
        "experiment": "basin-depth-perturbation-surface",
        "branch": "basin-depth-and-soft-relaxation",
        "weights": DEFAULT_WEIGHTS,
        "summary": summary,
        "phase_transitions": transitions,
        "baseline_hard_pruning": {"drop_stability_interior": 0.0},
        "surface": surface,
    }
    with open(os.path.join(OUT_DIR, "soft_surface_results.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote soft_surface_results.json")


if __name__ == "__main__":
    main()
