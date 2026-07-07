# LDGR harness setup

`ldgr init` installed the Pi project-local extension `.pi/extensions/ldgr-context.ts`.

If your agent harness is Pi, run `/reload` so `/ldgr <args>`, `/ldgr-context`, and `/run-loop` become available. `/ldgr` runs the LDGR CLI in the project and pipes stdout/stderr back into the conversation; with no args it runs `ldgr context --brief`. `/run-loop [adapter] [loop args]` selects an installed adapter loop prompt and runs `ldgr loop run --agent agentctl --until-empty --summary-agent agentctl`, launching one fresh worker agent per LDGR work item and one separate fresh summarizer call per completed cycle until no pending work remains or the loop blocks.

If your agent harness is not Pi or does not load project-local Pi extensions, point the agent at this document and ask it to adapt the installed extension for its harness. The extension is optional; core `ldgr ...` commands continue to work from the shell.
