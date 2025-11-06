from __future__ import annotations
from typing import List
from ..event import MarketEvent, SignalEvent
from ..strategy_base import StrategyBase

# Orderbook mock: react to 'micro-events' via 1m bar proxy (large uptick/downtick -> fade back)
class AlphaOrderbookMock(StrategyBase):
    def __init__(self, name="alpha5_orderbook", lb=5, spike=0.004):
        super().__init__(name, {"1m": lb})
        self.spike = spike

    def on_bar(self, bar: MarketEvent) -> List[SignalEvent]:
        out = super().on_bar(bar)
        if bar.timeframe != '1m':
            return out
        key = f"{bar.symbol}:{bar.timeframe}"
        closes = list(self.closes[key])
        if len(closes) < 2:
            return out
        ret = (closes[-1] - closes[-2]) / closes[-2]
        if ret >= self.spike:
            out.append(SignalEvent(ts=bar.ts, symbol=bar.symbol, strategy=self.name, direction='SELL', strength=1.0))
        elif ret <= -self.spike:
            out.append(SignalEvent(ts=bar.ts, symbol=bar.symbol, strategy=self.name, direction='BUY', strength=1.0))
        return out
