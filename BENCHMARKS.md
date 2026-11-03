# Benchmarks behind the routing tables

Looked up 2026-11-02 through the BenchLM MCP tools; BenchLM data as of 2026-10-29. Re-check when a
model ships, and update the routing tables in `SKILL.md` only from what changed here.

Read these as weak evidence. Sources: BenchLM current rankings (BenchAlign v5.8 composite, surfaces
overall / coding / agentic) and BenchLM's recorded benchmark results and verified prices. BenchLM
says its recorded boards hold values "from the benchmark operator or the model provider" and does
not mark which, so treat every task score below as possibly vendor-reported. CursorBench is run by
Cursor, the maker of Composer. BenchLM's own ranking intervals are flagged unvalidated, and an
"estimated" rank rests on no direct source for that surface. Effort settings change results a lot
and BenchLM does not always say which effort a score used. Coding scores do not by themselves
prove which model is better at architecture or review.

## Main table

| Model | BenchLM rank: overall / coding / agentic | Terminal-Bench 4.0 | DeepSWE | FrontierSWE v2 | OSWorld 2.0 | GraphWalks BFS 256K-1M | FrontierMath v2 T4 | SEC-Bench Pro | Price in / out per M tokens |
|---|---|---|---|---|---|---|---|---|---|
| Claude Fable 5.1 | 7 / 4 / 2 | 55.8 | 67.4 | 56.3 | 41.7 | 65.0 | 87.8 | - | $10 / $50 |
| Claude Opus 5.5 | 2 / 1 / 1 | 66.4 | 74.2 | 62.3 | 48.7 | 66.8 | 95.0 | - | $4 / $20 (2026-10-17 lookup) |
| Claude Sonnet 5.5 | 6 / 2 / 12 | 70.6 | 71.0 | 61.9 | - | - | 80.5 | - | $2 / $10 |
| Claude Haiku 5.5 | 24 / 40 / 22 | 39.2 | - | 43.8 | - | - | 46.3 | - | $0.10 / $0.50 (prompts up to 100K) |
| GPT-6 Astra | 3 / 5 / 7 | 57.9 | 74.1 | 65.5 | 72.6 | 71.8 | 97.6 | 85.4 | $10 / $50 |
| GPT-6 Sol | 11 / 13 / 36 | - | 68.8 | - | 60.5 | - | 90.0 | 66.3 | $2 / $10 |
| GPT-6 Luna | 46 / 41 / 45 (agentic estimated) | - | 66.6 | - | - | - | 56.1 | 34.2 | $0.10 / $0.50 |
| Gemini 4 Argon | 5 / 6 / 4 (agentic estimated) | 57.4 | 77.9 | 55.0 | 69.2 | 84.2 | 78.0 | 83.4 | $2 / $10 until 2026-11-30, then $4 / $20 |
| Gemini 3.8 Flash | 27 / 19 / 17 | 19.1 | 73.8 | 19.6 | 59.0 | - | 22.0 | - | $0.75 / $3.75 until 2026-12-31, then $1.50 / $7.50 |
| Grok 4.7 (xAI, via Cursor) | not ranked | 38.0 | 71.0 | 29.5 | - | - | 17.1 | - | $2 / $6 (prompts under 200K) |
| Grok 4.6 (xAI, via Cursor) | 22 / 21 / 10 | - | 65.9 | 25.3 | - | - | 31.7 | - | $2 / $6 (prompts under 200K) |
| Composer 2.5 (Cursor) | not ranked | - | - | - | - | - | - | - | $0.50 / $2.50 |

A dash means BenchLM holds no current score for that model on that board.

## Other figures that matter for routing

Same source.

- **Long context:** Gemini 4 Argon GraphWalks BFS 128K 99.7. GPT-6 Astra MRCR v2 256-512K 100,
  512K-1M 96.3 (no other model here has an MRCR v2 score in BenchLM). Grok 4.7's context window is
  500K, Composer 2.5's 200K (BenchLM catalogue).
