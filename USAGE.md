# Usage companion: plan quota for routing decisions

`scripts/usage` (next to this file) reads how much of each vendor's plan is left and turns it into
one JSON snapshot with a routing hint. Run it before every new worker or reviewer launch, including replacements and resumed CLI launches. An immediately
following batch may share a call. Select and launch the model using `SKILL.md` and its vendor instructions.

```bash
~/.claude/skills/orchestration/scripts/usage --text      # human summary
~/.claude/skills/orchestration/scripts/usage             # JSON (successful reads cached 15 min)
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
| Cursor/Grok models | `cursor-agent` interactive `/usage` screen, read through a short-lived local terminal; `status` and `about` provide sign-in and plan. Print mode sends `/usage` to the model, so the script does not use it. | none | `cursor-agent`'s own sign-in. The CLI may create local session metadata; this does not start a model turn. |
| Gemini | `agy -p /usage --output-format json` and `agy -p /credits --output-format json`: read-only slash commands that `agy` answers without an agent turn, without spending quota and without keeping a conversation | none | `agy`'s own sign-in; nothing is read from `~/.gemini`. |

Quota queries do not ordinarily spend model tokens. Exception: refreshing expired Claude
authentication can make one Haiku model call; `--no-refresh` disables that behavior. The script writes the local cache at
`~/.cache/orchestration-usage/last.json` and its lock file; Cursor's CLI may write local
session metadata. Successful vendor reads are cached separately for 15 minutes, including
`--vendor` calls. Failed or stale reads are reused for at most 60 seconds to avoid repeated launch delays.
Concurrent chats share refreshes through the lock. `--no-cache` forces a live read and updates
the shared cache, preserving other vendors. `--cache-ttl SECONDS` changes successful-read reuse.
A reset crossed since an observation invalidates that cached vendor. After a quota rejection,
force a refresh of the affected vendor before rerouting. JSON lists `cached_vendors`; each vendor
has `observed_at` and `age_seconds`. The snapshot timestamp is assembly time, not observation time.

## What a snapshot contains

```
vendors.<claude|codex|gemini|cursor>
  observed_at   time the vendor reader last ran (not proof a fallback source is fresh)
  age_seconds   elapsed time since that observation
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

Thresholds, in the script's constants: red at 90 % of an applicable shared window or a vendor-reported shared stop
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
| Cursor account | included plan usage shown by the CLI's `/usage` screen, with the plan's monthly or weekly label and reset date; the exact reset time is not exposed by that screen |
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

Claude model-specific windows carry `bucket` and `level` and do not set the shared vendor level.
Check both shared and model-specific limits before selecting a model. If only scoped limits are
reported, the shared level is unknown. Codex and Gemini scoped limits remain in windows and notes;
do not mistake a green shared level for permission to use an exhausted model bucket.

## How the orchestrator uses it

The policy is in `SKILL.md`: select the least expensive suitable model, then use quota headroom
and reset times among suitable accounts. Green is not a reason to upgrade. A required independent
review remains required when quota is scarce; mechanical work may use deterministic verification.

Unknown/stale quota must be recorded and is not evidence of spare capacity. Prefer a suitable
measured account. If all eligible shared/model limits are red, stop and report reset times.
Do not spend paid credits or reset credits without authorization. Record observation age and the
actual model-selection reason, not just the script's vendor-level `prefer` hint. The script does
not classify task difficulty or choose an exact model.
