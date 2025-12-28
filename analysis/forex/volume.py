"""Volume analysis for Forex."""

import numpy as np
import pandas as pd
from analysis.shared.indicators import TechnicalIndicators


class VolumeAnalysis:
    """Analyzes Forex volume."""

    @staticmethod
    def volume_trend(data: pd.DataFrame, period: int = 20) -> float:
        """
        Analyze volume trend.
        
        Returns volume trend signal 0-100.
        """
        if len(data) < period:
            return 50.0

        volumes = data['Volume'].values

        recent_avg = np.mean(volumes[-10:])
        prior_avg = np.mean(volumes[-20:-10])

        if prior_avg == 0:
            return 50.0

        ratio = recent_avg / prior_avg
        if ratio > 1.2:
            return 75.0
        elif ratio < 0.8:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def volume_profile_analysis(data: pd.DataFrame) -> float:
        """
        Analyze volume profile distribution.
        
        Returns profile signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values[-20:]
        volumes = data['Volume'].values[-20:]

        # High volume at higher prices = bullish
        high_prices = closes > np.mean(closes)
        high_price_volume = np.sum(volumes[high_prices])
        total_volume = np.sum(volumes)

        if total_volume == 0:
            return 50.0

        bullish_ratio = high_price_volume / total_volume
        return bullish_ratio * 100

    @staticmethod
    def accumulation_distribution(data: pd.DataFrame) -> float:
        """
        Analyze accumulation/distribution.
        
        Returns A/D signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values
        volumes = data['Volume'].values

        # CLV = (Close - Low) - (High - Close) / (High - Low)
        ad_values = np.zeros_like(closes)
        for i in range(len(closes)):
            range_hl = highs[i] - lows[i]
            if range_hl != 0:
                clv = ((closes[i] - lows[i]) - (highs[i] - closes[i])) / range_hl
                ad_values[i] = clv * volumes[i]

        recent_ad = np.sum(ad_values[-10:])
        prior_ad = np.sum(ad_values[-20:-10])

        if recent_ad > prior_ad:
            return 75.0
        elif recent_ad < prior_ad:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def on_balance_volume_signal(data: pd.DataFrame) -> float:
        """
        Generate signal from OBV.
        
        Returns OBV signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        volumes = data['Volume'].values

        obv = TechnicalIndicators.obv(closes, volumes)

        # Trend OBV
        obv_ma = TechnicalIndicators.ema(obv, 10)

        if obv[-1] > obv_ma[-1]:
            return 75.0
        elif obv[-1] < obv_ma[-1]:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def volume_strength(data: pd.DataFrame) -> float:
        """
        Calculate overall volume strength.
        
        Returns strength 0-100.
        """
        if len(data) < 10:
            return 50.0

        volumes = data['Volume'].values[-10:]
        avg_volume = np.mean(volumes)

        if avg_volume == 0:
            return 50.0

        current_strength = volumes[-1] / avg_volume
        signal = min(current_strength * 50, 100.0)
        return signal

    @staticmethod
    def volume_price_trend(data: pd.DataFrame) -> float:
        """
        Analyze volume-price trend relationship.
        
        Returns VPT signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        volumes = data['Volume'].values

        # VPT considers both price and volume changes
        price_changes = np.diff(closes) / closes[:-1]
        vpt = np.cumsum(price_changes * volumes[1:])

        if len(vpt) > 10:
            if vpt[-1] > vpt[-10]:
                return 75.0
            elif vpt[-1] < vpt[-10]:
                return 25.0

        return 50.0

    @staticmethod
    def volume_density(data: pd.DataFrame, price_levels: int = 10) -> float:
        """
        Analyze volume density at price levels.
        
        Returns density signal 0-100.
        """
        if len(data) < price_levels:
            return 50.0

        closes = data['Close'].values[-price_levels:]
        volumes = data['Volume'].values[-price_levels:]

        # Highest volume at highest price = accumulation
        max_vol_idx = np.argmax(volumes)
        max_price_idx = np.argmax(closes)

        if max_vol_idx == max_price_idx:
            return 75.0
        elif max_vol_idx == np.argmin(closes):
            return 25.0
        else:
            return 50.0
