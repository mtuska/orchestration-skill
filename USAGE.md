# Usage companion: plan quota for routing decisions

`scripts/usage` (next to this file) reads how much of each vendor's plan is left and turns it into
one JSON snapshot with a routing hint. Run it at the start of an orchestration and before any
launch that will burn a lot of tokens (a long implementation, a benchmark run, a wide review).

```bash
~/.claude/skills/orchestration/scripts/usage --text      # human summary
~/.claude/skills/orchestration/scripts/usage             # JSON (cached 60 s)
~/.claude/skills/orchestration/scripts/usage --vendor codex --no-cache
```

Inside the Claude desktop app the Claude half is also available without the script:
`mcp__ccd_session_mgmt__get_usage` returns the same windows. The script is still the only source
for Codex.

## Where the numbers come from

| Vendor | Live source | Fallback | Token handling |
|---|---|---|---|
| Claude | `GET https://api.anthropic.com/api/oauth/usage` with the claude.ai OAuth token from `~/.claude/.credentials.json` (the same call `/usage` makes) | none | If the stored token is expired the script runs one Haiku `claude -p` call, which makes Claude Code refresh and rewrite the file. `--no-refresh` disables that; the snapshot is then `unavailable`. |
| Codex | `codex app-server` JSON-RPC `initialize` + `account/rateLimits/read` (what `/status` shows): the default bucket, every extra bucket in `rateLimitsByLimitId`, `ordinaryUsageAllowed` and `rateLimitResetCredits` | last `token_count` event in `~/.codex/sessions/**/*.jsonl`, reported as `stale` (default bucket only) | Codex's own auth; nothing is read from `auth.json`. |

Both are read-only. Neither writes anything except the cache at
`~/.cache/orchestration-usage/last.json`.

## What a snapshot contains

```
vendors.<claude|codex>
  status        ok | stale | unavailable
  plan          Claude: pro / max / team / ...   Codex: plus / pro / prolite / business / ...
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
advice          level per vendor, prefer: claude | codex | either | neither, one-line rule, notes
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

On a standard Codex account a red window is not the end of the road: `credits.balance` keeps
usage going at credit cost, and `reset_credits.available` counts free full resets. Spending
either is the user's call; mention them when reporting Codex red, do not use them yourself.

## How the orchestrator uses it

Fit decides first; budget decides among the fits. Concretely:

1. **Both green:** route by the fit table alone.
2. **One vendor yellow:** for rows where the table lists both vendors as suitable (routine
   implementation, terminal-heavy runs, research, mechanical work), pick the greener vendor's
   model. High-consequence rows (architecture, hard root cause, security, migration) keep their
   first choice regardless.
3. **One vendor red:** launch no new *work* on it; use the other vendor wherever the table allows.
   Where only the red vendor fits (for example security review by Astra when Codex is red), tell
   the user and wait rather than quietly downgrading to a model the table forbids.
4. **Cross-checks are never skipped for budget.** They are small relative to the work. On a
   yellow or red vendor use the cheapest checker the cross-check table permits (Sol instead of
   Astra for ordinary code, Haiku/Luna for number re-derivation), never a same-vendor checker.
5. **Both red:** stop launching, report the snapshot and the reset times, and wait for the user.
6. **Unknown (unavailable):** treat as yellow and say in the record that the quota was not read.
7. Pace matters more than the raw percentage early in a window: 40 % used with a day gone of a
   week is fine; 40 % used after two hours of a five-hour session is not.

Record the snapshot's `advice` line next to who did and who checked each task in the system of
record, so a later reader can see why a routing differed from the fit table.
