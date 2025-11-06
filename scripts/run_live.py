import argparse, os, json
from qps.engine import Engine
from qps.data import BarFeed

from qps.strategies.alpha1_pairs import AlphaPairs
from qps.strategies.alpha2_breakout import AlphaBreakout
from qps.strategies.alpha3_mtf import AlphaMTFTrend
from qps.strategies.alpha4_multi_asset_momentum import AlphaMultiAssetMomentum
from qps.strategies.alpha5_orderbook_mock import AlphaOrderbookMock

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--session-id', type=str, required=True)
    ap.add_argument('--data-dir', type=str, default='data')
    args = ap.parse_args()

    logs_dir = os.path.join('logs', args.session_id)
    symbols = ['SYM_A','SYM_B','SYM_C','SYM_D']
    feeds = [
        BarFeed('SYM_A', os.path.join(args.data_dir, 'synth_SYM_A_1m.csv')),
        BarFeed('SYM_B', os.path.join(args.data_dir, 'synth_SYM_B_1m.csv')),
        BarFeed('SYM_C', os.path.join(args.data_dir, 'synth_SYM_C_1m.csv')),
        BarFeed('SYM_D', os.path.join(args.data_dir, 'synth_SYM_D_1m.csv')),
    ]

    strategies = [AlphaPairs(), AlphaBreakout(), AlphaMTFTrend(), AlphaMultiAssetMomentum(), AlphaOrderbookMock()]
    engine = Engine(symbols=symbols, strategies=strategies, logs_dir=logs_dir)

    # merge feeds by time in lockstep (since same timestamps from generator)
    iters = [iter(f) for f in feeds]
    for rows in zip(*iters):
        for bar in rows:
            engine.on_market_bar(bar)

    print('Live(sim) complete. Logs at', logs_dir)

if __name__ == '__main__':
    main()
