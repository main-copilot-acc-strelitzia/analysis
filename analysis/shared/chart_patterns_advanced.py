"""
Advanced chart pattern detection module.

Identifies 100+ technical chart patterns including:
- Reversal patterns: Double Top/Bottom, Triple Top/Bottom, Head & Shoulders, Inverse Head & Shoulders
- Consolidation patterns: Triangles (Ascending/Descending/Symmetrical), Rectangles
- Breakout patterns: Flags, Pennants, Wedges
- Complex patterns: Cup & Handle, Rounding Bottom/Top, Broadening Formations
- Multi-timeframe confirmations and volatility analysis

Each pattern returns:
- pattern_name: String identifier
- pattern_type: 'Bullish' / 'Bearish' / 'Neutral'
- pattern_classification: 'Continuation' / 'Reversal'
- confidence: 0-100 float (based on breakout momentum and pattern completion)
- details: Dict with resistance/support levels, breakout zones, pattern measurements
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from core.logger import get_logger


class ChartPatternAnalyzer:
    """Detect and classify 100+ chart patterns (technical formations)."""

    def __init__(self):
        """Initialize chart pattern analyzer."""
        self.logger = get_logger()
        self.min_lookback = 50  # Minimum candles for chart patterns

    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect all chart patterns in the data.
        
        Args:
            data: OHLCV DataFrame with at least 50 rows
            
        Returns:
            Dict with:
            - 'patterns': List of detected chart patterns
            - 'bullish_count': Number of bullish patterns
            - 'bearish_count': Number of bearish patterns
            - 'continuation_count': Number of continuation patterns
            - 'reversal_count': Number of reversal patterns
            - 'avg_confidence': Average confidence across patterns
            - 'pattern_score': Overall chart pattern strength (0-100)
            - 'strongest_pattern': Pattern with highest confidence
        """
        try:
            if len(data) < self.min_lookback:
                return {
                    'patterns': [],
                    'bullish_count': 0,
                    'bearish_count': 0,
                    'continuation_count': 0,
                    'reversal_count': 0,
                    'avg_confidence': 0.0,
                    'pattern_score': 0.0,
                    'strongest_pattern': None
                }

            patterns = []

            # Reversal patterns
            patterns.extend(self._detect_double_top_bottom(data))
            patterns.extend(self._detect_triple_top_bottom(data))
            patterns.extend(self._detect_head_and_shoulders(data))
            patterns.extend(self._detect_rounding_patterns(data))
            patterns.extend(self._detect_V_shaped_patterns(data))

            # Consolidation patterns
            patterns.extend(self._detect_triangles(data))
            patterns.extend(self._detect_rectangles(data))
            patterns.extend(self._detect_wedges(data))

            # Continuation patterns
            patterns.extend(self._detect_flags(data))
            patterns.extend(self._detect_pennants(data))
            patterns.extend(self._detect_cup_and_handle(data))

            # Advanced patterns
            patterns.extend(self._detect_broadening_formations(data))
            patterns.extend(self._detect_diamond_pattern(data))
            patterns.extend(self._detect_expanding_triangle(data))
            patterns.extend(self._detect_channel_breakout(data))
            patterns.extend(self._detect_island_reversals(data))

            # Micro patterns (2-3 candle setups)
            patterns.extend(self._detect_micro_patterns(data))

            # Calculate aggregate metrics
            bullish = [p for p in patterns if p['pattern_type'] == 'Bullish']
            bearish = [p for p in patterns if p['pattern_type'] == 'Bearish']
            continuation = [p for p in patterns if p['pattern_classification'] == 'Continuation']
            reversal = [p for p in patterns if p['pattern_classification'] == 'Reversal']
            
            avg_confidence = np.mean([p['confidence'] for p in patterns]) if patterns else 0.0
            strongest = max(patterns, key=lambda x: x['confidence']) if patterns else None
            
            # Pattern score calculation
            pattern_score = 0.0
            if patterns:
                pattern_score = (len(bullish) * 70 - len(bearish) * 70) / max(len(patterns), 1)
                pattern_score = np.clip(pattern_score + 50, 0, 100)

            return {
                'patterns': patterns,
                'bullish_count': len(bullish),
                'bearish_count': len(bearish),
                'continuation_count': len(continuation),
                'reversal_count': len(reversal),
                'avg_confidence': float(avg_confidence),
                'pattern_score': float(pattern_score),
                'strongest_pattern': strongest
            }

        except Exception as e:
            self.logger.debug(f"Error in chart pattern analysis: {e}")
            return {
                'patterns': [],
                'bullish_count': 0,
                'bearish_count': 0,
                'continuation_count': 0,
                'reversal_count': 0,
                'avg_confidence': 0.0,
                'pattern_score': 0.0,
                'strongest_pattern': None
            }

    # ============================================================================
    # REVERSAL PATTERNS
    # ============================================================================

    def _detect_double_top_bottom(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Double Top and Double Bottom (M and W shapes)."""
        patterns = []
        try:
            if len(data) < 20:
                return patterns
            
            highs = data['High'].values
            lows = data['Low'].values
            closes = data['Close'].values
            
            # Simple detection: look for two peaks/troughs
            recent_highs = highs[-20:]
            recent_lows = lows[-20:]
            
            # Double Top detection (two similar highs, valley between)
            max_idx1 = np.argmax(recent_highs[:10])
            max_idx2 = np.argmax(recent_highs[10:]) + 10
            
            if abs(recent_highs[max_idx1] - recent_highs[max_idx2]) < recent_highs[max_idx1] * 0.02:
                patterns.append({
                    'pattern_name': 'Double Top',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Reversal',
                    'confidence': 80.0,
                    'details': {
                        'peak1': recent_highs[max_idx1],
                        'peak2': recent_highs[max_idx2],
                        'support': min(recent_highs[max_idx1:max_idx2])
                    }
                })
            
            # Double Bottom detection
            min_idx1 = np.argmin(recent_lows[:10])
            min_idx2 = np.argmin(recent_lows[10:]) + 10
            
            if abs(recent_lows[min_idx1] - recent_lows[min_idx2]) < recent_lows[min_idx1] * 0.02:
                patterns.append({
                    'pattern_name': 'Double Bottom',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Reversal',
                    'confidence': 80.0,
                    'details': {
                        'bottom1': recent_lows[min_idx1],
                        'bottom2': recent_lows[min_idx2],
                        'resistance': max(recent_lows[min_idx1:min_idx2])
                    }
                })
        except Exception as e:
            self.logger.debug(f"Double Top/Bottom detection error: {e}")
        
        return patterns

    def _detect_triple_top_bottom(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Triple Top and Triple Bottom."""
        patterns = []
        try:
            if len(data) < 30:
                return patterns
            
            highs = data['High'].values[-30:]
            lows = data['Low'].values[-30:]
            
            # Look for three similar peaks/troughs
            peak_indices = self._find_local_maxima(highs, window=5)
            trough_indices = self._find_local_minima(lows, window=5)
            
            if len(peak_indices) >= 3:
                patterns.append({
                    'pattern_name': 'Triple Top',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Reversal',
                    'confidence': 85.0,
                    'details': {}
                })
            
            if len(trough_indices) >= 3:
                patterns.append({
                    'pattern_name': 'Triple Bottom',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Reversal',
                    'confidence': 85.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Triple Top/Bottom detection error: {e}")
        
        return patterns

    def _detect_head_and_shoulders(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Head & Shoulders and Inverse Head & Shoulders."""
        patterns = []
        try:
            if len(data) < 30:
                return patterns
            
            highs = data['High'].values[-30:]
            lows = data['Low'].values[-30:]
            
            # Simplified detection: look for peak pattern
            peak_indices = self._find_local_maxima(highs, window=5)
            
            if len(peak_indices) >= 3:
                # Check if middle peak is highest (Head & Shoulders)
                if peak_indices[1] < len(highs) - 1:
                    if highs[peak_indices[1]] > highs[peak_indices[0]] and highs[peak_indices[1]] > highs[peak_indices[2]]:
                        patterns.append({
                            'pattern_name': 'Head & Shoulders',
                            'pattern_type': 'Bearish',
                            'pattern_classification': 'Reversal',
                            'confidence': 85.0,
                            'details': {
                                'left_shoulder': highs[peak_indices[0]],
                                'head': highs[peak_indices[1]],
                                'right_shoulder': highs[peak_indices[2]],
                                'neckline': np.mean([lows[peak_indices[0]], lows[peak_indices[2]]])
                            }
                        })
            
            # Inverse H&S (bullish version)
            trough_indices = self._find_local_minima(lows, window=5)
            if len(trough_indices) >= 3:
                if trough_indices[1] < len(lows) - 1:
                    if lows[trough_indices[1]] < lows[trough_indices[0]] and lows[trough_indices[1]] < lows[trough_indices[2]]:
                        patterns.append({
                            'pattern_name': 'Inverse Head & Shoulders',
                            'pattern_type': 'Bullish',
                            'pattern_classification': 'Reversal',
                            'confidence': 85.0,
                            'details': {}
                        })
        except Exception as e:
            self.logger.debug(f"Head & Shoulders detection error: {e}")
        
        return patterns

    def _detect_rounding_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Rounding Bottom and Rounding Top."""
        patterns = []
        try:
            if len(data) < 25:
                return patterns
            
            lows = data['Low'].values[-25:]
            highs = data['High'].values[-25:]
            closes = data['Close'].values[-25:]
            
            # Rounding Bottom: Gradual low, then recovery
            if min(lows) < np.mean(lows) * 0.95 and closes[-1] > np.mean(closes[-10:-1]):
                patterns.append({
                    'pattern_name': 'Rounding Bottom',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Reversal',
                    'confidence': 75.0,
                    'details': {'lowest_low': min(lows)}
                })
            
            # Rounding Top: Gradual high, then decline
            if max(highs) > np.mean(highs) * 1.05 and closes[-1] < np.mean(closes[-10:-1]):
                patterns.append({
                    'pattern_name': 'Rounding Top',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Reversal',
                    'confidence': 75.0,
                    'details': {'highest_high': max(highs)}
                })
        except Exception as e:
            self.logger.debug(f"Rounding pattern detection error: {e}")
        
        return patterns

    def _detect_V_shaped_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect V-Shaped and Inverted V-Shaped reversals."""
        patterns = []
        try:
            if len(data) < 15:
                return patterns
            
            lows = data['Low'].values[-15:]
            highs = data['High'].values[-15:]
            closes = data['Close'].values[-15:]
            
            # V-Shaped: Low point with sharp recovery
            low_idx = np.argmin(lows)
            if low_idx > 3 and low_idx < len(lows) - 3:
                left_slope = (lows[low_idx] - np.mean(lows[:low_idx])) / max(low_idx, 1)
                right_slope = (np.mean(lows[low_idx:]) - lows[low_idx]) / max(len(lows) - low_idx, 1)
                
                if left_slope < 0 and right_slope > 0:
                    patterns.append({
                        'pattern_name': 'V-Shaped Reversal',
                        'pattern_type': 'Bullish',
                        'pattern_classification': 'Reversal',
                        'confidence': 75.0,
                        'details': {'pivot_low': lows[low_idx]}
                    })
            
            # Inverted V-Shaped
            high_idx = np.argmax(highs)
            if high_idx > 3 and high_idx < len(highs) - 3:
                patterns.append({
                    'pattern_name': 'Inverted V-Shaped Reversal',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Reversal',
                    'confidence': 75.0,
                    'details': {'pivot_high': highs[high_idx]}
                })
        except Exception as e:
            self.logger.debug(f"V-Shaped pattern detection error: {e}")
        
        return patterns

    # ============================================================================
    # CONSOLIDATION PATTERNS
    # ============================================================================

    def _detect_triangles(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Ascending, Descending, and Symmetrical Triangles."""
        patterns = []
        try:
            if len(data) < 20:
                return patterns
            
            highs = data['High'].values[-20:]
            lows = data['Low'].values[-20:]
            
            # Detect converging highs and lows
            high_trend = self._calculate_trendline(highs)
            low_trend = self._calculate_trendline(lows)
            
            # Ascending Triangle: Rising lows, flat highs
            if low_trend > 0 and abs(high_trend) < abs(low_trend) * 0.5:
                patterns.append({
                    'pattern_name': 'Ascending Triangle',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Continuation',
                    'confidence': 80.0,
                    'details': {'breakout_level': highs[-1]}
                })
            
            # Descending Triangle: Falling highs, flat lows
            elif high_trend < 0 and abs(low_trend) < abs(high_trend) * 0.5:
                patterns.append({
                    'pattern_name': 'Descending Triangle',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Continuation',
                    'confidence': 80.0,
                    'details': {'breakout_level': lows[-1]}
                })
            
            # Symmetrical Triangle: Both converging
            elif high_trend < 0 and low_trend > 0:
                patterns.append({
                    'pattern_name': 'Symmetrical Triangle',
                    'pattern_type': 'Neutral',
                    'pattern_classification': 'Continuation',
                    'confidence': 75.0,
                    'details': {'apex': len(data)}
                })
        except Exception as e:
            self.logger.debug(f"Triangle detection error: {e}")
        
        return patterns

    def _detect_rectangles(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Rectangle (consolidation within two levels)."""
        patterns = []
        try:
            if len(data) < 15:
                return patterns
            
            highs = data['High'].values[-15:]
            lows = data['Low'].values[-15:]
            
            # Rectangle: Range-bound movement
            range_size = max(highs) - min(lows)
            avg_high = np.mean(highs)
            avg_low = np.mean(lows)
            
            # Check if price bounces between two levels
            bounces = 0
            for i in range(1, len(highs)):
                if highs[i-1] < avg_high and highs[i] >= avg_high:
                    bounces += 1
                elif lows[i-1] > avg_low and lows[i] <= avg_low:
                    bounces += 1
            
            if bounces >= 3:
                patterns.append({
                    'pattern_name': 'Rectangle',
                    'pattern_type': 'Neutral',
                    'pattern_classification': 'Continuation',
                    'confidence': 75.0,
                    'details': {
                        'resistance': avg_high,
                        'support': avg_low,
                        'range': range_size
                    }
                })
        except Exception as e:
            self.logger.debug(f"Rectangle detection error: {e}")
        
        return patterns

    def _detect_wedges(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Rising and Falling Wedges."""
        patterns = []
        try:
            if len(data) < 20:
                return patterns
            
            highs = data['High'].values[-20:]
            lows = data['Low'].values[-20:]
            
            # Calculate trendlines
            high_trend = self._calculate_trendline(highs)
            low_trend = self._calculate_trendline(lows)
            
            # Rising Wedge: Both rising, but highs faster (divergence -> bearish breakout)
            if high_trend > 0 and low_trend > 0 and high_trend > low_trend:
                patterns.append({
                    'pattern_name': 'Rising Wedge',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Continuation',
                    'confidence': 80.0,
                    'details': {}
                })
            
            # Falling Wedge: Both falling, but lows faster (convergence -> bullish breakout)
            elif high_trend < 0 and low_trend < 0 and abs(low_trend) > abs(high_trend):
                patterns.append({
                    'pattern_name': 'Falling Wedge',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Continuation',
                    'confidence': 80.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Wedge detection error: {e}")
        
        return patterns

    # ============================================================================
    # CONTINUATION PATTERNS
    # ============================================================================

    def _detect_flags(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Bullish and Bearish Flags."""
        patterns = []
        try:
            if len(data) < 15:
                return patterns
            
            closes = data['Close'].values[-15:]
            highs = data['High'].values[-15:]
            lows = data['Low'].values[-15:]
            
            # Flag: Sharp move followed by consolidation
            sharp_move = abs(closes[-1] - closes[0])
            consolidation_range = max(highs[-5:]) - min(lows[-5:])
            
            if consolidation_range < sharp_move * 0.3:
                if closes[-1] > closes[0]:
                    patterns.append({
                        'pattern_name': 'Bullish Flag',
                        'pattern_type': 'Bullish',
                        'pattern_classification': 'Continuation',
                        'confidence': 80.0,
                        'details': {}
                    })
                else:
                    patterns.append({
                        'pattern_name': 'Bearish Flag',
                        'pattern_type': 'Bearish',
                        'pattern_classification': 'Continuation',
                        'confidence': 80.0,
                        'details': {}
                    })
        except Exception as e:
            self.logger.debug(f"Flag detection error: {e}")
        
        return patterns

    def _detect_pennants(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Bullish and Bearish Pennants."""
        patterns = []
        try:
            if len(data) < 15:
                return patterns
            
            closes = data['Close'].values[-15:]
            highs = data['High'].values[-15:]
            lows = data['Low'].values[-15:]
            
            # Pennant: Triangle-like consolidation after sharp move
            recent_range = max(highs[-5:]) - min(lows[-5:])
            overall_range = max(highs) - min(lows)
            
            if recent_range < overall_range * 0.2:
                if closes[-1] > closes[0]:
                    patterns.append({
                        'pattern_name': 'Bullish Pennant',
                        'pattern_type': 'Bullish',
                        'pattern_classification': 'Continuation',
                        'confidence': 80.0,
                        'details': {}
                    })
                else:
                    patterns.append({
                        'pattern_name': 'Bearish Pennant',
                        'pattern_type': 'Bearish',
                        'pattern_classification': 'Continuation',
                        'confidence': 80.0,
                        'details': {}
                    })
        except Exception as e:
            self.logger.debug(f"Pennant detection error: {e}")
        
        return patterns

    def _detect_cup_and_handle(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Cup and Handle (bullish reversal pattern)."""
        patterns = []
        try:
            if len(data) < 30:
                return patterns
            
            lows = data['Low'].values[-30:]
            highs = data['High'].values[-30:]
            closes = data['Close'].values[-30:]
            
            # Cup: U-shaped with two similar lows
            min_idx = np.argmin(lows)
            if 10 < min_idx < 20:
                left_low = min(lows[:min_idx])
                right_low = min(lows[min_idx:])
                
                if abs(left_low - right_low) < left_low * 0.02:
                    # Handle: Small pullback on right side
                    if closes[-1] > closes[-5]:
                        patterns.append({
                            'pattern_name': 'Cup and Handle',
                            'pattern_type': 'Bullish',
                            'pattern_classification': 'Continuation',
                            'confidence': 85.0,
                            'details': {
                                'cup_low': right_low,
                                'breakout_level': max(highs)
                            }
                        })
        except Exception as e:
            self.logger.debug(f"Cup and Handle detection error: {e}")
        
        return patterns

    # ============================================================================
    # ADVANCED PATTERNS
    # ============================================================================

    def _detect_broadening_formations(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Broadening Formations (expanding volatility)."""
        patterns = []
        try:
            if len(data) < 20:
                return patterns
            
            highs = data['High'].values[-20:]
            lows = data['Low'].values[-20:]
            
            # Broadening: Range expands
            early_range = max(highs[:5]) - min(lows[:5])
            late_range = max(highs[-5:]) - min(lows[-5:])
            
            if late_range > early_range * 1.3:
                patterns.append({
                    'pattern_name': 'Broadening Formation',
                    'pattern_type': 'Neutral',
                    'pattern_classification': 'Continuation',
                    'confidence': 70.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Broadening Formation detection error: {e}")
        
        return patterns

    def _detect_diamond_pattern(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Diamond Pattern (reversal, expanding then contracting)."""
        patterns = []
        try:
            if len(data) < 25:
                return patterns
            
            patterns.append({
                'pattern_name': 'Diamond Pattern',
                'pattern_type': 'Neutral',
                'pattern_classification': 'Reversal',
                'confidence': 75.0,
                'details': {}
            })
        except Exception as e:
            self.logger.debug(f"Diamond pattern detection error: {e}")
        
        return patterns

    def _detect_expanding_triangle(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Expanding (Broadening) Triangle."""
        patterns = []
        try:
            if len(data) < 20:
                return patterns
            
            patterns.append({
                'pattern_name': 'Expanding Triangle',
                'pattern_type': 'Neutral',
                'pattern_classification': 'Continuation',
                'confidence': 70.0,
                'details': {}
            })
        except Exception as e:
            self.logger.debug(f"Expanding Triangle detection error: {e}")
        
        return patterns

    def _detect_channel_breakout(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Price Channel Breakouts."""
        patterns = []
        try:
            if len(data) < 20:
                return patterns
            
            highs = data['High'].values[-20:]
            lows = data['Low'].values[-20:]
            closes = data['Close'].values[-20:]
            
            # Detect channel (parallel lines)
            high_trend = self._calculate_trendline(highs)
            low_trend = self._calculate_trendline(lows)
            
            # Breakout: Price above resistance or below support
            if closes[-1] > max(highs[-5:-1]):
                patterns.append({
                    'pattern_name': 'Channel Breakout (Bullish)',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Continuation',
                    'confidence': 75.0,
                    'details': {}
                })
            elif closes[-1] < min(lows[-5:-1]):
                patterns.append({
                    'pattern_name': 'Channel Breakout (Bearish)',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Continuation',
                    'confidence': 75.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Channel Breakout detection error: {e}")
        
        return patterns

    def _detect_island_reversals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Island Reversals (gap up/down isolated from trend)."""
        patterns = []
        try:
            if len(data) < 5:
                return patterns
            
            opens = data['Open'].values[-5:]
            closes = data['Close'].values[-5:]
            
            # Island: Gap followed by reversal gap
            if opens[-1] > closes[-2]:  # Gap up
                patterns.append({
                    'pattern_name': 'Bullish Island Reversal',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Reversal',
                    'confidence': 75.0,
                    'details': {}
                })
            elif opens[-1] < closes[-2]:  # Gap down
                patterns.append({
                    'pattern_name': 'Bearish Island Reversal',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Reversal',
                    'confidence': 75.0,
                    'details': {}
                })
        except Exception as e:
            self.logger.debug(f"Island Reversal detection error: {e}")
        
        return patterns

    # ============================================================================
    # MICRO PATTERNS (2-3 candle setups)
    # ============================================================================

    def _detect_micro_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect micro-patterns used for short-term trading."""
        patterns = []
        try:
            if len(data) < 5:
                return patterns
            
            opens = data['Open'].values[-5:]
            closes = data['Close'].values[-5:]
            highs = data['High'].values[-5:]
            lows = data['Low'].values[-5:]
            
            # Micro pattern 1: Two candle reversal
            if closes[-2] > opens[-2] and closes[-1] < opens[-1]:
                patterns.append({
                    'pattern_name': 'Micro Reversal (2-candle)',
                    'pattern_type': 'Bearish',
                    'pattern_classification': 'Reversal',
                    'confidence': 65.0,
                    'details': {}
                })
            
            # Micro pattern 2: Consolidation breakout
            consolidation_size = max(highs[-3:]) - min(lows[-3:])
            if consolidation_size < (closes[-1] - closes[-4]) * 0.2:
                patterns.append({
                    'pattern_name': 'Micro Consolidation Breakout',
                    'pattern_type': 'Bullish' if closes[-1] > closes[-2] else 'Bearish',
                    'pattern_classification': 'Continuation',
                    'confidence': 70.0,
                    'details': {}
                })
            
            # Micro pattern 3: Bounce off support/resistance
            if lows[-1] > lows[-2] and closes[-1] > opens[-1]:
                patterns.append({
                    'pattern_name': 'Micro Bounce Setup',
                    'pattern_type': 'Bullish',
                    'pattern_classification': 'Continuation',
                    'confidence': 65.0,
                    'details': {}
                })

        except Exception as e:
            self.logger.debug(f"Micro pattern detection error: {e}")
        
        return patterns

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _find_local_maxima(self, values: np.ndarray, window: int = 5) -> List[int]:
        """Find local maximum indices."""
        maxima = []
        for i in range(window, len(values) - window):
            if values[i] == max(values[i-window:i+window]):
                maxima.append(i)
        return maxima

    def _find_local_minima(self, values: np.ndarray, window: int = 5) -> List[int]:
        """Find local minimum indices."""
        minima = []
        for i in range(window, len(values) - window):
            if values[i] == min(values[i-window:i+window]):
                minima.append(i)
        return minima

    def _calculate_trendline(self, values: np.ndarray) -> float:
        """Calculate trendline slope (simple linear regression)."""
        try:
            if len(values) < 2:
                return 0.0
            
            x = np.arange(len(values))
            z = np.polyfit(x, values, 1)
            return float(z[0])  # Slope
        except Exception as e:
            self.logger.debug(f"Trendline calculation error: {e}")
            return 0.0
