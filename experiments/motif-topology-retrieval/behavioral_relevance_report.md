# Behavioral Relevance of Identity-Establishing Deletion

Memory content: LDGR historical observations, artifact descriptions, and report chunks from this project.
Architecture: label-free canonical topology index → typed payload projection → DP/LCS soft alignment.

## Corpus

- memory items: 32
- topics: {'deletion': 8, 'matcher': 6, 'identity': 5, 'noise': 6, 'polysemy': 2, 'typed': 4, 'phase0': 1}

## Clean Baseline

- clean accuracy: 1.0
- mean fine bundle: 1.0
- bundle reduction: 32.0

If clean accuracy is poor, the behavioral relevance profile should be treated as a corpus/encoding failure, not as evidence about deletion brittleness.

## Overall Query Profile

- n_queries: 320
- first_recurring_deletion_incidence: 0.4719
- survival: 0.7562
- survival_when_first_recurring_deleted: 0.6026
- survival_without_first_recurring_deleted: 0.8935
- mean_fine_bundle: 1.1313

## By Query Mode

| mode | n | first-rec incidence | repeat incidence | singleton incidence | survival | fine bundle |
|---|---:|---:|---:|---:|---:|---:|
| adversarial_first_recurring_drop | 32 | 1.0 | 0.0 | 0.0 | 0.9375 | 1.0 |
| prefix_4 | 32 | 0.0 | 0.0 | 0.0 | 0.9062 | 1.1875 |
| prefix_6 | 32 | 0.0 | 0.0 | 0.0 | 0.9375 | 1.0625 |
| prefix_8 | 32 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| prefix_plus_noise | 32 | 0.0 | 0.0 | 0.0 | 0.625 | 1.0625 |
| random_partial_0 | 32 | 0.875 | 0.9688 | 0.9688 | 0.3125 | 1.3438 |
| random_partial_1 | 32 | 1.0 | 0.9688 | 0.9688 | 0.0938 | 1.2188 |
| salient_summary | 32 | 1.0 | 0.0 | 1.0 | 0.9062 | 1.1875 |
| single_omission_0 | 32 | 0.3125 | 0.4375 | 0.25 | 0.9688 | 1.0312 |
| single_omission_1 | 32 | 0.5312 | 0.1562 | 0.3125 | 0.875 | 1.2188 |

## Plausible vs Control Modes

- plausible_modes: {'n': 224, 'first_recurring_deletion_incidence': 0.2634, 'survival': 0.8884, 'survival_when_first_recurring_deleted': 0.8644, 'survival_without_first_recurring_deleted': 0.897, 'mean_fine_bundle': 1.1071}
- control_modes: {'n': 96, 'first_recurring_deletion_incidence': 0.9583, 'survival': 0.4479, 'survival_when_first_recurring_deleted': 0.4348, 'survival_without_first_recurring_deleted': 0.75, 'mean_fine_bundle': 1.1875}

## Recovery With Extra Evidence

- overall survival by added evidence step: {'0': 0.6026, '1': 0.649, '2': 0.649, '3': 0.649}

By mode:

- adversarial_first_recurring_drop: {'0': 0.9375, '1': 1.0, '2': 1.0, '3': 1.0}
- random_partial_0: {'0': 0.25, '1': 0.25, '2': 0.25, '3': 0.25}
- random_partial_1: {'0': 0.0938, '1': 0.0938, '2': 0.0938, '3': 0.0938}
- salient_summary: {'0': 0.9062, '1': 0.9062, '2': 0.9062, '3': 0.9062}
- single_omission_0: {'0': 0.9, '1': 1.0, '2': 1.0, '3': 1.0}
- single_omission_1: {'0': 0.7647, '1': 1.0, '2': 1.0, '3': 1.0}

## Topic Polysemy Probe

- probes: 26
- shared topical inclusion: 1.0
- +mechanism disambiguation: 0.9231
- mean shared bundle: 5.5769
- mean +mechanism bundle: 1.1538

## Interpretation

This profile estimates whether the known destructive perturbation appears under behaviorally plausible historical-query conditions. Prefix/incomplete and noisy-prefix modes model missing tail evidence and inserted noise; single/random omissions model note-taking gaps; adversarial mode calibrates the known boundary.

Overall first-recurring deletion incidence was 0.4719; survival with first-recurring deletion was 0.6026 vs 0.8935 without it.

For the behaviorally plausible modes only, first-recurring deletion incidence was 0.2634 and survival stayed 0.8884 (0.8644 with first-recurring deletion vs 0.897 without).

For control/adversarial modes, first-recurring deletion incidence was 0.9583 and survival dropped to 0.4479. This separates realistic note/incomplete queries from destructive random/adversarial omissions.

Use the by-mode table, not the overall average alone: adversarial calibration is intentionally included and should not be mistaken for expected workload frequency.
