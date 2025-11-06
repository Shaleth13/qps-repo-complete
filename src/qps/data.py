from __future__ import annotations
import pandas as pd
from typing import Iterable, Dict, List

class BarFeed:
    """Simple 1-minute bar feed from CSV with columns:
    ts (ns), open, high, low, close, volume
    """
    def __init__(self, symbol: str, csv_path: str):
        self.symbol = symbol
        self.df = pd.read_csv(csv_path)
        self.i = 0

    def __iter__(self):
        for _, row in self.df.iterrows():
            yield {
                'ts': int(row['ts']),
                'symbol': self.symbol,
                'timeframe': '1m',
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume'])
            }

class MTFAggregator:
    """Aggregate 1m bars into 1h bars on the fly per symbol."""
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self.buffers: Dict[str, list] = {s: [] for s in symbols}
        self.current_hour: Dict[str, int] = {s: None for s in symbols}

    def update(self, bar: dict) -> Iterable[dict]:
        s = bar['symbol']
        hour_bucket = bar['ts'] // (3600 * 10**9)
        out = [bar]  # always emit 1m bar

        if self.current_hour[s] is None:
            self.current_hour[s] = hour_bucket

        self.buffers[s].append(bar)
        if hour_bucket != self.current_hour[s]:
            # flush prev hour
            buf = self.buffers[s][:-1]
            if buf:
                opens = buf[0]['open']; highs = max(b['high'] for b in buf)
                lows = min(b['low'] for b in buf); closes = buf[-1]['close']
                vol = sum(b['volume'] for b in buf)
                out.append({
                    'ts': buf[-1]['ts'], 'symbol': s, 'timeframe': '1h',
                    'open': opens, 'high': highs, 'low': lows, 'close': closes, 'volume': vol
                })
            self.buffers[s] = [bar]
            self.current_hour[s] = hour_bucket
        return out
