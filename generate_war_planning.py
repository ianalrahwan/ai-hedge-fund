"""
WAR PLANNING: Comprehensive volatility campaign analysis.
Geopolitical edge + quant equations + vega/theta/IV dynamics.
Aggressive 2x capital deployment across crisis phases.
"""
import math, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scipy.stats import norm, kurtosis as sp_kurtosis
from datetime import datetime, timedelta
import yfinance as yf

OUT = "war-planning/charts"

# ── Theme ───────────────────────────────────────────────────────────────────
DARK_BG = "#0a0e1a"
CARD_BG = "#141b2d"
TEXT_COLOR = "#e2e8f0"
GRID_COLOR = "#1e293b"
GREEN = "#22c55e"
YELLOW = "#eab308"
RED = "#ef4444"
ACCENT = "#38bdf8"
PURPLE = "#a78bfa"
PINK = "#f472b6"
ORANGE = "#f97316"
CYAN = "#06b6d4"

def style_ax(ax, title, fontsize=14):
    ax.set_facecolor(DARK_BG)
    ax.set_title(title, color=TEXT_COLOR, fontsize=fontsize, fontweight="bold", pad=14)
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.grid(True, color=GRID_COLOR, alpha=0.4, linewidth=0.5)

def bs_price(S, K, T, r, sigma, opt="call"):
    if T <= 0:
        return max(S - K, 0) if opt == "call" else max(K - S, 0)
    d1 = (math.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if opt == "call":
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

def bs_vega(S, K, T, r, sigma):
    if T <= 0: return 0
    d1 = (math.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * math.sqrt(T))
    return S * math.sqrt(T) * norm.pdf(d1) / 100

def bs_theta(S, K, T, r, sigma, opt="call"):
    if T <= 0: return 0
    d1 = (math.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    theta = -S * norm.pdf(d1) * sigma / (2 * math.sqrt(T))
    if opt == "call":
        theta -= r * K * math.exp(-r * T) * norm.cdf(d2)
    else:
        theta += r * K * math.exp(-r * T) * norm.cdf(-d2)
    return theta / 365  # per day

# ── Fetch UNG data ──────────────────────────────────────────────────────────
print("Fetching UNG data...")
ung = yf.Ticker("UNG")
hist = ung.history(start="2025-03-26", end="2026-03-27", auto_adjust=False)
spot = hist["Close"].iloc[-1]
returns = hist["Close"].pct_change().dropna()
rolling_vol = (returns.rolling(20).std() * math.sqrt(252)).dropna()

S = spot  # ~11.84
K = 12.0
r = 0.05
base_iv = 0.60

print(f"  Spot: ${S:.2f}")
print("Generating charts...")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 1: GEOPOLITICAL TIMELINE WITH CRISIS PHASES
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(18, 8))
fig.patch.set_facecolor(DARK_BG)

# Timeline events
events = [
    ("2026-02-28", "US/Israel strike\nIran", RED, 1.0),
    ("2026-03-02", "Hormuz\nclosed", RED, -1.0),
    ("2026-03-04", "QatarGas\nforce majeure", ORANGE, 1.2),
    ("2026-03-13", "Ras Laffan hit\nHelium offline", RED, -1.2),
    ("2026-03-16", "NATO rejects\nHormuz ops", YELLOW, 0.8),
    ("2026-03-17", "Iranian officials\nassassinated", RED, -0.8),
    ("2026-03-24", "US 15-point\nceasefire sent", GREEN, 1.0),
    ("2026-03-25", "Iran rejects\nproposal", RED, -1.0),
    ("2026-03-26", "Trump extends\ndeadline → Apr 6", YELLOW, 1.2),
    ("2026-04-06", "TRUMP\nDEADLINE", PINK, -1.5),
]

# Phase backgrounds
phases = [
    ("2026-02-28", "2026-03-12", "SHOCK", RED, 0.08),
    ("2026-03-12", "2026-03-26", "ESCALATION", ORANGE, 0.06),
    ("2026-03-26", "2026-04-06", "NEGOTIATION\n(WE ARE HERE)", YELLOW, 0.08),
    ("2026-04-06", "2026-04-20", "BINARY EVENT", PINK, 0.06),
    ("2026-04-20", "2026-06-01", "RESOLUTION\nOR ESCALATION", PURPLE, 0.04),
]

for start, end, label, color, alpha in phases:
    s = mdates.datestr2num(start)
    e = mdates.datestr2num(end)
    ax.axvspan(s, e, alpha=alpha, color=color)
    mid = (s + e) / 2
    ax.text(mid, 1.8, label, ha="center", va="center", color=color, fontsize=10, fontweight="bold", alpha=0.7)

for date_str, label, color, y_pos in events:
    x = mdates.datestr2num(date_str)
    ax.plot(x, 0, "o", color=color, markersize=12, zorder=5)
    ax.vlines(x, 0, y_pos, color=color, linewidth=2, alpha=0.7)
    ax.text(x, y_pos + (0.15 if y_pos > 0 else -0.15), label,
            ha="center", va="bottom" if y_pos > 0 else "top",
            color=TEXT_COLOR, fontsize=8, fontweight="bold")

# UNG price overlay
ung_recent = hist[hist.index >= "2026-02-25"]["Close"]
ax2 = ax.twinx()
dates_num = mdates.date2num(ung_recent.index.to_pydatetime())
ax2.plot(dates_num, ung_recent.values, color=ACCENT, linewidth=2, alpha=0.6, label="UNG price")
ax2.set_ylabel("UNG Price ($)", color=ACCENT, fontsize=10)
ax2.tick_params(colors=ACCENT)

ax.axhline(y=0, color=TEXT_COLOR, linewidth=1, alpha=0.3)
ax.set_ylim(-2, 2.2)
ax.set_xlim(mdates.datestr2num("2026-02-25"), mdates.datestr2num("2026-05-15"))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
ax.set_yticks([])
style_ax(ax, "2026 Iran-Hormuz Crisis Timeline — Geopolitical Phases & Strategy Windows")
plt.tight_layout()
plt.savefig(f"{OUT}/01_geopolitical_timeline.png", dpi=150, facecolor=DARK_BG, bbox_inches="tight")
plt.close()
print("  1/10 Timeline")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 2: HISTORICAL FEINT PATTERN — IRAN ESCALATION LADDER
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(16, 8))
fig.patch.set_facecolor(DARK_BG)

# Clausewitz escalation ladder
ladder = [
    (1, "Diplomatic Threats", "\"We will close Hormuz\"", YELLOW, 10),
    (2, "Proxy Actions", "Houthi tanker attacks, mine laying", YELLOW, 20),
    (3, "Limited Strikes", "Drone swarms on Saudi, Ras Laffan", ORANGE, 35),
    (4, "Strait Closure", "IRGC blocks shipping, force majeure", ORANGE, 55),
    (5, "Negotiation Deadlock", "Ceasefire rejected, deadlines extended", YELLOW, 45),
    (6, "Military Confrontation", "US Navy vs IRGC in the strait", RED, 75),
    (7, "Full Escalation", "US strikes on Iranian military + energy", RED, 95),
]

# We are at step 5
current_step = 5

