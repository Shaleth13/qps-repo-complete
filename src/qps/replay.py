from __future__ import annotations
import json, os
from typing import Dict
from .engine import Engine
from .strategies.alpha1_pairs import AlphaPairs
from .strategies.alpha2_breakout import AlphaBreakout
from .strategies.alpha3_mtf import AlphaMTFTrend
from .strategies.alpha4_multi_asset_momentum import AlphaMultiAssetMomentum
from .strategies.alpha5_orderbook_mock import AlphaOrderbookMock

def run_replay(logs_dir: str) -> Dict:
    symbols = ['SYM_A','SYM_B','SYM_C','SYM_D']
    strategies = [AlphaPairs(), AlphaBreakout(), AlphaMTFTrend(), AlphaMultiAssetMomentum(), AlphaOrderbookMock()]
    engine = Engine(symbols=symbols, strategies=strategies, logs_dir=os.path.join(logs_dir, 'replay_tmp'))

    # Replay market log
    with open(os.path.join(logs_dir, 'market.jsonl')) as f:
        for line in f:
            bar = json.loads(line)
            engine.on_market_bar(bar)

    # Collect metrics: per-strategy realized pnl + positions
    portfolio = engine.portfolio
    summary = {'portfolio_equity': engine.snapshot_equity(),
               'positions': {s: vars(p) for s, p in portfolio.positions.items()}}
    return summary
