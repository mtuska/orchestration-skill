---
name: orchestration
description: Choose economical models for delegated work, check quota before each launch, write scoped briefs, and verify results in proportion to risk. Use when choosing and coordinating subagents; ordinary serial work stays in the main session.
---

# Orchestration

Use the least expensive model that can reliably meet the task's requirements in the available
harness. Preserve premium capacity for difficult decisions, uncertainty and consequential errors.
Green quota means capacity is available; it is not a reason to choose the strongest model.

## Before launching

The main session selects the model and effort using this skill and the current usage snapshot.
Launch with the host subagent tool or the vendor CLI documented below.

Do ordinary serial investigation, edits and verification in the main session. Delegate when an
independent assignment benefits from parallelism, context isolation, specialist tools or quota
offloading. Do not create a worker for a trivial command. Workers do not delegate further.

Before **every new worker or reviewer launch**, including a replacement after failure, call:

```bash
~/.claude/skills/orchestration/scripts/usage --text
```

A batch may share one immediately preceding usage call. Read the snapshot before choosing the
model; the script is quota evidence, not a task classifier. See [USAGE.md](USAGE.md) for freshness
and failure handling.

Read the selected vendor's launch and result-collection instructions before dispatch:
[Claude](vendors/claude.md), [Codex](vendors/codex.md), [Gemini](vendors/gemini.md),
[Cursor](vendors/cursor.md). Use only model IDs actually supported by the host or CLI.
Check required paths, services, commands and network access before launch. Preserve read-only
roles and existing authorization. A failed tool call does not authorize broader permissions.
See [PROJECT-SETUP.md](PROJECT-SETUP.md) when a vendor needs project command permissions.

## Choose by the decisions still needed

You own model and effort selection. Choose using the task's unresolved decisions, consequences
of error, required tools, acceptance checks, current quota and reset timing, benchmark evidence,
and observed outcomes. Choose an economical model likely to succeed, considering retries, review
and repair costs. Do not equate API prices with subscription-quota consumption.

Model lists and benchmark rankings are references, not defaults or mandatory ladders. Spending
more requires a concrete benefit for this assignment; choosing cheaply must still meet its
requirements. Briefly record why the choice fits and reconsider when actual results contradict it.

Use these considerations to exercise judgment, not as automatic escalation triggers:

| Assignment | Considerations |
|---|---|
| Extraction, inventories, narrow lookup, simple summaries | Are sources clear and results directly checkable, or is interpretation needed? |
| Prescribed builds/tests and result collection | Can direct tools handle it? Separate execution from diagnosing unexpected failures. |
| Local implementation and directed verification | Is behavior settled, scope limited, and verification adequate? |
| Implementation, debugging, review and synthesis | How much ambiguity, cross-system context and independent reasoning remain? |
| Architecture, security, concurrency, persistence and migrations | What are the consequences of a wrong decision, and what evidence or expertise is needed? |

Confirm actual model IDs and supported effort settings in the selected host or CLI.
[BENCHMARKS.md](BENCHMARKS.md) provides provisional evidence, not a routing order. Account for
conflicting results and differences in revisions, effort, harnesses and tools; do not infer
suitability from one score or treat a prior successful choice as a permanent default.

Small models may exercise limited judgment when requirements are clear, scope is limited, errors
are recoverable and results can be checked. Do not require "no judgment". A short diff can still
require strong reasoning. A long run of prescribed commands need not.

Separate making a decision from executing an agreed decision when they produce useful independent
assignments. Do not fragment tightly coupled work merely to obtain a cheaper tier. A premium-model
selection needs a concrete reason such as unresolved ownership semantics, not "best quality".
Effort is a separate choice: use default or low effort for prescribed work, increasing it for
reasoning the assignment actually requires. Do not automatically choose maximum effort.

## Quota and escalation

`usage-policy.json` is the user's editable per-vendor policy, applied on every usage run even
with cached measurements. Use `routing_level` and policy notes for shared-account eligibility;
`level` preserves the measured quota warning. `ignore_pace` bypasses pace restrictions, `prefer`
favors suitable models on that vendor, and `allow_credits` authorizes existing credits only.
Credit-based continuation currently requires Codex's positive credit balance and affirmative
service availability. Other vendors retain exhaustion checks until their credit availability is
verified. `reserve_percent` reduces available headroom by that many percentage points (0–100), for any
vendor; Claude currently reserves 10. Missing reserves default to 0 and switches to false.
Edit `usage-policy.json` or use `--policy <path>`.
These options never authorize purchases, spending-limit increases or reset-credit redemption.

- Inspect shared and model-specific limits. A red model bucket excludes its affected models, not
  every model on that account. A red shared routing level excludes all models drawing from it.
