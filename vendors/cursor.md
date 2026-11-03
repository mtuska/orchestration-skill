# Cursor (xAI), through `cursor-agent`

Models: Grok 4.7 and Grok 4.6 (xAI) and Composer 2.5 (Cursor). xAI owns Cursor, so all three are
this vendor's own models. Scores and prices are in `../BENCHMARKS.md`.

Cursor also serves Claude, GPT, Gemini and other makers' models, and its `auto` model can pick any
of them. **Use only the Grok and Composer IDs below, always with an explicit `--model`.** Never run
Claude, GPT or Gemini through Cursor, and never count such a run as a Cursor check.

Call the CLI as `cursor-agent`. On this machine `agent` on the PATH is Grok's own CLI
(`~/.grok/bin/agent`), not Cursor's.

## What it can do in this harness

- **Read-only is enforced by mode.** `--mode ask` (questions, read-only) and `--mode plan`
  (planning, no edits) are the CLI's read-only modes. Seen on 2026-11-02: both Grok 4.7 and
  Composer 2.5 answered a file question correctly in `ask` mode with the workspace unchanged.
- **Commands follow the user's allowlist.** Print mode (`-p`) has write and shell tools, but a
  command not on the allowlist in `~/.cursor/cli-config.json` is rejected (the allowlist there held
  only `Shell(ls)` on 2026-11-02). `--force` / `--yolo` runs every command; do not use it without
  the user's say-so, and do not edit the allowlist.
- **A rejected command still reports success.** Seen on 2026-11-02: asked to run `wc -l`, the
  command was rejected, the run ended `is_error: false` with exit 0, and the model wrote what the
  output "would" be. Never accept a command result from Cursor without the log line that shows it
  ran; treat it as unverified otherwise.
- **Prompt injection:** see the Gray Swan note in `../BENCHMARKS.md`. Do not hand Grok untrusted
  content.

## How to launch

The CLI in print mode, through the shell tool's background facility:

```bash
cursor-agent -p "$(cat <task-dir>/prompt.md)" --model grok-4.7-high --mode ask --trust --workspace <workdir> --output-format json < /dev/null > <task-dir>/result.json 2> <task-dir>/run.log; echo "cursor exit $?"
```

- `--model grok-4.7-low | -medium | -high | -xhigh`, `cursor-grok-4.6-low | -medium | -high | -xhigh`,
  or `composer-2.5` (`composer-2.5-fast` is the faster, dearer variant). `cursor-agent --list-models`
  shows the account's list; take only these from it.
- `--mode ask` for reviews, questions and checks; `--mode plan` for plans; drop `--mode` only for
  work that must edit files, and then say exactly which files it may change.
- `--trust` skips the workspace trust prompt that would otherwise block a headless run.
  `--workspace` is the root it works in; `--add-dir` adds another. `--sandbox enabled` turns on the
  CLI's sandbox (off in this user's config).
- Read the result: exit status 0 and `is_error: false`, then `result` is the answer text. Grok may
  put a sentence of preamble before the answer in `result`, so ask for the answer on its own line.
  `session_id` resumes the conversation with `--resume <id>`; `usage` has token counts.
- For any run, capture `git status --porcelain` and `git diff --stat` (or a checksum list outside
  Git) before launch and compare after, even in `ask` mode.
- If `cursor-agent status` does not say authenticated, ask the user to run `cursor-agent login`.

## Quota

Not readable. `cursor-agent` shows plan usage only on its interactive `/usage` screen; in print mode
`/usage` is sent to the model as an ordinary prompt (seen 2026-11-02). `scripts/usage` reports
Cursor's sign-in and plan and always lists the quota as unknown, so treat Cursor as yellow.
