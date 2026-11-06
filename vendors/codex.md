# Codex (OpenAI)

Models: GPT-6 Astra, GPT-6 Sol, GPT-6 Luna. Scores and prices are in `../BENCHMARKS.md`.

## What it can do in this harness

Reads, edits, builds and tests inside the sandbox you give it. The sandbox is enforced by the CLI,
so `-s read-only` constrains filesystem writes. Workspace-write does not by itself establish
network access. Prefer `.codex/config.toml` for stable project defaults and select the role with
`-s`; see [project permissions](../PROJECT-SETUP.md#codex).

## How to launch

The CLI, run through the shell tool's own background facility (the command itself does not
background anything or notify you; the harness does):

```bash
codex exec --skip-git-repo-check -m gpt-6-sol -s workspace-write -C <workdir> -o <task-dir>/last-message.md "$(cat <task-dir>/prompt.md)" < /dev/null > <task-dir>/run.log 2>&1; echo "codex exit $?"
```

- `-m gpt-6-astra | gpt-6-sol | gpt-6-luna`.
- Project configuration is loaded only for trusted projects; verify it was applied. The parent
  may add the exact current project trust entry to Codex's user config under the
  [trust exception](../PROJECT-SETUP.md#codex-project-trust-exception); do not broaden global permissions.
- Sandbox, least access first: `-s read-only` for reviews and diagnosis; `-s workspace-write` for
  edits, builds and tests, adding `--add-dir <dir>` for each extra directory it must write;
  `-s danger-full-access` only when the task requires it and existing user authorization covers it.
  A sandbox failure alone is not authorization to widen access.
- `--skip-git-repo-check` is needed outside Git repositories. `< /dev/null` stops the CLI waiting
  for stdin in a non-interactive shell (stdin can otherwise be used to pass the prompt).
- Use a unique `<task-dir>` per task. Before accepting the report, check the exit status and that
  `last-message.md` was written by this run (timestamp after launch), then read it.

## Streamed progress and follow-up (tested 2026-11-06)

Add `--json` to `codex exec` and write stdout to an event log, stderr separately. Capture
`thread_id` from `thread.started`. Read `item.completed` entries whose `item.type` is
`agent_message` for progress; command items provide execution status. Require `turn.completed`
and successful process termination; inspect error events rather than trusting an exit code alone.

For a completed read-only worker, the tested resume form is:

```bash
codex -a never -s read-only -C <workdir> exec resume <thread_id> --skip-git-repo-check -m gpt-6-luna --json - < <task-dir>/followup.txt > <task-dir>/followup.jsonl 2> <task-dir>/followup.stderr
```

The test passed prompt text as the final argument; `-` is the CLI-supported stdin equivalent.
Keep sandbox, approval policy, workspace and model explicit as above; choose actual values from
the assignment. Luna produced intermediate progress, retained its thread ID and recalled the
marker without rereading it. The resumed write probe reported sandbox rejection; no canary was
created. This tests the specified launch configuration, not implicit permission inheritance.

### Resume network and writable roots

User-reported probe (2026-11-06): a Luna thread started in a trusted workspace could bind a UDP
socket, but resuming it failed with `PermissionError` in two launch forms. Explicit network
configuration on resume resolved the reported issue. This is evidence not to rely on project
sandbox-setting inheritance during resume, not proof that every Codex version drops those settings.

Reuse an appropriate completed thread. For workspace-write workers, repeat the authorized network
setting and complete extra writable-root list explicitly on **every resume**, taking their values
from the project's approved `.codex/config.toml` and worker record. Keep the project file as the
source of truth; these launch overrides reproduce it, rather than granting additional access.
For example, for a task that already needs network and the illustrated extra output directory:

```bash
codex -a never -s workspace-write -C /absolute/project \
  -c 'sandbox_workspace_write.network_access=true' \
  -c 'sandbox_workspace_write.writable_roots=["/absolute/build-output"]' \
  exec resume <thread_id> --skip-git-repo-check -m <selected-model> --json - \
  < <task-dir>/followup.txt > <task-dir>/followup.jsonl 2> <task-dir>/followup.stderr
```

Substitute actual approved paths; use `false` for offline tasks and `[]` when no extra writable
roots are needed. Do not copy this workspace-write example into a read-only reviewer launch.
After resume, repeat the minimal required socket/output-write probe inside the worker's execution
environment before starting expensive tests. Check errors and effective access, not just accepted
CLI syntax. If the explicit settings still fail, diagnose host restrictions or run the check in
the parent's authorized environment. Do not discard useful context and start a new thread solely
as a permissions workaround. This workaround has not been independently rerun by this skill update.

`codex queue` is separate from live steering; `--resume` can warn while still exiting zero.
App-server `turn/steer` requires the active thread/turn on the owning server. Do not assume a new
app-server controls an existing `exec` worker. Neither path is runtime-validated here.

## Quota

`scripts/usage` reads Codex's rate limits through `codex app-server` (`USAGE.md`). A red Codex
account may still have a credits balance and free limit resets; spending either is the user's
call.
