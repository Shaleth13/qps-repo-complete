from __future__ import annotations
from typing import List
from ..event import MarketEvent, SignalEvent
from ..strategy_base import StrategyBase

# Breakout on 1m
class AlphaBreakout(StrategyBase):
    def __init__(self, name="alpha2_breakout", lb=40):
        super().__init__(name, {"1m": lb})

    def on_bar(self, bar: MarketEvent) -> List[SignalEvent]:
        out = super().on_bar(bar)
        if bar.timeframe != '1m':
            return out
        key = f"{bar.symbol}:{bar.timeframe}"
        closes = list(self.closes[key])
        if len(closes) < self.lookbacks['1m']:
            return out
        hi = max(closes[-self.lookbacks['1m']:])
        lo = min(closes[-self.lookbacks['1m']:])
        if bar.close >= hi:
            out.append(SignalEvent(ts=bar.ts, symbol=bar.symbol, strategy=self.name, direction='BUY', strength=1.0))
        elif bar.close <= lo:
            out.append(SignalEvent(ts=bar.ts, symbol=bar.symbol, strategy=self.name, direction='SELL', strength=1.0))
        return out
