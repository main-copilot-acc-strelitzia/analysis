"""
Confluence Engine - Aggregates analysis signals and computes confluence scores.

Combines outputs from all analysis modules (Forex, Synthetics, Indices, etc).
Weights signals appropriately. Computes bullish/bearish/neutral confluence with confidence.
Filters candlestick patterns with lower weighting.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import statistics

from core.logger import Logger


class SignalType(Enum):
    """Signal classification types."""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class SignalCategory(Enum):
    """Signal source categories with default weights."""
    STRUCTURE = 1.0          # Market structure (highest weight)
    TREND = 0.95             # Trend analysis
    MOMENTUM = 0.90          # Momentum indicators
    VOLATILITY = 0.85        # Volatility measures
    VOLUME = 0.80            # Volume analysis
    SESSIONS = 0.75          # Session-based signals
    LIQUIDITY = 0.90         # Liquidity analysis
    ORDER_BLOCKS = 0.95      # Institutional order blocks
    FAIR_VALUE_GAPS = 0.88   # Fair value gap analysis
    CONFLUENCE = 0.92        # Level confluence
    MULTI_TIMEFRAME = 0.98   # Multi-timeframe bias (very high)
    CANDLESTICK = 0.40       # Candlestick patterns (low weight)
    SYNTHETIC_VOLATILITY = 0.85  # Synthetic volatility
    SYNTHETIC_REGIME = 0.88      # Synthetic regime detection
    SESSION_BEHAVIOR = 0.80      # Index session behavior


@dataclass
class Signal:
    """Individual analysis signal with metadata."""
    
    category: SignalCategory
    signal_type: SignalType
    confidence: float  # 0.0-100.0
    weight: float     # 1.0 by default, can be custom
    source: str       # e.g., "RSI_momentum", "bullish_OB", "morning_star"
    description: str
    
    def __post_init__(self):
        """Validate signal."""
        self.confidence = max(0.0, min(100.0, self.confidence))
        self.weight = max(0.0, self.weight)
    
    def get_effective_weight(self) -> float:
        """Get effective weight = category weight * custom weight."""
        return self.category.value * self.weight
    
    def get_weighted_signal(self) -> float:
        """
        Get weighted signal value (-100 to +100).
        
        Positive = bullish, Negative = bearish
        Magnitude affected by confidence and weight.
        """
        base_value = 100.0 if self.signal_type == SignalType.BULLISH else -100.0
        confidence_factor = self.confidence / 100.0
        weight_factor = self.get_effective_weight()
        
        return base_value * confidence_factor * weight_factor


@dataclass
class ConfluenceResult:
    """Result of confluence analysis."""
    
    bullish_score: float        # 0-100
    bearish_score: float        # 0-100
    neutral_probability: float  # 0-100
    confidence_percentage: float  # 0-100
    
    market_bias: str  # "Strong Bullish", "Bullish", "Neutral", "Bearish", "Strong Bearish"
    
    signal_count: int
    bullish_signals: int
    bearish_signals: int
    neutral_signals: int
    
    top_factors: List[Tuple[str, float]]  # [(source, weight), ...]
    weighted_signals: List[float] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate confluence result."""
        self.bullish_score = max(0.0, min(100.0, self.bullish_score))
        self.bearish_score = max(0.0, min(100.0, self.bearish_score))
        self.neutral_probability = max(0.0, min(100.0, self.neutral_probability))
        self.confidence_percentage = max(0.0, min(100.0, self.confidence_percentage))
        
        # Normalize to sum ~100
        total = self.bullish_score + self.bearish_score + self.neutral_probability
        if total > 0:
            factor = 100.0 / total
            self.bullish_score *= factor
            self.bearish_score *= factor
            self.neutral_probability *= factor


