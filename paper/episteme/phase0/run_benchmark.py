"""Phase 0 toy semantic retrieval benchmark entrypoint.

Runs the four variants (unordered, ordered, typed, shuffled) over Dataset A,
emits results.json, retrieval_steps.json, comparison.md, and run_summary.json.

Usage:
    python3 -m experiments.phase0-toy-semantic-retrieval.run_benchmark
"""

from __future__ import annotations

import json
import os
import statistics

from . import dataset as D
from . import substrate as S

# number of independent shuffled seeds to average for a stable control
N_SHUFFLE_SEEDS = 5

# phase-0 acceptance thresholds (docs/...recommended first experiment + phase 2)
THRESHOLDS = {
    "top_3_recall_min": 0.95,
    "candidate_set_reduction_min": 3.0,
    "false_elimination_rate_max": 0.05,
    "monotonic_narrowing_rate_min": 0.75,
    # phase-3 order-importance: ordered/typed must beat shuffled on reduction by
    # >=15% with no meaningful recall loss (<=3%).
    "order_reduction_improvement_min": 0.15,
    "order_recall_loss_max": 0.03,
}

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_structured_variant(world, variant, matcher, evidence_fn):
    """Run a structured (deterministic) variant; return trajectories + steps."""
    trajectories = {}
    steps = {}
    for t in D.TARGETS:
        ev = evidence_fn(world, t)
        traj = S.retrieve_trajectory(world, t, matcher, ev)
        trajectories[t] = traj
        steps[t] = [
            {"step": k + 1, "evidence": ev[: k + 1], "candidates": traj[k], "size": len(traj[k])}
            for k in range(len(traj))
        ]
    return trajectories, steps


def run_shuffled_variant(world):
    """Average the shuffled control over N_SHUFFLE_SEEDS independent seeds.

    Returns aggregated metrics, a representative step trace (seed 0), and the
    per-seed top-line metrics so the variance is visible.
    """
    per_seed_top = []
    rep_traj = None
    rep_steps = None
    # accumulate step-level survival/monotonic across seeds for the aggregate
    all_trajectories_for_metrics = {}
    # We compute metrics per seed then average, which correctly weights each seed.
    seed_metrics = []
    for seed in range(N_SHUFFLE_SEEDS):
        trajectories = {}
        steps = {}
        for t in D.TARGETS:
            ev = S.shuffled_evidence(world, t, seed)
            traj = S.retrieve_trajectory(world, t, S.match_ordered, ev)
            trajectories[t] = traj
            steps[t] = [
                {"step": k + 1, "evidence": ev[: k + 1], "candidates": traj[k], "size": len(traj[k])}
                for k in range(len(traj))
            ]
        m = S.compute_metrics(world, "shuffled", trajectories)
        seed_metrics.append(m)
        per_seed_top.append({"seed": seed, "top_3_recall": m["top_3_recall"],
                             "candidate_set_reduction": m["candidate_set_reduction"],
                             "false_elimination_rate": m["false_elimination_rate"],
                             "monotonic_narrowing_rate": m["monotonic_narrowing_rate"]})
        if seed == 0:
            rep_traj = trajectories
            rep_steps = steps
            all_trajectories_for_metrics = trajectories

    keys = ["top_1_recall", "top_3_recall", "mean_candidate_set_size_final",
            "candidate_set_reduction", "world_reduction", "false_elimination_rate",
            "target_survival_rate", "monotonic_narrowing_rate", "final_empty_rate"]
    avg = {k: round(statistics.fmean([m[k] for m in seed_metrics]), 4) for k in keys}
    avg.update({"variant": "shuffled", "n_targets": len(D.TARGETS), "n_world": len(world)})
    return avg, rep_traj, rep_steps, per_seed_top