- Prefer healthy capacity among suitable candidates; do not automatically upgrade to a premium
  model on another provider when an economical model remains eligible.
- Unknown or stale quota is uncertainty, not free capacity. Prefer a suitable measured account;
  if none exists, record the uncertainty and use a bounded assignment without blind retries.
- If every eligible account is red, stop new launches and report reset times. Do not spend extra
  credits or reset credits without the user's authorization.
- After a quota rejection, refresh the affected provider with `--vendor <name> --no-cache`, then
  reroute. Do not resubmit an unchanged blocked assignment.
- When a worker discovers unresolved semantics, conflicting requirements or failed acceptance
  checks it cannot resolve within scope, it returns evidence and the exact decision needed.
  Continue the existing worker for a concrete correction; reroute reasoning when necessary.
  Do not repeatedly retry the same approach or jump to the strongest model without a reason.

## Verification proportional to consequences

Every result needs evidence. Mechanical transformations and prescribed runs may be accepted using
deterministic checks and parent inspection of the artifacts; they do not require a second model.
A run is not repeated solely to verify its report. Check numbers against its raw output.

Use one independent, different-vendor review for consequential changes, ambiguous conclusions,
architecture/security decisions and broad-impact work, or whenever the project/user requires it.
Explicitly select a checker from a different model maker. Vendor means the model's maker,
not the hosting CLI; do not use an auto-selected model for an independent check.
A narrow check against explicit acceptance criteria may use an economical checker. Broad searches
for unknown defects need stronger reasoning. Judge the check's scope, not just the worker's tier.

The checker is read-only. It reports confirmed versus suspected findings with source evidence,
what it could not inspect, and plainly when it finds nothing. Its report is not itself re-reviewed.
After a fix, rerun affected checks and obtain targeted independent review when the changed behavior
remains consequential. Do not restart a full review cycle for a mechanical correction.

The parent adjudicates findings against actual evidence. A required independent review that cannot
run remains incomplete; report that limitation rather than calling the work accepted.

## Progress and follow-ups

For all four vendors, use the tested event-stream and explicit-session follow-up paths in the
vendor files. Gemini read-only launches require its explicit deny profile on every turn; plan
mode alone does not prevent writes.

Keep a small worker record: vendor, model/effort, explicit session ID, workspace, access settings,
process handle/PID, raw event log, stderr, final result and last consumed log offset. Never address
"the most recent" session. Give only one process ownership of a worker's active turn.

Ask for a short update at start, meaningful milestones, blockers and completion: completed work,
new finding, next step, blocker. During long work, request updates between steps when practical;
do not promise clock-timed model output during blocking tool calls. Native workers use the host's
parent-message channel with completion notifications enabled. CLI workers emit updates to stdout;
the parent must collect the stream, not just the final response.

Read only newly appended complete events, retaining partial lines until complete. Extract concise
assistant messages, tool status, errors and final results; do not repeatedly load raw transcripts
or private reasoning. Preserve complete logs on disk. Check process state and log activity during
long commands without sending model status prompts. Activity is not proof of task progress.

After a turn finishes, reuse its explicit session ID for a related correction. Run the cached
usage check before every resumed CLI launch too. Repeat the workspace, model and access settings;
do not assume resume inherits them. Preserve the model unless changed scope or quota warrants
reconsideration. Start a new session with a concise handoff when scope changes substantially or
accumulated context becomes wasteful. A context handoff must preserve unresolved work and evidence.

Distinguish follow-up after completion, queued input, live steering, and interrupt-then-redirect.
Do not start a duplicate resume against a running session. Treat submission, acknowledgment and
completion as separate facts where exposed; verify the returned session ID and relevant response.
Exit zero alone is not delivery or acceptance. Live steering and ACP cancellation remain untested
here; do not use them as the default or claim they worked based on CLI help alone.

## Brief and record

Each assignment has one deliverable, its dependencies, settled behavior, unresolved decisions,
exact scope, relevant project rules, required access and observable acceptance checks. Give paths
and focused context instead of copying the whole conversation. Include the worker's escalation
boundary. A review brief adds the original requirements, resulting artifacts and review scope.

Record the chosen model/effort and concrete reason, quota observation time, worker and checker
results, retries/escalations, parent repairs, and total reported usage per accepted result.
Keep missing usage marked unknown; do not invent token counts or infer subscription charges from
API prices. Use the project's existing authorized record or local task artifact; this skill does
not mandate Noriq updates. Compare acceptance rate, repair work, total usage and elapsed time when
adjusting defaults. Cheap first attempts are useful only when total accepted-result cost improves.

Keep heavy jobs to one at a time where project rules require it. Before ending, every process you
started must be finished, killed, or explicitly handed to the user with its PID and purpose.
