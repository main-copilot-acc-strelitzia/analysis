"""Comprehensive Forex analyzer using all analysis methods."""

import pandas as pd
import numpy as np
from typing import Dict, Any
from analysis.base import BaseAnalyzer
from analysis.forex.market_structure import MarketStructureAnalysis
from analysis.forex.trend import TrendAnalysis
from analysis.forex.momentum import MomentumAnalysis
from analysis.forex.volatility import VolatilityAnalysis
from analysis.forex.volume import VolumeAnalysis
from analysis.forex.sessions import SessionAnalysis
from analysis.forex.liquidity import LiquidityAnalysis
from analysis.forex.order_blocks import OrderBlockAnalysis
from analysis.forex.fair_value_gaps import FairValueGapAnalysis
from analysis.forex.support_resistance import SupportResistanceAnalysis
from analysis.forex.multi_timeframe import MultiTimeframeAnalysis
from analysis.forex.confluence import ConfluenceAnalysis
from analysis.forex.candlestick_patterns import CandlestickPatternAnalysis
from analysis.shared.multi_candle_price_action import MultiCandlePriceAction
from analysis.shared.candlestick_patterns_advanced import CandlestickPatternAnalyzer
from analysis.shared.chart_patterns_advanced import ChartPatternAnalyzer
from analysis.shared.structure_price_action_patterns import StructurePriceActionAnalyzer
from core.logger import get_logger


