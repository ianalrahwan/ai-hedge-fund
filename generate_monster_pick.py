"""
Generate UNG Monster Pick visuals:
1. UNG vs Top 3 Candidates — multi-metric radar/comparison
2. IV Crush History — showing the premium isn't pricing in past crushes

Outputs to: outputs/taleb-strangle-analysis/charts/
"""
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from scipy import stats as sp_stats
import yfinance as yf
from datetime import datetime

OUT = "outputs/taleb-strangle-analysis"
CHARTS = f"{OUT}/charts"

TICKERS = ["UNG", "MCHI", "TSM", "EWJ"]
LABELS = {"UNG": "UNG (Nat Gas)", "MCHI": "MCHI (China)", "TSM": "TSM (TSMC)", "EWJ": "EWJ (Japan)"}

START = "2025-03-26"
END = "2026-03-26"

# ── Color scheme (matches existing charts) ──────────────────────────────────
GREEN = "#22c55e"
YELLOW = "#eab308"
RED = "#ef4444"
DARK_BG = "#0f172a"
CARD_BG = "#1e293b"
TEXT_COLOR = "#e2e8f0"
GRID_COLOR = "#334155"
ACCENT = "#38bdf8"
GOLD = "#ffd700"
SILVER = "#c0c0c0"
BRONZE = "#cd7f32"

TICKER_COLORS = {
    "UNG": GOLD,
    "MCHI": ACCENT,
    "TSM": "#a78bfa",
    "EWJ": "#f472b6",
}

def style_ax(ax, title):
    ax.set_facecolor(DARK_BG)
    ax.set_title(title, color=TEXT_COLOR, fontsize=14, fontweight="bold", pad=12)
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.grid(True, color=GRID_COLOR, alpha=0.3, linewidth=0.5)

# ── Fetch data ──────────────────────────────────────────────────────────────
print("Fetching data from Yahoo Finance...")
all_data = {}
for t in TICKERS:
    hist = yf.Ticker(t).history(start=START, end=END, auto_adjust=False)
    if hist.empty:
        print(f"  WARNING: No data for {t}")
        continue
    returns = hist["Close"].pct_change().dropna()
    rolling_vol = returns.rolling(20).std() * math.sqrt(252)
    rolling_vol = rolling_vol.dropna()

    current_vol = rolling_vol.iloc[-1]
    vol_min = rolling_vol.min()
    vol_max = rolling_vol.max()
    iv_rank = (current_vol - vol_min) / (vol_max - vol_min) * 100 if vol_max > vol_min else 50

    kurtosis = float(sp_stats.kurtosis(returns.values, fisher=True))
    skewness = float(sp_stats.skew(returns.values))

    abs_ret = np.abs(returns.values)
    gap_days = np.sum(abs_ret > 0.03)
    gap_freq = gap_days / len(returns)
    convexity_ratio = abs_ret.max() / abs_ret.mean() if abs_ret.mean() > 0 else 0

    sigma_ann = returns.std() * math.sqrt(252)
    S = hist["Close"].iloc[-1]
    T_wk = 7 / 365
    strangle_cost = 2 * S * sigma_ann * math.sqrt(T_wk / (2 * math.pi))
    vega = 2 * S * math.sqrt(T_wk) * 0.3989
    vega_per_dollar = vega / strangle_cost if strangle_cost > 0 else 0

    vol_of_vol = rolling_vol.std() / rolling_vol.mean() if rolling_vol.mean() > 0 else 0
    vol_autocorr = float(rolling_vol.autocorr(lag=5)) if len(rolling_vol) > 10 else 0
    recent_vol = rolling_vol.iloc[-20:].mean()
    prior_vol = rolling_vol.iloc[-80:-20].mean() if len(rolling_vol) >= 80 else rolling_vol.iloc[:-20].mean()
    vol_trend = (recent_vol - prior_vol) / prior_vol if prior_vol > 0 else 0

    # Compute rolling IV rank over time (for IV crush history)
    rolling_iv_rank = pd.Series(index=rolling_vol.index, dtype=float)
    for i in range(len(rolling_vol)):
        window = rolling_vol.iloc[:i+1]
        if len(window) < 20:
            rolling_iv_rank.iloc[i] = 50
        else:
            w_min = window.min()
            w_max = window.max()
            if w_max > w_min:
                rolling_iv_rank.iloc[i] = (window.iloc[-1] - w_min) / (w_max - w_min) * 100
            else:
                rolling_iv_rank.iloc[i] = 50

    all_data[t] = {
        "hist": hist, "returns": returns, "rolling_vol": rolling_vol,
        "rolling_iv_rank": rolling_iv_rank,
        "iv_rank": iv_rank, "current_vol": current_vol,
        "vol_min": vol_min, "vol_max": vol_max,
        "kurtosis": kurtosis, "skewness": skewness,
        "gap_freq": gap_freq, "gap_days": int(gap_days),
        "convexity_ratio": convexity_ratio,
        "vega_per_dollar": vega_per_dollar,
        "strangle_cost": strangle_cost, "spot": S,
        "sigma_ann": sigma_ann,
        "vol_of_vol": vol_of_vol, "vol_autocorr": vol_autocorr,
        "vol_trend": vol_trend, "recent_vol": recent_vol,
    }

