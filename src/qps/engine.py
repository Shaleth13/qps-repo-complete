from __future__ import annotations
import json, os
from typing import Dict, List
from .event import MarketEvent, SignalEvent, OrderEvent
from .broker import PaperBroker
from .portfolio import Portfolio
from .logger import JSONLLogger
from .data import MTFAggregator

class Engine:
    def __init__(self, symbols: List[str], strategies: List, logs_dir: str, cash: float = 100000.0):
        self.symbols = symbols
        self.strategies = strategies
        self.aggregator = MTFAggregator(symbols)
        self.broker = PaperBroker()
        self.portfolio = Portfolio(cash=cash)
        os.makedirs(logs_dir, exist_ok=True)
        self.mkt_log = JSONLLogger(os.path.join(logs_dir, 'market.jsonl'))
        self.sig_log = JSONLLogger(os.path.join(logs_dir, 'signals.jsonl'))
        self.ord_log = JSONLLogger(os.path.join(logs_dir, 'orders.jsonl'))
        self.fill_log = JSONLLogger(os.path.join(logs_dir, 'fills.jsonl'))
        self.price_cache: Dict[str, float] = {}

    def on_market_bar(self, bar_dict: dict):
        # write market log
        self.mkt_log.write(bar_dict)
        self.price_cache[bar_dict['symbol']] = bar_dict['close']

        # Pass through MTF aggregator (emits 1m and sometimes 1h bars)
        for agg_bar in self.aggregator.update(bar_dict):
            me = MarketEvent(**agg_bar)
            signals: List[SignalEvent] = []
            # First pass: let each strategy compute own signals
            for strat in self.strategies:
                signals.extend(strat.on_bar(me))

            # Simple cross-strategy helpers:
            # - AlphaPairs: compute pair zscore on A/B using engine prices
            if me.timeframe == '1m':
                for strat in self.strategies:
                    if strat.__class__.__name__ == 'AlphaPairs':
                        a = self.price_cache.get('SYM_A'); b = self.price_cache.get('SYM_B')
                        if a is not None and b is not None:
                            spread = a - b
                            strat.spread.append(spread)
                            if len(strat.spread) >= strat.lookbacks['1m']:
                                import statistics
                                window = list(strat.spread)[-strat.lookbacks['1m']:]
                                mu = statistics.mean(window); sd = statistics.pstdev(window) or 1e-9
                                z = (spread - mu) / sd
                                if z > strat.z:
                                    signals.append(SignalEvent(ts=me.ts, symbol='SYM_A', strategy=strat.name, direction='SELL'))
                                    signals.append(SignalEvent(ts=me.ts, symbol='SYM_B', strategy=strat.name, direction='BUY'))
                                elif z < -strat.z:
                                    signals.append(SignalEvent(ts=me.ts, symbol='SYM_A', strategy=strat.name, direction='BUY'))
                                    signals.append(SignalEvent(ts=me.ts, symbol='SYM_B', strategy=strat.name, direction='SELL'))

                    if strat.__class__.__name__ == 'AlphaMultiAssetMomentum':
                        # rank SMA vs universe
                        key = f"{me.symbol}:{me.timeframe}"
                        closes = strat.closes.get(key, [])
                        if len(closes) >= strat.lookbacks['1m']:
                            sma = sum(list(closes)[-strat.lookbacks['1m']:]) / strat.lookbacks['1m']
                            snapshot = {s: self.price_cache.get(s) for s in self.symbols if self.price_cache.get(s) is not None}
                            if len(snapshot) == len(self.symbols):
                                import statistics
                                median = statistics.median(snapshot.values())
                                if sma > median:
                                    signals.append(SignalEvent(ts=me.ts, symbol=me.symbol, strategy=strat.name, direction='BUY'))
                                elif sma < median:
                                    signals.append(SignalEvent(ts=me.ts, symbol=me.symbol, strategy=strat.name, direction='SELL'))

            # Turn signals into naive orders: fixed qty per signal, ignore duplicates within same ts/symbol/strategy
            emitted = set()
            for sig in signals:
                key = (sig.ts, sig.symbol, sig.strategy, sig.direction)
                if key in emitted:
                    continue
                emitted.add(key)
                self.sig_log.write({'ts': sig.ts, 'symbol': sig.symbol, 'strategy': sig.strategy, 'direction': sig.direction, 'strength': sig.strength})
                side = 'BUY' if sig.direction == 'BUY' else 'SELL'
                qty = 1.0  # fixed size
                order = OrderEvent(ts=sig.ts, symbol=sig.symbol, strategy=sig.strategy, side=side, qty=qty)
                self.ord_log.write({'ts': order.ts, 'symbol': order.symbol, 'strategy': order.strategy, 'side': order.side, 'qty': order.qty})
                # Execute immediately at close
                price = self.price_cache[order.symbol]
                fill = self.broker.execute(ts=order.ts, price=price, order=order)
                self.portfolio.on_fill(fill)
                self.fill_log.write({'ts': fill.ts, 'symbol': fill.symbol, 'strategy': fill.strategy,
                                     'side': fill.side, 'qty': fill.qty, 'price': fill.price, 'fee': fill.fee})

    def snapshot_equity(self):
        return self.portfolio.total_equity(self.price_cache)
