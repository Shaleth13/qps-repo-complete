import argparse, os, json
from qps.replay import run_replay
from qps.evaluate import build_results_json

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--session-id', type=str, required=True)
    args = ap.parse_args()
    logs_dir = os.path.join('logs', args.session_id)

    summary = run_replay(logs_dir)
    print('Replay summary:', summary)

    results_path = os.path.join('results.json')
    build_results_json(
        live_fills=os.path.join(logs_dir, 'fills.jsonl'),
        replay_fills=os.path.join(logs_dir, 'replay_tmp', 'fills.jsonl'),
        out_path=results_path
    )
    print('Wrote', results_path)

if __name__ == '__main__':
    main()