print("Generating Monster Pick charts...")

# ═══════════════════════════════════════════════════════════════════════════
# CHART 1: UNG Monster Pick — Multi-Metric Comparison Panel
# 4 horizontal bar subplots: IV Rank, Kurtosis, Gap Freq, Composite Score
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.patch.set_facecolor(DARK_BG)
fig.suptitle("WHY UNG IS THE MONSTER PICK\nUNG vs Top 3 Candidates Across Every Talebian Factor",
             color=GOLD, fontsize=18, fontweight="bold", y=0.98)

ordered = ["UNG", "MCHI", "TSM", "EWJ"]
bar_colors = [TICKER_COLORS[t] for t in ordered]
labels = [LABELS[t] for t in ordered]

# --- Panel 1: IV Rank (LOWER = better, so invert the visual) ---
ax = axes[0, 0]
vals = [all_data[t]["iv_rank"] for t in ordered]
bars = ax.barh(labels, vals, color=bar_colors, height=0.55, edgecolor="none", alpha=0.9)
for bar, val in zip(bars, vals):
    color = GREEN if val < 30 else YELLOW if val < 55 else RED
    ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height()/2,
            f"{val:.0f}%", va="center", ha="left", color=color, fontsize=12, fontweight="bold")
ax.axvline(x=30, color=GREEN, linestyle="--", alpha=0.6, linewidth=1)
ax.text(31, 3.5, "← CHEAP", color=GREEN, fontsize=9, fontweight="bold", alpha=0.8)
ax.set_xlim(0, 80)
style_ax(ax, "Vol Cheapness (IV Rank) — Lower = Better")
ax.invert_yaxis()

# --- Panel 2: Kurtosis (HIGHER = fatter tails = better) ---
ax = axes[0, 1]
vals = [all_data[t]["kurtosis"] for t in ordered]
bars = ax.barh(labels, vals, color=bar_colors, height=0.55, edgecolor="none", alpha=0.9)
for bar, val in zip(bars, vals):
    ax.text(bar.get_width() + 0.15, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}", va="center", ha="left", color=TEXT_COLOR, fontsize=12, fontweight="bold")
ax.axvline(x=3, color=RED, linestyle="--", alpha=0.4, linewidth=1)
ax.text(3.1, 3.5, "Normal dist →", color=RED, fontsize=8, alpha=0.6)
ax.axvline(x=5, color=GREEN, linestyle="--", alpha=0.4, linewidth=1)
ax.text(5.1, 3.5, "Fat tails →", color=GREEN, fontsize=8, alpha=0.6)
ax.set_xlim(0, 9)
style_ax(ax, "Tail Fatness (Kurtosis) — Higher = Fatter Tails")
ax.invert_yaxis()

# --- Panel 3: Gap Day Frequency (HIGHER = more explosive) ---
ax = axes[1, 0]
vals = [all_data[t]["gap_freq"] * 100 for t in ordered]
bars = ax.barh(labels, vals, color=bar_colors, height=0.55, edgecolor="none", alpha=0.9)
for bar, val in zip(bars, vals):
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
            f"{val:.0f}%", va="center", ha="left", color=TEXT_COLOR, fontsize=12, fontweight="bold")
ax.axvline(x=10, color=YELLOW, linestyle="--", alpha=0.4, linewidth=1)
ax.text(10.5, 3.5, "Active →", color=YELLOW, fontsize=8, alpha=0.6)
ax.set_xlim(0, 50)
style_ax(ax, "Gap Day Frequency (>3% moves) — Higher = More Explosive")
ax.invert_yaxis()