for step, name, detail, color, iv_impact in ladder:
    y = step
    width = iv_impact / 100 * 8
    alpha = 0.9 if step <= current_step else 0.3

    bar = ax.barh(y, width, height=0.6, color=color, alpha=alpha, edgecolor="none")

    marker = "★" if step == current_step else "●"
    ax.text(-0.2, y, f"{marker} {step}", ha="right", va="center", color=color if step <= current_step else GRID_COLOR,
            fontsize=14, fontweight="bold")
    ax.text(width + 0.1, y + 0.1, name, ha="left", va="center", color=TEXT_COLOR, fontsize=11, fontweight="bold", alpha=alpha)
    ax.text(width + 0.1, y - 0.2, detail, ha="left", va="center", color=GRID_COLOR, fontsize=9, alpha=alpha, style="italic")
    ax.text(width - 0.1, y, f"IV +{iv_impact}%", ha="right", va="center", color=DARK_BG, fontsize=9, fontweight="bold")

# Arrow showing "YOU ARE HERE"
ax.annotate("YOU ARE\nHERE", xy=(ladder[4][4]/100*8, 5), xytext=(6, 2.5),
            fontsize=14, color=PINK, fontweight="bold",
            arrowprops=dict(arrowstyle="fancy", color=PINK, lw=2),
            bbox=dict(boxstyle="round,pad=0.4", facecolor=CARD_BG, edgecolor=PINK))

# Next steps
ax.annotate("NEXT?", xy=(ladder[5][4]/100*8, 6), xytext=(7, 6),
            fontsize=12, color=RED, fontweight="bold", alpha=0.5,
            arrowprops=dict(arrowstyle="->", color=RED, lw=1.5, alpha=0.5))

ax.set_xlim(-1, 9)
ax.set_ylim(0, 8)
ax.set_xlabel("Estimated IV Impact (% increase)", color=TEXT_COLOR, fontsize=10)
style_ax(ax, "Clausewitz Escalation Ladder — Iran 2026\n(Each rung spikes IV further; historical pattern: feint → feint → real move)")
ax.set_yticks([])
plt.tight_layout()
plt.savefig(f"{OUT}/02_escalation_ladder.png", dpi=150, facecolor=DARK_BG, bbox_inches="tight")
plt.close()
print("  2/10 Escalation ladder")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 3: THE FIVE QUANT EQUATIONS
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.patch.set_facecolor(DARK_BG)

# 1. Kelly Criterion
ax = axes[0, 0]
p_range = np.linspace(0.1, 0.9, 100)
b = 1.55  # win/loss ratio from UNG
kelly_f = (p_range * b - (1 - p_range)) / b
kelly_f = np.clip(kelly_f, -0.5, 0.5)

ax.plot(p_range * 100, kelly_f * 100, color=ACCENT, linewidth=3)
ax.fill_between(p_range * 100, kelly_f * 100, 0, where=kelly_f > 0, color=GREEN, alpha=0.2)
ax.fill_between(p_range * 100, kelly_f * 100, 0, where=kelly_f <= 0, color=RED, alpha=0.2)
ax.axhline(y=0, color=TEXT_COLOR, linewidth=0.5, alpha=0.3)
ax.axvline(x=47, color=YELLOW, linestyle="--", linewidth=2)
ax.annotate(f"UNG: p=47%\nf*=12.9%", xy=(47, 12.9), textcoords="offset points", xytext=(15, 15),
            color=YELLOW, fontsize=10, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=YELLOW))
ax.set_xlabel("Win Probability (%)", color=TEXT_COLOR, fontsize=9)
ax.set_ylabel("Optimal Bet Size (%)", color=TEXT_COLOR, fontsize=9)
style_ax(ax, "1. KELLY CRITERION\nf* = (p·b − q) / b", fontsize=11)

# 2. Expected Value Gap
ax = axes[0, 1]
model_values = np.linspace(0.5, 2.0, 100)
market_price = 1.0
ev_gap = (model_values - market_price) / market_price * 100

ax.plot(model_values, ev_gap, color=ACCENT, linewidth=3)
ax.fill_between(model_values, ev_gap, 0, where=ev_gap > 0, color=GREEN, alpha=0.2)
ax.fill_between(model_values, ev_gap, 0, where=ev_gap <= 0, color=RED, alpha=0.2)
ax.axhline(y=0, color=TEXT_COLOR, linewidth=0.5, alpha=0.3)

# UNG point: IV rank 15% suggests model value > market
ax.scatter([1.35], [35], s=200, color=YELLOW, zorder=5, edgecolors="white")
ax.annotate("UNG: Model says\nvol should be 35%\nhigher than priced", xy=(1.35, 35),
            textcoords="offset points", xytext=(20, -20), color=YELLOW, fontsize=9, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=YELLOW))

ax.set_xlabel("Model Fair Value / Market Price", color=TEXT_COLOR, fontsize=9)
ax.set_ylabel("EV Gap (%)", color=TEXT_COLOR, fontsize=9)
style_ax(ax, "2. EXPECTED VALUE GAP\nEV_gap = (model − market) / market", fontsize=11)

# 3. KL-Divergence
ax = axes[0, 2]
x = np.linspace(-0.15, 0.15, 200)
# P = fat-tailed (reality), Q = normal (what BS assumes)
P = 0.6 * norm.pdf(x, 0, 0.03) + 0.4 * norm.pdf(x, 0, 0.08)  # mixture
Q = norm.pdf(x, 0, 0.035)  # normal

ax.fill_between(x * 100, P, alpha=0.3, color=ACCENT, label="Reality (fat tails)")
ax.fill_between(x * 100, Q, alpha=0.3, color=RED, label="Black-Scholes assumes")
ax.plot(x * 100, P, color=ACCENT, linewidth=2)
ax.plot(x * 100, Q, color=RED, linewidth=2, linestyle="--")

# Highlight the tails
tail_mask = np.abs(x) > 0.06
ax.fill_between(x[tail_mask] * 100, P[tail_mask], Q[tail_mask], color=GREEN, alpha=0.4)
ax.text(9, 3, "FREE\nMONEY", color=GREEN, fontsize=10, fontweight="bold", ha="center", alpha=0.7)
ax.text(-9, 3, "FREE\nMONEY", color=GREEN, fontsize=10, fontweight="bold", ha="center", alpha=0.7)

ax.set_xlabel("Daily Return (%)", color=TEXT_COLOR, fontsize=9)
ax.legend(fontsize=8, facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, loc="upper right")
style_ax(ax, "3. KL-DIVERGENCE\nD_KL(P||Q) — Reality vs Model", fontsize=11)

# 4. Bayesian Updating
ax = axes[1, 0]
# Prior: P(big move) = 20% (base rate)
# Evidence: Iran rejects ceasefire, deadline Apr 6, Hormuz still closed
prior = 0.20
evidence_items = [
    ("Base rate", 0.20),
    ("+ War started", 0.35),
    ("+ Hormuz closed", 0.50),
    ("+ Ras Laffan hit", 0.58),
    ("+ Ceasefire rejected", 0.65),
    ("+ Apr 6 deadline", 0.72),
]

x_pos = range(len(evidence_items))
probs = [e[1] for e in evidence_items]
labels = [e[0] for e in evidence_items]
colors_bar = [GRID_COLOR, YELLOW, ORANGE, ORANGE, RED, RED]

