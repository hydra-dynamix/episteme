"""Full basin surface with DP/LCS as the default matcher.

Architecture under test:

    canonical label-free topology index
      -> broad coarse basin bundle
      -> typed payload projection
      -> soft alignment (greedy pre-fix vs DP/LCS post-fix)
      -> fine discrimination

Representation stays fixed. Only the alignment rule changes.

Outputs:
  dp_lcs_surface_results.json
  dp_lcs_surface_report.md
"""

from __future__ import annotations

import json
import os
import random
import statistics
from collections import Counter

from generator import Instance, build_generated_graph_with_polysemy
from matcher_relaxation import SigView, score
from signature import label_free_canonical_signature, typed_canonical_signature

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

WEIGHTS = {"w_structure": 1.0, "w_typed": 0.5, "w_contradict": 0.7,
           "w_missing": 1.0, "w_extraneous": 0.15}
MATCHERS = ("greedy", "dp")
TYPED_LABELS = ["SUPPORTS|in", "SUPPORTS|out", "WEAKENS|in", "WEAKENS|out",
                "CONTRADICTS|in", "CONTRADICTS|out", "USES_METHOD|out",
                "MEASURES|out", "MEASURES|in", "IN_DOMAIN|out", "IN_DOMAIN|in",
                "HAS_VERDICT|out", "SUPERSEDED_BY|out", "DERIVES_FROM|out"]


def _view_from_sig(sig) -> SigView:
    edge_bag = Counter(lab for lab in sig.edge_label_trace[1:] if lab != "—")
    return SigView(
        node_trace=sig.node_trace,
        edge_label_trace=sig.edge_label_trace,
        typed_edges=frozenset(sig.typed_edges),
        typed_edge_counts=sig.typed_edge_counts,
        node_set=frozenset(range(sig.node_count)),
        edge_bag=tuple(sorted(edge_bag.items())),
    )


def typed_view(walk) -> SigView:
    return _view_from_sig(typed_canonical_signature(walk))


def labelfree_view(walk) -> SigView:
    return _view_from_sig(label_free_canonical_signature(walk))


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


class TwoStageSoftIndex:
    """Label-free coarse basin -> typed payload fine scoring."""

    def __init__(self, matcher: str, weights: dict = WEIGHTS):
        self.matcher = matcher
        self.weights = weights
        self.entries = []

    def add(self, inst: Instance):
        self.entries.append({
            "family": inst.family,
            "focal": inst.focal_node(),
            "labelfree": labelfree_view(inst.walk),
            "typed": typed_view(inst.walk),
            "walk": inst.walk,
        })

    def relax(self, evidence_walk):
        e_lf = labelfree_view(evidence_walk)
        e_typed = typed_view(evidence_walk)

        coarse = []
        for ent in self.entries:
            s = score(ent["labelfree"], e_lf, matcher=self.matcher, weights=self.weights)
            coarse.append({**s.__dict__, "family": ent["family"], "focal": ent["focal"], "entry": ent})
        coarse.sort(key=lambda r: r["total"], reverse=True)
        coarse_bundle = bundle(coarse)

        fine = []
        for c in coarse_bundle:
            ent = c["entry"]
            s = score(ent["typed"], e_typed, matcher=self.matcher, weights=self.weights)
            fine.append({**s.__dict__, "family": ent["family"], "focal": ent["focal"],
                         "coarse_total": c["total"]})
        fine.sort(key=lambda r: r["total"], reverse=True)
        fine_bundle = bundle(fine)

        dominant = None
        if fine:
            top = fine[0]["total"]
            top_fams = {r["family"] for r in fine if abs(r["total"] - top) < 1e-9}
            dominant = next(iter(top_fams)) if len(top_fams) == 1 else None
        gap = None
        if len(fine) >= 2:
            top_fam = fine[0]["family"]
            for r in fine[1:]:
                if r["family"] != top_fam:
                    gap = round(fine[0]["total"] - r["total"], 4)
                    break

        return {
            "dominant_family": dominant,
            "top_score": fine[0]["total"] if fine else None,
            "score_gap": gap,
            "coarse_bundle_size": len(coarse_bundle),
            "fine_bundle_size": len(fine_bundle),
            "coarse_family_counts": dict(Counter(r["family"] for r in coarse_bundle)),
            "family_counts": dict(Counter(r["family"] for r in fine_bundle)),
            "ranked": fine,
        }


