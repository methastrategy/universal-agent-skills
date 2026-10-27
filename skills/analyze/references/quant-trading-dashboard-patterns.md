# Quantitative Trading Dashboard Patterns

Patterns observed in manifest-driven quant trading dashboards (MeaHub / formerly MeEA Dashboard).

## 1. Manifest-Driven Architecture

Single JSON file as source of truth for all algorithmic entities. ~1.8 MB manifest for tens of EAs. Each EA contains: metadata, metrics, per-window benchmarks, empirical results for multiple account types, presets, source code. Git-tracked, partly rebuilt via Python pipeline from benchmark CSVs, partly hand-edited.

**Pitfall:** Two copies exist — `src/data/ea-manifest.json` (what the UI actually imports) and `public/data/eas/*.json` (a static per-EA dump). Editing only the public dump changes nothing on screen. Update both, or verify which one the component imports first.

**Pitfall:** Manifest grows large — consider splitting into per-EA files + index for >100 EAs.

## 2. Multi-Capital Empirical Data Pattern

Each EA stores empirical results for multiple account types side-by-side: USD_STANDARD (XAUUSDm) and USC_CENT (XAUUSDc). UI switches capital tier ($10/$30/$50/$100) and account category → client-side engine selects empirical data or scales dynamically with ruin guardrail.

**Pitfall:** Scaling logic must verify margin call risk — maxDrawdownUSD >= capital = liquidation.

**Pitfall:** Windows come from different runs with different units. Cent-account windows show `0.0x`, USD-standard audit runs show `30–44`. Never average or sum across windows without checking the account type the number came from.

## 3. 5-Gate Institutional Criteria Engine

Domain-specific evaluation logic (src/lib/ea-criteria.ts):
- Gate 0: Toxicity (Martingale, Grid, No-SL, DD>60%) — Hard Block
- Gate 1: Core Stats (PF, MaxDD, Recovery Factor) — 15 pts
- Gate 2: Entry Quality (4M WR, Expectancy, Payoff, Horizons, Entry Eff.) — 45 pts
- Gate 3: Consistency (Cons Losses, Degradation, CV of WR) — 25 pts
- Gate 4: Risk-Adjusted (Sharpe, Calmar) — 15 pts

Tier Thresholds: >=80 CHAMPION | 65-79 LAB_STAGE2 | 45-64 LAB_STAGE1 | <45 ARCHIVE

Hybrid Score (Model 1): 65% Current Regime (1W/30D/4M) + 35% Survivability (1Y/2Y) — caps at 42 if 2Y PnL<=0 or DD>25% or Horizons<50%.

**Pitfall (fixed pattern):** Gate 0 toxicity by naive substring search flags `anti-martingale`, `no martingale`, `ไม่มีการเบิ้ล martingale`. Use negation-aware matching: scan each occurrence and look back ~40 chars for `anti|no|zero|not|never|without|ไม่มีการ|ไม่ใช้|ไม่มี|ปราศจาก` before flagging. Genuine retirement notes (`contains toxic martingale/grid sizing`) must still trip.

**Pitfall:** A declared tier and a computed tier are different things. Always expose both and flag divergence — a manifest can declare 15 CHAMPION while 0 actually pass the gate.

### 3.1 Champion promotion gate
Separate evidence from quality: **hard gates** (toxicity, USD audit, USC audit when dual, 2Y/12M/4M/30D backtests present, source assets) plus **soft gates** (score thresholds, survivability, PF, DD cap). Report `readinessPct` = share of hard gates passed so the UI can show what is missing instead of a bare yes/no.

**Pitfall:** Set score thresholds from the observed distribution, not from round numbers. If the best EA in the whole set scores 64, a `>= 80` Champion bar guarantees zero champions forever — measure max/median first, then pick.

### 3.2 Missing-data imputation
When a scoring window has no data, do **not** score it 0 (punishes missing data as if it were bad performance) and do **not** impute the mean ratio of the other windows (rewards sparse EAs above fully-observed ones). Impute conservatively — e.g. `min(meanRatio, 0.5) * 0.8` — and assert the invariant in a test: a no-data EA must not outrank a fully-observed EA with mediocre results.

## 4. Python Build Pipeline for Manifest Generation

scripts/build_ea_manifest.py ingests reports/{EA_NAME}_benchmark/{EA_NAME}_results.csv and outputs src/data/ea-manifest.json.

**Pitfall:** CSV column names must match exactly (net_profit, total_trades, win_rate, profit_factor, equity_dd_pct, payoff_ratio).

## 5. localStorage Auth Vault with Seeded Accounts

Key: `meea_accounts_vault_v1`. Roles: OWNER | VERIFIED_DEVELOPER | COMMUNITY. Seed password hash comes from `MEEA_SEED_PASSWORD_HASH` with a built-in fallback.

