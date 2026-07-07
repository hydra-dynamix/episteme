"""Dataset A: toy semantic world.

Each target is an object with:
  - attrs:    unordered set of attribute tokens (variant A: unordered neighborhood)
  - trace:    canonical ordered value sequence, general -> specific (variant B: ordered)
  - typed:    canonical ordered (type, value) edge sequence (variant C: typed ordered)
  - evidence: the retrieval query for a held-out target = its own trace, fed token by token.

Source: docs/relational-transition-memory-substrate.md (Dataset A examples:
cat, dog, crow, panther; bear appears in the phase-2 narrowing walkthrough).
wolf and eagle are added to create the attribute overlap required for a
non-trivial top_3_recall and candidate_set_reduction on a controlled toy world.

The evidence for a target is its own canonical trace. This is the best-case
arrival order a transition-trace substrate must handle (phase 2 / phase 3 of the
program). The shuffled-order control permutes that same evidence to test whether
the benefit comes from transition structure rather than content alone.
"""

# relation type for each attribute value. In this toy every value has exactly
# one type, so typed-edge matching coincides with ordered value matching; this
# is recorded as an honest limitation and a phase-4 dataset concern (polymorphic
# values across relation types are needed to discriminate typed from ordered).
ATTR_TYPE = {
    "animal": "ROOT",
    "mammal": "CLASS",
    "bird": "CLASS",
    "black": "COLOR",
    "brown": "COLOR",
    "white": "COLOR",
    "fur": "COVERING",
    "feathers": "COVERING",
    "tail": "BODY",
    "wings": "BODY",
    "beak": "BODY",
    "whiskers": "BODY",
    "four_paws": "BODY",
    "two_legs": "BODY",
    "claws": "BODY",
    "predator": "BEHAVIOR",
    "pack_animal": "BEHAVIOR",
    "omnivore": "BEHAVIOR",
}

# canonical traces: general -> specific. Ordering is the meaningful discovery
# order the transition-trace variant is meant to exploit.
TRACES = {
    "cat":     ["animal", "mammal", "fur", "tail", "four_paws", "whiskers", "predator"],
    "dog":     ["animal", "mammal", "fur", "tail", "four_paws", "pack_animal"],
    "panther": ["animal", "mammal", "black", "fur", "tail", "four_paws", "predator"],
    "bear":    ["animal", "mammal", "fur", "four_paws", "claws", "omnivore"],
    "wolf":    ["animal", "mammal", "fur", "tail", "four_paws", "pack_animal", "predator"],
    "crow":    ["animal", "bird", "black", "wings", "beak", "two_legs"],
    "eagle":   ["animal", "bird", "wings", "beak", "two_legs", "predator"],
}


def build_world():
    """Return the toy world as a dict target -> {attrs, trace, typed}."""
    world = {}
    for name, trace in TRACES.items():
        attrs = set(trace)
        typed = [(ATTR_TYPE[v], v) for v in trace]
        world[name] = {"attrs": attrs, "trace": list(trace), "typed": typed}
    return world


def evidence_for(world, target):
    """Retrieval query for a held-out target = its own canonical trace."""
    return list(world[target]["trace"])


def typed_evidence_for(world, target):
    return list(world[target]["typed"])


TARGETS = sorted(TRACES.keys())