class ForexAnalyzer(BaseAnalyzer):
    """Complete Forex analysis with 300+ methods:
    - 41 indicator-based methods (trend, momentum, volatility, volume, sessions, liquidity, etc.)
    - 1 multi-candle price action and market structure analysis
    - 80+ candlestick patterns (single, multi-candle, advanced, directional flow)
    - 100+ chart patterns (reversals, continuations, consolidations)
    - 200+ structure/price-action patterns (trends, S/R, formations, breakouts, market behavior)
    """

    def __init__(self, symbol: str, timeframe: str):
        """Initialize Forex analyzer."""
        super().__init__(symbol, timeframe)
        self.logger = get_logger()
        self.price_action = MultiCandlePriceAction()
        self.candlestick_patterns = CandlestickPatternAnalyzer()
        self.chart_patterns = ChartPatternAnalyzer()
        self.structure_patterns = StructurePriceActionAnalyzer()

    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive Forex analysis using 300+ methods:
        - 41 indicator-based methods (trend, momentum, volatility, volume, sessions, liquidity, etc.)
        - 1 multi-candle price action and market structure analysis
        - 80+ candlestick patterns (single, multi-candle, advanced, directional flow)
        - 100+ chart patterns (reversals, continuations, consolidations)
        - 200+ structure/price-action patterns (trends, S/R, formations, breakouts, market behavior)
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Dict with confluence score and all analysis results.
        """
        if not self.validate_data(data):
            return self.create_result(
                confluence_score=0.0,
                error="Insufficient or invalid data"
            )

        try:
            signals = {}

            # Market Structure (8 methods)
            signals['higher_highs_lower_lows'] = MarketStructureAnalysis.higher_highs_lower_lows(data)
            signals['support_resistance_test'] = MarketStructureAnalysis.support_resistance_test(data)
            signals['order_block_id'] = MarketStructureAnalysis.order_block_identification(data)
            signals['liquidity_analysis'] = MarketStructureAnalysis.liquidity_analysis(data)
            signals['market_regime'] = MarketStructureAnalysis.market_regime(data)
            signals['price_action'] = MarketStructureAnalysis.price_action_patterns(data)
            signals['imbalance_detection'] = MarketStructureAnalysis.imbalance_detection(data)

            # Trend Analysis (8 methods)
            signals['ma_crossover'] = TrendAnalysis.moving_average_crossover(data)
            signals['ema_trend'] = TrendAnalysis.ema_trend(data)
            signals['adx_strength'] = TrendAnalysis.adx_trend_strength(data)
            signals['price_slope'] = TrendAnalysis.price_slope(data)
            signals['supertrend'] = TrendAnalysis.supertrend_indicator(data)
            signals['vwap_trend'] = TrendAnalysis.vwap_trend(data)
            signals['rsi_trend'] = TrendAnalysis.rsi_trend(data)
            signals['macd_trend'] = TrendAnalysis.macd_trend(data)

            # Momentum Analysis (8 methods)
            signals['rsi_momentum'] = MomentumAnalysis.rsi_momentum(data)
            signals['stochastic'] = MomentumAnalysis.stochastic_momentum(data)
            signals['roc'] = MomentumAnalysis.roc_momentum(data)
            signals['price_momentum'] = MomentumAnalysis.price_momentum(data)
            signals['williams_r'] = MomentumAnalysis.williams_r_momentum(data)
            signals['cci'] = MomentumAnalysis.cci_momentum(data)
            signals['volume_momentum'] = MomentumAnalysis.volume_momentum(data)
            signals['obv_momentum'] = MomentumAnalysis.obv_momentum(data)

            # Volatility Analysis (8 methods)
            signals['atr_vol'] = VolatilityAnalysis.atr_volatility(data)
            signals['bb_squeeze'] = VolatilityAnalysis.bollinger_band_squeeze(data)
            signals['hist_vol'] = VolatilityAnalysis.historical_volatility(data)
            signals['vol_clustering'] = VolatilityAnalysis.volatility_clustering(data)
            signals['atr_percent'] = VolatilityAnalysis.average_true_range_percent(data)
            signals['range_vol'] = VolatilityAnalysis.range_volatility(data)
            signals['parkinson_vol'] = VolatilityAnalysis.parkinson_volatility(data)
            signals['keltner_width'] = VolatilityAnalysis.keltner_channel_width(data)

            # Volume Analysis (8 methods)
            signals['volume_trend'] = VolumeAnalysis.volume_trend(data)
            signals['volume_profile'] = VolumeAnalysis.volume_profile_analysis(data)
            signals['accum_dist'] = VolumeAnalysis.accumulation_distribution(data)
            signals['obv_signal'] = VolumeAnalysis.on_balance_volume_signal(data)
            signals['volume_strength'] = VolumeAnalysis.volume_strength(data)
            signals['vpt'] = VolumeAnalysis.volume_price_trend(data)
            signals['volume_density'] = VolumeAnalysis.volume_density(data)

            # Sessions (8 methods)
            signals['london_session'] = SessionAnalysis.london_session_analysis(data)
            signals['tokyo_session'] = SessionAnalysis.tokyo_session_analysis(data)
            signals['newyork_session'] = SessionAnalysis.new_york_session_analysis(data)
            signals['sydney_session'] = SessionAnalysis.sydney_session_analysis(data)
            signals['overlap_analysis'] = SessionAnalysis.overlap_analysis(data)
            signals['session_open'] = SessionAnalysis.session_open_analysis(data)
            signals['session_vol_pattern'] = SessionAnalysis.session_volatility_pattern(data)

            # Liquidity (8 methods)
            signals['liquidity_level'] = LiquidityAnalysis.liquidity_level_detection(data)
            signals['liquidity_void'] = LiquidityAnalysis.liquidity_void_detection(data)
            signals['sweep_detection'] = LiquidityAnalysis.sweep_detection(data)
            signals['bid_ask_imbalance'] = LiquidityAnalysis.bid_ask_imbalance(data)
            signals['mm_activity'] = LiquidityAnalysis.market_maker_activity(data)
            signals['pool_level'] = LiquidityAnalysis.pool_level_analysis(data)
            signals['liquidity_collapse'] = LiquidityAnalysis.liquidity_collapse_detection(data)

            # Order Blocks (6 methods)
            signals['bullish_ob'] = OrderBlockAnalysis.bullish_order_block(data)
            signals['bearish_ob'] = OrderBlockAnalysis.bearish_order_block(data)
            signals['ob_rejection'] = OrderBlockAnalysis.order_block_rejection(data)
            signals['institutional_activity'] = OrderBlockAnalysis.institutional_activity_marker(data)
            signals['mitigation_level'] = OrderBlockAnalysis.mitigation_level_detection(data)
            signals['fvg_ob_confirm'] = OrderBlockAnalysis.fair_value_gap_ob_confirmation(data)

            # Fair Value Gaps (6 methods)
            signals['bullish_fvg'] = FairValueGapAnalysis.bullish_fvg_detection(data)
            signals['bearish_fvg'] = FairValueGapAnalysis.bearish_fvg_detection(data)
            signals['fvg_fill_prob'] = FairValueGapAnalysis.fvg_fill_probability(data)
            signals['fvg_magnitude'] = FairValueGapAnalysis.fvg_magnitude(data)
            signals['fvg_structure'] = FairValueGapAnalysis.fvg_structure_confirmation(data)
            signals['fvg_depletion'] = FairValueGapAnalysis.fvg_depletion_level(data)

            # Support & Resistance (8 methods)
            signals['support_strength'] = SupportResistanceAnalysis.support_strength(data)
            signals['resistance_strength'] = SupportResistanceAnalysis.resistance_strength(data)
            signals['sr_ratio'] = SupportResistanceAnalysis.support_resistance_ratio(data)
            signals['level_confluence'] = SupportResistanceAnalysis.level_confluence(data)
            signals['breakout_resist'] = SupportResistanceAnalysis.breakout_above_resistance(data)
            signals['breakdown_support'] = SupportResistanceAnalysis.breakdown_below_support(data)

            # Multi-Timeframe (6 methods)
            signals['tf_alignment'] = MultiTimeframeAnalysis.higher_timeframe_alignment(
                np.mean([v for k, v in signals.items() if 'trend' in k]),
                np.mean([v for k, v in signals.items() if 'momentum' in k])
            )
            signals['tf_confirmation'] = MultiTimeframeAnalysis.timeframe_confirmation(
                {'current': np.mean(list(signals.values()))}
            )
            signals['trend_alignment'] = MultiTimeframeAnalysis.trend_alignment_strength(
                {'current': MarketStructureAnalysis.market_regime(data)}
            )
            signals['confluence_tf'] = MultiTimeframeAnalysis.confluence_across_timeframes(
                {'current': np.mean(list(signals.values()))}
            )
            signals['mean_reversion'] = MultiTimeframeAnalysis.mean_reversion_setup(data, data)
            signals['trend_continuation'] = MultiTimeframeAnalysis.trend_continuation_likelihood(data, data)

            # Candlestick Patterns (10 methods)
            signals['doji'] = CandlestickPatternAnalysis.doji_pattern(data)
            signals['hammer'] = CandlestickPatternAnalysis.hammer_pattern(data)
            signals['inverted_hammer'] = CandlestickPatternAnalysis.inverted_hammer_pattern(data)
            signals['engulfing'] = CandlestickPatternAnalysis.engulfing_pattern(data)
            signals['morning_star'] = CandlestickPatternAnalysis.morning_star_pattern(data)
            signals['evening_star'] = CandlestickPatternAnalysis.evening_star_pattern(data)
            signals['pin_bar'] = CandlestickPatternAnalysis.pin_bar_pattern(data)
            signals['inside_bar'] = CandlestickPatternAnalysis.inside_bar_pattern(data)
            signals['outside_bar'] = CandlestickPatternAnalysis.outside_bar_pattern(data)
            signals['marubozu'] = CandlestickPatternAnalysis.marubozu_pattern(data)

            # Multi-Candle Price Action & Market Structure (1 method)
            # Analyzes sequences of candles to understand price flow, directional control,
            # momentum persistence, and structural behavior (separate from candlestick patterns)
            signals['multi_candle_price_action'] = self.price_action.analyze(data)

            # Advanced Candlestick Patterns (80+ methods: single, multi-candle, advanced, directional flow)
            # Comprehensive pattern detection including doji, hammer, engulfing, harami, morning star,
            # three white soldiers, kicker, mat hold, bull run, bear run, momentum divergence, etc. with confidence scoring
            candlestick_result = self.candlestick_patterns.analyze(data)
            signals['candlestick_patterns_analysis'] = candlestick_result
            signals['candlestick_pattern_score'] = candlestick_result.get('pattern_score', 0.0)

            # Advanced Chart Patterns (100+ methods: technical formations)
            # Detects reversals (double top/bottom, head & shoulders), continuations (flags, pennants),
            # consolidations (triangles, rectangles), and advanced patterns (cup & handle, wedges, etc.)
            chart_result = self.chart_patterns.analyze(data)
            signals['chart_patterns_analysis'] = chart_result
            signals['chart_pattern_score'] = chart_result.get('pattern_score', 0.0)

            # Structure & Price-Action Patterns (200+ methods: comprehensive market structure)
            # Detects trend structures (uptrend, downtrend, accelerating, parabolic, exhaustion),
            # support/resistance (horizontal, dynamic, role reversals), chart formations (double top/bottom,
            # head & shoulders, cup & handle, broadening), continuation (flags, pennants, rectangles),
            # triangles/wedges, breakout patterns, market behavior (accumulation, distribution, mean reversion),
            # and time-based structures with full contextual analysis
            structure_result = self.structure_patterns.analyze(data)
            signals['structure_patterns_analysis'] = structure_result
            signals['structure_pattern_score'] = structure_result.get('structure_score', 0.0)
            signals['market_trend'] = structure_result.get('trend_direction', 'Unknown')
            signals['market_context'] = structure_result.get('market_context', 'Unknown')

            # Calculate confluence
            confluence_score = ConfluenceAnalysis.calculate_confluence_score(signals)

            return self.create_result(
                confluence_score=confluence_score,
                analysis=signals,
                signal_count=len(signals),
                bullish_signals=ConfluenceAnalysis.bullish_confluence_count(signals),
                bearish_signals=ConfluenceAnalysis.bearish_confluence_count(signals),
                rating=ConfluenceAnalysis.confluence_strength_rating(confluence_score)
            )

        except Exception as e:
            self.logger.error(f"Error in Forex analysis: {e}")
            return self.create_result(
                confluence_score=0.0,
                error=str(e)
            )