def main():
    world = D.build_world()

    u_traj, u_steps = run_structured_variant(world, "unordered", S.match_unordered, D.evidence_for)
    o_traj, o_steps = run_structured_variant(world, "ordered", S.match_ordered, D.evidence_for)
    t_traj, t_steps = run_structured_variant(world, "typed", S.match_typed, D.typed_evidence_for)
    sh_metrics, sh_traj, sh_steps, sh_per_seed = run_shuffled_variant(world)

    metrics = {
        "unordered": S.compute_metrics(world, "unordered", u_traj),
        "ordered": S.compute_metrics(world, "ordered", o_traj),
        "typed": S.compute_metrics(world, "typed", t_traj),
        "shuffled": sh_metrics,
    }

    # ---- gate evaluation -------------------------------------------------
    gate = evaluate_gate(metrics)
    interpretation = build_interpretation(metrics, gate, sh_per_seed)

    # ---- results.json ----------------------------------------------------
    results = {
        "experiment": "phase0-toy-semantic-retrieval",
        "spine": {
            "program": "relational-transition-memory-substrate",
            "branch": "main",
            "question": "does-toy-evidence-narrowing-work",
            "option": "compare-substrate-variants-on-toy-world",
            "mode": "falsification",
        },
        "dataset": {
            "targets": D.TARGETS,
            "n_targets": len(D.TARGETS),
            "traces": D.TRACES,
            "attr_type": D.ATTR_TYPE,
        },
        "thresholds": THRESHOLDS,
        "metrics_by_variant": metrics,
        "shuffled_per_seed": sh_per_seed,
        "gate": gate,
        "interpretation": interpretation,
    }
    write_json("results.json", results)

    # ---- retrieval_steps.json -------------------------------------------
    retrieval_steps = {
        "experiment": "phase0-toy-semantic-retrieval",
        "note": ("shuffled step trace shown for seed 0; metrics for shuffled are "
                 f"averaged over {N_SHUFFLE_SEEDS} seeds (see shuffled_per_seed)."),
        "variants": {
            "unordered": u_steps,
            "ordered": o_steps,
            "typed": t_steps,
            "shuffled_seed0": sh_steps,
        },
    }
    write_json("retrieval_steps.json", retrieval_steps)

    # ---- comparison.md ---------------------------------------------------
    md = render_comparison(metrics, gate, sh_per_seed, interpretation)
    with open(os.path.join(OUT_DIR, "comparison.md"), "w") as f:
        f.write(md)

    # ---- run_summary.json ------------------------------------------------
    run_summary = {
        "hypothesis": (
            "Incremental evidence accumulation narrows the candidate set "
            "(>=3x reduction) while preserving the correct target "
            "(top_3_recall >= 0.95, false_elimination_rate <= 0.05), and an "
            "ordered/typed variant beats the shuffled-order control."
        ),
        "changed": [
            "experiments/phase0-toy-semantic-retrieval/dataset.py",
            "experiments/phase0-toy-semantic-retrieval/substrate.py",
            "experiments/phase0-toy-semantic-retrieval/run_benchmark.py",
        ],
        "commands": [
            "python3 -m experiments.phase0-toy-semantic-retrieval.run_benchmark",
        ],
        "metrics": compact_metrics(metrics),
        "pass_criteria": gate,
        "outcome": gate["overall"],
        "claim_delta": interpretation["claim_delta"],
        "artifacts": [
            "experiments/phase0-toy-semantic-retrieval/results.json",
            "experiments/phase0-toy-semantic-retrieval/retrieval_steps.json",
            "experiments/phase0-toy-semantic-retrieval/comparison.md",
        ],
        "next_work": interpretation["next_work"],
    }
    write_json("run_summary.json", run_summary)

    print("phase0 toy semantic retrieval benchmark complete")
    print(json.dumps(compact_metrics(metrics), indent=2))
    print("gate:", json.dumps(gate, indent=2))


# ---------------------------------------------------------------------------
# gate + interpretation
# ---------------------------------------------------------------------------