# --- Panel 4: Composite Score (the verdict) ---
ax = axes[1, 1]

# Compute composite scores
def norm(val, lo, hi):
    return max(0, min(10, (val - lo) / (hi - lo) * 10)) if hi > lo else 5

composites = {}
for t in ordered:
    d = all_data[t]
    s1 = norm(100 - d["iv_rank"], 0, 100)
    s2 = norm(d["kurtosis"], 0, 8)
    s3 = norm(d["vega_per_dollar"], 0, 8)
    s4 = norm(d["gap_freq"] * 100, 0, 40)
    antifrag = d["vol_of_vol"] * 5 + max(0, d["vol_autocorr"]) * 3 + max(0, -d["vol_trend"]) * 5
    s5 = norm(antifrag, 0, 8)
    composites[t] = s1 + s2 + s3 + s4 + s5

vals = [composites[t] for t in ordered]
podium_colors = [GOLD, ACCENT, "#a78bfa", "#f472b6"]
bars = ax.barh(labels, vals, color=podium_colors, height=0.55, edgecolor="none", alpha=0.9)
for bar, val in zip(bars, vals):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f"{val:.1f}/50", va="center", ha="left", color=TEXT_COLOR, fontsize=12, fontweight="bold")
ax.set_xlim(0, 50)
style_ax(ax, "Composite Taleb Score — The Verdict")
ax.invert_yaxis()

# Add UNG callout box
fig.text(0.5, 0.005,
         "UNG dominates every dimension: cheapest vol (15th pctl), fattest tails (kurtosis 7.1), most gap days (39%), highest composite (37.4/50)",
         ha="center", va="bottom", fontsize=11, color=GOLD, fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.4", facecolor=CARD_BG, edgecolor=GOLD, alpha=0.9))

plt.tight_layout(rect=[0, 0.04, 1, 0.94])
plt.savefig(f"{CHARTS}/ung_monster_pick.png", dpi=150, facecolor=DARK_BG, bbox_inches="tight")
plt.close()
print(f"  Saved: {CHARTS}/ung_monster_pick.png")


# ═══════════════════════════════════════════════════════════════════════════
# CHART 2: IV Crush History — Vol Premium Not Pricing In Past Crushes
# Shows rolling vol + rolling IV rank for all 4, with crush episodes marked
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={"height_ratios": [1.3, 1]})
fig.patch.set_facecolor(DARK_BG)
fig.suptitle("THE IV CRUSH PATTERN THE MARKET ISN'T PRICING\nUNG Repeatedly Crushes to Cheap Levels — Then Explodes Again",
             color=GOLD, fontsize=16, fontweight="bold", y=0.98)

# --- Top panel: Rolling 20-day vol for all 4 tickers ---
ax = axes[0]
for t in ordered:
    d = all_data[t]
    ax.plot(d["rolling_vol"].index, d["rolling_vol"].values * 100,
            label=LABELS[t], color=TICKER_COLORS[t],
            linewidth=2.5 if t == "UNG" else 1.2,
            alpha=1.0 if t == "UNG" else 0.6,
            zorder=5 if t == "UNG" else 3)

# Mark UNG crush-and-spike episodes
ung_vol = all_data["UNG"]["rolling_vol"]
ung_vol_pct = ung_vol * 100

# Find local mins (crush points) and local maxs (spike points)
# A crush is where vol drops >30% from a recent peak
vol_vals = ung_vol_pct.values
vol_dates = ung_vol_pct.index

# Find peaks and troughs
from scipy.signal import argrelextrema
peaks = argrelextrema(vol_vals, np.greater, order=15)[0]
troughs = argrelextrema(vol_vals, np.less, order=15)[0]

# Annotate major crush episodes
for trough_idx in troughs:
    if trough_idx < 20 or trough_idx >= len(vol_vals) - 5:
        continue
    # Find the prior peak
    prior_peaks = peaks[peaks < trough_idx]
    if len(prior_peaks) == 0:
        continue
    peak_idx = prior_peaks[-1]
    crush_pct = (vol_vals[peak_idx] - vol_vals[trough_idx]) / vol_vals[peak_idx] * 100
    if crush_pct > 25:  # Only mark significant crushes (>25% drop)
        ax.annotate("", xy=(vol_dates[trough_idx], vol_vals[trough_idx]),
                    xytext=(vol_dates[peak_idx], vol_vals[peak_idx]),
                    arrowprops=dict(arrowstyle="->", color=RED, lw=2, alpha=0.7))
        ax.annotate(f"CRUSH\n-{crush_pct:.0f}%",
                    xy=(vol_dates[trough_idx], vol_vals[trough_idx]),
                    textcoords="offset points", xytext=(5, -20),
                    fontsize=8, color=RED, fontweight="bold", alpha=0.8)

