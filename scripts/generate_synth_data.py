import argparse
import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

def gen_symbol(seed, start, periods, mu=0.0, sigma=0.002, start_price=100.0):
    rng = np.random.default_rng(seed)
    prices = [start_price]
    for _ in range(periods-1):
        ret = rng.normal(mu, sigma)
        prices.append(prices[-1]*(1+ret))
    prices = np.array(prices)
    # OHLC from close with small jitter
    df = pd.DataFrame({'close': prices})
    df['open'] = df['close'].shift(1).fillna(df['close'])
    df['high'] = df[['open','close']].max(axis=1)*(1+abs(rng.normal(0, 0.0008, size=periods)))
    df['low']  = df[['open','close']].min(axis=1)*(1-abs(rng.normal(0, 0.0008, size=periods)))
    df['volume'] = rng.integers(50, 150, size=periods)
    df = df[['open','high','low','close','volume']]
    # timestamps at 1-minute intervals (ns)
    ts = np.array([(start + timedelta(minutes=i)).timestamp()*1_000_000_000 for i in range(periods)], dtype=np.int64)
    df.insert(0, 'ts', ts)
    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=int, default=3)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--outdir', type=str, default='data')
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    periods = args.days*24*60
    start = datetime(2025, 1, 1, 9, 15)  # arbitrary fixed start

    # correlated A/B; independent C/D
    dfA = gen_symbol(args.seed, start, periods, mu=0.00005, sigma=0.0020, start_price=100.0)
    dfB = gen_symbol(args.seed+1, start, periods, mu=0.00003, sigma=0.0020, start_price=100.5)
    dfC = gen_symbol(args.seed+2, start, periods, mu=0.00002, sigma=0.0025, start_price=50.0)
    dfD = gen_symbol(args.seed+3, start, periods, mu=0.00004, sigma=0.0022, start_price=200.0)

    dfA.to_csv(os.path.join(args.outdir, 'synth_SYM_A_1m.csv'), index=False)
    dfB.to_csv(os.path.join(args.outdir, 'synth_SYM_B_1m.csv'), index=False)
    dfC.to_csv(os.path.join(args.outdir, 'synth_SYM_C_1m.csv'), index=False)
    dfD.to_csv(os.path.join(args.outdir, 'synth_SYM_D_1m.csv'), index=False)
    print('Wrote synthetic CSVs to', args.outdir)

if __name__ == '__main__':
    main()
