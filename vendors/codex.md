# Codex (OpenAI)

Models: GPT-6 Astra, GPT-6 Sol, GPT-6 Luna. Scores and prices are in `../BENCHMARKS.md`.

## What it can do in this harness

Reads, edits, builds and tests inside the sandbox you give it. The sandbox is enforced by the CLI,
so `-s read-only` really is read-only.

## How to launch

The CLI, run through the shell tool's own background facility (the command itself does not
background anything or notify you; the harness does):

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

## Quota

`scripts/usage` reads Codex's rate limits through `codex app-server` (`USAGE.md`). A red Codex
account may still have a credits balance and free limit resets; spending either is the user's
call.