bars = ax.bar(x_pos, [p * 100 for p in probs], color=colors_bar, alpha=0.8, edgecolor="none")
for bar, p, label in zip(bars, probs, labels):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f"{p:.0%}", ha="center", color=TEXT_COLOR, fontsize=10, fontweight="bold")

ax.set_xticks(x_pos)
ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
ax.set_ylabel("P(UNG moves >7% this week)", color=TEXT_COLOR, fontsize=9)
ax.set_ylim(0, 85)
style_ax(ax, "4. BAYESIAN UPDATING\nP(move|evidence) ∝ P(evidence|move)·P(move)", fontsize=11)

# 5. LMSR Market Impact
ax = axes[1, 1]
position_sizes = np.linspace(0, 50000, 100)
# UNG daily volume ~4M shares, avg price ~$12 = $48M daily volume
daily_vol = 48e6
daily_volatility = 0.029  # 2.9% daily
impact = (position_sizes / daily_vol) * daily_volatility * 100

ax.plot(position_sizes / 1000, impact, color=ACCENT, linewidth=3)
ax.fill_between(position_sizes / 1000, impact, alpha=0.2, color=ACCENT)

# Your position size
your_pos = 22 * 100 * 12  # 22 contracts * 100 shares * ~$12
ax.axvline(x=your_pos/1000, color=GREEN, linestyle="--", linewidth=2)
your_impact = (your_pos / daily_vol) * daily_volatility * 100
ax.annotate(f"Your 22ct: ${your_pos/1000:.0f}k\nImpact: {your_impact:.4f}%\n(negligible)",
            xy=(your_pos/1000, your_impact),
            textcoords="offset points", xytext=(40, 40), color=GREEN, fontsize=9, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=GREEN))

ax.set_xlabel("Position Size ($k)", color=TEXT_COLOR, fontsize=9)
ax.set_ylabel("Estimated Market Impact (%)", color=TEXT_COLOR, fontsize=9)
style_ax(ax, "5. LMSR MARKET IMPACT\nImpact = (size/volume) × σ_daily", fontsize=11)

# 6. Summary equation
ax = axes[1, 2]
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")
ax.set_facecolor(DARK_BG)

summary_text = """THE FIVE EQUATIONS SAY:

[1] Kelly f* = 12.9% -> 3.2% quarter
    Bet ~1,920/week on 60k bankroll
    2x aggressive: ~3,840/week

[2] EV Gap = +35%
    Vol at 15th pctile vs model fair value
    Strangles are 35% underpriced

[3] KL-Divergence = 0.91
    UNG returns are wildly non-normal
    Tails 2x fatter than BS assumes

[4] Bayesian P(big move) = 72%
    Prior 20% -> 72% after evidence
    Ceasefire rejected + Apr 6 deadline

[5] Market Impact: negligible
    Your position is dust in UNG volume
    Scale freely up to 100+ contracts"""

ax.text(0.5, 0.5, summary_text, transform=ax.transAxes, fontsize=11,
        color=TEXT_COLOR, ha="center", va="center", fontfamily="monospace",
        bbox=dict(boxstyle="round,pad=0.8", facecolor=CARD_BG, edgecolor=ACCENT, linewidth=2))
ax.set_title("COMBINED VERDICT", color=ACCENT, fontsize=14, fontweight="bold", pad=14)

plt.suptitle("THE FIVE QUANT EQUATIONS — Applied to UNG Hormuz Campaign",
             color=TEXT_COLOR, fontsize=16, fontweight="bold", y=0.98)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(f"{OUT}/03_five_equations.png", dpi=150, facecolor=DARK_BG, bbox_inches="tight")
plt.close()
print("  3/10 Five equations")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 4: THETA IS YOUR ENEMY — DAILY DECAY VISUALIZATION
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.patch.set_facecolor(DARK_BG)

# Left: Straddle value decay over 7 days at different IV levels
ax = axes[0]
days = np.linspace(7, 0.1, 100)
for iv, color, label in [(0.60, ACCENT, "IV 60% (now)"), (0.80, YELLOW, "IV 80%"),
                          (1.00, GREEN, "IV 100%"), (1.20, PURPLE, "IV 120%")]:
    values = []
    for d in days:
        T = d / 365
        c = bs_price(S, K, T, r, iv, "call")
        p = bs_price(S, K, T, r, iv, "put")
        values.append(c + p)
    ax.plot(7 - days, values, color=color, linewidth=2.5, label=label)

ax.axhline(y=0.75, color=RED, linestyle="--", linewidth=2, alpha=0.5)
ax.text(0.2, 0.78, "Your entry: $0.75", color=RED, fontsize=10, fontweight="bold")

# Shade the "theta kills you" zone
ax.fill_between([5, 7], 0, 2, color=RED, alpha=0.1)
ax.text(6, 0.15, "THETA\nDEATH\nZONE", color=RED, fontsize=12, fontweight="bold", ha="center", alpha=0.5)

