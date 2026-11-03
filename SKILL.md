---
name: orchestration
description: Route work to the best-fit model and cross-check it with a different vendor. Use whenever you act as orchestrator and hand work to subagents: implementation, debugging, planning, design, reviews, research, analysis, benchmark or test runs. Covers which model fits which task (Claude Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5; Codex GPT-6 Astra, Sol, Luna; Gemini 4 Argon and 3.8 Flash through the Antigravity CLI; Cursor's Grok 4.7 and Composer 2.5 through cursor-agent), how to brief and launch each, and the rule that work produced by one vendor is checked once by another before it is accepted.
---

# Orchestration: route by fit, cross-check across vendors

You are the orchestrator. You decide, brief, review and record; subagents do the work. Two rules:

1. **Route each task to the best-fit model**, using the tables below. Fit means quality for that
   kind of work, what the model can actually do in this harness, and the consequence of getting it
   wrong first, then cost and speed.
2. **Cross-check across vendors, once.** Anything one vendor produced (code, plan, design,
   diagnosis, analysis) is checked by a model of a different vendor before you accept it. The
   checker is never the same family. One independent check plus your own adjudication completes
   the cycle: the checker's report is not itself re-checked. If a fix is needed, the fix is new
   work and gets its own single check.

You own the result: verify each finding against the source before acting on it, and decide. A
cross-check is evidence, not a verdict. If no other vendor is available, or the checker could not
inspect the evidence (tool failure, missing access, denied action), the work is **unverified**:
say so and do not treat it as accepted.

## The four vendors and where to read about each

| Vendor | Models used | Runs through | Details |
|---|---|---|---|
| Claude (Anthropic) | Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5 | Agent tool | `vendors/claude.md` |
| Codex (OpenAI) | GPT-6 Astra, Sol, Luna | `codex exec` | `vendors/codex.md` |
| Gemini (Google) | Gemini 4 Argon, Gemini 3.8 Flash | `agy` via the cc-gemini-plugin bridge | `vendors/gemini.md` |
| Cursor (xAI) | Grok 4.7, Grok 4.6, Composer 2.5 | `cursor-agent` | `vendors/cursor.md` |

Vendor is the model's maker, not the tool that runs it. `agy` and Cursor also serve other makers'
models; use each tool only for its own vendor's models, and never count a run of another maker's
model through them as a check by that tool's vendor.

**Every vendor can do every kind of work** (read, review, plan, edit, implement, run things) and
can check any other vendor's work. They differ in how well, which is what the rankings below and
`BENCHMARKS.md` are for, and in what their tool needs set up first. **Read the vendor's file before
launching one of its models**: it gives the launch command, how to read the result, and the setup
facts (Gemini and Cursor run only the commands their allowlists permit; Cursor reports success
even when a command was refused). `BENCHMARKS.md` holds the evidence behind the rankings; read it
when a choice is close or contested.

## Before routing: read the quota

At the start of an orchestration, and before any launch that will burn a lot of tokens, run:

```bash
~/.claude/skills/orchestration/scripts/usage --text
```

It gives each vendor a level (green, yellow, red, unknown) and an `advice` line. Cursor's quota
cannot be read and is always unknown. Fit decides first; the levels decide how far down a ranking
to go:

- All green: take the first model in the row.
- A vendor yellow or unknown: where its model and a greener vendor's are close in the row (next to
  each other, or the row says they are close), take the greener one (`prefer` names it, or several
  joined with `+`). High-consequence rows keep their first choice unless it is red.
- A vendor red: no new work on it; take the next model in the row from another vendor. When that
  means a clearly weaker model for high-consequence work, say so in the record, and ask the user
  if the gap is large.
- Cross-checks are never skipped for budget; take the next checker in the row on a greener vendor.
- All red: stop launching and report the snapshot and reset times.
- If the script could not read a vendor, say so in the record.

Details, thresholds and account shapes: `USAGE.md`.

## Which model for which task

Judgement informed by `BENCHMARKS.md`, not proven by it. Each row ranks the best model of every
vendor for that kind of work, best first; a later model is a fallback, not a forbidden choice.
Route by the hardest and most consequential part of the task, not its length.