def evaluate_gate(metrics):
    u, o, t, s = metrics["unordered"], metrics["ordered"], metrics["typed"], metrics["shuffled"]

    def beats_shuffled(v):
        if s["candidate_set_reduction"] <= 0:
            red_improve = float("inf")
        else:
            red_improve = (v["candidate_set_reduction"] - s["candidate_set_reduction"]) / s["candidate_set_reduction"]
        recall_loss = v["top_3_recall"] - s["top_3_recall"]  # positive == better
        return (red_improve >= THRESHOLDS["order_reduction_improvement_min"]
                and recall_loss >= -THRESHOLDS["order_recall_loss_max"]), red_improve, recall_loss

    # Order importance (phase-3 preview): does ordered beat unordered on content?
    def beats(v, baseline):
        if baseline["candidate_set_reduction"] <= 0:
            return 0.0, v["top_3_recall"] - baseline["top_3_recall"]
        red = (v["candidate_set_reduction"] - baseline["candidate_set_reduction"]) / baseline["candidate_set_reduction"]
        return red, v["top_3_recall"] - baseline["top_3_recall"]

    o_vs_u_red, o_vs_u_recall = beats(o, u)
    t_vs_o_red, t_vs_o_recall = beats(t, o)

    o_beats, o_red, o_recall = beats_shuffled(o)
    t_beats, t_red, t_recall = beats_shuffled(t)

    # The shuffled control is degenerate when its final candidate set is usually
    # empty: a random permutation almost never is a subsequence of a strict
    # canonical trace, so the matcher empties out and the target is eliminated.
    # In that regime 'ordered beats shuffled' is technically true but reflects
    # matcher brittleness, not that canonical order carries retrieval value.
    shuffled_degenerate = s["final_empty_rate"] >= 0.5

    checks = {
        "top_3_recall_ordered_ge_0.95": o["top_3_recall"] >= THRESHOLDS["top_3_recall_min"],
        "candidate_set_reduction_ordered_ge_3x": o["candidate_set_reduction"] >= THRESHOLDS["candidate_set_reduction_min"],
        "false_elimination_rate_ordered_le_0.05": o["false_elimination_rate"] <= THRESHOLDS["false_elimination_rate_max"],
        "monotonic_narrowing_rate_ordered_ge_0.75": o["monotonic_narrowing_rate"] >= THRESHOLDS["monotonic_narrowing_rate_min"],
        "ordered_beats_shuffled": o_beats,
        "typed_beats_shuffled": t_beats,
        "ordered_or_typed_beats_shuffled": o_beats or t_beats,
    }
    phase0_pass = all([
        checks["top_3_recall_ordered_ge_0.95"],
        checks["candidate_set_reduction_ordered_ge_3x"],
        checks["false_elimination_rate_ordered_le_0.05"],
        checks["monotonic_narrowing_rate_ordered_ge_0.75"],
        checks["ordered_or_typed_beats_shuffled"],
    ])
    overall = "supported" if phase0_pass else "falsified"
    return {
        "overall": overall,
        "checks": checks,
        "order_importance": {
            "note": ("phase-3 preview: does ordered beat unordered? In this toy "
                     "ordered == unordered because the toy world has a globally "
                     "consistent general->specific ordering with no order conflicts."),
            "ordered_vs_unordered_reduction_improvement_pct": round(o_vs_u_red * 100, 2),
            "ordered_vs_unordered_recall_delta": round(o_vs_u_recall, 4),
            "order_matters": o_vs_u_red >= THRESHOLDS["order_reduction_improvement_min"],
        },
        "type_importance": {
            "note": ("phase-4 preview: does typed beat ordered? In this toy every "
                     "attribute value maps to exactly one relation type, so typed "
                     "== ordered."),
            "typed_vs_ordered_reduction_improvement_pct": round(t_vs_o_red * 100, 2),
            "typed_vs_ordered_recall_delta": round(t_vs_o_recall, 4),
            "type_matters": t_vs_o_red >= 0.20,
        },
        "shuffled_control": {
            "final_empty_rate": s["final_empty_rate"],
            "degenerate": shuffled_degenerate,
            "warning": ("Shuffled control collapses to empty candidate sets; "
                        "'ordered beats shuffled' is technically true but reflects "
                        "subsequence-matcher brittleness to permutation, NOT that "
                        "canonical order carries retrieval value." if shuffled_degenerate else None),
        },
        "structured_vs_shuffled": {
            "ordered": {"reduction_improvement_pct": (None if o_red == float("inf") else round(o_red * 100, 2)),
                        "recall_delta": round(o_recall, 4), "beats_shuffled": o_beats},
            "typed": {"reduction_improvement_pct": (None if t_red == float("inf") else round(t_red * 100, 2)),
                      "recall_delta": round(t_recall, 4), "beats_shuffled": t_beats},
        },
    }


