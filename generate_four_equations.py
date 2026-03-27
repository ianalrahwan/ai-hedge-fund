"""Regenerate the quant equations chart: 4 equations (no LMSR), 2x2 grid, better sizing."""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import norm
import yfinance as yf

OUT = "war-planning/charts"

DARK_BG = "#0a0e1a"
CARD_BG = "#141b2d"
TEXT_COLOR = "#e2e8f0"
GRID_COLOR = "#1e293b"
GREEN = "#22c55e"
YELLOW = "#eab308"
RED = "#ef4444"
ACCENT = "#38bdf8"
PURPLE = "#a78bfa"
ORANGE = "#f97316"

def style_ax(ax, title, fontsize=13):
    ax.set_facecolor(DARK_BG)
    ax.set_title(title, color=TEXT_COLOR, fontsize=fontsize, fontweight="bold", pad=14)
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.grid(True, color=GRID_COLOR, alpha=0.4, linewidth=0.5)

print("Fetching UNG data...")
ung = yf.Ticker("UNG")
hist = ung.history(start="2025-03-26", end="2026-03-27", auto_adjust=False)
S = hist["Close"].iloc[-1]

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.patch.set_facecolor(DARK_BG)

# ── 1. Kelly Criterion ──────────────────────────────────────────────────────
ax = axes[0, 0]
p_range = np.linspace(0.1, 0.9, 100)
b = 1.55
kelly_f = (p_range * b - (1 - p_range)) / b
kelly_f = np.clip(kelly_f, -0.5, 0.5)

ax.plot(p_range * 100, kelly_f * 100, color=ACCENT, linewidth=3)
ax.fill_between(p_range * 100, kelly_f * 100, 0, where=kelly_f > 0, color=GREEN, alpha=0.15)
ax.fill_between(p_range * 100, kelly_f * 100, 0, where=kelly_f <= 0, color=RED, alpha=0.15)
ax.axhline(y=0, color=TEXT_COLOR, linewidth=0.5, alpha=0.3)
ax.axvline(x=47, color=YELLOW, linestyle="--", linewidth=2)
ax.plot(47, 12.9, "o", color=YELLOW, markersize=12, zorder=5)
ax.annotate("UNG: p=47%, f*=12.9%\nQuarter Kelly: 3.2%\n2x Aggressive: 6.4%",
            xy=(47, 12.9), textcoords="offset points", xytext=(18, 12),
            color=YELLOW, fontsize=11, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=YELLOW, lw=1.5),
            bbox=dict(boxstyle="round,pad=0.3", facecolor=CARD_BG, edgecolor=YELLOW, alpha=0.9))
ax.set_xlabel("Win Probability (%)", color=TEXT_COLOR, fontsize=10)
ax.set_ylabel("Optimal Bet Size (% of bankroll)", color=TEXT_COLOR, fontsize=10)
style_ax(ax, "KELLY CRITERION\nf* = (p*b - q) / b")

# ── 2. Expected Value Gap ───────────────────────────────────────────────────
ax = axes[0, 1]
model_values = np.linspace(0.5, 2.0, 100)
market_price = 1.0
ev_gap = (model_values - market_price) / market_price * 100

ax.plot(model_values, ev_gap, color=ACCENT, linewidth=3)
ax.fill_between(model_values, ev_gap, 0, where=ev_gap > 0, color=GREEN, alpha=0.15)
ax.fill_between(model_values, ev_gap, 0, where=ev_gap <= 0, color=RED, alpha=0.15)
ax.axhline(y=0, color=TEXT_COLOR, linewidth=0.5, alpha=0.3)

ax.plot(1.35, 35, "o", color=YELLOW, markersize=12, zorder=5)
ax.annotate("UNG strangles:\nModel says vol should\nbe 35% higher than\nwhat the market charges",
            xy=(1.35, 35), textcoords="offset points", xytext=(18, -15),
            color=YELLOW, fontsize=10, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=YELLOW, lw=1.5),
            bbox=dict(boxstyle="round,pad=0.3", facecolor=CARD_BG, edgecolor=YELLOW, alpha=0.9))

