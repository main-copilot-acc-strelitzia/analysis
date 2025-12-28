"""
Context-Aware Candlestick Pattern Evaluation.

Evaluates candlestick patterns in context (trend, support/resistance, volatility).
Applies false-positive filtering and lower confidence weighting.
Ensures patterns don't override higher-level structure analysis.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple, List
from dataclasses import dataclass

from core.logger import Logger
from analysis.shared.utils import AnalysisUtils
from analysis.shared.indicators import TechnicalIndicators


@dataclass
class PatternContext:
    """Context information for pattern evaluation."""
    
    trend_direction: str  # "up", "down", "sideways"
    volatility_regime: str  # "low", "normal", "high"
    near_support: bool
    near_resistance: bool
    in_liquidity_zone: bool
    candle_strength: float  # 0-100, body size relative to range


class CandlestickContextEvaluator:
    """
    Evaluates candlestick patterns within market context.
    
    Filters false positives, applies context-based confidence adjustments,
    weights patterns lower than structure/trend signals.
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """Initialize evaluator."""
        self.logger = logger or Logger.get_instance()
    
    def evaluate_pattern(
        self,
        candles: pd.DataFrame,
        pattern_type: str,
        pattern_confidence: float,
        context: Optional[PatternContext] = None
    ) -> Tuple[float, str]:
        """
        Evaluate a detected candlestick pattern in context.
        
        Args:
            candles: OHLCV dataframe
            pattern_type: Pattern name (e.g., "bullish_engulfing", "hammer")
            pattern_confidence: Raw pattern confidence (0-100)
            context: PatternContext with market information
            
        Returns:
            Tuple of (adjusted_confidence, signal_type)
            adjusted_confidence: 0-100, accounting for context
            signal_type: "bullish", "bearish", or "neutral"
        """
        if context is None:
            context = self._analyze_context(candles)
        
        # Determine pattern signal type
        signal_type = self._get_pattern_signal(pattern_type)
        
        # Apply context-based adjustments
        adjusted_confidence = self._apply_context_adjustments(
            pattern_confidence,
            pattern_type,
            signal_type,
            context,
            candles
        )
        
        # Apply false-positive filters
        adjusted_confidence = self._apply_false_positive_filter(
            adjusted_confidence,
            pattern_type,
            candles,
            context
        )
        
        # Scale down pattern confidence (patterns are lower weight than structure)
        adjusted_confidence = adjusted_confidence * 0.6  # 60% of original
        
        return adjusted_confidence, signal_type
    
    def _analyze_context(self, candles: pd.DataFrame) -> PatternContext:
        """Analyze market context from candles."""
        if len(candles) < 20:
            return PatternContext(
                trend_direction="sideways",
                volatility_regime="normal",
                near_support=False,
                near_resistance=False,
                in_liquidity_zone=False,
                candle_strength=50.0
            )
        
        # Trend direction
        sma_20 = TechnicalIndicators.sma(candles['Close'], 20).iloc[-1]
        sma_50 = TechnicalIndicators.sma(candles['Close'], 50).iloc[-1] if len(candles) >= 50 else sma_20
        current_price = candles['Close'].iloc[-1]
        
        if current_price > sma_20 > sma_50:
            trend = "up"
        elif current_price < sma_20 < sma_50:
            trend = "down"
        else:
            trend = "sideways"
        
        # Volatility regime
        recent_volatility = candles['High'].iloc[-10:].max() - candles['Low'].iloc[-10:].min()
        avg_volatility = (candles['High'] - candles['Low']).tail(20).mean()
        
        if recent_volatility > avg_volatility * 1.5:
            vol_regime = "high"
        elif recent_volatility < avg_volatility * 0.7:
            vol_regime = "low"
        else:
            vol_regime = "normal"
        
        # Support/Resistance proximity
        support, resistance = AnalysisUtils.find_support_resistance(
            candles['Close'].values,
            window=20
        )
        
        near_support = abs(current_price - support) < (current_price * 0.01)
        near_resistance = abs(current_price - resistance) < (current_price * 0.01)
        
        # Liquidity zones (highs/lows from recent candles)
        recent_high = candles['High'].tail(10).max()
        recent_low = candles['Low'].tail(10).min()
        in_liquidity = (
            abs(current_price - recent_high) < (current_price * 0.005) or
            abs(current_price - recent_low) < (current_price * 0.005)
        )
        
        # Candle strength
        last_candle = candles.iloc[-1]
        candle_range = last_candle['High'] - last_candle['Low']
        candle_body = abs(last_candle['Close'] - last_candle['Open'])
        candle_strength = (candle_body / candle_range * 100) if candle_range > 0 else 50.0
        
        return PatternContext(
            trend_direction=trend,
            volatility_regime=vol_regime,
            near_support=near_support,
            near_resistance=near_resistance,
            in_liquidity_zone=in_liquidity,
            candle_strength=min(100.0, candle_strength)
        )
    
    def _get_pattern_signal(self, pattern_type: str) -> str:
        """Get signal type for pattern."""
        bullish_patterns = {
            'hammer', 'inverted_hammer', 'bullish_engulfing',
            'morning_star', 'pin_bar_bullish', 'inside_bar_bullish',
            'mechanical_doji_bullish', 'synthetic_reversal_candle_bullish'
        }
        
        bearish_patterns = {
            'hanging_man', 'bearish_engulfing',
            'evening_star', 'pin_bar_bearish', 'inside_bar_bearish',
            'mechanical_doji_bearish', 'synthetic_reversal_candle_bearish'
        }
        
        if pattern_type in bullish_patterns:
            return "bullish"
        elif pattern_type in bearish_patterns:
            return "bearish"
        else:
            return "neutral"
    
    def _apply_context_adjustments(
        self,
        confidence: float,
        pattern_type: str,
        signal_type: str,
        context: PatternContext,
        candles: pd.DataFrame
    ) -> float:
        """Apply context-based adjustments to pattern confidence."""
        adjusted = confidence
        
        # Trend alignment bonus
        if signal_type == "bullish" and context.trend_direction == "up":
            adjusted *= 1.15  # 15% boost
        elif signal_type == "bearish" and context.trend_direction == "down":
            adjusted *= 1.15
        elif context.trend_direction == "sideways":
            adjusted *= 0.9  # 10% penalty in sideways market
        else:
            adjusted *= 0.7  # 30% penalty against trend
        
        # Support/Resistance context
        if signal_type == "bullish" and context.near_support:
            adjusted *= 1.20  # 20% boost at support
        elif signal_type == "bearish" and context.near_resistance:
            adjusted *= 1.20
        
        # Volatility context
        if context.volatility_regime == "high":
            adjusted *= 0.8  # Lower confidence in high volatility
        elif context.volatility_regime == "low":
            adjusted *= 0.9  # Slightly lower in low volatility
        
        # Candle strength
        if context.candle_strength > 70:
            adjusted *= 1.10  # Strong candles more reliable
        elif context.candle_strength < 30:
            adjusted *= 0.7  # Weak candles less reliable
        
        return min(100.0, max(0.0, adjusted))
    
    def _apply_false_positive_filter(
        self,
        confidence: float,
        pattern_type: str,
        candles: pd.DataFrame,
        context: PatternContext
    ) -> float:
        """
        Apply false-positive filtering.
        
        Reduces confidence for patterns with typical false-positive indicators.
        """
        if len(candles) < 5:
            return 0.0  # Insufficient data
        
        last_candle = candles.iloc[-1]
        prev_candle = candles.iloc[-2]
        
        # High spread = unreliable
        spread = last_candle.get('Spread', 0)
        if spread > 0:
            spread_pct = (spread / last_candle['Close']) * 100
            if spread_pct > 0.5:  # > 0.5% spread
                confidence *= 0.6
        
        # Very small candles = noise
        candle_size = abs(last_candle['Close'] - last_candle['Open'])
        avg_candle_size = (candles['High'] - candles['Low']).tail(10).mean()
        if avg_candle_size > 0 and candle_size < avg_candle_size * 0.3:
            confidence *= 0.5
        
        # Contradictory volume = false signal
        volume = last_candle.get('Volume', 0)
        avg_volume = candles['Volume'].tail(10).mean()
        if avg_volume > 0 and volume < avg_volume * 0.3:
            confidence *= 0.7  # Low volume = less reliable
        
        # Recent patterns (within past 2 candles) = higher reliability
        # Older patterns already formed = might be less relevant
        
        return min(100.0, max(0.0, confidence))
    
    def filter_pattern_set(
        self,
        patterns: List[Tuple[str, float]],
        candles: pd.DataFrame,
        max_patterns: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Filter and rank multiple patterns.
        
        Args:
            patterns: List of (pattern_type, confidence) tuples
            candles: OHLCV dataframe
            max_patterns: Maximum patterns to return
            
        Returns:
            Filtered and sorted patterns
        """
        context = self._analyze_context(candles)
        evaluated = []
        
        for pattern_type, confidence in patterns:
            adjusted_conf, _ = self.evaluate_pattern(
                candles, pattern_type, confidence, context
            )
            if adjusted_conf > 20.0:  # Minimum threshold
                evaluated.append((pattern_type, adjusted_conf))
        
        # Sort by adjusted confidence
        evaluated.sort(key=lambda x: x[1], reverse=True)
        
        # Return top patterns
        return evaluated[:max_patterns]
    
    def is_pattern_reliable(
        self,
        pattern_type: str,
        confidence: float,
        candles: pd.DataFrame
    ) -> bool:
        """
        Quick check if pattern meets reliability threshold.
        
        Returns:
            True if pattern confidence > 50 after context adjustment
        """
        adjusted, _ = self.evaluate_pattern(candles, pattern_type, confidence)
        return adjusted > 50.0
