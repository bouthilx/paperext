# Model Cost Analysis — Backend Bake-off (WS-B)

*Decision record for [#29](https://github.com/bouthilx/paperext/issues/29) (B2, OpenAI cost analysis) extended to the Anthropic and Google arms (B3, Vertex cost estimation). Feeds A8 (the model to pin) and B1 (the bake-off). Runnable now, no GCP required.*

*Date: 2026-07-24. Prices are current published rates as of this date.*

## TL;DR

- Eight candidate models compared, aligned into three **cost bands** (not capability tiers): **3 OpenAI + 3 Claude + 2 Gemini**. Gemini contributes only 2 because its most expensive model is priced at the *mid* band — it has no frontier entry.
- Full-corpus cost (fresh 2023–2026 + 2024 re-extraction ≈ **3,986 single-paper calls**) ranges **~$117 (Claude Haiku) to ~$615 (OpenAI Sol)**. Everything is cheap; **cost does not gate the choice — extraction accuracy (the B1 bake-off) does.**
- **Claude Haiku 4.5 (~$117) is the single cheapest of all eight** — cheaper than Gemini 3.6 Flash (~$176), because this workload is input-dominated (~22.1k in / 1.46k out per paper) and Flash's $1.50 input rate is 50% above Haiku/Luna's $1.00. The "Gemini is always cheapest" intuition **breaks on an input-heavy extraction workload.**
- In the frontier band, **Claude Opus 4.8 (~$586) ≈ OpenAI Sol (~$615)** — near-identical, Opus marginally cheaper on the lower output rate.
- Prompt/context caching saves **~3.5–3.7% everywhere** — a non-lever: only the ~1.2k-token shared system+schema prefix is cacheable; the paper body dominates input and is unique per call.

## 1. Token-volume baseline

Derived from the `usage` blocks of the **2110 stored 2024 OpenAI extractions** (`data/mdl/queries/openai/legacy-2024/`; 0 missing). These are 1999 unique papers; 111 have a second legacy call (`_01`, an old two-prompt pass). The current pipeline issues **one call per paper**, and the `_00`-only means (22.1k in / 1.48k out) are within 1% of the all-2110 means, so the full sample is used.

| Metric | Input (prompt) tokens | Output (completion) tokens | Total |
|---|---:|---:|---:|
| mean | 22,093 | 1,464 | 23,556 |
| median | 18,999 | 1,274 | 20,433 |
| p90 | 38,857 | 2,552 | 40,289 |
| p95 | 48,979 | 3,034 | 50,830 |
| p99 | 78,290 | 4,240 | 81,304 |
| min | 1,555 | 269 | 1,853 |
| max | 240,713 | 7,215 | 244,446 |

Validation subset (110 papers): mean **21,641 input / 1,132 output**.

Notes:
- Output is tiny (~6.6% of input) — the extraction is a compact structured object.
- Input scales ~linearly with paper length (~1.86 tokens/word median; regression `prompt ≈ 1.2k + 2.0·words`). The ~1.2k intercept is the cacheable fixed prefix.
- **Projections use the mean** (correct estimator for a corpus total = n × mean). The distribution is right-skewed, so mean > median.

> **Tokenizer caveat (the main cross-provider approximation).** Token counts are measured on OpenAI's tokenizer. Claude and Gemini tokenize the same text differently — Claude is close; Gemini can differ by roughly ±10–15% on technical text. The Claude and Gemini dollar figures therefore carry ~±10–15% uncertainty from token-count drift alone. Treat cross-provider gaps smaller than that as noise; the band structure and the "cost doesn't decide" conclusion are robust to it.

## 2. Candidate models + pricing (aligned by cost band)

Accuracy is the gating constraint (see B1); this grid is for the cost dimension only. Input / cached-input / output, per 1M tokens. Claude-on-Vertex per-token rates match Anthropic first-party rates (Vertex adds enterprise packaging at ~10% premium; token rates unchanged). Gemini rates are Vertex standard tier. There is no high-accuracy `-mini`/`nano` in the GPT-5.6 family — `luna` is its low tier.

| Cost band | Model | Input | Cached | Output | Notes |
|---|---|---:|---:|---:|---|
| **High** | OpenAI `gpt-5.6-sol` | 5.00 | 0.50 | 30.00 | |
| **High** | Claude Opus 4.8 | 5.00 | 0.50 | 25.00 | |
| **High** | *(no Gemini)* | — | — | — | Gemini tops out below this band |
| **Mid** | OpenAI `gpt-5.6-terra` | 2.50 | 0.25 | 15.00 | |
| **Mid** | Claude Sonnet 5 | 3.00 | 0.30 | 15.00 | intro $2 / $0.20 / $10 through 2026-08-31 |
| **Mid** | Gemini 3.1 Pro | 2.00 | 0.20 | 12.00 | >200K input → $4 / $18 (2× in, 1.5× out) |
| **Low** | OpenAI `gpt-5.6-luna` | 1.00 | 0.10 | 6.00 | |
| **Low** | Claude Haiku 4.5 | 1.00 | 0.10 | 5.00 | |
| **Low** | Gemini 3.6 Flash | 1.50 | 0.15 | 7.50 | flat (no >200K surcharge) |

The GPT-5.6 family (Sol/Terra/Luna) launched 2026-07-09: 1.05M-token context, 128K max output; cached-input reads are 90% cheaper, cache writes 1.25× with a 30-min minimum. Cheaper Gemini alternative not costed in the grid: **Gemini 3 Flash Preview** ($0.50 / $3) would be the cost floor of all options at **~$62 corpus** — below Haiku — if it clears the accuracy bar in B1. Above the whole grid sits **Claude Fable 5** ($10/$50), a tier above Sol — excluded as not GPT-5.6-comparable.

## 3. Cost projection

Volume: **3,986 single-paper calls** — fresh 2023–2026 (~1987 papers) + 2024 re-extraction (~1999). Validation set = **110 papers** (one B1 bake-off arm), using its own means. Per-paper cost = (mean_in × input + mean_out × output) / 1e6.

| Band | Model | $/paper | **Val. set (110)** | **Corpus (3986)** | w/ caching | Cache saving |
|---|---|---:|---:|---:|---:|---:|
| High | OpenAI Sol | 0.1544 | 15.64 | **615.3** | 593.8 | 3.5% |
| High | Claude Opus 4.8 | 0.1471 | 15.02 | **586.2** | 564.6 | 3.7% |
| Mid | OpenAI Terra | 0.0772 | 7.82 | **307.7** | 296.9 | 3.5% |
| Mid | Claude Sonnet 5 (std) | 0.0882 | 9.01 | **351.7** | 338.8 | 3.7% |
| Mid | Claude Sonnet 5 (intro) | 0.0588 | 6.01 | **234.5** | 225.9 | 3.7% |
| Mid | Gemini 3.1 Pro | 0.0617 | 6.26 | **247.1** | 237.5 | 3.5% |
| Low | OpenAI Luna | 0.0309 | 3.13 | **123.1** | 118.8 | 3.5% |
| Low | Claude Haiku 4.5 | 0.0294 | 3.00 | **117.2** | 112.9 | 3.7% |
| Low | Gemini 3.6 Flash | 0.0441 | 4.50 | **175.8** | 169.4 | 3.7% |

### Surcharges and caching

- **Large-context surcharges barely bind.** Max observed input is 240,713 tokens — under OpenAI's 272K threshold (0 calls affected), and Opus 4.8 / Sonnet 5 are priced flat with no long-context premium at these sizes. Gemini 3.1 Pro's >200K surcharge hits only **1 of 2110 sampled calls (0.05%)**, adding ~$1 to its corpus total (flat would be $246.1).
- **Caching is a non-lever (~3.5–3.7%).** The message is `system prompt + tool schema + "…following research paper:\n" + {paper text}`, so the paper body sits at the end and is unique per call. Only the fixed prefix — empirically **~1,200 tokens** (regression intercept; bounded above by the 1,555-token minimum prompt) — is a cacheable shared prefix, ~5% of mean input. Even at a 100% prefix cache-hit rate the total drops only ~3.5–3.7%. Worth enabling (it's automatic and free) but it should not influence model choice.

## 4. Reading the results

**By band, cheapest first:**
- **High:** Opus 4.8 ($586) < Sol ($615). Near-identical; Opus edges it on the $25 vs $30 output rate.
- **Mid:** Sonnet 5 intro ($234) < Gemini 3.1 Pro ($247) < Terra ($308) < Sonnet 5 std ($352). If extraction runs before **2026-08-31**, Sonnet's intro rate is the mid-band floor; at standard rates Gemini 3.1 Pro is cheapest.
- **Low:** Haiku 4.5 ($117) < Luna ($123) < Gemini 3.6 Flash ($176).

**Two findings worth flagging:**
1. **Gemini is not automatically cheapest here.** On list *input* price Gemini undercuts each rung, but this workload spends ~94% of its tokens on input, and Gemini 3.6 Flash's $1.50 input rate is 50% above the $1.00 low-band rate — so Flash lands *above* the entire low band. Gemini wins only where its input rate is competitive (Pro, mid band).
2. **The spread is small in absolute terms.** Frontier-to-floor is ~$117 → ~$615 across the whole two-corpus run. Against Mila's budget this is immaterial — which is why the bake-off should decide on extraction accuracy, and cost only breaks ties.

## 5. Recommendation for the bake-off (B1)

Cost clears every candidate, so carry the **accuracy-credible** models into B1 and let `evaluate.py` decide on precision/recall:

- **Frontier arm:** Sol vs Opus 4.8 — cost-equivalent (~$0.15/paper); pick on accuracy alone.
- **Mid arm:** Terra vs Sonnet 5 vs Gemini 3.1 Pro — all ~$0.06–0.09/paper; Gemini Pro's accuracy is the open question (prior: it trails Sol/Opus meaningfully).
- **Low arm:** Luna vs Haiku 4.5 — both ~$0.03/paper and cheapest overall; worth scoring, since if either clears the bar the whole run costs ~$120.

Running any single arm over the validation set costs **$3–16** (the Val. set column) — trivial. There is **no cost reason to prune the bake-off**; prune only on expected accuracy.

**What A8 pins / B1 runs:** whichever model wins B1 on accuracy within the cheapest band that clears the bar. B2's OpenAI-only recommendation was `gpt-5.6-terra` (with `gpt-5.6-luna` as the cost-floor fallback); the cross-provider view adds Claude Haiku/Sonnet and Gemini Pro/Flash as equally cost-viable arms.

---

*Reproduction: `tokens.py`, `project.py`, `valset.py`, and `eight.py` in the analysis scratchpad read only the `usage` blocks under `data/mdl/queries/openai/legacy-2024/`.*
*Sources: OpenAI pricing — aipricing.guru, tldl.io, devtk.ai. Gemini/Claude Vertex pricing — cloud.google.com/vertex-ai/generative-ai/pricing, cloudzero.com. Claude API — claude-api reference (cached 2026-06-24).*
