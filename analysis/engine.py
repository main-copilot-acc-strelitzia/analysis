"""Continuous analysis engine that runs always-on and pushes updates via callback.

This module intentionally keeps synchronous MT5 calls off the main thread
by using a Thread + asyncio event loop and run_in_executor for IO.
"""
from __future__ import annotations

import os
import sys
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Callable, Optional

# Ensure the project root (the `trader` folder) is on sys.path so imports resolve when running directly
THIS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(THIS_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd

from mt5.market_data import MarketDataManager
from analysis.forex.analyzer import ForexAnalyzer
from core.logger import get_logger


class AnalysisEngine:
    """Always-on analysis engine.

    Usage:
      engine = AnalysisEngine()
      engine.start(symbol, timeframe, history_days=7, poll_interval=30, update_cb=callable)
      engine.stop()
    """

    def __init__(self):
        self.logger = get_logger()
        self._md = MarketDataManager()
        self._analyzer: Optional[ForexAnalyzer] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._last_hist_end = None
        self._full_refresh_minutes = 60
        self._last_full_refresh = None

    def start(self, symbol: str, timeframe: str, history_days: int = 7, poll_interval: int = 30, update_cb: Optional[Callable] = None):
        if self._thread and self._thread.is_alive():
            self.logger.info("Analysis engine already running")
            return

        self._stop_event.clear()
        self._analyzer = ForexAnalyzer(symbol, timeframe)

        def _run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            try:
                self._loop.run_until_complete(self._main_loop(symbol, timeframe, history_days, poll_interval, update_cb))
            except RuntimeError as e:
                # If the loop is stopped from another thread (engine.stop), run_until_complete
                # can raise 'Event loop stopped before Future completed.' — treat as normal shutdown.
                if 'Event loop stopped' in str(e):
                    self.logger.info('Analysis engine event loop stopped, exiting thread')
                else:
                    self.logger.exception('Runtime error in analysis engine loop')
            finally:
                try:
                    self._loop.close()
                except Exception:
                    pass

        self._thread = threading.Thread(target=_run_loop, daemon=True)
        self._thread.start()
        self.logger.info(f"Started analysis engine for {symbol} {timeframe}")

    def stop(self):
        self._stop_event.set()
        if self._loop and self._loop.is_running():
            # stop the loop safely
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=5)
        self.logger.info("Stopped analysis engine")

    async def _main_loop(self, symbol: str, timeframe: str, history_days: int, poll_interval: int, update_cb: Optional[Callable]):
        # Run until stop event
        while not self._stop_event.is_set():
            try:
                # Fetch historical candles covering history_days + a buffer
                now = datetime.utcnow()
                start_dt = now - timedelta(days=history_days)

                # Determine approx candle count per day based on timeframe
                tf_map = {
                    'M1': 1440,
                    'M5': 288,
                    'M15': 96,
                    'M30': 48,
                    'H1': 24,
                    'H4': 6,
                    'D1': 1,
                }
                per_day = tf_map.get(timeframe, 24)
                count = int(max(500, min(10000, int(per_day * history_days * 1.1))))

                # Synchronous MT5 calls are executed in threadpool
                loop = asyncio.get_running_loop()

                # Use cached historical data where possible to avoid full refreshes every loop
                cached = self._md.get_cached_data(symbol, timeframe)
                need_full = False
                if cached is None or len(cached) == 0:
                    need_full = True
                elif self._last_full_refresh is None or (datetime.utcnow() - self._last_full_refresh).total_seconds() > self._full_refresh_minutes * 60:
                    need_full = True

                if need_full:
                    hist_df = await loop.run_in_executor(None, lambda: self._md.get_candles(symbol, timeframe, count))
                    self._last_full_refresh = datetime.utcnow()
                else:
                    # Only fetch most recent candles to update the cache / current slice
                    recent_count = max(100, int(min(500, count * 0.05)))
                    recent = await loop.run_in_executor(None, lambda: self._md.get_candles(symbol, timeframe, recent_count))
                    # Merge recent with cache
                    if cached is not None:
                        df_combined = pd.concat([cached, recent]).drop_duplicates(subset=['Timestamp']).sort_values('Timestamp').reset_index(drop=True)
                        hist_df = df_combined
                        # update cache
                        try:
                            if symbol not in self._md._data_cache:
                                self._md._data_cache[symbol] = {}
                            self._md._data_cache[symbol][timeframe] = MarketDataManager.CacheEntry(df_combined, timeframe)
                        except Exception:
                            # fallback if CacheEntry not accessible
                            self._md._data_cache[symbol][timeframe] = df_combined
                    else:
                        hist_df = recent

                cur_df = None
                if hist_df is not None and len(hist_df) > 0:
                    # Ensure we provide latest candles as 'current' slice
                    cur_df = hist_df.tail(200).copy()

                # Run analysis (preserve current-first behavior)
                analyze_input = {'current': cur_df, 'historical': hist_df}
                result = await loop.run_in_executor(None, lambda: self._analyzer.analyze(analyze_input))

                # Attach raw candles (serialized) to result for UI plotting, but do not modify core analyzer logic
                try:
                    if hist_df is not None and len(hist_df) > 0:
                        # include last N candles for visualization (keep modest size)
                        raw = hist_df.tail(200).copy()
                        raw['Timestamp'] = raw['Timestamp'].astype(str)
                        result['raw_candles'] = raw.to_dict(orient='records')
                    elif cur_df is not None and len(cur_df) > 0:
                        raw = cur_df.copy()
                        raw['Timestamp'] = raw['Timestamp'].astype(str)
                        result['raw_candles'] = raw.to_dict(orient='records')
                except Exception:
                    self.logger.exception('Failed to attach raw_candles to analysis result')

                # Callback with results (non-blocking)
                if update_cb:
                    try:
                        update_cb(result)
                    except Exception:
                        self.logger.exception("Update callback failed")

                # If no valid trade, sleep poll_interval and continue. The analyzer result contains rating/confluence.
                # If result indicates forming setup, it may include an estimated validation time in 'analysis'.
                await asyncio.sleep(poll_interval)

            except Exception:
                self.logger.exception("Error in analysis engine main loop, will continue after short delay")
                await asyncio.sleep(max(5, poll_interval))