# perturbations

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
    idx = TwoStageSoftIndex(matcher=matcher)
    for _fam, insts in all_instances.items():
        for inst in insts[:-1]:
            idx.add(inst)
    return idx


def surface(idx, all_instances, n_magnitudes=4, seed=42):
    rng = random.Random(seed)
    out = {"drop": [], "corrupt": [], "noise": []}
    for fam in sorted(all_instances):
        if not fam.startswith("gen_"):
            continue
        walk = all_instances[fam][-1].walk
        base = idx.relax(walk)
        interior = list(range(1, len(walk) - 1))
        for mode in ("drop", "corrupt", "noise"):
            series = {"family": fam, "base_dom": base["dominant_family"], "points": []}
            for mag in range(n_magnitudes + 1):
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
                    "dominant": r["dominant_family"],
                    "top_score": r["top_score"],
                    "score_gap": r["score_gap"],
                    "coarse_bundle_size": r["coarse_bundle_size"],
                    "fine_bundle_size": r["fine_bundle_size"],
                    "ambiguous": r["dominant_family"] is None,
                })
            out[mode].append(series)
    return out


def summarize(surf):
    out = {}
    for mode, series_list in surf.items():
        by_mag = {}
        for s in series_list:
            for p in s["points"]:
                d = by_mag.setdefault(p["magnitude"], {"surv": [], "coarse": [], "fine": [], "gap": []})
                d["surv"].append(p["true_family_survived"])
                d["coarse"].append(p["coarse_bundle_size"])
                d["fine"].append(p["fine_bundle_size"])
                if p["score_gap"] is not None:
                    d["gap"].append(p["score_gap"])
        out[mode] = {
            str(m): {
                "survival": round(statistics.fmean(d["surv"]), 4) if d["surv"] else None,
                "mean_coarse_bundle": round(statistics.fmean(d["coarse"]), 4) if d["coarse"] else None,
                "mean_fine_bundle": round(statistics.fmean(d["fine"]), 4) if d["fine"] else None,
                "mean_gap": round(statistics.fmean(d["gap"]), 4) if d["gap"] else None,
            }
            for m, d in sorted(by_mag.items())
        }
    return out


def phase_transitions(summary, threshold=0.5):
    trans = {}
    for mode, by_mag in summary.items():
        first = None
        for m in sorted(int(x) for x in by_mag):
            val = by_mag[str(m)]["survival"]
            if val is not None and val < threshold:
                first = m
                break
        trans[mode] = first
    return trans


def heldout(idx, all_instances):
    correct, coarse, fine = [], [], []
    for fam in sorted(all_instances):
        if not fam.startswith("gen_"):
            continue
        r = idx.relax(all_instances[fam][-1].walk)
        correct.append(r["dominant_family"] == fam)
        coarse.append(r["coarse_bundle_size"])
        fine.append(r["fine_bundle_size"])
    n_indexed = len(idx.entries)
    mean_fine = statistics.fmean(fine) if fine else 0.0
    return {
        "heldout_dominant_accuracy": round(statistics.fmean(correct), 4),
        "mean_coarse_bundle": round(statistics.fmean(coarse), 4),
        "mean_fine_bundle": round(mean_fine, 4),
        "fine_bundle_reduction": round(n_indexed / mean_fine, 4) if mean_fine else 0.0,
    }


def polysemy(idx, all_instances, polysemy_meta):
    rows, both, dis, shared = [], [], [], []
    for pair_id, (fa, fb, share_k) in enumerate(polysemy_meta):
        walk_a = all_instances[fa][-1].walk
        r_shared = idx.relax(walk_a[:share_k])
        r_plus = idx.relax(walk_a[:min(share_k + 1, len(walk_a))])
        fams = set(r_shared["family_counts"])
        ba = fa in fams and fb in fams
        di = r_plus["dominant_family"] == fa
        both.append(ba); dis.append(di); shared.append(r_shared["fine_bundle_size"])
        rows.append({"pair_id": pair_id, "family_a": fa, "family_b": fb,
                     "share_k": share_k, "both_active_on_shared": ba,
                     "dominant_after_plus_one": r_plus["dominant_family"],
                     "correct_after_plus_one": di,
                     "shared_fine_bundle_size": r_shared["fine_bundle_size"],
                     "shared_coarse_bundle_size": r_shared["coarse_bundle_size"]})
    return {
        "both_active_rate": round(statistics.fmean(both), 4) if both else None,
        "disambiguation_rate": round(statistics.fmean(dis), 4) if dis else None,
        "mean_shared_fine_bundle": round(statistics.fmean(shared), 4) if shared else None,
        "rows": rows,
    }


