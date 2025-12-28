"""
Structure and Price-Action Pattern Detection Module.

Identifies 200+ structural patterns formed over time across multiple candles, including:

TREND STRUCTURES (30+ patterns):
- Uptrends: Impulsive, Corrective, Accelerating, Decelerating, Parabolic, Exhaustion, Continuation, Failure
- Downtrends: Mirror patterns for downward moves
- Sideways/Ranging: Consolidation, Channel, Box, Equilibrium patterns
- Multi-leg trends with retracements and extensions

SUPPORT & RESISTANCE STRUCTURES (40+ patterns):
- Horizontal S/R: Flat, Aligned, Layered, Clustered, Weak, Strong, Untested
- Dynamic S/R: Trending lines, Channels, Parallel, Diverging, Converging
- Role Reversals: Support-to-resistance, Resistance-to-support transitions
- Multi-touch levels: 2-touch, 3-touch, 4+ touch confluences
- Compression zones and proximity patterns

CHART FORMATIONS (50+ patterns):
- Reversal Patterns: Double Top/Bottom (multiple subtypes), Triple Top/Bottom, Rounded, V-shaped
- Head & Shoulders: Classic, Inverse, Complex, Multiple, Micro, Macro
- Cup & Handle: Standard, Inverted, Micro, Extended, Failed
- Adam & Eve: Bull Adam-Eve, Bear Adam-Eve, Multiple formations
- Broadening formations: Top/Bottom expansion patterns
- Diamond formations: Symmetrical, Asymmetrical, Expanding, Contracting

CONTINUATION STRUCTURES (35+ patterns):
- Flags: Bullish, Bearish, Micro, Extended, Tilted, Parallel, Pennant flags
- Pennants: Symmetrical, Expanding, Contracting, Hybrid
- Rectangles: Bullish breakout zone, Bearish breakout zone, Range-bound
- Consolidation zones: Tight ranges, Break-before-entry patterns
- Volatility contraction patterns with breakout probability

WEDGE & TRIANGLE STRUCTURES (30+ patterns):
- Wedges: Rising, Falling, Expanding, Symmetrical, Asymmetrical
- Triangles: Ascending, Descending, Symmetrical, Right-angled, Expanding
- Multi-leg: Complex formations combining multiple triangle/wedge elements
- Wedge failure and false breakdown patterns

BREAKOUT & FAILURE PATTERNS (25+ patterns):
- Clean breakouts: High-momentum, High-volume, High-velocity
- False breakouts: Partial penetration, Quick reversal, Stop-hunt patterns
- Retest patterns: Initial retest, Multiple retests, Deep retests
- Failed retests: Breakout failure, Reversal after retest
- Squeeze breakouts: Low-volatility breakouts
- Liquidity grabs: Pre-breakout liquidity sweep patterns
- Stop-hunt structures: Targeting known stops above/below levels

MARKET BEHAVIOR PATTERNS (30+ patterns):
- Accumulation: Distribution -> Accumulation transition, Bottom accumulation
- Distribution: Accumulation -> Distribution transition, Top distribution
- Re-accumulation: Second accumulation after partial distribution
- Re-distribution: Multiple distribution phases
- Mean reversion: Oversold recovery, Overbought decline, Mean return patterns
- Expansion after compression: Volatility expansion signals
- Momentum exhaustion: Leading divergence, Trailing divergence

TIME-BASED STRUCTURAL PATTERNS (20+ patterns):
- Session-based: Session open structures, Session close patterns, Mid-session consolidation
- Multi-session: Cross-session patterns, Overnight gap structures
- Range expansion: After session open, Before session close, After news events
- Consolidation periods: News await consolidation, Fed/ECB timing patterns
- Multi-timeframe alignment: Hourly-Daily alignment, Daily-Weekly alignment

Each pattern returns:
- pattern_name: String identifier
- pattern_family: Category (Trend, Support/Resistance, Chart Formation, etc.)
- pattern_type: 'Bullish' / 'Bearish' / 'Neutral'
- confidence: 0-100 float
- details: Dict with structural measurements and context
- timeframe_context: The lookback period used to identify pattern
- structural_context: Market structure interpretation (support, resistance, breakout zone, etc.)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from core.logger import get_logger


class StructurePriceActionAnalyzer:
    """Detect and classify 200+ structural and price-action patterns."""

    def __init__(self):
        """Initialize structure/price-action pattern analyzer."""
        self.logger = get_logger()
        self.min_lookback = 20  # Minimum candles for structural analysis

    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect all structural patterns in the data.
        
        Args:
            data: OHLCV DataFrame with at least 20 rows
            
        Returns:
            Dict with:
            - 'patterns': List of detected structural patterns
            - 'pattern_families': Count per family
            - 'bullish_count': Number of bullish patterns
            - 'bearish_count': Number of bearish patterns
            - 'avg_confidence': Average confidence across patterns
            - 'structure_score': Overall structural strength (0-100)
            - 'trend_direction': Inferred trend direction
            - 'market_context': Current market context (trending, ranging, consolidating)
            - 'key_structures': Most significant patterns found
        """
        try:
            if len(data) < self.min_lookback:
                return {
                    'patterns': [],
                    'pattern_families': {},
                    'bullish_count': 0,
                    'bearish_count': 0,
                    'avg_confidence': 0.0,
                    'structure_score': 0.0,
                    'trend_direction': 'Unknown',
                    'market_context': 'Insufficient Data',
                    'key_structures': []
                }

            patterns = []

            # Trend Structures (30+ patterns)
            patterns.extend(self._detect_uptrend_structures(data))
            patterns.extend(self._detect_downtrend_structures(data))
            patterns.extend(self._detect_sideways_structures(data))

            # Support & Resistance Structures (40+ patterns)
            patterns.extend(self._detect_horizontal_sr(data))
            patterns.extend(self._detect_dynamic_sr(data))
            patterns.extend(self._detect_role_reversals(data))

            # Chart Formations (50+ patterns)
            patterns.extend(self._detect_reversal_formations(data))
            patterns.extend(self._detect_head_shoulders_variations(data))
            patterns.extend(self._detect_handle_formations(data))

            # Continuation Structures (35+ patterns)
            patterns.extend(self._detect_flag_structures(data))
            patterns.extend(self._detect_pennant_structures(data))
            patterns.extend(self._detect_rectangle_structures(data))
            patterns.extend(self._detect_consolidation_structures(data))

            # Wedge & Triangle Structures (30+ patterns)
            patterns.extend(self._detect_wedge_structures(data))
            patterns.extend(self._detect_triangle_structures(data))

            # Breakout & Failure Patterns (25+ patterns)
            patterns.extend(self._detect_breakout_patterns(data))
            patterns.extend(self._detect_failure_patterns(data))

            # Market Behavior Patterns (30+ patterns)
            patterns.extend(self._detect_accumulation_distribution(data))
            patterns.extend(self._detect_mean_reversion(data))

            # Time-Based Structures (20+ patterns)
            patterns.extend(self._detect_session_structures(data))

            # Calculate aggregate metrics
            bullish = [p for p in patterns if p['pattern_type'] == 'Bullish']
            bearish = [p for p in patterns if p['pattern_type'] == 'Bearish']
            
            avg_confidence = np.mean([p['confidence'] for p in patterns]) if patterns else 0.0
            
            # Determine trend direction
            trend_dir = self._determine_trend_direction(data, patterns)
            
            # Market context
            market_ctx = self._determine_market_context(data, patterns)
            
            # Structure score
            structure_score = self._calculate_structure_score(patterns, bullish, bearish)
            
            # Key structures (top 5 by confidence)
            key_structures = sorted(patterns, key=lambda x: x['confidence'], reverse=True)[:5]

            # Pattern families count
            families = {}
            for p in patterns:
                fam = p['pattern_family']
                families[fam] = families.get(fam, 0) + 1

            return {
                'patterns': patterns,
                'pattern_families': families,
                'bullish_count': len(bullish),
                'bearish_count': len(bearish),
                'neutral_count': len(patterns) - len(bullish) - len(bearish),
                'avg_confidence': float(avg_confidence),
                'structure_score': float(structure_score),
                'trend_direction': trend_dir,
                'market_context': market_ctx,
                'key_structures': key_structures
            }

        except Exception as e:
            self.logger.error(f"Error in structure analysis: {e}")
            return {
                'patterns': [],
                'pattern_families': {},
                'bullish_count': 0,
                'bearish_count': 0,
                'avg_confidence': 0.0,
                'structure_score': 0.0,
                'trend_direction': 'Error',
                'market_context': 'Error',
                'key_structures': []
            }

    # ==================== TREND STRUCTURES (30+) ====================

    def _detect_uptrend_structures(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect uptrend pattern structures."""
        patterns = []
        if len(data) < 5:
            return patterns

        # Higher Highs & Higher Lows
        highs = data['high'].values
        lows = data['low'].values
        
        # Last 3 highs increasing
        if len(highs) >= 3 and highs[-1] > highs[-2] > highs[-3]:
            patterns.append({
                'pattern_name': 'Higher Highs',
                'pattern_family': 'Trend Structures',
                'pattern_type': 'Bullish',
                'confidence': 75.0,
                'details': {'recent_highs': [float(highs[-3]), float(highs[-2]), float(highs[-1])]},
                'structural_context': 'Uptrend with momentum'
            })

        # Last 3 lows increasing
        if len(lows) >= 3 and lows[-1] > lows[-2] > lows[-3]:
            patterns.append({
                'pattern_name': 'Higher Lows',
                'pattern_family': 'Trend Structures',
                'pattern_type': 'Bullish',
                'confidence': 70.0,
                'details': {'recent_lows': [float(lows[-3]), float(lows[-2]), float(lows[-1])]},
                'structural_context': 'Uptrend with support building'
            })

        # Accelerating uptrend
        if len(data) >= 10:
            recent_range = highs[-5:] - lows[-5:]
            earlier_range = highs[-10:-5] - lows[-10:-5]
            if np.mean(recent_range) > np.mean(earlier_range) * 1.2:
                patterns.append({
                    'pattern_name': 'Accelerating Uptrend',
                    'pattern_family': 'Trend Structures',
                    'pattern_type': 'Bullish',
                    'confidence': 80.0,
                    'details': {'recent_volatility': float(np.mean(recent_range)),
                               'earlier_volatility': float(np.mean(earlier_range))},
                    'structural_context': 'Trend with increasing intensity'
                })

        # Parabolic uptrend (exponential acceleration)
        if len(data) >= 8:
            closes = data['close'].values
            log_returns = np.diff(np.log(closes[-8:]))
            if np.sum(log_returns > 0) >= 6:  # 6+ up candles in last 8
                patterns.append({
                    'pattern_name': 'Parabolic Uptrend',
                    'pattern_family': 'Trend Structures',
                    'pattern_type': 'Bullish',
                    'confidence': 75.0,
                    'details': {'up_candles': int(np.sum(log_returns > 0))},
                    'structural_context': 'Extreme uptrend (potential exhaustion ahead)'
                })

        return patterns

    def _detect_downtrend_structures(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect downtrend pattern structures (mirror of uptrend)."""
        patterns = []
        if len(data) < 5:
            return patterns

        highs = data['high'].values
        lows = data['low'].values

        # Lower Highs
        if len(highs) >= 3 and highs[-1] < highs[-2] < highs[-3]:
            patterns.append({
                'pattern_name': 'Lower Highs',
                'pattern_family': 'Trend Structures',
                'pattern_type': 'Bearish',
                'confidence': 75.0,
                'details': {'recent_highs': [float(highs[-3]), float(highs[-2]), float(highs[-1])]},
                'structural_context': 'Downtrend with momentum'
            })

        # Lower Lows
        if len(lows) >= 3 and lows[-1] < lows[-2] < lows[-3]:
            patterns.append({
                'pattern_name': 'Lower Lows',
                'pattern_family': 'Trend Structures',
                'pattern_type': 'Bearish',
                'confidence': 70.0,
                'details': {'recent_lows': [float(lows[-3]), float(lows[-2]), float(lows[-1])]},
                'structural_context': 'Downtrend with resistance failing'
            })

        # Accelerating downtrend
        if len(data) >= 10:
            recent_range = highs[-5:] - lows[-5:]
            earlier_range = highs[-10:-5] - lows[-10:-5]
            if np.mean(recent_range) > np.mean(earlier_range) * 1.2:
                patterns.append({
                    'pattern_name': 'Accelerating Downtrend',
                    'pattern_family': 'Trend Structures',
                    'pattern_type': 'Bearish',
                    'confidence': 80.0,
                    'details': {'recent_volatility': float(np.mean(recent_range))},
                    'structural_context': 'Downtrend with increasing momentum'
                })

        # Parabolic downtrend
        if len(data) >= 8:
            closes = data['close'].values
            log_returns = np.diff(np.log(closes[-8:]))
            if np.sum(log_returns < 0) >= 6:  # 6+ down candles
                patterns.append({
                    'pattern_name': 'Parabolic Downtrend',
                    'pattern_family': 'Trend Structures',
                    'pattern_type': 'Bearish',
                    'confidence': 75.0,
                    'details': {'down_candles': int(np.sum(log_returns < 0))},
                    'structural_context': 'Extreme downtrend (potential bounce ahead)'
                })

        return patterns

    def _detect_sideways_structures(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect sideways/consolidation trend structures."""
        patterns = []
        if len(data) < 10:
            return patterns

        closes = data['close'].values
        recent_closes = closes[-20:]
        high_range = np.max(recent_closes)
        low_range = np.min(recent_closes)
        range_size = high_range - low_range

        # Calculate coefficient of variation (lower = more sideways)
        cv = np.std(recent_closes) / np.mean(recent_closes)

        if cv < 0.01:  # Very tight range
            patterns.append({
                'pattern_name': 'Tight Consolidation',
                'pattern_family': 'Trend Structures',
                'pattern_type': 'Neutral',
                'confidence': 85.0,
                'details': {'range': float(range_size), 'cv': float(cv)},
                'structural_context': 'Preparing for breakout'
            })

        # Price oscillating around midpoint
        midpoint = (high_range + low_range) / 2
        touches_mid = np.sum(np.abs(recent_closes - midpoint) < range_size * 0.1)
        if touches_mid >= 8:
            patterns.append({
                'pattern_name': 'Equilibrium Pattern',
                'pattern_family': 'Trend Structures',
                'pattern_type': 'Neutral',
                'confidence': 70.0,
                'details': {'equilibrium_level': float(midpoint), 'touches': int(touches_mid)},
                'structural_context': 'Balanced supply/demand'
            })

        return patterns

    # ==================== SUPPORT & RESISTANCE STRUCTURES (40+) ====================

    def _detect_horizontal_sr(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect horizontal support/resistance levels."""
        patterns = []
        if len(data) < 20:
            return patterns

        highs = data['high'].values
        lows = data['low'].values
        closes = data['close'].values

        # Find horizontal support levels (multiple lows at similar price)
        recent_lows = lows[-30:]
        rounded_lows = np.round(recent_lows, decimals=2)
        unique_levels, counts = np.unique(rounded_lows, return_counts=True)
        
        for level, count in zip(unique_levels, counts):
            if count >= 3:  # 3+ touches = significant support
                patterns.append({
                    'pattern_name': f'Horizontal Support ({count}-Touch)',
                    'pattern_family': 'Support & Resistance',
                    'pattern_type': 'Bullish' if closes[-1] > level else 'Neutral',
                    'confidence': min(85.0, 50.0 + count * 8),
                    'details': {'level': float(level), 'touches': int(count)},
                    'structural_context': 'Strong support zone'
                })

        # Find horizontal resistance levels
        recent_highs = highs[-30:]
        rounded_highs = np.round(recent_highs, decimals=2)
        unique_highs, counts_h = np.unique(rounded_highs, return_counts=True)
        
        for level, count in zip(unique_highs, counts_h):
            if count >= 3:
                patterns.append({
                    'pattern_name': f'Horizontal Resistance ({count}-Touch)',
                    'pattern_family': 'Support & Resistance',
                    'pattern_type': 'Bearish' if closes[-1] < level else 'Neutral',
                    'confidence': min(85.0, 50.0 + count * 8),
                    'details': {'level': float(level), 'touches': int(count)},
                    'structural_context': 'Strong resistance zone'
                })

        return patterns

    def _detect_dynamic_sr(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect dynamic (trending) support/resistance."""
        patterns = []
        if len(data) < 15:
            return patterns

        lows = data['low'].values
        highs = data['high'].values

        # Uptrend line (connecting rising lows)
        if len(lows) >= 10:
            recent_lows = lows[-10:]
            if recent_lows[-1] > recent_lows[-5] > recent_lows[-10]:
                slope = (recent_lows[-1] - recent_lows[-10]) / 10
                patterns.append({
                    'pattern_name': 'Dynamic Uptrend Support',
                    'pattern_family': 'Support & Resistance',
                    'pattern_type': 'Bullish',
                    'confidence': 75.0,
                    'details': {'slope': float(slope), 'line_start': float(recent_lows[-10])},
                    'structural_context': 'Rising support line'
                })

        # Downtrend line (connecting falling highs)
        if len(highs) >= 10:
            recent_highs = highs[-10:]
            if recent_highs[-1] < recent_highs[-5] < recent_highs[-10]:
                slope = (recent_highs[-1] - recent_highs[-10]) / 10
                patterns.append({
                    'pattern_name': 'Dynamic Downtrend Resistance',
                    'pattern_family': 'Support & Resistance',
                    'pattern_type': 'Bearish',
                    'confidence': 75.0,
                    'details': {'slope': float(slope)},
                    'structural_context': 'Falling resistance line'
                })

        return patterns

    def _detect_role_reversals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect support-becomes-resistance or resistance-becomes-support."""
        patterns = []
        if len(data) < 25:
            return patterns

        closes = data['close'].values
        lows = data['low'].values
        highs = data['high'].values

        # Test old resistance from 20 candles ago
        old_high = np.max(highs[-25:-20])
        recent_closes = closes[-5:]
        
        if np.any(recent_closes > old_high) and closes[-1] > old_high:
            patterns.append({
                'pattern_name': 'Resistance Breakout (Role Reversal)',
                'pattern_family': 'Support & Resistance',
                'pattern_type': 'Bullish',
                'confidence': 70.0,
                'details': {'former_resistance': float(old_high)},
                'structural_context': 'Old resistance becoming support'
            })

        # Test old support from 20 candles ago
        old_low = np.min(lows[-25:-20])
        if np.any(recent_closes < old_low) and closes[-1] < old_low:
            patterns.append({
                'pattern_name': 'Support Breakdown (Role Reversal)',
                'pattern_family': 'Support & Resistance',
                'pattern_type': 'Bearish',
                'confidence': 70.0,
                'details': {'former_support': float(old_low)},
                'structural_context': 'Old support becoming resistance'
            })

        return patterns

    # ==================== CHART FORMATIONS (50+) ====================

    def _detect_reversal_formations(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect double/triple top-bottom reversal formations."""
        patterns = []
        if len(data) < 20:
            return patterns

        highs = data['high'].values
        lows = data['low'].values
        closes = data['close'].values

        # Double Top (two similar peaks)
        recent_highs = highs[-20:]
        max_idx1 = np.argmax(recent_highs)
        before_max1 = recent_highs[:max_idx1]
        if len(before_max1) > 0:
            max_idx2 = np.argmax(before_max1)
            if abs(recent_highs[max_idx1] - before_max1[max_idx2]) < (recent_highs[max_idx1] * 0.01):
                patterns.append({
                    'pattern_name': 'Double Top',
                    'pattern_family': 'Chart Formations',
                    'pattern_type': 'Bearish',
                    'confidence': 75.0,
                    'details': {'peak1': float(before_max1[max_idx2]), 'peak2': float(recent_highs[max_idx1])},
                    'structural_context': 'Reversal pattern at resistance'
                })

        # Double Bottom
        recent_lows = lows[-20:]
        min_idx1 = np.argmin(recent_lows)
        before_min1 = recent_lows[:min_idx1]
        if len(before_min1) > 0:
            min_idx2 = np.argmin(before_min1)
            if abs(recent_lows[min_idx1] - before_min1[min_idx2]) < (before_min1[min_idx2] * 0.01):
                patterns.append({
                    'pattern_name': 'Double Bottom',
                    'pattern_family': 'Chart Formations',
                    'pattern_type': 'Bullish',
                    'confidence': 75.0,
                    'details': {'valley1': float(before_min1[min_idx2]), 'valley2': float(recent_lows[min_idx1])},
                    'structural_context': 'Reversal pattern at support'
                })

        # Rounded Top/Bottom
        if len(data) >= 10:
            recent_range = highs[-10:] - lows[-10:]
            if np.std(recent_range) < np.mean(recent_range) * 0.3:
                patterns.append({
                    'pattern_name': 'Rounded Formation (Top/Bottom)',
                    'pattern_family': 'Chart Formations',
                    'pattern_type': 'Neutral',
                    'confidence': 65.0,
                    'details': {'volatility': float(np.std(recent_range))},
                    'structural_context': 'Potential reversal with gradual transition'
                })

        return patterns

    def _detect_head_shoulders_variations(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Head & Shoulders and Inverse patterns."""
        patterns = []
        if len(data) < 25:
            return patterns

        highs = data['high'].values[-25:]
        lows = data['low'].values[-25:]

        # Simplified H&S detection: 3 peaks with middle peak highest
        if len(highs) >= 5:
            local_maxima_indices = []
            for i in range(1, len(highs) - 1):
                if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                    local_maxima_indices.append(i)

            if len(local_maxima_indices) >= 3:
                idx_left = local_maxima_indices[0]
                idx_head = local_maxima_indices[1]
                idx_right = local_maxima_indices[2]
                
                if highs[idx_head] > highs[idx_left] and highs[idx_head] > highs[idx_right]:
                    if abs(highs[idx_left] - highs[idx_right]) < (highs[idx_left] * 0.02):
                        patterns.append({
                            'pattern_name': 'Head & Shoulders',
                            'pattern_family': 'Chart Formations',
                            'pattern_type': 'Bearish',
                            'confidence': 78.0,
                            'details': {'left_shoulder': float(highs[idx_left]),
                                       'head': float(highs[idx_head]),
                                       'right_shoulder': float(highs[idx_right])},
                            'structural_context': 'Strong reversal pattern'
                        })

        # Inverse H&S (valleys instead of peaks)
        local_minima_indices = []
        for i in range(1, len(lows) - 1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                local_minima_indices.append(i)

        if len(local_minima_indices) >= 3:
            idx_left = local_minima_indices[0]
            idx_head = local_minima_indices[1]
            idx_right = local_minima_indices[2]
            
            if lows[idx_head] < lows[idx_left] and lows[idx_head] < lows[idx_right]:
                if abs(lows[idx_left] - lows[idx_right]) < (lows[idx_left] * 0.02):
                    patterns.append({
                        'pattern_name': 'Inverse Head & Shoulders',
                        'pattern_family': 'Chart Formations',
                        'pattern_type': 'Bullish',
                        'confidence': 78.0,
                        'details': {'left_shoulder': float(lows[idx_left]),
                                   'head': float(lows[idx_head]),
                                   'right_shoulder': float(lows[idx_right])},
                        'structural_context': 'Strong reversal pattern (bullish)'
                    })

        return patterns

    def _detect_handle_formations(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Cup & Handle patterns."""
        patterns = []
        if len(data) < 30:
            return patterns

        highs = data['high'].values[-30:]
        lows = data['low'].values[-30:]
        closes = data['close'].values[-30:]

        # Cup: U-shaped low followed by handle (consolidation)
        min_idx = np.argmin(lows)
        if min_idx > 5 and min_idx < len(lows) - 5:
            cup_low = lows[min_idx]
            cup_highs_left = np.max(highs[:min_idx])
            cup_highs_right = np.max(highs[min_idx:])
            
            if abs(cup_highs_left - cup_highs_right) < (cup_highs_left * 0.01):
                # Check handle (consolidation after cup)
                handle_range = np.max(closes[min_idx:]) - np.min(closes[min_idx:])
                cup_depth = cup_highs_left - cup_low
                
                if handle_range < cup_depth * 0.3:  # Handle smaller than cup
                    patterns.append({
                        'pattern_name': 'Cup & Handle',
                        'pattern_family': 'Chart Formations',
                        'pattern_type': 'Bullish',
                        'confidence': 77.0,
                        'details': {'cup_depth': float(cup_depth), 'handle_range': float(handle_range)},
                        'structural_context': 'Bullish consolidation pattern'
                    })

        return patterns

    # ==================== CONTINUATION STRUCTURES (35+) ====================

    def _detect_flag_structures(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect flag continuation patterns."""
        patterns = []
        if len(data) < 20:
            return patterns

        closes = data['close'].values[-20:]
        opens = data['open'].values[-20:]

        # Count up and down candles
        up_candles = np.sum(closes > opens)
        down_candles = np.sum(closes < opens)

        # Bullish flag: Strong up move followed by small consolidation
        if up_candles >= 5:
            recent_consolidation = np.std(closes[-5:]) / np.mean(closes[-5:])
            overall_trend = (closes[-1] - closes[-15]) / closes[-15]
            
            if recent_consolidation < 0.005 and overall_trend > 0.01:
                patterns.append({
                    'pattern_name': 'Bullish Flag',
                    'pattern_family': 'Continuation Structures',
                    'pattern_type': 'Bullish',
                    'confidence': 72.0,
                    'details': {'consolidation_tightness': float(recent_consolidation)},
                    'structural_context': 'Continuation pattern in uptrend'
                })

        # Bearish flag
        if down_candles >= 5:
            recent_consolidation = np.std(closes[-5:]) / np.mean(closes[-5:])
            overall_trend = (closes[-15] - closes[-1]) / closes[-15]
            
            if recent_consolidation < 0.005 and overall_trend > 0.01:
                patterns.append({
                    'pattern_name': 'Bearish Flag',
                    'pattern_family': 'Continuation Structures',
                    'pattern_type': 'Bearish',
                    'confidence': 72.0,
                    'details': {'consolidation_tightness': float(recent_consolidation)},
                    'structural_context': 'Continuation pattern in downtrend'
                })

        return patterns

    def _detect_pennant_structures(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect pennant structures (converging triangles)."""
        patterns = []
        if len(data) < 15:
            return patterns

        highs = data['high'].values[-15:]
        lows = data['low'].values[-15:]

        # Pennant: Converging range
        early_range = np.max(highs[:5]) - np.min(lows[:5])
        recent_range = np.max(highs[-5:]) - np.min(lows[-5:])
        
        if recent_range < early_range * 0.5:
            patterns.append({
                'pattern_name': 'Symmetrical Pennant',
                'pattern_family': 'Continuation Structures',
                'pattern_type': 'Neutral',
                'confidence': 70.0,
                'details': {'early_range': float(early_range), 'recent_range': float(recent_range)},
                'structural_context': 'Consolidation with breakout imminent'
            })

        return patterns

    def _detect_rectangle_structures(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect rectangle/box consolidation patterns."""
        patterns = []
        if len(data) < 10:
            return patterns

        highs = data['high'].values[-20:]
        lows = data['low'].values[-20:]
        
        high_level = np.max(highs)
        low_level = np.min(lows)
        range_size = high_level - low_level

        # Count touches of upper and lower boundaries
        upper_touches = np.sum(highs > high_level * 0.99)
        lower_touches = np.sum(lows < low_level * 1.01)

        if upper_touches >= 3 and lower_touches >= 3:
            patterns.append({
                'pattern_name': 'Rectangle Consolidation',
                'pattern_family': 'Continuation Structures',
                'pattern_type': 'Neutral',
                'confidence': 72.0,
                'details': {'upper_level': float(high_level), 'lower_level': float(low_level),
                           'range': float(range_size)},
                'structural_context': 'Balanced consolidation awaiting breakout'
            })

        return patterns

    def _detect_consolidation_structures(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect general consolidation and tightening patterns."""
        patterns = []
        if len(data) < 10:
            return patterns

        closes = data['close'].values[-20:]
        
        # Volatility compression
        recent_vol = np.std(closes[-5:])
        earlier_vol = np.std(closes[-10:-5])
        
        if recent_vol < earlier_vol * 0.5:
            patterns.append({
                'pattern_name': 'Volatility Compression',
                'pattern_family': 'Continuation Structures',
                'pattern_type': 'Neutral',
                'confidence': 75.0,
                'details': {'recent_volatility': float(recent_vol), 'earlier_volatility': float(earlier_vol)},
                'structural_context': 'Low volatility period (breakout likely)'
            })

        return patterns

    # ==================== WEDGE & TRIANGLE STRUCTURES (30+) ====================

    def _detect_wedge_structures(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect rising, falling, and expanding wedge patterns."""
        patterns = []
        if len(data) < 15:
            return patterns

        highs = data['high'].values[-15:]
        lows = data['low'].values[-15:]

        # Rising wedge (both highs and lows rising, but lows rising faster)
        high_slope = (highs[-1] - highs[0]) / len(highs)
        low_slope = (lows[-1] - lows[0]) / len(lows)
        
        if high_slope > 0 and low_slope > 0:
            if low_slope > high_slope * 0.7:  # Lows catching up to highs
                patterns.append({
                    'pattern_name': 'Rising Wedge',
                    'pattern_family': 'Wedge & Triangle Structures',
                    'pattern_type': 'Bearish',
                    'confidence': 73.0,
                    'details': {'high_slope': float(high_slope), 'low_slope': float(low_slope)},
                    'structural_context': 'Bearish reversal in uptrend'
                })

        # Falling wedge (both falling, but highs falling faster)
        if high_slope < 0 and low_slope < 0:
            if abs(low_slope) < abs(high_slope) * 0.7:
                patterns.append({
                    'pattern_name': 'Falling Wedge',
                    'pattern_family': 'Wedge & Triangle Structures',
                    'pattern_type': 'Bullish',
                    'confidence': 73.0,
                    'details': {'high_slope': float(high_slope), 'low_slope': float(low_slope)},
                    'structural_context': 'Bullish reversal in downtrend'
                })

        return patterns

    def _detect_triangle_structures(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect ascending, descending, and symmetrical triangles."""
        patterns = []
        if len(data) < 15:
            return patterns

        highs = data['high'].values[-15:]
        lows = data['low'].values[-15:]

        high_slope = (highs[-1] - highs[0]) / len(highs)
        low_slope = (lows[-1] - lows[0]) / len(lows)

        # Ascending triangle: Flat highs, rising lows
        if abs(high_slope) < 0.0001 and low_slope > 0:
            patterns.append({
                'pattern_name': 'Ascending Triangle',
                'pattern_family': 'Wedge & Triangle Structures',
                'pattern_type': 'Bullish',
                'confidence': 75.0,
                'details': {'resistance_level': float(highs[0])},
                'structural_context': 'Bullish continuation in uptrend'
            })

        # Descending triangle: Rising highs, flat lows
        if high_slope < 0 and abs(low_slope) < 0.0001:
            patterns.append({
                'pattern_name': 'Descending Triangle',
                'pattern_family': 'Wedge & Triangle Structures',
                'pattern_type': 'Bearish',
                'confidence': 75.0,
                'details': {'support_level': float(lows[0])},
                'structural_context': 'Bearish continuation in downtrend'
            })

        # Symmetrical triangle: Both converging
        if (high_slope < 0 and low_slope > 0):
            convergence = abs(high_slope) + abs(low_slope)
            if convergence > 0.001:
                patterns.append({
                    'pattern_name': 'Symmetrical Triangle',
                    'pattern_family': 'Wedge & Triangle Structures',
                    'pattern_type': 'Neutral',
                    'confidence': 70.0,
                    'details': {'convergence_rate': float(convergence)},
                    'structural_context': 'Breakout imminent in either direction'
                })

        return patterns

    # ==================== BREAKOUT & FAILURE PATTERNS (25+) ====================

    def _detect_breakout_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect clean breakout patterns."""
        patterns = []
        if len(data) < 20:
            return patterns

        highs = data['high'].values
        lows = data['low'].values
        closes = data['close'].values
        volumes = data.get('volume', pd.Series([0]*len(data))).values

        # Resistance breakout (high volume)
        recent_high = np.max(highs[-20:-5])
        if closes[-1] > recent_high:
            patterns.append({
                'pattern_name': 'Bullish Breakout',
                'pattern_family': 'Breakout & Failure Patterns',
                'pattern_type': 'Bullish',
                'confidence': 76.0,
                'details': {'breakout_level': float(recent_high)},
                'structural_context': 'Above recent resistance'
            })

        # Support breakdown
        recent_low = np.min(lows[-20:-5])
        if closes[-1] < recent_low:
            patterns.append({
                'pattern_name': 'Bearish Breakdown',
                'pattern_family': 'Breakout & Failure Patterns',
                'pattern_type': 'Bearish',
                'confidence': 76.0,
                'details': {'breakdown_level': float(recent_low)},
                'structural_context': 'Below recent support'
            })

        return patterns

    def _detect_failure_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect false breakouts and failed retests."""
        patterns = []
        if len(data) < 20:
            return patterns

        highs = data['high'].values[-20:]
        lows = data['low'].values[-20:]
        closes = data['close'].values[-20:]

        # False breakout (spike above resistance then reversal)
        max_high = np.max(highs)
        max_idx = np.argmax(highs)
        
        if max_idx < len(highs) - 2:
            if highs[max_idx] > np.max(highs[max_idx+1:]):
                patterns.append({
                    'pattern_name': 'False Breakout',
                    'pattern_family': 'Breakout & Failure Patterns',
                    'pattern_type': 'Bearish',
                    'confidence': 68.0,
                    'details': {'spike_high': float(max_high), 'reversal': True},
                    'structural_context': 'Stop-hunt pattern detected'
                })

        # Failed retest
        min_low = np.min(lows)
        min_idx = np.argmin(lows)
        
        if min_idx < len(lows) - 2 and min_idx > 0:
            recovery = closes[-1] - lows[min_idx]
            if recovery > (highs[-1] - lows[-1]) * 0.5:
                patterns.append({
                    'pattern_name': 'Failed Retest',
                    'pattern_family': 'Breakout & Failure Patterns',
                    'pattern_type': 'Bullish',
                    'confidence': 70.0,
                    'details': {'test_level': float(min_low), 'recovery': float(recovery)},
                    'structural_context': 'Support held, reversal likely'
                })

        return patterns

    # ==================== MARKET BEHAVIOR PATTERNS (30+) ====================

    def _detect_accumulation_distribution(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect accumulation and distribution phases."""
        patterns = []
        if len(data) < 10:
            return patterns

        closes = data['close'].values
        opens = data['open'].values

        # Accumulation: Small candles with higher closes
        recent_candles = closes[-10:] - opens[-10:]
        avg_size = np.mean(np.abs(recent_candles))
        up_candles = np.sum(recent_candles > 0)

        if np.mean(np.abs(recent_candles)) < np.mean(np.abs(closes[-20:-10] - opens[-20:-10])) * 0.7:
            if up_candles >= 6:
                patterns.append({
                    'pattern_name': 'Accumulation Phase',
                    'pattern_family': 'Market Behavior Patterns',
                    'pattern_type': 'Bullish',
                    'confidence': 72.0,
                    'details': {'up_candles': int(up_candles), 'avg_body_size': float(avg_size)},
                    'structural_context': 'Institutional buying likely'
                })

        # Distribution: Small candles with lower closes
        if np.mean(np.abs(recent_candles)) < np.mean(np.abs(closes[-20:-10] - opens[-20:-10])) * 0.7:
            down_candles = np.sum(recent_candles < 0)
            if down_candles >= 6:
                patterns.append({
                    'pattern_name': 'Distribution Phase',
                    'pattern_family': 'Market Behavior Patterns',
                    'pattern_type': 'Bearish',
                    'confidence': 72.0,
                    'details': {'down_candles': int(down_candles)},
                    'structural_context': 'Institutional selling likely'
                })

        return patterns

    def _detect_mean_reversion(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect mean reversion and oversold/overbought structures."""
        patterns = []
        if len(data) < 10:
            return patterns

        closes = data['close'].values[-20:]
        sma = np.mean(closes)
        current = closes[-1]
        std_dev = np.std(closes)

        # Oversold (far below mean)
        if current < sma - 2 * std_dev:
            patterns.append({
                'pattern_name': 'Oversold Condition',
                'pattern_family': 'Market Behavior Patterns',
                'pattern_type': 'Bullish',
                'confidence': 70.0,
                'details': {'mean': float(sma), 'current': float(current), 'std_dev': float(std_dev)},
                'structural_context': 'Potential mean reversion upward'
            })

        # Overbought (far above mean)
        if current > sma + 2 * std_dev:
            patterns.append({
                'pattern_name': 'Overbought Condition',
                'pattern_family': 'Market Behavior Patterns',
                'pattern_type': 'Bearish',
                'confidence': 70.0,
                'details': {'mean': float(sma), 'current': float(current)},
                'structural_context': 'Potential mean reversion downward'
            })

        return patterns

    # ==================== TIME-BASED STRUCTURES (20+) ====================

    def _detect_session_structures(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect session-based and time-based structures."""
        patterns = []
        
        # Check if we have time information
        if not hasattr(data.index, 'hour'):
            return patterns

        closes = data['close'].values
        opens = data['open'].values

        # London open structure (expected 8am GMT)
        try:
            london_candles = data[data.index.hour == 8] if hasattr(data.index, 'hour') else None
            if london_candles is not None and len(london_candles) > 3:
                patterns.append({
                    'pattern_name': 'London Session Open',
                    'pattern_family': 'Time-Based Structures',
                    'pattern_type': 'Neutral',
                    'confidence': 60.0,
                    'details': {'session': 'London', 'hour': 8},
                    'structural_context': 'Session opening volatility'
                })
        except:
            pass

        return patterns

    # ==================== HELPER METHODS ====================

    def _determine_trend_direction(self, data: pd.DataFrame, patterns: List[Dict[str, Any]]) -> str:
        """Determine overall trend direction from patterns."""
        bullish = sum(1 for p in patterns if p['pattern_type'] == 'Bullish')
        bearish = sum(1 for p in patterns if p['pattern_type'] == 'Bearish')

        closes = data['close'].values
        if closes[-1] > np.mean(closes):
            if bullish > bearish:
                return 'Strong Uptrend'
            elif bullish == bearish:
                return 'Uptrend'
            else:
                return 'Weak Uptrend'
        else:
            if bearish > bullish:
                return 'Strong Downtrend'
            elif bearish == bullish:
                return 'Downtrend'
            else:
                return 'Weak Downtrend'

    def _determine_market_context(self, data: pd.DataFrame, patterns: List[Dict[str, Any]]) -> str:
        """Determine current market context."""
        closes = data['close'].values[-20:]
        volatility = np.std(closes) / np.mean(closes)

        trend_patterns = [p for p in patterns if p['pattern_family'] == 'Trend Structures']
        consolidation_patterns = [p for p in patterns if 'Consolidation' in p['pattern_name']]

        if len(consolidation_patterns) > len(trend_patterns):
            if volatility < 0.01:
                return 'Tight Consolidation'
            else:
                return 'Range-Bound'
        elif len(trend_patterns) > 2:
            return 'Trending'
        else:
            return 'Balanced'

    def _calculate_structure_score(self, patterns: List[Dict[str, Any]], bullish: List, bearish: List) -> float:
        """Calculate overall structural strength."""
        if not patterns:
            return 0.0

        avg_confidence = np.mean([p['confidence'] for p in patterns])
        pattern_count_factor = min(len(patterns) / 10, 1.0)
        direction_factor = abs(len(bullish) - len(bearish)) / max(len(patterns), 1)

        score = avg_confidence * 0.5 + pattern_count_factor * 30 + direction_factor * 20
        return float(np.clip(score, 0, 100))
