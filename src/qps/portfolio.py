from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from .event import FillEvent

@dataclass
class Position:
    qty: float = 0.0
    avg_price: float = 0.0
    realized_pnl: float = 0.0

class Portfolio:
    def __init__(self, cash: float = 100000.0):
        self.cash = cash
        self.positions: Dict[str, Position] = {}

    def on_fill(self, fill: FillEvent):
        pos = self.positions.setdefault(fill.symbol, Position())
        signed_qty = fill.qty if fill.side == 'BUY' else -fill.qty
        cost = fill.price * signed_qty + (fill.fee if signed_qty>0 else -fill.fee)
        # Realized P&L if reducing/closing
        if pos.qty != 0 and (pos.qty > 0) != (signed_qty > 0):
            closing_qty = min(abs(pos.qty), abs(signed_qty)) * (1 if pos.qty>0 else -1)
            pnl = closing_qty * (pos.avg_price - fill.price) * (-1 if pos.qty>0 else 1)
            pos.realized_pnl += pnl
        new_qty = pos.qty + signed_qty
        if new_qty == 0:
            pos.avg_price = 0.0
        else:
            if (pos.qty == 0) or ((pos.qty > 0) == (signed_qty > 0)):
                pos.avg_price = (pos.avg_price * abs(pos.qty) + fill.price * abs(signed_qty)) / abs(new_qty)
        pos.qty = new_qty
        self.cash -= cost

    def total_unrealized(self, prices: Dict[str, float]) -> float:
        upnl = 0.0
        for sym, pos in self.positions.items():
            if pos.qty != 0 and sym in prices:
                upnl += pos.qty * (prices[sym] - pos.avg_price)
        return upnl

    def total_equity(self, prices: Dict[str, float]) -> float:
        return self.cash + self.total_unrealized(prices) + sum(p.realized_pnl for p in self.positions.values())