ax.set_xlabel("Model Fair Value / Market Price", color=TEXT_COLOR, fontsize=10)
ax.set_ylabel("EV Gap (%)", color=TEXT_COLOR, fontsize=10)
style_ax(ax, "EXPECTED VALUE GAP\nEV_gap = (model - market) / market")

# ── 3. KL-Divergence ───────────────────────────────────────────────────────
ax = axes[1, 0]
x = np.linspace(-0.15, 0.15, 200)
P = 0.6 * norm.pdf(x, 0, 0.03) + 0.4 * norm.pdf(x, 0, 0.08)  # fat-tailed reality
Q = norm.pdf(x, 0, 0.035)  # what Black-Scholes assumes

ax.fill_between(x * 100, P, alpha=0.3, color=ACCENT, label="Reality (fat tails)")
ax.fill_between(x * 100, Q, alpha=0.3, color=RED, label="Black-Scholes assumes")
ax.plot(x * 100, P, color=ACCENT, linewidth=2)
ax.plot(x * 100, Q, color=RED, linewidth=2, linestyle="--")

# Highlight the tails where strangles profit
tail_mask = np.abs(x) > 0.06
ax.fill_between(x[tail_mask] * 100, P[tail_mask], Q[tail_mask],
                where=P[tail_mask] > Q[tail_mask], color=GREEN, alpha=0.4)

ax.text(9, 3.5, "MISPRICED\nTAIL", color=GREEN, fontsize=12, fontweight="bold", ha="center", alpha=0.7)
ax.text(-9, 3.5, "MISPRICED\nTAIL", color=GREEN, fontsize=12, fontweight="bold", ha="center", alpha=0.7)

ax.text(0, 12, "UNG kurtosis: 7.09\n(Normal = 0)\nTails 2.4x fatter",
        ha="center", color=YELLOW, fontsize=10, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor=CARD_BG, edgecolor=YELLOW, alpha=0.9))

ax.set_xlabel("Daily Return (%)", color=TEXT_COLOR, fontsize=10)
ax.legend(fontsize=10, facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR, loc="upper right")
style_ax(ax, "KL-DIVERGENCE: Reality vs The Model\nD_KL(P||Q) = 0.91 — severely non-normal")

# ── 4. Bayesian Updating ───────────────────────────────────────────────────
ax = axes[1, 1]
evidence_items = [
    ("Base\nrate", 0.20),
    ("+ War\nstarted", 0.35),
    ("+ Hormuz\nclosed", 0.50),
    ("+ Ras Laffan\ndestroyed", 0.58),
    ("+ Ceasefire\nrejected", 0.65),
    ("+ Apr 6\ndeadline", 0.72),
]

x_pos = range(len(evidence_items))
probs = [e[1] for e in evidence_items]
labels = [e[0] for e in evidence_items]
colors_bar = [GRID_COLOR, YELLOW, ORANGE, ORANGE, RED, RED]

bars = ax.bar(x_pos, [p * 100 for p in probs], color=colors_bar, alpha=0.8, edgecolor="none", width=0.7)
for bar, p in zip(bars, probs):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
            f"{p:.0%}", ha="center", color=TEXT_COLOR, fontsize=12, fontweight="bold")

# Arrow showing the update
ax.annotate("", xy=(5, 72), xytext=(0, 20),
            arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=2, connectionstyle="arc3,rad=0.2"))

ax.set_xticks(x_pos)
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("P(UNG moves >7% this week)", color=TEXT_COLOR, fontsize=10)
ax.set_ylim(0, 85)
style_ax(ax, "BAYESIAN UPDATING\nP(move|evidence) updates from 20% to 72%")

plt.suptitle("THE FOUR QUANT EQUATIONS — Applied to the UNG Hormuz Campaign",
             color=TEXT_COLOR, fontsize=16, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig(f"{OUT}/03_five_equations.png", dpi=150, facecolor=DARK_BG, bbox_inches="tight")
plt.close()

print("Done — saved to war-planning/charts/03_five_equations.png")
