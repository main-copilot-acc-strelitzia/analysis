"""Statistical utilities for analysis."""

import numpy as np
import pandas as pd
from typing import Tuple, Optional


class StatisticalTools:
    """Statistical analysis tools."""

    @staticmethod
    def calculate_returns(prices: np.ndarray) -> np.ndarray:
        """
        Calculate returns from price series.
        
        Args:
            prices: Price array
            
        Returns:
            np.ndarray: Returns array
        """
        prices = np.asarray(prices, dtype=float)
        return np.diff(prices) / prices[:-1]

    @staticmethod
    def calculate_log_returns(prices: np.ndarray) -> np.ndarray:
        """
        Calculate log returns.
        
        Args:
            prices: Price array
            
        Returns:
            np.ndarray: Log returns
        """
        prices = np.asarray(prices, dtype=float)
        return np.diff(np.log(prices))

    @staticmethod
    def volatility(returns: np.ndarray, periods: int = 252) -> float:
        """
        Calculate annualized volatility.
        
        Args:
            returns: Returns array
            periods: Periods per year (252 for daily)
            
        Returns:
            float: Annualized volatility
        """
        if len(returns) < 2:
            return 0.0
        return np.std(returns) * np.sqrt(periods)

    @staticmethod
    def sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.02, periods: int = 252) -> float:
        """
        Calculate Sharpe Ratio.
        
        Args:
            returns: Returns array
            risk_free_rate: Annual risk-free rate
            periods: Periods per year
            
        Returns:
            float: Sharpe Ratio
        """
        if len(returns) < 2:
            return 0.0
        excess_return = np.mean(returns) * periods - risk_free_rate
        vol = StatisticalTools.volatility(returns, periods)
        if vol == 0:
            return 0.0
        return excess_return / vol

    @staticmethod
    def correlation(series1: np.ndarray, series2: np.ndarray) -> float:
        """
        Calculate correlation between two series.
        
        Args:
            series1: First series
            series2: Second series
            
        Returns:
            float: Correlation coefficient
        """
        if len(series1) != len(series2) or len(series1) < 2:
            return 0.0
        return np.corrcoef(series1, series2)[0, 1]

    @staticmethod
    def rolling_correlation(series1: np.ndarray, series2: np.ndarray, window: int) -> np.ndarray:
        """
        Calculate rolling correlation.
        
        Args:
            series1: First series
            series2: Second series
            window: Rolling window size
            
        Returns:
            np.ndarray: Rolling correlation values
        """
        s1 = pd.Series(series1)
        s2 = pd.Series(series2)
        return s1.rolling(window).corr(s2).values

    @staticmethod
    def percentile(data: np.ndarray, percentile: float) -> float:
        """
        Calculate percentile.
        
        Args:
            data: Data array
            percentile: Percentile value (0-100)
            
        Returns:
            float: Percentile value
        """
        return np.percentile(data, percentile)

    @staticmethod
    def quantile(data: np.ndarray, q: float) -> float:
        """
        Calculate quantile.
        
        Args:
            data: Data array
            q: Quantile (0-1)
            
        Returns:
            float: Quantile value
        """
        return np.quantile(data, q)

    @staticmethod
    def value_at_risk(returns: np.ndarray, confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk.
        
        Args:
            returns: Returns array
            confidence: Confidence level (0-1)
            
        Returns:
            float: VaR value
        """
        return np.percentile(returns, (1 - confidence) * 100)

    @staticmethod
    def var_ratio(prices: np.ndarray, lag: int = 2) -> float:
        """
        Calculate variance ratio.
        
        Args:
            prices: Price array
            lag: Lag period
            
        Returns:
            float: Variance ratio
        """
        returns = StatisticalTools.calculate_returns(prices)
        var_lag = np.var(returns[::lag])
        var_1 = np.var(returns)
        if var_1 == 0:
            return 0.0
        return var_lag / var_1

    @staticmethod
    def hurst_exponent(prices: np.ndarray, lags: Optional[list] = None) -> float:
        """
        Calculate Hurst Exponent.
        
        Args:
            prices: Price array
            lags: Lag values to test
            
        Returns:
            float: Hurst Exponent
        """
        if lags is None:
            lags = list(range(10, min(len(prices) // 2, 100), 5))

        returns = StatisticalTools.calculate_log_returns(prices)
        tau = []

        for lag in lags:
            if lag >= len(returns):
                continue
            tau.append(np.sqrt(np.var(np.array([np.sum(returns[i:i+lag]) for i in range(0, len(returns)-lag, lag)]))))

        if len(tau) < 2:
            return 0.5

        log_tau = np.log(tau)
        log_lags = np.log(lags[:len(tau)])
        poly = np.polyfit(log_lags, log_tau, 1)
        return poly[0]

    @staticmethod
    def entropy(data: np.ndarray, bins: int = 10) -> float:
        """
        Calculate Shannon entropy.
        
        Args:
            data: Data array
            bins: Number of bins for histogram
            
        Returns:
            float: Entropy value
        """
        hist, _ = np.histogram(data, bins=bins, density=True)
        hist = hist[hist > 0]
        return -np.sum(hist * np.log2(hist + 1e-10))

    @staticmethod
    def skewness(data: np.ndarray) -> float:
        """
        Calculate skewness.
        
        Args:
            data: Data array
            
        Returns:
            float: Skewness value
        """
        if len(data) < 3:
            return 0.0
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 3)

    @staticmethod
    def kurtosis(data: np.ndarray) -> float:
        """
        Calculate excess kurtosis.
        
        Args:
            data: Data array
            
        Returns:
            float: Excess kurtosis
        """
        if len(data) < 4:
            return 0.0
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 4) - 3

    @staticmethod
    def autocorrelation(data: np.ndarray, lag: int) -> float:
        """
        Calculate autocorrelation.
        
        Args:
            data: Data array
            lag: Lag period
            
        Returns:
            float: Autocorrelation value
        """
        if lag >= len(data):
            return 0.0
        c0 = np.var(data)
        c = np.mean((data[:-lag] - np.mean(data)) * (data[lag:] - np.mean(data)))
        if c0 == 0:
            return 0.0
        return c / c0


class StatisticalAnalysis:
    """Compatibility shim providing higher-level statistical analyses used by analyzers.

    This wraps lower-level utilities in `StatisticalTools` so older imports keep working.
    """

    @staticmethod
    def correlation_with_market(data) -> dict:
        """Return simple correlation metrics for the provided OHLCV DataFrame-like object."""
        try:
            closes = np.asarray(data['Close'].values)
        except Exception:
            return {}

        result = {
            'close_autocorr_lag1': float(StatisticalTools.autocorrelation(closes, 1))
        }

        if 'Volume' in data.columns:
            vols = np.asarray(data['Volume'].values)
            result['close_volume_corr'] = float(StatisticalTools.correlation(closes, vols))

        return result

    @staticmethod
    def price_distribution_analysis(data) -> dict:
        """Return basic distribution statistics for the `Close` price series."""
        try:
            closes = np.asarray(data['Close'].values, dtype=float)
        except Exception:
            return {}

        returns = StatisticalTools.calculate_log_returns(closes)
        return {
            'mean_return': float(np.mean(returns)) if len(returns) else 0.0,
            'std_return': float(np.std(returns)) if len(returns) else 0.0,
            'skewness': float(StatisticalTools.skewness(returns)) if len(returns) else 0.0,
            'kurtosis': float(StatisticalTools.kurtosis(returns)) if len(returns) else 0.0,
            'var_95': float(StatisticalTools.value_at_risk(returns, 0.95)) if len(returns) else 0.0,
        }

    @staticmethod
    def anomaly_detection(data, z_thresh: float = 3.0) -> dict:
        """Detect simple anomalies in `Close` returns using z-score thresholding."""
        try:
            closes = np.asarray(data['Close'].values, dtype=float)
        except Exception:
            return {'anomalies': []}

        returns = StatisticalTools.calculate_log_returns(closes)
        if len(returns) == 0:
            return {'anomalies': []}

        mu = np.mean(returns)
        sigma = np.std(returns)
        if sigma == 0:
            return {'anomalies': []}

        z = (returns - mu) / sigma
        anomaly_idxs = list(np.where(np.abs(z) >= z_thresh)[0].tolist())
        return {'anomalies': anomaly_idxs, 'count': len(anomaly_idxs)}
