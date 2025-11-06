from __future__ import annotations
from collections import deque
from typing import Dict, Deque, List
from .event import MarketEvent, SignalEvent

class StrategyBase:
    def __init__(self, name: str, lookbacks: Dict[str, int]):
        self.name = name
        self.lookbacks = lookbacks
        self.closes: Dict[str, Deque[float]] = {}

    def on_bar(self, bar: MarketEvent) -> List[SignalEvent]:
        dq = self.closes.setdefault(f"{bar.symbol}:{bar.timeframe}", deque(maxlen=5000))
        dq.append(bar.close)
        return []
