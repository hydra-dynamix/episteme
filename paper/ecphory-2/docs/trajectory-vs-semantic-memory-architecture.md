# Trajectory vs Semantic Memory Architecture

Date: 2026-07-06

Status: Architectural decision note.

## Core Decision

Trajectory memory and semantic memory should not be forced into one retrieval mechanism.

They intersect and communicate, but they solve different lookup problems.

## Trajectory Memory

Trajectory memory retrieves from prefixes.

```text
past -> now

retrieve plausible futures
```

Its job is dynamic:

> Given this partial history, retrieve plausible continuations.

Current invariants:

- identity-free lookup keys,
- temporal prefix signatures,
- predictive evidence,
- retrieved bundles of possible futures,
- post-lookup semantic hydration,
- trust-weighted movement of internal control state toward similar trajectories.

The toy-control ladder supports this mechanism:

`partial topology trace -> nearby possible control futures -> trust-weighted parameter movement -> expected outcome shift`

Identity-free topology is appropriate here because semantic labels should not contaminate the retrieval key. The trace should represent state-transition shape, not named meaning.

## Semantic Memory

Semantic memory retrieves from constraints.

```text
observed constraints

compatible graph

candidate concepts
```

Its job is relational and descriptive:

> Given these observed constraints, retrieve compatible concept neighborhoods.

For a query like "what is a cat?", event order should not dominate retrieval. Evidence can arrive as:

```text
has whiskers
is a mammal
has four legs
hunts mice
meows
```

or:

```text
meows
hunts mice
has whiskers
```

The retrieval target is not a path. It is a compatible neighborhood:

```text
animal
mammal
pet
tail
whiskers
predator
```

Current proposed invariants after the unlabeled-basin result:

- concept identities are post-hoc names for stable basins,
- labels are communication/evaluation payload, not the substrate's organizing key,
- unlabeled constraints should be able to form reusable basins before labels are attached,
- relational constraints dominate order,
- retrieval returns compatible neighborhoods or stabilized basins,
- semantic graph updates may be fed by episodic evidence but are not tied to original event order after consolidation.

This revises the earlier labeled-neighborhood framing. Labels are still useful,
but the primary semantic question is whether compatible constraints settle into
stable reusable basins that later align with human concepts better than chance.
The graph is a convenient projection of those intersections, not necessarily
the memory substrate itself.

## Interface

One experience can feed both systems:

```text
Episode:
I saw a black cat cross the road.

Trajectory memory:
before -> during -> after

Semantic memory:
cat, black, animal, road, movement
```

The systems should communicate:

- trajectory memory answers: what is probably happening?
- semantic memory answers: what does that mean?

Example:

```text
trajectory prediction:
enemy expanding left

semantic neighborhood:
expansion
territory
production
economy
risk
counter expansion
```

## Architectural Implication

Do not make semantic memory retrieve paths by default. Use neighborhoods.

Do not make trajectory memory semantic by default. Use identity-free temporal prefixes.

The bridge is post-lookup interpretation and consolidation:

- trajectory evidence can update semantic graph constraints,
- semantic graph neighborhoods can help interpret new trajectories,
- neither substrate should be collapsed into the other.

## Next Experiment Implication

For the semantic-memory line, test topology/graph lookup as constraint-neighborhood retrieval, not temporal prefix retrieval.

A minimal semantic experiment should:

1. create unlabeled constraint records whose labels are hidden until after lookup,
2. query with unordered constraint sets,
3. retrieve compatible neighborhoods or stabilized basins,
4. attach labels only after lookup for evaluation and communication,
5. compare against label-first lookup as a control,
6. test communication with trajectory memory by using trajectory output as semantic constraints.

The key divergence:

- trajectory topology: identity-free temporal prefix lookup,
- semantic topology: unlabeled relational constraint/basin lookup, with post-hoc labels.

## Constraint-Field Directive

The semantic graph should be treated as a projection, not as the primitive
memory object.

Working ontology:

```text
constraint field
-> local interactions
-> stable attractor basins
-> graph/neighborhood projection
-> post-hoc concept labels
```

This means the next semantic experiments should not optimize only for retrieval
accuracy. They should measure basin dynamics:

- ambiguity: can one surface token such as "bat" activate multiple basins that
  resolve under context?
- composition: can evidence such as "black" plus "cat" settle without requiring
  a new memorized "black cat" basin?
- continuous refinement: does activation deform as new evidence arrives instead
  of restarting lookup?
- locality: can simple local support/conflict/reinforcement rules produce the
  observed basin without a central index?
- stability: how many perturbations can a basin absorb before it transitions to
  another attractor?

The target is not:

```text
query -> hash table -> concept
```

The target is:

```text
activate constraints
-> neighbors reinforce
-> weak links decay
-> cluster stabilizes
-> label attaches after lookup
```

This also preserves the optimization invariant from the sequence-identity work:
when an unexpected optimization appears, do not call it cheating and remove it.
Interrogate the signal, identify where it helps or hurts, and expose it as a
controllable mechanism.