| Task kind | Ranked fit, best first | Notes |
|---|---|---|
| Architecture, design, plans that set direction | Fable 5.1 (or Opus 5.5), Astra, Argon, Grok 4.7 | High consequence; spend on the strongest model available |
| Hard root cause, ambiguous bugs, concurrency, persistence, lifecycle ordering | Opus 5.5 or Fable 5.1, Astra, Argon, Grok 4.7 | Do not route these down because the diff is small. Diagnosis usually runs repros: with Gemini or Cursor, allow the commands or have another agent run them |
| Security review, auth, input validation, anything security-sensitive (even small diffs) | Astra, Argon, Opus 5.5 or Fable 5.1, Grok 4.7 | Astra and Argon lead SEC-Bench Pro and ExploitGym. Use a vendor's strongest model here, not its small one |
| Migration, rollback, data conversion, schema/wire changes | Opus 5.5, Astra, Argon, Grok 4.7 | Requires a rehearsal or test plan |
| Complex implementation, large refactors | Opus 5.5, Astra or Sol, Argon, Grok 4.7 | Argon leads DeepSWE. Whoever cannot run the build and tests hands them to the checker |
| Routine implementation, local fixes | Sonnet 5.5, Sol, Argon, Grok 4.7 or Composer 2.5 | Same note on builds and tests |
| Terminal-heavy runs: builds, test suites, benchmark runs, collecting results | Sonnet 5.5, Sol or Astra, Argon, Grok 4.7 | Sonnet leads Terminal-Bench 4.0 (70.6); Astra 57.9, Argon 57.4, Grok 4.7 38.0. Gemini and Cursor need the commands on their allowlists first |
| Reading very long inputs: whole subsystems, long logs or traces, cross-file consistency | Argon, Astra, Opus 5.5, Grok 4.7 | Argon leads GraphWalks 256K-1M; give it paths and a precise question. Grok's window is 500K |
| Experiment design, statistics, interpreting benchmark or A/B results, causal claims | Opus 5.5, Astra, Argon, Grok 4.7 | Not arithmetic; needs reasoning about noise and confounds |
| UI and visual QA that drives the app (clicks, screenshots, layout) | Sonnet 5.5 or Opus 5.5, Astra, Argon, Grok 4.7 | Requires the tools to see the UI; say if they cannot. No computer-use score for Grok |
| Reading static images, charts, video or scanned documents | Argon, Opus 5.5 or Sonnet 5.5, Astra, Grok 4.7 | Argon leads no-tools chart and video reading; Claude with tools is stronger on charts. No vision score for Grok |
| Extracting fields from documents into structure | Sol or Luna, Opus 5.5, Flash, Composer 2.5 | Sol and Luna lead ExtractBench |
| Mechanical: extracting numbers from logs, file inventories, renames, simple summaries | Haiku 5.5, Luna, Flash, Composer 2.5 | Use the small models only when the task truly has no judgement in it |
| Research and source lookup | Sonnet 5.5, Sol, Argon, Grok 4.7 | Require cited primary sources and versions. Grok 4.6's prompt-injection score is weak (`BENCHMARKS.md`); check what Grok read |
| Adversarial review of a finished change | See the cross-check table | |

Effort: for high-consequence work use the model's high or xhigh effort (Gemini and Grok: the
`-high` or `-xhigh` model ID); for mechanical work the default is enough.

## Who checks what

The checker is always a different vendor from the worker. Each row ranks the other three vendors'
best checker for that kind of work, best first; take the first that is not red.

| Work done by | Kind of work | Checkers, best first |
|---|---|---|
| Claude | Code, fixes | Codex Sol (Astra if security, concurrency, persistence, migration or wide impact), Gemini Argon, Cursor Grok 4.7 |
| Claude | Plan, design, architecture, diagnosis, analysis of results | Codex Astra, Gemini Argon, Cursor Grok 4.7 |
| Claude | Long-input or cross-file consistency claims, image or video reading | Gemini Argon, Codex Astra, Cursor Grok 4.7 |
| Claude | Measurement or run report (numbers only) | Codex Luna, Gemini Flash, Cursor Composer 2.5, each re-deriving the numbers from the raw logs |
| Codex | Code, fixes | Claude Opus 5.5 (Sonnet 5.5 for small, low-risk local diffs), Gemini Argon, Cursor Grok 4.7 |
| Codex | Plan, design, architecture, diagnosis, analysis of results | Claude Fable 5.1 or Opus 5.5, Gemini Argon, Cursor Grok 4.7 |
| Codex | Measurement or run report (numbers only) | Claude Haiku 5.5, Gemini Flash, Cursor Composer 2.5 |
| Gemini | Code, fixes | Claude Opus 5.5, Codex Sol (Astra if security-sensitive), Cursor Grok 4.7 |
| Gemini | Plan, design, architecture, diagnosis, long-input reading, analysis | Claude Fable 5.1 or Opus 5.5, Codex Astra, Cursor Grok 4.7 |
| Gemini | Measurement or extraction (numbers only) | Claude Haiku 5.5, Codex Luna, Cursor Composer 2.5 |
| Cursor | Code, fixes | Claude Sonnet 5.5 (Opus 5.5 if the change is not small), Codex Sol, Gemini Argon |
| Cursor | Plan, design, architecture, diagnosis, analysis | Claude Opus 5.5, Codex Astra, Gemini Argon |
| Cursor | Measurement or extraction (numbers only) | Claude Haiku 5.5, Codex Luna, Gemini Flash |

For security-sensitive or high-impact work, use the checker vendor's strongest model (Astra, Opus
5.5 or Fable 5.1, Argon, Grok 4.7 xhigh), not its small one. A check that needs to run something (a
test, a repro) needs the commands allowed for that checker; if they are not, the checker says what
it could not run, and that part stays unverified until it is run by someone.

Proportionality: every substantive change, plan or conclusion gets one check. A pure data run
(build, benchmark run) is not repeated; its interpretation is checked from the raw logs.
A checker does not edit the work it checks; launch it read-only where the tool allows (Codex
`-s read-only`, Cursor `--mode ask`), and for Gemini and Cursor confirm the workspace is unchanged
after the run (the vendor files say how).

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
plainly when it finds nothing. A Gemini or Cursor brief also says which commands it may run (only
those on its allowlist will work), and asks for the answer on its own line.

## Orchestrator duties that stay with you

- Decide, sequence and record. Keep heavy jobs (builds, test suites, benchmarks) to one at a time
  across all agents.
- Review every diff yourself, in addition to the cross-check.
- Never report a subagent's claim as fact without checking it against the artefact (diff, log,
  trace). Never predict a running agent's result.
- Record in the project's system of record (here: Noriq) which model did the work, which model
  checked it, and the outcome (accepted, fixed, or unverified), plus the usage `advice` line that
  was in force when the routing was chosen.