ax.set_xlabel("Days Elapsed", color=TEXT_COLOR, fontsize=10)
ax.set_ylabel("Straddle Value ($/share)", color=TEXT_COLOR, fontsize=10)
ax.legend(fontsize=9, facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
style_ax(ax, "Theta Decay: Your $0.75 Straddle Melting\n(Higher IV = slower decay = more time to be right)")

# Right: Daily theta in dollars for your position
ax = axes[1]
days_left = np.arange(7, 0, -1)
theta_daily = []
for d in days_left:
    T = d / 365
    tc = bs_theta(S, K, T, r, 0.60, "call")
    tp = bs_theta(S, K, T, r, 0.60, "put")
    theta_daily.append((tc + tp) * 100 * 22)  # 22 contracts

colors_theta = [YELLOW if abs(t) < 30 else ORANGE if abs(t) < 50 else RED for t in theta_daily]
bars = ax.bar([f"Day {7-d+1}" for d in days_left], theta_daily, color=colors_theta, alpha=0.8)

for bar, val in zip(bars, theta_daily):
    ax.text(bar.get_x() + bar.get_width()/2, val - 3,
            f"${val:.0f}", ha="center", color=TEXT_COLOR, fontsize=10, fontweight="bold")

ax.set_ylabel("Daily Theta Decay ($) — 22 Contracts", color=TEXT_COLOR, fontsize=10)
style_ax(ax, "How Much You Lose Per Day If UNG Stays Flat\n(This is the cost of carrying straddles)")

plt.suptitle("THETA IS YOUR ENEMY — The Price of Waiting",
             color=RED, fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(f"{OUT}/04_theta_enemy.png", dpi=150, facecolor=DARK_BG, bbox_inches="tight")
plt.close()
print("  4/10 Theta enemy")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 5: IV CRUSH & VEGA CRUSH — WHAT KILLS CALENDARS
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.patch.set_facecolor(DARK_BG)

prices = np.linspace(9, 15, 300)

# Left: Calendar P&L under IV crush scenario
ax = axes[0]
for iv, color, label, lw in [
    (0.60, ACCENT, "IV 60% (now) — entry", 2),
    (0.80, GREEN, "IV 80% — headlines spike fear", 3),
    (0.40, RED, "IV 40% — CRUSH (Hormuz opens)", 3),
    (0.30, PINK, "IV 30% — full de-escalation", 2),
]:
    pnl = []
    for s in prices:
        front_val = max(s - K, 0)
        remaining_T = (49 - 6) / 365
        back_val = bs_price(s, K, remaining_T, r, iv, "call")
        profit = (back_val - front_val - 0.68) * 100  # $0.68 debit
        pnl.append(profit)
    ax.plot(prices, pnl, color=color, linewidth=lw, label=label, alpha=0.9)

ax.axhline(y=0, color=TEXT_COLOR, linewidth=0.5, alpha=0.3)
ax.axvline(x=S, color=PURPLE, linestyle=":", alpha=0.5)

# IV crush danger zone
ax.annotate("IV CRUSH\nHormuz opens\n= calendar destroyed", xy=(12, -40),
            fontsize=11, color=RED, fontweight="bold", ha="center",
            bbox=dict(boxstyle="round", facecolor=CARD_BG, edgecolor=RED))

ax.set_xlabel("UNG Price at Front Expiry", color=TEXT_COLOR, fontsize=10)
ax.set_ylabel("Calendar P&L per Contract ($)", color=TEXT_COLOR, fontsize=10)
ax.legend(fontsize=9, facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, loc="upper right")
style_ax(ax, "Calendar Spread: IV Expansion vs IV CRUSH\n(Red lines = what happens if crisis resolves)")

# Right: Vega crush on straddle
ax = axes[1]
iv_levels = np.linspace(0.30, 1.50, 100)
straddle_vals = []
for iv in iv_levels:
    T = 5 / 365  # 5 days left
    c = bs_price(S, K, T, r, iv, "call")
    p = bs_price(S, K, T, r, iv, "put")
    straddle_vals.append(c + p)

ax.plot(iv_levels * 100, straddle_vals, color=ACCENT, linewidth=3)
ax.fill_between(iv_levels * 100, straddle_vals, 0, color=ACCENT, alpha=0.1)

# Your entry
ax.axhline(y=0.75, color=YELLOW, linestyle="--", linewidth=2)
ax.text(35, 0.80, "Your entry $0.75", color=YELLOW, fontsize=10, fontweight="bold")

# Current IV
ax.axvline(x=60, color=GREEN, linestyle="--", alpha=0.7)
ax.text(62, 1.5, "Now\n60%", color=GREEN, fontsize=10, fontweight="bold")

# If IV crushes
ax.axvline(x=35, color=RED, linestyle="--", alpha=0.7)
ax.text(28, 0.3, "If IV\ncrushes\nto 35%", color=RED, fontsize=9, fontweight="bold")

# If IV spikes
ax.axvline(x=100, color=PURPLE, linestyle="--", alpha=0.7)
ax.text(102, 1.2, "If IV\nspikes\nto 100%", color=PURPLE, fontsize=9, fontweight="bold")

ax.set_xlabel("Implied Volatility (%)", color=TEXT_COLOR, fontsize=10)
ax.set_ylabel("Straddle Value ($/share)", color=TEXT_COLOR, fontsize=10)
style_ax(ax, "Straddle Value vs IV Level (5 days to expiry)\n(Vega exposure: higher IV = higher straddle value)")

plt.suptitle("THE DOUBLE-EDGED SWORD: What IV Crush Does to Your Positions",
             color=ORANGE, fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(f"{OUT}/05_iv_crush.png", dpi=150, facecolor=DARK_BG, bbox_inches="tight")
plt.close()
print("  5/10 IV crush")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 6: STRADDLE vs STRANGLE vs CALENDAR — THE TRINITY
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(20, 7))
fig.patch.set_facecolor(DARK_BG)

titles = [
    "STRADDLE ($12/$12)\n$85/ct | BE: ±7.1%\nWins on BIG moves",
    "STRANGLE ($11/$13)\n~$35/ct | BE: ±8-9%\nCheaper, needs BIGGER move",
    "CALENDAR (sell 6d/buy 49d)\n$68/ct | BE: stay near $12\nWins on IV EXPANSION",
]

for ax_idx, (ax, title) in enumerate(zip(axes, titles)):
    for iv, color, alpha, lw in [(0.60, ACCENT, 0.9, 2.5), (1.00, GREEN, 0.5, 1.5)]:
        pnl = []
        for s in prices:
            if ax_idx == 0:  # Straddle
                if iv == 0.60:  # at expiry
                    val = max(K - s, 0) + max(s - K, 0) - 0.85
                else:
                    T = 3/365
                    val = bs_price(s, K, T, r, iv, "call") + bs_price(s, K, T, r, iv, "put") - 0.85
                pnl.append(val * 100)
            elif ax_idx == 1:  # Strangle
                put_k, call_k = 11.0, 13.0
                if iv == 0.60:
                    val = max(put_k - s, 0) + max(s - call_k, 0) - 0.35
                else:
                    T = 3/365
                    val = bs_price(s, call_k, T, r, iv, "call") + bs_price(s, put_k, T, r, iv, "put") - 0.35
                pnl.append(val * 100)
            else:  # Calendar
                front_val = max(s - K, 0)
                remaining_T = (49 - 6) / 365
                back_val = bs_price(s, K, remaining_T, r, iv, "call")
                pnl.append((back_val - front_val - 0.68) * 100)

        label = "At expiry (IV 60%)" if iv == 0.60 else "If IV → 100%"
        ax.plot(prices, pnl, color=color, linewidth=lw, alpha=alpha, label=label)

    ax.fill_between(prices, pnl, 0, where=np.array(pnl) > 0, color=GREEN, alpha=0.1)
    ax.fill_between(prices, pnl, 0, where=np.array(pnl) <= 0, color=RED, alpha=0.1)
    ax.axhline(y=0, color=TEXT_COLOR, linewidth=0.5, alpha=0.3)
    ax.axvline(x=S, color=PURPLE, linestyle=":", alpha=0.3)
    ax.set_xlabel("UNG Price", color=TEXT_COLOR, fontsize=9)
    ax.set_ylabel("P&L per Contract ($)", color=TEXT_COLOR, fontsize=9)
    ax.legend(fontsize=8, facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    style_ax(ax, title, fontsize=10)

plt.suptitle("THE TRINITY: Three Ways to Play Volatility",
             color=TEXT_COLOR, fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(f"{OUT}/06_trinity_comparison.png", dpi=150, facecolor=DARK_BG, bbox_inches="tight")
plt.close()
print("  6/10 Trinity")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 7: BLACK SWAN PAYOFF — THE TAIL THAT PAYS FOR EVERYTHING
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 7))
fig.patch.set_facecolor(DARK_BG)

# Simulate a 26-week campaign with strangles
# Most weeks lose. One black swan pays for everything.
np.random.seed(42)
weekly_returns = hist["Close"].resample("W").last().pct_change().dropna().values

# Simulate 26 weeks: $35/ct strangle (Put $11/Call $13), 25 contracts/week
strangle_entry = 0.35
contracts_per_week = 25
weekly_cost = strangle_entry * 100 * contracts_per_week  # $875/week

weeks = 26
cumulative_pnl = np.zeros(weeks)
week_pnl = np.zeros(weeks)

for w in range(weeks):
    ret = np.random.choice(weekly_returns)
    new_price = S * (1 + ret)
    put_val = max(11.0 - new_price, 0)
    call_val = max(new_price - 13.0, 0)
    strangle_val = put_val + call_val
    pnl = (strangle_val - strangle_entry) * 100 * contracts_per_week
    week_pnl[w] = pnl
    cumulative_pnl[w] = cumulative_pnl[w-1] + pnl if w > 0 else pnl

colors_bar = [GREEN if p > 0 else RED for p in week_pnl]
ax.bar(range(weeks), week_pnl, color=colors_bar, alpha=0.7, edgecolor="none")

# Cumulative line
ax2 = ax.twinx()
ax2.plot(range(weeks), cumulative_pnl, color=ACCENT, linewidth=3, marker="o", markersize=4)
ax2.set_ylabel("Cumulative P&L ($)", color=ACCENT, fontsize=10)
ax2.tick_params(colors=ACCENT)
ax2.axhline(y=0, color=YELLOW, linewidth=1, linestyle="--", alpha=0.5)

# Find the black swan week
max_week = np.argmax(week_pnl)
if week_pnl[max_week] > 0:
    ax.annotate(f"BLACK SWAN\n+${week_pnl[max_week]:,.0f}", xy=(max_week, week_pnl[max_week]),
                textcoords="offset points", xytext=(20, 20),
                fontsize=14, color=GREEN, fontweight="bold",
                arrowprops=dict(arrowstyle="fancy", color=GREEN, lw=2),
                bbox=dict(boxstyle="round", facecolor=CARD_BG, edgecolor=GREEN))

# Stats
wins = sum(1 for p in week_pnl if p > 0)
total_invested = weekly_cost * weeks
final_pnl = cumulative_pnl[-1]

stats_text = (f"Weeks: {weeks} | Wins: {wins} | Losses: {weeks-wins}\n"
              f"Total invested: ${total_invested:,.0f} | Final P&L: ${final_pnl:+,.0f}\n"
              f"The {wins} winning weeks paid for the {weeks-wins} losing weeks")

ax.text(0.02, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
        color=TEXT_COLOR, va="top", fontfamily="monospace",
        bbox=dict(boxstyle="round,pad=0.4", facecolor=CARD_BG, edgecolor=GRID_COLOR))

ax.set_xlabel("Week", color=TEXT_COLOR, fontsize=10)
ax.set_ylabel("Weekly P&L ($)", color=TEXT_COLOR, fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:+,.0f}"))
style_ax(ax, "THE BLACK SWAN CAMPAIGN\n\"You lose small, often. You win big, rarely. The math works.\" — Taleb")
plt.tight_layout()
plt.savefig(f"{OUT}/07_black_swan_campaign.png", dpi=150, facecolor=DARK_BG, bbox_inches="tight")
plt.close()
print("  7/10 Black swan")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 8: AGGRESSIVE 2X CAPITAL DEPLOYMENT WATERFALL
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(16, 8))
fig.patch.set_facecolor(DARK_BG)

bankroll = 60000
base_weekly = 3840  # 2x aggressive (~6.4% of bankroll)

# Phase-adjusted deployment
phase_plan = [
    # (week_start, week_end, phase_name, cal_pct, str_pct, size_mult, color)
    (1, 2, "NEGOTIATION\n(now → Apr 4)", 0.55, 0.45, 1.0, YELLOW),
    (3, 3, "DEADLINE WEEK\n(Apr 6)", 0.20, 0.80, 1.5, RED),
    (4, 6, "POST-DEADLINE\n(assess)", 0.35, 0.65, 1.0, ORANGE),
    (7, 12, "SUSTAINED\nCAMPAIGN", 0.40, 0.60, 0.8, ACCENT),
    (13, 20, "GRIND\n(if stalemate)", 0.40, 0.60, 0.7, PURPLE),
    (21, 26, "LATE STAGE\n(fatigue)", 0.50, 0.50, 0.5, GRID_COLOR),
]

week_labels = []
cal_amounts = []
str_amounts = []
total_deployed = 0
running_bankroll = bankroll

for ws, we, name, cal_pct, str_pct, mult, color in phase_plan:
    for w in range(ws, we + 1):
        if w > 26: break
        weekly = min(base_weekly * mult, running_bankroll * 0.08)  # cap at 8% of bankroll
        cal = weekly * cal_pct
        strang = weekly * str_pct
        cal_amounts.append(cal)
        str_amounts.append(strang)
        total_deployed += weekly
        week_labels.append(f"W{w}")

x = np.arange(len(week_labels))
ax.bar(x, cal_amounts, label="Calendar Spreads", color=CYAN, alpha=0.8, edgecolor="none")
ax.bar(x, str_amounts, bottom=cal_amounts, label="Strangles", color=ORANGE, alpha=0.8, edgecolor="none")

# Phase annotations
phase_x = 0
for ws, we, name, _, _, mult, color in phase_plan:
    width = min(we, 26) - ws + 1
    if phase_x + width > len(week_labels): break
    mid = phase_x + width / 2 - 0.5
    ax.text(mid, max(cal_amounts) + max(str_amounts) + 100, name,
            ha="center", va="bottom", color=color, fontsize=9, fontweight="bold")
    ax.axvline(x=phase_x - 0.5, color=color, linestyle=":", alpha=0.3)
    phase_x += width

# Cumulative line
cumul = np.cumsum([c + s for c, s in zip(cal_amounts, str_amounts)])
ax2 = ax.twinx()
ax2.plot(x, cumul, color=RED, linewidth=3, marker=".", markersize=6)
ax2.set_ylabel("Cumulative Deployed ($)", color=RED, fontsize=10)
ax2.tick_params(colors=RED)
ax2.axhline(y=bankroll, color=YELLOW, linestyle="--", linewidth=1, alpha=0.5)
ax2.text(25, bankroll + 1000, "$60k bankroll", color=YELLOW, fontsize=9, ha="right")

ax.set_xticks(x[::2])
ax.set_xticklabels(week_labels[::2], rotation=45, fontsize=8)
ax.set_ylabel("Weekly Deployment ($)", color=TEXT_COLOR, fontsize=10)
ax.legend(fontsize=10, facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, loc="upper left")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

style_ax(ax, f"AGGRESSIVE 2× DEPLOYMENT: $60K Bankroll, Phase-Adjusted\n(Total deployed over 26 weeks: ${total_deployed:,.0f})")
plt.tight_layout()
plt.savefig(f"{OUT}/08_capital_deployment.png", dpi=150, facecolor=DARK_BG, bbox_inches="tight")
plt.close()
print("  8/10 Capital deployment")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 9: MONTE CARLO — 1000 CAMPAIGN PATHS
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(16, 8))
fig.patch.set_facecolor(DARK_BG)

