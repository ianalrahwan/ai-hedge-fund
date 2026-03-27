"""
Leg-Out Analysis: Should you sell the put and hold the call?
UNG $12 Straddle, 22 contracts, expiry Apr 1 (Tuesday)
Entry: $0.39/share avg cost basis (straddle)
Current UNG: ~$11.84
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import norm
import math

# ── Position parameters ─────────────────────────────────────────────────
S = 11.84           # Current UNG price
K = 12.00           # Strike
contracts = 22
cost_basis_per_share = 0.39  # Total straddle cost per share at entry
cost_basis_total = cost_basis_per_share * contracts * 100  # $858

# Current position value
current_value = 1166.0  # From app
current_profit = 315.20

# Time parameters
DTE_now = 3          # Calendar days to expiry (Fri → Tue)
trading_days = 2     # Mon + Tue
weekend_theta_days = 3  # Fri close → Mon open = 3 calendar days

# Estimated IV (UNG has been ~45-55% recently)
IV = 0.50            # 50% annualized
T_now = DTE_now / 365
T_monday = 2 / 365   # After weekend, 2 calendar days left

# ── Black-Scholes functions ─────────────────────────────────────────────
def bs_price(S, K, T, sigma, option_type='call'):
    if T <= 0:
        if option_type == 'call':
            return max(S - K, 0)
        else:
            return max(K - S, 0)
    d1 = (math.log(S / K) + (0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if option_type == 'call':
        return S * norm.cdf(d1) - K * norm.cdf(d2)
    else:
        return K * norm.cdf(-d2) - S * norm.cdf(-d1)

def bs_greeks(S, K, T, sigma, option_type='call'):
    if T <= 0:
        return {'delta': 1 if option_type == 'call' and S > K else (-1 if option_type == 'put' and S < K else 0),
                'gamma': 0, 'theta': 0, 'vega': 0, 'vanna': 0}
    d1 = (math.log(S / K) + (0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    npdf_d1 = norm.pdf(d1)

    gamma = npdf_d1 / (S * sigma * math.sqrt(T))
    theta_call = -(S * npdf_d1 * sigma) / (2 * math.sqrt(T))
    vega = S * npdf_d1 * math.sqrt(T) / 100  # per 1% IV move
    vanna = -npdf_d1 * d2 / sigma  # dDelta/dVol

    if option_type == 'call':
        delta = norm.cdf(d1)
        theta = theta_call / 365
    else:
        delta = norm.cdf(d1) - 1
        theta = theta_call / 365

    return {'delta': delta, 'gamma': gamma, 'theta': theta, 'vega': vega, 'vanna': vanna}

# ── Current Greeks ──────────────────────────────────────────────────────
print("=" * 70)
print("UNG $12 STRADDLE — LEG-OUT ANALYSIS")
print("=" * 70)

call_price_now = bs_price(S, K, T_now, IV, 'call')
put_price_now = bs_price(S, K, T_now, IV, 'put')
straddle_price_now = call_price_now + put_price_now

call_greeks = bs_greeks(S, K, T_now, IV, 'call')
put_greeks = bs_greeks(S, K, T_now, IV, 'put')

print(f"\nCurrent UNG: ${S:.2f} | Strike: ${K:.2f} | IV: {IV*100:.0f}% | DTE: {DTE_now}")
print(f"\nTheoretical Prices (BS):")
print(f"  Call: ${call_price_now:.4f} | Put: ${put_price_now:.4f} | Straddle: ${straddle_price_now:.4f}")
print(f"  Your cost basis: ${cost_basis_per_share:.4f}/share")
print(f"\nGreeks:")
print(f"  {'':15s} {'Delta':>8s} {'Gamma':>8s} {'Theta/day':>10s} {'Vega/1%':>8s} {'Vanna':>8s}")
print(f"  {'Call':15s} {call_greeks['delta']:8.3f} {call_greeks['gamma']:8.4f} {call_greeks['theta']:10.4f} {call_greeks['vega']:8.4f} {call_greeks['vanna']:8.4f}")
print(f"  {'Put':15s} {put_greeks['delta']:8.3f} {put_greeks['gamma']:8.4f} {put_greeks['theta']:10.4f} {put_greeks['vega']:8.4f} {put_greeks['vanna']:8.4f}")
print(f"  {'Straddle':15s} {call_greeks['delta']+put_greeks['delta']:8.3f} {call_greeks['gamma']+put_greeks['gamma']:8.4f} {call_greeks['theta']+put_greeks['theta']:10.4f} {call_greeks['vega']+put_greeks['vega']:8.4f}")

# ── Weekend Theta Cost ──────────────────────────────────────────────────
print(f"\n{'='*70}")
print("WEEKEND THETA COST (3 calendar days)")
print(f"{'='*70}")

straddle_theta_weekend = (call_greeks['theta'] + put_greeks['theta']) * 3
call_only_theta_weekend = call_greeks['theta'] * 3

print(f"  Straddle weekend theta (22 contracts): ${straddle_theta_weekend * contracts * 100:.2f}")
print(f"  Call-only weekend theta (22 contracts): ${call_only_theta_weekend * contracts * 100:.2f}")
print(f"  Theta savings from legging out put:     ${(straddle_theta_weekend - call_only_theta_weekend) * contracts * 100:.2f}")

# ── Scenario Analysis: Monday Open ──────────────────────────────────────
print(f"\n{'='*70}")
print("SCENARIO ANALYSIS: MONDAY OPEN P&L")
print(f"{'='*70}")

monday_prices = np.arange(10.50, 13.51, 0.25)
IV_scenarios = [0.40, 0.50, 0.60, 0.80, 1.00]  # IV crush to IV spike

# If you sell put now, you get put_price_now * 100 * 22
put_proceeds = put_price_now * 100 * contracts

print(f"\n  Put sale proceeds (at theoretical mid): ${put_proceeds:.2f}")
print(f"  Remaining call cost basis: ${cost_basis_total - put_proceeds:.2f}")

print(f"\n  STRATEGY 1: HOLD FULL STRADDLE")
print(f"  {'Monday':>8s}", end="")
for iv in IV_scenarios:
    print(f"  IV={iv*100:.0f}%", end="")
print(f"  {'':>4s}| Move needed to break even")
print(f"  {'Price':>8s}", end="")
for iv in IV_scenarios:
    print(f"  {'P&L':>8s}", end="")
print()

for price in monday_prices:
    move_pct = (price - S) / S * 100
    print(f"  ${price:>6.2f}", end="")
    for iv in IV_scenarios:
        call_val = bs_price(price, K, T_monday, iv, 'call')
        put_val = bs_price(price, K, T_monday, iv, 'put')
        straddle_val = (call_val + put_val) * 100 * contracts
        pnl = straddle_val - cost_basis_total
        color = "+" if pnl >= 0 else ""
        print(f"  {color}${pnl:>7.0f}", end="")
    print(f"  ({move_pct:+.1f}%)")

print(f"\n  STRATEGY 2: LEG OUT PUT NOW → HOLD CALL ONLY")
print(f"  (Put sold at ~${put_price_now:.3f}, proceeds: ${put_proceeds:.0f})")
print(f"  {'Monday':>8s}", end="")
for iv in IV_scenarios:
    print(f"  IV={iv*100:.0f}%", end="")
print()
print(f"  {'Price':>8s}", end="")
for iv in IV_scenarios:
    print(f"  {'P&L':>8s}", end="")
print()

for price in monday_prices:
    move_pct = (price - S) / S * 100
    print(f"  ${price:>6.2f}", end="")
    for iv in IV_scenarios:
        call_val = bs_price(price, K, T_monday, iv, 'call')
        call_total = call_val * 100 * contracts
        # Total P&L = put proceeds + call value - original cost basis
        pnl = put_proceeds + call_total - cost_basis_total
        color = "+" if pnl >= 0 else ""
        print(f"  {color}${pnl:>7.0f}", end="")
    print(f"  ({move_pct:+.1f}%)")

# ── The Critical Comparison ─────────────────────────────────────────────
print(f"\n{'='*70}")
print("HEAD-TO-HEAD: STRADDLE vs LEGGED-OUT CALL")
print("(Difference = how much better/worse legging out is)")
print(f"{'='*70}")

print(f"\n  Positive = legging out WINS | Negative = straddle WINS")
print(f"  {'Monday':>8s}", end="")
for iv in IV_scenarios:
    print(f"  IV={iv*100:.0f}%", end="")
print()

for price in [10.50, 11.00, 11.50, 11.84, 12.00, 12.25, 12.50, 13.00, 13.50]:
    print(f"  ${price:>6.2f}", end="")
    for iv in IV_scenarios:
        call_val = bs_price(price, K, T_monday, iv, 'call')
        put_val = bs_price(price, K, T_monday, iv, 'put')

        straddle_pnl = (call_val + put_val) * 100 * contracts - cost_basis_total
        legged_pnl = put_proceeds + call_val * 100 * contracts - cost_basis_total

        diff = legged_pnl - straddle_pnl
        print(f"  {'+' if diff >= 0 else ''}${diff:>7.0f}", end="")
    print()

print(f"\n  Interpretation:")
print(f"  - Legging out ALWAYS wins when UNG goes UP (you locked in put profit, call appreciates)")
print(f"  - Straddle ALWAYS wins when UNG goes DOWN (the put you sold would have made more)")
print(f"  - The crossover is around ${K:.2f} (the strike)")

# ── Decision Matrix ─────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("DECISION MATRIX")
print(f"{'='*70}")

# Calculate breakeven for call-only (how much UNG needs to rise)
call_cost_after_put_sale = (cost_basis_total - put_proceeds) / (contracts * 100)
print(f"\n  If you leg out:")
print(f"    Put proceeds lock in: ${put_proceeds:.0f}")
print(f"    Remaining call cost basis: ${cost_basis_total - put_proceeds:.0f} (${call_cost_after_put_sale:.3f}/share)")
print(f"    Call breakeven on Monday: UNG needs to be above ${K + call_cost_after_put_sale:.2f}")
print(f"    Max loss (call expires worthless): -${cost_basis_total - put_proceeds:.0f}")
print(f"    But net of put gain: {'+'  if put_proceeds > cost_basis_total/2 else '-'}${abs(put_proceeds - cost_basis_total/2):.0f} vs entry")

print(f"\n  If you hold straddle:")
print(f"    Weekend theta cost (3 days): ~${abs(straddle_theta_weekend * contracts * 100):.0f}")
print(f"    Straddle breakeven: UNG needs to move ±${cost_basis_per_share:.2f} from ${K:.2f}")
print(f"    i.e., below ${K - cost_basis_per_share:.2f} or above ${K + cost_basis_per_share:.2f}")
print(f"    Max loss if flat through Tuesday: ~${cost_basis_total:.0f} (full premium)")

# ── Probability-weighted expected value ─────────────────────────────────
print(f"\n{'='*70}")
print("PROBABILITY-WEIGHTED EV (using your war thesis probabilities)")
print(f"{'='*70}")

scenarios = [
    ("Escalation weekend gap UP", 0.35, 12.80, 0.70),   # +8%, IV spikes to 70%
    ("Moderate up drift", 0.20, 12.20, 0.55),            # +3%, modest IV bump
    ("Flat / no news", 0.20, 11.85, 0.45),               # flat, IV drifts down
    ("De-escalation gap DOWN", 0.15, 11.20, 0.35),       # -5.4%, IV crush
    ("Major escalation spike", 0.10, 13.50, 1.00),       # +14%, IV explosion
]

print(f"\n  {'Scenario':<30s} {'Prob':>5s} {'UNG':>6s} {'IV':>5s} {'Straddle':>10s} {'Legged':>10s} {'Winner':>10s}")

ev_straddle = 0
ev_legged = 0

for name, prob, price, iv in scenarios:
    call_val = bs_price(price, K, T_monday, iv, 'call')
    put_val = bs_price(price, K, T_monday, iv, 'put')

    straddle_pnl = (call_val + put_val) * 100 * contracts - cost_basis_total
    legged_pnl = put_proceeds + call_val * 100 * contracts - cost_basis_total

    ev_straddle += prob * straddle_pnl
    ev_legged += prob * legged_pnl

    winner = "LEG OUT" if legged_pnl > straddle_pnl else "STRADDLE"
    print(f"  {name:<30s} {prob:>5.0%} ${price:>5.2f} {iv:>4.0%} {'+' if straddle_pnl>=0 else ''}${straddle_pnl:>8.0f} {'+' if legged_pnl>=0 else ''}${legged_pnl:>8.0f} {winner:>10s}")

print(f"\n  {'Expected Value':<30s} {'':>5s} {'':>6s} {'':>5s} {'+' if ev_straddle>=0 else ''}${ev_straddle:>8.0f} {'+' if ev_legged>=0 else ''}${ev_legged:>8.0f} {'LEG OUT' if ev_legged > ev_straddle else 'STRADDLE':>10s}")
print(f"\n  EV difference: ${ev_legged - ev_straddle:+.0f} in favor of {'legging out' if ev_legged > ev_straddle else 'holding straddle'}")

# ── Generate visual ─────────────────────────────────────────────────────
DARK_BG = "#0f172a"
CARD_BG = "#1e293b"
TEXT_COLOR = "#e2e8f0"
GRID_COLOR = "#334155"
GREEN = "#22c55e"
RED = "#ef4444"
GOLD = "#ffd700"
ACCENT = "#38bdf8"

fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.patch.set_facecolor(DARK_BG)
fig.suptitle("LEG OUT PUT vs HOLD STRADDLE — P&L by Monday Open Price",
             color=GOLD, fontsize=16, fontweight="bold", y=0.98)

prices = np.arange(10.00, 14.01, 0.05)

for idx, iv in enumerate([0.50, 0.80]):
    ax = axes[idx]
    ax.set_facecolor(DARK_BG)

    straddle_pnls = []
    legged_pnls = []

    for price in prices:
        call_val = bs_price(price, K, T_monday, iv, 'call')
        put_val = bs_price(price, K, T_monday, iv, 'put')

        straddle_pnl = (call_val + put_val) * 100 * contracts - cost_basis_total
        legged_pnl = put_proceeds + call_val * 100 * contracts - cost_basis_total

        straddle_pnls.append(straddle_pnl)
        legged_pnls.append(legged_pnl)

    ax.plot(prices, straddle_pnls, color=ACCENT, linewidth=2.5, label="Hold Straddle")
    ax.plot(prices, legged_pnls, color=GOLD, linewidth=2.5, label="Leg Out (Sell Put, Hold Call)")
    ax.axhline(y=0, color=TEXT_COLOR, linestyle="--", alpha=0.3)
    ax.axvline(x=S, color=RED, linestyle=":", alpha=0.5, label=f"Current ${S}")
    ax.axvline(x=K, color=GREEN, linestyle=":", alpha=0.5, label=f"Strike ${K}")

    # Fill the difference
    straddle_arr = np.array(straddle_pnls)
    legged_arr = np.array(legged_pnls)
    ax.fill_between(prices, straddle_arr, legged_arr,
                    where=legged_arr > straddle_arr, alpha=0.15, color=GOLD, label="Leg out wins")
    ax.fill_between(prices, straddle_arr, legged_arr,
                    where=straddle_arr > legged_arr, alpha=0.15, color=ACCENT, label="Straddle wins")

    ax.set_xlabel("UNG Monday Open Price", color=TEXT_COLOR, fontsize=11)
    ax.set_ylabel("P&L ($)", color=TEXT_COLOR, fontsize=11)
    ax.set_title(f"IV = {iv*100:.0f}% {'(current)' if iv == 0.50 else '(escalation spike)'}",
                 color=TEXT_COLOR, fontsize=13, fontweight="bold")
    ax.legend(loc="upper left", fontsize=8, facecolor=CARD_BG, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    for spine in ax.spines.values():
        spine.set_color(GRID_COLOR)
    ax.grid(True, color=GRID_COLOR, alpha=0.3)
    ax.set_xlim(10.5, 13.5)

plt.tight_layout(rect=[0, 0.06, 1, 0.94])

fig.text(0.5, 0.01,
         f"22 contracts | Entry: $0.39/share | Put sale at ~${put_price_now:.3f} locks in ${put_proceeds:.0f} | "
         f"Legging out wins on UP moves, straddle wins on DOWN moves — crossover at strike",
         ha="center", va="bottom", fontsize=10, color=TEXT_COLOR,
         bbox=dict(boxstyle="round,pad=0.4", facecolor=CARD_BG, edgecolor=GRID_COLOR, alpha=0.9))

plt.savefig("outputs/taleb-strangle-analysis/charts/leg_out_analysis.png", dpi=150, facecolor=DARK_BG, bbox_inches="tight")
plt.close()
print(f"\n  Chart saved: outputs/taleb-strangle-analysis/charts/leg_out_analysis.png")