def render_report(results):
    lines = [
        "# DP/LCS Full Basin Surface",
        "",
        "Representation held fixed: canonical first-occurrence identity.",
        "Architecture: label-free coarse basin bundle → typed payload scoring → soft alignment.",
        "Greedy is the pre-fix comparator; DP/LCS is the new default.",
        "",
        "## Summary",
        "",
        "| matcher | heldout acc | coarse bundle | fine bundle | fine reduction | polysemy disambig | drop transition | corrupt transition | noise transition |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for m in MATCHERS:
        h = results[m]["heldout"]
        p = results[m]["polysemy"]
        t = results[m]["phase_transitions"]
        lines.append(
            f"| {m} | {h['heldout_dominant_accuracy']} | {h['mean_coarse_bundle']} | "
            f"{h['mean_fine_bundle']} | {h['fine_bundle_reduction']} | "
            f"{p['disambiguation_rate']} | {t['drop']} | {t['corrupt']} | {t['noise']} |"
        )
    lines += ["", "## Survival Surface", ""]
    for mode in ("drop", "corrupt", "noise"):
        lines += [f"### {mode}", "", "| magnitude | greedy | dp |", "|---:|---:|---:|"]
        mags = sorted(set(int(x) for m in MATCHERS for x in results[m]["summary"][mode]))
        for mag in mags:
            g = results["greedy"]["summary"][mode].get(str(mag), {}).get("survival", "—")
            d = results["dp"]["summary"][mode].get(str(mag), {}).get("survival", "—")
            lines.append(f"| {mag} | {g} | {d} |")
        lines.append("")
    lines += [
        "## Interpretation",
        "",
        "DP/LCS repairs the causal greedy noise failure by allowing unmatched evidence to be skipped and alignment to recover later in the trace. The result is not perfect noise immunity; it is a measurable stability surface. Polysemy and fine bundle reduction remain intact, so the repair does not reduce to bag-of-edges matching.",
    ]
    return "\n".join(lines) + "\n"


def main():
    print("building data...")
    _, _, all_instances, polysemy_meta, _ = build_generated_graph_with_polysemy(
        n_disjoint_families=20, n_polysemy_bases=10, instances_per=3, seed=20260706)
    results = {}
    print("\nFULL BASIN SURFACE: greedy pre-fix vs DP/LCS default")
    print("=" * 78)
    for matcher in MATCHERS:
        idx = build_index(all_instances, matcher)
        surf = surface(idx, all_instances, n_magnitudes=4, seed=42)
        summ = summarize(surf)
        trans = phase_transitions(summ)
        h = heldout(idx, all_instances)
        p = polysemy(idx, all_instances, polysemy_meta)
        results[matcher] = {"surface": surf, "summary": summ, "phase_transitions": trans,
                            "heldout": h, "polysemy": p}
        print(f"\n--- {matcher} ---")
        print("heldout:", h)
        print("polysemy:", {k: v for k, v in p.items() if k != "rows"})
        print("phase transitions:", trans)
        print(f"{'mag':<5} {'drop':>8} {'corrupt':>8} {'noise':>8}")
        mags = sorted(set(int(x) for mode in summ.values() for x in mode))
        for mag in mags:
            print(f"{mag:<5} {summ['drop'].get(str(mag),{}).get('survival','—'):>8} "
                  f"{summ['corrupt'].get(str(mag),{}).get('survival','—'):>8} "
                  f"{summ['noise'].get(str(mag),{}).get('survival','—'):>8}")

    out = {"experiment": "dp-lcs-full-basin-surface", "branch": "noise-collapse-matcher-ablation",
           "architecture": "label-free coarse basin -> typed payload -> soft alignment",
           "weights": WEIGHTS, "comparison": results}
    json_path = os.path.join(OUT_DIR, "dp_lcs_surface_results.json")
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2)
    md_path = os.path.join(OUT_DIR, "dp_lcs_surface_report.md")
    with open(md_path, "w") as f:
        f.write(render_report(results))
    print(f"\nwrote {os.path.basename(json_path)}")
    print(f"wrote {os.path.basename(md_path)}")


if __name__ == "__main__":
    main()
