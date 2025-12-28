"""Jump indices analysis."""

import numpy as np
import pandas as pd


class JumpIndicesAnalysis:
    """Analyzes Jump synthetic indices."""

    @staticmethod
    def jump_detection(data: pd.DataFrame) -> float:
        """
        Detect jump events in index.
        
        Returns jump signal 0-100.
        """
        if len(data) < 5:
            return 50.0

        opens = data['Open'].values
        closes = data['Close'].values

        gaps = np.abs(opens[1:] - closes[:-1]) / closes[:-1] * 100

        avg_gap = np.mean(gaps)
        current_gap = abs(opens[-1] - closes[-2]) / closes[-2] * 100 if len(closes) > 1 else 0

        if current_gap > avg_gap * 2:
            return 80.0
        elif current_gap > avg_gap:
            return 65.0
        else:
            return 50.0

    @staticmethod
    def jump_frequency(data: pd.DataFrame, threshold: float = 0.5) -> float:
        """
        Measure jump frequency.
        
        Returns frequency signal 0-100.
        """
        if len(data) < 20:
            return 50.0

        opens = data['Open'].values
        closes = data['Close'].values

        gaps = np.abs(opens[1:] - closes[:-1]) / closes[:-1] * 100
        jump_count = np.sum(gaps > threshold)

        frequency_ratio = jump_count / len(gaps)

        return min(frequency_ratio * 100, 100.0)

    @staticmethod
    def jump_direction_bias(data: pd.DataFrame) -> float:
        """
        Detect directional bias in jumps.
        
        Returns direction bias 0-100.
        """
        if len(data) < 10:
            return 50.0

        opens = data['Open'].values
        closes = data['Close'].values

        upjumps = np.sum(opens[1:] > closes[:-1])
        downjumps = np.sum(opens[1:] < closes[:-1])

        if len(opens) < 2:
            return 50.0

        if upjumps > downjumps * 1.5:
            return 75.0
        elif downjumps > upjumps * 1.5:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def jump_magnitude_analysis(data: pd.DataFrame) -> float:
        """
        Analyze magnitude of jumps.
        
        Returns magnitude signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        opens = data['Open'].values
        closes = data['Close'].values

        gaps = np.abs(opens[1:] - closes[:-1])
        avg_gap = np.mean(gaps)
        max_gap = np.max(gaps)

        if max_gap > avg_gap * 3:
            return 75.0
        elif max_gap > avg_gap * 2:
            return 60.0
        else:
            return 50.0

    @staticmethod
    def jump_volatility_correlation(data: pd.DataFrame) -> float:
        """
        Correlate jumps with volatility.
        
        Returns correlation signal 0-100.
        """
        if len(data) < 15:
            return 50.0

        ranges = data['High'].values - data['Low'].values
        volumes = data['Volume'].values

        high_vol_periods = volumes > np.mean(volumes)
        jumpy_periods = ranges > np.mean(ranges)

        overlap = np.sum(high_vol_periods & jumpy_periods)
        correlation = overlap / max(np.sum(high_vol_periods | jumpy_periods), 1)

        return correlation * 100

    @staticmethod
    def jump_predictability(data: pd.DataFrame) -> float:
        """
        Estimate predictability of jumps.
        
        Returns predictability 0-100.
        """
        if len(data) < 20:
            return 50.0

        opens = data['Open'].values
        closes = data['Close'].values

        gaps = np.abs(opens[1:] - closes[:-1])
        gap_std = np.std(gaps)
        gap_mean = np.mean(gaps)

        if gap_mean == 0:
            return 50.0

        # Low std = predictable, high std = unpredictable
        unpredictability = gap_std / gap_mean
        predictability = 100.0 / (1.0 + unpredictability)

        return min(predictability, 100.0)

    @staticmethod
    def consecutive_jump_analysis(data: pd.DataFrame) -> float:
        """
        Analyze consecutive jump patterns.
        
        Returns pattern signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        opens = data['Open'].values
        closes = data['Close'].values

        gaps = np.abs(opens[1:] - closes[:-1])
        avg_gap = np.mean(gaps)

        large_gaps = gaps > avg_gap * 1.5

        # Count consecutive large gaps
        max_consecutive = 0
        current_consecutive = 0

        for gap in large_gaps:
            if gap:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0

        if max_consecutive >= 3:
            return 80.0
        elif max_consecutive >= 2:
            return 65.0
        else:
            return 50.0
