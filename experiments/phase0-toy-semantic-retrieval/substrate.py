"""Relational transition memory substrate: variants, retrieval, metrics.

Variants (per docs/relational-transition-memory-substrate.md phase 1):
  A  unordered  : evidence treated as a set; candidate survives iff evidence-set
                  is a subset of the candidate's attribute set.
  B  ordered    : evidence treated as a sequence; candidate survives iff the
                  evidence sequence is a subsequence of the candidate's trace.
  C  typed      : evidence treated as typed (type,value) edges; candidate
                  survives iff the typed evidence sequence is a subsequence of
                  the candidate's typed trace.
  D  shuffled   : same evidence as ordered, but order randomized per seed;
                  retrieval uses the ordered matcher on the permuted sequence.

Retrieval is incremental: after each evidence step we record the active
candidate set, then derive the phase-2 metrics over the resulting trajectory.
"""

from . import dataset as D


# ---------------------------------------------------------------------------
# matchers
# ---------------------------------------------------------------------------

def _is_subsequence(seq, sup):
    it = iter(sup)
    return all(tok in it for tok in seq)


def match_unordered(world, candidate, evidence_prefix):
    return set(evidence_prefix) <= world[candidate]["attrs"]


def match_ordered(world, candidate, evidence_prefix):
    return _is_subsequence(evidence_prefix, world[candidate]["trace"])


def match_typed(world, candidate, typed_evidence_prefix):
    return _is_subsequence(typed_evidence_prefix, world[candidate]["typed"])


# ---------------------------------------------------------------------------
# incremental retrieval
# ---------------------------------------------------------------------------

def retrieve_trajectory(world, target, matcher, evidence):
    """Run incremental retrieval for one target's evidence under one matcher.

    Returns a list of candidate sets, one per evidence step (length == len(evidence)).
    Each candidate set is a sorted list of target names.
    """
    traj = []
    for k in range(1, len(evidence) + 1):
        prefix = evidence[:k]
        cands = [t for t in D.TARGETS if matcher(world, t, prefix)]
        traj.append(sorted(cands))
    return traj


def shuffled_evidence(world, target, seed):
    """Permute a target's value-trace evidence using a fixed seed (deterministic)."""
    import random
    rng = random.Random(f"{seed}:{target}")  # seed includes target -> per-target stream
    seq = list(D.evidence_for(world, target))
    rng.shuffle(seq)
    return seq


# ---------------------------------------------------------------------------
# ranking (for top_k_recall / rank_of_target)
# ---------------------------------------------------------------------------

def rank_score(world, target, candidate):
    """Overlap of candidate's attributes with the query target's attributes.

    The true target scores 1.0; supersets (e.g. wolf over dog) also score 1.0
    and are broken by name. Used only to order candidates within a candidate set.
    """
    q = world[target]["attrs"]
    c = world[candidate]["attrs"]
    return len(q & c) / len(q)


def rank_of(world, target, candidate_set):
    """1-indexed rank of `target` within `candidate_set` (lower is better)."""
    ordered = sorted(candidate_set, key=lambda c: (-rank_score(world, target, c), c))
    try:
        return ordered.index(target) + 1
    except ValueError:
        return None  # target not in candidate set


# ---------------------------------------------------------------------------
# metrics over a set of per-target trajectories
# ---------------------------------------------------------------------------

def compute_metrics(world, variant, trajectories):
    """Aggregate phase-2 metrics across all per-target trajectories.

    trajectories: dict target -> list[set] (candidate set per evidence step).
    """
    n_targets = len(trajectories)
    n_world = len(world)

    # per-step aggregates
    total_steps = 0
    survival_hits = 0
    elim_events = 0          # steps where target wrongly absent
    monotonic_ok = 0
    monotonic_total = 0
    final_sizes = []
    first_sizes = []
    reductions = []          # first_size / final_size per query

    # final-step ranking
    top1 = 0
    top3 = 0

    for t, traj in trajectories.items():
        if not traj:
            continue
        for k, cand_set in enumerate(traj):
            total_steps += 1
            if t in cand_set:
                survival_hits += 1
            else:
                elim_events += 1
            if k > 0:
                prev = set(traj[k - 1])
                cur = set(cand_set)
                monotonic_total += 1
                if cur <= prev:        # narrowing: no new members appeared
                    monotonic_ok += 1
        first = set(traj[0]) if traj else set()
        final = set(traj[-1]) if traj else set()
        first_sizes.append(len(first))
        final_sizes.append(len(final))
        if len(final) > 0:
            reductions.append(len(first) / len(final))

        # ranking at final step
        final_rank = rank_of(world, t, traj[-1])
        if final_rank is not None and final_rank <= 1:
            top1 += 1
        if final_rank is not None and final_rank <= 3:
            top3 += 1

    def gmean(xs):
        if not xs:
            return 0.0
        p = 1.0
        for x in xs:
            p *= x
        return p ** (1.0 / len(xs))

    mean_final = sum(final_sizes) / len(final_sizes) if final_sizes else 0.0
    empty_final_rate = (sum(1 for s in final_sizes if s == 0) / len(final_sizes)) if final_sizes else 0.0
    return {
        "variant": variant,
        "n_targets": n_targets,
        "n_world": n_world,
        "final_empty_rate": round(empty_final_rate, 4),
        "top_1_recall": round(top1 / n_targets, 4),
        "top_3_recall": round(top3 / n_targets, 4),
        "mean_candidate_set_size_final": round(mean_final, 4),
        "candidate_set_reduction": round(gmean(reductions), 4) if reductions else 0.0,
        "world_reduction": round(n_world / mean_final, 4) if mean_final else 0.0,
        "false_elimination_rate": round(elim_events / total_steps, 4) if total_steps else 0.0,
        "target_survival_rate": round(survival_hits / total_steps, 4) if total_steps else 0.0,
        "monotonic_narrowing_rate": round(monotonic_ok / monotonic_total, 4) if monotonic_total else 0.0,
    }
