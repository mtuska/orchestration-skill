# Gemini (Google), through the Antigravity CLI `agy`

Models: Gemini 4 Argon and Gemini 3.8 Flash. Scores and prices are in `../BENCHMARKS.md`.

`agy` also serves Claude Opus 5.5, Claude Sonnet 5.5 and GPT-OSS 120B. Those are Anthropic and
OpenAI models: never use them through `agy`, and never count a run on them as a Gemini check. Use
only `gemini-*` model IDs.

## What it can do in this harness

Every kind of work: reading, review, planning, editing and implementation. Setup facts:

- **Commands run only if allowed.** `agy` in headless mode auto-denies every command that no allow
  rule covers, and the run then fails with `denied_actions`. Seen on 2026-11-02: a question the
  model chose to answer with a command was denied and returned nothing. Give the project its own
  rules first (`../PROJECT-SETUP.md`) and pass them with `--settings`; then Gemini builds, tests
  and runs repros like the other vendors. Never edit the global `settings.json`.
- **Plan mode is not read-only enforcement.** A 2026-11-06 canary test wrote a file even with
  `--mode plan`. The bridge's `accept-edits` mode also permits writes. For read-only work, use the
  explicit deny profile below through the direct CLI, not the bridge. `--sandbox` is a terminal
  restriction, not proof all file tools are isolated. Use a different harness when OS-enforced
  filesystem isolation is required.
- **It reads files itself** from the `--cwd` workspace; give it paths, not pasted content.

## How to launch

Two forms, both run through the shell tool's background facility.

**With commands (builds, tests, repros, any work that runs things):** call `agy` directly, because
the bridge cannot pass `--settings`. Run it from the workspace root:

```bash
cd <workdir> && agy -p "$(cat <task-dir>/prompt.md)" --model gemini-4-argon-high --mode accept-edits --settings <workdir>/.agents/agy-settings.json --output-format json --disable-slash-commands --print-timeout 900s < /dev/null > <task-dir>/result.json 2> <task-dir>/run.log; echo "gemini exit $?"
```

Read `response` for the answer. The run exits 0 even when a command was refused, so also require
`denied_actions` to be absent and `status` to be `SUCCESS`. `conversation_id` resumes the
conversation with `--conversation <id>`, and `usage` has token counts. Seen on 2026-11-02: with an
allow rule for `wc`, `wc -l` ran and its real output came back; without one, the same run exited 0
with an empty `response` and `denied_actions` set.

**Without commands (authorized edits someone else will build):** the `cc-gemini-plugin`
bridge. It passes the task to `agy` over stdin unchanged, fails the run itself on any denied action,
and prints one JSON envelope:

```bash
B=$(ls -d ~/.claude/plugins/cache/cc-gemini-plugin/cc-gemini-plugin/*/skills/gemini-integration/scripts/gemini-bridge.mjs | sort -V | tail -1)
node "$B" --cwd <workdir> --model gemini-4-argon-high --format json --timeout 900 -- "$(cat <task-dir>/prompt.md)" > <task-dir>/result.json 2> <task-dir>/run.log; echo "gemini exit $?"
```

- `--model gemini-4-argon-low | -medium | -high` or `gemini-3.8-flash-low | -medium | -high`; the
  suffix is the effort. `agy models` lists what the account offers; re-check it when routing to a
  model not seen before.
- `--cwd` is the workspace it reads and may write. `--timeout` defaults to 600 seconds; raise it for
  long reads. `--sandbox` turns on `agy`'s terminal sandbox, which does not confine file edits.
- Read the result: exit status 0 and `ok: true` are both required (`agy` can report `SUCCESS`
  after denying an action). The answer is `result.response`; `result.denied_actions` names what
  was refused; `result.conversation_id` resumes the same conversation with `--conversation <id>`;
  `result.usage` has token counts. `error` explains a failure.
- For read-only work, capture `git status --porcelain` and `git diff --stat` (or a checksum list
  outside Git) before launch and compare after. Any change made by a checker fails the check;
  report it, do not keep it.
- Say in the brief exactly which commands it may run (those in the project's allow rules). A
  command that is not allowed fails the whole run. With the bridge, which allows none, ask it to
  edit and read only and say who will build and test.
- The plugin also provides the Agent tool type `cc-gemini-plugin:gemini-agent` (a Claude wrapper
  with Bash, Glob and Read that runs the same bridge) and the `/cc-gemini-plugin:gemini` command.
  The wrapper works (smoke test 2026-11-02: exit 0, `ok: true`, correct answer), but its report
  is Claude's restatement. For a cross-check, run the bridge directly or ask the wrapper to save
  the JSON and read `result.response` yourself.
- If `agy` is missing or signed out, the bridge fails; ask the user to sign in with `agy`
  interactively. Do not fall back to any other Gemini client.

## Streamed progress and follow-up (tested 2026-11-06)

The direct CLI with `--output-format stream-json` emits `init`, `step_update` and `result` events.
Capture `conversation_id` from `init`; assistant text arrives in `step_update.text_delta`.
Tool events include name, state and errors. The final payload is `result`, with `status`,
`response` and usage. Inspect tool errors too: an intentionally denied write returned overall
`SUCCESS`, so success alone does not prove all requested actions ran. Usage counters on a retained
conversation are cumulative; do not sum them as if each turn were independent.

After completion, repeat the same launch configuration with `--conversation <conversation_id>`
and a new prompt/log path. Do not use `--continue` to guess the conversation. Flash passed streamed
output, matching IDs and marker recall without rereading. Persistent stream input is a separate
path: documentation says wait for the current result before sending the next prompt. Live
steering, ACP cancellation and concurrently resuming an active turn are not validated here.

### Required read-only profile

Store this profile in the task's artifact directory and pass it with `--settings` on **every**
initial and resumed read-only launch. Do not modify global settings or merge in command/MCP allows.
The parent creates the directory and profile; the worker must not change them.

```json
{
  "permissions": {
    "allow": [],
    "ask": [],
    "deny": ["write_file(*)", "command(*)", "mcp(*)", "execute_url(*)"]
  }
}
```

```bash
agy --model gemini-3.8-flash-low --settings <task-dir>/readonly.json --output-format stream-json --print-timeout 900s -p "$(cat <task-dir>/prompt.txt)" < /dev/null > <task-dir>/events.jsonl 2> <task-dir>/stderr.log
```

Run from the intended workspace. For follow-up, add `--conversation <conversation_id>` and use
new prompt/output files, repeating `--settings` and the model. This profile supports file-reading
work; terminal commands, MCP and browser execution are denied. Route command-dependent checks
elsewhere rather than weakening it. Model defaults still must follow the task and quota snapshot.

The 2026-11-06 Flash test used this exact profile: it read a random marker, attempted a file write,
then recalled the marker and attempted another write on resume. Both writes produced actual
`write_file` tool errors matching the configured deny rule; neither canary file existed. This is
verified native permission enforcement for that path, not a proof against every tool or filesystem
escape. Check the workspace before and after. Retest after CLI changes before relying on it.

Do not rely on `--mode plan`; also, combining it with `--disable-slash-commands` emitted a warning
that plan mode had no effect. Neither flag is needed in the tested deny-profile command above.
The bridge cannot pass `--settings`, so it is not an eligible route for this profile.

Permission rule semantics: [official CLI permissions](https://antigravity.google/docs/permissions).

## Quota

`scripts/usage` reads it with `agy -p /usage`, which spends no quota (`USAGE.md`). Gemini's level
comes from the "Gemini Models" group; Argon has its own weekly bucket on Pro plans, reported as a
note.
