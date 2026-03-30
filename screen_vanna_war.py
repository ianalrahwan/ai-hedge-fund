"""
VANNA WAR ROOM — Hormuz Play Screen
Scores tickers on: vol cheapness, fat tails, war correlation, gap frequency, vol trend
"""
import math
import numpy as np
import yfinance as yf
from scipy import stats as sp_stats
from scipy.stats import norm
from datetime import datetime

candidates = {
    'USO': 'Oil ETF (direct Hormuz)',
    'XLE': 'Energy Sector ETF',
    'XOP': 'Oil & Gas E&P ETF',
    'OIH': 'Oil Services ETF',
    'OXY': 'Occidental Petroleum',
    'DVN': 'Devon Energy',
    'FANG': 'Diamondback Energy',
    'MPC': 'Marathon Petroleum',
    'VLO': 'Valero Energy',
    'PSX': 'Phillips 66',
    'HAL': 'Halliburton',
    'SLB': 'Schlumberger',
    'FRO': 'Frontline (tankers)',
    'STNG': 'Scorpio Tankers',
    'LNG': 'Cheniere Energy',
    'LMT': 'Lockheed Martin',
    'RTX': 'RTX Corp (Raytheon)',
    'NOC': 'Northrop Grumman',
    'EWY': 'South Korea ETF',
    'MCHI': 'China ETF',
}

# Get USO returns for war correlation baseline
uso = yf.Ticker('USO')
uso_hist = uso.history(start='2025-03-30', end='2026-03-30', auto_adjust=False)
uso_ret = uso_hist['Close'].pct_change().dropna()

results = []

for ticker, desc in candidates.items():
    try:
        t = yf.Ticker(ticker)
        h = t.history(start='2025-03-30', end='2026-03-30', auto_adjust=False)
        if h.empty or len(h) < 60:
            continue
        r = h['Close'].pct_change().dropna()
        rv = r.rolling(20).std() * math.sqrt(252)
        rv = rv.dropna()

        cv = rv.iloc[-1]
        vmin = rv.min()
        vmax = rv.max()
        ivr = (cv - vmin) / (vmax - vmin) * 100 if vmax > vmin else 50
        ivp = (rv < cv).sum() / len(rv) * 100

        sorted_vol = np.sort(rv.values)
        vol_95 = sorted_vol[int(len(sorted_vol) * 0.95)]
        ivr_adj = min((cv - vmin) / (vol_95 - vmin) * 100 if vol_95 > vmin else 50, 100)

        kurt = sp_stats.kurtosis(r.values, fisher=True)
        abs_ret = np.abs(r.values)
        gaps = np.sum(abs_ret > 0.03) / len(r) * 100
        S = h['Close'].iloc[-1]

        recent = rv.iloc[-20:].mean()
        prior = rv.iloc[-60:-20].mean() if len(rv) >= 60 else rv.iloc[:-20].mean()
        vol_trend = (recent - prior) / prior * 100

        common = r.index.intersection(uso_ret.index)
        last30 = common[-30:]
        war_corr = np.corrcoef(r[last30].values, uso_ret[last30].values)[0, 1] if len(last30) > 10 else 0

        # Composite: vol cheapness 30%, tails 20%, war corr 20%, gaps 15%, vol trend 15%
        vol_score = max(0, (40 - ivp) / 40 * 10) if ivp < 40 else 0
        tail_score = min(kurt / 8 * 10, 10)
        gap_score = min(gaps / 20 * 10, 10)
        war_score = max(0, war_corr * 10)
        trend_score = max(0, min(-vol_trend / 30 * 10, 10)) if vol_trend < 0 else 0
        composite = vol_score * 0.30 + tail_score * 0.20 + gap_score * 0.15 + war_score * 0.20 + trend_score * 0.15

        results.append({
            'ticker': ticker, 'desc': desc, 'spot': S,
            'vol': cv * 100, 'ivr': ivr, 'ivp': ivp, 'ivr_adj': ivr_adj,
            'kurt': kurt, 'gaps': gaps, 'war_corr': war_corr,
            'vol_trend': vol_trend, 'composite': composite,
            'vol_score': vol_score, 'tail_score': tail_score,
            'gap_score': gap_score, 'war_score': war_score, 'trend_score': trend_score,
        })
    except Exception as e:
        print(f"{ticker}: {e}")

results.sort(key=lambda x: x['composite'], reverse=True)

print("=" * 120)
print("VANNA WAR ROOM — HORMUZ PLAY SCREEN (March 30, 2026)")
print("Scoring: Vol Cheapness 30% | Fat Tails 20% | War Correlation 20% | Gap Freq 15% | Vol Trend 15%")
print("=" * 120)
header = f"{'#':>2} {'Ticker':<6} {'Description':<24} {'Spot':>8} {'Vol':>5} {'IVR':>4} {'IVP':>4} {'Kurt':>5} {'Gaps':>5} {'WCorr':>6} {'VTrnd':>6} {'Score':>6}"
print(header)
print("-" * len(header))

for i, r in enumerate(results):
    print(f"{i+1:>2} {r['ticker']:<6} {r['desc']:<24} ${r['spot']:>6.2f} {r['vol']:>4.0f}% {r['ivr']:>3.0f}% {r['ivp']:>3.0f}% {r['kurt']:>5.1f} {r['gaps']:>4.1f}% {r['war_corr']:>+5.2f} {r['vol_trend']:>+5.0f}% {r['composite']:>5.1f}")

# Top 5 deep dive
def bs_straddle(S, K, T, sigma):
    if T <= 0:
        return abs(S - K) * 2
    d1 = (math.log(S / K) + 0.5 * sigma ** 2 * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return S * norm.cdf(d1) - K * norm.cdf(d2) + K * norm.cdf(-d2) - S * norm.cdf(-d1)

print()
print("=" * 90)
print("TOP 5 — VANNA/THETA DEEP DIVE")
print("=" * 90)

for r in results[:5]:
    ticker = r['ticker']
    S = r['spot']
    sigma = r['vol'] / 100
    K = round(S)

    print(f"\n--- {ticker}: {r['desc']} ---")
    print(f"Spot: ${S:.2f} | Vol: {r['vol']:.0f}% | IVR: {r['ivr']:.0f}% | IVP: {r['ivp']:.0f}% | Kurt: {r['kurt']:.1f} | War Corr: {r['war_corr']:+.2f}")
    print(f"{'DTE':>4} {'Cost(22ct)':>11} {'Theta/day':>10} {'+10%IV':>10} {'V/T Ratio':>10} {'BE':>6} {'%Bankroll':>10}")

    for dte in [10, 17, 24, 31, 45]:
        T = dte / 365
        strad = bs_straddle(S, K, T, sigma)
        cost = strad * 22 * 100
        T2 = (dte - 1) / 365
        theta = abs(bs_straddle(S, K, T2, sigma) - strad) * 22 * 100
        strad_up = bs_straddle(S, K, T, sigma * 1.10)
        vega10 = (strad_up - strad) * 22 * 100
        ratio = vega10 / theta if theta > 0 else 0
        be = strad / S * 100
        pct = cost / 60000 * 100
        print(f"{dte:>4} ${cost:>10,.0f} ${theta:>9,.0f} ${vega10:>9,.0f} {ratio:>9.1f}x {be:>5.1f}% {pct:>9.1f}%")

print()
print("RECOMMENDATION:")
print("Look for: IVP < 35% + War Corr > +0.30 + Kurt > 4 + Vol contracting")
print("Avoid: IVP > 80% (vol already expensive), War Corr < 0 (inverse Hormuz)")
