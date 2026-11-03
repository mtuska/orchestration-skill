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

**Read the vendor's file before launching one of its models**: each says what the model can and
cannot do here (Gemini cannot run commands; Cursor reports success when a command was refused),
the exact launch command, and how to read the result. `BENCHMARKS.md` holds the evidence behind
the tables below; read it when a routing choice is close or contested.

## Before routing: read the quota

At the start of an orchestration, and before any launch that will burn a lot of tokens, run:

```bash
~/.claude/skills/orchestration/scripts/usage --text
```

It gives each vendor a level (green, yellow, red, unknown) and an `advice` line. Cursor's quota
cannot be read and is always unknown. Fit decides first; the levels decide among the fits:

- All green: route by the tables alone.
- A vendor yellow or unknown: where a row lists several vendors as suitable, pick the greenest
  (`prefer` names it, or several joined with `+`). High-consequence rows keep their first choice.
- A vendor red: no new work on it; use another the tables allow, including the cross-check
  alternatives. Where only that vendor fits, ask the user instead of routing down to a model the
  table forbids.
- Cross-checks are never skipped for budget; use the cheapest checker the table allows, on the
  greenest permitted vendor.
- All red: stop launching and report the snapshot and reset times.
- If the script could not read a vendor, say so in the record.

Details, thresholds and account shapes: `USAGE.md`.

## Which model for which task

Judgement informed by `BENCHMARKS.md`, not proven by it. Route by the hardest and most
consequential part of the task, not its length.

| Task kind | First choice | Also suitable | Notes |
|---|---|---|---|
| Architecture, design, plans that set direction | Fable 5.1 | Astra, Opus 5.5, Argon | High consequence; spend on the strongest model |
| Hard root cause, ambiguous bugs, concurrency, persistence, lifecycle ordering | Opus 5.5 or Fable 5.1 | Astra | Do not route these down because the diff is small. Not Gemini or Cursor as the worker: diagnosis needs to run things |
| Security review, auth, input validation, anything security-sensitive (even small diffs) | Astra | Argon, Opus 5.5 / Fable 5.1 | Never Haiku, Luna, Flash or a Cursor model |
| Migration, rollback, data conversion, schema/wire changes | Opus 5.5 | Astra | Requires a rehearsal or test plan |
| Complex implementation, large refactors | Opus 5.5 | Sol, Argon | Argon only where someone else runs the build and tests afterwards |
| Routine implementation, local fixes | Sonnet 5.5 | Sol, Grok 4.7 | Grok only where someone else runs the build and tests afterwards |
| Terminal-heavy runs: builds, test suites, benchmark runs, collecting results | Sonnet 5.5 | Sol | Sonnet leads Terminal-Bench 4.0. Never Gemini or Cursor unless the user has allowed the commands in that tool |
| Reading very long inputs: whole subsystems, long logs or traces, cross-file consistency | Argon | Astra, Opus 5.5 | Argon leads GraphWalks 256K-1M; give it paths and a precise question |
| Experiment design, statistics, interpreting benchmark or A/B results, causal claims | Opus 5.5 | Astra | Not arithmetic; needs reasoning about noise and confounds |
| UI and visual QA that drives the app (clicks, screenshots, layout) | Sonnet 5.5 or Opus 5.5 | Sol | Requires the tools to see the UI; say if they cannot |
| Reading static images, charts, video or scanned documents | Argon | Opus 5.5, Sonnet 5.5 | Argon leads no-tools chart and video reading; Claude with tools is stronger on charts |
| Extracting fields from documents into structure | Sol | Luna, Flash | Sol and Luna lead ExtractBench |
| Mechanical: extracting numbers from logs, file inventories, renames, simple summaries | Haiku 5.5 | Luna, Flash, Composer 2.5 | Only when the task truly has no judgement in it. Flash and Composer only on files they can read, never for commands |
| Research and source lookup | Sonnet 5.5 | Sol | Require cited primary sources and versions. Not Grok: it handles untrusted content badly |
| Adversarial review of a finished change | See the cross-check table | | |

