"""Forex carry paper line. Separate $10,000 paper account, 1x notional.
Holds long the highest-policy-rate G10 currency against short the lowest (from policy_rates.csv),
rebalanced at the first data date of each month (and at the start). Daily P&L = cross-rate move
+ rate differential accrued per calendar day. Cost: 0.03% of notional per leg change (entry or exit),
so a switch costs 0.06%. Prices: ECB euro reference rates in g10_rates.csv (EUR itself = 1).
Rates are applied as they stand in policy_rates.csv on each run (no history kept). Paper only.
Usage: python3 carry.py -> prints JSON; writes carry_state.json"""
import csv, json, os, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); START = "2026-11-18"; EQ0 = 10000.0; COST = 0.0003
rates = {r["ccy"]: float(r["rate_pct"]) / 100 for r in csv.DictReader(open(os.path.join(HERE, "policy_rates.csv")))}
rows = sorted(csv.DictReader(open(os.path.join(HERE, "g10_rates.csv"))), key=lambda r: r["Date"])
def eurx(r, c): return 1.0 if c == "EUR" else float(r[c])
def cross(r, h, l): return eurx(r, l) / eurx(r, h)  # price of 1 unit of h in l
eq = EQ0; hold = None; log = []; peak = EQ0; mdd = 0.0; prev = None
for r in rows:
    d = r["Date"]
    if d <= START: prev = r; continue
    if hold:  # mark to market vs previous date
        h, l = hold; days = (dt.date.fromisoformat(d) - dt.date.fromisoformat(prev["Date"])).days
        eq *= 1 + (cross(r, h, l) / cross(prev, h, l) - 1) + (rates[h] - rates[l]) * days / 365
    want = (max(rates, key=rates.get), min(rates, key=rates.get))
    new_month = hold is None or d[:7] != prev["Date"][:7]
    if new_month and want != hold:
        eq *= 1 - COST * (2 if hold else 1); log.append({"date": d, "from": hold, "to": want}); hold = want
    peak = max(peak, eq); mdd = max(mdd, (peak - eq) / peak); prev = r
out = {"last_data_date": rows[-1]["Date"], "equity": round(eq, 2), "return_pct": round((eq / EQ0 - 1) * 100, 2),
       "holding": f"long {hold[0]} / short {hold[1]}" if hold else "not started",
       "rate_diff_pct": round((rates[hold[0]] - rates[hold[1]]) * 100, 2) if hold else None,
       "max_drawdown_pct": round(mdd * 100, 2), "rebalances": log}
json.dump(out, open(os.path.join(HERE, "carry_state.json"), "w"), indent=1); print(json.dumps(out, indent=1))
