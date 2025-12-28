"""Shared analysis indicators and technical analysis utilities."""

import numpy as np
import pandas as pd
from typing import Optional, Tuple, List


class TechnicalIndicators:
    """Technical analysis indicators."""

    @staticmethod
    def sma(data: np.ndarray, period: int) -> np.ndarray:
        """
        Simple Moving Average.
        
        Args:
            data: Price data
            period: Period for calculation
            
        Returns:
            np.ndarray: SMA values
        """
        return pd.Series(data).rolling(window=period).mean().values

    @staticmethod
    def ema(data: np.ndarray, period: int) -> np.ndarray:
        """
        Exponential Moving Average.
        
        Args:
            data: Price data
            period: Period for calculation
            
        Returns:
            np.ndarray: EMA values
        """
        return pd.Series(data).ewm(span=period, adjust=False).mean().values

    @staticmethod
    def rsi(data: np.ndarray, period: int = 14) -> np.ndarray:
        """
        Relative Strength Index.
        
        Args:
            data: Price data
            period: Period for calculation
            
        Returns:
            np.ndarray: RSI values
        """
        deltas = np.diff(data)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        rsi_values = np.zeros_like(data)
        rsi_values[:period] = 100.0 - 100.0 / (1.0 + rs)

        for i in range(period, len(data)):
            delta = deltas[i-1]
            if delta > 0:
                upval = delta
                downval = 0.0
            else:
                upval = 0.0
                downval = -delta

            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            rs = up / down if down != 0 else 0
            rsi_values[i] = 100.0 - 100.0 / (1.0 + rs)

        return rsi_values

    @staticmethod
    def macd(data: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        MACD (Moving Average Convergence Divergence).
        
        Args:
            data: Price data
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            
        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: MACD, Signal, Histogram
        """
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    @staticmethod
    def bollinger_bands(data: np.ndarray, period: int = 20, std_dev: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Bollinger Bands.
        
        Args:
            data: Price data
            period: Period for MA
            std_dev: Standard deviation multiplier
            
        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: Upper, Middle, Lower bands
        """
        middle = TechnicalIndicators.sma(data, period)
        std = pd.Series(data).rolling(window=period).std().values
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return upper, middle, lower

    @staticmethod
    def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
        """
        Average True Range.
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Period for calculation
            
        Returns:
            np.ndarray: ATR values
        """
        tr1 = high - low
        tr2 = np.abs(high - np.roll(close, 1))
        tr3 = np.abs(low - np.roll(close, 1))
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        tr[0] = tr1[0]

        atr_values = np.zeros_like(tr)
        atr_values[:period] = tr[:period].mean()

        for i in range(period, len(tr)):
            atr_values[i] = (atr_values[i-1] * (period - 1) + tr[i]) / period

        return atr_values

    @staticmethod
    def stochastic(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14, smooth_k: int = 3, smooth_d: int = 3) -> Tuple[np.ndarray, np.ndarray]:
        """
        Stochastic Oscillator.
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Lookback period
            smooth_k: K smoothing period
            smooth_d: D smoothing period
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: %K and %D values
        """
        lowest_low = pd.Series(low).rolling(window=period).min().values
        highest_high = pd.Series(high).rolling(window=period).max().values

        k_raw = np.zeros_like(close, dtype=float)
        for i in range(period-1, len(close)):
            if highest_high[i] != lowest_low[i]:
                k_raw[i] = 100 * (close[i] - lowest_low[i]) / (highest_high[i] - lowest_low[i])

        k_smooth = TechnicalIndicators.sma(k_raw, smooth_k)
        d_smooth = TechnicalIndicators.sma(k_smooth, smooth_d)

        return k_smooth, d_smooth

    @staticmethod
    def obv(close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """
        On-Balance Volume.
        
        Args:
            close: Close prices
            volume: Volume data
            
        Returns:
            np.ndarray: OBV values
        """
        obv_values = np.zeros_like(close, dtype=float)
        obv_values[0] = volume[0]

        for i in range(1, len(close)):
            if close[i] > close[i-1]:
                obv_values[i] = obv_values[i-1] + volume[i]
            elif close[i] < close[i-1]:
                obv_values[i] = obv_values[i-1] - volume[i]
            else:
                obv_values[i] = obv_values[i-1]

        return obv_values

    @staticmethod
    def adx(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
        """
        Average Directional Index.
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Period for calculation
            
        Returns:
            np.ndarray: ADX values
        """
        plus_dm = np.zeros_like(high)
        minus_dm = np.zeros_like(high)

        for i in range(1, len(high)):
            up_move = high[i] - high[i-1]
            down_move = low[i-1] - low[i]

            if up_move > down_move and up_move > 0:
                plus_dm[i] = up_move
            if down_move > up_move and down_move > 0:
                minus_dm[i] = down_move

        atr_vals = TechnicalIndicators.atr(high, low, close, period)
        plus_di = 100 * TechnicalIndicators.sma(plus_dm, period) / atr_vals
        minus_di = 100 * TechnicalIndicators.sma(minus_dm, period) / atr_vals
        di_diff = np.abs(plus_di - minus_di)
        di_sum = plus_di + minus_di
        di_sum = np.where(di_sum == 0, 1, di_sum)
        dx = 100 * di_diff / di_sum

        adx_values = TechnicalIndicators.sma(dx, period)
        return adx_values

    @staticmethod
    def roc(data: np.ndarray, period: int = 12) -> np.ndarray:
        """
        Rate of Change.
        
        Args:
            data: Price data
            period: Period for calculation
            
        Returns:
            np.ndarray: ROC values
        """
        roc_values = np.zeros_like(data, dtype=float)
        for i in range(period, len(data)):
            if data[i-period] != 0:
                roc_values[i] = ((data[i] - data[i-period]) / data[i-period]) * 100
        return roc_values

    @staticmethod
    def williams_percent_r(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
        """
        Williams %R.
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Period for calculation
            
        Returns:
            np.ndarray: Williams %R values
        """
        highest_high = pd.Series(high).rolling(window=period).max().values
        lowest_low = pd.Series(low).rolling(window=period).min().values

        wr = np.zeros_like(close, dtype=float)
        for i in range(period-1, len(close)):
            if highest_high[i] != lowest_low[i]:
                wr[i] = -100 * (highest_high[i] - close[i]) / (highest_high[i] - lowest_low[i])

        return wr

    @staticmethod
    def cci(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 20) -> np.ndarray:
        """
        Commodity Channel Index.
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Period for calculation
            
        Returns:
            np.ndarray: CCI values
        """
        typical_price = (high + low + close) / 3
        sma_tp = TechnicalIndicators.sma(typical_price, period)
        mad = pd.Series(typical_price).rolling(window=period).apply(
            lambda x: np.mean(np.abs(x - x.mean())), raw=True
        ).values

        cci_values = np.zeros_like(close, dtype=float)
        for i in range(period-1, len(close)):
            if mad[i] != 0:
                cci_values[i] = (typical_price[i] - sma_tp[i]) / (0.015 * mad[i])

        return cci_values
