# Cursor (xAI), through `cursor-agent`

Models: Grok 4.7 and Grok 4.6 (xAI) and Composer 2.5 (Cursor). xAI owns Cursor, so all three are
this vendor's own models. Scores and prices are in `../BENCHMARKS.md`.

Cursor also serves Claude, GPT, Gemini and other makers' models, and its `auto` model can pick any
of them. **Use only the explicit Grok or Composer model IDs below.** Never run
Claude, GPT or Gemini through Cursor, and never count such a run as a Cursor check.

Call the CLI as `cursor-agent`. On this machine `agent` on the PATH is Grok's own CLI
(`~/.grok/bin/agent`), not Cursor's.

## What it can do in this harness

Every kind of work: reading, review, planning, editing and implementation. Setup facts:

- **Read-only is enforced by mode.** `--mode ask` (questions, read-only) and `--mode plan`
  (planning, no edits) are the CLI's read-only modes. Seen on 2026-11-02: both Grok 4.7 and
  Composer 2.5 answered a file question correctly in `ask` mode with the workspace unchanged.
- **Edits work in the default mode.** Without `--mode`, print mode (`-p`) has write and shell tools.
- **Commands run only if allowed.** A command no allow rule covers is rejected (the global
  `~/.cursor/cli-config.json` allowed only `Shell(ls)` on 2026-11-02). Give the project its own
  rules first in `<workdir>/.cursor/cli.json` (`../PROJECT-SETUP.md`), which the CLI reads from the
  workspace root; then Cursor builds, tests and runs repros like the other vendors. Never edit the
  global config, and never use `--force` / `--yolo`, which runs every command.
- **A rejected command still reports success.** Seen on 2026-11-02: asked to run `wc -l`, the
  command was rejected, the run ended `is_error: false` with exit 0, and the model wrote what the
  output "would" be. Never accept a command result from Cursor without the log line that shows it
  ran; treat it as unverified otherwise.
- **Prompt injection:** Grok 4.6's Gray Swan score is weak (`../BENCHMARKS.md`). When Grok works on
  untrusted content (web pages, outside issue text or logs), have its result checked with that in
  mind.

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

## Streamed progress and follow-up (tested 2026-11-06)

For progress, replace `--output-format json` with `--output-format stream-json` in the launch
command and use an `.jsonl` event log. Capture `session_id` from the initialization/final events.
Read assistant text from `assistant.message.content[]`, tool activity from `tool_call` events,
and final status from `result`. Do not append a second copy of final text already streamed.

After the process finishes, use the same command with `--resume <session_id>` and a new prompt
and log paths. Repeat `--model`, `--mode ask` (for a read-only assignment), `--trust`, and
`--workspace`; preserve any additional access settings. Never use `--continue` to guess the ID.

Composer 2.5 passed progress, matching session ID and marker recall without rereading. The resumed
write probe refused in Ask mode and left no file. Its init event nevertheless reported
`permissionMode: default`: that field is not proof of Ask-mode enforcement. The observed refusal
is not a filesystem-isolation test. Continue checking workspace changes.

`cursor-agent acp` exposes prompts, updates and cancellation, but it was not runtime-tested here.
Do not call cancel-then-prompt seamless steering, or start a duplicate CLI against an active turn.

## Quota

`cursor-agent` shows plan usage on its interactive `/usage` screen. In print mode, `/usage` is
sent to the model as an ordinary prompt (seen 2026-11-02). `scripts/usage` opens a short-lived
local terminal, reads the interactive screen without a model turn, and reports the included plan
percentage and reset date. The exact reset time is not exposed. The result is cached for 15 minutes;
if the screen cannot be read, the quota is unknown and should be treated as yellow.
