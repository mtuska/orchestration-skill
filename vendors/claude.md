# Claude (Anthropic)

Models: Fable 5.1, Opus 5.5, Sonnet 5.5, Haiku 5.5. Scores and prices are in `../BENCHMARKS.md`.

## What it can do in this harness

Everything the session's own tools allow: read, edit, run builds and tests, drive the browser.
Claude subagents inherit the session's permission settings.

## How to launch

The Agent tool, `subagent_type: "general-purpose"` (or `Plan` / `explore` for read-only work), with
`model: "fable" | "opus" | "sonnet" | "haiku"`. Launch it with the tool's background option and
wait for its completion notice; never poll its transcript.

For read-only work prefer a read-only agent type over an instruction not to edit.

## Quota

`scripts/usage` reads the claude.ai plan windows (`USAGE.md`). In the Claude desktop app
`mcp__ccd_session_mgmt__get_usage` gives the same windows directly.
