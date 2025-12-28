"""
Multi-candle price action and market structure analysis.

This module analyzes sequences of candles over time to understand:
- Directional control (higher highs/lows vs lower highs/lows)
- Structural patterns (impulse, correction, continuation)
- Price momentum and persistence
- Market structure breaks (BOS) and changes of character (CHOCH)
- Candle flow behavior (compression, expansion, rejection)

Unlike candlestick pattern recognition which looks at individual candles,
this layer examines how price FLOWS across multiple candles to identify
behavioral shifts, structural integrity, and directional bias.

Works across all asset classes: Forex, Synthetics, Indices, Commodities, Crypto.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from core.logger import get_logger


class MultiCandlePriceAction:
    """
    Analyzes multi-candle price action and market structure.
    
    This is a dedicated behavioral layer separate from:
    - Individual candlestick patterns (doji, engulfing, hammer, etc.)
    - Indicator-based trend analysis (moving averages, RSI, MACD, etc.)
    - Statistical analysis (distributions, correlations, etc.)
    
    This layer focuses on HOW price MOVES over time.
    """
    
    def __init__(self):
        """Initialize price action analyzer."""
        self.logger = get_logger()
    
    def analyze(self, data: pd.DataFrame, window_size: int = 10) -> Dict[str, Any]:
        """
        Comprehensive multi-candle price action analysis.
        
        Args:
            data: OHLCV DataFrame
            window_size: Number of candles to analyze in windows (default 10)
            
        Returns:
            Dict with directional_bias, structure_strength, momentum_condition, confidence
        """
        try:
            if len(data) < window_size:
                return {
                    'directional_bias': 'neutral',
                    'structure_strength': 'weak',
                    'momentum_condition': 'stable',
                    'confidence': 0.0,
                    'explanation': 'Insufficient data for multi-candle analysis',
                    'analysis_details': {}
                }
            
            analysis = {}
            
            # Core structural analysis
            analysis['hh_hl_sequence'] = self._analyze_higher_highs_lows(data, window_size)
            analysis['lh_ll_sequence'] = self._analyze_lower_highs_lows(data, window_size)
            analysis['structure_break'] = self._detect_break_of_structure(data, window_size)
            analysis['change_of_character'] = self._detect_change_of_character(data, window_size)
            
            # Impulse and correction patterns
            analysis['impulse_correction'] = self._detect_impulse_correction_continuation(data, window_size)
            analysis['momentum_persistence'] = self._analyze_momentum_persistence(data, window_size)
            
            # Compression and expansion
            analysis['compression_expansion'] = self._analyze_compression_expansion(data, window_size)
            
            # Candle flow analysis
            analysis['candle_dominance'] = self._analyze_candle_dominance(data, window_size)
            analysis['candle_body_trend'] = self._analyze_candle_body_expansion(data, window_size)
            analysis['wick_rejection'] = self._analyze_wick_rejection_pattern(data, window_size)
            
            # Structural patterns
            analysis['stair_step_movement'] = self._detect_stair_step_pattern(data, window_size)
            analysis['fake_breakout'] = self._detect_fake_breakout(data, window_size)
            analysis['channel_behavior'] = self._analyze_channel_formation(data, window_size)
            analysis['micro_trend'] = self._detect_micro_trend(data, window_size)
            analysis['range_versus_trend'] = self._analyze_range_vs_trend(data, window_size)
            
            # Calculate composite metrics
            directional_bias = self._calculate_directional_bias(analysis)
            structure_strength = self._calculate_structure_strength(analysis)
            momentum_condition = self._calculate_momentum_condition(analysis)
            confidence = self._calculate_confidence(analysis)
            
            return {
                'directional_bias': directional_bias,
                'structure_strength': structure_strength,
                'momentum_condition': momentum_condition,
                'confidence': confidence,
                'analysis_details': analysis,
                'explanation': self._generate_explanation(
                    directional_bias, structure_strength, momentum_condition, analysis
                )
            }
        
        except Exception as e:
            self.logger.error(f"Error in multi-candle price action analysis: {e}")
            return {
                'directional_bias': 'neutral',
                'structure_strength': 'weak',
                'momentum_condition': 'stable',
                'confidence': 0.0,
                'error': str(e),
                'analysis_details': {}
            }
    
    def _analyze_higher_highs_lows(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Detect higher highs and higher lows sequence (bullish structure).
        
        Returns: Dict with pattern details and strength (0-100)
        """
        try:
            recent = data.tail(window_size)
            highs = recent['High'].values
            lows = recent['Low'].values
            
            # Count consecutive higher highs and higher lows
            hh_count = 0
            hl_count = 0
            
            for i in range(1, len(highs)):
                if highs[i] > highs[i-1]:
                    hh_count += 1
                if lows[i] > lows[i-1]:
                    hl_count += 1
            
            # Strength based on consistency
            hh_strength = (hh_count / (len(highs) - 1)) * 100 if len(highs) > 1 else 0
            hl_strength = (hl_count / (len(lows) - 1)) * 100 if len(lows) > 1 else 0
            
            # Both HH and HL needed for strong uptrend
            combined_strength = (hh_strength + hl_strength) / 2
            
            return {
                'pattern_detected': 'HH/HL' if combined_strength > 60 else 'Mixed',
                'higher_highs_percent': round(hh_strength, 1),
                'higher_lows_percent': round(hl_strength, 1),
                'strength': round(combined_strength, 1),
                'trend_quality': 'Strong' if combined_strength > 75 else 'Moderate' if combined_strength > 50 else 'Weak'
            }
        except Exception as e:
            self.logger.debug(f"HH/HL analysis error: {e}")
            return {'pattern_detected': 'Error', 'strength': 0}
    
    def _analyze_lower_highs_lows(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Detect lower highs and lower lows sequence (bearish structure).
        
        Returns: Dict with pattern details and strength (0-100)
        """
        try:
            recent = data.tail(window_size)
            highs = recent['High'].values
            lows = recent['Low'].values
            
            # Count consecutive lower highs and lower lows
            lh_count = 0
            ll_count = 0
            
            for i in range(1, len(highs)):
                if highs[i] < highs[i-1]:
                    lh_count += 1
                if lows[i] < lows[i-1]:
                    ll_count += 1
            
            # Strength based on consistency
            lh_strength = (lh_count / (len(highs) - 1)) * 100 if len(highs) > 1 else 0
            ll_strength = (ll_count / (len(lows) - 1)) * 100 if len(lows) > 1 else 0
            
            # Both LH and LL needed for strong downtrend
            combined_strength = (lh_strength + ll_strength) / 2
            
            return {
                'pattern_detected': 'LH/LL' if combined_strength > 60 else 'Mixed',
                'lower_highs_percent': round(lh_strength, 1),
                'lower_lows_percent': round(ll_strength, 1),
                'strength': round(combined_strength, 1),
                'trend_quality': 'Strong' if combined_strength > 75 else 'Moderate' if combined_strength > 50 else 'Weak'
            }
        except Exception as e:
            self.logger.debug(f"LH/LL analysis error: {e}")
            return {'pattern_detected': 'Error', 'strength': 0}
    
    def _detect_break_of_structure(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Detect break of market structure (BOS).
        
        BOS occurs when price violates established structural highs or lows,
        indicating a potential shift in directional control.
        """
        try:
            recent = data.tail(window_size + 5)  # Extra candles for context
            
            if len(recent) < 5:
                return {'bos_detected': False, 'type': 'None', 'strength': 0}
            
            # Find recent structure highs and lows
            struct_high = recent['High'].iloc[:-5].max()
            struct_low = recent['Low'].iloc[:-5].min()
            
            latest_high = recent['High'].iloc[-1]
            latest_low = recent['Low'].iloc[-1]
            
            bos_bullish = latest_high > struct_high
            bos_bearish = latest_low < struct_low
            
            if bos_bullish and not bos_bearish:
                return {
                    'bos_detected': True,
                    'type': 'Bullish BOS',
                    'strength': 75,
                    'interpretation': 'Break above previous structural resistance'
                }
            elif bos_bearish and not bos_bullish:
                return {
                    'bos_detected': True,
                    'type': 'Bearish BOS',
                    'strength': 75,
                    'interpretation': 'Break below previous structural support'
                }
            else:
                return {
                    'bos_detected': False,
                    'type': 'None',
                    'strength': 0,
                    'interpretation': 'Structure intact'
                }
        
        except Exception as e:
            self.logger.debug(f"BOS detection error: {e}")
            return {'bos_detected': False, 'type': 'Error', 'strength': 0}
    
    def _detect_change_of_character(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Detect change of character (CHOCH).
        
        CHOCH occurs when the pattern of price action fundamentally changes,
        such as from HH/HL to LH/LL or vice versa.
        """
        try:
            # Compare first half and second half of window
            half = window_size // 2
            first_half = data.tail(window_size).head(half)
            second_half = data.tail(half)
            
            # First half trend
            first_hh = sum(1 for i in range(1, len(first_half)) 
                          if first_half['High'].iloc[i] > first_half['High'].iloc[i-1])
            first_ll = sum(1 for i in range(1, len(first_half)) 
                          if first_half['Low'].iloc[i] < first_half['Low'].iloc[i-1])
            
            # Second half trend
            second_hh = sum(1 for i in range(1, len(second_half)) 
                           if second_half['High'].iloc[i] > second_half['High'].iloc[i-1])
            second_ll = sum(1 for i in range(1, len(second_half)) 
                           if second_half['Low'].iloc[i] < second_half['Low'].iloc[i-1])
            
            # Detect reversal
            first_trend = 'Bullish' if first_hh > first_ll else 'Bearish' if first_ll > first_hh else 'Mixed'
            second_trend = 'Bullish' if second_hh > second_ll else 'Bearish' if second_ll > second_hh else 'Mixed'
            
            choch_detected = first_trend != second_trend and first_trend != 'Mixed' and second_trend != 'Mixed'
            
            return {
                'choch_detected': choch_detected,
                'previous_character': first_trend,
                'current_character': second_trend,
                'strength': 80 if choch_detected else 20,
                'interpretation': f'Change from {first_trend} to {second_trend}' if choch_detected else 'Character consistent'
            }
        
        except Exception as e:
            self.logger.debug(f"CHOCH detection error: {e}")
            return {'choch_detected': False, 'strength': 0}
    
    def _detect_impulse_correction_continuation(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Detect impulse (strong directional move), correction, and continuation patterns.
        
        Impulse: Strong move in one direction (large bodies, minimal wicks)
        Correction: Pullback against trend (smaller moves, consolidation)
        Continuation: Resumption of trend after correction
        """
        try:
            recent = data.tail(window_size)
            
            # Measure candle body sizes and ranges
            bodies = np.abs(recent['Close'] - recent['Open']).values
            wicks = np.maximum(
                recent['High'] - np.maximum(recent['Close'], recent['Open']),
                np.minimum(recent['Close'], recent['Open']) - recent['Low']
            ).values
            
            avg_body = bodies.mean()
            avg_wick = wicks.mean()
            
            # Impulse characteristics: large bodies, small wicks
            body_to_wick_ratio = avg_body / (avg_wick + 0.0001)  # Avoid division by zero
            
            if body_to_wick_ratio > 2.0:
                # Likely in impulse phase
                pattern = 'Impulse'
                strength = 70
            elif body_to_wick_ratio < 0.8:
                # Likely in correction/consolidation
                pattern = 'Correction/Consolidation'
                strength = 60
            else:
                # Mixed
                pattern = 'Mixed'
                strength = 40
            
            return {
                'pattern': pattern,
                'strength': strength,
                'body_to_wick_ratio': round(body_to_wick_ratio, 2),
                'avg_body_size': round(avg_body, 4),
                'interpretation': 'Strong directional move' if pattern == 'Impulse' 
                                 else 'Consolidation phase' if pattern == 'Correction/Consolidation'
                                 else 'Transitional phase'
            }
        
        except Exception as e:
            self.logger.debug(f"Impulse/correction analysis error: {e}")
            return {'pattern': 'Error', 'strength': 0}
    
    def _analyze_momentum_persistence(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Analyze how well momentum is persisting across candles.
        
        Persistent momentum: Consistent directional candles, low pullback depth
        Fading momentum: Alternating direction, increased pullbacks
        """
        try:
            recent = data.tail(window_size)
            
            # Determine direction of each candle (bullish/bearish)
            candle_directions = np.array([
                1 if close > open_ else -1 if close < open_ else 0
                for open_, close in zip(recent['Open'], recent['Close'])
            ])
            
            # Count consecutive moves in same direction
            direction_changes = sum(1 for i in range(1, len(candle_directions)) 
                                   if candle_directions[i] != candle_directions[i-1] 
                                   and candle_directions[i] != 0)
            
            # Lower direction changes = more persistent
            persistence_ratio = (1 - direction_changes / (len(candle_directions) - 1)) * 100 if len(candle_directions) > 1 else 0
            
            if persistence_ratio > 70:
                condition = 'Building'
                strength = 75
            elif persistence_ratio > 40:
                condition = 'Stable'
                strength = 50
            else:
                condition = 'Fading'
                strength = 30
            
            return {
                'momentum_condition': condition,
                'persistence_percent': round(persistence_ratio, 1),
                'direction_changes': direction_changes,
                'strength': strength
            }
        
        except Exception as e:
            self.logger.debug(f"Momentum persistence error: {e}")
            return {'momentum_condition': 'Error', 'strength': 0}
    
    def _analyze_compression_expansion(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Detect compression (low volatility, tight ranges) and expansion (high volatility, wide ranges).
        
        Compression often precedes expansion (breakout)
        Expansion may signal exhaustion or continuation depending on context
        """
        try:
            recent = data.tail(window_size)
            ranges = recent['High'] - recent['Low']
            
            # Calculate recent range vs historical range
            recent_avg_range = ranges[-5:].mean()
            historical_avg_range = ranges[:-5].mean() if len(ranges) > 5 else ranges.mean()
            
            compression_ratio = recent_avg_range / (historical_avg_range + 0.0001)
            
            if compression_ratio < 0.7:
                pattern = 'Compression'
                strength = 70
                interpretation = 'Volatility consolidation - potential breakout setup'
            elif compression_ratio > 1.4:
                pattern = 'Expansion'
                strength = 70
                interpretation = 'Increased volatility - momentum accelerating or exhausting'
            else:
                pattern = 'Normal'
                strength = 40
                interpretation = 'Range in normal state'
            
            return {
                'pattern': pattern,
                'compression_ratio': round(compression_ratio, 2),
                'strength': strength,
                'interpretation': interpretation
            }
        
        except Exception as e:
            self.logger.debug(f"Compression/expansion analysis error: {e}")
            return {'pattern': 'Error', 'strength': 0}
    
    def _analyze_candle_dominance(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Analyze which direction dominates: bullish or bearish candles.
        
        Dominance indicates directional bias in price flow.
        """
        try:
            recent = data.tail(window_size)
            
            bullish_count = sum(1 for close, open_ in zip(recent['Close'], recent['Open']) if close > open_)
            bearish_count = sum(1 for close, open_ in zip(recent['Close'], recent['Open']) if close < open_)
            
            total = bullish_count + bearish_count
            if total == 0:
                return {'dominance': 'Neutral', 'bullish_percent': 50, 'strength': 0}
            
            bullish_percent = (bullish_count / total) * 100
            
            if bullish_percent > 70:
                dominance = 'Strongly Bullish'
                strength = 75
            elif bullish_percent > 55:
                dominance = 'Bullish'
                strength = 60
            elif bullish_percent < 30:
                dominance = 'Strongly Bearish'
                strength = 75
            elif bullish_percent < 45:
                dominance = 'Bearish'
                strength = 60
            else:
                dominance = 'Neutral'
                strength = 30
            
            return {
                'dominance': dominance,
                'bullish_percent': round(bullish_percent, 1),
                'bullish_count': bullish_count,
                'bearish_count': bearish_count,
                'strength': strength
            }
        
        except Exception as e:
            self.logger.debug(f"Candle dominance error: {e}")
            return {'dominance': 'Error', 'strength': 0}
    
    def _analyze_candle_body_expansion(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Detect whether candle bodies are expanding or contracting over time.
        
        Expansion: Increasing body sizes = strengthening momentum
        Contraction: Decreasing body sizes = weakening momentum
        """
        try:
            recent = data.tail(window_size)
            bodies = np.abs(recent['Close'] - recent['Open']).values
            
            if len(bodies) < 5:
                return {'trend': 'Insufficient data', 'strength': 0}
            
            # Compare recent bodies to earlier bodies
            recent_bodies = bodies[-5:].mean()
            earlier_bodies = bodies[:-5].mean() if len(bodies) > 5 else bodies.mean()
            
            expansion_ratio = recent_bodies / (earlier_bodies + 0.0001)
            
            if expansion_ratio > 1.3:
                trend = 'Expansion'
                strength = 70
            elif expansion_ratio < 0.8:
                trend = 'Contraction'
                strength = 70
            else:
                trend = 'Stable'
                strength = 40
            
            return {
                'trend': trend,
                'expansion_ratio': round(expansion_ratio, 2),
                'strength': strength,
                'interpretation': 'Momentum strengthening' if trend == 'Expansion' 
                                 else 'Momentum weakening' if trend == 'Contraction'
                                 else 'Momentum stable'
            }
        
        except Exception as e:
            self.logger.debug(f"Candle body expansion error: {e}")
            return {'trend': 'Error', 'strength': 0}
    
    def _analyze_wick_rejection_pattern(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Detect wick rejection patterns across multiple candles.
        
        Rejection: Wicks appear at resistance/support but price closes away
        This indicates buyer/seller rejection at key levels
        """
        try:
            recent = data.tail(window_size)
            
            # Identify candles with significant upper wicks (potential rejection at highs)
            upper_wick_rejection = sum(1 for i in range(len(recent)) 
                                      if (recent['High'].iloc[i] - recent['Close'].iloc[i]) > 
                                      (recent['Close'].iloc[i] - recent['Open'].iloc[i]) * 1.5)
            
            # Identify candles with significant lower wicks (potential rejection at lows)
            lower_wick_rejection = sum(1 for i in range(len(recent)) 
                                      if (recent['Open'].iloc[i] - recent['Low'].iloc[i]) > 
                                      (recent['Close'].iloc[i] - recent['Open'].iloc[i]) * 1.5)
            
            if upper_wick_rejection > lower_wick_rejection:
                pattern = 'Upper Rejection'
                interpretation = 'Sellers rejecting higher prices'
                strength = 60 if upper_wick_rejection > len(recent) * 0.5 else 40
            elif lower_wick_rejection > upper_wick_rejection:
                pattern = 'Lower Rejection'
                interpretation = 'Buyers rejecting lower prices'
                strength = 60 if lower_wick_rejection > len(recent) * 0.5 else 40
            else:
                pattern = 'Balanced'
                interpretation = 'No significant rejection bias'
                strength = 30
            
            return {
                'pattern': pattern,
                'upper_wick_count': upper_wick_rejection,
                'lower_wick_count': lower_wick_rejection,
                'strength': strength,
                'interpretation': interpretation
            }
        
        except Exception as e:
            self.logger.debug(f"Wick rejection analysis error: {e}")
            return {'pattern': 'Error', 'strength': 0}
    
    def _detect_stair_step_pattern(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Detect stair-step patterns (step-by-step price progression).
        
        Stair-steps indicate controlled, momentum-driven movement
        Smooth stair-steps = healthy trend progression
        Chaotic = indecision or reversal
        """
        try:
            recent = data.tail(window_size)
            closes = recent['Close'].values
            
            # Count "steps" (direction changes in a methodical pattern)
            steps_up = sum(1 for i in range(1, len(closes)) if closes[i] > closes[i-1])
            steps_down = sum(1 for i in range(1, len(closes)) if closes[i] < closes[i-1])
            
            # Imbalance = stair-step pattern
            step_imbalance = abs(steps_up - steps_down) / (len(closes) - 1) * 100 if len(closes) > 1 else 0
            
            if step_imbalance > 60:
                pattern = 'Stair-Step'
                strength = 75
                interpretation = 'Methodical directional progression'
            else:
                pattern = 'Chaotic/Mixed'
                strength = 30
                interpretation = 'Indecisive or choppy movement'
            
            return {
                'pattern': pattern,
                'steps_up': steps_up,
                'steps_down': steps_down,
                'imbalance_percent': round(step_imbalance, 1),
                'strength': strength,
                'interpretation': interpretation
            }
        
        except Exception as e:
            self.logger.debug(f"Stair-step detection error: {e}")
            return {'pattern': 'Error', 'strength': 0}
    
    def _detect_fake_breakout(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Detect fake breakouts (price breaks structure but closes back inside).
        
        Fake breakouts indicate lack of follow-through, potential reversal setup
        """
        try:
            recent = data.tail(window_size)
            
            if len(recent) < 3:
                return {'fake_breakout_detected': False, 'strength': 0}
            
            # Look for recent structural break that wasn't sustained
            struct_high = recent['High'].iloc[:-2].max()
            struct_low = recent['Low'].iloc[:-2].min()
            
            latest_close = recent['Close'].iloc[-1]
            prev_high = recent['High'].iloc[-2]
            prev_low = recent['Low'].iloc[-2]
            
            # Fake breakout: price breaks above but closes below structure
            fake_breakup = (prev_high > struct_high and latest_close < struct_high)
            # Fake breakout: price breaks below but closes above structure
            fake_breakdown = (prev_low < struct_low and latest_close > struct_low)
            
            if fake_breakup or fake_breakdown:
                return {
                    'fake_breakout_detected': True,
                    'type': 'Breakup' if fake_breakup else 'Breakdown',
                    'strength': 65,
                    'interpretation': 'Lack of follow-through on breakout'
                }
            else:
                return {
                    'fake_breakout_detected': False,
                    'strength': 0,
                    'interpretation': 'No fake breakout detected'
                }
        
        except Exception as e:
            self.logger.debug(f"Fake breakout detection error: {e}")
            return {'fake_breakout_detected': False, 'strength': 0}
    
    def _analyze_channel_formation(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Analyze channel formation based on closing prices (not just highs/lows).
        
        Channels indicate price consolidation within defined boundaries
        """
        try:
            recent = data.tail(window_size)
            closes = recent['Close'].values
            
            if len(closes) < 5:
                return {'channel_detected': False, 'strength': 0}
            
            # Find min and max closes
            max_close = closes.max()
            min_close = closes.min()
            range_ = max_close - min_close
            
            if range_ == 0:
                return {'channel_detected': False, 'strength': 0}
            
            # Calculate how many closes stay within upper and lower thirds (channel test)
            upper_third = min_close + (range_ * 0.67)
            lower_third = min_close + (range_ * 0.33)
            
            channel_touches = sum(1 for c in closes 
                                 if (c >= upper_third) or (c <= lower_third))
            
            if channel_touches > len(closes) * 0.6:
                return {
                    'channel_detected': True,
                    'type': 'Range/Channel',
                    'strength': 70,
                    'range_size': round(range_, 4),
                    'interpretation': 'Price consolidating within defined channel'
                }
            else:
                return {
                    'channel_detected': False,
                    'strength': 30,
                    'interpretation': 'Price moves freely, no channel'
                }
        
        except Exception as e:
            self.logger.debug(f"Channel analysis error: {e}")
            return {'channel_detected': False, 'strength': 0}
    
    def _detect_micro_trend(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Detect micro-trends (small-scale trends within larger structures).
        
        Micro-trends help identify breakdowns within higher-timeframe trends
        """
        try:
            recent = data.tail(window_size)
            
            # Split into thirds and check each
            third = window_size // 3
            sections = [
                recent.iloc[0:third],
                recent.iloc[third:2*third],
                recent.iloc[2*third:]
            ]
            
            micro_trends = []
            for section in sections:
                if len(section) < 2:
                    continue
                higher_highs = sum(1 for i in range(1, len(section)) 
                                  if section['High'].iloc[i] > section['High'].iloc[i-1])
                if higher_highs > len(section) * 0.6:
                    micro_trends.append('Bullish')
                elif higher_highs < len(section) * 0.4:
                    micro_trends.append('Bearish')
                else:
                    micro_trends.append('Mixed')
            
            # Alignment strength
            if len(set(micro_trends)) == 1:
                strength = 75
                interpretation = f'All micro-trends aligned: {micro_trends[0]}'
            else:
                strength = 40
                interpretation = 'Micro-trends diverging'
            
            return {
                'micro_trends': micro_trends,
                'strength': strength,
                'interpretation': interpretation
            }
        
        except Exception as e:
            self.logger.debug(f"Micro-trend detection error: {e}")
            return {'micro_trends': [], 'strength': 0}
    
    def _analyze_range_vs_trend(self, data: pd.DataFrame, window_size: int) -> Dict[str, Any]:
        """
        Determine if price is in a trend or range/consolidation.
        
        Trending: Directional bias, low consolidation
        Range: Price bouncing between support/resistance
        """
        try:
            recent = data.tail(window_size)
            
            # Measure directional bias
            closes = recent['Close'].values
            higher_closes = sum(1 for i in range(1, len(closes)) if closes[i] > closes[i-1])
            directional_ratio = higher_closes / (len(closes) - 1) if len(closes) > 1 else 0.5
            
            # Measure volatility relative to close movement
            ranges = recent['High'] - recent['Low']
            close_movement = np.abs(np.diff(closes))
            
            avg_range = ranges.mean()
            avg_movement = close_movement.mean()
            
            # If movement < range, price is consolidating
            consolidation_ratio = avg_movement / (avg_range + 0.0001)
            
            if directional_ratio > 0.65 or directional_ratio < 0.35:
                # Clear directional bias
                if consolidation_ratio < 0.5:
                    condition = 'Trending'
                    strength = 75
                else:
                    condition = 'Weak Trend'
                    strength = 50
            else:
                # No clear directional bias
                condition = 'Range'
                strength = 70
            
            return {
                'condition': condition,
                'directional_ratio': round(directional_ratio * 100, 1),
                'consolidation_ratio': round(consolidation_ratio, 2),
                'strength': strength
            }
        
        except Exception as e:
            self.logger.debug(f"Range vs trend analysis error: {e}")
            return {'condition': 'Error', 'strength': 0}
    
    def _calculate_directional_bias(self, analysis: Dict) -> str:
        """Calculate overall directional bias from all analyses."""
        bullish_score = 0
        bearish_score = 0
        
        # HH/HL = bullish
        if analysis.get('hh_hl_sequence', {}).get('strength', 0) > 50:
            bullish_score += 2
        
        # LH/LL = bearish
        if analysis.get('lh_ll_sequence', {}).get('strength', 0) > 50:
            bearish_score += 2
        
        # BOS analysis
        bos = analysis.get('structure_break', {})
        if bos.get('type') == 'Bullish BOS':
            bullish_score += 1
        elif bos.get('type') == 'Bearish BOS':
            bearish_score += 1
        
        # Candle dominance
        dominance = analysis.get('candle_dominance', {}).get('dominance', '')
        if 'Bullish' in dominance:
            bullish_score += 1
        elif 'Bearish' in dominance:
            bearish_score += 1
        
        # Stair-step direction
        stair = analysis.get('stair_step_movement', {})
        if stair.get('steps_up', 0) > stair.get('steps_down', 0):
            bullish_score += 1
        elif stair.get('steps_down', 0) > stair.get('steps_up', 0):
            bearish_score += 1
        
        if bullish_score > bearish_score:
            return 'bullish'
        elif bearish_score > bullish_score:
            return 'bearish'
        else:
            return 'neutral'
    
    def _calculate_structure_strength(self, analysis: Dict) -> str:
        """Calculate overall structure strength."""
        strengths = []
        
        strengths.append(analysis.get('hh_hl_sequence', {}).get('strength', 0))
        strengths.append(analysis.get('lh_ll_sequence', {}).get('strength', 0))
        strengths.append(analysis.get('structure_break', {}).get('strength', 0))
        strengths.append(analysis.get('change_of_character', {}).get('strength', 0))
        
        avg_strength = np.mean([s for s in strengths if s > 0]) if any(strengths) else 0
        
        if avg_strength > 70:
            return 'strong'
        elif avg_strength > 50:
            return 'moderate'
        else:
            return 'weak'
    
    def _calculate_momentum_condition(self, analysis: Dict) -> str:
        """Calculate overall momentum condition."""
        momentum = analysis.get('momentum_persistence', {}).get('momentum_condition', 'stable')
        return momentum
    
    def _calculate_confidence(self, analysis: Dict) -> float:
        """Calculate overall confidence in the analysis (0-100)."""
        strengths = []
        
        for key, value in analysis.items():
            if isinstance(value, dict) and 'strength' in value:
                strengths.append(value['strength'])
        
        if not strengths:
            return 0.0
        
        avg_strength = np.mean(strengths)
        return round(avg_strength, 1)
    
    def _generate_explanation(self, bias: str, strength: str, momentum: str, analysis: Dict) -> str:
        """Generate human-readable explanation of multi-candle price action."""
        parts = []
        
        # Directional bias
        if bias == 'bullish':
            parts.append("Price shows bullish structure")
        elif bias == 'bearish':
            parts.append("Price shows bearish structure")
        else:
            parts.append("Price structure is neutral/mixed")
        
        # Structure strength
        if strength == 'strong':
            parts.append(f"with strong structural integrity")
        elif strength == 'moderate':
            parts.append(f"with moderate structural integrity")
        else:
            parts.append(f"with weak structural integrity")
        
        # Momentum
        parts.append(f". Momentum is {momentum.lower()}.")
        
        # Additional details
        if analysis.get('structure_break', {}).get('bos_detected'):
            parts.append("Break of structure detected.")
        
        if analysis.get('change_of_character', {}).get('choch_detected'):
            parts.append("Change of character detected.")
        
        if analysis.get('impulse_correction', {}).get('pattern') == 'Impulse':
            parts.append("Price is in impulse phase (strong directional move).")
        
        if analysis.get('compression_expansion', {}).get('pattern') == 'Compression':
            parts.append("Volatility compression suggests potential breakout.")
        
        return " ".join(parts)