def build_interpretation(metrics, gate, sh_per_seed):
    o, t, s = metrics["ordered"], metrics["typed"], metrics["shuffled"]
    claim_delta = (
        "Phase-0 gate {status} on the controlled toy semantic world: incremental "
        "evidence accumulation narrows the candidate set {red:.2f}x for ordered "
        "(top_3_recall={recall:.2f}, false_elimination={fe:.3f}, monotonic={mon:.2f}), "
        "so the primary falsification condition (narrowing fails OR target "
        "eliminated too often) is NOT triggered. HOWEVER two honest caveats "
        "bound this result tightly: (1) order and type are INERT in this toy -- "
        "ordered == unordered == typed for every target ({order_pct:.1f}% reduction "
        "gain of ordered over unordered, {type_pct:.1f}% of typed over ordered) "
        "because the toy world has a globally consistent general->specific "
        "attribute ordering with no order conflicts and every value carries one "
        "relation type; (2) the shuffled control is degenerate "
        "(final_empty_rate={fe_rate:.2f}) -- a random permutation is almost never "
        "a subsequence of a strict canonical trace, so the matcher empties out and "
        "the target is eliminated, making 'ordered beats shuffled' technically "
        "true but a brittleness artifact, not evidence that canonical order "
        "carries retrieval value. NET: this validates the narrowing+survival "
        "mechanic on a controlled toy but does NOT validate transition structure; "
        "whether order/typing matters is inconclusive here and requires a "
        "conflict-rich dataset or adversarial arrival-order evidence."
    ).format(
        status=gate["overall"].upper(),
        red=o["candidate_set_reduction"], recall=o["top_3_recall"],
        fe=o["false_elimination_rate"], mon=o["monotonic_narrowing_rate"],
        order_pct=gate["order_importance"]["ordered_vs_unordered_reduction_improvement_pct"],
        type_pct=gate["type_importance"]["typed_vs_ordered_reduction_improvement_pct"],
        fe_rate=gate["shuffled_control"]["final_empty_rate"],
    )
    # Next work targets the real open question: does transition order carry
    # value over set membership? This toy cannot answer it (ordered==unordered).
    next_work = {
        "slug": "order-importance-with-conflict-dataset",
        "title": "Phase 3 order-importance test on a conflict-rich dataset",
        "description": (
            "Phase 0 confirmed narrowing+survival but showed order and type are "
            "inert on Dataset A (ordered==unordered==typed) because attributes "
            "have a globally consistent ordering. Build a dataset (or adversarial "
            "arrival-order evidence) where shared attributes appear in DIFFERENT "
            "relative order across targets, plus at least one value reused under "
            "different relation types, then rerun ordered vs unordered vs typed vs "
            "a non-degenerate shuffled control. Pass = ordered beats unordered by "
            ">=15% reduction with <=3% recall loss AND typed beats ordered by "
            ">=20%. If ordered still does not beat unordered, the substrate "
            "should be graph-neighborhood based, not trajectory based (docs phase 3)."
        ),
    }
    return {
        "claim_delta": claim_delta,
        "order_matters": gate["order_importance"]["order_matters"],
        "type_matters": gate["type_importance"]["type_matters"],
        "shuffled_degenerate": gate["shuffled_control"]["degenerate"],
        "shuffled_per_seed": sh_per_seed,
        "next_work": next_work,
    }


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