Effort: for high-consequence work use the model's high or xhigh effort (Gemini and Grok: the
`-high` or `-xhigh` model ID); for mechanical work the default is enough.

## Who checks what

The checker is always a different vendor from the worker. The first choice is listed first; use
the alternatives in order when the first vendor is red, unavailable, or the row says it fits better.

| Work done by | Kind of work | Cross-check with | Alternatives |
|---|---|---|---|
| Claude | Code, fixes | Codex Sol; Astra if security, concurrency, persistence, migration or wide impact | Gemini Argon; Grok 4.7 for small, low-risk local diffs |
| Claude | Plan, design, architecture, diagnosis | Codex Astra | Gemini Argon |
| Claude | Long-input or cross-file consistency claims, image or video reading | Gemini Argon | Codex Astra |
| Claude | Measurement or run report (numbers only) | Codex Luna re-derives the numbers from the raw logs | Gemini Flash or Composer 2.5, reading the log files |
| Claude | Analysis or interpretation of results | Codex Astra | Gemini Argon |
| Codex | Code, fixes | Claude Opus 5.5 (Sonnet 5.5 for small, low-risk local diffs; never for security-sensitive ones) | Gemini Argon; Grok 4.7 for small, low-risk local diffs |
| Codex | Plan, design, architecture, diagnosis | Claude Fable 5.1 or Opus 5.5 | Gemini Argon |
| Codex | Measurement or run report (numbers only) | Claude Haiku 5.5 or Sonnet 5.5 re-derive the numbers | Gemini Flash or Composer 2.5 |
| Codex | Analysis or interpretation of results | Claude Opus 5.5 | Gemini Argon |
| Gemini | Code, fixes | Claude Opus 5.5, which also runs the build and tests Gemini could not | Codex Sol (Astra if security-sensitive) |
| Gemini | Plan, design, architecture, diagnosis, long-input reading | Claude Fable 5.1 or Opus 5.5 | Codex Astra |
| Gemini | Measurement or extraction (numbers only) | Claude Haiku 5.5 | Codex Luna; Composer 2.5 |
| Gemini | Analysis or interpretation of results | Claude Opus 5.5 | Codex Astra |
| Cursor | Code, fixes | Claude Sonnet 5.5 (Opus 5.5 if the change is not small), which also runs the build and tests | Codex Sol; Gemini Argon |
| Cursor | Measurement or extraction (numbers only) | Claude Haiku 5.5 | Codex Luna; Gemini Flash |
| Cursor | Anything else | Claude Opus 5.5 | Codex Astra; Gemini Argon |

Gemini as checker: Argon only, except Flash for re-deriving numbers from files. Cursor as checker:
Grok 4.7 only for small, low-risk local diffs, Composer 2.5 only for re-deriving numbers; never for
plans, designs, diagnoses, security or anything with wide impact. A Gemini or Cursor check that
needed to run something (a test, a repro) cannot run it; the checker must say so, and that part
stays unverified until another vendor or you run it.

Proportionality: every substantive change, plan or conclusion gets one check. A pure data run
(build, benchmark run) is not repeated; its interpretation is checked from the raw logs.
Checkers are read-only and never edit; for Gemini and Cursor, check the workspace is unchanged
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
plainly when it finds nothing. A Gemini or Cursor brief also says what it must not run and that it
must not edit, and asks for the answer on its own line.

## Orchestrator duties that stay with you

- Decide, sequence and record. Keep heavy jobs (builds, test suites, benchmarks) to one at a time
  across all agents.
- Review every diff yourself, in addition to the cross-check.
- Never report a subagent's claim as fact without checking it against the artefact (diff, log,
  trace). Never predict a running agent's result.
- Record in the project's system of record (here: Noriq) which model did the work, which model
  checked it, and the outcome (accepted, fixed, or unverified), plus the usage `advice` line that
  was in force when the routing was chosen.
