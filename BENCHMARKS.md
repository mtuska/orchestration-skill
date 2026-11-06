# Model benchmarks

Updated 2026-11-06. Compare within the same source, benchmark version and effort level.
Scores guide model selection; they do not prove local task success. Repeated results across
sources are not independent evidence. `—` means unavailable or unverified in this snapshot.

## BenchLM

[Source](https://benchlm.ai/). Historical BenchAlign v5.8 snapshot: data 2026-10-29,
retrieved 2026-11-02. Effort/harness details are incomplete; some results are provider-reported.
Ranks are overall / coding / agentic (lower is better); benchmark scores are higher-is-better.

| Model | Ranks | Terminal-Bench 4.0 | DeepSWE | FrontierSWE v2 |
|---|---|---|---|---|
| Claude Fable 5.1 | 7 / 4 / 2 | 55.8 | 67.4 | 56.3 |
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

*Agentic rank estimated. The 6.1 models were not verified in this BenchLM snapshot.
Flash and Grok scores vary sharply by benchmark; do not select them on DeepSWE alone.

## Artificial Analysis

[Leaderboard](https://artificialanalysis.ai/leaderboards/models), fetched 2026-11-06.
Intelligence Index v5.0.1 (higher is better); cost/time are per AA index task, not our jobs.
Medium effort where listed; otherwise high. Effort differs across rows—this is not a controlled
same-effort comparison. GPT-6 Sol, Grok 4.6 and Composer 2.5 were not in the fetched table.

| Model | Effort | Intelligence Index | Cost/task | Time/task |
|---|---|---|---|---|
| Claude Fable 5.1 | medium | 43 | $5.56 | 9.5 min |
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
substitutes for current revisions; Sol/Terra 6.1 were not present. Listing does not imply CLI availability.

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
retrieved 2026-11-06. General capability composite; higher is better. Intervals are Epoch's
reported credible bounds; effort is not specified in this export. Overlapping intervals do not
establish a clear ranking. Credit: Epoch AI, CC BY 4.0. Composer 2.5 was absent from the export.

| Model | ECI | Credible interval |
|---|---|---|
| GPT-6 Astra | 169.07 | 166.16–172.28 |
| GPT-6.1 Sol | 168.94 | 165.97–172.19 |
| Claude Opus 5.5 | 168.36 | 165.54–171.51 |
| GPT-6.1 Terra | 167.82 | 164.88–171.17 |
| Claude Fable 5.1 | 166.90 | 164.27–169.85 |
| Gemini 4 Argon | 166.45 | 163.83–169.38 |
| Claude Sonnet 5.5 | 166.24 | 163.52–169.23 |
| GPT-6 Sol | 164.06 | 161.58–166.80 |
| Claude Haiku 5.5 | 160.22 | 158.04–162.57 |
| Gemini 3.8 Flash | 158.63 | 156.65–160.79 |
| Grok 4.6 | 157.92 | 155.99–160.09 |
| GPT-6 Luna | 156.68 | 154.78–158.74 |
| Grok 4.7 | 156.07 | 154.20–158.03 |

Keep this file to one table per source. Add models to the relevant table, retain dates and effort,
and refresh sources before changing routing. Detailed historical scores, pricing and caveats are
preserved in the [research snapshot](references/benchmark-snapshot-2026-11-06.txt); read it only
when a task needs those details.
