---
name: orchestration
description: Route work to the best-fit model and cross-check it with the other vendor. Use whenever you act as orchestrator and hand work to subagents: implementation, debugging, planning, design, reviews, research, analysis, benchmark or test runs. Covers which model fits which task (Claude Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5; Codex GPT-6 Astra, Sol, Luna), how to brief and launch each, and the rule that work produced by one vendor is checked once by the other before it is accepted.
---

# Orchestration: route by fit, cross-check across vendors

You are the orchestrator. You decide, brief, review and record; subagents do the work. Two rules:

1. **Route each task to the best-fit model**, using the guidance below. Fit means quality for that
   kind of work and the consequence of getting it wrong first, then cost and speed.
2. **Cross-check across vendors, once.** Anything a Claude model produced (code, plan, design,
   diagnosis, analysis) is checked by a Codex model before you accept it, and anything Codex
   produced is checked by a Claude model. The checker is the other vendor, never the same family.
   One independent check plus your own adjudication completes the cycle: the checker's report is
   not itself re-checked. If a fix is needed, the fix is new work and gets its own single check.

You own the result: verify each finding against the source before acting on it, and decide. A
cross-check is evidence, not a verdict. If the other vendor is unavailable, or the checker could
not inspect the evidence (tool failure, missing access), the work is **unverified**: say so and do
not treat it as accepted.

## Which model for which task

### What the benchmarks say (looked up 2026-10-17)

Read these as weak evidence. The two vendors report different coding suites (Anthropic: SWE-bench
Pro; OpenAI: DeepSWE), which cannot be compared to each other; versions are easy to confuse;
effort settings change results a lot; and most figures are vendor-reported. Coding scores do not
by themselves prove which model is better at architecture or review. Re-check when a model ships.

