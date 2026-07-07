# Primary Research Path: Regime-Conditioned Objective Evidence Control

Status: primary research direction as of the Orbit Wars self-play evidence experiment.

This note records the current course correction for Ecphory research. The prior
candidate/PBH refinement branch remains useful negative and baseline evidence,
but it is no longer the primary path. The primary path is now the objective-level
self-play evidence system and its emerging regime-conditioned hierarchy.

The important result is not that the system has produced a deployable Orbit Wars
bot. It has not. The important result is that evidence retrieval measurably
changed objective selection and exposed a mechanistic vocabulary failure in the
flat objective set.

---

## Current Primary Claim

The promising research claim is:

```text
state
  -> infer or retrieve within game regime
  -> retrieve similar historical objective traces
  -> build evidence brief
  -> choose control objective
  -> use boring objective policy to generate action
  -> annotate outcomes
  -> refine objective/regime vocabulary
```

This differs from end-to-end policy learning and from direct hand-tuning of a
single candidate bot. Ecphory should preserve historical structure, retrieve
bounded relevant experience, and use that evidence to select explicit strategic
control surfaces.

---

## Experiment That Triggered the Course Correction

Experiment directory:

```text
experiments/orbit_wars_self_play_evidence/
```

Main scripts:

```text
experiments/orbit_wars_self_play_evidence/run_self_play.py
experiments/orbit_wars_self_play_evidence/audit_objective_traces.py
```

Primary 500-game evidence run:

```text
experiments/orbit_wars_self_play_evidence/runs/tiny-500/
```

Random baseline:

```text
experiments/orbit_wars_self_play_evidence/runs/tiny-500-random/
```

Comparison artifact:

```text
experiments/orbit_wars_self_play_evidence/runs/tiny-500-comparison.json
```

DEFEND audit comparison:

```text
experiments/orbit_wars_self_play_evidence/runs/defend-audit-comparison.json
```

---

## Self-Play Objective Experiment

Initial objective surface was deliberately small:

```text
EXPAND
DEFEND
ABSTAIN
```

The discriminator chose objectives only. It did not emit raw moves.

```text
state + evidence -> choose objective
objective -> boring action generator -> concrete action
```

Each turn produced an objective-decision trace. After each game, traces were
annotated with local, trajectory, and final outcomes using a non-final-dominant
reward:

```text
decision_reward = 0.50 * local_delta
                + 0.35 * trajectory_delta
                + 0.15 * final_outcome
```

This preserves local/trajectory credit assignment and prevents final win/loss
from becoming the dominant explanatory variable.

---

## 500-Game Evidence vs Random Result

| Objective | Evidence mean reward | Random mean reward | Delta |
| --- | ---: | ---: | ---: |
| EXPAND | 0.193669 | 0.070286 | +0.123383 |
| ABSTAIN | 0.096696 | 0.062613 | +0.034083 |
| DEFEND | 0.010707 | 0.027963 | -0.017256 |

Evidence-mode run:

```text
games: 500
traces: 495,238
winner counts: bot_a=255, bot_b=245
objective choices: ABSTAIN=201,122; DEFEND=159,157; EXPAND=134,959
```

Random-mode baseline:

```text
games: 500
traces: 496,226
winner counts: bot_a=253, bot_b=246, draw=1
objective choices: ABSTAIN=215,796; DEFEND=156,855; EXPAND=123,575
```

Interpretation:

* Evidence retrieval was not acting randomly; deltas did not hover around zero.
* `EXPAND` was selected less often than `ABSTAIN` or `DEFEND`, but when selected
  it produced much better reward than random.
* The first useful behavioral signature is therefore not "the bot wins" but
  "evidence changes objective timing in a meaningful direction."

This is a proof of concept for evidence-conditioned objective selection, not a
validated policy result.

---

## DEFEND Audit: Mechanistic Reason to Split the Vocabulary

The DEFEND audit mined all DEFEND decisions in the evidence run:

```text
DEFEND traces: 159,157
positive reward: 60,955
negative reward: 98,202
mean reward: 0.010707
median reward: -0.139087
```

Positive vs negative state contrast:

| Feature | Positive DEFEND | Negative DEFEND | Difference |
| --- | ---: | ---: | ---: |
| ship_ratio | 3.794175 | 0.805779 | +2.988396 |
| production_ratio | 1.913197 | 0.813415 | +1.099782 |
| owned_planet_ratio | 1.834870 | 0.846232 | +0.988638 |
| frontier_pressure | 0.135051 | 0.562449 | -0.427398 |
| enemy_threat_score | 0.132759 | 0.537602 | -0.404842 |
| fleet_commitment_ratio | 0.130601 | 0.349660 | -0.219059 |

K-means audit selected `k=2` as the best diagnostic split among `2,3,4` by the
centroid-separation proxy.

### Cluster 0: ahead-state defense label

```text
count: 114,107
fraction: 71.7%
mean reward: +0.080119
positive rate: 53.4%
final outcomes: win=64,145, loss=49,962
mean ship_ratio: 2.646196
mean production_ratio: 1.486583
mean owned_planet_ratio: 1.448519
mean frontier_pressure: 0.198261
mean enemy_threat_score: 0.184241
```

Interpretation: this is not really emergency defense. It is closer to preserving
or maintaining an advantage under low pressure.

### Cluster 1: high-pressure disadvantaged defense

