# Dumb Learned Candidate Ranker

## Purpose

Test the minimum meaningful ML investment after topology retrieval:

```text
topology index generates candidate continuations
simple learned model reranks / abstains over those candidates
```

The model does not replace the topology index. It only discriminates among candidates already produced by the index.

## Model

A deliberately small online pairwise linear ranker:

- no external ML dependency,
- hand-built candidate features,
- trained to rank the held-out true suffix above other topology candidates,
- optional learned abstention threshold selected on train utility.

Features:

```text
bias
log_support
support_share
baseline_reciprocal_rank
log_candidate_count
suffix_length
success_share
ambiguous_share
neutral_share
failure_share
blocker_share
outcome_score
```

## Primary Result: Refined Tokens

Corpus/config:

```text
/mnt/nas/data/ldgr/benchmarks/splits/benchmarks
token_mode=refined
window=30..36
stride=6
```

Train/test split:

```text
rank-train queries: 2525
rank-test queries:  2526
```

| method | utility/query | repeated top1 hit rate | emitted | false emits | precision emitted |
|---|---:|---:|---:|---:|---:|
| support baseline | 0.100679 | 0.488648 | 2437 | 1447 | 0.406237 |
| learned no threshold | 0.099491 | 0.487660 | 2437 | 1449 | 0.405416 |
| learned thresholded | 0.103098 | 0.487660 | 2415 | 1427 | 0.409110 |

Interpretation: the model did not improve ranking, but a learned abstention threshold slightly improved utility by suppressing some false emits. The gain is tiny.

Raw result:

```text
results/dumb_learned_candidate_ranker.json
```

## Token-Mode Follow-up

| token mode | baseline utility | learned threshold utility | baseline top1 | learned top1 | learned precision |
|---|---:|---:|---:|---:|---:|
| entity | 0.091219 | 0.091219 | 0.484733 | 0.484733 | 0.400631 |
| coarse | 0.089804 | 0.089804 | 0.489011 | 0.489011 | 0.398924 |
| refined | 0.100679 | 0.103098 | 0.488648 | 0.487660 | 0.409110 |
| command_refined | 0.113865 | 0.099211 | 0.498028 | 0.456114 | 0.432445 |
| artifact_ext_refined | 0.098913 | 0.113953 | 0.484983 | 0.468735 | 0.439317 |

The strongest baseline was `command_refined`. The strongest learned-threshold result was `artifact_ext_refined`, but it improved by abstaining more, not by improving top-1 hit rate.

Raw result:

```text
results/dumb_learned_candidate_ranker_token_modes.json
```

## Interpretation

The dumb model provides a weak signal:

- It can learn a useful abstention threshold in some token schemas.
- It did not meaningfully improve candidate ranking/top-1 recall.
- The best gains are small enough that larger model investment is not yet justified purely from this result.

This supports the architectural boundary:

```text
topology index = candidate recall/search reduction
model = optional discriminator/formatter over candidates
agent = final consumer/decision-maker
```

But it also says the first trained discriminator should probably receive richer input than these dumb structural features.

## Recommendation

Do not invest days in a heavier model yet.

Next model step, if any:

```text
small candidate reranker with richer candidate/context features
```

Potential features to add before changing model class:

- agreement across entity/coarse/refined indexes,
- two-stage coarse-to-fine survival features,
- goal-conditioned outcome context,
- current workflow phase/goal,
- candidate rendered as compact symbolic trace for an LLM/agent consumer.

The current dumb model is a useful sanity check, but not a strong enough win to justify heavier training by itself.