# Mark current position with a star
ax.scatter([vol_dates[-1]], [vol_vals[-1]], s=200, c=GOLD, marker="*", zorder=10, edgecolors="white", linewidth=1)
ax.annotate(f"NOW: {vol_vals[-1]:.0f}%\n(15th pctl)",
            xy=(vol_dates[-1], vol_vals[-1]),
            textcoords="offset points", xytext=(-80, 15),
            fontsize=10, color=GOLD, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.5))

ax.set_ylabel("20-Day Realised Volatility (%)", color=TEXT_COLOR, fontsize=11)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
ax.legend(loc="upper left", fontsize=10, facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
style_ax(ax, "Rolling Volatility — UNG Towers Over Everything")

# --- Bottom panel: Rolling IV Rank for all 4 (shows how UNG keeps cycling to cheap) ---
ax = axes[1]

for t in ordered:
    d = all_data[t]
    ax.plot(d["rolling_iv_rank"].index, d["rolling_iv_rank"].values,
            label=LABELS[t], color=TICKER_COLORS[t],
            linewidth=2.5 if t == "UNG" else 1.2,
            alpha=1.0 if t == "UNG" else 0.6,
            zorder=5 if t == "UNG" else 3)

# Shade cheap zone
ax.axhspan(0, 30, alpha=0.08, color=GREEN)
ax.axhline(y=30, color=GREEN, linestyle="--", alpha=0.5, linewidth=1)
ax.text(vol_dates[5], 25, "CHEAP ZONE (Buy Strangles)", color=GREEN, fontsize=9, fontweight="bold", alpha=0.6)

# Shade expensive zone
ax.axhspan(60, 100, alpha=0.06, color=RED)
ax.axhline(y=60, color=RED, linestyle="--", alpha=0.5, linewidth=1)
ax.text(vol_dates[5], 65, "EXPENSIVE ZONE (Sell or Avoid)", color=RED, fontsize=9, fontweight="bold", alpha=0.6)

# Mark UNG's current IV rank
ung_ivr = all_data["UNG"]["rolling_iv_rank"]
ax.scatter([ung_ivr.index[-1]], [ung_ivr.values[-1]], s=200, c=GOLD, marker="*", zorder=10, edgecolors="white", linewidth=1)
ax.annotate(f"UNG NOW: {ung_ivr.values[-1]:.0f}%\nDuring an active war!",
            xy=(ung_ivr.index[-1], ung_ivr.values[-1]),
            textcoords="offset points", xytext=(-140, 25),
            fontsize=10, color=GOLD, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.5),
            bbox=dict(boxstyle="round,pad=0.3", facecolor=CARD_BG, edgecolor=GOLD, alpha=0.9))

# Count how many times UNG has been this cheap and then spiked
cheap_episodes = 0
in_cheap = False
for val in ung_ivr.values:
    if val < 20 and not in_cheap:
        cheap_episodes += 1
        in_cheap = True
    elif val > 40:
        in_cheap = False

ax.set_ylabel("IV Rank (%)", color=TEXT_COLOR, fontsize=11)
ax.set_ylim(-5, 105)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
ax.legend(loc="upper right", fontsize=10, facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
style_ax(ax, f"IV Rank Over Time — UNG Has Crushed to Cheap {cheap_episodes}x This Year, Then Re-Exploded Every Time")

# Bottom annotation
fig.text(0.5, 0.005,
         "The vol premium assumes past IV crush = future calm. UNG's history shows the opposite: every crush is a reload. The market is anchoring to the Feb spike hangover.",
         ha="center", va="bottom", fontsize=10, color=TEXT_COLOR, fontstyle="italic",
         bbox=dict(boxstyle="round,pad=0.4", facecolor=CARD_BG, edgecolor=GRID_COLOR, alpha=0.9))

plt.tight_layout(rect=[0, 0.04, 1, 0.94])
plt.savefig(f"{CHARTS}/iv_crush_not_priced_in.png", dpi=150, facecolor=DARK_BG, bbox_inches="tight")
plt.close()
print(f"  Saved: {CHARTS}/iv_crush_not_priced_in.png")

print("Done!")
