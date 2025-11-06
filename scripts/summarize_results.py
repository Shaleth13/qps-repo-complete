import json, os
import pandas as pd

def summarize_fills(path):
    df = pd.read_json(path, lines=True)
    by_strat = (
        df.groupby("strategy")
          .agg(trades=("strategy", "size"),
               fees=("fee", "sum"))
          .sort_values("trades", ascending=False)
          .reset_index()
          .to_dict(orient="records")
    )
    return {
        "total_trades": int(len(df)),
        "total_fees": float(df["fee"].sum() if "fee" in df else 0.0),
        "by_strategy": by_strat
    }

def main(session_id="demo1"):
    logs = os.path.join("logs", session_id)
    live_fills = os.path.join(logs, "fills.jsonl")
    replay_fills = os.path.join(logs, "replay_tmp", "fills.jsonl")

    live = summarize_fills(live_fills)
    rep  = summarize_fills(replay_fills)

    results = {
        "portfolio_pnl": {
            "sandbox_trades": live["total_trades"],
            "backtest_trades": rep["total_trades"],
            "pnl_match": "PASS" if live["total_trades"] == rep["total_trades"]
                                   and abs(live["total_fees"] - rep["total_fees"]) < 1e-12 else "FAIL"
        },
        "alphas": {
            "sandbox": live["by_strategy"],
            "backtest": rep["by_strategy"]
        }
    }
    with open("results_detailed.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Wrote results_detailed.json")

if __name__ == "__main__":
    main()