```text
count: 45,050
fraction: 28.3%
mean reward: -0.165106
positive rate: 0.000755
final outcomes: loss=45,050
mean ship_ratio: 0.187648
mean production_ratio: 0.596413
mean owned_planet_ratio: 0.658381
mean frontier_pressure: 0.906607
mean enemy_threat_score: 0.884855
```

Interpretation: these are collapse-management states. They may already be near
unrecoverable. Treating them as ordinary DEFEND negatives corrupts the objective
learning signal.

---

## Primary Interpretation

The flat objective vocabulary is missing a latent variable: **game regime**.

The current evidence indicates this hierarchy is more appropriate:

```text
regime -> objective -> action generator
```

Instead of a single global objective vocabulary, each regime should expose only
objectives that make sense in that strategic situation.

Candidate regime hierarchy:

```text
AHEAD
  EXPAND
  MAINTAIN_ADVANTAGE
  PRESSURE
  ABSTAIN

BALANCED
  EXPAND
  DEFEND
  HARASS
  ABSTAIN

BEHIND
  REBUILD
  DELAY
  COUNTERATTACK
  ABSTAIN

CRITICAL
  EMERGENCY_STALL
  SAVE_CORE
  SACRIFICE
  ABSTAIN
```

The immediate lesson is not simply "split DEFEND." It is that `DEFEND` was
standing in for at least two different control problems:

```text
Maintain a winning state.
Prevent imminent collapse.
```

Those problems should not share one policy, one reward expectation, or one
evidence neighborhood.

---

## Regime Audit Results

Completed next-step audit artifacts:

```text
experiments/orbit_wars_self_play_evidence/runs/tiny-500/analysis/regime-audit.json
experiments/orbit_wars_self_play_evidence/runs/tiny-500/analysis/regime-objective-reward.csv
experiments/orbit_wars_self_play_evidence/runs/tiny-500/analysis/regime-transition-summary.json
experiments/orbit_wars_self_play_evidence/runs/tiny-500/analysis/regime-audit-report.md
experiments/orbit_wars_self_play_evidence/runs/regime-audit-comparison.json
```

Regime labels are provisional state-feature audit annotations, not retrieval
signatures or validated policy labels.

Evidence-run regime summary:

| Regime | Count | Fraction | P(win) | Mean reward | Positive rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| AHEAD | 161,070 | 32.52% | 95.62% | +0.414487 | 84.84% |
| BALANCED | 172,149 | 34.76% | 50.21% | +0.022404 | 50.73% |
| BEHIND | 98,489 | 19.89% | 7.25% | -0.133909 | 8.43% |
| CRITICAL | 63,530 | 12.83% | 0.02% | -0.159619 | 0.21% |

Evidence-vs-random regime deltas:

| Regime | Fraction delta | Mean reward delta | Win-rate delta |
| --- | ---: | ---: | ---: |
| AHEAD | +4.49 pp | +0.103660 | -1.36 pp |
| BALANCED | -8.86 pp | +0.005610 | +0.10 pp |
| BEHIND | +2.07 pp | +0.002936 | +2.51 pp |
| CRITICAL | +2.29 pp | -0.002955 | -0.08 pp |

Main objective-level findings:

* AHEAD `EXPAND` is the clearest positive signal: +0.554794 mean reward, +0.202548 over random within the same regime/objective cell.
* BALANCED `DEFEND` is suspect: -0.027539 mean reward and -0.032928 below random in the same cell.
* BEHIND `EXPAND` remains negative but is the least bad non-abstain signal and improves over random by +0.020655 mean reward and +0.067790 win-rate delta.
* CRITICAL is mostly unrecoverable with this surface: P(win) about 0.02%; 30-turn CRITICAL -> non-CRITICAL transitions are only 2.04%.

The audit strengthens the hierarchy:

```text
state -> regime -> regime-scoped evidence -> objective -> boring policy -> action
```

---

## Next Atomic Work

Implement a minimal regime-conditioned A/B experiment. Keep the reward formula,
post-game annotation, and evidence-vs-random methodology fixed. Change only the
control vocabulary/policy surface enough to test whether regime conditioning
makes evidence neighborhoods more coherent.

Initial staged objective mapping:

```text
AHEAD:    EXPAND, MAINTAIN_ADVANTAGE, ABSTAIN
BALANCED: EXPAND, CONTEST_FRONTIER, ABSTAIN
BEHIND:   REBUILD, DELAY, ABSTAIN
CRITICAL: EMERGENCY_STALL, SAVE_CORE, ABSTAIN
```

Do not add HARASS or a richer tactical planner yet. Policies should remain
boring and hand-written. CRITICAL objectives should be evaluated on survival,
score-loss reduction, core preservation, or repair-path discovery rather than
ordinary win probability.

---

## Governance Decision

This self-play evidence/regime path is now the primary Ecphory research path.

The previous PBH/candidate-refinement branch is retained as baseline and negative
evidence, but should not consume the main research loop unless explicitly
requested. Its failed or inconclusive results remain useful evidence about the
limits of direct candidate tuning and broad hand-authored strategy rewrites.

Future work should prioritize:

1. objective trace mining;
2. regime annotation;
3. regime-conditioned retrieval;
4. regime-scoped objective vocabularies;
5. boring objective policies before tactical invention;
6. validation against random and ablated baselines.

Claims remain evidence-quality claims until validated. The current result is a
research-direction milestone, not a deployed-game-performance claim.
