"""Forex paper bot. Replays the whole strategy from ecb_rates.csv every run (deterministic).
Data: ECB euro reference rates (one daily fix ~16:00 CET), converted to EURUSD, GBPUSD, USDJPY.
Strategy: 20-day close breakout, entries filtered by trend: MA50>MA200 once 200 days exist,
else close vs MA50 once 50 days exist, else no filter. Exit on opposite 10-day close extreme,
trend flip against the position, or stop (2x avg abs daily move at entry). Size = 1% of equity
at risk per trade. Spread cost: EURUSD 1.0 pip, GBPUSD 1.5 pip, USDJPY 1.5 pip per round trip.
Paper only. Trades only on dates after START; earlier rows are indicator history.
Usage: python3 sim.py  -> prints JSON summary; writes state.json"""
import csv, json, os, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__))
START = "2026-11-18"; EQ0 = 10000.0; RISK = 0.01
SPREAD = {"EURUSD": 0.00010, "GBPUSD": 0.00015, "USDJPY": 0.015}
rows = sorted(csv.DictReader(open(os.path.join(HERE, "ecb_rates.csv"))), key=lambda r: r["Date"])
dates = [r["Date"] for r in rows]
px = {"EURUSD": [float(r["USD"]) for r in rows],
      "GBPUSD": [float(r["USD"]) / float(r["GBP"]) for r in rows],
      "USDJPY": [float(r["JPY"]) / float(r["USD"]) for r in rows]}
def usd(pair, pnl_quote, price):  # convert P&L in quote ccy to USD
    return pnl_quote / price if pair == "USDJPY" else pnl_quote
eq = EQ0; pos = {}; trades = []; curve = []
for i, d in enumerate(dates):
    for pair, p in px.items():
        c = p[i]
        if i < 20: continue
        hi20, lo20 = max(p[i-20:i]), min(p[i-20:i]); hi10, lo10 = max(p[i-10:i]), min(p[i-10:i])
        if i >= 200: trend = 1 if st.mean(p[i-50:i]) > st.mean(p[i-200:i]) else -1
        elif i >= 50: trend = 1 if c > st.mean(p[i-50:i]) else -1
        else: trend = 0
        o = pos.get(pair)
        if o:
            s = o["side"]; reason = None
            if (s == 1 and c <= o["stop"]) or (s == -1 and c >= o["stop"]): reason = "stop"
            elif (s == 1 and c < lo10) or (s == -1 and c > hi10): reason = "10d exit"
            elif trend == -s: reason = "trend flip"
            if reason:
                pnl = usd(pair, (c - o["entry"]) * s * o["units"] - SPREAD[pair] * o["units"], c)
                eq += pnl; trades.append({**o, "pair": pair, "exit_date": d, "exit": round(c, 5), "pnl": round(pnl, 2), "reason": reason})
                del pos[pair]
        if d > START and pair not in pos:
            side = 1 if (c > hi20 and trend >= 0) else -1 if (c < lo20 and trend <= 0) else 0
            if side:
                atr = st.mean(abs(p[k] - p[k-1]) for k in range(i-19, i+1)); dist = 2 * atr
                risk_q = eq * RISK * (c if pair == "USDJPY" else 1)
                pos[pair] = {"side": side, "entry_date": d, "entry": round(c, 5), "units": round(risk_q / dist),
                             "stop": round(c - side * dist, 5)}
    open_pnl = sum(usd(pr, (px[pr][i] - o["entry"]) * o["side"] * o["units"] - SPREAD[pr] * o["units"], px[pr][i]) for pr, o in pos.items())
    if d > START: curve.append((d, round(eq + open_pnl, 2)))
last = curve[-1][1] if curve else EQ0
peak, mdd = EQ0, 0.0
for _, v in curve: peak = max(peak, v); mdd = max(mdd, (peak - v) / peak)
wins = [t for t in trades if t["pnl"] > 0]
out = {"last_data_date": dates[-1], "days_of_history": len(dates), "equity": last, "return_pct": round((last / EQ0 - 1) * 100, 2),
       "realized_equity": round(eq, 2), "closed_trades": len(trades), "win_rate_pct": round(100 * len(wins) / len(trades), 1) if trades else None,
       "max_drawdown_pct": round(mdd * 100, 2), "open_positions": {k: {**v, "last": round(px[k][-1], 5)} for k, v in pos.items()},
       "trades": trades, "trend_filter": "MA50>MA200" if len(dates) > 200 else "close vs MA50" if len(dates) > 50 else "none yet (<50 days)"}
json.dump(out, open(os.path.join(HERE, "state.json"), "w"), indent=1); print(json.dumps(out, indent=1))
