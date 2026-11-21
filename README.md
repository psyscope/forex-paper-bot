# Forex paper bot

**Paper-trading simulation only.** No broker, no real or demo orders, no money at risk.

A 4-week test (2026-11-23 to 2026-12-18) of two simple forex strategies. A GitHub Action (`.github/workflows/daily.yml`) runs `forex-paper/daily.py` each weekday at 06:07 UTC; a Claude routine reads the results and posts a scorecard on Fridays.

- **Breakout line** (`forex-paper/sim.py`): 20-day close breakout on EURUSD, GBPUSD and USDJPY, 1% risk per trade, $10,000 paper account. Reads `ecb_rates.csv`, writes `state.json`.
- **Carry line** (`forex-paper/carry.py`): long the highest-rate G10 currency against the lowest, monthly rebalance, separate $10,000 paper account. Reads `g10_rates.csv` and `policy_rates.csv`, writes `carry_state.json`.

Prices are ECB euro reference rates (one daily fix), fetched from the ECB's 90-day XML and added by each run (existing rows are never changed). `forex-paper/log.md` holds one row per run; `forex-paper/status.json` counts consecutive data failures. `policy_rates.csv` is edited by hand.

Run locally:

```
python3 -I forex-paper/sim.py
python3 -I forex-paper/carry.py
```

Both scripts replay everything from the CSVs each time, so results are deterministic. Strategy details are in each script's docstring.
