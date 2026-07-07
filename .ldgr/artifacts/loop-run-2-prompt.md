# Assigned work (run 2)

You are run 2. Complete exactly this work item and no other:

- slug: toy-semantic-retrieval-benchmark
- title: Implement toy semantic retrieval benchmark
- description: Build the Phase 0/2 toy semantic world benchmark in the research harness layout. Compare unordered, ordered, typed, and shuffled-order variants with incremental evidence retrieval. Emit results.json, retrieval_steps.json, comparison.md, and a compact run_summary.json with top_3_recall, candidate_set_reduction, false_elimination_rate, monotonic_narrowing_rate, and shuffled-control comparison. Research spine: program relational-transition-memory-substrate / branch main / question does-toy-evidence-narrowing-work / option compare-substrate-variants-on-toy-world / experiment phase0-toy-semantic-retrieval (mode=falsification). Source: docs/relational-transition-memory-substrate.md. Do not touch LDGR integration until phase 6 passes.

In the context below this item appears with status `running` because this run was started for it. Other pending items in the context are NOT yours this cycle.

# Research Loop

Job completion policy: complete exactly one bounded work item, queue concrete follow-up LDGR work when gaps are found, ensure a pending next task exists unless no useful work remains, and never self-certify whole-project completion.

Project completion was not requested. Do not claim whole-project completion; focus on the next bounded LDGR work item.

You are running one bounded research cycle. Complete exactly the assigned work
item stated at the top of this prompt. Treat this cycle as one experiment, not a
research program. LDGR carries continuity between cycles; you do not need to keep
the whole project in context.

The LDGR context below is the durable source of truth. When it conflicts with
project docs or memory, the ledger wins.

## Start of cycle

1. Read `AGENTS.md` if present.
2. Run `git status --short`.
3. Read the assigned work item and the LDGR context.
4. Select exactly one hypothesis to test in this cycle.

If the assigned work item already names the hypothesis, use that. If it names a
broader research direction, narrow it to one testable hypothesis before doing
any implementation.

## Required research sequence

Complete these steps in order while minimizing ceremony:

1. **Select hypothesis to test.** State the one hypothesis this cycle will test.
   If the work item already names it, do not restate it in multiple places.
2. **Implement experiment.** Make only the changes needed to run this experiment.
   Keep scope narrow and avoid unrelated cleanup.
3. **Execute experiment.** Run the command, script, benchmark, inspection, or
   manual check that tests the hypothesis. Save important raw outputs as
   artifacts only when they are too large or important to preserve inline.
4. **Create one compact run summary artifact.** Write `run_summary.json` with
   stable keys:
   - `hypothesis`
   - `changed`
   - `commands`
   - `metrics`
   - `pass_criteria`
   - `outcome`: `supported|weakened|falsified|inconclusive|blocked`
   - `claim_delta`
   - `artifacts`
   - `next_work`
5. **Record the compact evidence.** Add the `run_summary.json` artifact to LDGR
   and record at most one concise observation that points to the artifact and
   states the outcome. Do not duplicate the same content in observations,
   markdown reports, and final prose.
6. **Queue possible next research direction.** If more useful research remains,
   queue exactly one next hypothesis/direction as the next work item. Keep it
   bounded enough for a fresh agent instantiation to test in one cycle. You may
   promote a newly discovered work item when the evidence supports that direction;
   make the evidence link explicit in the run summary and closing decision.
7. **End the run.** Close the run with a compact decision rationale. It should
   reference the run summary artifact and include only outcome, confidence or
   limitation if material, and next work if queued.

## Rules

- One bounded experiment per cycle.
- Do not carry out multiple competing hypotheses in one run.
- Do not broaden a narrow positive result; state exactly what was shown.
- Negative results are progress. Preserve what changed and why.
- Prefer one machine-summarizable artifact over repeated prose. The target is
  maximum continuity per token/minute, not maximum narrative.
- If blocked, record what prevented the experiment and close the run as blocked
  or partial rather than inventing a workaround.
- Queue follow-up work only when it is a concrete next hypothesis or research
  direction. Do not create broad placeholder tasks.

## Artifact/report policy

Routine cycles should produce the thin structured `run_summary.json` record only.
Use `templates/run-summary.json` as the shape when helpful.

Write longer markdown reports only at promotion points:

- claim graph changes;
- surprising negative results;
- operator/model/policy promotion or demotion;
- external-validity shifts;
- milestone synthesis.

Optional promotion-point templates:

- `templates/experiment-plan.md`
- `templates/claim-review.md`
- `templates/negative-result.md`
- `templates/campaign-branch.md`
- `templates/campaign-comparison.md`

The durable record for a routine bounded cycle is the run summary artifact,
minimal evidence references, validation records, and closing decision.

## LDGR context

