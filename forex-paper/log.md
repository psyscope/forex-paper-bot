# Forex paper bot log

Paper account, $10,000 start, no real money or broker. Data: ECB daily euro reference rates (one fix a day around 16:00 CET; Yahoo and other price feeds are blocked here). Strategy and costs: see the docstring at the top of sim.py.
Price history seeded 2026-11-20 with ECB rates 2026-09-29 to 2026-11-18. Trading starts with data after 2026-11-18. Test runs 2026-11-23 to 2026-12-18.
Added 2026-11-20 at Tim's request: a separate $10,000 carry line (carry.py): long the highest-rate G10 currency vs the lowest, monthly rebalance, spread cost. Starting pick: long AUD (4.85%) / short CHF (0.00%). Rates in policy_rates.csv.

| Run date | Data through | Breakout equity | Breakout return | Carry equity | Carry return | Open positions | Closed trades | Notes |
|---|---|---|---|---|---|---|---|---|
| 2026-11-21 | 2026-11-20 | 10033.77 | +0.34% | 9890.42 | -1.10% | GBPUSD short 1.31513 | 0 | manual run; added 2026-11-19, 2026-11-20; new GBPUSD short at 1.31513 (2026-11-19); carry rebalance 2026-11-19: AUD/CHF |
| 2026-11-23 | 2026-11-23 | 10101.45 | +1.01% | 9827.87 | -1.72% | GBPUSD short 1.31513; EURUSD short 1.0939 | 0 | added 2026-11-23; new EURUSD short at 1.0939 (2026-11-23) |
| 2026-11-24 | 2026-11-24 | 10036.19 | +0.36% | 9840.85 | -1.59% | GBPUSD short 1.31513; EURUSD short 1.0939 | 0 | added 2026-11-24 |
| 2026-11-25 | 2026-11-25 | 10125.27 | +1.25% | 9657.00 | -3.43% | GBPUSD short 1.31513; EURUSD short 1.0939 | 0 | added 2026-11-25 |
| 2026-11-26 | 2026-11-26 | 10012.33 | +0.12% | 9791.74 | -2.08% | GBPUSD short 1.31513; EURUSD short 1.0939 | 0 | added 2026-11-26 |
