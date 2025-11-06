from __future__ import annotations
from typing import List
from ..event import MarketEvent, SignalEvent
from ..strategy_base import StrategyBase

# Multi-timeframe trend: 1h filter, 1m trigger (buy if 1h > SMA, sell if below)
class AlphaMTFTrend(StrategyBase):
    def __init__(self, name="alpha3_mtf", lb_1m=20, lb_1h=10):
        super().__init__(name, {"1m": lb_1m, "1h": lb_1h})

    def on_bar(self, bar: MarketEvent) -> List[SignalEvent]:
        out = super().on_bar(bar)
        key_1h = f"{bar.symbol}:1h"
        key_1m = f"{bar.symbol}:1m"
        # need both TF history
        if bar.timeframe == '1m':
            closes_1m = list(self.closes.get(key_1m, []))
            closes_1h = list(self.closes.get(key_1h, []))
            if len(closes_1m) >= self.lookbacks['1m'] and len(closes_1h) >= self.lookbacks['1h']:
                sma_1h = sum(closes_1h[-self.lookbacks['1h']:]) / self.lookbacks['1h']
                sma_1m = sum(closes_1m[-self.lookbacks['1m']:]) / self.lookbacks['1m']
                if sma_1h > closes_1h[-1] and closes_1m[-1] < sma_1m:
                    out.append(SignalEvent(ts=bar.ts, symbol=bar.symbol, strategy=self.name, direction='SELL', strength=1.0))
                elif sma_1h < closes_1h[-1] and closes_1m[-1] > sma_1m:
                    out.append(SignalEvent(ts=bar.ts, symbol=bar.symbol, strategy=self.name, direction='BUY', strength=1.0))
        return out
