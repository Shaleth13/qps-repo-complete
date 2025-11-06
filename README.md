# Multi-Asset Quant Portfolio System — Deterministic Live ↔ Backtest Replication

This project implements a reproducible multi-alpha trading system that can be executed in two modes:

1. **Live Simulation Mode** — streams market data, generates signals, places trades, logs all events.
2. **Replay / Backtest Mode** — replays the logged market data and verifies that the system produces **identical** portfolio outcomes.

The primary objective is **replication** — ensuring that the strategy behavior does not change between live and backtest execution.

---

## Key Features

| Component | Description |
|---------|-------------|
| Event-Driven Engine | Processes market data and dispatches events to strategies. |
| Deterministic Broker | Order matching and fills produce repeatable execution results. |
| Portfolio Manager | Tracks positions, cash, realized & unrealized PnL. |
| Multi-Alpha Support | Several independent strategies run simultaneously. |
| Log-Based Replay | Live session logs are replayed to verify identical outcomes. |

---

## Strategies Included

| Strategy File | Idea |
|--------------|------|
| `alpha_1_pairs.py` | Pair-trading mean reversion |
| `alpha_2_breakout.py` | Price breakout momentum |
| `alpha_3_mtf.py` | Multi-timeframe trend confirmation |
| `alpha_4_multi_asset.py` | Cross-asset relative momentum |
| `alpha_5_orderbook.py` | Orderflow-inspired microstructure signal |

All strategies operate independently and send signals to the broker through the engine.

---
qps-repo-complete/
│
├── scripts/ # Executable scripts (no code editing needed)
│ ├── generate_synth_data.py
│ ├── run_live.py
│ └── run_replay.py
│
├── src/
│ └── qps/
│ ├── engine.py # Core event loop
│ ├── broker.py # Trade execution logic
│ ├── portfolio.py # Position & PnL tracking
│ ├── data.py # Market data feed
│ └── strategies/ # Strategy implementations
│
├── logs/ # Created automatically after running
├── results.json # Replication result summary
└── results_detailed.json # (Optional) Per-strategy breakdown


---

## Installation

```cmd
pip install -r requirements.txt
---
Running the System
1) Generate Synthetic Market Data
python scripts/generate_synth_data.py --days 3 --seed 42

2) Run Live Simulation
python scripts/run_live.py --session-id demo1


This creates logs under:

logs/demo1/

3) Replay for Backtest Replication
python scripts/run_replay.py --session-id demo1


This produces:
results.json

If replication is correct, we will see:

{
  "pnl_match": "PASS"
}

(Optional) Strategy-Level Breakdown
python scripts/summarize_results.py


Produces:
results_detailed.json

Matching PnL and trade counts means:

No implicit randomness

No time-dependent side effects

Stable signal → execution pipeline

Why Deterministic Replication Matters

This ensures that:

A portfolio tested in research behaves identically in deployment.

Strategy performance is attributable to the logic — not execution artifacts.

Results are scientifically defensible and auditable.

Conclusion

This repository demonstrates a complete and reproducible multi-strategy trading system.
It ensures that the same inputs produce the same outputs, both in live mode and backtest replay mode — which is the core requirement for reliable quantitative research and deployment.
## Project Structure

