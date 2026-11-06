# Project permissions for vendor CLIs

Configure once per project, reuse on initial and resumed launches. Inspect and merge existing
vendor files; do not overwrite unrelated settings or rewrite global configuration, except for
the exact-path Codex trust registration below. Keep shared
settings in version control according to project rules; keep machine-specific paths in local
settings. Worktrees need their own applicable files. Record the selected files and access in the
worker brief. Model and effort remain task decisions, not permission-file defaults.

## Preserve the orchestrator's access

Before changing permissions, identify the active orchestrator and which configuration files it
loads. Preserve its working tool, filesystem, network, MCP and approval access. In particular,
when Claude is the orchestrator, do not tighten shared `.claude/settings.json` or
`.claude/settings.local.json` to restrict a Claude worker: those changes can also restrict the
parent or future parent sessions. Never disable the parent's tools or sandbox escape/approval
path as a side effect of worker setup.

Keep stable project settings compatible with the orchestrator. Apply narrower worker permissions
through worker-only launch flags, a retained native settings overlay passed only to that worker,
or a separate worktree with its own configuration. Check the vendor's merge rules: an overlay is
not automatically isolated, and shared deny rules may still win. Do not mutate a shared file
between concurrent launches. For different-vendor workers, verify that their files are not also
loaded by the orchestrator or a shared wrapper.

Only change the orchestrator's own access when the user explicitly requests that change. If worker
isolation cannot be achieved without affecting the parent, use a separate execution environment
or let the parent perform the authorized operation; do not risk locking it out to enforce a
worker role. Record and preserve existing settings when adding project permissions.

## Files and roles

| Vendor CLI | Project-local configuration | Launch selection |
|---|---|---|
| Claude `claude` | `.claude/settings.json`; `.claude/settings.local.json` for machine-local additions | Auto-loaded from the project; `--settings <file>` for a retained role overlay |
| Codex `codex` | `.codex/config.toml` in a trusted project | `-C <project>`; `-s read-only` for inspection, `-s workspace-write` for implementation/tests |
| Gemini `agy` | `.agents/agy-settings.json` and `.agents/agy-readonly.json`, using native settings JSON | Pass the chosen file with `--settings` every time; this path is our convention, not automatic discovery |
| Cursor `cursor-agent` | `.cursor/cli.json` for tool permissions; `.cursor/sandbox.json` for filesystem/network | `--workspace <project> --sandbox enabled`; select `--mode ask` for inspection, omit mode for implementation |

Select a role without editing shared settings between concurrent workers. Keep stable project
build/test permissions in the main file; narrow a reviewer's tool set or use a dedicated review
worktree and retained overlay. Do not flip the project's shared sandbox to writable for a test
while a reviewer is using it. CLI flags can override files; check effective settings rather than
assuming the file won. Host/admin restrictions and MCP approvals still apply independently.

A read-only source review may need writable build outputs, caches and temp files. Either run
those checks in a separate authorized build workspace and give the reviewer the logs, or use
filesystem controls that explicitly allow only those output paths. Do not launch a file-only
reviewer and expect it to build. Do not enable a general shell and call it read-only merely
because Edit/Write tools were removed.

## Preflight and failure handling

List the required source reads, output/cache writes, exact gated commands, network destinations,
and local sockets before dispatch. Tool approval, filesystem access and network access are
separate controls. A working model API or web-search tool does not prove shell network access.
HTTP domain access does not prove UDP, TCP listeners, multicast, Unix sockets or host loopback.

For network tests, run a minimal relevant probe under the **same worker execution permissions**:
create/bind a socket to `127.0.0.1:0`, exchange a packet between two local UDP sockets if needed,
and exercise required host services or remote endpoints. Avoid fixed ports and clean up sockets.
For builds, verify the output directory and required cache paths are writable. A parent-shell
probe only establishes the parent environment; repeat through the worker's sandbox or test runner.
Where the CLI has a direct sandbox runner, use it without spending a model turn. Otherwise make
preflight the worker's first bounded step. Preserve stdout, stderr, exit status and effective config.

