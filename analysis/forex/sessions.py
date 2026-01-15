"""Session-based analysis for Forex."""

import numpy as np
import pandas as pd
from datetime import datetime, time
from typing import Dict, Any


class SessionAnalysis:
    """Analyzes Forex by trading sessions."""

    @staticmethod
    def london_session_analysis(data: pd.DataFrame) -> float:
        """
        Analyze price behavior during London session (8:00-16:30 GMT).
        
        Returns London session signal 0-100.
        """
        if len(data) < 5:
            return 50.0

        closes = data['Close'].values[-5:]

        # Typical London session behavior: strong volatility
        london_range = np.max(closes) - np.min(closes)
        avg_range = np.mean([np.max(data['Close'].values[max(0, i-5):i+1]) - 
                            np.min(data['Close'].values[max(0, i-5):i+1]) 
                            for i in range(5, len(data), 5)])

        if avg_range == 0:
            return 50.0

        if london_range > avg_range * 1.3:
            return 75.0
        elif london_range < avg_range * 0.7:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def tokyo_session_analysis(data: pd.DataFrame) -> float:
        """
        Analyze price behavior during Tokyo session (21:00-06:00 GMT).
        
        Returns Tokyo session signal 0-100.
        """
        if len(data) < 5:
            return 50.0

        closes = data['Close'].values[-5:]

        # Tokyo typically lower volatility
        tokyo_range = np.max(closes) - np.min(closes)

        if tokyo_range > np.mean(closes[-1]) * 0.02:
            return 75.0
        else:
            return 25.0

    @staticmethod
    def new_york_session_analysis(data: pd.DataFrame) -> float:
        """
        Analyze price behavior during New York session (13:00-22:00 GMT).
        
        Returns New York session signal 0-100.
        """
        if len(data) < 5:
            return 50.0

        closes = data['Close'].values[-5:]

        # NY session typically strong, especially first hour
        ny_range = np.max(closes) - np.min(closes)

        if ny_range > np.mean(closes[-1]) * 0.025:
            return 80.0
        else:
            return 40.0

    @staticmethod
    def sydney_session_analysis(data: pd.DataFrame) -> float:
        """
        Analyze price behavior during Sydney session (21:00-06:00 GMT).
        
        Returns Sydney session signal 0-100.
        """
        if len(data) < 5:
            return 50.0

        closes = data['Close'].values[-5:]
        opens = data['Open'].values[-5:]

        # Sydney session typically opens with some volatility
        movement = np.abs(closes - opens)
        avg_movement = np.mean(movement)

        if avg_movement > np.mean(closes[-1]) * 0.015:
            return 65.0
        else:
            return 45.0

    @staticmethod
    def overlap_analysis(data: pd.DataFrame) -> float:
        """
        Analyze overlap sessions (highest volatility periods).
        
        Returns overlap signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        highs = data['High'].values[-10:]
        lows = data['Low'].values[-10:]

        ranges = highs - lows
        avg_range = np.mean(ranges)

        if ranges[-1] > avg_range * 1.5:
            return 80.0
        else:
            return 40.0

    @staticmethod
    def session_open_analysis(data: pd.DataFrame) -> float:
        """
        Analyze price movement at session opens.
        
        Returns open signal 0-100.
        """
        if len(data) < 5:
            return 50.0

        # Take the last N opens/closes and coerce to numpy arrays
        opens = np.asarray(data['Open'].values[-5:], dtype=float)
        closes = np.asarray(data['Close'].values[-5:], dtype=float)

        # Need at least two close values to compare previous close
        if closes.size < 2 or opens.size == 0:
            return 50.0

        # Align lengths if there's any mismatch (defensive)
        if opens.size != closes.size:
            min_len = min(opens.size, closes.size)
            opens = opens[-min_len:]
            closes = closes[-min_len:]

        # Build previous-close series aligned to opens: first previous is NaN
        prev_closes = np.concatenate(([np.nan], closes[:-1]))
        prev_closes = prev_closes[-opens.size:]

        # Compute absolute gaps and ignore NaNs
        gaps = np.abs(opens - prev_closes)
        valid_gaps = gaps[~np.isnan(gaps)]
        avg_gap = float(np.mean(valid_gaps)) if valid_gaps.size > 0 else 0.0

        # Current gap compares latest open to the previous close (if available)
        current_gap = float(abs(opens[-1] - closes[-2])) if closes.size > 1 else 0.0

        if avg_gap == 0.0:
            return 50.0

        return 70.0 if current_gap > avg_gap * 1.3 else 50.0

    @staticmethod
    def session_volatility_pattern(data: pd.DataFrame) -> float:
        """
        Identify session volatility patterns.
        
        Returns pattern signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        returns = np.abs(np.diff(closes) / closes[:-1])

        recent_vol = np.mean(returns[-5:])
        prior_vol = np.mean(returns[-10:-5])

        if prior_vol == 0:
            return 50.0

        if recent_vol > prior_vol * 1.3:
            return 75.0
        elif recent_vol < prior_vol * 0.7:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def tag_sessions(df: pd.DataFrame) -> pd.DataFrame:
        """
        Tag each candle with a trading session name and session start timestamp.

        Adds two columns: 'Session' and 'SessionStart'. Does not modify input in-place.
        Session windows are defined in GMT and are intentionally coarse to match MT5
        session boundaries used by the rest of the system.
        """
        if df is None or 'Timestamp' not in df.columns:
            return df

        df = df.copy()
        # Ensure Timestamp is timezone-naive UTC datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        def session_name(ts: pd.Timestamp) -> str:
            h = ts.hour
            m = ts.minute
            # Tokyo: 21:00 - 06:00 GMT
            if (h >= 21) or (h < 6):
                return 'Tokyo'
            # London: 08:00 - 16:30 GMT
            if (h >= 8 and (h < 16 or (h == 16 and m <= 30))):
                return 'London'
            # New York: 13:00 - 22:00 GMT
            if (h >= 13 and h < 22):
                return 'NewYork'
            # Sydney: fallback for quieter periods
            return 'Sydney'

        df['Session'] = df['Timestamp'].apply(session_name)

        # Compute session start: combine date and session start hour for grouping
        def session_start(ts: pd.Timestamp) -> pd.Timestamp:
            s = session_name(ts)
            if s == 'Tokyo':
                # session starts at 21:00 previous day when ts.hour < 6
                if ts.hour < 6:
                    start_date = (ts - pd.Timedelta(days=0)).normalize()
                else:
                    start_date = ts.normalize()
                return pd.Timestamp(start_date) + pd.Timedelta(hours=21)
            if s == 'London':
                return pd.Timestamp(ts.normalize()) + pd.Timedelta(hours=8)
            if s == 'NewYork':
                return pd.Timestamp(ts.normalize()) + pd.Timedelta(hours=13)
            return pd.Timestamp(ts.normalize()) + pd.Timedelta(hours=22)

        df['SessionStart'] = df['Timestamp'].apply(session_start)
        return df

    @staticmethod
    def compute_session_aggregates(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Compute high/low/open/close and volume aggregates per session across the DataFrame.

        Returns a dict: { session_name: { session_start: {open, high, low, close, volume} , ... } }
        """
        out: Dict[str, Dict[str, Any]] = {}
        if df is None or len(df) == 0:
            return out

        tagged = df if 'Session' in df.columns and 'SessionStart' in df.columns else SessionAnalysis.tag_sessions(df)

        groups = tagged.groupby(['Session', 'SessionStart'])
        for (sess, start), g in groups:
            if sess not in out:
                out[sess] = {}
            out[sess][pd.Timestamp(start)] = {
                'open': float(g['Open'].iloc[0]),
                'high': float(g['High'].max()),
                'low': float(g['Low'].min()),
                'close': float(g['Close'].iloc[-1]),
                'volume': float(g['Volume'].sum()),
                'count': int(len(g)),
            }
        return out

    @staticmethod
    def session_context(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Produce a concise session-aware context summary used to augment confidence scoring.

        Returns keys: 'last_session', 'session_aggregates', 'recent_session_changes'
        """
        ctx: Dict[str, Any] = {
            'last_session': None,
            'session_aggregates': {},
            'recent_session_changes': {}
        }
        if df is None or len(df) == 0:
            return ctx

        tagged = df if 'Session' in df.columns and 'SessionStart' in df.columns else SessionAnalysis.tag_sessions(df)
        last_row = tagged.iloc[-1]
        ctx['last_session'] = {
            'name': last_row['Session'],
            'start': pd.Timestamp(last_row['SessionStart'])
        }

        ctx['session_aggregates'] = SessionAnalysis.compute_session_aggregates(tagged)

        # Recent session changes: compare last two sessions of same type
        sess = last_row['Session']
        sess_aggs = ctx['session_aggregates'].get(sess, {})
        if len(sess_aggs) >= 2:
            starts = sorted(sess_aggs.keys())
            last = sess_aggs[starts[-1]]
            prev = sess_aggs[starts[-2]]
            ctx['recent_session_changes'] = {
                'high_change': last['high'] - prev['high'],
                'low_change': last['low'] - prev['low'],
                'volume_change': last['volume'] - prev['volume']
            }

        return ctx
