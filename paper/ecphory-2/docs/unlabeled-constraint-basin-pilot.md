# Unlabeled Constraint Basin Pilot

Date: 2026-07-06

## Purpose

This experiment tests the concern that semantic labels may fragment topology/neighborhood retrieval.

Question:

Can an unlabeled constraint substrate recover stable reusable basins that align with human concepts better than chance?

## Boundary

Lookup and basin formation use only:

- anonymous constraint IDs,
- anonymous pairwise constraint structure.

Human concept labels are evaluation-only payload. They are revealed only after lookup.

This deliberately differs from the labeled semantic-neighborhood pilot.

## Experiment

Script:

`scripts/run_unlabeled_constraint_basin_pilot.py`

Report:

`results/unlabeled-constraint-basin-pilot/report.json`

Concept records use hidden human labels such as `cat`, `dog`, `bird`, `fish`, `car`, and `truck`, but lookup sees only anonymous constraints like `c01`, `c02`, etc.

## Results

Query retrieval:

| Metric | Value |
| --- | ---: |
| Train records | 30 |
| Query records | 12 |
| Top-k | 5 |
| Query accuracy after lookup | 1.000000 |
| Shuffled-label accuracy | 0.000000 |
| Accuracy lift vs shuffled | 1.000000 |

Default basin threshold `0.35`:

| Metric | Value |
| --- | ---: |
| Basin count | 4 |
| Mean basin size | 7.500000 |
| Mean post-hoc label purity | 0.750000 |

Threshold sweep:

| Threshold | Basin count | Mean size | Mean purity | Reusable basins | Reusable purity |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.25 | 4 | 7.500000 | 0.750000 | 4 | 0.750000 |
| 0.30 | 4 | 7.500000 | 0.750000 | 4 | 0.750000 |
| 0.35 | 4 | 7.500000 | 0.750000 | 4 | 0.750000 |
| 0.40 | 6 | 5.000000 | 1.000000 | 6 | 1.000000 |
| 0.45 | 12 | 2.500000 | 1.000000 | 6 | 1.000000 |
| 0.50 | 12 | 2.500000 | 1.000000 | 6 | 1.000000 |

## Interpretation

The answer is yes in this controlled pilot:

- unlabeled constraint lookup recovers human concept labels above shuffled chance,
- reusable basins emerge without using human labels as lookup keys,
- basin scale matters.

At low thresholds, the substrate forms broader super-basins. These are not failures; they show structural similarity across related concepts. For example, nearby animal-like or vehicle-like concepts can merge.

At threshold `0.40`, the substrate recovers six reusable basins with perfect post-hoc human-label purity and mean basin size `5.0`. That is the useful operating point in this toy setup.

## Decision

The semantic substrate should support an unlabeled mode:

```text
anonymous constraints
-> structural neighborhood/basin
-> post-hoc concept alignment
```

Human labels should not be required for basin formation. Labels can be attached after lookup for interpretation, evaluation, and communication with human concepts.

This suggests a revised semantic-memory split:

- unlabeled constraint substrate: basin formation and reusable neighborhoods,
- labeled semantic layer: post-hoc naming, interpretation, and communication.

## Next Work

Combine this with the semantic-control loop:

1. retrieve an unlabeled basin,
2. align the basin to semantic concepts after lookup,
3. perturb internal choice state through the aligned concept neighborhood,
4. compare against directly labeled semantic lookup.

The key question becomes whether unlabeled basins produce better control perturbations than label-first semantic neighborhoods.