Classify failure from evidence: EACCES/EPERM, EADDRINUSE, missing tools, refused commands, missing
service, DNS/proxy failures and test assertions are different problems. A UDP bind failure alone
is not proof of a code defect or proof of sandbox interference. Compare a minimal probe in the
restricted and already-authorized test environments before attributing it.

If the worker is blocked, the parent fixes the project configuration within existing authorization
or executes the required checks itself in an appropriate authorized environment. Reuse the worker
for analysis afterward. Do not defer an otherwise runnable required suite to the user just because
the selected worker was too restricted. Do not discard failing tests, claim a pass, weaken a
reviewer's role, or rerun unchanged after a denial. If host policy prevents the needed access,
report the precise blocked check and permission; no nested CLI bypasses that host policy.

## Codex

For a project whose authorized tests need networking, merge into `.codex/config.toml`:

```toml
approval_policy = "never"
sandbox_mode = "workspace-write"

[sandbox_workspace_write]
network_access = true
# writable_roots = ["/absolute/required/build-cache"]
```

Use `network_access = false` for offline projects. `never` means denied operations fail instead
of waiting for an unattended approval; it does not grant access. Keep `-s read-only` for file
reviews; the workspace-write network setting is not a read-only network switch. If a review
needs networked tests, the parent can run them in the configured build environment.

`--add-dir` adds writable roots, not network permission. `--search` enables a model tool, not
shell sockets. `-s danger-full-access` removes filesystem/network sandbox restrictions; it is
not the normal fix for networked tests. Use it only for an explicitly appropriate authorized
execution environment, never to defeat a host restriction.

### Codex project trust exception

When setting up Codex for the user's current project, the orchestrator may register that exact
project as trusted in `$CODEX_HOME/config.toml` (normally `~/.codex/config.toml`). This is the
narrow exception to keeping changes project-local; permissions remain in `.codex/config.toml`.

Resolve the canonical absolute project/worktree root and inspect its applicable `.codex`
configuration, hooks and rules before trusting it. Merge or update only the matching entry:

```toml
[projects."/absolute/path/to/project"]
trust_level = "trusted"
```

Preserve unrelated entries, comments and settings; validate the TOML and avoid duplicate tables.
Do not replace a config that changed concurrently. Never trust `/`, the home directory, a general
checkout parent or an unrelated repository just to suppress the warning. If an entry explicitly
marks the project untrusted, establish why before changing it; do not override an intentional
user/admin restriction under this setup exception. Trust registration must not alter global
sandbox, approval, network, tool or orchestrator permissions, or use a bypass flag.

Verify the next Codex launch loads the intended project settings and retains the selected role's
restrictions. Record the exact trusted path. Handle a new worktree explicitly rather than trusting
its parent directory. A trust entry is permission to load project configuration, not proof that
network-dependent tests will run; retain the preflight checks above.

Project config requires project trust. Do not put `[profiles.*]` in project config: current
Codex ignores project-local configuration profiles. `--profile` resolves user-home profile files.
Keep project permissions in `.codex/config.toml` and select the role with supported launch flags.
New permission-profile/network-proxy configurations have different semantics; do not mix their
keys with legacy sandbox examples without checking the installed schema. In particular, HTTP
proxy access is not evidence that raw UDP binds or host networking work.

