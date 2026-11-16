# Model benchmarks

Updated 2026-11-09; source dates below. Compare within the same source, benchmark version and effort level.
Scores guide model selection; they do not prove local task success. Repeated results across
sources are not independent evidence. `—` means unavailable or unverified in this snapshot.

## BenchLM

[Source](https://benchlm.ai/). Historical BenchAlign v5.8 snapshot: data 2026-10-29,
retrieved 2026-11-02. Effort/harness details are incomplete; some results are provider-reported.
Ranks are overall / coding / agentic (lower is better); benchmark scores are higher-is-better.

| Model | Ranks | Terminal-Bench 4.0 | DeepSWE | FrontierSWE v2 |
|---|---|---|---|---|
| Claude Fable 5.2 | — / 1 / 1 | 67.6 | 74.3 | 69.9 |
| Claude Opus 5.5 | 2 / 1 / 1 | 66.4 | 74.2 | 62.3 |
| Claude Sonnet 5.5 | 6 / 2 / 12 | 70.6 | 71.0 | 61.9 |
| Claude Haiku 5.5 | 24 / 40 / 22 | 39.2 | — | 43.8 |
| GPT-6 Astra | 3 / 5 / 7 | 57.9 | 74.1 | 65.5 |
| GPT-6 Sol | 11 / 13 / 36 | — | 68.8 | — |
| GPT-6.1 Sol | — | — | — | — |
| GPT-6.1 Terra | — | — | — | — |
| GPT-6 Luna | 46 / 41 / 45* | — | 66.6 | — |
| Gemini 4 Argon | 5 / 6 / 4* | 57.4 | 77.9 | 55.0 |
| Gemini 3.8 Flash | 27 / 19 / 17 | 19.1 | 73.8 | 19.6 |
| Grok 4.7 | — | 38.0 | 71.0 | 29.5 |
| Grok 4.6 | 22 / 21 / 10 | — | 65.9 | 25.3 |
| Composer 2.5 | — | — | — | — |

[Fable 5.2](https://benchlm.ai/models/claude-fable-5-2) refreshed 2026-11-09; its ranks use a newer
cohort. Its Terminal-Bench/DeepSWE scores are provider-reported; FrontierSWE links to the evaluator.

*Agentic rank estimated. The 6.1 models were not verified in this BenchLM snapshot.
Flash and Grok scores vary sharply by benchmark; do not select them on DeepSWE alone.

## Artificial Analysis

[Leaderboard](https://artificialanalysis.ai/leaderboards/models): Fable 5.2 refreshed 2026-11-09;
other rows fetched 2026-11-06.
Intelligence Index v5.0.1 (higher is better); cost/time are per AA index task, not our jobs.
Medium effort where listed; otherwise high. Effort differs across rows—this is not a controlled
same-effort comparison. GPT-6 Sol, Grok 4.6 and Composer 2.5 were not in the fetched table.

| Model | Effort | Intelligence Index | Cost/task | Time/task |
|---|---|---|---|---|
| Claude Fable 5.2 | medium | 56 | $3.80 | 8.3 min |
| Claude Opus 5.5 | medium | 48 | $2.45 | 6.8 min |
| Claude Sonnet 5.5 | medium | 31 | $0.78 | 3.6 min |
| Claude Haiku 5.5 | medium | 25 | $0.09 | 4.1 min |
| GPT-6 Astra | medium | 52 | $2.73 | 6.5 min |
| GPT-6.1 Sol | medium | 46 | $0.36 | 4.2 min |
| GPT-6.1 Terra | medium | 38 | $0.17 | 2.6 min |
| GPT-6 Luna | medium | 18 | $0.04 | 3.4 min |
| Gemini 4 Argon | high | 50 | $9.95 | 26.4 min |
| Gemini 3.8 Flash | medium | 30 | $6.26 | 11.8 min |
| Grok 4.7 | high | 35 | $6.18 | 20.7 min |

## DeepSWE / Datacurve

[Leaderboard](https://deepswe.datacurve.ai/), fetched 2026-11-06; page dated 2026-09-22.
All 21 entries in the fetched view, with exact model labels. 113 tasks, mini-swe-agent harness.
The v1/v1.1 selection and confidence level of ± values were not resolved. Older labels are not
substitutes for current revisions; Sol/Terra 6.1 were not present. Fable 5.2 remains absent as of
2026-11-09. Listing does not imply CLI availability.

| Model as published | Effort | Score | Cost/task |
|---|---|---|---|
| gpt-6-astra | xhigh | 74% ±3% | $4.43 |
| gemini-3.8-flash | high | 74% ±1% | $2.36 |
| claude-opus-5 | max | 74% ±4% | $11.84 |
| gpt-5.6-sol | max | 73% ±3% | $6.46 |
| claude-fable-5 | xhigh | 70% ±3% | $13.41 |
| glm-5.3 | max | 69% ±3% | $3.99 |
| kimi-k3 | max | 69% ±5% | $4.65 |
| grok-4.6 | medium | 67% ±2% | $3.45 |
| gpt-5.6-luna | max | 67% ±4% | $0.61 |
| gpt-5.5 | xhigh | 67% ±6% | $7.23 |
| gemini-3.7-flash | medium | 65% ±3% | $2.03 |
| glm-5.3-flash | max | 63% ±4% | $0.24 |
| deepseek-v4-pro | max | 63% ±6% | $1.67 |
| claude-opus-4.8 | max | 59% ±2% | $13.22 |
| qwen3.8-max | xhigh | 57% ±3% | $3.73 |
| muse-spark-1.2 | xhigh | 55% ±2% | $3.70 |
| claude-sonnet-5 | max | 54% ±4% | $26.40 |
| deepseek-v4-flash | max | 53% ±4% | $0.46 |
| gemini-3.6-flash | high | 47% ±4% | $2.21 |
| glm-5.2 | max | 44% ±2% | $3.92 |
| gemini-3.5-flash | high | 36% ±4% | $3.45 |

## Epoch AI

[Epoch Capabilities Index](https://epoch.ai/eci) · [score CSV](https://epoch.ai/data/eci_scores.csv),
retrieved 2026-11-09. General capability composite; higher is better. Intervals are Epoch's
reported credible bounds; effort is not specified in this export. Overlapping intervals do not
establish a clear ranking. Credit: Epoch AI, CC BY 4.0. Composer 2.5 was absent from the export.

| Model | ECI | Credible interval |
|---|---|---|
| Claude Fable 5.2 | 174.24 | 170.12–178.79 |
| GPT-6 Astra | 169.16 | 166.19–172.51 |
| GPT-6.1 Sol | 168.87 | 165.90–172.24 |
| Claude Opus 5.5 | 168.67 | 165.78–171.91 |
| GPT-6.1 Terra | 168.11 | 165.09–171.50 |
| Gemini 4 Argon | 166.53 | 163.88–169.53 |
| Claude Sonnet 5.5 | 166.32 | 163.65–169.35 |
| GPT-6 Sol | 164.00 | 161.51–166.81 |
| Claude Haiku 5.5 | 160.25 | 158.02–162.73 |
| Gemini 3.8 Flash | 158.66 | 156.59–160.92 |
| Grok 4.6 | 157.91 | 155.87–160.12 |
| GPT-6 Luna | 156.50 | 154.60–158.57 |
| Grok 4.7 | 156.05 | 154.15–158.13 |

## LLM Stats

[Leaderboard](https://llm-stats.com/) · [methodology v3.1](https://llm-stats.com/methodology/llm-stats-score),
retrieved 2026-11-09. Conservative composite ratings (higher is better, not percentages).
Category indexes use different benchmark subsets; effort is unspecified in this export.
Evidence mixes lab-reported, third-party and verified results; overlap with other sources is
not independent confirmation. Composer 2.5 was absent from the fetched data.

| Model | LLM Stats | Reasoning | Coding | Agent |
|---|---|---|---|---|
| Claude Fable 5.2 | 61.6 | 60.8 | 51.5 | 47.5 |
| Claude Opus 5.5 | 59.2 | 57.9 | 49.2 | 44.8 |
| Claude Sonnet 5.5 | 57.6 | 55.9 | 47.3 | 42.9 |
| Claude Haiku 5.5 | 49.0 | 46.2 | 38.5 | 33.1 |
| GPT-6 Astra | 57.0 | 55.6 | 45.5 | 43.5 |
| GPT-6 Sol | 47.2 | 44.0 | 33.3 | 34.5 |
| GPT-6.1 Sol | 53.2 | 50.4 | 39.0 | 37.7 |
| GPT-6.1 Terra | 47.3 | 48.6 | 36.4 | 38.0 |
| GPT-6 Luna | 42.9 | 39.1 | 29.0 | 29.9 |
| Gemini 4 Argon | 54.0 | 51.5 | 42.6 | 40.7 |
| Gemini 3.8 Flash | 48.7 | 45.8 | 34.4 | 33.6 |
| Grok 4.7 | 45.9 | 41.6 | 34.9 | 33.1 |
| Grok 4.6 | 44.3 | 46.3 | 32.6 | 34.0 |
| Composer 2.5 | — | — | — | — |

Keep this file to one table per source. Add models to the relevant table, retain dates and effort,
and refresh sources before changing routing. Detailed historical scores, pricing and caveats are
preserved in the [research snapshot](references/benchmark-snapshot-2026-11-06.txt); read it only
when a task needs those details.