class ConfluenceEngine:
    """
    Aggregates analysis signals and computes confluence scores.
    
    Handles signal weighting, filters low-confidence patterns,
    computes normalized bullish/bearish/neutral probabilities.
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """Initialize confluence engine."""
        self.logger = logger or Logger.get_instance()
    
    def calculate_confluence(
        self,
        signals: List[Signal],
        min_confidence: float = 40.0
    ) -> ConfluenceResult:
        """
        Calculate confluence from list of signals.
        
        Args:
            signals: List of Signal objects
            min_confidence: Minimum confidence threshold (0-100)
        
        Returns:
            ConfluenceResult with aggregated scores
        """
        # Filter low-confidence signals
        valid_signals = [
            s for s in signals
            if s.confidence >= min_confidence
        ]
        
        if not valid_signals:
            # No valid signals
            return ConfluenceResult(
                bullish_score=0.0,
                bearish_score=0.0,
                neutral_probability=100.0,
                confidence_percentage=0.0,
                market_bias="Neutral",
                signal_count=0,
                bullish_signals=0,
                bearish_signals=0,
                neutral_signals=0,
                top_factors=[]
            )
        
        # Compute weighted signals
        weighted_signals = [s.get_weighted_signal() for s in valid_signals]
        
        # Calculate bullish and bearish scores
        bullish_signals = [s for s in valid_signals if s.signal_type == SignalType.BULLISH]
        bearish_signals = [s for s in valid_signals if s.signal_type == SignalType.BEARISH]
        neutral_signals = [s for s in valid_signals if s.signal_type == SignalType.NEUTRAL]
        
        bullish_score = self._compute_score(bullish_signals)
        bearish_score = self._compute_score(bearish_signals)
        neutral_probability = self._compute_neutral(neutral_signals, len(valid_signals))
        
        # Compute overall confidence
        confidence = self._compute_confidence(valid_signals)
        
        # Get top contributing factors
        top_factors = self._get_top_factors(valid_signals, top_n=5)
        
        # Determine market bias
        market_bias = self._determine_bias(bullish_score, bearish_score, confidence)
        
        result = ConfluenceResult(
            bullish_score=bullish_score,
            bearish_score=bearish_score,
            neutral_probability=neutral_probability,
            confidence_percentage=confidence,
            market_bias=market_bias,
            signal_count=len(valid_signals),
            bullish_signals=len(bullish_signals),
            bearish_signals=len(bearish_signals),
            neutral_signals=len(neutral_signals),
            top_factors=top_factors,
            weighted_signals=weighted_signals
        )
        
        return result
    
    def _compute_score(self, signals: List[Signal]) -> float:
        """
        Compute bullish or bearish score from signals.
        
        Score = average of (confidence * weight) across signals.
        """
        if not signals:
            return 0.0
        
        scores = []
        for signal in signals:
            score = signal.confidence * signal.get_effective_weight()
            scores.append(score)
        
        return statistics.mean(scores) if scores else 0.0
    
    def _compute_neutral(self, neutral_signals: List[Signal], total_signals: int) -> float:
        """
        Compute neutral probability.
        
        Based on neutral signals and distribution of bullish/bearish.
        """
        if total_signals == 0:
            return 100.0
        
        neutral_count = len(neutral_signals)
        neutral_probability = (neutral_count / total_signals) * 50.0  # Max 50%
        
        return min(50.0, neutral_probability)
    
    def _compute_confidence(self, signals: List[Signal]) -> float:
        """
        Compute overall confidence percentage.
        
        Based on signal count, average confidence, and category diversity.
        """
        if not signals:
            return 0.0
        
        # Average confidence
        avg_confidence = statistics.mean([s.confidence for s in signals])
        
        # Signal count factor (more signals = higher confidence, but diminishing returns)
        signal_count_factor = min(1.0, len(signals) / 20.0)
        
        # Category diversity factor (signals from different categories = higher confidence)
        categories = set(s.category for s in signals)
        diversity_factor = min(1.0, len(categories) / 8.0)
        
        confidence = avg_confidence * (0.5 + 0.25 * signal_count_factor + 0.25 * diversity_factor)
        
        return min(100.0, confidence)
    
    def _get_top_factors(self, signals: List[Signal], top_n: int = 5) -> List[Tuple[str, float]]:
        """Get top contributing factors sorted by impact."""
        # Score each signal by impact
        scored = [
            (s.source, s.confidence * s.get_effective_weight())
            for s in signals
        ]
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N
        return scored[:top_n]
    
    def _determine_bias(
        self,
        bullish: float,
        bearish: float,
        confidence: float
    ) -> str:
        """Determine market bias label."""
        if confidence < 30:
            return "Neutral"
        
        diff = bullish - bearish
        abs_diff = abs(diff)
        
        if abs_diff < 10:
            return "Neutral"
        elif abs_diff < 25:
            return "Bullish" if bullish > bearish else "Bearish"
        else:
            return "Strong Bullish" if bullish > bearish else "Strong Bearish"
    
    def merge_confluences(
        self,
        confluences: List[ConfluenceResult],
        weights: Optional[List[float]] = None
    ) -> ConfluenceResult:
        """
        Merge multiple confluence results (e.g., across timeframes).
        
        Args:
            confluences: List of ConfluenceResult objects
            weights: Optional weights for each confluence (default: equal)
        
        Returns:
            Merged ConfluenceResult
        """
        if not confluences:
            raise ValueError("No confluences to merge")
        
        if weights is None:
            weights = [1.0] * len(confluences)
        
        if len(weights) != len(confluences):
            raise ValueError("Weights must match confluences length")
        
        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Weighted average of scores
        bullish_avg = sum(
            c.bullish_score * w for c, w in zip(confluences, weights)
        )
        bearish_avg = sum(
            c.bearish_score * w for c, w in zip(confluences, weights)
        )
        neutral_avg = sum(
            c.neutral_probability * w for c, w in zip(confluences, weights)
        )
        confidence_avg = sum(
            c.confidence_percentage * w for c, w in zip(confluences, weights)
        )
        
        # Merge top factors
        all_factors = []
        for conf in confluences:
            all_factors.extend(conf.top_factors)
        
        all_factors.sort(key=lambda x: x[1], reverse=True)
        top_factors = all_factors[:5]
        
        # Determine bias
        market_bias = self._determine_bias(bullish_avg, bearish_avg, confidence_avg)
        
        # Total signals
        total_signals = sum(c.signal_count for c in confluences)
        total_bullish = sum(c.bullish_signals for c in confluences)
        total_bearish = sum(c.bearish_signals for c in confluences)
        total_neutral = sum(c.neutral_signals for c in confluences)
        
        return ConfluenceResult(
            bullish_score=bullish_avg,
            bearish_score=bearish_avg,
            neutral_probability=neutral_avg,
            confidence_percentage=confidence_avg,
            market_bias=market_bias,
            signal_count=total_signals,
            bullish_signals=total_bullish,
            bearish_signals=total_bearish,
            neutral_signals=total_neutral,
            top_factors=top_factors
        )