Sources: [configuration](https://learn.chatgpt.com/docs/config-file/config-reference),
[CLI](https://developers.openai.com/codex/cli/reference). Local help checked: Codex 0.167.0.

## Claude

Put project permissions in `.claude/settings.json`. For example, replace the sample test command
and domain with the project's actual authorized entry point and destination:

```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep", "Bash(git diff *)", "Bash(./scripts/test-unit *)"],
    "deny": ["Bash(git push *)"]
  },
  "sandbox": {
    "enabled": true,
    "allowUnsandboxedCommands": false,
    "network": {"allowedDomains": ["registry.npmjs.org"]}
  }
}
```

Use `--permission-mode dontAsk` for preallowed headless commands; use `acceptEdits` when the
assignment authorizes edits, with the project's command rules still in force. For file-only
reviews, restrict `--tools Read,Glob,Grep` and MCP exposure as in `vendors/claude.md`. `--add-dir`
adds tool-access directories, not blanket command approval. Enable only needed MCP servers;
server availability is not authorization for every operation.

Sandbox network rules and Bash permission rules are separate. On Linux, sandbox localhost is
private to the command; `allowLocalBinding` is not a Linux fix for reaching host services. On
macOS, `sandbox.network.allowLocalBinding` controls local binding. For unsupported protocols or
host services, use a narrowly scoped authorized `sandbox.excludedCommands` entry or parent-run
check; an excluded command has no sandbox filesystem/network protection. Do not broadly exclude
interpreters, shells or build tools to fix one test. Keep read-only reviews separate.

Sources: [settings](https://code.claude.com/docs/en/settings),
[sandbox](https://code.claude.com/docs/en/sandboxing). Local help checked: Claude 2.1.318.

## Gemini through Antigravity

Keep the build profile at `.agents/agy-settings.json`; pass it on every launch and resume:

```json
{
  "enableTerminalSandbox": true,
  "permissions": {
    "allow": ["command(git diff)", "command(./scripts/test-unit)", "read_url(registry.npmjs.org)"],
    "deny": ["command(git push)"],
    "ask": []
  }
}
```

Replace examples with exact project entry points, including required lock/memory wrappers.
`command(...)` grants command execution; `read_file(...)` and `write_file(...)` extend sandbox
path access, and `read_url(...)` supplies outbound domains. These do not establish raw socket
support. Unsupported network/host checks should run through the parent's authorized runner.
`--add-dir` extends the workspace. `--sandbox` enables terminal isolation; it does not make file
editing tools read-only. Do not invent `--network` or treat `--mode plan` as enforcement.

Retain the tested deny profile from `vendors/gemini.md` in `.agents/agy-readonly.json`, separate
from build allows. Deny wins over allow. Headless denied commands must not wait for UI approval;
inspect `denied_actions` and tool errors even with `status: SUCCESS`. Do not use the bridge when
permissions require `--settings`, since it cannot pass that file. Never use the blanket skip switch.

Sources: [permissions](https://antigravity.google/docs/permissions?tab=cli),
[terminal sandbox](https://antigravity.google/docs/sandbox?tab=cli). CLI help checked 2026-11-06;
network/path examples are documented controls, not new live-agent verification.

## Cursor / Grok / Composer through cursor-agent

Merge exact command grants into `.cursor/cli.json`:

```json
{"permissions":{"allow":["Shell(git diff)","Shell(./scripts/test-unit)"],"deny":["Shell(git push)"]}}
```

Use `.cursor/sandbox.json` for persistent sandbox access, for example:

```json
{
  "type": "workspace_readwrite",
  "networkPolicy": {"default": "deny", "allow": ["registry.npmjs.org"]},
  "additionalReadwritePaths": [],
  "additionalReadonlyPaths": []
}
```

Set `type: workspace_readonly` in a dedicated review workspace when shell-level write protection
is needed, and keep `--mode ask`. Add only required absolute paths. If authorized tests require
unrestricted outbound traffic, `networkPolicy.default: allow` is available; verify local socket
behavior separately. `--sandbox enabled` activates the sandbox; `--trust` only skips workspace
trust, not command permissions. Never use `--force`/`--yolo` to paper over missing rules. Do not
change global config. Verify merged policy and command execution, since an exit-zero answer can
still describe an unexecuted command. Ask mode alone is not a proven OS filesystem boundary.

Sources: [sandbox configuration](https://prod.cursor.com/docs/reference/sandbox),
[CLI configuration](https://prod.cursor.com/docs/cli/reference/configuration).
Local help checked: 2026.11.05-86047df; new sandbox-file examples require project preflight.
