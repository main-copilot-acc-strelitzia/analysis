"""Multi-timeframe analysis for Forex."""

import numpy as np
import pandas as pd


class MultiTimeframeAnalysis:
    """Analyzes relationships across timeframes."""

    @staticmethod
    def higher_timeframe_alignment(current_tf_signal: float, higher_tf_signal: float) -> float:
        """
        Measure alignment between current and higher timeframe.
        
        Args:
            current_tf_signal: Signal from current timeframe (0-100)
            higher_tf_signal: Signal from higher timeframe (0-100)
            
        Returns:
            Alignment score 0-100.
        """
        diff = abs(current_tf_signal - higher_tf_signal)

        if diff < 10:
            return 90.0
        elif diff < 20:
            return 75.0
        elif diff < 30:
            return 60.0
        else:
            return 40.0

    @staticmethod
    def timeframe_confirmation(data_dict: dict) -> float:
        """
        Confirm signal across multiple timeframes.
        
        Args:
            data_dict: Dictionary of timeframe signals
            
        Returns:
            Confirmation strength 0-100.
        """
        if not data_dict:
            return 50.0

        signals = list(data_dict.values())

        if len(signals) < 2:
            return 50.0

        # All signals bullish (>60)
        bullish_count = sum(1 for s in signals if s > 60)
        bearish_count = sum(1 for s in signals if s < 40)

        if bullish_count >= len(signals) - 1:
            return 85.0
        elif bearish_count >= len(signals) - 1:
            return 15.0
        else:
            return 50.0

    @staticmethod
    def trend_alignment_strength(trends: dict) -> float:
        """
        Measure strength of trend alignment across timeframes.
        
        Args:
            trends: Dictionary of timeframe trends ('Uptrend', 'Downtrend', 'Sideways')
            
        Returns:
            Alignment strength 0-100.
        """
        if not trends:
            return 50.0

        uptrends = sum(1 for t in trends.values() if t == 'Uptrend')
        downtrends = sum(1 for t in trends.values() if t == 'Downtrend')
        sideways = sum(1 for t in trends.values() if t == 'Sideways')

        total = len(trends)

        if uptrends == total:
            return 95.0
        elif downtrends == total:
            return 5.0
        elif uptrends >= downtrends:
            return 50.0 + (uptrends / total * 30)
        else:
            return 50.0 - (downtrends / total * 30)

    @staticmethod
    def confluence_across_timeframes(signals_by_tf: dict) -> float:
        """
        Calculate confluence score across timeframes.
        
        Args:
            signals_by_tf: Dictionary mapping timeframe to signal value
            
        Returns:
            Confluence score 0-100.
        """
        if not signals_by_tf:
            return 50.0

        values = list(signals_by_tf.values())

        # Calculate variance
        mean_signal = np.mean(values)
        variance = np.var(values)

        # Low variance = high confluence
        if variance < 100:
            return 80.0
        elif variance < 300:
            return 65.0
        elif variance < 600:
            return 50.0
        else:
            return 35.0

    @staticmethod
    def divergence_detection(data_m15: pd.DataFrame, data_h1: pd.DataFrame) -> str:
        """
        Detect divergences between lower and higher timeframes.
        
        Args:
            data_m15: Lower timeframe data
            data_h1: Higher timeframe data
            
        Returns:
            Divergence type: 'Bullish', 'Bearish', 'None'
        """
        if len(data_m15) < 5 or len(data_h1) < 5:
            return 'None'

        # Simple divergence: price makes lower low but oscillator makes higher low
        m15_close = data_m15['Close'].values
        h1_close = data_h1['Close'].values

        m15_lower_low = m15_close[-1] < np.min(m15_close[-10:-1])
        h1_higher_low = h1_close[-1] > np.min(h1_close[-10:-1])

        if m15_lower_low and h1_higher_low:
            return 'Bullish'

        m15_higher_high = m15_close[-1] > np.max(m15_close[-10:-1])
        h1_lower_high = h1_close[-1] < np.max(h1_close[-10:-1])

        if m15_higher_high and h1_lower_high:
            return 'Bearish'

        return 'None'

    @staticmethod
    def sweet_spot_timeframe(signals_by_tf: dict) -> str:
        """
        Identify the timeframe with strongest confluence.
        
        Args:
            signals_by_tf: Dictionary mapping timeframe to signal value
            
        Returns:
            Timeframe with highest signal strength.
        """
        if not signals_by_tf:
            return None

        # Find timeframe closest to extreme (0 or 100)
        best_tf = max(signals_by_tf.items(), 
                     key=lambda x: max(x[1], 100 - x[1]))
        return best_tf[0]

    @staticmethod
    def mean_reversion_setup(data_short: pd.DataFrame, data_long: pd.DataFrame) -> float:
        """
        Identify mean reversion setups across timeframes.
        
        Returns setup strength 0-100.
        """
        if len(data_short) < 10 or len(data_long) < 20:
            return 50.0

        short_close = data_short['Close'].values
        long_close = data_long['Close'].values

        # Price far from mean on short TF but near mean on long TF
        short_mean = np.mean(short_close)
        long_mean = np.mean(long_close)

        short_distance = abs(short_close[-1] - short_mean) / short_mean * 100
        long_distance = abs(long_close[-1] - long_mean) / long_mean * 100

        if short_distance > 2 * long_distance:
            return 75.0
        else:
            return 50.0

    @staticmethod
    def trend_continuation_likelihood(data_short: pd.DataFrame, data_long: pd.DataFrame) -> float:
        """
        Estimate trend continuation likelihood across timeframes.
        
        Returns continuation probability 0-100.
        """
        if len(data_short) < 10 or len(data_long) < 20:
            return 50.0

        short_trend = np.mean(np.diff(data_short['Close'].values[-5:])) > 0
        long_trend = np.mean(np.diff(data_long['Close'].values[-10:])) > 0

        if short_trend == long_trend:
            return 80.0
        else:
            return 40.0
