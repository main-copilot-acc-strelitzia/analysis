"""Step indices analysis."""

import numpy as np
import pandas as pd


class StepIndicesAnalysis:
    """Analyzes Step synthetic indices."""

    @staticmethod
    def step_size_consistency(data: pd.DataFrame) -> float:
        """
        Measure consistency of steps.
        
        Returns consistency signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        closes = data['Close'].values
        changes = np.abs(np.diff(closes))

        avg_change = np.mean(changes)
        std_change = np.std(changes)

        if avg_change == 0:
            return 50.0

        consistency = 1.0 / (1.0 + std_change / avg_change)
        return consistency * 100

    @staticmethod
    def step_direction_pattern(data: pd.DataFrame) -> float:
        """
        Identify step direction pattern.
        
        Returns direction signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        closes = data['Close'].values
        diffs = np.diff(closes)

        upsteps = np.sum(diffs > 0)
        downsteps = np.sum(diffs < 0)

        if upsteps > downsteps * 1.3:
            return 75.0
        elif downsteps > upsteps * 1.3:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def step_acceleration(data: pd.DataFrame) -> float:
        """
        Detect step acceleration or deceleration.
        
        Returns acceleration signal 0-100.
        """
        if len(data) < 15:
            return 50.0

        closes = data['Close'].values
        changes = np.abs(np.diff(closes))

        recent_change = np.mean(changes[-5:])
        prior_change = np.mean(changes[-10:-5])

        if prior_change == 0:
            return 50.0

        acceleration = recent_change / prior_change

        if acceleration > 1.3:
            return 75.0
        elif acceleration < 0.7:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def step_uniformity(data: pd.DataFrame) -> float:
        """
        Measure uniformity of steps.
        
        Returns uniformity 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        changes = np.abs(np.diff(closes))

        avg_change = np.mean(changes)
        uniform_count = np.sum((changes > avg_change * 0.9) & (changes < avg_change * 1.1))

        uniformity = uniform_count / len(changes)
        return uniformity * 100

    @staticmethod
    def step_regularity(data: pd.DataFrame) -> float:
        """
        Measure regularity of step timing.
        
        Returns regularity 0-100.
        """
        if len(data) < 20:
            return 50.0

        closes = data['Close'].values
        changes = np.diff(closes)

        # Steps occur at regular intervals
        step_intervals = []
        last_step_idx = 0

        for i in range(1, len(changes)):
            if abs(changes[i]) > np.mean(np.abs(changes)) * 0.5:
                interval = i - last_step_idx
                step_intervals.append(interval)
                last_step_idx = i

        if len(step_intervals) < 2:
            return 50.0

        interval_std = np.std(step_intervals)
        interval_mean = np.mean(step_intervals)

        if interval_mean == 0:
            return 50.0

        regularity = 1.0 / (1.0 + interval_std / interval_mean)
        return regularity * 100

    @staticmethod
    def step_momentum_buildup(data: pd.DataFrame) -> float:
        """
        Detect momentum building in step pattern.
        
        Returns momentum signal 0-100.
        """
        if len(data) < 15:
            return 50.0

        closes = data['Close'].values
        changes = np.abs(np.diff(closes[-10:]))

        for i in range(1, len(changes)):
            if changes[i] < changes[i-1]:
                return 40.0  # Decelerating

        return 75.0  # Accelerating

    @staticmethod
    def step_sequence_prediction(data: pd.DataFrame) -> float:
        """
        Predict next step direction.
        
        Returns prediction confidence 0-100.
        """
        if len(data) < 10:
            return 50.0

        closes = data['Close'].values
        diffs = np.diff(closes)

        recent_direction = np.mean(diffs[-3:])

        if recent_direction > 0:
            return 70.0
        elif recent_direction < 0:
            return 30.0
        else:
            return 50.0

    @staticmethod
    def step_volatility_profile(data: pd.DataFrame) -> str:
        """
        Identify step volatility profile.
        
        Returns profile: 'Consistent', 'Increasing', 'Decreasing'
        """
        if len(data) < 15:
            return 'Neutral'

        closes = data['Close'].values
        ranges = data['High'].values - data['Low'].values

        recent_range = np.mean(ranges[-5:])
        prior_range = np.mean(ranges[-10:-5])

        if recent_range > prior_range * 1.2:
            return 'Increasing'
        elif recent_range < prior_range * 0.8:
            return 'Decreasing'
        else:
            return 'Consistent'
