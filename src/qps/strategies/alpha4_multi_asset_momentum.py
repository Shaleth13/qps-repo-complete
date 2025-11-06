from __future__ import annotations
from typing import List
from ..event import MarketEvent, SignalEvent
from ..strategy_base import StrategyBase

# Multi-asset momentum: rank symbol's 1m SMA vs universe median; go with trend.
class AlphaMultiAssetMomentum(StrategyBase):
    def __init__(self, name="alpha4_multi_asset", lb=30):
        super().__init__(name, {"1m": lb})
        self.last_universe_snapshot = {}

    def on_bar(self, bar: MarketEvent) -> List[SignalEvent]:
        out = super().on_bar(bar)
        if bar.timeframe != '1m':
            return out
        # Decision delegated to engine with universe snapshot/prices to keep this simple.
        return out