def compact_metrics(metrics):
    m = metrics
    s = m["shuffled"]
    o = m["ordered"]
    t = m["typed"]
    u = m["unordered"]
    return {
        "unordered": _pick(u),
        "ordered": _pick(o),
        "typed": _pick(t),
        "shuffled": _pick(s),
        "shuffled_control_comparison": {
            "ordered_vs_shuffled_reduction_improvement_pct": (
                None if s["candidate_set_reduction"] == 0 else
                round((o["candidate_set_reduction"] - s["candidate_set_reduction"])
                      / s["candidate_set_reduction"] * 100, 2)),
            "ordered_recall_delta_vs_shuffled": round(o["top_3_recall"] - s["top_3_recall"], 4),
            "shuffled_final_empty_rate": s["final_empty_rate"],
            "shuffled_degenerate": s["final_empty_rate"] >= 0.5,
        },
        "order_importance_ordered_vs_unordered": {
            "reduction_improvement_pct": (
                None if u["candidate_set_reduction"] == 0 else
                round((o["candidate_set_reduction"] - u["candidate_set_reduction"])
                      / u["candidate_set_reduction"] * 100, 2)),
            "recall_delta": round(o["top_3_recall"] - u["top_3_recall"], 4),
            "order_identical_to_unordered": _pick(u) == _pick(o),
        },
        "type_importance_typed_vs_ordered": {
            "reduction_improvement_pct": (
                None if o["candidate_set_reduction"] == 0 else
                round((t["candidate_set_reduction"] - o["candidate_set_reduction"])
                      / o["candidate_set_reduction"] * 100, 2)),
            "recall_delta": round(t["top_3_recall"] - o["top_3_recall"], 4),
            "type_identical_to_ordered": _pick(t) == _pick(o),
        },
    }


def _pick(m):
    return {
        "top_3_recall": m["top_3_recall"],
        "top_1_recall": m["top_1_recall"],
        "candidate_set_reduction": m["candidate_set_reduction"],
        "false_elimination_rate": m["false_elimination_rate"],
        "monotonic_narrowing_rate": m["monotonic_narrowing_rate"],
        "mean_candidate_set_size_final": m["mean_candidate_set_size_final"],
        "target_survival_rate": m["target_survival_rate"],
        "final_empty_rate": m["final_empty_rate"],
    }


def fmt_red(pct):
    return "n/a (shuffled degenerate)" if pct is None else f"{pct}%"


