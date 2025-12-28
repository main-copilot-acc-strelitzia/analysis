"""Fair value gap analysis for Forex."""

import numpy as np
import pandas as pd


class FairValueGapAnalysis:
    """Analyzes fair value gaps (FVG)."""

    @staticmethod
    def bullish_fvg_detection(data: pd.DataFrame) -> float:
        """
        Detect bullish FVG (imbalance).
        
        Returns bullish FVG signal 0-100.
        """
        if len(data) < 3:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values

        # Bullish FVG: Current bar's low > Previous-2 bar's high
        for i in range(2, len(data)):
            if lows[i] > highs[i-2]:
                return 80.0

        return 50.0

    @staticmethod
    def bearish_fvg_detection(data: pd.DataFrame) -> float:
        """
        Detect bearish FVG (imbalance).
        
        Returns bearish FVG signal 0-100.
        """
        if len(data) < 3:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values

        # Bearish FVG: Current bar's high < Previous-2 bar's low
        for i in range(2, len(data)):
            if highs[i] < lows[i-2]:
                return 20.0

        return 50.0

    @staticmethod
    def fvg_fill_probability(data: pd.DataFrame) -> float:
        """
        Estimate probability that FVG will be filled.
        
        Returns fill probability 0-100.
        """
        if len(data) < 10:
            return 50.0

        # Count filled vs unfilled FVGs
        highs = data['High'].values
        lows = data['Low'].values

        filled_count = 0
        unfilled_count = 0

        for i in range(5, len(data)):
            # Check historical FVGs
            if lows[i] > highs[i-2]:  # Bullish FVG formed
                # Check if filled later
                if np.min(lows[i:min(i+5, len(data))]) < highs[i-2]:
                    filled_count += 1
                else:
                    unfilled_count += 1

            if highs[i] < lows[i-2]:  # Bearish FVG formed
                if np.max(highs[i:min(i+5, len(data))]) > lows[i-2]:
                    filled_count += 1
                else:
                    unfilled_count += 1

        total = filled_count + unfilled_count
        if total == 0:
            return 50.0

        return (filled_count / total) * 100

    @staticmethod
    def fvg_magnitude(data: pd.DataFrame) -> float:
        """
        Measure magnitude of FVGs.
        
        Returns magnitude score 0-100.
        """
        if len(data) < 3:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values
        closes = data['Close'].values

        max_fvg_size = 0
        for i in range(2, len(data)):
            if lows[i] > highs[i-2]:
                fvg_size = lows[i] - highs[i-2]
                max_fvg_size = max(max_fvg_size, fvg_size)
            if highs[i] < lows[i-2]:
                fvg_size = lows[i-2] - highs[i]
                max_fvg_size = max(max_fvg_size, fvg_size)

        # Normalize to percentage
        magnitude_pct = (max_fvg_size / closes[-1]) * 100
        return min(magnitude_pct * 10, 100.0)

    @staticmethod
    def fvg_structure_confirmation(data: pd.DataFrame) -> float:
        """
        Confirm FVG with market structure.
        
        Returns confirmation signal 0-100.
        """
        if len(data) < 10:
            return 50.0

        closes = data['Close'].values
        highs = data['High'].values
        lows = data['Low'].values

        # FVG + higher highs = strong bullish
        bullish_confirmation = 0
        bearish_confirmation = 0

        for i in range(5, len(data)):
            if lows[i] > highs[i-2]:  # Bullish FVG
                if highs[i] > highs[i-1]:  # Higher high
                    bullish_confirmation += 1

            if highs[i] < lows[i-2]:  # Bearish FVG
                if lows[i] < lows[i-1]:  # Lower low
                    bearish_confirmation += 1

        if bullish_confirmation > bearish_confirmation:
            return 75.0
        elif bearish_confirmation > bullish_confirmation:
            return 25.0
        else:
            return 50.0

    @staticmethod
    def fvg_type_analysis(data: pd.DataFrame) -> str:
        """
        Classify FVG types.
        
        Returns FVG type: 'Bullish', 'Bearish', 'None'
        """
        if len(data) < 3:
            return 'None'

        highs = data['High'].values
        lows = data['Low'].values

        for i in range(2, len(data)):
            if lows[i] > highs[i-2]:
                return 'Bullish'
            if highs[i] < lows[i-2]:
                return 'Bearish'

        return 'None'

    @staticmethod
    def fvg_depletion_level(data: pd.DataFrame) -> float:
        """
        Identify FVG depletion (where imbalance ends).
        
        Returns depletion signal 0-100.
        """
        if len(data) < 5:
            return 50.0

        highs = data['High'].values
        lows = data['Low'].values

        depletion_signal = 50.0

        for i in range(2, len(data) - 1):
            if lows[i] > highs[i-2]:  # Bullish FVG
                # Check if price goes back into FVG
                if lows[i+1] < highs[i-2]:
                    depletion_signal = 80.0

            if highs[i] < lows[i-2]:  # Bearish FVG
                if highs[i+1] > lows[i-2]:
                    depletion_signal = 20.0

        return depletion_signal
