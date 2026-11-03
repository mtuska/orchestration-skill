# Usage companion: plan quota for routing decisions

`scripts/usage` (next to this file) reads how much of each vendor's plan is left and turns it into
one JSON snapshot with a routing hint. Run it at the start of an orchestration and before any
launch that will burn a lot of tokens (a long implementation, a benchmark run, a wide review).

```bash
~/.claude/skills/orchestration/scripts/usage --text      # human summary
~/.claude/skills/orchestration/scripts/usage             # JSON (cached 60 s)
~/.claude/skills/orchestration/scripts/usage --vendor codex --no-cache
~/.claude/skills/orchestration/scripts/usage --vendor gemini --no-cache
~/.claude/skills/orchestration/scripts/usage --vendor cursor --no-cache
```

Inside the Claude desktop app the Claude half is also available without the script:
`mcp__ccd_session_mgmt__get_usage` returns the same windows. The script is still the only source
for Codex, Gemini and Cursor.

## Where the numbers come from

| Vendor | Live source | Fallback | Token handling |
|---|---|---|---|
| Claude | `GET https://api.anthropic.com/api/oauth/usage` with the claude.ai OAuth token from `~/.claude/.credentials.json` (the same call `/usage` makes) | none | If the stored token is expired the script runs one Haiku `claude -p` call, which makes Claude Code refresh and rewrite the file. `--no-refresh` disables that; the snapshot is then `unavailable`. |
| Codex | `codex app-server` JSON-RPC `initialize` + `account/rateLimits/read` (what `/status` shows): the default bucket, every extra bucket in `rateLimitsByLimitId`, `ordinaryUsageAllowed` and `rateLimitResetCredits` | last `token_count` event in `~/.codex/sessions/**/*.jsonl`, reported as `stale` (default bucket only) | Codex's own auth; nothing is read from `auth.json`. |
| Cursor | none: `cursor-agent` shows usage only on its interactive `/usage` screen, and in print mode `/usage` goes to the model as a prompt. The script runs `cursor-agent status` and `about` (`--format json`) for sign-in and plan only | none | `cursor-agent`'s own sign-in. |
| Gemini | `agy -p /usage --output-format json` and `agy -p /credits --output-format json`: read-only slash commands that `agy` answers without an agent turn, without spending quota and without keeping a conversation | none | `agy`'s own sign-in; nothing is read from `~/.gemini`. |

All are read-only. Neither writes anything except the cache at
`~/.cache/orchestration-usage/last.json`.

## What a snapshot contains

```
vendors.<claude|codex|gemini|cursor>
  status        ok | stale | unavailable
  plan          Claude: pro / max / team / ...   Codex: plus / pro / prolite / business / ...
                Gemini: null (agy does not report the plan)   Cursor: premium / ...
  level         green | yellow | red | null (nothing measurable)
  windows[]     id, label, percent used, resets_at, resets_in,
                expected_percent_now (elapsed share of the window), pace: ahead | on | behind
                (Codex windows from an extra per-model bucket carry `bucket` and the bucket
                name in the label; they do not set the level or binding, but a yellow or red
                bucket adds a note, so check notes before routing to that model)
  binding       the window with the least headroom
  extra_usage   (Claude) whether overage credits are on
  credits, individual_limit, rate_limit_reached_type,
  ordinary_usage_allowed, reset_credits {available, next_expires_at}   (Codex)
  credits {balance}   (Gemini: AI credits, used after the plan quota runs out)
advice          level per vendor; prefer: one vendor, several greenest joined with "+"
                (for example claude+gemini), either (all equal) or neither (all red);
                one-line rule; notes
                (with --vendor only that vendor's level, and prefer: n/a)
```

Thresholds, in the script's constants: red at 90 % of any window or a vendor-reported stop
(Claude lock; Codex `rateLimitReachedType`, spend control, `ordinaryUsageAllowed: false`, or no
credits and no window); yellow at 70 %, or 50 % while running more than 1.3x ahead of pace.

Account shapes differ, and the script reports whatever the vendor returns, so read the labels
rather than assuming the shape:

| Account | Windows you will see |
|---|---|
| Claude Pro / Max | 5-hour, weekly all models, and a weekly per-model window (for example Fable) |
| Claude Team | session, weekly all models, per-model weekly |
| ChatGPT Plus / Pro / Pro Lite (standard) | a single 7-day window, or a 5-hour primary plus a weekly secondary, depending on plan; sometimes extra per-model buckets; a credits balance used after the windows run out; occasional free "full reset" credits |
| ChatGPT Business with credits | no 5-hour or weekly window, only a monthly individual limit |
| Cursor account | no windows: status is always `unavailable` and the level unknown, with the plan and a note saying the quota was not read |
| Google account in `agy` | per model group: "Gemini Models" (Flash and Pro, shared) with a weekly and a 5-hour window; "Claude and GPT models" with the same pair; and, on paid Pro plans, a separate weekly "Gemini 4 Argon" window (on Ultra it is part of the larger Gemini bucket) |

Gemini's level is set by the "Gemini Models" group only. The Argon group is reported like a Codex
per-model bucket: it adds a note when yellow or red, so check notes before routing to Argon. The
"Claude and GPT models" group is Anthropic and OpenAI models served through `agy`; it is reported
and never sets any level. `agy` reports remaining fractions, which the script turns into percent
used. A Google Cloud project or API-key sign-in has no such groups, and the vendor then reads as
`unavailable`.

On a standard Codex account a red window is not the end of the road: `credits.balance` keeps
usage going at credit cost, and `reset_credits.available` counts free full resets. Spending
either is the user's call; mention them when reporting Codex red, do not use them yourself. The
same holds for Gemini's AI credits (`credits.balance`).

## How the orchestrator uses it

Fit decides first; budget decides among the fits. Concretely:

Every row of the routing and cross-check tables ranks all vendors, so budget decides how far
down a row to go:

1. **All green:** take the first model in the row.
2. **A vendor yellow:** where its model and a greener vendor's sit close together in the row
   (routine implementation, terminal-heavy runs, research, mechanical work), take the greener one
   (`prefer`). High-consequence rows (architecture, hard root cause, security, migration) keep
   their first choice unless it is red.
3. **A vendor red:** launch no new *work* on it; take the next model in the row from another
   vendor. If that model is clearly weaker for high-consequence work, say so in the record, and
   ask the user when the gap is large. If the next model's tool cannot run a step the work needs
   (Gemini and Cursor run only allowlisted commands), give that step to another agent.
4. **Cross-checks are never skipped for budget.** They are small relative to the work. On a
   yellow or red vendor take the next checker in the row, or the vendor's cheaper model where the
   work is ordinary (Sol instead of Astra for ordinary code; Haiku, Luna, Flash or Composer for
   number re-derivation), never a same-vendor checker.
5. **All red:** stop launching, report the snapshot and the reset times, and wait for the user.
6. **Unknown (unavailable):** treat as yellow and say in the record that the quota was not read.
7. Pace matters more than the raw percentage early in a window: 40 % used with a day gone of a
   week is fine; 40 % used after two hours of a five-hour session is not.

Record the snapshot's `advice` line next to who did and who checked each task in the system of
record, so a later reader can see why a routing differed from the fit table.