```json
{
  "pending_work_items": 0,
  "running_work_items": 1,
  "held_work_items": 0,
  "done_work_items": 1,
  "canceled_work_items": 0,
  "loop_state": {
    "run_id": 2,
    "work_slug": "toy-semantic-retrieval-benchmark",
    "work_title": "Implement toy semantic retrieval benchmark",
    "current_phase": "prompt_source",
    "progress_report": "Using loop prompt path /home/bakobi/.ldgr/adapters/research/loop-prompt.md.",
    "command": "agentctl",
    "started_at": "2026-07-06 18:15:15",
    "finished_at": null,
    "terminal_status": null,
    "recent_cycle_narrative": [
      {
        "created_at": "2026-07-06 18:15:15",
        "phase": "started",
        "message": "Started loop cycle."
      },
      {
        "created_at": "2026-07-06 18:15:15",
        "phase": "started",
        "message": "Started bounded loop session for toy-semantic-retrieval-benchmark."
      },
      {
        "created_at": "2026-07-06 18:15:15",
        "phase": "rendering_prompt",
        "message": "Rendering loop prompt for toy-semantic-retrieval-benchmark."
      },
      {
        "created_at": "2026-07-06 18:15:15",
        "phase": "prompt_source",
        "message": "Using loop prompt path /home/bakobi/.ldgr/adapters/research/loop-prompt.md."
      }
    ]
  },
  "active_runs": [
    {
      "run_id": 2,
      "work_slug": "toy-semantic-retrieval-benchmark",
      "work_title": "Implement toy semantic retrieval benchmark",
      "command": "agentctl",
      "started_at": "2026-07-06 18:15:15"
    }
  ],
  "next_work_item": null,
  "latest_decision": {
    "decision_id": 1,
    "work_slug": "prepare-research-onramp",
    "outcome": "continue",
    "rationale": "Research on-ramp is ready: the program document is reviewed, constraints and first falsification gate are recorded, and the next run should implement the smallest toy benchmark.",
    "next_work_slug": "toy-semantic-retrieval-benchmark",
    "created_at": "2026-07-06 09:02:06"
  },
  "latest_observations": [
    {
      "observation_id": 4,
      "run_id": 1,
      "work_slug": "prepare-research-onramp",
      "body": "Research overlay initialized at project level (ldgr research init): created .ldgr/research/{research.db,policy.yaml,tools.yaml}, applied migrations 1-4, created artifact roots output/ and experiments/, installed research prompts (~/.ldgr/prompts/research-loop.md) and adapter-owned skills, activated research-loop prompt. Built program spine: program=relational-transition-memory-substrate, branch=main, question=does-toy-evidence-narrowing-work, option=compare-substrate-variants-on-toy-world, experiment=phase0-toy-semantic-retrieval (mode=falsification). Existing pending core work toy-semantic-retrieval-benchmark linked to the spine as the single bounded next loop task.",
      "created_at": "2026-07-06 11:46:53"
    },
    {
      "observation_id": 3,
      "run_id": 1,
      "work_slug": "prepare-research-onramp",
      "body": "Initial acceptance criteria: top_3_recall >= 0.95, false_elimination_rate <= 0.05, candidate_set_reduction >= 3x, and ordered or typed variant must beat shuffled control. Do not touch LDGR integration until phase 6 passes.",
      "created_at": "2026-07-06 09:01:48"
    },
    {
      "observation_id": 2,
      "run_id": 1,
      "work_slug": "prepare-research-onramp",
      "body": "Immediate research gate: start with the toy semantic world and compare unordered neighborhood, ordered transition trace, typed ordered trace, and shuffled-order control using incremental evidence retrieval.",
      "created_at": "2026-07-06 09:01:48"
    }
  ],
  "latest_validations": [
    {
      "validation_id": 21,
      "run_id": 1,
      "work_slug": "prepare-research-onramp",
      "outcome": "pass",
      "command": "ldgr research program list / branch list / question list / option list / experiment list",
      "rationale": "Spine created: program relational-transition-memory-substrate, branch main, question does-toy-evidence-narrowing-work, option compare-substrate-variants-on-toy-world, experiment phase0-toy-semantic-retrieval.",
      "created_at": "2026-07-06 11:46:53"
    },
    {
      "validation_id": 20,
      "run_id": 1,
      "work_slug": "prepare-research-onramp",
      "outcome": "pass",
      "command": "ldgr research status / ldgr research context",
      "rationale": "One active program, one open question, one validation option; exactly one pending core work item (toy-semantic-retrieval-benchmark) aligned to experiment phase0-toy-semantic-retrieval.",
      "created_at": "2026-07-06 11:46:53"
    },
    {
      "validation_id": 18,
      "run_id": 1,
      "work_slug": "prepare-research-onramp",
      "outcome": "pass",
      "command": "ldgr research mode status",
      "rationale": "Research overlay enabled; status/context/loop use research defaults; core passthrough via ldgr research core.",
      "created_at": "2026-07-06 11:46:53"
    }
  ],
  "global_observations": [],
  "latest_artifacts": [
    {
      "artifact_id": 2,
      "run_id": 1,
      "work_slug": "prepare-research-onramp",
      "kind": "prompt",
      "path": "submitted/run-1-1783328514974396314-episteme-research-loop.md",
      "description": "Reusable project loop prompt for future one-work-item Episteme research runs.",
      "created_at": "2026-07-06 09:01:54"
    },
    {
      "artifact_id": 1,
      "run_id": 1,
      "work_slug": "prepare-research-onramp",
      "kind": "document",
      "path": "submitted/run-1-1783328514939632277-relational-transition-memory-substrate.md",
      "description": "Research program source document defining hypotheses, phases, metrics, gates, kill criteria, and recommended first experiment.",
      "created_at": "2026-07-06 09:01:54"
    }
  ],
  "loop_interventions": [],
  "latest_events": [
    {
      "event_id": 26,
      "entity_type": "run",
      "entity_id": 2,
      "event_type": "phase",
      "payload_json": "{\"phase\":\"prompt_source\",\"progress_report\":\"Using loop prompt path /home/bakobi/.ldgr/adapters/research/loop-prompt.md.\"}",
      "created_at": "2026-07-06 18:15:15"
    },
    {
      "event_id": 25,
      "entity_type": "run",
      "entity_id": 2,
      "event_type": "phase",
      "payload_json": "{\"phase\":\"rendering_prompt\",\"progress_report\":\"Rendering loop prompt for toy-semantic-retrieval-benchmark.\"}",
      "created_at": "2026-07-06 18:15:15"
    },
    {
      "event_id": 24,
      "entity_type": "run",
      "entity_id": 2,
      "event_type": "phase",
      "payload_json": "{\"phase\":\"started\",\"progress_report\":\"Started bounded loop session for toy-semantic-retrieval-benchmark.\"}",
      "created_at": "2026-07-06 18:15:15"
    },
    {
      "event_id": 23,
      "entity_type": "run",
      "entity_id": 2,
      "event_type": "start",
      "payload_json": "{\"command\":\"agentctl\"}",
      "created_at": "2026-07-06 18:15:15"
    },
    {
      "event_id": 22,
      "entity_type": "work_item",
      "entity_id": 2,
      "event_type": "start_run",
      "payload_json": "{\"run_id\":2}",
      "created_at": "2026-07-06 18:15:15"
    },
    {
      "event_id": 21,
      "entity_type": "run",
      "entity_id": 1,
      "event_type": "validation",
      "payload_json": "{\"command\":\"ldgr research program list / branch list / question list / option list / experiment list\",\"outcome\":\"pass\",\"rationale\":\"Spine created: program relational-transition-memory-substrate, branch main, question does-toy-evidence-narrowing-work, option compare-substrate-variants-on-toy-world, experiment phase0-toy-semantic-retrieval.\",\"run_id\":1}",
      "created_at": "2026-07-06 11:46:53"
    },
    {
      "event_id": 20,
      "entity_type": "run",
      "entity_id": 1,
      "event_type": "validation",
      "payload_json": "{\"command\":\"ldgr research status / ldgr research context\",\"outcome\":\"pass\",\"rationale\":\"One active program, one open question, one validation option; exactly one pending core work item (toy-semantic-retrieval-benchmark) aligned to experiment phase0-toy-semantic-retrieval.\",\"run_id\":1}",
      "created_at": "2026-07-06 11:46:53"
    },
    {
      "event_id": 19,
      "entity_type": "observation",
      "entity_id": 4,
      "event_type": "add",
      "payload_json": "{}",
      "created_at": "2026-07-06 11:46:53"
    },
    {
      "event_id": 18,
      "entity_type": "run",
      "entity_id": 1,
      "event_type": "validation",
      "payload_json": "{\"command\":\"ldgr research mode status\",\"outcome\":\"pass\",\"rationale\":\"Research overlay enabled; status/context/loop use research defaults; core passthrough via ldgr research core.\",\"run_id\":1}",
      "created_at": "2026-07-06 11:46:53"
    },
    {
      "event_id": 17,
      "entity_type": "work_item",
      "entity_id": 2,
      "event_type": "edit",
      "payload_json": "{\"description\":\"Build the Phase 0/2 toy semantic world benchmark in the research harness layout. Compare unordered, ordered, typed, and shuffled-order variants with incremental evidence retrieval. Emit results.json, retrieval_steps.json, comparison.md, and a compact run_summary.json with top_3_recall, candidate_set_reduction, false_elimination_rate, monotonic_narrowing_rate, and shuffled-control comparison. Research spine: program relational-transition-memory-substrate / branch main / question does-toy-evidence-narrowing-work / option compare-substrate-variants-on-toy-world / experiment phase0-toy-semantic-retrieval (mode=falsification). Source: docs/relational-transition-memory-substrate.md. Do not touch LDGR integration until phase 6 passes.\",\"title\":null}",
      "created_at": "2026-07-06 11:46:53"
    }
  ]
}
```
