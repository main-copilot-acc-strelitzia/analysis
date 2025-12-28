"""
Multi-Timeframe Analysis Orchestrator.

Runs analysis on multiple selected timeframes, computes timeframe-specific bias,
aggregates confluence across timeframes with proper weighting.
"""

from typing import List, Dict, Optional, Tuple
import pandas as pd

from core.logger import Logger
from analysis.confluence_engine import ConfluenceEngine, ConfluenceResult, Signal, SignalType, SignalCategory
from mt5.market_data import MarketDataManager


class TimeframeWeight:
    """Default timeframe weights for multi-timeframe analysis."""
    
    # Higher timeframes have stronger influence on bias
    WEIGHTS = {
        'M1': 0.6,
        'M5': 0.7,
        'M15': 0.8,
        'M30': 0.85,
        'H1': 0.9,
        'H4': 1.0,    # Reference timeframe
        'D1': 1.1,    # Higher timeframes stronger
        'W1': 1.2,
        'MN1': 1.3
    }
    
    @staticmethod
    def normalize(weights: Dict[str, float]) -> Dict[str, float]:
        """Normalize weights to sum to 1."""
        total = sum(weights.values())
        if total <= 0:
            return weights
        return {tf: w / total for tf, w in weights.items()}


class TimeframeBias:
    """Computed timeframe-specific bias."""
    
    def __init__(
        self,
        timeframe: str,
        bullish_score: float,
        bearish_score: float,
        confidence: float,
        weight: float = 1.0
    ):
        self.timeframe = timeframe
        self.bullish_score = bullish_score
        self.bearish_score = bearish_score
        self.confidence = confidence
        self.weight = weight
        
        # Compute bias direction
        diff = bullish_score - bearish_score
        if diff > 25:
            self.bias_direction = "Strong Bullish"
        elif diff > 10:
            self.bias_direction = "Bullish"
        elif diff < -25:
            self.bias_direction = "Strong Bearish"
        elif diff < -10:
            self.bias_direction = "Bearish"
        else:
            self.bias_direction = "Neutral"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'timeframe': self.timeframe,
            'bullish': self.bullish_score,
            'bearish': self.bearish_score,
            'confidence': self.confidence,
            'weight': self.weight,
            'bias': self.bias_direction
        }


class MultiTimeframeResult:
    """Result of multi-timeframe analysis."""
    
    def __init__(
        self,
        symbol: str,
        timeframes: List[TimeframeBias]
    ):
        self.symbol = symbol
        self.timeframes = timeframes
        
        # Compute aggregated scores
        self._compute_aggregates()
    
    def _compute_aggregates(self):
        """Compute weighted aggregates across timeframes."""
        if not self.timeframes:
            self.overall_bullish = 0.0
            self.overall_bearish = 0.0
            self.overall_confidence = 0.0
            self.overall_bias = "Neutral"
            self.confluence = None
            return
        
        # Normalize weights
        weights = {tf.timeframe: tf.weight for tf in self.timeframes}
        normalized_weights = TimeframeWeight.normalize(weights)
        
        # Weighted average of scores
        total_weight = sum(normalized_weights.values())
        self.overall_bullish = sum(
            tf.bullish_score * normalized_weights[tf.timeframe]
            for tf in self.timeframes
        ) / total_weight if total_weight > 0 else 0.0
        
        self.overall_bearish = sum(
            tf.bearish_score * normalized_weights[tf.timeframe]
            for tf in self.timeframes
        ) / total_weight if total_weight > 0 else 0.0
        
        self.overall_confidence = sum(
            tf.confidence * normalized_weights[tf.timeframe]
            for tf in self.timeframes
        ) / total_weight if total_weight > 0 else 0.0
        
        # Determine overall bias
        diff = self.overall_bullish - self.overall_bearish
        if diff > 25:
            self.overall_bias = "Strong Bullish"
        elif diff > 10:
            self.overall_bias = "Bullish"
        elif diff < -25:
            self.overall_bias = "Strong Bearish"
        elif diff < -10:
            self.overall_bias = "Bearish"
        else:
            self.overall_bias = "Neutral"
        
        # Confluence = how aligned are timeframes
        if len(self.timeframes) > 1:
            bias_alignments = [
                1.0 if tf.bias_direction == self.overall_bias else 0.5
                for tf in self.timeframes
            ]
            self.confluence = sum(bias_alignments) / len(bias_alignments) * 100
        else:
            self.confluence = 100.0 if self.timeframes else 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'overall_bullish': self.overall_bullish,
            'overall_bearish': self.overall_bearish,
            'overall_confidence': self.overall_confidence,
            'overall_bias': self.overall_bias,
            'timeframe_confluence': self.confluence,
            'timeframes': [tf.to_dict() for tf in self.timeframes]
        }