def render_comparison(metrics, gate, sh_per_seed, interpretation):
    o = metrics["ordered"]
    rows = []
    header = ["variant", "top_1_recall", "top_3_recall", "candidate_set_reduction",
              "false_elim_rate", "monotonic_narrow", "final_set_size", "survival_rate"]
    rows.append("| " + " | ".join(header) + " |")
    rows.append("|" + "|".join(["---"] * len(header)) + "|")
    for v in ["unordered", "ordered", "typed", "shuffled"]:
        m = metrics[v]
        rows.append("| " + " | ".join([
            v,
            f"{m['top_1_recall']:.3f}",
            f"{m['top_3_recall']:.3f}",
            f"{m['candidate_set_reduction']:.2f}x",
            f"{m['false_elimination_rate']:.3f}",
            f"{m['monotonic_narrowing_rate']:.3f}",
            f"{m['mean_candidate_set_size_final']:.2f}",
            f"{m['target_survival_rate']:.3f}",
        ]) + " |")

    checks_md = "\n".join(f"- {'PASS' if ok else 'FAIL'} `{k}`" for k, ok in gate["checks"].items())
    sv = gate["structured_vs_shuffled"]
    oi = gate["order_importance"]
    ti = gate["type_importance"]
    sc = gate["shuffled_control"]
    md = f"""# Phase 0 toy semantic retrieval benchmark

Spine: program `relational-transition-memory-substrate` / branch `main` /
question `does-toy-evidence-narrowing-work` / option `compare-substrate-variants-on-toy-world` /
experiment `phase0-toy-semantic-retrieval` (mode=falsification).

## Hypothesis

Incremental evidence accumulation narrows the candidate set (>=3x reduction)
while preserving the correct target (top_3_recall >= 0.95,
false_elimination_rate <= 0.05), and an ordered/typed variant beats the
shuffled-order control.

## Setup

Dataset A toy semantic world, {len(D.TARGETS)} targets (cat, dog, panther,
bear, wolf, crow, eagle) with overlapping attributes. For each held-out target
the evidence is its own canonical trace, fed token by token. Four variants:
unordered (set), ordered (value subsequence), typed (typed-edge subsequence),
shuffled (ordered matcher on a permuted sequence, averaged over
{N_SHUFFLE_SEEDS} seeds). Evidence = target's own attributes = best-case
arrival order; this is the case a transition-trace substrate must handle and
the case the shuffled control is designed to break.

## Metrics by variant

{chr(10).join(rows)}

## Phase-0 gate

Overall: **{gate['overall']}**

{checks_md}

Structured vs shuffled (reduction improvement / recall delta):
- ordered: {fmt_red(sv['ordered']['reduction_improvement_pct'])} reduction gain, recall delta {sv['ordered']['recall_delta']:+.3f} -> beats shuffled: {sv['ordered']['beats_shuffled']}
- typed:   {fmt_red(sv['typed']['reduction_improvement_pct'])} reduction gain, recall delta {sv['typed']['recall_delta']:+.3f} -> beats shuffled: {sv['typed']['beats_shuffled']}

## Honest caveats (read before interpreting the pass)

**Order and type are inert on this toy.** Ordered == unordered == typed for
every target:
- ordered vs unordered: {oi['ordered_vs_unordered_reduction_improvement_pct']}% reduction gain, recall delta {oi['ordered_vs_unordered_recall_delta']:+.3f} -> order_matters={oi['order_matters']}
- typed vs ordered: {ti['typed_vs_ordered_reduction_improvement_pct']}% reduction gain, recall delta {ti['typed_vs_ordered_recall_delta']:+.3f} -> type_matters={ti['type_matters']}

Reason: the toy world has a globally consistent general->specific attribute
ordering, so two shared attributes always appear in the same relative order
across targets -- there are no order conflicts for sequence matching to
exploit. And every attribute value maps to exactly one relation type, so
typed-edge matching coincides with ordered value matching.

**The shuffled control is degenerate** (final_empty_rate={sc['final_empty_rate']},
degenerate={sc['degenerate']}): a random permutation is almost never a
subsequence of a strict canonical trace, so the matcher empties the candidate
set and eliminates the target. "Ordered beats shuffled" is therefore
*technically* true but reflects subsequence-matcher brittleness to permutation,
not that canonical order carries retrieval value.

**Net.** The phase-0 gate passes on its literal criteria (narrowing + survival
+ beats-shuffled), so the primary falsification condition is NOT triggered.
But this validates only the narrowing+survival mechanic on a controlled toy; it
does NOT validate that transition order or typing helps retrieval. Whether
order matters is inconclusive on this toy and is the queued next experiment.

## Shuffled control per-seed top line

| seed | top_3_recall | reduction | false_elim | monotonic |
|------|--------------|-----------|------------|-----------|
"""
    for r in sh_per_seed:
        md += f"| {r['seed']} | {r['top_3_recall']:.3f} | {r['candidate_set_reduction']:.2f}x | {r['false_elimination_rate']:.3f} | {r['monotonic_narrowing_rate']:.3f} |\n"

    md += f"""
## Interpretation

{interpretation['claim_delta']}

## Limitations

- Evidence is the target's own canonical attributes (best-case arrival order).
  Real-world evidence is noisier and partial in a different way; that is a
  phase-6 (real Learning Records) concern, deliberately out of scope here.
- Ordered == unordered == typed in this toy (see Honest caveats). Order/type
  importance cannot be evaluated on Dataset A; queued as a phase-3 test on a
  conflict-rich dataset.
- Shuffled control collapses to empty candidate sets (degenerate); a
  non-degenerate order test requires evidence arrival orders that are wrong but
  still content-consistent, or a conflict-rich dataset.
- Ordered/typed metrics use canonical-order evidence and are therefore an upper
  bound on arrival-order robustness; phase 3 should add adversarial/deceptive
  evidence ordering.
"""
    return md


def write_json(name, obj):
    with open(os.path.join(OUT_DIR, name), "w") as f:
        json.dump(obj, f, indent=2)


if __name__ == "__main__":
    main()