- **Vision, video, documents:** Gemini 4 Argon LVBench (long video) 91.7, Gemini 3.8 Flash 87.1;
  Chartography without tools: Argon 71.6, Opus 5.5 64.4, Sonnet 5.5 61.6, Haiku 5.5 46.4 (with
  tools Opus 89.0, Sonnet 90.2); ExtractBench (LlamaIndex): Sol 94.6, Luna 91.0, Flash 80.7;
  ExtractBench Pro: Astra 58, Opus 51, Sonnet 32, Argon 30, Luna 0.
- **Computer use:** OSWorld 2.1 Offline: Opus 5.5 87.2, Sonnet 5.5 83.9, Argon 74.7, Haiku 5.5 72.4,
  Luna 48.9.
- **SWE-bench Pro:** Opus 5.5 89.9, Sonnet 5.5 81.3, Fable 5.1 81.2 (this settles the 5.1 figure
  that was unresolved on 2026-10-17).
- **CursorBench 4.0** (Cursor's own benchmark): Opus 5.5 57.8, Sonnet 5.5 55.5, Fable 5.1 51.8,
  Grok 4.7 46.3, Grok 4.6 41.4, Gemini 3.8 Flash 39.6, Composer 2.5 27.7.
- **Composer 2.5's only other scores** are Terminal-Bench 2.0 69.3 and CursorBench 3.1 / 3.2
  (63.2 / 56.1). Terminal-Bench 2.0 is an older version and cannot be compared with 4.0.
- **Bug Hunt Bench:** Sonnet 5.5 51.3, Astra 45.0, Fable 5.1 43.0, Opus 5.5 41.7, Argon 40.7,
  Grok 4.7 29.0, Grok 4.6 27.0, Haiku 5.5 21.5, Luna 18.3, Flash 18.0.
- **Security:** ExploitGym: Astra 42.4, Argon 39.5, Sol 22.1, Luna 11.6.
- **Prompt injection:** Gray Swan IPI (15 attempts): Argon 0.7, Fable 5.1 1, Opus 5.5 1, Flash 5.5,
  Astra 8.5, Sol 10.1, Grok 4.6 51.8. BenchLM does not state the unit or direction; if it is the
  attack success rate, as the benchmark name suggests, Grok 4.6 is far easier to hijack than the
  rest. Check Grok's work on untrusted content (web pages, issue text, logs from outside) with that
  in mind until a Grok 4.7 figure says otherwise.
- **Independent index:** Epoch Capabilities Index (CC BY 4.0, not vendor-reported): Opus 5.5
  168.8, Astra 168.8, Fable 5.1 166.5, Sonnet 5.5 166.2, Sol 163.7, Haiku 5.5 159.3, Luna 156.8,
  Grok 4.6 156.6, Grok 4.7 154.4. No Gemini or Composer model here has an ECI score yet.

## Cautions specific to this lookup

- Gemini 3.8 Flash's scores disagree with each other (DeepSWE 73.8 against Terminal-Bench 4.0 19.1
  and FrontierSWE v2 19.6). Grok 4.7 shows the same pattern (DeepSWE 71.0 against FrontierSWE v2
  29.5). Do not rank either higher for agentic coding on the strength of DeepSWE alone.
- Gemini 4 Argon's agentic rank is an estimate with no direct agentic source; its coding rank rests
  on one source family. It is five weeks old (released 2026-09-30).
- Grok 4.7 (released 2026-09-21) and Composer 2.5 (2026-05-18) have no BenchLM ranking. Composer's
  evidence is almost all from its maker's own benchmark.
- Gemini 4 Carbon (released 2026-10-28) ranks first overall on BenchLM but `agy models` did not
  offer it on this account on 2026-11-02. Do not route to it until it appears there.
- GPT-6.1 Sol ranks above GPT-6 Sol on BenchLM; it is a different model and says nothing about
  GPT-6 Sol.
- Both Gemini prices are introductory and double on the dates shown.
