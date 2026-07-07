# Episteme Research Loop

Run `ldgr status` first. Use `ldgr context --brief` or `ldgr context` only when the brief status does not contain enough continuity.

Take exactly one pending work item. Start one LDGR run for that item, complete only that item, and close the run before signing off.

For this project, follow `docs/relational-transition-memory-substrate.md` as the research program. Do not touch LDGR integration until the program reaches the real Learning Record retrieval phase and passes the earlier gates.

Prefer small falsifiable experiments. The current first gate is the toy semantic world benchmark comparing unordered, ordered, typed ordered, and shuffled-order variants for evidence accumulation retrieval.

Routine runs should leave compact machine-summarizable artifacts, such as `run_summary.json`, containing:

- objective or hypothesis
- changed files and research surfaces
- commands run
- metrics observed
- outcome
- artifact references
- next work, if discovered

Record LDGR observations, artifacts, validations, and decisions only when they add durable continuity. Do not duplicate the same evidence across observations, documents, decisions, and final prose.

Queue follow-up work only when new scope is discovered or the current run reaches a clean handoff point.