**Pitfall:** All auth decisions happen client-side in localStorage — any user can rewrite their session from DevTools. It is a UI gate, not a security boundary. Never describe it as secure; if multi-user exposure matters, move verification to a route handler with an httpOnly cookie.

**Pitfall:** Do not copy the seeded password or its hash into skills, docs, or tickets. Refer to the env var only.

## 6. Benchmark Window Taxonomy

Curated volatility windows across 3 scales: 1 Month (6), 2 Month (1), 4 Month (3), Custom (12M02, 30D, 1W, 5TD). Each has dangerLevel (EXTREME/HIGH/CRITICAL).

**Pitfall:** Window names differ per producer (`1W_Latest`, `4M_2025`, `30D_Latest`, `30D_Latest_champion_oos`). When matching reports to windows, normalise the filename (strip non-alphanumerics) before token matching — `1W_Latest` will not match a naive `'1wlatest' in name` test because of the underscore. Exclude `champion_oos` variants from baselines.

## 7. Tech Stack Signature

Next.js 16 + React 19, Tailwind v4, Three.js, lucide-react, React Context + localStorage, `/api/manifest`, `/api/telemetry` (6s polling).

**Pitfall:** Importing the manifest from a `'use client'` context ships the whole JSON (plus embedded `source_code`) into the JS bundle. Fetch it in a server component or API route instead; measure bundle size before/after.

## 8. Client-inlined env secrets

`NEXT_PUBLIC_*` variables are inlined into the client bundle — anyone with the URL can extract them. For a telemetry bridge that means an attacker can POST forged state (fake profit, hidden drawdown).

Correct split:
- **Read**: `GET` is public read-only, no credential.
- **Write**: `POST` requires a server-only var (`MEEA_TELEMETRY_TOKEN`), compared against `Bearer <token>`.
- **Fail closed**: if the server var is unset, return 503. `if (expectedToken && ...)` silently opens the endpoint when config is missing.
- Add a per-IP rate limit.

Verify by running the built app and asserting `GET 200`, `POST` no-token `401`, `POST` bad-token `401`, and grepping `.next/static` for the env name (must be absent).

## 9. Snapshot tests for the scoring engine

The criteria/promotion engines are pure functions (`EAItem → evaluation`), which makes them ideal snapshot targets and the cheapest regression net for a manifest-driven dashboard.

- `vitest@^3` when the project pins `@types/node@^20` (vitest 5 requires `>=22`).
- Alias `@` via `fileURLToPath(new URL('./src', import.meta.url))` in `vitest.config.ts`.
- Snapshot: per-EA `{id, totalScore, hybridScore, qualifiedTier, gate scores}` and a tier/eligibility distribution block so drift is visible in the diff.
- Round floats (`toFixed(3)`) or every run produces noise.
- Add unit cases for the heuristics that are easy to regress: negation-aware toxicity, hard-block ⇒ score 0, survivability cap, USD/USC verification boundaries, `eligible === evidenceComplete && qualityComplete`.

**Value proof:** these tests immediately caught (a) imputation ranking sparse EAs above full-data EAs, and (b) a tier union missing a value that exists in the real manifest (`EXPERIMENTAL`), which `tsc` only surfaced through the test file.

## 10. Provenance audit of displayed metrics

Before trusting any dashboard number, reconcile it against the raw artifacts:

1. Parse every report file (`reports/**/*.htm*`, MT5 HTML/UTF-16) into `{net_profit, profit_factor, total_trades, win_rate, max_drawdown_pct}`.
2. Index by `(normalised_ea_key, window)`.
3. For each manifest metric window emit `MATCH` (|Δ| ≤ 0.02 and identical trade count) / `MISMATCH` / `NO_BASELINE`.
4. Publish counts per window, not a single “verified” badge.

**Expect this to hurt:** in practice 1W/4M matched well while 12M had a report for ~1 of 50 EAs and 2Y had none — meaning a third of the composite score came from unverifiable data. Report that explicitly; it changes how the score should be weighted.

## 11. Audit Checklist for Quant Dashboards

- Manifest is single source of truth, and every viewer reads that same file
- Empirical data exists for BOTH account types, with units distinguished
- Criteria engine gates are deterministic and snapshot-tested
- Hybrid score survivability gate caps at 42 for failed 2Y metrics
- Missing windows imputed conservatively, never zeroed or mean-filled
- Declared tier shown alongside computed tier, divergence flagged
- Preset files (.set) referenced by the manifest actually exist in `public/presets/`
- No `NEXT_PUBLIC_*` secret; write endpoints fail closed and are rate limited
- localStorage keys are versioned (v1 suffix) and acknowledged as UI-only auth
- All EAs have magic_number for MT5 identification
- Benchmark windows cover regime diversity, and every displayed window has a `source_report` path
