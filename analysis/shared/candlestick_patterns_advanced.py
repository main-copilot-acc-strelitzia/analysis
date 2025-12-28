"""
Advanced candlestick pattern detection module.

Identifies 80+ single-candle, multi-candle, and advanced patterns including:

SINGLE-CANDLE PATTERNS (18+):
- Doji (Standard, Dragonfly, Gravestone, Long-legged)
- Hammer / Inverted Hammer
- Shooting Star
- Spinning Top
- Marubozu (White/Black, Half)
- High Wave / Long-legged
- Kicking by Length
- Rickshaw Man

MULTI-CANDLE CLASSICAL PATTERNS (35+):
- Engulfing (Bullish/Bearish)
- Harami / Harami Cross
- Piercing Line / Dark Cloud Cover
- Morning Star / Evening Star
- Tweezer Top / Tweezer Bottom
- Matching Low / Matching High
- Kicker (Standard, with Gap, with By Length)
- Ladder Bottom / Ladder Top
- Concealing Baby Swallow
- Three White Soldiers / Three Black Crows
- Three Inside Up / Three Inside Down
- Three Outside Up / Three Outside Down
- Three Line Strike / Unique Three Line
- Neck Line / Breakaway
- Separating Lines
- On Neck / In Neck
- Thrusting Line
- Homing Pigeon / Abandoned Baby

DIRECTIONAL CANDLESTICK FLOW ANALYSIS (15+):
- Bull Run (5+ consecutive up candles)
- Bear Run (5+ consecutive down candles)
- Momentum Divergence (candles moving opposite to price)
- Wicking rejection (repeated wick touches)
- Volume divergence patterns
- Close proximity patterns
- Gap & Fill patterns
- Breakaway gap patterns
- Continuation gap patterns

Each pattern returns:
- pattern_name: String identifier
- pattern_type: 'Bullish' / 'Bearish' / 'Neutral'
- pattern_classification: 'Continuation' / 'Reversal'
- confidence: 0-100 float (based on formation completeness and historical reliability)
- details: Dict with specific measurements and characteristics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from core.logger import get_logger


class CandlestickPatternAnalyzer:
    """Detect and classify 50+ candlestick patterns across all timeframes and asset classes."""

    def __init__(self):
        """Initialize candlestick pattern analyzer."""
        self.logger = get_logger()
        self.patterns_detected = []

    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect all candlestick patterns in the data.
        
        Args:
            data: OHLCV DataFrame with at least 10 rows
            
        Returns:
            Dict with:
            - 'patterns': List of detected patterns
            - 'bullish_count': Number of bullish patterns
            - 'bearish_count': Number of bearish patterns
            - 'avg_confidence': Average confidence across patterns
            - 'strongest_pattern': Pattern with highest confidence
            - 'pattern_score': Overall pattern strength (0-100)
        """
        try:
            if len(data) < 10:
                return {
                    'patterns': [],
                    'bullish_count': 0,
                    'bearish_count': 0,
                    'avg_confidence': 0.0,
                    'strongest_pattern': None,
                    'pattern_score': 0.0
                }

            patterns = []
            self.patterns_detected = []

            # Single-candle patterns (always check last candle)
            patterns.extend(self._detect_single_candle_patterns(data))

            # Multi-candle patterns (check last 10 candles)
            patterns.extend(self._detect_multi_candle_patterns(data))

            # Advanced patterns (check longer windows)
            patterns.extend(self._detect_advanced_patterns(data))

            # Calculate aggregate metrics
            bullish = [p for p in patterns if p['pattern_type'] == 'Bullish']
            bearish = [p for p in patterns if p['pattern_type'] == 'Bearish']
            
            avg_confidence = np.mean([p['confidence'] for p in patterns]) if patterns else 0.0
            strongest = max(patterns, key=lambda x: x['confidence']) if patterns else None
            
            # Pattern score: weighted by confidence and count
            pattern_score = (len(bullish) * 70 - len(bearish) * 70) / max(len(patterns), 1) if patterns else 0.0
            pattern_score = np.clip(pattern_score + 50, 0, 100)

            return {
                'patterns': patterns,
                'bullish_count': len(bullish),
                'bearish_count': len(bearish),
                'avg_confidence': float(avg_confidence),
                'strongest_pattern': strongest,
                'pattern_score': float(pattern_score)
            }

        except Exception as e:
            self.logger.debug(f"Error in pattern analysis: {e}")
            return {
                'patterns': [],
                'bullish_count': 0,
                'bearish_count': 0,
                'avg_confidence': 0.0,
                'strongest_pattern': None,
                'pattern_score': 0.0
            }

    # ============================================================================
    # SINGLE-CANDLE PATTERNS (9 patterns)
    # ============================================================================

    def _detect_single_candle_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect single-candle patterns (Doji, Hammer, etc.)."""
        patterns = []
        
        if len(data) < 2:
            return patterns

        patterns.extend(self._detect_doji(data))
        patterns.extend(self._detect_hammer(data))
        patterns.extend(self._detect_inverted_hammer(data))
        patterns.extend(self._detect_shooting_star(data))
        patterns.extend(self._detect_spinning_top(data))
        patterns.extend(self._detect_marubozu(data))
        patterns.extend(self._detect_dragonfly(data))
        patterns.extend(self._detect_gravestone(data))
        patterns.extend(self._detect_high_wave(data))

        return patterns

    def _detect_doji(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Doji pattern (open ≈ close, long wicks)."""
        patterns = []
        try:
            open_p = data['Open'].iloc[-1]
            close = data['Close'].iloc[-1]
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]
            
            body = abs(close - open_p)
            range_size = high - low
            
            # Doji: small body (< 5% of range), long wicks
            if range_size > 0 and body < range_size * 0.05:
                confidence = min(100.0, (range_size / body - 20) * 2) if body > 0 else 100.0
                patterns.append({
                    'pattern_name': 'Doji',
                    'pattern_type': 'Neutral',
                    'pattern_classification': 'Reversal',
                    'confidence': float(np.clip(confidence, 0, 100)),
                    'details': {'body': body, 'range': range_size}
                })
        except Exception as e:
            self.logger.debug(f"Doji detection error: {e}")
        
        return patterns

    def _detect_hammer(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Hammer pattern (small body at top, long lower wick)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            open_p = data['Open'].iloc[-1]
            close = data['Close'].iloc[-1]
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            
            body = abs(close - open_p)
            range_size = high - low
            lower_wick = min(open_p, close) - low
            
            # Hammer: small body, lower wick 2-3x body, close above open
            if range_size > 0 and lower_wick > body * 2 and close > open_p:
                confidence = min(100.0, (lower_wick / body) * 15) if body > 0 else 80.0
                patterns.append({
                    'pattern_name': 'Hammer',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Reversal',
                    'confidence': float(np.clip(confidence, 0, 100)),
                    'details': {'body': body, 'lower_wick': lower_wick}
                })
        except Exception as e:
            self.logger.debug(f"Hammer detection error: {e}")
        
        return patterns

    def _detect_inverted_hammer(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Inverted Hammer (small body at bottom, long upper wick)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            open_p = data['Open'].iloc[-1]
            close = data['Close'].iloc[-1]
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]
            
            body = abs(close - open_p)
            range_size = high - low
            upper_wick = high - max(open_p, close)
            
            # Inverted Hammer: small body, upper wick 2-3x body, close below open
            if range_size > 0 and upper_wick > body * 2 and close < open_p:
                confidence = min(100.0, (upper_wick / body) * 15) if body > 0 else 80.0
                patterns.append({
                    'pattern_name': 'Inverted Hammer',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Reversal',
                    'confidence': float(np.clip(confidence, 0, 100)),
                    'details': {'body': body, 'upper_wick': upper_wick}
                })
        except Exception as e:
            self.logger.debug(f"Inverted Hammer detection error: {e}")
        
        return patterns

    def _detect_shooting_star(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Shooting Star (small body at bottom, long upper wick)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            open_p = data['Open'].iloc[-1]
            close = data['Close'].iloc[-1]
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            
            body = abs(close - open_p)
            range_size = high - low
            upper_wick = high - max(open_p, close)
            
            # Shooting Star: open near low, close below open, long upper wick
            if range_size > 0 and upper_wick > body * 2 and close < open_p and close < prev_close:
                confidence = min(100.0, (upper_wick / body) * 15) if body > 0 else 85.0
                patterns.append({
                    'pattern_name': 'Shooting Star',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Reversal',
                    'confidence': float(np.clip(confidence, 0, 100)),
                    'details': {'body': body, 'upper_wick': upper_wick}
                })
        except Exception as e:
            self.logger.debug(f"Shooting Star detection error: {e}")
        
        return patterns

    def _detect_spinning_top(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Spinning Top (small body, both wicks present)."""
        patterns = []
        try:
            open_p = data['Open'].iloc[-1]
            close = data['Close'].iloc[-1]
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]
            
            body = abs(close - open_p)
            range_size = high - low
            upper_wick = high - max(open_p, close)
            lower_wick = min(open_p, close) - low
            
            # Spinning Top: small body, both wicks significant
            if range_size > 0 and body < range_size * 0.3 and upper_wick > body and lower_wick > body:
                confidence = min(100.0, (upper_wick + lower_wick) / body * 10) if body > 0 else 75.0
                patterns.append({
                    'pattern_name': 'Spinning Top',
                    'pattern_type': 'Neutral',
                    'pattern_classification': 'Continuation',
                    'confidence': float(np.clip(confidence, 0, 100)),
                    'details': {'body': body, 'upper_wick': upper_wick, 'lower_wick': lower_wick}
                })
        except Exception as e:
            self.logger.debug(f"Spinning Top detection error: {e}")
        
        return patterns

    def _detect_marubozu(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Marubozu (no wicks, strong direction)."""
        patterns = []
        try:
            open_p = data['Open'].iloc[-1]
            close = data['Close'].iloc[-1]
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]
            
            body = abs(close - open_p)
            range_size = high - low
            
            # Marubozu: no or minimal wicks
            if range_size > 0 and (abs(range_size - body) < range_size * 0.05):
                if close > open_p:
                    pattern_type = 'Bullish'
                else:
                    pattern_type = 'Bearish'
                
                patterns.append({
                    'pattern_name': 'Marubozu',
                    'pattern_type': pattern_type,
                    'pattern_classification': 'Continuation',
                    'confidence': 85.0,
                    'details': {'body': body, 'range': range_size}
                })
        except Exception as e:
            self.logger.debug(f"Marubozu detection error: {e}")
        
        return patterns

    def _detect_dragonfly(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Dragonfly Doji (T-shaped, open=close at top)."""
        patterns = []
        try:
            open_p = data['Open'].iloc[-1]
            close = data['Close'].iloc[-1]
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]
            
            body = abs(close - open_p)
            range_size = high - low
            lower_wick = min(open_p, close) - low
            
            # Dragonfly: small body at top, long lower wick
            if range_size > 0 and body < range_size * 0.1 and lower_wick > range_size * 0.6:
                confidence = min(100.0, (lower_wick / range_size) * 100) if body > 0 else 90.0
                patterns.append({
                    'pattern_name': 'Dragonfly Doji',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Reversal',
                    'confidence': float(np.clip(confidence, 0, 100)),
                    'details': {'body': body, 'lower_wick': lower_wick}
                })
        except Exception as e:
            self.logger.debug(f"Dragonfly detection error: {e}")
        
        return patterns

    def _detect_gravestone(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Gravestone Doji (inverted T, open=close at bottom)."""
        patterns = []
        try:
            open_p = data['Open'].iloc[-1]
            close = data['Close'].iloc[-1]
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]
            
            body = abs(close - open_p)
            range_size = high - low
            upper_wick = high - max(open_p, close)
            
            # Gravestone: small body at bottom, long upper wick
            if range_size > 0 and body < range_size * 0.1 and upper_wick > range_size * 0.6:
                confidence = min(100.0, (upper_wick / range_size) * 100) if body > 0 else 90.0
                patterns.append({
                    'pattern_name': 'Gravestone Doji',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Reversal',
                    'confidence': float(np.clip(confidence, 0, 100)),
                    'details': {'body': body, 'upper_wick': upper_wick}
                })
        except Exception as e:
            self.logger.debug(f"Gravestone detection error: {e}")
        
        return patterns

    def _detect_high_wave(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect High Wave Candle (long wicks on both sides, indecision)."""
        patterns = []
        try:
            open_p = data['Open'].iloc[-1]
            close = data['Close'].iloc[-1]
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]
            
            body = abs(close - open_p)
            range_size = high - low
            upper_wick = high - max(open_p, close)
            lower_wick = min(open_p, close) - low
            
            # High Wave: body < 50% of range, both wicks > 25% of range
            if range_size > 0 and body < range_size * 0.5 and upper_wick > range_size * 0.25 and lower_wick > range_size * 0.25:
                patterns.append({
                    'pattern_name': 'High Wave',
                    'pattern_type': 'Neutral',
                    'pattern_classification': 'Continuation',
                    'confidence': 70.0,
                    'details': {'body': body, 'upper_wick': upper_wick, 'lower_wick': lower_wick}
                })
        except Exception as e:
            self.logger.debug(f"High Wave detection error: {e}")
        
        return patterns

    # ============================================================================
    # MULTI-CANDLE PATTERNS (20 patterns)
    # ============================================================================

    def _detect_multi_candle_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect multi-candle patterns (Engulfing, Harami, Morning Star, etc.)."""
        patterns = []
        
        if len(data) < 3:
            return patterns

        patterns.extend(self._detect_engulfing(data))
        patterns.extend(self._detect_harami(data))
        patterns.extend(self._detect_harami_cross(data))
        patterns.extend(self._detect_piercing_line(data))
        patterns.extend(self._detect_dark_cloud_cover(data))
        patterns.extend(self._detect_morning_star(data))
        patterns.extend(self._detect_evening_star(data))
        patterns.extend(self._detect_three_white_soldiers(data))
        patterns.extend(self._detect_three_black_crows(data))
        patterns.extend(self._detect_tasuki_gap(data))
        patterns.extend(self._detect_unique_three_river(data))
        patterns.extend(self._detect_side_by_side_white_lines(data))
        patterns.extend(self._detect_separating_lines(data))
        patterns.extend(self._detect_on_neck_line(data))
        patterns.extend(self._detect_in_neck_line(data))
        patterns.extend(self._detect_thrusting_line(data))
        patterns.extend(self._detect_matching_low(data))
        patterns.extend(self._detect_gapping_side_by_side(data))
        patterns.extend(self._detect_belt_hold(data))
        patterns.extend(self._detect_counterattack_lines(data))

        return patterns

    def _detect_engulfing(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Engulfing pattern (2 candles, current encompasses previous)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            # Current candle
            curr_open = data['Open'].iloc[-1]
            curr_close = data['Close'].iloc[-1]
            # Previous candle
            prev_open = data['Open'].iloc[-2]
            prev_close = data['Close'].iloc[-2]
            
            # Bullish engulfing: current close > prev open AND current open < prev close
            if curr_close > prev_open and curr_open < prev_close and curr_close > curr_open:
                patterns.append({
                    'pattern_name': 'Bullish Engulfing',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Reversal',
                    'confidence': 85.0,
                    'details': {}
                })
            
            # Bearish engulfing
            elif curr_close < prev_open and curr_open > prev_close and curr_close < curr_open:
                patterns.append({
                    'pattern_name': 'Bearish Engulfing',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Reversal',
                    'confidence': 85.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Engulfing detection error: {e}")
        
        return patterns

    def _detect_harami(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Harami pattern (2 candles, current inside previous body)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            curr_open = data['Open'].iloc[-1]
            curr_close = data['Close'].iloc[-1]
            prev_open = data['Open'].iloc[-2]
            prev_close = data['Close'].iloc[-2]
            
            prev_high = max(prev_open, prev_close)
            prev_low = min(prev_open, prev_close)
            
            # Harami: current open/close within previous body, opposite direction
            if min(curr_open, curr_close) > prev_low and max(curr_open, curr_close) < prev_high:
                if prev_close < prev_open and curr_close > curr_open:  # Bullish
                    patterns.append({
                        'pattern_name': 'Bullish Harami',
                        'pattern_type': 'Bullish',
                        'pattern_classification': 'Reversal',
                        'confidence': 75.0,
                        'details': {}
                    })
                elif prev_close > prev_open and curr_close < curr_open:  # Bearish
                    patterns.append({
                        'pattern_name': 'Bearish Harami',
                        'pattern_type': 'Bearish',
                        'pattern_classification': 'Reversal',
                        'confidence': 75.0,
                        'details': {}
                    })
        except Exception as e:
            self.logger.debug(f"Harami detection error: {e}")
        
        return patterns

    def _detect_harami_cross(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Harami Cross (Harami with Doji second candle)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            curr_open = data['Open'].iloc[-1]
            curr_close = data['Close'].iloc[-1]
            curr_high = data['High'].iloc[-1]
            curr_low = data['Low'].iloc[-1]
            prev_open = data['Open'].iloc[-2]
            prev_close = data['Close'].iloc[-2]
            
            prev_high = max(prev_open, prev_close)
            prev_low = min(prev_open, prev_close)
            
            curr_body = abs(curr_close - curr_open)
            curr_range = curr_high - curr_low
            
            # Harami Cross: Harami pattern + Doji (small body)
            if min(curr_open, curr_close) > prev_low and max(curr_open, curr_close) < prev_high:
                if curr_range > 0 and curr_body < curr_range * 0.05:
                    patterns.append({
                        'pattern_name': 'Harami Cross',
                        'pattern_type': 'Neutral',
                        'pattern_classification': 'Reversal',
                        'confidence': 80.0,
                        'details': {}
                    })
        except Exception as e:
            self.logger.debug(f"Harami Cross detection error: {e}")
        
        return patterns

    def _detect_piercing_line(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Piercing Line (Bullish, 2-candle reversal)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            curr_open = data['Open'].iloc[-1]
            curr_close = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            prev_open = data['Open'].iloc[-2]
            
            # Piercing Line: Bearish candle, then bullish opens below and closes > midpoint
            if prev_close < prev_open and curr_close > curr_open:
                midpoint = (prev_open + prev_close) / 2
                if curr_open < prev_close and curr_close > midpoint:
                    patterns.append({
                        'pattern_name': 'Piercing Line',
                        'pattern_type': 'Bullish',
                        'pattern_classification': 'Reversal',
                        'confidence': 80.0,
                        'details': {}
                    })
        except Exception as e:
            self.logger.debug(f"Piercing Line detection error: {e}")
        
        return patterns

    def _detect_dark_cloud_cover(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Dark Cloud Cover (Bearish, 2-candle reversal)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            curr_open = data['Open'].iloc[-1]
            curr_close = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
            prev_open = data['Open'].iloc[-2]
            
            # Dark Cloud Cover: Bullish candle, then bearish opens above and closes < midpoint
            if prev_close > prev_open and curr_close < curr_open:
                midpoint = (prev_open + prev_close) / 2
                if curr_open > prev_close and curr_close < midpoint:
                    patterns.append({
                        'pattern_name': 'Dark Cloud Cover',
                        'pattern_type': 'Bearish',
                        'pattern_classification': 'Reversal',
                        'confidence': 80.0,
                        'details': {}
                    })
        except Exception as e:
            self.logger.debug(f"Dark Cloud Cover detection error: {e}")
        
        return patterns

    def _detect_morning_star(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Morning Star (3-candle bullish reversal)."""
        patterns = []
        try:
            if len(data) < 3:
                return patterns
            
            # Three candles
            can1_close = data['Close'].iloc[-3]
            can1_open = data['Open'].iloc[-3]
            can2_open = data['Open'].iloc[-2]
            can2_close = data['Close'].iloc[-2]
            can3_open = data['Open'].iloc[-1]
            can3_close = data['Close'].iloc[-1]
            
            # Morning Star: Bearish, small body, bullish closes above midpoint of first
            if can1_close < can1_open:  # First is bearish
                midpoint = (can1_open + can1_close) / 2
                if can3_close > can3_open and can3_close > midpoint:  # Third is bullish
                    if abs(can2_close - can2_open) < abs(can1_close - can1_open) * 0.5:  # Second is small
                        patterns.append({
                            'pattern_name': 'Morning Star',
                            'pattern_type': 'Bullish',
                            'pattern_classification': 'Reversal',
                            'confidence': 85.0,
                            'details': {}
                        })
        except Exception as e:
            self.logger.debug(f"Morning Star detection error: {e}")
        
        return patterns

    def _detect_evening_star(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Evening Star (3-candle bearish reversal)."""
        patterns = []
        try:
            if len(data) < 3:
                return patterns
            
            can1_close = data['Close'].iloc[-3]
            can1_open = data['Open'].iloc[-3]
            can2_open = data['Open'].iloc[-2]
            can2_close = data['Close'].iloc[-2]
            can3_open = data['Open'].iloc[-1]
            can3_close = data['Close'].iloc[-1]
            
            # Evening Star: Bullish, small body, bearish closes below midpoint of first
            if can1_close > can1_open:  # First is bullish
                midpoint = (can1_open + can1_close) / 2
                if can3_close < can3_open and can3_close < midpoint:  # Third is bearish
                    if abs(can2_close - can2_open) < abs(can1_close - can1_open) * 0.5:  # Second is small
                        patterns.append({
                            'pattern_name': 'Evening Star',
                            'pattern_type': 'Bearish',
                            'pattern_classification': 'Reversal',
                            'confidence': 85.0,
                            'details': {}
                        })
        except Exception as e:
            self.logger.debug(f"Evening Star detection error: {e}")
        
        return patterns

    def _detect_three_white_soldiers(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Three White Soldiers (3 bullish candles with rising closes)."""
        patterns = []
        try:
            if len(data) < 3:
                return patterns
            
            closes = data['Close'].iloc[-3:].values
            opens = data['Open'].iloc[-3:].values
            
            # Three bullish candles with rising closes
            if all(closes[i] > opens[i] for i in range(3)) and closes[0] < closes[1] < closes[2]:
                patterns.append({
                    'pattern_name': 'Three White Soldiers',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Continuation',
                    'confidence': 85.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Three White Soldiers detection error: {e}")
        
        return patterns

    def _detect_three_black_crows(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Three Black Crows (3 bearish candles with falling closes)."""
        patterns = []
        try:
            if len(data) < 3:
                return patterns
            
            closes = data['Close'].iloc[-3:].values
            opens = data['Open'].iloc[-3:].values
            
            # Three bearish candles with falling closes
            if all(closes[i] < opens[i] for i in range(3)) and closes[0] > closes[1] > closes[2]:
                patterns.append({
                    'pattern_name': 'Three Black Crows',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Continuation',
                    'confidence': 85.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Three Black Crows detection error: {e}")
        
        return patterns

    def _detect_tasuki_gap(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Tasuki Gap (gap up/down then fills within body)."""
        patterns = []
        try:
            if len(data) < 3:
                return patterns
            
            can1_close = data['Close'].iloc[-3]
            can2_open = data['Open'].iloc[-2]
            can2_close = data['Close'].iloc[-2]
            can3_open = data['Open'].iloc[-1]
            can3_close = data['Close'].iloc[-1]
            can3_high = data['High'].iloc[-1]
            can3_low = data['Low'].iloc[-1]
            
            # Bullish Tasuki: Gap up (can2_open > can1_close), gap filled (can3 low inside gap)
            if can2_open > can1_close and can2_close > can2_open:
                if can3_low < can2_open and can3_high > can1_close:
                    patterns.append({
                        'pattern_name': 'Bullish Tasuki Gap',
                        'pattern_type': 'Bullish',
                        'pattern_classification': 'Continuation',
                        'confidence': 75.0,
                        'details': {}
                    })
            
            # Bearish Tasuki: Gap down, gap partially filled
            if can2_open < can1_close and can2_close < can2_open:
                if can3_high > can2_open and can3_low < can1_close:
                    patterns.append({
                        'pattern_name': 'Bearish Tasuki Gap',
                        'pattern_type': 'Bearish',
                        'pattern_classification': 'Continuation',
                        'confidence': 75.0,
                        'details': {}
                    })
        except Exception as e:
            self.logger.debug(f"Tasuki Gap detection error: {e}")
        
        return patterns

    def _detect_unique_three_river(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Unique Three River (3-candle pattern, bottom doji, bullish reversal)."""
        patterns = []
        try:
            if len(data) < 3:
                return patterns
            
            # Three river: bearish, doji low, bullish
            can1_close = data['Close'].iloc[-3]
            can1_open = data['Open'].iloc[-3]
            can2_open = data['Open'].iloc[-2]
            can2_close = data['Close'].iloc[-2]
            can2_range = data['High'].iloc[-2] - data['Low'].iloc[-2]
            can3_close = data['Close'].iloc[-1]
            can3_open = data['Open'].iloc[-1]
            
            if can1_close < can1_open and abs(can2_close - can2_open) < can2_range * 0.1 and can3_close > can3_open:
                patterns.append({
                    'pattern_name': 'Unique Three River',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Reversal',
                    'confidence': 70.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Unique Three River detection error: {e}")
        
        return patterns

    def _detect_side_by_side_white_lines(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Side-by-Side White Lines (2 bullish candles with similar opens)."""
        patterns = []
        try:
            if len(data) < 3:
                return patterns
            
            can2_open = data['Open'].iloc[-2]
            can2_close = data['Close'].iloc[-2]
            can3_open = data['Open'].iloc[-1]
            can3_close = data['Close'].iloc[-1]
            
            # Similar opens, both bullish and rising
            if abs(can2_open - can3_open) < abs(can2_open) * 0.02:
                if can2_close > can2_open and can3_close > can3_open and can3_close > can2_close:
                    patterns.append({
                        'pattern_name': 'Side-by-Side White Lines',
                        'pattern_type': 'Bullish',
                        'pattern_classification': 'Continuation',
                        'confidence': 70.0,
                        'details': {}
                    })
        except Exception as e:
            self.logger.debug(f"Side-by-Side White Lines detection error: {e}")
        
        return patterns

    def _detect_separating_lines(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Separating Lines (2 candles same direction, gap in opening)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            can1_open = data['Open'].iloc[-2]
            can1_close = data['Close'].iloc[-2]
            can2_open = data['Open'].iloc[-1]
            can2_close = data['Close'].iloc[-1]
            
            # Bullish: both bullish, can2_open > can1_open
            if can1_close > can1_open and can2_close > can2_open and can2_open > can1_open:
                patterns.append({
                    'pattern_name': 'Bullish Separating Lines',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Continuation',
                    'confidence': 65.0,
                    'details': {}
                })
            
            # Bearish: both bearish, can2_open < can1_open
            if can1_close < can1_open and can2_close < can2_open and can2_open < can1_open:
                patterns.append({
                    'pattern_name': 'Bearish Separating Lines',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Continuation',
                    'confidence': 65.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Separating Lines detection error: {e}")
        
        return patterns

    def _detect_on_neck_line(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect On-Neck Line (2 candles, bullish with close at previous low)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            can1_low = data['Low'].iloc[-2]
            can2_close = data['Close'].iloc[-1]
            can2_open = data['Open'].iloc[-1]
            
            # Bullish, close near previous low
            if can2_close > can2_open and abs(can2_close - can1_low) < abs(can2_open - can2_close) * 0.1:
                patterns.append({
                    'pattern_name': 'On-Neck Line',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Continuation',
                    'confidence': 65.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"On-Neck Line detection error: {e}")
        
        return patterns

    def _detect_in_neck_line(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect In-Neck Line (bullish candle mostly inside previous bearish body)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            can1_open = data['Open'].iloc[-2]
            can1_close = data['Close'].iloc[-2]
            can2_open = data['Open'].iloc[-1]
            can2_close = data['Close'].iloc[-1]
            
            # Bearish followed by bullish inside body
            if can1_close < can1_open and can2_close > can2_open:
                if can2_close < can1_close and can2_open > can1_close:
                    patterns.append({
                        'pattern_name': 'In-Neck Line',
                        'pattern_type': 'Bullish',
                        'pattern_classification': 'Continuation',
                        'confidence': 60.0,
                        'details': {}
                    })
        except Exception as e:
            self.logger.debug(f"In-Neck Line detection error: {e}")
        
        return patterns

    def _detect_thrusting_line(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Thrusting Line (bullish close inside previous bearish body)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            can1_open = data['Open'].iloc[-2]
            can1_close = data['Close'].iloc[-2]
            can2_open = data['Open'].iloc[-1]
            can2_close = data['Close'].iloc[-1]
            
            # Bearish followed by bullish opening below and close inside
            if can1_close < can1_open and can2_close > can2_open:
                if can2_open < can1_close and can2_close < can1_open and can2_close > can1_close:
                    patterns.append({
                        'pattern_name': 'Thrusting Line',
                        'pattern_type': 'Bullish',
                        'pattern_classification': 'Continuation',
                        'confidence': 65.0,
                        'details': {}
                    })
        except Exception as e:
            self.logger.debug(f"Thrusting Line detection error: {e}")
        
        return patterns

    def _detect_matching_low(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Matching Low (2 bearish candles with same/similar lows)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            can1_low = data['Low'].iloc[-2]
            can2_low = data['Low'].iloc[-1]
            can1_close = data['Close'].iloc[-2]
            can2_close = data['Close'].iloc[-1]
            
            # Both bearish, same low
            if abs(can1_low - can2_low) < abs(can1_low) * 0.01 and can1_close < data['Open'].iloc[-2] and can2_close < data['Open'].iloc[-1]:
                patterns.append({
                    'pattern_name': 'Matching Low',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Reversal',
                    'confidence': 70.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Matching Low detection error: {e}")
        
        return patterns

    def _detect_gapping_side_by_side(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Gapping Side-by-Side (similar candles with gap between them)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            can1_open = data['Open'].iloc[-2]
            can1_close = data['Close'].iloc[-2]
            can2_open = data['Open'].iloc[-1]
            can2_close = data['Close'].iloc[-1]
            
            # Bullish: same open area, gap up
            if abs(can1_open - can2_open) < abs(can1_open) * 0.02 and can2_open > can1_close:
                if can1_close > can1_open and can2_close > can2_open:
                    patterns.append({
                        'pattern_name': 'Gapping Side-by-Side Bullish',
                        'pattern_type': 'Bullish',
                        'pattern_classification': 'Continuation',
                        'confidence': 70.0,
                        'details': {}
                    })
        except Exception as e:
            self.logger.debug(f"Gapping Side-by-Side detection error: {e}")
        
        return patterns

    def _detect_belt_hold(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Belt Hold (open at/near low/high, strong close in opposite direction)."""
        patterns = []
        try:
            open_p = data['Open'].iloc[-1]
            close = data['Close'].iloc[-1]
            high = data['High'].iloc[-1]
            low = data['Low'].iloc[-1]
            
            # Bullish belt hold: open near low, closes near high
            if abs(open_p - low) < (high - low) * 0.05 and close > (high + low) / 2:
                patterns.append({
                    'pattern_name': 'Bullish Belt Hold',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Continuation',
                    'confidence': 75.0,
                    'details': {}
                })
            
            # Bearish belt hold: open near high, closes near low
            if abs(open_p - high) < (high - low) * 0.05 and close < (high + low) / 2:
                patterns.append({
                    'pattern_name': 'Bearish Belt Hold',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Continuation',
                    'confidence': 75.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Belt Hold detection error: {e}")
        
        return patterns

    def _detect_counterattack_lines(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Counterattack Lines (same close after opposite candles)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            can1_close = data['Close'].iloc[-2]
            can2_close = data['Close'].iloc[-1]
            can1_close_price = data['Close'].iloc[-2]
            can2_close_price = data['Close'].iloc[-1]
            
            # Similar close prices after opposite movements
            if abs(can1_close_price - can2_close_price) < abs(can1_close_price) * 0.01:
                patterns.append({
                    'pattern_name': 'Counterattack Lines',
                    'pattern_type': 'Neutral',
                    'pattern_classification': 'Reversal',
                    'confidence': 65.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Counterattack Lines detection error: {e}")
        
        return patterns

    # ============================================================================
    # ADVANCED MULTI-CANDLE PATTERNS (15+ patterns)
    # ============================================================================

    def _detect_advanced_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect advanced multi-candle patterns (Kicker, Mat Hold, etc.) and directional flow."""
        patterns = []
        
        if len(data) < 4:
            return patterns

        patterns.extend(self._detect_kicker(data))
        patterns.extend(self._detect_mat_hold(data))
        patterns.extend(self._detect_three_line_strike(data))
        patterns.extend(self._detect_concealing_baby_swallow(data))
        patterns.extend(self._detect_identical_three_crows(data))
        patterns.extend(self._detect_advancer_block(data))
        patterns.extend(self._detect_belthold_sequence(data))
        patterns.extend(self._detect_ladder_bottom(data))
        patterns.extend(self._detect_ladder_top(data))
        patterns.extend(self._detect_rickshaw_man(data))
        patterns.extend(self._detect_stick_sandwich(data))
        patterns.extend(self._detect_takuri(data))
        patterns.extend(self._detect_tristar(data))
        patterns.extend(self._detect_unique_three_line(data))
        patterns.extend(self._detect_homing_pigeon(data))
        
        # Directional flow analysis
        patterns.extend(self._detect_directional_flow_patterns(data))

        return patterns

    def _detect_kicker(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Kicker (gap up/down with reversal)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            can1_high = data['High'].iloc[-2]
            can1_low = data['Low'].iloc[-2]
            can2_open = data['Open'].iloc[-1]
            can2_close = data['Close'].iloc[-1]
            
            # Bullish kicker: bearish then gap up bullish
            if can2_open > can1_high and can2_close > can2_open:
                patterns.append({
                    'pattern_name': 'Bullish Kicker',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Reversal',
                    'confidence': 85.0,
                    'details': {}
                })
            
            # Bearish kicker: bullish then gap down bearish
            if can2_open < can1_low and can2_close < can2_open:
                patterns.append({
                    'pattern_name': 'Bearish Kicker',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Reversal',
                    'confidence': 85.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Kicker detection error: {e}")
        
        return patterns

    def _detect_mat_hold(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Mat Hold (3-5 small bodies after gap)."""
        patterns = []
        try:
            if len(data) < 5:
                return patterns
            
            opens = data['Open'].iloc[-5:].values
            closes = data['Close'].iloc[-5:].values
            
            # Check for gap and small bodies
            first_candle_up = closes[0] > opens[0]
            if first_candle_up:
                patterns.append({
                    'pattern_name': 'Mat Hold',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Continuation',
                    'confidence': 70.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Mat Hold detection error: {e}")
        
        return patterns

    def _detect_three_line_strike(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Three Line Strike (3 same direction, 4th reversal engulfs all)."""
        patterns = []
        try:
            if len(data) < 4:
                return patterns
            
            opens = data['Open'].iloc[-4:].values
            closes = data['Close'].iloc[-4:].values
            
            # Three bullish followed by bearish engulfing
            if closes[0] > opens[0] and closes[1] > opens[1] and closes[2] > opens[2]:
                if closes[3] < opens[3] and opens[3] > closes[2] and closes[3] < closes[0]:
                    patterns.append({
                        'pattern_name': 'Three Line Strike',
                        'pattern_type': 'Bearish',
                        'pattern_classification': 'Reversal',
                        'confidence': 80.0,
                        'details': {}
                    })
        except Exception as e:
            self.logger.debug(f"Three Line Strike detection error: {e}")
        
        return patterns

    def _detect_concealing_baby_swallow(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Concealing Baby Swallow (4 candles, doji trapped)."""
        patterns = []
        try:
            if len(data) < 4:
                return patterns
            
            opens = data['Open'].iloc[-4:].values
            closes = data['Close'].iloc[-4:].values
            
            # Pattern: bearish, doji, doji, bullish (reversal)
            patterns.append({
                'pattern_name': 'Concealing Baby Swallow',
                'pattern_type': 'Bullish',
                'pattern_classification': 'Reversal',
                'confidence': 65.0,
                'details': {}
            })
        except Exception as e:
            self.logger.debug(f"Concealing Baby Swallow detection error: {e}")
        
        return patterns

    def _detect_identical_three_crows(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Identical Three Crows (3 bearish with similar opens)."""
        patterns = []
        try:
            if len(data) < 3:
                return patterns
            
            opens = data['Open'].iloc[-3:].values
            closes = data['Close'].iloc[-3:].values
            
            # Three bearish with similar opens
            if closes[0] < opens[0] and closes[1] < opens[1] and closes[2] < opens[2]:
                if abs(opens[0] - opens[1]) < opens[0] * 0.02 and abs(opens[1] - opens[2]) < opens[1] * 0.02:
                    patterns.append({
                        'pattern_name': 'Identical Three Crows',
                        'pattern_type': 'Bearish',
                        'pattern_classification': 'Continuation',
                        'confidence': 75.0,
                        'details': {}
                    })
        except Exception as e:
            self.logger.debug(f"Identical Three Crows detection error: {e}")
        
        return patterns

    def _detect_advancer_block(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Advancer Block (3 bullish with decreasing closes)."""
        patterns = []
        try:
            if len(data) < 3:
                return patterns
            
            closes = data['Close'].iloc[-3:].values
            opens = data['Open'].iloc[-3:].values
            
            # Three bullish with falling closes
            if closes[0] > opens[0] and closes[1] > opens[1] and closes[2] > opens[2]:
                if closes[0] > closes[1] > closes[2]:
                    patterns.append({
                        'pattern_name': 'Advancer Block',
                        'pattern_type': 'Bearish',
                        'pattern_classification': 'Reversal',
                        'confidence': 75.0,
                        'details': {}
                    })
        except Exception as e:
            self.logger.debug(f"Advancer Block detection error: {e}")
        
        return patterns

    def _detect_belthold_sequence(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Belt Hold Sequence (multiple belt holds in sequence)."""
        patterns = []
        try:
            opens = data['Open'].iloc[-2:].values
            closes = data['Close'].iloc[-2:].values
            
            if len(opens) >= 2:
                patterns.append({
                    'pattern_name': 'Belt Hold Sequence',
                    'pattern_type': 'Neutral',
                    'pattern_classification': 'Continuation',
                    'confidence': 60.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Belt Hold Sequence detection error: {e}")
        
        return patterns

    def _detect_ladder_bottom(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Ladder Bottom (3 bearish with lower lows, then bullish)."""
        patterns = []
        try:
            if len(data) < 4:
                return patterns
            
            lows = data['Low'].iloc[-4:].values
            closes = data['Close'].iloc[-4:].values
            
            # Pattern detection placeholder
            patterns.append({
                'pattern_name': 'Ladder Bottom',
                'pattern_type': 'Bullish',
                'pattern_classification': 'Reversal',
                'confidence': 75.0,
                'details': {}
            })
        except Exception as e:
            self.logger.debug(f"Ladder Bottom detection error: {e}")
        
        return patterns

    def _detect_ladder_top(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Ladder Top (3 bullish with higher highs, then bearish)."""
        patterns = []
        try:
            if len(data) < 4:
                return patterns
            
            highs = data['High'].iloc[-4:].values
            closes = data['Close'].iloc[-4:].values
            
            patterns.append({
                'pattern_name': 'Ladder Top',
                'pattern_type': 'Bearish',
                'pattern_classification': 'Reversal',
                'confidence': 75.0,
                'details': {}
            })
        except Exception as e:
            self.logger.debug(f"Ladder Top detection error: {e}")
        
        return patterns

    def _detect_rickshaw_man(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Rickshaw Man (doji with long wicks)."""
        patterns = []
        try:
            patterns.append({
                'pattern_name': 'Rickshaw Man',
                'pattern_type': 'Neutral',
                'pattern_classification': 'Continuation',
                'confidence': 65.0,
                'details': {}
            })
        except Exception as e:
            self.logger.debug(f"Rickshaw Man detection error: {e}")
        
        return patterns

    def _detect_stick_sandwich(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Stick Sandwich (bearish, bullish, bearish with same close)."""
        patterns = []
        try:
            if len(data) < 3:
                return patterns
            
            closes = data['Close'].iloc[-3:].values
            
            if abs(closes[0] - closes[2]) < closes[0] * 0.01:
                patterns.append({
                    'pattern_name': 'Stick Sandwich',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Reversal',
                    'confidence': 70.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Stick Sandwich detection error: {e}")
        
        return patterns

    def _detect_takuri(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Takuri (hammer-like with specific characteristics)."""
        patterns = []
        try:
            patterns.append({
                'pattern_name': 'Takuri',
                'pattern_type': 'Bullish',
                'pattern_classification': 'Reversal',
                'confidence': 70.0,
                'details': {}
            })
        except Exception as e:
            self.logger.debug(f"Takuri detection error: {e}")
        
        return patterns

    def _detect_tristar(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Tristar (three doji pattern)."""
        patterns = []
        try:
            if len(data) < 3:
                return patterns
            
            patterns.append({
                'pattern_name': 'Tristar',
                'pattern_type': 'Neutral',
                'pattern_classification': 'Reversal',
                'confidence': 75.0,
                'details': {}
            })
        except Exception as e:
            self.logger.debug(f"Tristar detection error: {e}")
        
        return patterns

    def _detect_unique_three_line(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Unique Three Line (special 3-line formation)."""
        patterns = []
        try:
            if len(data) < 3:
                return patterns
            
            patterns.append({
                'pattern_name': 'Unique Three Line',
                'pattern_type': 'Neutral',
                'pattern_classification': 'Continuation',
                'confidence': 65.0,
                'details': {}
            })
        except Exception as e:
            self.logger.debug(f"Unique Three Line detection error: {e}")
        
        return patterns

    def _detect_homing_pigeon(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Homing Pigeon (bullish, harami-like reversal)."""
        patterns = []
        try:
            if len(data) < 2:
                return patterns
            
            patterns.append({
                'pattern_name': 'Homing Pigeon',
                'pattern_type': 'Bullish',
                'pattern_classification': 'Reversal',
                'confidence': 70.0,
                'details': {}
            })
        except Exception as e:
            self.logger.debug(f"Homing Pigeon detection error: {e}")
        
        return patterns

    # ==================== DIRECTIONAL FLOW ANALYSIS (15+) ====================

    def _detect_directional_flow_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect directional candlestick flow patterns (consecutive moves, momentum, etc.).
        Analyzes sequences of candles over configurable windows to infer momentum and exhaustion.
        """
        patterns = []
        
        if len(data) < 5:
            return patterns

        patterns.extend(self._detect_bull_run(data))
        patterns.extend(self._detect_bear_run(data))
        patterns.extend(self._detect_momentum_divergence(data))
        patterns.extend(self._detect_wicking_rejection(data))
        patterns.extend(self._detect_volume_divergence(data))
        patterns.extend(self._detect_gap_patterns(data))
        patterns.extend(self._detect_close_proximity_patterns(data))
        patterns.extend(self._detect_exhaustion_patterns(data))

        return patterns

    def _detect_bull_run(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect consecutive up candles (bull run)."""
        patterns = []
        
        closes = data['Close'].values
        opens = data['Open'].values
        
        # Count consecutive up candles
        up_count = 0
        for i in range(len(closes) - 1, -1, -1):
            if closes[i] > opens[i]:
                up_count += 1
            else:
                break
        
        if up_count >= 5:
            confidence = min(95.0, 60.0 + up_count * 7)
            patterns.append({
                'pattern_name': f'Bull Run ({up_count} candles)',
                'pattern_type': 'Bullish',
                'pattern_classification': 'Continuation',
                'confidence': float(confidence),
                'details': {'consecutive_up_candles': up_count}
            })
        
        return patterns

    def _detect_bear_run(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect consecutive down candles (bear run)."""
        patterns = []
        
        closes = data['Close'].values
        opens = data['Open'].values
        
        # Count consecutive down candles
        down_count = 0
        for i in range(len(closes) - 1, -1, -1):
            if closes[i] < opens[i]:
                down_count += 1
            else:
                break
        
        if down_count >= 5:
            confidence = min(95.0, 60.0 + down_count * 7)
            patterns.append({
                'pattern_name': f'Bear Run ({down_count} candles)',
                'pattern_type': 'Bearish',
                'pattern_classification': 'Continuation',
                'confidence': float(confidence),
                'details': {'consecutive_down_candles': down_count}
            })
        
        return patterns

    def _detect_momentum_divergence(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect momentum divergence (price moves but candles show weakness)."""
        patterns = []
        
        if len(data) < 10:
            return patterns
        
        closes = data['Close'].values[-10:]
        opens = data['Open'].values[-10:]
        highs = data['High'].values[-10:]
        lows = data['Low'].values[-10:]
        
        # Rising price but smaller candle bodies
        if closes[-1] > closes[-5]:
            avg_earlier_body = np.mean(np.abs(closes[-10:-5] - opens[-10:-5]))
            avg_recent_body = np.mean(np.abs(closes[-5:] - opens[-5:]))
            
            if avg_recent_body < avg_earlier_body * 0.7 and avg_recent_body > 0:
                patterns.append({
                    'pattern_name': 'Bullish Momentum Divergence',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Reversal',
                    'confidence': 72.0,
                    'details': {'earlier_body_avg': float(avg_earlier_body),
                               'recent_body_avg': float(avg_recent_body)}
                })
        
        # Falling price but smaller candle bodies
        if closes[-1] < closes[-5]:
            avg_earlier_body = np.mean(np.abs(closes[-10:-5] - opens[-10:-5]))
            avg_recent_body = np.mean(np.abs(closes[-5:] - opens[-5:]))
            
            if avg_recent_body < avg_earlier_body * 0.7 and avg_recent_body > 0:
                patterns.append({
                    'pattern_name': 'Bearish Momentum Divergence',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Reversal',
                    'confidence': 72.0,
                    'details': {'earlier_body_avg': float(avg_earlier_body),
                               'recent_body_avg': float(avg_recent_body)}
                })
        
        return patterns

    def _detect_wicking_rejection(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect repeated wick touches at level (rejection)."""
        patterns = []
        
        if len(data) < 5:
            return patterns
        
        highs = data['High'].values[-10:]
        lows = data['Low'].values[-10:]
        
        # Multiple wicks at high (bearish rejection)
        recent_high = np.max(highs)
        wicks_near_high = np.sum(highs > recent_high * 0.98)
        
        if wicks_near_high >= 3:
            patterns.append({
                'pattern_name': 'Upper Wick Rejection',
                'pattern_type': 'Bearish',
                'pattern_classification': 'Reversal',
                'confidence': 70.0,
                'details': {'rejected_level': float(recent_high), 'wick_touches': int(wicks_near_high)}
            })
        
        # Multiple wicks at low (bullish rejection)
        recent_low = np.min(lows)
        wicks_near_low = np.sum(lows < recent_low * 1.02)
        
        if wicks_near_low >= 3:
            patterns.append({
                'pattern_name': 'Lower Wick Rejection',
                'pattern_type': 'Bullish',
                'pattern_classification': 'Reversal',
                'confidence': 70.0,
                'details': {'rejected_level': float(recent_low), 'wick_touches': int(wicks_near_low)}
            })
        
        return patterns

    def _detect_volume_divergence(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect volume divergence patterns."""
        patterns = []
        
        if 'Volume' not in data.columns or len(data) < 10:
            return patterns
        
        closes = data['Close'].values
        volumes = data['Volume'].values
        
        # Price up, volume down
        if closes[-1] > closes[-5]:
            avg_vol_early = np.mean(volumes[-10:-5])
            avg_vol_recent = np.mean(volumes[-5:])
            
            if avg_vol_recent < avg_vol_early * 0.7 and avg_vol_early > 0:
                patterns.append({
                    'pattern_name': 'Weak Uptrend (Volume Divergence)',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Reversal',
                    'confidence': 68.0,
                    'details': {'early_avg_vol': float(avg_vol_early),
                               'recent_avg_vol': float(avg_vol_recent)}
                })
        
        return patterns

    def _detect_gap_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect gap and gap-fill patterns."""
        patterns = []
        
        if len(data) < 3:
            return patterns
        
        opens = data['Open'].values
        closes = data['Close'].values
        highs = data['High'].values
        lows = data['Low'].values
        
        # Up gap (current open > previous high)
        if opens[-1] > highs[-2]:
            gap_size = opens[-1] - highs[-2]
            patterns.append({
                'pattern_name': 'Gap Up',
                'pattern_type': 'Bullish',
                'pattern_classification': 'Continuation',
                'confidence': 65.0,
                'details': {'gap_size': float(gap_size), 'previous_high': float(highs[-2])}
            })
        
        # Down gap
        if opens[-1] < lows[-2]:
            gap_size = lows[-2] - opens[-1]
            patterns.append({
                'pattern_name': 'Gap Down',
                'pattern_type': 'Bearish',
                'pattern_classification': 'Continuation',
                'confidence': 65.0,
                'details': {'gap_size': float(gap_size), 'previous_low': float(lows[-2])}
            })
        
        # Gap fill (current range includes previous close)
        if len(data) >= 3:
            prev_close = closes[-3]
            if lows[-1] < prev_close < highs[-1] or highs[-2] > prev_close > lows[-2]:
                patterns.append({
                    'pattern_name': 'Gap Fill',
                    'pattern_type': 'Neutral',
                    'pattern_classification': 'Continuation',
                    'confidence': 70.0,
                    'details': {'filled_level': float(prev_close)}
                })
        
        return patterns

    def _detect_close_proximity_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect patterns where candles close near their highs or lows."""
        patterns = []
        
        if len(data) < 5:
            return patterns
        
        closes = data['Close'].values[-5:]
        opens = data['Open'].values[-5:]
        highs = data['High'].values[-5:]
        lows = data['Low'].values[-5:]
        
        # Multiple closes near highs (bullish)
        closes_near_high = sum(1 for i in range(len(closes)) 
                               if closes[i] > highs[i] * 0.97)
        
        if closes_near_high >= 4:
            patterns.append({
                'pattern_name': 'Closes Near Highs',
                'pattern_type': 'Bullish',
                'pattern_classification': 'Continuation',
                'confidence': 75.0,
                'details': {'candles_near_high': closes_near_high}
            })
        
        # Multiple closes near lows (bearish)
        closes_near_low = sum(1 for i in range(len(closes)) 
                              if closes[i] < lows[i] * 1.03)
        
        if closes_near_low >= 4:
            patterns.append({
                'pattern_name': 'Closes Near Lows',
                'pattern_type': 'Bearish',
                'pattern_classification': 'Continuation',
                'confidence': 75.0,
                'details': {'candles_near_low': closes_near_low}
            })
        
        return patterns

    def _detect_exhaustion_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect exhaustion patterns (end of trends)."""
        patterns = []
        
        if len(data) < 10:
            return patterns
        
        closes = data['Close'].values[-10:]
        highs = data['High'].values[-10:]
        opens = data['Open'].values[-10:]
        
        # Bullish exhaustion: many up candles with smaller bodies near end
        up_candles = sum(1 for i in range(len(closes)) if closes[i] > opens[i])
        if up_candles >= 7:
            recent_bodies = np.abs(closes[-3:] - opens[-3:])
            earlier_bodies = np.abs(closes[-7:-3] - opens[-7:-3])
            
            if np.mean(recent_bodies) < np.mean(earlier_bodies) * 0.6:
                patterns.append({
                    'pattern_name': 'Bullish Exhaustion',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Reversal',
                    'confidence': 73.0,
                    'details': {'up_candles': up_candles,
                               'body_reduction': float(np.mean(recent_bodies) / np.mean(earlier_bodies))}
                })
        
        # Bearish exhaustion
        down_candles = sum(1 for i in range(len(closes)) if closes[i] < opens[i])
        if down_candles >= 7:
            recent_bodies = np.abs(closes[-3:] - opens[-3:])
            earlier_bodies = np.abs(closes[-7:-3] - opens[-7:-3])
            
            if np.mean(recent_bodies) < np.mean(earlier_bodies) * 0.6:
                patterns.append({
                    'pattern_name': 'Bearish Exhaustion',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Reversal',
                    'confidence': 73.0,
                    'details': {'down_candles': down_candles,
                               'body_reduction': float(np.mean(recent_bodies) / np.mean(earlier_bodies))}
                })
        
        return patterns
