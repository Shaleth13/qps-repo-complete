from __future__ import annotations
from collections import deque
from typing import List
from ..event import MarketEvent, SignalEvent
from ..strategy_base import StrategyBase

# Mean-reversion on synthetic correlated pair: SYM_A vs SYM_B
class AlphaPairs(StrategyBase):
    def __init__(self, name="alpha1_pairs", lb=30, z=1.0):
        super().__init__(name, {"1m": lb})
        self.z = z
        self.spread: deque = deque(maxlen=10000)

    def on_bar(self, bar: MarketEvent) -> List[SignalEvent]:
        out = super().on_bar(bar)
        if bar.timeframe != '1m':
            return out
        # Use close of A and B; assume they exist in closes dict
        # We'll compute only when both updated in the same minute via engine price cache
        return out
