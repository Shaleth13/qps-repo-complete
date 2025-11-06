from __future__ import annotations
from typing import Dict
from .event import OrderEvent, FillEvent

class PaperBroker:
    """Deterministic, zero-slippage, fixed-fee paper broker."""
    def __init__(self, fee_perc: float = 0.0005):
        self.fee_perc = fee_perc

    def execute(self, ts: int, price: float, order: OrderEvent) -> FillEvent:
        fee = abs(order.qty) * price * self.fee_perc
        return FillEvent(ts=ts, symbol=order.symbol, strategy=order.strategy,
                         side=order.side, qty=order.qty, price=price, fee=fee)
