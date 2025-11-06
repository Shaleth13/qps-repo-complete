# Quick & Minimal: Multi-Asset, Multi-Timeframe Quant Portfolio System

This repo is a **compact, deterministic** implementation that satisfies the core assignment requirements with the least friction. It includes:

- 5 concurrent alphas (breakout, mean-reversion pairs, MTF trend, multi-asset momentum, mock orderbook).
- Deterministic synthetic data generator (multi-asset, multi-timeframe) so **replication must match**.
- Event-driven engine, paper broker, portfolio/risk, logging of market/signals/orders/fills.
- **Backtest replay** that ingests the exact market-data log from the "live" sandbox run and verifies a match.
- `results.json` produced automatically.

> Tip: Run the "live" sandbox (simulated) first to create logs, then run the replay backtest.


## One-time setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Generate deterministic synthetic data

Creates aligned 1-minute bars for 4 symbols and aggregates to 1-hour.

```bash
python scripts/generate_synth_data.py --days 5 --seed 42
```

## Run "live" sandbox (simulated)

This consumes the synthetic 1-minute feed and trades the 5 alphas concurrently while logging everything.

```bash
python scripts/run_live.py --session-id demo1
```

## Run replay backtest against the logs

Reads the market/exec logs from the live run and replays them through the backtester. Writes `results.json` with PASS/FAIL per alpha and portfolio.

```bash
python scripts/run_replay.py --session-id demo1
```

You should see a perfect match on P&L and trade counts.


## What’s inside (short)

```
src/qps/
  event.py            # Event definitions
  logger.py           # JSONL logging
  data.py             # Feed + MTF aggregator
  broker.py           # PaperBroker (deterministic fills)
  portfolio.py        # Positions, P&L
  strategy_base.py    # Base class + utils
  strategies/
    alpha1_pairs.py
    alpha2_breakout.py
    alpha3_mtf.py
    alpha4_multi_asset_momentum.py
    alpha5_orderbook_mock.py
  engine.py           # Event loop that runs all strategies
  replay.py           # Backtest/replay using logged data
  evaluate.py         # Correlations + results.json
scripts/
  generate_synth_data.py
  run_live.py
  run_replay.py
data/
  synth_*.csv         # Created by generator
logs/
  <session-id>/       # Live logs written here
results.json          # Produced by run_replay.py
```

## Notes

- Broker latency/fees are fixed to keep things replicable.
- If you want to hook real APIs later, add adapters in `data.py` and `broker.py` with the same event schema.
- Plots/reporting kept minimal to avoid heavy deps; you can extend as needed.
