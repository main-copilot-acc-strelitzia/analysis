"""Run the analysis engine headless for testing or CLI operation.

Usage:
    python run_engine.py --symbol EURUSD --timeframe M15
"""
import argparse
import os
import sys

THIS_DIR = os.path.dirname(__file__)
if THIS_DIR not in sys.path:
    sys.path.insert(0, THIS_DIR)

from analysis.engine import AnalysisEngine

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--symbol', required=True)
    p.add_argument('--timeframe', required=True)
    p.add_argument('--history', type=int, default=7)
    p.add_argument('--poll', type=int, default=30)

    args = p.parse_args()

    engine = AnalysisEngine()

    def cb(result):
        print('Analysis update:', result.get('confluence_score'), result.get('setup_status'))

    engine.start(args.symbol, args.timeframe, history_days=args.history, poll_interval=args.poll, update_cb=cb)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        engine.stop()
        print('Stopped')