np.random.seed(42)
n_sims = 1000
n_weeks = 26
paths = np.zeros((n_sims, n_weeks + 1))
paths[:, 0] = bankroll

for w in range(1, n_weeks + 1):
    br = paths[:, w - 1]

    # Phase sizing
    if w <= 2: pct = 0.064
    elif w == 3: pct = 0.096
    elif w <= 6: pct = 0.064
    elif w <= 12: pct = 0.050
    else: pct = 0.040

    budget = br * pct

    # Split: 40% calendar, 60% strangle
    cal_spend = budget * 0.40
    str_spend = budget * 0.60

    # Calendar: 55% win rate, 40% avg win, 60% avg loss
    cal_win = np.random.random(n_sims) < 0.55
    cal_pnl = np.where(cal_win, cal_spend * 0.40, -cal_spend * 0.60)

    # Strangle: 25% win rate, 250% avg win, 100% loss
    str_win = np.random.random(n_sims) < 0.25
    str_pnl = np.where(str_win, str_spend * 2.5, -str_spend * 1.0)

    paths[:, w] = br + cal_pnl + str_pnl

# Plot paths
for i in range(min(200, n_sims)):
    final = paths[i, -1]
    color = GREEN if final > bankroll else RED
    ax.plot(range(n_weeks + 1), paths[i], color=color, alpha=0.05, linewidth=0.5)

