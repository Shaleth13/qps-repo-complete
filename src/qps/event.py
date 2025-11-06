from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Event:
    ts: int

@dataclass
class MarketEvent(Event):
    symbol: str
    timeframe: str  # '1m' or '1h'
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class SignalEvent(Event):
    symbol: str
    strategy: str
    direction: str  # 'BUY' or 'SELL' or 'FLAT'
    strength: float = 1.0

@dataclass
class OrderEvent(Event):
    symbol: str
    strategy: str
    side: str   # 'BUY' or 'SELL'
    qty: float

@dataclass
class FillEvent(Event):
    symbol: str
    strategy: str
    side: str
    qty: float
    price: float
    fee: float = 0.0
