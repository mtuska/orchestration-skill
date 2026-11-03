# Gemini (Google), through the Antigravity CLI `agy`

Models: Gemini 4 Argon and Gemini 3.8 Flash. Scores and prices are in `../BENCHMARKS.md`.

`agy` also serves Claude Opus 5.5, Claude Sonnet 5.5 and GPT-OSS 120B. Those are Anthropic and
OpenAI models: never use them through `agy`, and never count a run on them as a Gemini check. Use
only `gemini-*` model IDs.

## What it can do in this harness

Every kind of work: reading, review, planning, editing and implementation. Setup facts:

- **Commands run only if allowed.** `agy` in headless mode auto-denies every command that no allow
  rule in its `settings.json` (`~/.gemini/antigravity-cli/settings.json`, `permissions.allow`)
  covers, and the bridge then fails the run with `denied_actions`. Seen on 2026-11-02: a question
  the model chose to answer with a command was denied and returned nothing. On 2026-11-02 that file
  held no allow rules, so builds and tests for Gemini's work are run by the checker or by you until
  the user adds rules for the commands it needs. Adding them is the user's configuration; do not
  edit it yourself.
- **File edits are auto-accepted.** The bridge always runs `agy` in `accept-edits` mode, so
  implementation works without approval prompts. The other side: "do not modify files" is only an
  instruction in the brief, so for read-only work check the workspace after the run.
- **It reads files itself** from the `--cwd` workspace; give it paths, not pasted content.

## How to launch

The `cc-gemini-plugin` bridge, run through the shell tool's background facility. The bridge passes
the task to `agy` over stdin unchanged and prints one JSON envelope:

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
- Say in the brief which commands it may run. A command that is not allowed fails the whole run,
  so while none are allowed, ask it to edit and read only and say who will build and test.
- The plugin also provides the Agent tool type `cc-gemini-plugin:gemini-agent` (a Claude wrapper
  with Bash, Glob and Read that runs the same bridge) and the `/cc-gemini-plugin:gemini` command.
  The wrapper works (smoke test 2026-11-02: exit 0, `ok: true`, correct answer), but its report
  is Claude's restatement. For a cross-check, run the bridge directly or ask the wrapper to save
  the JSON and read `result.response` yourself.
- If `agy` is missing or signed out, the bridge fails; ask the user to sign in with `agy`
  interactively. Do not fall back to any other Gemini client.

## Quota

`scripts/usage` reads it with `agy -p /usage`, which spends no quota (`USAGE.md`). Gemini's level
comes from the "Gemini Models" group; Argon has its own weekly bucket on Pro plans, reported as a
note.