class MultiTimeframeOrchestrator:
    """
    Orchestrates analysis across multiple timeframes.
    
    Runs analysis on selected timeframes, computes bias per timeframe,
    aggregates across timeframes with proper weighting.
    """
    
    def __init__(
        self,
        market_data_manager: MarketDataManager,
        confluence_engine: ConfluenceEngine,
        analyzer: callable,
        logger: Optional[Logger] = None
    ):
        """
        Initialize multi-timeframe orchestrator.
        
        Args:
            market_data_manager: MarketDataManager instance
            confluence_engine: ConfluenceEngine instance
            analyzer: Analysis function taking (symbol, timeframe, candles) -> signals list
            logger: Logger instance
        """
        self.market_data_manager = market_data_manager
        self.confluence_engine = confluence_engine
        self.analyzer = analyzer
        self.logger = logger or Logger.get_instance()
    
    def analyze_multiple_timeframes(
        self,
        symbol: str,
        timeframes: List[str],
        timeframe_weights: Optional[Dict[str, float]] = None
    ) -> Optional[MultiTimeframeResult]:
        """
        Analyze symbol across multiple timeframes.
        
        Args:
            symbol: Symbol name
            timeframes: List of timeframe strings
            timeframe_weights: Optional custom weights per timeframe
            
        Returns:
            MultiTimeframeResult with aggregated analysis or None on error
        """
        if not timeframes:
            self.logger.error("No timeframes specified")
            return None
        
        # Use default weights if not provided
        if timeframe_weights is None:
            timeframe_weights = {tf: TimeframeWeight.WEIGHTS.get(tf, 1.0) for tf in timeframes}
        
        # Fetch market data for all timeframes
        self.logger.debug(f"Fetching data for {symbol} on {len(timeframes)} timeframes")
        candles_data = self.market_data_manager.get_multiple_timeframes(symbol, timeframes)
        
        # Analyze each timeframe
        timeframe_biases = []
        for tf in timeframes:
            candles = candles_data.get(tf)
            
            if candles is None or len(candles) == 0:
                self.logger.warning(f"No candles for {symbol} {tf}")
                continue
            
            try:
                # Run analysis
                signals = self.analyzer(symbol, tf, candles)
                
                if not signals:
                    self.logger.debug(f"No signals for {symbol} {tf}")
                    continue
                
                # Calculate confluence for this timeframe
                confluence = self.confluence_engine.calculate_confluence(signals)
                
                # Create timeframe bias
                weight = timeframe_weights.get(tf, 1.0)
                bias = TimeframeBias(
                    timeframe=tf,
                    bullish_score=confluence.bullish_score,
                    bearish_score=confluence.bearish_score,
                    confidence=confluence.confidence_percentage,
                    weight=weight
                )
                timeframe_biases.append(bias)
                
                self.logger.debug(
                    f"{symbol} {tf}: Bullish={confluence.bullish_score:.1f}, "
                    f"Bearish={confluence.bearish_score:.1f}, Conf={confluence.confidence_percentage:.1f}%"
                )
            
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol} {tf}: {e}")
                continue
        
        if not timeframe_biases:
            self.logger.error(f"Failed to analyze {symbol} on any timeframe")
            return None
        
        # Create multi-timeframe result
        result = MultiTimeframeResult(symbol, timeframe_biases)
        
        self.logger.info(
            f"Multi-timeframe analysis complete for {symbol}: "
            f"Overall={result.overall_bias}, Confluence={result.confluence:.1f}%"
        )
        
        return result
    
    def compute_higher_timeframe_bias(
        self,
        symbol: str,
        lower_timeframes: List[str],
        higher_timeframes: List[str]
    ) -> Dict[str, float]:
        """
        Compute bias of higher timeframes vs lower timeframes.
        
        Used for identifying higher-timeframe structure vs lower-timeframe execution.
        
        Args:
            symbol: Symbol name
            lower_timeframes: List of lower timeframe strings (e.g., ['M5', 'M15'])
            higher_timeframes: List of higher timeframe strings (e.g., ['H1', 'H4'])
            
        Returns:
            Dict with analysis of timeframe alignment
        """
        # Analyze higher timeframes
        higher_result = self.analyze_multiple_timeframes(symbol, higher_timeframes)
        
        # Analyze lower timeframes
        lower_result = self.analyze_multiple_timeframes(symbol, lower_timeframes)
        
        if not higher_result or not lower_result:
            return {
                'aligned': False,
                'higher_bias': 'Unknown',
                'lower_bias': 'Unknown',
                'alignment_score': 0.0
            }
        
        # Check alignment
        higher_is_bullish = higher_result.overall_bullish > higher_result.overall_bearish
        lower_is_bullish = lower_result.overall_bullish > lower_result.overall_bearish
        
        aligned = higher_is_bullish == lower_is_bullish
        
        # Alignment score (0-100)
        if aligned:
            # Both bullish or both bearish
            alignment_score = 80.0 + min(20.0, abs(
                higher_result.overall_bullish - lower_result.overall_bullish
            ) / 5)
        else:
            # Divergent
            alignment_score = 30.0 - abs(
                higher_result.overall_bullish - lower_result.overall_bullish
            ) / 5
        
        alignment_score = max(0.0, min(100.0, alignment_score))
        
        return {
            'aligned': aligned,
            'higher_bias': higher_result.overall_bias,
            'lower_bias': lower_result.overall_bias,
            'alignment_score': alignment_score,
            'higher_confidence': higher_result.overall_confidence,
            'lower_confidence': lower_result.overall_confidence
        }
    
    def get_sweet_spot_timeframe(
        self,
        symbol: str,
        timeframes: Optional[List[str]] = None
    ) -> Optional[Tuple[str, float]]:
        """
        Find timeframe with highest confluence and confidence.
        
        Identifies the "sweet spot" timeframe for analysis.
        
        Args:
            symbol: Symbol name
            timeframes: List of timeframes to evaluate (default: all standard)
            
        Returns:
            Tuple of (best_timeframe, confidence_score) or None
        """
        if timeframes is None:
            timeframes = ['M15', 'M30', 'H1', 'H4', 'D1']
        
        result = self.analyze_multiple_timeframes(symbol, timeframes)
        
        if not result or not result.timeframes:
            return None
        
        # Score each timeframe
        best_tf = None
        best_score = 0.0
        
        for tf_bias in result.timeframes:
            # Score = confidence * confluence alignment
            score = tf_bias.confidence * (result.confluence / 100.0)
            
            if score > best_score:
                best_score = score
                best_tf = tf_bias.timeframe
        
        if best_tf:
            self.logger.info(f"Sweet spot timeframe for {symbol}: {best_tf} (score: {best_score:.1f})")
        
        return (best_tf, best_score) if best_tf else None