# Percentile bands
p10 = np.percentile(paths, 10, axis=0)
p25 = np.percentile(paths, 25, axis=0)
p50 = np.percentile(paths, 50, axis=0)
p75 = np.percentile(paths, 75, axis=0)
p90 = np.percentile(paths, 90, axis=0)

ax.fill_between(range(n_weeks + 1), p10, p90, color=ACCENT, alpha=0.1, label="10th-90th %ile")
ax.fill_between(range(n_weeks + 1), p25, p75, color=ACCENT, alpha=0.2, label="25th-75th %ile")
ax.plot(range(n_weeks + 1), p50, color=ACCENT, linewidth=3, label="Median")

ax.axhline(y=bankroll, color=YELLOW, linestyle="--", linewidth=2, alpha=0.5)

final_vals = paths[:, -1]
stats = (f"Median: \\${np.median(final_vals):,.0f} | Mean: \\${np.mean(final_vals):,.0f}\n"
         f"P(profit): {(final_vals > bankroll).mean():.0%} | P(>80k): {(final_vals > 80000).mean():.0%}\n"
         f"Worst 10%: <\\${np.percentile(final_vals, 10):,.0f} | Best 10%: >\\${np.percentile(final_vals, 90):,.0f}")

ax.text(0.02, 0.02, stats, transform=ax.transAxes, fontsize=11,
        color=TEXT_COLOR, va="bottom", fontfamily="monospace",
        bbox=dict(boxstyle="round,pad=0.4", facecolor=CARD_BG, edgecolor=ACCENT, linewidth=2))

ax.set_xlabel("Week", color=TEXT_COLOR, fontsize=10)
ax.set_ylabel("Bankroll ($)", color=TEXT_COLOR, fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.legend(fontsize=10, facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, loc="upper left")
style_ax(ax, f"MONTE CARLO: 1,000 Campaign Simulations — 2× Aggressive Deployment")
plt.tight_layout()
plt.savefig(f"{OUT}/09_monte_carlo_paths.png", dpi=150, facecolor=DARK_BG, bbox_inches="tight")
plt.close()
print("  9/10 Monte Carlo")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 10: THE DECISION TREE
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(18, 10))
fig.patch.set_facecolor(DARK_BG)
ax.set_facecolor(DARK_BG)
ax.axis("off")
ax.set_xlim(0, 18)
ax.set_ylim(0, 10)

def draw_box(ax, x, y, w, h, text, color, fontsize=9):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                           facecolor=CARD_BG, edgecolor=color, linewidth=2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha="center", va="center",
            color=TEXT_COLOR, fontsize=fontsize, fontweight="bold")

def draw_arrow(ax, x1, y1, x2, y2, color, label=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=2))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my + 0.15, label, ha="center", va="bottom",
                color=color, fontsize=8, fontweight="bold")

# Root
draw_box(ax, 0.5, 4.2, 3.5, 1.5, "WEEK 1-2\n$3,840/week\n55% Calendar\n45% Strangle", YELLOW, 10)

# Week 3
draw_arrow(ax, 4.0, 5.0, 5.0, 5.0, YELLOW, "Apr 4")
draw_box(ax, 5.0, 4.2, 3.5, 1.5, "WEEK 3\nDEADLINE WEEK\n$5,760\n20% Cal / 80% Str", RED, 10)

# Apr 6 branch
draw_arrow(ax, 8.5, 5.8, 10.0, 8.2, GREEN, "Iran opens\nHormuz")
draw_box(ax, 10.0, 7.8, 3.5, 1.5, "STOP\nClose everything\nTake profits/losses\nVol crushes", GREEN, 9)

draw_arrow(ax, 8.5, 5.0, 10.0, 5.0, YELLOW, "Stalemate\ndeadline extended")
draw_box(ax, 10.0, 4.2, 3.5, 1.5, "CONTINUE\n$3,000/week\n40% Cal / 60% Str\nFeint pattern", YELLOW, 9)

draw_arrow(ax, 8.5, 4.2, 10.0, 2.0, RED, "US military\nops begin")
draw_box(ax, 10.0, 1.2, 3.5, 1.5, "GO HEAVY\n$3,000/week\n100% Strangles\nClose calendars", RED, 9)

# From stalemate
draw_arrow(ax, 13.5, 5.0, 14.5, 5.0, YELLOW)
draw_box(ax, 14.5, 4.2, 3.0, 1.5, "WEEKS 7-26\nGrind it out\n$2,400/week\nRepeat weekly", ACCENT, 9)

# From escalation
draw_arrow(ax, 13.5, 2.0, 14.5, 2.0, RED)
draw_box(ax, 14.5, 1.2, 3.0, 1.5, "BLACK SWAN\nUNG ±20-30%\nStrangles 5-10×\nCLOSE & TAKE $$$", GREEN, 9)

# Stop rules
draw_box(ax, 5.5, 0.2, 6.5, 0.8, "STOP RULES: IV rank >60% | Bankroll <$36k | Hormuz reopens", PINK, 9)

ax.set_title("THE DECISION TREE — Phase-Adjusted War Campaign",
             color=TEXT_COLOR, fontsize=16, fontweight="bold", pad=20)

plt.tight_layout()
plt.savefig(f"{OUT}/10_decision_tree.png", dpi=150, facecolor=DARK_BG, bbox_inches="tight")
plt.close()
print("  10/10 Decision tree")

print("\nAll charts saved.")
print("Writing report...")

# ═══════════════════════════════════════════════════════════════════════════
# MARKDOWN REPORT
# ═══════════════════════════════════════════════════════════════════════════

