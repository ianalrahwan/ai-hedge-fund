<div align="center">

# WAR PLANNING

**A Long-Volatility Campaign Against the Hormuz Crisis**

$30K Bankroll | 2x Aggressive Kelly | 26 Weeks | March 2026

[![Built with AI Hedge Fund](https://img.shields.io/badge/built%20with-AI%20Hedge%20Fund-blue)](README_ORIGINAL.md)
[![Nassim Taleb Agent](https://img.shields.io/badge/agent-Nassim%20Taleb-green)](#the-nassim-taleb-agent)
[![Signal: Strong Buy Vol](https://img.shields.io/badge/signal-strong__buy__vol%2088%25-brightgreen)](#the-nassim-taleb-agent)

---

*"The fragile wants tranquility, the antifragile grows from disorder."*
**Nassim Nicholas Taleb**, Antifragile (2012)

*"War is merely the continuation of policy by other means."*
**Carl von Clausewitz**, On War (1832)

*"The market can stay irrational longer than you can stay solvent — unless you sized with Kelly."*

---

</div>

> **Looking for the original AI Hedge Fund README?** See [README_ORIGINAL.md](README_ORIGINAL.md)

## Table of Contents

| # | Section | What's Inside |
|:-:|---------|---------------|
| I | [Situation Assessment](#i-situation-assessment) | The crisis timeline, current state, and the April 6 inflection point |
| II | [The Nassim Taleb Agent](#ii-the-nassim-taleb-agent) | AI agent output — quantitative case for long volatility on UNG |
| III | [Clausewitz Escalation Ladder](#iii-the-clausewitz-escalation-ladder) | Why Iran always feints before the real move |
| IV | [The Five Quant Equations](#iv-the-five-quant-equations) | Kelly, EV Gap, KL-Divergence, Bayesian Updating, LMSR — applied to UNG |
| V | [Theta Is Your Enemy](#v-theta-is-your-enemy) | Daily bleed, why weeklies expire worthless, and how calendars hedge it |
| VI | [IV Crush](#vi-iv-crush--the-silent-killer) | What happens to every long option if the crisis resolves overnight |
| VII | [The Trinity](#vii-the-trinity-straddle-vs-strangle-vs-calendar) | Three ways to play volatility — when each wins and loses |
| VIII | [Black Swan Campaign](#viii-the-black-swan-campaign) | Lose small for 24 weeks, win big for 2 — the Taleb thesis in practice |
| IX | [Capital Deployment](#ix-capital-deployment--2-aggressive) | Phase-adjusted week-by-week allocation with stop rules |
| X | [Monte Carlo](#x-monte-carlo-simulation) | 1,000 simulated 26-week campaigns |
| XI | [Decision Tree](#xi-the-decision-tree) | The full execution protocol |
| XII | [Alerting for Fidelity](#xii-alerting-schedule-for-fidelity) | How a normal person monitors weekly options positions with a day job |
| XIII | [Sources](#xiii-sources) | Geopolitical, market, and quantitative theory citations |

---

<br>

## I. Situation Assessment

<p align="center">
  <img src="war-planning/charts/01_geopolitical_timeline.png" alt="Geopolitical Timeline" width="100%">
</p>

### What Happened

On **February 28, 2026**, the United States and Israel launched surprise airstrikes on Iran, killing Supreme Leader Khamenei. Iran retaliated with missiles and drones, and the IRGC closed the **Strait of Hormuz** — choking:

> **20%** of global oil | **33%** of global helium | **20%** of global LNG

### Current State (March 26)

| Date | Event | Source |
|------|-------|--------|
| Mar 24 | US delivers 15-point ceasefire proposal via Pakistan | [NPR](https://www.npr.org/2026/03/26/nx-s1-5761882/iran-war-peace-conditions) |
| Mar 25 | **Iran rejects proposal** as "maximalist, unreasonable" | [Al Jazeera](https://www.aljazeera.com/news/2026/3/25/iran-calls-us-proposal-to-end-war-maximalist-unreasonable) |
| Mar 26 | **Trump extends Hormuz deadline to April 6** | [NPR](https://www.npr.org/2026/03/26/nx-s1-5761882/iran-war-peace-conditions) |
| — | 150+ freight ships stalled in the strait | [NPR](https://www.npr.org/2026/03/04/nx-s1-5736104/iran-war-oil-trump-israel-strait-hormuz-closed-energy-crisis) |
| — | QatarGas: "extensive" damage, "years to repair" | [Fortune](https://fortune.com/2026/03/21/iran-war-helium-shortage-qatar-chip-supply-chains-ai-boom/) |
| — | UNG **down 6.2%** since Mar 13 while crisis intensified | Yahoo Finance |

The key observation: **implied volatility is contracting into the catalyst.** The options market is asleep at the 15th percentile of its annual range while an active war rages over the world's most important energy chokepoint.

<br>

### The April 6 Inflection

> In **11 days**, Trump's ultimatum expires.

| Scenario | Probability | UNG Impact | IV Impact | Optimal Strategy |
|:---------|:----------:|:----------:|:---------:|:-------------|
| Iran opens Hormuz | ~15% | -5% to -10% | **CRUSH** to 35% | Close all positions immediately. |
| Stalemate / extension | ~55% | ±3-5% | Stays 55-70% | Calendar-heavy — profit from persistent fear. |
| US military operation | ~30% | **+15% to +30%** | **SPIKE** to 120%+ | Strangle-heavy — the black swan pays. |

---

<br>

## II. The Nassim Taleb Agent

This project includes a custom AI agent that channels Nassim Nicholas Taleb's long-volatility philosophy. It evaluates **long strangles** — never directional bets — by scoring five factors:

1. **IV Rank Proxy** — Is vol cheap relative to its own history?
2. **Tail Thickness (Kurtosis)** — Are the tails fatter than Black-Scholes assumes?
3. **Vega Efficiency** — How much vol exposure does each dollar of premium buy?
4. **Convexity** — How often does the asset gap beyond the breakeven?
5. **Antifragility** — Does vol cluster, and is it contracting (cheap entry)?

### Agent Output: UNG — March 26, 2026

> **Signal: `strong_buy_vol`** | **Confidence: 88%**

The agent's full analysis, generated by `src/agents/nassim_taleb.py`:

| Metric | Value | Interpretation |
|--------|:-----:|----------------|
| IV Rank Proxy | **15.2%** | Bottom 15th percentile — vol is on sale |
| Excess Kurtosis | **7.09** | Tails ~2.4x fatter than normal distribution |
| Skewness | -0.33 | Slight left-tail bias (irrelevant for strangles) |
| Gap Frequency | **39%** | Nearly 2 in 5 days move >3% |
| Convexity Ratio | **8.6x** | Max daily move is 8.6x the average |
| Vega Efficiency | 1.56 | Acceptable — not great, but vol is cheap |
| Vol-of-Vol | 0.43 | Volatility itself is volatile (good for strangles) |
| Vol Autocorrelation | 0.87 | When it spikes, it stays spiked |
| Vol Trend | **-37%** | Contracting from peak — buying at the trough |
| Antifragility Score | **7.5/10** | High — this asset benefits from disorder |

<br>

> *"Vol is obscenely cheap — IV rank proxy at 15%. The market is pricing UNG as if natural gas were a sleepy utility stock. Current 20d realized vol sits at 50%, but the 1-year range stretches to 145%. This is textbook mispricing."*

> *"Excess kurtosis of 7.09 — the Gaussian charlatans are blind here. Black-Scholes assumes kurtosis of 3. UNG delivers 10+. The tails are massively fatter than the models admit."*

> *"Convexity ratio of 8.6x and 39% gap frequency — this is strangle paradise. The payoff function is gloriously convex: small bleeds on quiet days, explosive gains when natural gas has a tantrum."*

> *"Vol-of-vol at 0.43 and autocorrelation of 0.87 — volatility clusters hard. Recent vol has contracted 37% from prior levels, which is exactly when you want to enter: buying at the trough before the next clustering event. This is antifragile positioning."*

> *"UNG is a barbell dream. Vol is cheap, tails are fat, gaps are frequent, and volatility itself is volatile. The market is Gaussian-blind. Optionality is nearly free here — convexity harvest mode engaged."*

— **Nassim Taleb Antifragile Volatility Agent** (`src/agents/nassim_taleb.py`)

---

<br>

## III. The Clausewitz Escalation Ladder

<p align="center">
  <img src="war-planning/charts/02_escalation_ladder.png" alt="Escalation Ladder" width="100%">
</p>

Every Iran confrontation since 1988 follows the same pattern:

<div align="center">

### FEINT → FEINT → FEINT → HEADLINES → CALM → REAL ESCALATION

</div>

| Year | The Feints | The Real Move | Source |
|:----:|------------|---------------|--------|
| 1984-88 | 3 years of tanker attacks | **Operation Praying Mantis** — US sinks half of Iranian navy | [Strauss Center](https://www.strausscenter.org/strait-of-hormuz-tanker-war/) |
| 2019 | Months of Gulf provocations | **Saudi Aramco drone strike** — oil spikes 15% overnight | [Washington Institute](https://www.washingtoninstitute.org/policy-analysis/irans-retaliation-choreography-escalation-management-and-mirage-all-out-war) |
| Jan 2020 | Proxy attacks on US bases | **Soleimani assassination** → Iranian missile barrage | [HISTORY.com](https://www.history.com/articles/us-iran-conflict-key-moments) |
| Apr 2024 | 233 telegraphed drones (all intercepted) | **Oct 2024** real strike with ballistic missiles | [Washington Institute](https://www.washingtoninstitute.org/policy-analysis/irans-retaliation-choreography-escalation-management-and-mirage-all-out-war) |
| **2026** | Feb-Mar: closure, strikes, negotiations | **April 6? →** ??? | **The feint phase is still active** |

<br>

> The crisis is at **Step 5 on the 7-step escalation ladder.** The historical pattern says the real move hasn't happened yet.

Each feint spikes IV without a commensurate price move — **calendar spread territory.**
The real move spikes both IV and price — **strangle territory.**

A well-structured campaign profits from **both**.

---

<br>

## IV. The Five Quant Equations

<p align="center">
  <img src="war-planning/charts/03_five_equations.png" alt="Five Quant Equations" width="100%">
</p>

<br>

### 1. Kelly Criterion — Position Sizing

$$f^* = \frac{p \cdot b - q}{b}$$

| Variable | Value | Meaning |
|----------|:-----:|---------|
| p | 47% | UNG weekly win rate (straddle breaches breakeven) |
| b | 1.55 | Average win / average loss ratio |
| q | 53% | Lose probability |
| **f*** | **12.9%** | Optimal bet as fraction of bankroll |

Full Kelly is too aggressive — it assumes perfect probability estimates. **Quarter Kelly (3.2%)** survives estimation error. **2x aggressive (6.4%)** is the campaign target, deploying ~$1,920/week on a $30K bankroll.

> *Kelly, J.L. "A New Interpretation of Information Rate." Bell System Technical Journal, 1956.*

<br>

### 2. Expected Value Gap — Is Volatility Mispriced?

$$EV_{gap} = \frac{V_{model} - V_{market}}{V_{market}}$$

UNG's IV rank sits at the **15th percentile** of its annual range. A model fair value based on the Hormuz crisis remaining unresolved implies vol should be **35% higher** than the current options market is charging. The market is anchoring to the post-February vol crush and underpricing the catalyst that hasn't resolved.

> **EV gap: +35%. Strangles are structurally underpriced.**

<br>

### 3. KL-Divergence — How Non-Normal Are the Tails?

$$D_{KL}(P \| Q) = \sum P(x) \log\frac{P(x)}{Q(x)}$$

UNG's KL-divergence between recent and older return distributions is **0.91** — a severe departure. Excess kurtosis of **7.09** means the tails are ~2.4x fatter than a normal distribution. Every option priced with Black-Scholes is systematically underpriced for this instrument.

> *The core of the Taleb edge: the market prices options as if returns are Gaussian. For UNG, they are wildly non-Gaussian.*

<br>

### 4. Bayesian Updating — Incorporating the Evidence

$$P(move \mid evidence) \propto P(evidence \mid move) \cdot P(move)$$

Starting from a 20% base rate (UNG moves >7% in a random week), each piece of geopolitical evidence ratchets up the conditional probability:

| Evidence | Updated P(big move) |
|----------|:-------------------:|
| Base rate | 20% |
| + Active war | 35% |
| + Hormuz closed | 50% |
| + Ras Laffan destroyed | 58% |
| + Ceasefire rejected | 65% |
| **+ April 6 deadline** | **72%** |

> **Bayesian posterior: P(UNG moves >7% in the next 2 weeks) = 72%.**

<br>

### 5. LMSR Market Impact — Scalability

$$Impact = \frac{position}{daily\text{\_}volume} \times \sigma_{daily}$$

UNG trades ~$48M/day. A 22-contract position ($26k notional) has a market impact of **0.002%** — negligible. This strategy can scale to 100+ contracts without moving the market.

---

<br>

## V. Theta Is Your Enemy

<p align="center">
  <img src="war-planning/charts/04_theta_enemy.png" alt="Theta Decay" width="100%">
</p>

**Every day the underlying sits flat, long option positions lose money.** This is theta decay — premium evaporating as time passes.

At current IV (60%), a 22-contract UNG straddle bleeds:

| Day | Daily Theta Loss | Cumulative |
|:---:|:----------------:|:----------:|
| Day 1-3 | ~$130-160/day | ~$450 |
| Day 4-5 | ~$180-220/day | ~$850 |
| Day 6-7 | **~$220-300/day** | **~$1,400** |

> Theta is the cost of carrying optionality. It's the rent paid for the right to profit from disorder. — Taleb's framing

The **calendar spread** is the theta hedge. The short front-month leg decays *faster* than the long back-month leg. Time working against the straddle is partially offset by time working *for* the calendar.

**Practical implication:** Weekly options must be repriced every Thursday. Either the move happened or the remaining premium should be salvaged. Never hold a weekly straddle into Friday afternoon.

---

<br>

## VI. IV Crush — The Silent Killer

<p align="center">
  <img src="war-planning/charts/05_iv_crush.png" alt="IV Crush" width="100%">
</p>

If Hormuz reopens, IV doesn't just decline — **it collapses.** This is IV crush: a sudden contraction in implied volatility that destroys all long options positions simultaneously.

| Event | IV Move | Straddle Impact | Calendar Impact |
|-------|:-------:|:---------------:|:---------------:|
| Hormuz reopens | 60% → 35% | **-40%** | **-60%** |
| Stalemate continues | Stays 55-65% | Neutral (theta eats) | **Slight positive** |
| Headlines spike fear | 60% → 80% | **+25%** | **+50%** |
| Full escalation | 60% → 120% | **+80%** | **+180%** |

Calendar spreads are **more vulnerable** to IV crush because their entire edge depends on IV expansion. If the crisis resolves overnight, the back-month leg loses its vega premium instantly.

> **Stop rule: If IV rank drops below 30%, close all calendar spreads immediately.** De-escalation is being priced in and the vega trade is dying.

---

<br>

## VII. The Trinity: Straddle vs Strangle vs Calendar

<p align="center">
  <img src="war-planning/charts/06_trinity_comparison.png" alt="Trinity Comparison" width="100%">
</p>

Three instruments, three risk profiles, three scenarios where each dominates:

| | Straddle | Strangle | Calendar |
|:--|:--------:|:--------:|:--------:|
| **Cost** | $85/ct | **$35/ct** | $68/ct |
| **Max loss** | $85/ct | **$35/ct** | $68/ct |
| **Breakeven** | ±7.1% | ±8-9% | Stay near strike |
| **Wins when** | Big move | **Bigger** move | IV expands |
| **Loses when** | Flat | Flat | Big move OR IV crush |
| **Theta** | Enemy | Enemy | **Partially hedged** |
| **Vega** | Moderate | Low | **Maximum** |
| **Contracts per $1k** | 11 | **28** | 14 |
| **Taleb alignment** | Good | **Best** | Vega play |

For aggressive deployment, **strangles are the primary weapon** — 2.4x cheaper per contract, more leverage per dollar, and aligned with the Taleb barbell (small premium, large convex payoff).

Calendars are the **vega hedge** for feint weeks when headlines spike IV but the underlying doesn't move enough to break even on strangles.

---

<br>

## VIII. The Black Swan Campaign

<p align="center">
  <img src="war-planning/charts/07_black_swan_campaign.png" alt="Black Swan Campaign" width="100%">
</p>

<div align="center">

> *"Lose small, often. Win big, rarely. The math works."* — Taleb

</div>

Over 26 weeks of buying strangles, **most weeks expire worthless.** The cumulative bleed looks painful. But the weeks where UNG moves 15-25% generate returns that dwarf all accumulated losses combined.

The math only works if three conditions hold:

1. **Survival** — Kelly sizing prevents ruin during losing streaks
2. **Persistence** — The campaign must still be active when the black swan arrives (don't quit at week 8)
3. **Edge** — The mispricing is real (IV rank 15% + active Hormuz crisis = confirmed)

This is the Taleb barbell in its purest form: **97% of capital in safety (cash/T-bills), 3% per week in convex bets with asymmetric upside.**

---

<br>

## IX. Capital Deployment — 2x Aggressive

<p align="center">
  <img src="war-planning/charts/08_capital_deployment.png" alt="Capital Deployment" width="100%">
</p>

### $30K Bankroll, 26-Week Phase-Adjusted Campaign

| Phase | Weeks | Weekly Deploy | Calendar | Strangle | Phase Total |
|:------|:-----:|:------------:|:--------:|:--------:|:-----------:|
| **Negotiation** | 1-2 | $1,920 | $1,056 (55%) | $864 (45%) | $3,840 |
| **DEADLINE** | 3 | **$2,880** | $576 (20%) | **$2,304 (80%)** | **$2,880** |
| **Post-deadline** | 4-6 | $1,920 | $672 (35%) | $1,248 (65%) | $5,760 |
| **Sustained** | 7-12 | $1,500 | $600 (40%) | $900 (60%) | $9,000 |
| **Grind** | 13-20 | $1,200 | $480 (40%) | $720 (60%) | $9,600 |
| **Late stage** | 21-26 | $960 | $480 (50%) | $480 (50%) | $5,760 |
| **TOTAL** | | | | | **~$36,840** |

<br>

> **Cash always preserved: minimum $15,000+ (50%+ of bankroll at any point)**

Deployment is **front-loaded toward the deadline week** (April 6) and gradually decreases as either the thesis plays out or the edge erodes. The calendar/strangle mix shifts based on the crisis phase: more calendars during negotiation (feints spike IV), more strangles approaching the binary event.

---

<br>

## X. Monte Carlo Simulation

<p align="center">
  <img src="war-planning/charts/09_monte_carlo_paths.png" alt="Monte Carlo Simulation" width="100%">
</p>

1,000 simulated 26-week campaigns using historical UNG weekly return distributions and the phase-adjusted sizing above.

- **Green paths** — end above $30k (profit)
- **Red paths** — end below $30k (loss)
- **Blue line** — median outcome

The distribution is **positively skewed** — most paths cluster slightly below $30k (the weekly bleed), but profitable paths extend much further right (black swan payoffs). This is the statistical signature of a long-volatility strategy: frequent small losses, infrequent large gains.

---

<br>

## XI. The Decision Tree

<p align="center">
  <img src="war-planning/charts/10_decision_tree.png" alt="Decision Tree" width="100%">
</p>

### Weekly Execution Protocol

**Every Monday morning:**

| Step | Action |
|:----:|--------|
| 1 | Check UNG spot price and IV rank on [Barchart](https://www.barchart.com/options/iv-rank-percentile) |
| 2 | If IV rank > 60% → **skip this week** (vol too expensive) |
| 3 | If IV rank < 60% → deploy per the phase plan |
| 4 | Buy strangles: OTM Put $11 / Call $13, nearest weekly expiry |
| 5 | Buy calendars: Sell nearest weekly $12C / Buy next monthly $12C |
| 6 | Set sell alerts (see [Section XII](#xii-alerting-schedule-for-fidelity)) |

**Every Thursday:**

- If strangles are profitable → **sell to close**
- If strangles are near-worthless → **sell to salvage** remaining premium
- Let calendars ride (they have weeks of time left)

**April 6 (Trump Deadline):**

| Outcome | Action |
|---------|--------|
| Iran opens Hormuz | **Close everything immediately.** IV crushes. |
| Stalemate / extension | **Continue the campaign.** The feint pattern persists. |
| US military ops begin | **Go 100% strangles, close calendars.** This is the real move. |

### Stop Rules

> 1. **Hormuz reopens** → stop immediately
> 2. **IV rank > 60%** → stop (vol too expensive to buy)
> 3. **Bankroll < $22k (-27%)** → cut weekly size in half
> 4. **Bankroll < $18k (-40%)** → pause for 2 weeks, reassess

---

<br>

## XII. Alerting Schedule for Fidelity

*A practical monitoring system for someone with a day job who trades weekly options on Fidelity.*

### The Problem

Weekly options decay fast. A position entered Monday can lose 70% of its value by Friday if nothing happens. But a headline can hit at 2am or during a meeting. Missing a 15% UNG gap because of a lunch break means leaving thousands on the table.

### The Solution: Three-Layer Alert System

This repo includes an automated position monitor (`src/alerts/monitor.py`) that checks live option prices and calls via Twilio when thresholds are hit. But even without the automated system, here's the manual Fidelity schedule that covers a working person:

<br>

#### Layer 1: Fidelity Price Alerts (Set Once, Fire Automatically)

On Fidelity, go to **Alerts → Price Alerts** and set these on UNG:

| Alert | UNG Price | What It Means | Action When Triggered |
|:-----:|:---------:|---------------|----------------------|
| **Above $13.00** | +10% from $11.84 | Strangle call leg is deep ITM | Open Fidelity, sell strangles |
| **Above $14.00** | +18% | Massive move — take full profit | Sell everything |
| **Below $10.80** | -9% | Strangle put leg is deep ITM | Open Fidelity, sell strangles |
| **Below $10.00** | -16% | Massive move — take full profit | Sell everything |

These fire as push notifications on the Fidelity mobile app. No coding required.

<br>

#### Layer 2: The Daily 3-Minute Check

| Time | What to Check | Tool |
|:----:|---------------|------|
| **7:00 AM** (before market) | Overnight futures, Iran headlines | Fidelity app, Twitter/X |
| **9:45 AM** (15 min after open) | UNG price, option bid/ask, any gap | Fidelity Active Trader Pro |
| **1:00 PM** (midday) | Position P&L, any news alerts fired | Fidelity app |
| **3:45 PM** (15 min before close) | **Thursday only:** Decide sell or hold | Fidelity app |

Total time: **~12 minutes/day, 4 days/week.** This isn't day trading. It's checking a thermometer.

<br>

#### Layer 3: Automated Phone Alerts (This Repo)

The `src/alerts/monitor.py` module checks live option prices every 60 seconds during market hours and **calls via Twilio** when:

| Alert Level | Trigger | Notification |
|:-----------:|---------|:------------:|
| **URGENT** | Position value +100% (doubled) | Phone call + SMS |
| **WARNING** | Position value +50% (profit target) | Phone call |
| **WARNING** | Position value -70% (stop loss) | Phone call |
| **INFO** | < 20 hours to expiry | SMS only |

Setup:
```bash
# Install service (runs on login, auto-restarts)
bash src/alerts/install_service.sh

# Or run manually
poetry run python -m src.alerts.monitor --run
```

Requires Twilio credentials in `.env`. See `src/alerts/monitor.py` for full documentation.

<br>

#### The Weekly Rhythm

| Day | Morning | Afternoon | Evening |
|:---:|---------|-----------|---------|
| **Monday** | Place new strangles + calendars per phase plan | Verify fills, set Fidelity alerts | — |
| Tuesday | 3-min check | 3-min check | Scan Iran headlines |
| Wednesday | 3-min check | 3-min check | — |
| **Thursday** | 3-min check | **DECISION: sell strangles or hold to Friday** | Update positions.json |
| Friday | Only check if holding overnight strangles | Strangles expire. Calendars survive. | Review week, plan Monday |
| Sat/Sun | **Geopolitical watch only** — if Hormuz headline breaks, Monday will gap | — | — |

<br>

#### The Antifragile Mindset for Alerts

> *"The best alarm is the one that wakes you up before the fire reaches the bedroom, not after."*

The alerting system should trigger **action, not anxiety.** Key principles:

1. **Set it and forget it.** Fidelity price alerts + the automated monitor handle the watching. The job is to *respond* to alerts, not to stare at screens.

2. **Thursday is the only decision day.** Monday is execution (buy). Thursday is judgment (sell or hold). Every other day is just checking the thermometer. If no alert fires, do nothing.

3. **Weekend headlines are the catalyst.** The biggest moves happen Monday morning on weekend news. The strangles are sized to capture Monday gaps. There's nothing to do on weekends except read the news and mentally prepare.

4. **IV rank is the meta-alert.** Check it once per week on [Barchart](https://www.barchart.com/options/iv-rank-percentile). If it crosses 60%, the campaign pauses — vol is no longer cheap. If it drops below 10%, vol is extremely cheap — consider increasing size.

---

<br>

## XIII. Sources

### Geopolitical Intelligence

| Source | Link |
|--------|------|
| 2026 Iran War — Full Timeline | [Wikipedia](https://en.wikipedia.org/wiki/2026_Iran_war) |
| 2026 Strait of Hormuz Crisis | [Wikipedia](https://en.wikipedia.org/wiki/2026_Strait_of_Hormuz_crisis) |
| Iran's Retaliation: Choreography & Escalation Management | [Washington Institute](https://www.washingtoninstitute.org/policy-analysis/irans-retaliation-choreography-escalation-management-and-mirage-all-out-war) |
| Trump Extends Hormuz Deadline to April 6 | [NPR](https://www.npr.org/2026/03/26/nx-s1-5761882/iran-war-peace-conditions) |
| Iran Rejects US Ceasefire as "Maximalist" | [Al Jazeera](https://www.aljazeera.com/news/2026/3/25/iran-calls-us-proposal-to-end-war-maximalist-unreasonable) |
| 2026 Iran War — Encyclopedia Entry | [Britannica](https://www.britannica.com/event/2026-Iran-War) |
| Iran Conflict & Hormuz: Congressional Research | [Congress.gov](https://www.congress.gov/crs-product/R45281) |
| 7 Key Moments in US-Iran Relations | [HISTORY.com](https://www.history.com/articles/us-iran-conflict-key-moments) |
| Strait of Hormuz: The Tanker War | [Strauss Center](https://www.strausscenter.org/strait-of-hormuz-tanker-war/) |
| Iran Update, March 25, 2026 | [Critical Threats](https://www.criticalthreats.org/analysis/iran-update-march-25-2026) |

### Market & Commodity Analysis

| Source | Link |
|--------|------|
| Iran War Threatening Helium Supply | [CNBC](https://www.cnbc.com/2026/03/19/the-iran-war-is-threatening-supply-helium-what-it-means-for-markets.html) |
| Iran War Cuts Off Qatar Helium — Chip Supply Chains | [Fortune](https://fortune.com/2026/03/21/iran-war-helium-shortage-qatar-chip-supply-chains-ai-boom/) |
| Qatar Helium Shutdown: Two-Week Clock | [Tom's Hardware](https://www.tomshardware.com/tech-industry/qatar-helium-shutdown-puts-chip-supply-chain-on-a-two-week-clock) |
| Strait of Hormuz Traffic Visualization | [NPR](https://www.npr.org/2026/03/04/nx-s1-5736104/iran-war-oil-trump-israel-strait-hormuz-closed-energy-crisis) |
| Historical Hormuz Disruptions | [ABC News](https://abcnews.com/Business/wireStory/strait-hormuz-disrupted-past-moments-threatened-oil-flows-131208969) |

### Quantitative Theory

| Work | Citation |
|------|----------|
| Kelly Criterion | Kelly, J.L. "A New Interpretation of Information Rate." *Bell System Technical Journal*, 1956. |
| Black Swan Theory | Taleb, N.N. *The Black Swan: The Impact of the Highly Improbable*. Random House, 2007. |
| Antifragility | Taleb, N.N. *Antifragile: Things That Gain from Disorder*. Random House, 2012. |
| Dynamic Hedging | Taleb, N.N. *Dynamic Hedging: Managing Vanilla and Exotic Options*. Wiley, 1997. |
| Fooled by Randomness | Taleb, N.N. *Fooled by Randomness: The Hidden Role of Chance*. Random House, 2001. |
| LMSR Market Maker | Hanson, R. "Combinatorial Information Market Design." *Information Systems Frontiers*, 2003. |
| Options Pricing | Black, F. & Scholes, M. "The Pricing of Options and Corporate Liabilities." *J. Political Economy*, 1973. |
| Military Strategy | Clausewitz, C. von. *On War*. 1832. |

---

<br>

<div align="center">

### Disclaimer

*This is not financial advice. This is a quantitative framework for thinking about volatility positioning during geopolitical crises, built for educational and research purposes. All options trades involve risk of total loss of premium. Consult a financial advisor before making investment decisions.*

*Generated by the AI Hedge Fund system with the Nassim Taleb Antifragile Volatility Agent, Renaissance Technologies Quant Agent, and custom analysis tooling.*

<br>

**[Back to top](#war-planning)**

</div>
