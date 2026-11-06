# Claude (Anthropic)

Models: Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5. Scores and prices are in `../BENCHMARKS.md`.

## What it can do in this harness

Everything the session's own tools allow: read, edit, run builds and tests, drive the browser.
Claude subagents inherit the session's permission settings; confirm the chosen agent type's tools.

## How to launch

The Agent tool, `subagent_type: "general-purpose"` (or `Plan` / `explore` for read-only work), with
`model: "fable" | "opus" | "sonnet" | "haiku"`. Launch it with the tool's background option and
keep completion notifications enabled. Ask native workers to send milestone updates through
the host parent-message channel; do not repeatedly poll their full transcript.

For read-only work prefer a read-only agent type over an instruction not to edit.

## CLI progress and follow-up (tested 2026-11-06)

When the host has no Claude Agent tool, the CLI can run a retained conversation. For a read-only
file-reading worker, this exact restriction set was tested with Haiku:

```bash
claude -p --model haiku --effort low --tools Read --permission-mode dontAsk --strict-mcp-config --mcp-config '{"mcpServers":{}}' --verbose --output-format stream-json < <task-dir>/prompt.txt > <task-dir>/events.jsonl 2> <task-dir>/stderr.log
```

Use the model and tool set appropriate to the actual assignment; this example intentionally
exposes only Read and disables MCP. Capture `session_id` from `system`/`init` or `result` events.
Assistant text is in `assistant.message.content[]` blocks with `type: text`. The final `result`
contains `is_error` and the answer. Keep event and stderr logs separate.

After process completion, rerun the same command with `--resume <session_id>`, a follow-up prompt
file and new log filenames. Repeat model, effort and restriction flags. The test verified matching
IDs, a pre-read progress message, marker recall without a second read, and Read-only tool exposure
on resume; the write probe had no permitted write tool.

Do not use `--bg --resume` against a running session: it can create a copy. Persistent streaming
input and SDK interruption are separate, not runtime-tested by this procedure.

## Quota

`scripts/usage` reads the claude.ai plan windows (`USAGE.md`). In the Claude desktop app
`mcp__ccd_session_mgmt__get_usage` gives the same windows directly.
