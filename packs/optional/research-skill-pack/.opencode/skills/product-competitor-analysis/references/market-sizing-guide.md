# Market Sizing Guide: TAM, SAM, SOM for Product Decisions

## 1) Why market sizing is often wrong
Teams overestimate opportunity when they confuse theoretical demand with reachable demand.
Use sizing to prioritize strategy, not to justify a preselected plan.

## 2) Definitions you must keep separate

- TAM (Total Addressable Market): total demand if constraints did not exist.
- SAM (Serviceable Addressable Market): demand in your target segment and model.
- SOM (Serviceable Obtainable Market): realistic near-term capture under execution limits.

Never present TAM as forecasted revenue.

## 3) Top-down vs bottom-up (when to use each)

## Top-down

Start from industry-wide totals and narrow by filters.

Use when:

- you need fast directional framing,
- reliable macro datasets are available,
- product category boundaries are clear.

Risk:

- hidden assumptions multiply quickly.

## Bottom-up

Build from unit economics and reachable customer counts.

Use when:

- GTM model is defined,
- pricing model is known,
- segment access assumptions are explicit.

Risk:

- optimistic conversion assumptions inflate results.

Best practice: run both and reconcile gaps.

## 4) TAM calculation patterns

Pattern A (spend-based):

TAM = total buyers x annual category spend per buyer

Pattern B (usage-based):

TAM = total usage units x price per usage unit

Pattern C (outcome-replacement):

TAM = current cost of workaround x replaceable share

Show formula, data source, and adjustment factors.

## 5) SAM calculation patterns

SAM filters TAM by practical applicability.

Common filters:

- geography,
- industry vertical,
- company size,
- compliance constraints,
- required integration ecosystem,
- acceptable price range.

Template:

SAM = TAM x segment fit rate x channel reach rate x model compatibility rate

## 6) SOM calculation patterns

SOM should reflect execution reality in 12-36 month horizon.

Template:

SOM = SAM x reachable accounts x win rate x ramp factor

Where:

- reachable accounts = accounts you can actually engage,
- win rate = expected conversion under competition,
- ramp factor = adoption speed over time.

Use scenario ranges (low/base/high), not single-point precision.

## 7) Data source stack (recommended)

Use a mixed-source stack:

- public filings and investor reports,
- analyst datasets and industry associations,
- government and trade statistics,
- first-party sales funnel or pilot data,
- channel partner and procurement signals.

Assign source reliability:

- Tier 1: audited or official,
- Tier 2: reputable third-party,
- Tier 3: self-reported or proxy.

## 8) Common estimation traps

Trap 1: Double counting segments across channels.
Trap 2: Using global TAM for local launch strategy.
Trap 3: Ignoring replacement cycles and switching costs.
Trap 4: Treating survey intent as purchase behavior.
Trap 5: Extrapolating from tiny pilots without confidence bounds.
Trap 6: Assuming stable pricing despite competitive pressure.

## 9) Confidence and sensitivity reporting

Always publish sizing with confidence labels and sensitivity tests.

Sensitivity checklist:

- +/-20% on pricing,
- +/-20% on reachable account counts,
- +/-10% on win rate,
- alternative adoption ramp assumptions.

If result flips strategy under modest assumption shifts,
state explicitly that decision confidence is low.

## 10) Decision-ready output template

Use this compact structure:

1. TAM/SAM/SOM numbers as ranges.
2. Formulas and key assumptions.
3. Source table with reliability tiers.
4. Sensitivity summary.
5. Strategic implication (where to focus first).
6. Validation plan for highest-uncertainty assumption.

## 11) Example (B2B compliance automation)

Assumptions: mid-market regulated verticals, ACV 20k-60k, 2,500 reachable year-2 accounts, base win rate 12%.
Result: TAM too broad for phase 1, SAM supports vertical-first, SOM favors one-vertical beachhead.
Action: prioritize lower-friction segment and validate win-rate via 10-15 design partner cycles.
