"""Volatility indices analysis."""

import numpy as np
import pandas as pd
from analysis.shared.indicators import TechnicalIndicators


class VolatilityIndicesAnalysis:
    """Analyzes volatility indices (VOLATILITY10, VOLATILITY25, etc)."""

    @staticmethod
    def volatility_mean_reversion(data: pd.DataFrame) -> float:
        """
        Detect mean reversion in volatility index.
        
        Returns signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        mean = np.mean(closes)
        current = closes[-1]

        deviation = (current - mean) / mean * 100

        if deviation > 20:
            return 25.0  # High vol, expect reversion down
        elif deviation < -20:
            return 75.0  # Low vol, expect reversion up
        else:
            return 50.0

    @staticmethod
    def volatility_regime_detection(data: pd.DataFrame) -> str:
        """
        Identify volatility regime.
        
        Returns regime: 'High', 'Normal', 'Low'
        """
        if len(data) < 30:
            return 'Normal'

        closes = data['Close'].values
        recent_vol = np.std(closes[-10:])
        historical_vol = np.std(closes[-30:])

        if recent_vol > historical_vol * 1.3:
            return 'High'
        elif recent_vol < historical_vol * 0.7:
            return 'Low'
        else:
            return 'Normal'

    @staticmethod
    def volatility_expansion_contraction(data: pd.DataFrame) -> float:
        """
        Analyze volatility expansion/contraction cycles.
        
        Returns signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        ranges = np.abs(np.diff(closes))

        recent_range = np.mean(ranges[-5:])
        prior_range = np.mean(ranges[-15:-5])

        if prior_range == 0:
            return 50.0

        if recent_range > prior_range * 1.5:
            return 75.0  # Expanding
        elif recent_range < prior_range * 0.7:
            return 25.0  # Contracting
        else:
            return 50.0

    @staticmethod
    def vix_style_spikes(data: pd.DataFrame) -> float:
        """
        Identify VIX-style spike patterns.
        
        Returns spike signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        avg = np.mean(closes)

        if closes[-1] > avg * 1.5:
            return 85.0  # Spike up
        elif closes[-1] < avg * 0.5:
            return 15.0  # Spike down
        else:
            return 50.0

    @staticmethod
    def volatility_oscillator(data: pd.DataFrame) -> float:
        """
        Calculate volatility oscillator.
        
        Returns oscillator value 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        ema5 = TechnicalIndicators.ema(closes, 5)
        ema20 = TechnicalIndicators.ema(closes, 20)

        if ema5[-1] > ema20[-1]:
            return 75.0
        else:
            return 25.0

    @staticmethod
    def fear_index_reading(data: pd.DataFrame) -> float:
        """
        Read fear index level.
        
        Returns fear reading 0-100 (high = high fear).
        """
        if len(data) < 1:
            return 50.0

        # Normalize closing price to 0-100 scale as fear indicator
        closes = data['Close'].values
        min_close = np.min(closes[-30:]) if len(closes) >= 30 else np.min(closes)
        max_close = np.max(closes[-30:]) if len(closes) >= 30 else np.max(closes)

        if max_close == min_close:
            return 50.0

        normalized = (closes[-1] - min_close) / (max_close - min_close) * 100
        return 100.0 - normalized  # Invert: higher price = lower fear

    @staticmethod
    def volatility_rate_of_change(data: pd.DataFrame) -> float:
        """
        Calculate rate of change in volatility.
        
        Returns ROC signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        vol_recent = np.std(closes[-10:])
        vol_prior = np.std(closes[-20:-10])

        if vol_prior == 0:
            return 50.0

        roc = (vol_recent - vol_prior) / vol_prior * 100

        if roc > 30:
            return 80.0
        elif roc < -30:
            return 20.0
        else:
            return 50.0 + (roc / 60 * 50)

    @staticmethod
    def calm_before_storm(data: pd.DataFrame) -> float:
        """
        Detect calm before storm pattern (low vol before spike).
        
        Returns pattern signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        ranges = np.abs(np.diff(closes))

        recent_vol = np.mean(ranges[-3:])
        prior_vol = np.mean(ranges[-10:-3])

        if recent_vol < prior_vol * 0.5 and prior_vol > np.mean(ranges[-20:]):
            return 80.0  # Calm detected
        else:
            return 50.0
