"""Smoke: the greedy matcher chokes on one inserted evidence node; skip matchers recover."""

from __future__ import annotations

import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m

gen = _load("generator", os.path.join(HERE, "generator.py"))
matcher = _load("matcher_relaxation", os.path.join(HERE, "matcher_relaxation.py"))

W = {"w_structure": 1.0, "w_typed": 0.5, "w_contradict": 0.7, "w_missing": 1.0, "w_extraneous": 0.15}


def main():
    _, _, all_instances, _, _ = gen.build_generated_graph_with_polysemy(
        n_disjoint_families=5, n_polysemy_bases=3, instances_per=3, seed=20260706)
    inst = all_instances["gen_000"][0]
    clean = inst.walk
    noisy = clean[:3] + [("F-noise", "FOREIGN", "in")] + clean[3:]
    c = matcher.view(clean)
    e = matcher.view(noisy)
    print("clean node trace:", c.node_trace)
    print("noisy node trace:", e.node_trace)
    print("\nMATCHER SMOKE: clean candidate vs noisy evidence")
    print(f"{'matcher':<14} {'aligned':>7} {'missing':>7} {'extra':>7} {'typed':>7} {'total':>8}")
    for name in ("greedy", "dp", "bidirectional", "bag_edges"):
        s = matcher.score(c, e, matcher=name, weights=W)
        print(f"{name:<14} {s.aligned:>7} {s.missing:>7} {s.extraneous:>7} {s.typed_support:>7} {s.total:>8}")
    print("\nExpected: dp/bidirectional align more evidence than greedy after the inserted node.")


if __name__ == "__main__":
    main()