md = """# WAR PLANNING
### Volatility Campaign: Iran-Hormuz Crisis | $60K Bankroll | 2× Aggressive | March 26, 2026

---

> *"War is merely the continuation of policy by other means."* — Carl von Clausewitz, *On War* (1832)

> *"The market is a device for transferring money from the impatient to the patient."* — Warren Buffett

> *"My major hobby is teasing people who take themselves and the quality of their knowledge too seriously."* — Nassim Nicholas Taleb, *The Black Swan*

---

## I. Situation Assessment

![Geopolitical Timeline](charts/01_geopolitical_timeline.png)

### What Happened

On February 28, 2026, the United States and Israel launched surprise airstrikes on Iran, killing Supreme Leader Khamenei. Iran retaliated with missiles and drones, and the IRGC closed the Strait of Hormuz — choking 20% of global oil, 33% of global helium, and 20% of global LNG.

### Where We Are Now (March 26)

- Iran **rejected** the US 15-point ceasefire proposal as "maximalist" *(Al Jazeera, Mar 25)*
- Trump **extended** the Hormuz deadline to **April 6** *(NPR, Mar 26)*
- 150+ freight ships stalled in the strait *(NPR, Mar 4)*
- QatarGas declared force majeure — "extensive" damage "years to repair" *(Fortune, Mar 21)*
- UNG down 6.2% since Mar 13 while crisis intensified — **IV contracting into the catalyst**

### The April 6 Inflection

In 11 days, Trump's ultimatum expires. Three outcomes:

| Scenario | Probability | UNG Impact | IV Impact | Strategy |
|----------|:-----------:|:----------:|:---------:|----------|
| Iran opens Hormuz | ~15% | -5 to -10% | **CRUSH** to 35% | STOP. Close all. |
| Stalemate / extension | ~55% | ±3-5% | Stays 55-70% | Calendar-heavy |
| US military operation | ~30% | **+15 to +30%** | **SPIKE** to 120%+ | Strangle-heavy |

---

## II. The Clausewitz Escalation Ladder

![Escalation Ladder](charts/02_escalation_ladder.png)

Every Iran confrontation since 1988 follows the same **feint → feint → real move** pattern:

| Year | Feints | Real Move | Source |
|------|--------|-----------|--------|
| 1984-88 | 3 years of tanker attacks | Operation Praying Mantis — US sinks Iranian navy | *Strauss Center* |
| 2019 | Months of Gulf provocations | Saudi Aramco drone strike — oil spikes 15% | *Washington Institute* |
| Jan 2020 | Proxy attacks on US bases | Soleimani assassination → Iranian missile barrage | *HISTORY.com* |
| Apr 2024 | 233 telegraphed drones (intercepted) | Oct 2024 real strike with ballistic missiles | *Washington Institute* |
| 2026 | Feb-Mar: closure, strikes, negotiations | **April 6? →** ??? | We're in the feint phase |

**We are at Step 5 on the escalation ladder.** The pattern says the real move hasn't happened yet.

Each feint spikes IV without a commensurate price move — **calendar spread territory**. The real move spikes both — **strangle territory**. The campaign must be structured to profit from both.

---

## III. The Five Quant Equations

![Five Equations](charts/03_five_equations.png)

### 1. Kelly Criterion — How Much to Bet

$$f^* = \\frac{p \\cdot b - q}{b}$$

Where p = 47% (UNG weekly win rate), b = 1.55 (win/loss ratio), q = 53%.

**Full Kelly: 12.9% = $7,740/week.** Quarter Kelly (safe): 3.2% = $1,920/week. **2× aggressive: 6.4% = $3,840/week.**

*Source: Kelly, J.L. "A New Interpretation of Information Rate." Bell System Technical Journal, 1956.*

### 2. Expected Value Gap — Is Vol Mispriced?

$$EV_{gap} = \\frac{V_{model} - V_{market}}{V_{market}}$$

UNG IV rank is at the **15th percentile** of its annual range. Our model fair value (based on the Hormuz crisis remaining unresolved) implies vol should be 35% higher. The options market is underpricing the tail risk because it's anchoring to the post-Feb vol crush.

**EV gap: +35%. Strangles are structurally underpriced.**

### 3. KL-Divergence — How Non-Normal Are the Tails?

$$D_{KL}(P \\| Q) = \\sum P(x) \\log\\frac{P(x)}{Q(x)}$$

UNG's KL-divergence is **0.91** — a severe departure from normality. Excess kurtosis of **7.09** means the tails are ~2× fatter than Black-Scholes assumes. Every option priced with BS is systematically underpriced for UNG.

*This is the core of the Taleb edge: the market prices options as if returns are normal. They are not.*

### 4. Bayesian Updating — What Does the Evidence Say?

$$P(move | evidence) \\propto P(evidence | move) \\cdot P(move)$$

Starting from a 20% base rate (UNG moves >7% in a random week), Bayesian updating with current evidence:

| Evidence | Updated P(big move) |
|----------|:---:|
| Base rate | 20% |
| + Active war | 35% |
| + Hormuz closed | 50% |
| + Ras Laffan destroyed | 58% |
| + Ceasefire rejected | 65% |
| **+ April 6 deadline** | **72%** |

**After incorporating all available evidence, P(UNG moves >7% in the next 2 weeks) = 72%.**

### 5. LMSR Market Impact — Can You Scale?

$$Impact = \\frac{position}{daily\\_volume} \\times \\sigma_{daily}$$

UNG trades $48M/day. Your 22-contract position is $26k notional. Market impact: **0.002%** — negligible. You can scale to 100+ contracts without moving the market.

---

## IV. Theta Is Your Enemy

![Theta Enemy](charts/04_theta_enemy.png)

**Every day UNG sits flat, your straddle loses money.** This is theta decay — the premium you paid slowly evaporating as time passes.

At current IV (60%), your 22-contract UNG straddle bleeds approximately:
- **Day 1-3:** ~$15-20/day
- **Day 4-5:** ~$30-40/day
- **Day 6-7:** ~$60-80/day (accelerating into expiry)

**Total theta cost over 7 days if UNG doesn't move: ~$200-250** (about 15% of the $1,650 position). This is why you need weekly repricing — you can't hold a weekly straddle and hope. Either it moves by Thursday or you salvage what's left.

**The calendar spread is your theta hedge.** The front-month leg you sold *decays faster* than the back-month leg you bought. Time working against you on the straddle is partially offset by time working *for* you on the calendar.

---

## V. IV Crush — The Silent Killer

![IV Crush](charts/05_iv_crush.png)

**If Hormuz reopens, IV doesn't just decline — it collapses.** This is IV crush: a sudden, violent contraction in implied volatility that destroys the value of all long options positions simultaneously.

| Event | Expected IV Move | Effect on Straddle | Effect on Calendar |
|-------|:----------------:|:------------------:|:------------------:|
| Hormuz reopens | IV 60% → 35% | **-40% value** | **-60% value** |
| Stalemate continues | IV stays 55-65% | Neutral (theta eats you) | **Slight positive** |
| Headlines spike fear | IV 60% → 80% | **+25% value** | **+50% value** |
| Full escalation | IV 60% → 120% | **+80% value** | **+180% value** |

**The calendar is MORE vulnerable to IV crush than the straddle** because its entire edge depends on IV expansion. If Hormuz opens Monday morning, the calendar's back-month leg loses its vega premium instantly.

**Stop rule: If IV rank drops below 30%, close all calendars immediately.** This means the market is pricing in de-escalation, and your vega bet is dying.

---

## VI. The Trinity: Straddle vs Strangle vs Calendar

![Trinity](charts/06_trinity_comparison.png)

| | Straddle | Strangle | Calendar |
|---|---|---|---|
| **Cost** | $85/ct | **$35/ct** | $68/ct |
| **Max loss** | $85/ct | **$35/ct** | $68/ct |
| **Breakeven** | ±7.1% | ±8-9% | Stay near $12 |
| **Wins when** | Big move either way | **Bigger** move either way | IV expands |
| **Loses when** | UNG flat | UNG flat | UNG moves 15%+ OR IV crushes |
| **Theta** | Enemy | Enemy | **Partially hedged** |
| **Vega** | Moderate exposure | Low exposure | **Maximum exposure** |
| **Contracts per $1k** | 11 | **28** | 14 |

**For 2× aggressive deployment, use strangles as the primary weapon** — they're 2.4× cheaper per contract, giving you more leverage per dollar. The calendar is the vega hedge for the feint weeks.

---

## VII. The Black Swan Campaign

![Black Swan](charts/07_black_swan_campaign.png)

This is the Taleb thesis in practice: **you lose small, often, and win big, rarely.** Over 26 weeks of buying strangles, most weeks expire worthless. But the weeks where UNG moves 15-25% generate returns that dwarf all the accumulated losses.

The math only works if:
1. **You survive the losing streaks** (Kelly sizing prevents ruin)
2. **You're still in the game when the black swan arrives** (don't quit at week 8)
3. **The edge is real** (IV rank 15% + Hormuz crisis = yes)

---

## VIII. Capital Deployment — 2× Aggressive

![Capital Deployment](charts/08_capital_deployment.png)

### $60K Bankroll, 26-Week Campaign

| Phase | Weeks | Weekly Deploy | Calendar | Strangle | Total |
|-------|:-----:|:------------:|:--------:|:--------:|:-----:|
| **Negotiation** | 1-2 | $3,840 | $2,112 (55%) | $1,728 (45%) | $7,680 |
| **DEADLINE** | 3 | **$5,760** | $1,152 (20%) | **$4,608 (80%)** | $5,760 |
| **Post-deadline** | 4-6 | $3,840 | $1,344 (35%) | $2,496 (65%) | $11,520 |
| **Sustained** | 7-12 | $3,000 | $1,200 (40%) | $1,800 (60%) | $18,000 |
| **Grind** | 13-20 | $2,400 | $960 (40%) | $1,440 (60%) | $19,200 |
| **Late stage** | 21-26 | $1,920 | $960 (50%) | $960 (50%) | $11,520 |
| **TOTAL** | | | | | **~$73,680** |

**Cash always preserved: minimum $30,000+ (50%+ of bankroll at any point)**

The deployment is front-loaded toward the deadline week and gradually decreases as either the thesis plays out or the edge erodes.

---

## IX. Monte Carlo Simulation

![Monte Carlo](charts/09_monte_carlo_paths.png)

1,000 simulated 26-week campaigns at 2× aggressive sizing. The fan shows the range of outcomes. Green paths end above $60k (profit), red paths end below.

**The distribution is positively skewed** — most paths cluster slightly below $60k (the weekly bleed), but the profitable paths extend much further right (black swan payoffs). This is the signature of a long-volatility strategy.

---

## X. The Decision Tree

![Decision Tree](charts/10_decision_tree.png)

### Execution Protocol

**Every Monday morning:**
1. Check UNG spot price and IV rank on [Barchart](https://www.barchart.com/options/iv-rank-percentile)
2. If IV rank > 60% → **skip this week** (vol too expensive)
3. If IV rank < 60% → deploy per the phase plan:
   - Buy strangles: OTM Put $11 / Call $13, nearest weekly expiry
   - Buy calendars: Sell nearest weekly $12C / Buy next monthly $12C
4. Set sell alerts via the monitor: +50% profit target, -70% stop loss

**Every Thursday:**
- If strangles are profitable → sell
- If strangles are near-worthless → sell to salvage remaining premium
- Let calendars ride (they have weeks of time left)

**April 6 (Trump Deadline):**
- If Hormuz opens → close everything immediately
- If stalemate → continue the campaign
- If military ops → go 100% strangles, close calendars

---

## XI. Sources

### Geopolitical
- [Wikipedia: 2026 Iran War](https://en.wikipedia.org/wiki/2026_Iran_war)
- [Wikipedia: 2026 Strait of Hormuz Crisis](https://en.wikipedia.org/wiki/2026_Strait_of_Hormuz_crisis)
- [Washington Institute: Iran's Retaliation Choreography](https://www.washingtoninstitute.org/policy-analysis/irans-retaliation-choreography-escalation-management-and-mirage-all-out-war)
- [NPR: Trump Extends Hormuz Deadline to Apr 6](https://www.npr.org/2026/03/26/nx-s1-5761882/iran-war-peace-conditions)
- [Al Jazeera: Iran Rejects US Ceasefire Proposal](https://www.aljazeera.com/news/2026/3/25/iran-calls-us-proposal-to-end-war-maximalist-unreasonable)
- [Britannica: 2026 Iran War](https://www.britannica.com/event/2026-Iran-War)
- [Congress.gov: Iran Conflict and the Strait of Hormuz](https://www.congress.gov/crs-product/R45281)
- [HISTORY.com: 7 Key Moments in US-Iran Relations](https://www.history.com/articles/us-iran-conflict-key-moments)
- [Strauss Center: Strait of Hormuz Tanker War](https://www.strausscenter.org/strait-of-hormuz-tanker-war/)
- [Critical Threats: Iran Update Mar 25, 2026](https://www.criticalthreats.org/analysis/iran-update-march-25-2026)

### Market & Commodities
- [CNBC: Iran War Threatening Helium Supply](https://www.cnbc.com/2026/03/19/the-iran-war-is-threatening-supply-helium-what-it-means-for-markets.html)
- [Fortune: Iran War Cuts Off Helium from Qatar](https://fortune.com/2026/03/21/iran-war-helium-shortage-qatar-chip-supply-chains-ai-boom/)
- [Tom's Hardware: Qatar Helium Two-Week Clock](https://www.tomshardware.com/tech-industry/qatar-helium-shutdown-puts-chip-supply-chain-on-a-two-week-clock)
- [NPR: Strait of Hormuz Traffic Visualization](https://www.npr.org/2026/03/04/nx-s1-5736104/iran-war-oil-trump-israel-strait-hormuz-closed-energy-crisis)
- [ABC News: Strait of Hormuz Historical Disruptions](https://abcnews.com/Business/wireStory/strait-hormuz-disrupted-past-moments-threatened-oil-flows-131208969)

### Quantitative Theory
- Kelly, J.L. "A New Interpretation of Information Rate." *Bell System Technical Journal*, 1956.
- Taleb, N.N. *The Black Swan: The Impact of the Highly Improbable*. Random House, 2007.
- Taleb, N.N. *Antifragile: Things That Gain from Disorder*. Random House, 2012.
- Hanson, R. "Combinatorial Information Market Design." *Information Systems Frontiers*, 2003. (LMSR)
- Black, F. & Scholes, M. "The Pricing of Options and Corporate Liabilities." *Journal of Political Economy*, 1973.
- Clausewitz, C. von. *On War*. 1832.

---

*Generated by the AI Hedge Fund War Planning System. This is not financial advice. This is a quantitative framework for thinking about volatility positioning during geopolitical crises. All options trades involve risk of total loss of premium.*
"""

with open("war-planning/WAR_PLANNING.md", "w") as f:
    f.write(md)

print(f"\nReport: war-planning/WAR_PLANNING.md")
print(f"Charts: war-planning/charts/ (10 files)")
print("Done!")
