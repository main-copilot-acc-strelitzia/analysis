"""Tick behavior analysis for synthetics."""

import numpy as np
import pandas as pd


class TickBehaviorAnalysis:
    """Analyzes tick-by-tick behavior in synthetics."""

    @staticmethod
    def tick_frequency(data: pd.DataFrame) -> float:
        """
        Measure tick frequency (approximate with volume).
        
        Returns frequency signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        volumes = data['Volume'].values[-10:]
        avg_volume = np.mean(volumes)

        if volumes[-1] > avg_volume * 1.5:
            return 75.0
        elif volumes[-1] < avg_volume * 0.5:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def tick_volatility(data: pd.DataFrame) -> float:
        """
        Measure volatility at tick level.
        
        Returns tick volatility 0-100.
        """
        if len(data) < 10:
            return 50.0

        ranges = (data['High'].values - data['Low'].values) / data['Close'].values * 100

        avg_range = np.mean(ranges[-10:])

        if avg_range > 0.5:
            return 75.0
        elif avg_range < 0.1:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def tick_direction_bias(data: pd.DataFrame) -> float:
        """
        Detect directional bias in ticks.
        
        Returns bias signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        closes = data['Close'].values
        upticks = np.sum(np.diff(closes) > 0)
        downticks = np.sum(np.diff(closes) < 0)

        total = upticks + downticks
        if total == 0:
            return 50.0

        upbias = upticks / total
        return upbias * 100

    @staticmethod
    def tick_clustering(data: pd.DataFrame) -> float:
        """
        Detect tick clustering patterns.
        
        Returns clustering signal 0-100.
        """
        if len(data) < 15:
            return 50.0

        ranges = data['High'].values - data['Low'].values
        volumes = data['Volume'].values

        # Clustering: high volume with tight range
        tight_range = ranges < np.mean(ranges)
        high_volume = volumes > np.mean(volumes)

        clusters = np.sum(tight_range & high_volume)

        if clusters >= 3:
            return 75.0
        else:
            return 50.0

    @staticmethod
    def microstructure_noise(data: pd.DataFrame) -> float:
        """
        Estimate microstructure noise level.
        
        Returns noise level 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        diffs = np.abs(np.diff(closes))

        noise_level = np.std(diffs) / np.mean(diffs) if np.mean(diffs) > 0 else 0

        return min(noise_level * 50, 100.0)
