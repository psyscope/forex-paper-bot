# Forex paper bot

**Paper-trading simulation only.** No broker, no real or demo orders, no money at risk.

A 4-week test (2026-11-23 to 2026-12-18) of two simple forex strategies, run once each weekday by a scheduled Claude routine:

- **Breakout line** (`forex-paper/sim.py`): 20-day close breakout on EURUSD, GBPUSD and USDJPY, 1% risk per trade, $10,000 paper account. Reads `ecb_rates.csv`, writes `state.json`.
- **Carry line** (`forex-paper/carry.py`): long the highest-rate G10 currency against the lowest, monthly rebalance, separate $10,000 paper account. Reads `g10_rates.csv` and `policy_rates.csv`, writes `carry_state.json`.

Prices are ECB euro reference rates (one daily fix), appended by each run. `forex-paper/log.md` holds one row per run.

Run locally:

```
python3 -I forex-paper/sim.py
python3 -I forex-paper/carry.py
```

Both scripts replay everything from the CSVs each time, so results are deterministic. Strategy details are in each script's docstring.
