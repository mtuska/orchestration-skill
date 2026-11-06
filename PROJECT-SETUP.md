# Per-project command setup for Gemini and Cursor

These native-CLI setup notes complement the vendor launch instructions. Command allowlists alone
do not enforce read-only filesystem access. Configure only the access authorized for the current assignment.

Claude agents run under the session's own permissions and Codex under its `-s` sandbox flag, so
both can run builds and tests out of the box. `agy` and `cursor-agent` refuse, in a headless run,
every command that no allow rule covers. Give each project its own rules before Gemini or Cursor
works there; after that they build, test and run repros like the other vendors.

When the current task authorizes setup, keep it per project: never edit the global files
(`~/.gemini/antigravity-cli/settings.json`, `~/.cursor/cli-config.json`), and never use the
allow-everything switches (`agy --dangerously-skip-permissions`, `cursor-agent --force` / `--yolo`).
Those bypass the lock and process rules that every agent on a shared machine must follow.

## Where the rules live

| Tool | File | How it is applied | Tested 2026-11-02 |
|---|---|---|---|
| `agy` (Gemini) | `<project root>/.agents/agy-settings.json` | passed on every run with `--settings <file>`; applies to that run only and is never saved | `command(wc)` let `wc -l` run; without `--settings` it was denied, and the global file was unchanged |
| `cursor-agent` (Cursor) | `<project root>/.cursor/cli.json` | read automatically from the workspace root | `Shell(wc)` let `wc -l` run; without the file it was refused, and the global config was unchanged |

A separate workspace of the same project (a second checkout, a worktree) needs its own copy. The
plugin's Gemini bridge cannot pass `--settings`, so a run that needs commands calls `agy` directly (`vendors/gemini.md`). Neither run needed the folder to be on `agy`'s trusted-workspace list.

If the project is under version control, add these files the way the project adds any tooling
file (committed, or ignored if the project's rules say tooling stays local), and say which in the
record.

For Gemini read-only file inspection, use the separate deny profile in `vendors/gemini.md`.
Do not add the command allow rules below to that profile; command-dependent work needs another
appropriate harness. Plan mode alone was observed to permit writes.

## What to allow

Take the commands from the project's own instructions (AGENTS.md, CLAUDE.md, its build and test
rules), never from what a model asks for:

- **Read-only inspection:** `git show`, `git diff`, `git log`, `git status`, `rg`, `grep`, `ls`,
  `wc`, and the project's own read-only tools. These command rules do not by themselves confine file edits for reviews.
- **The project's gated build and test entry points, exactly as its rules write them**, including
  any lock or memory-gate wrapper (for example `flock ... mem-gate.sh ... make -f Makefile.ext
  test-unit`). Allow the gated form, not the bare build command, so the agent cannot skip the lock.
- Nothing that publishes, commits or deletes, unless the task is that.

Deny explicitly what must never run even if a broader rule matches: `git push`, `git reset`,
`git clean`, `rm`, `kill`, `pkill`, and the project's commit or sync commands. Deny wins over allow
in both tools.

## Syntax

`agy` (`.agents/agy-settings.json`):

```json
{
  "permissions": {
    "allow": ["command(git show)", "command(git diff)", "command(rg)", "command(regex:make -f Makefile\\.ext (test-unit|build-editor))"],
    "deny": ["command(git push)", "command(rm)", "command(pkill)"],
    "ask": []
  }
}
```

Rules match command prefixes word by word, so `command(git)` would allow `git push` too; name the
subcommand. A `regex:` target treats each word as an anchored regular expression. Pipes, `&&`
chains and wrappers like `timeout` and `env` still match by prefix, but command substitution
(`$(...)`), brace expansion and network redirects turn prefix matching off for the whole line, so
such a command is denied. Source: Google's permissions page
(https://antigravity.google/docs/permissions?tab=cli), read 2026-11-02.

`cursor-agent` (`.cursor/cli.json`):

```json
{ "permissions": { "allow": ["Shell(git show)", "Shell(git diff)", "Shell(rg)"], "deny": ["Shell(git push)", "Shell(rm)", "Shell(pkill)"] } }
```

Subcommand rules work in both tools. Tested 2026-11-02 with `git status` allowed: `git status
--short` ran and returned its real output, and `git log --oneline` was refused, in `agy` and in
`cursor-agent` alike. Wrapper forms (`flock ...`, `timeout ...`) were not tested in Cursor: before
relying on one, check it with a scratch run that asks for an allowed and a disallowed command and
compare the log.

## After setup

- Brief the agent with the exact allowed commands. A refused command fails a Gemini run outright
  (`denied_actions`), and a Cursor run still reports success with an invented result, so the
  brief must not invite anything else.
- Read the run log for every build or test result; accept a result only from a command that
  visibly ran.
- When a project's entry points change, update both files in the same change.