| Model | Figures and source quality |
|---|---|
| Claude Fable 5.1 | Terminal-Bench 4.0 55.8% (secondary). FrontierCode 1.1 Extended 63.6%, per OpenAI's Astra table as reported by a Codex review (the 64.9% often quoted is Fable 5). SWE-bench: no 5.1 figure confirmed; the widely quoted 95.0% Verified / 80.0% Pro are attributed to Fable 5 by some sources and to 5.1 by others; unresolved. |
| Claude Opus 5.5 | SWE-bench Pro 89.9% (secondary); Terminal-Bench 4.0 66.4% at xhigh effort (Anthropic). Anthropic calls it "clearly stronger at complex, open-ended work" than Sonnet 5.5. Priced at $4 / $20 per million input/output tokens, twice Sonnet 5.5. |
| Claude Sonnet 5.5 | SWE-bench Pro 81.3% (secondary); Terminal-Bench 4.0 70.6%, above Opus 5.5 (Anthropic). $2 / $10 per million tokens; Anthropic says "up to 30% less per task than its predecessor" (Sonnet 5), not cheaper than Opus by 30%. |
| Claude Haiku 5.5 | Terminal-Bench 4.0 39.2%, FrontierSWE v2 43.8% (secondary). Anthropic's Sonnet 5.5 page announced it as coming; confirm availability. |
| GPT-6 Astra | DeepSWE v1.1 74.1%; Terminal-Bench 4.0 57.9% (OpenAI's table, as reported by a Codex review; secondary sources say 57.7%); FrontierCode 1.1 53.3% main, 64.5% Extended. |
| GPT-6 Sol | DeepSWE v1.1 68.8% at max effort (secondary). The 72.7% sometimes quoted is GPT-5.6 Sol. GPT-6.1 Sol figures (75.2%) describe a different model and say nothing about GPT-6 Sol. FrontierCode 1.1 49.3%. Much cheaper than Astra. |
| GPT-6 Luna | DeepSWE v1.1 66.6% at max effort (secondary); FrontierCode 1.1 42.4%; reported 93-96% cheaper per task than the top models. |

The OpenAI primary page (https://openai.com/index/gpt-6-astra/) returned 403 to the orchestrator
on 2026-10-17, so the OpenAI-table corrections above come from a Codex review and are not
independently re-read.

### Routing (judgement informed by the above, not proven by it)

Route by the hardest and most consequential part of the task, not its length.

| Task kind | First choice | Also suitable | Notes |
|---|---|---|---|
| Architecture, design, plans that set direction | Fable 5.1 | Astra, Opus 5.5 | High consequence; spend on the strongest model |
| Hard root cause, ambiguous bugs, concurrency, persistence, lifecycle ordering | Opus 5.5 or Fable 5.1 | Astra | Do not route these down because the diff is small |
| Security review, auth, input validation, anything security-sensitive (even small diffs) | Astra | Opus 5.5 / Fable 5.1 | Never Haiku/Luna |
| Migration, rollback, data conversion, schema/wire changes | Opus 5.5 | Astra | Requires a rehearsal or test plan |
| Complex implementation, large refactors | Opus 5.5 | Sol | |
| Routine implementation, local fixes | Sonnet 5.5 | Sol | |
| Terminal-heavy runs: builds, test suites, benchmark runs, collecting results | Sonnet 5.5 | Sol | Sonnet leads Terminal-Bench among Claude models |
| Experiment design, statistics, interpreting benchmark or A/B results, causal claims | Opus 5.5 | Astra | Not arithmetic; needs reasoning about noise and confounds |
| UI and visual QA, screenshots, layout | Sonnet 5.5 or Opus 5.5 | Sol | Requires the tools to see the UI; say if they cannot |
| Mechanical: extracting numbers from logs, file inventories, renames, simple summaries | Haiku 5.5 | Luna | Only when the task truly has no judgement in it |
| Research and source lookup | Sonnet 5.5 | Sol | Require cited primary sources and versions |
| Adversarial review of a finished change | Astra (for Claude work) / Opus 5.5 or Fable 5.1 (for Codex work) | | See cross-check table |

Effort: for high-consequence work use the model's high or xhigh effort; for mechanical work the
default is enough.

### Who checks what

| Work done by | Kind of work | Cross-check with |
|---|---|---|
| Claude | Code, fixes | Codex Sol; Astra if security, concurrency, persistence, migration or wide impact |
| Claude | Plan, design, architecture, diagnosis | Codex Astra |
| Claude | Measurement or run report (numbers only) | Codex Luna re-derives the numbers from the raw logs |
| Claude | Analysis or interpretation of results | Codex Astra |
| Codex | Code, fixes | Claude Opus 5.5 (Sonnet 5.5 for small, low-risk local diffs; never for security-sensitive ones) |
| Codex | Plan, design, architecture, diagnosis | Claude Fable 5.1 or Opus 5.5 |
| Codex | Measurement or run report (numbers only) | Claude Haiku 5.5 or Sonnet 5.5 re-derive the numbers |
| Codex | Analysis or interpretation of results | Claude Opus 5.5 |

Proportionality: every substantive change, plan or conclusion gets one check. A pure data run
(build, benchmark run) is not repeated; its interpretation is checked from the raw logs.
Checkers are read-only and never edit.

## How to launch

**Claude subagent:** the Agent tool, `subagent_type: "general-purpose"` (or `Plan` / `explore`
for read-only work), with `model: "fable" | "opus" | "sonnet" | "haiku"`. Launch it with the tool's
background option and wait for its completion notice; never poll its transcript.

**Codex:** the CLI, run through the shell tool's own background facility (the command itself does
not background anything or notify you; the harness does):

```bash
codex exec --skip-git-repo-check -m gpt-6-sol -s workspace-write -C <workdir> -o <task-dir>/last-message.md "$(cat <task-dir>/prompt.md)" < /dev/null > <task-dir>/run.log 2>&1; echo "codex exit $?"
```

- `-m gpt-6-astra | gpt-6-sol | gpt-6-luna`.
- Sandbox, least access first: `-s read-only` for reviews and diagnosis; `-s workspace-write` for
  edits, builds and tests, adding `--add-dir <dir>` for each extra directory it must write;
  `-s danger-full-access` only when that has been seen to fail for the job (record why in the brief).
- `--skip-git-repo-check` is needed outside Git repositories. `< /dev/null` stops the CLI waiting
  for stdin in a non-interactive shell (stdin can otherwise be used to pass the prompt).
- Use a unique `<task-dir>` per task. Before accepting the report, check the exit status and that
  `last-message.md` was written by this run (timestamp after launch), then read it.

## How to brief any subagent

Write the brief to a file and pass it. A good brief has:

1. **Goal and why**, plus where things stand (commit, branch, what earlier phases did), so the
   worker does not rediscover the repo.
2. **Exact scope:** files it may change, files it must not touch, and what it must not run.
3. **The repository's standing rules**, copied from its AGENTS.md / CLAUDE.md: version control
   rules, one heavy build or test at a time, no pattern-killing processes, no shared
   infrastructure changes without approval, never touching processes it did not start.
4. **Acceptance:** observable truths and the exact commands that prove them.
5. **Report format:** files changed, results with numbers, every deviation with its reason, and
   verified facts kept separate from inferences.

A cross-check brief adds: the original task brief, the produced diff or document (paths), the
acceptance criteria, and the instruction to report findings ranked by severity, each with
file:line evidence and "confirmed" or "suspected", to state what it could not inspect, and to say
plainly when it finds nothing.

## Budget-aware routing

Plan quota is a routing input, after fit. At the start of an orchestration, and before any launch
that will burn a lot of tokens, run the companion script and read its `advice`:

```bash
~/.claude/skills/orchestration/scripts/usage --text
```

It reports each vendor's windows (percent used, reset time, pace against elapsed time) and a
level per vendor: green, yellow, red, or unknown. Rules, in full in `USAGE.md` next to this file:

- Both green: route by the fit table alone.
- One vendor yellow: where the table lists both vendors as suitable, pick the greener vendor's
  model. High-consequence rows keep their first choice.
- One vendor red: no new work on it; where only that vendor fits, ask the user instead of
  routing down to a model the table forbids.
- Cross-checks are never skipped for budget; use the cheapest checker the cross-check table
  allows on the constrained vendor.
- Both red, or quota unknown for both: stop launching and report the snapshot and reset times.

In the Claude desktop app, `mcp__ccd_session_mgmt__get_usage` gives the Claude half directly; the
script is the only source for Codex.

## Orchestrator duties that stay with you

- Decide, sequence and record. Keep heavy jobs (builds, test suites, benchmarks) to one at a time
  across all agents.
- Review every diff yourself, in addition to the cross-check.
- Never report a subagent's claim as fact without checking it against the artefact (diff, log,
  trace). Never predict a running agent's result.
- Record in the project's system of record (here: Noriq) which model did the work, which model
  checked it, and the outcome (accepted, fixed, or unverified), plus the usage `advice` line that
  was in force when the routing was chosen.
