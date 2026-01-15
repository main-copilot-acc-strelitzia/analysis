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
        # Backwards-compatible: accept either a single DataFrame (current/live) or a dict
        # with keys 'current' and 'historical' (both pd.DataFrame). The single-DataFrame
        # path preserves existing behavior exactly.
        def _numeric_mean(iterable):
            vals = []
            for v in iterable:
                try:
                    vals.append(float(v))
                except Exception:
                    continue
            return float(np.mean(vals)) if vals else 0.0

        def _gather_signals(df: pd.DataFrame) -> Dict[str, Any]:
            # Runs the existing comprehensive analysis pipeline on provided df
            signals: Dict[str, Any] = {}
            # Market Structure
            signals['higher_highs_lower_lows'] = MarketStructureAnalysis.higher_highs_lower_lows(df)
            signals['support_resistance_test'] = MarketStructureAnalysis.support_resistance_test(df)
            signals['order_block_id'] = MarketStructureAnalysis.order_block_identification(df)
            signals['liquidity_analysis'] = MarketStructureAnalysis.liquidity_analysis(df)
            signals['market_regime'] = MarketStructureAnalysis.market_regime(df)
            signals['price_action'] = MarketStructureAnalysis.price_action_patterns(df)
            signals['imbalance_detection'] = MarketStructureAnalysis.imbalance_detection(df)

            # Trend
            signals['ma_crossover'] = TrendAnalysis.moving_average_crossover(df)
            signals['ema_trend'] = TrendAnalysis.ema_trend(df)
            signals['adx_strength'] = TrendAnalysis.adx_trend_strength(df)
            signals['price_slope'] = TrendAnalysis.price_slope(df)
            signals['supertrend'] = TrendAnalysis.supertrend_indicator(df)
            signals['vwap_trend'] = TrendAnalysis.vwap_trend(df)
            signals['rsi_trend'] = TrendAnalysis.rsi_trend(df)
            signals['macd_trend'] = TrendAnalysis.macd_trend(df)

            # Momentum
            signals['rsi_momentum'] = MomentumAnalysis.rsi_momentum(df)
            signals['stochastic'] = MomentumAnalysis.stochastic_momentum(df)
            signals['roc'] = MomentumAnalysis.roc_momentum(df)
            signals['price_momentum'] = MomentumAnalysis.price_momentum(df)
            signals['williams_r'] = MomentumAnalysis.williams_r_momentum(df)
            signals['cci'] = MomentumAnalysis.cci_momentum(df)
            signals['volume_momentum'] = MomentumAnalysis.volume_momentum(df)
            signals['obv_momentum'] = MomentumAnalysis.obv_momentum(df)

            # Volatility
            signals['atr_vol'] = VolatilityAnalysis.atr_volatility(df)
            signals['bb_squeeze'] = VolatilityAnalysis.bollinger_band_squeeze(df)
            signals['hist_vol'] = VolatilityAnalysis.historical_volatility(df)
            signals['vol_clustering'] = VolatilityAnalysis.volatility_clustering(df)
            signals['atr_percent'] = VolatilityAnalysis.average_true_range_percent(df)
            signals['range_vol'] = VolatilityAnalysis.range_volatility(df)
            signals['parkinson_vol'] = VolatilityAnalysis.parkinson_volatility(df)
            signals['keltner_width'] = VolatilityAnalysis.keltner_channel_width(df)

            # Volume
            signals['volume_trend'] = VolumeAnalysis.volume_trend(df)
            signals['volume_profile'] = VolumeAnalysis.volume_profile_analysis(df)
            signals['accum_dist'] = VolumeAnalysis.accumulation_distribution(df)
            signals['obv_signal'] = VolumeAnalysis.on_balance_volume_signal(df)
            signals['volume_strength'] = VolumeAnalysis.volume_strength(df)
            signals['vpt'] = VolumeAnalysis.volume_price_trend(df)
            signals['volume_density'] = VolumeAnalysis.volume_density(df)

            # Sessions
            signals['london_session'] = SessionAnalysis.london_session_analysis(df)
            signals['tokyo_session'] = SessionAnalysis.tokyo_session_analysis(df)
            signals['newyork_session'] = SessionAnalysis.new_york_session_analysis(df)
            signals['sydney_session'] = SessionAnalysis.sydney_session_analysis(df)
            signals['overlap_analysis'] = SessionAnalysis.overlap_analysis(df)
            signals['session_open'] = SessionAnalysis.session_open_analysis(df)
            signals['session_vol_pattern'] = SessionAnalysis.session_volatility_pattern(df)

            # Liquidity
            signals['liquidity_level'] = LiquidityAnalysis.liquidity_level_detection(df)
            signals['liquidity_void'] = LiquidityAnalysis.liquidity_void_detection(df)
            signals['sweep_detection'] = LiquidityAnalysis.sweep_detection(df)
            signals['bid_ask_imbalance'] = LiquidityAnalysis.bid_ask_imbalance(df)
            signals['mm_activity'] = LiquidityAnalysis.market_maker_activity(df)
            signals['pool_level'] = LiquidityAnalysis.pool_level_analysis(df)
            signals['liquidity_collapse'] = LiquidityAnalysis.liquidity_collapse_detection(df)

            # Order Blocks
            signals['bullish_ob'] = OrderBlockAnalysis.bullish_order_block(df)
            signals['bearish_ob'] = OrderBlockAnalysis.bearish_order_block(df)
            signals['ob_rejection'] = OrderBlockAnalysis.order_block_rejection(df)
            signals['institutional_activity'] = OrderBlockAnalysis.institutional_activity_marker(df)
            signals['mitigation_level'] = OrderBlockAnalysis.mitigation_level_detection(df)
            signals['fvg_ob_confirm'] = OrderBlockAnalysis.fair_value_gap_ob_confirmation(df)

            # Fair Value Gaps
            signals['bullish_fvg'] = FairValueGapAnalysis.bullish_fvg_detection(df)
            signals['bearish_fvg'] = FairValueGapAnalysis.bearish_fvg_detection(df)
            signals['fvg_fill_prob'] = FairValueGapAnalysis.fvg_fill_probability(df)
            signals['fvg_magnitude'] = FairValueGapAnalysis.fvg_magnitude(df)
            signals['fvg_structure'] = FairValueGapAnalysis.fvg_structure_confirmation(df)
            signals['fvg_depletion'] = FairValueGapAnalysis.fvg_depletion_level(df)

            # Support & Resistance
            signals['support_strength'] = SupportResistanceAnalysis.support_strength(df)
            signals['resistance_strength'] = SupportResistanceAnalysis.resistance_strength(df)
            signals['sr_ratio'] = SupportResistanceAnalysis.support_resistance_ratio(df)
            signals['level_confluence'] = SupportResistanceAnalysis.level_confluence(df)
            signals['breakout_resist'] = SupportResistanceAnalysis.breakout_above_resistance(df)
            signals['breakdown_support'] = SupportResistanceAnalysis.breakdown_below_support(df)

            # Multi-Timeframe
            signals['tf_alignment'] = MultiTimeframeAnalysis.higher_timeframe_alignment(
                _numeric_mean(v for k, v in signals.items() if 'trend' in k),
                _numeric_mean(v for k, v in signals.items() if 'momentum' in k)
            )
            signals['tf_confirmation'] = MultiTimeframeAnalysis.timeframe_confirmation(
                {'current': _numeric_mean(signals.values())}
            )
            signals['trend_alignment'] = MultiTimeframeAnalysis.trend_alignment_strength(
                {'current': MarketStructureAnalysis.market_regime(df)}
            )
            signals['confluence_tf'] = MultiTimeframeAnalysis.confluence_across_timeframes(
                {'current': _numeric_mean(signals.values())}
            )
            signals['mean_reversion'] = MultiTimeframeAnalysis.mean_reversion_setup(df, df)
            signals['trend_continuation'] = MultiTimeframeAnalysis.trend_continuation_likelihood(df, df)

            # Candlestick Patterns
            signals['doji'] = CandlestickPatternAnalysis.doji_pattern(df)
            signals['hammer'] = CandlestickPatternAnalysis.hammer_pattern(df)
            signals['inverted_hammer'] = CandlestickPatternAnalysis.inverted_hammer_pattern(df)
            signals['engulfing'] = CandlestickPatternAnalysis.engulfing_pattern(df)
            signals['morning_star'] = CandlestickPatternAnalysis.morning_star_pattern(df)
            signals['evening_star'] = CandlestickPatternAnalysis.evening_star_pattern(df)
            signals['pin_bar'] = CandlestickPatternAnalysis.pin_bar_pattern(df)
            signals['inside_bar'] = CandlestickPatternAnalysis.inside_bar_pattern(df)
            signals['outside_bar'] = CandlestickPatternAnalysis.outside_bar_pattern(df)
            signals['marubozu'] = CandlestickPatternAnalysis.marubozu_pattern(df)

            # Multi-Candle Price Action
            signals['multi_candle_price_action'] = self.price_action.analyze(df)

            # Advanced Candlestick & Chart Patterns
            candlestick_result = self.candlestick_patterns.analyze(df)
            signals['candlestick_patterns_analysis'] = candlestick_result
            signals['candlestick_pattern_score'] = candlestick_result.get('pattern_score', 0.0)

            chart_result = self.chart_patterns.analyze(df)
            signals['chart_patterns_analysis'] = chart_result
            signals['chart_pattern_score'] = chart_result.get('pattern_score', 0.0)

            structure_result = self.structure_patterns.analyze(df)
            signals['structure_patterns_analysis'] = structure_result
            signals['structure_pattern_score'] = structure_result.get('structure_score', 0.0)
            signals['market_trend'] = structure_result.get('trend_direction', 'Unknown')
            signals['market_context'] = structure_result.get('market_context', 'Unknown')

            return signals

        # If caller passed a single DataFrame (backwards-compatible path)
        if isinstance(data, pd.DataFrame):
            if not self.validate_data(data):
                return self.create_result(confluence_score=0.0, error="Insufficient or invalid data")

            try:
                signals = _gather_signals(data)
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
                self.logger.exception(f"Error in Forex analysis: {e}")
                return self.create_result(confluence_score=0.0, error=str(e))

        # New: dict input with 'current' and 'historical' keys
        if isinstance(data, dict):
            current = data.get('current')
            historical = data.get('historical')

            if current is None or not isinstance(current, pd.DataFrame):
                return self.create_result(confluence_score=0.0, error="Missing 'current' DataFrame")

            # Run current analysis immediately (preserve behaviour)
            current_signals = {}
            try:
                current_signals = _gather_signals(current)
            except Exception:
                self.logger.exception("Error running current pipeline")

            # Prepare merged historical dataframe for structure analysis
            hist_df = None
            if historical is not None and isinstance(historical, pd.DataFrame) and len(historical) > 0:
                # Merge historical + current ensuring chronological order and no duplicates
                combined = pd.concat([historical, current], ignore_index=True)
                combined = combined.drop_duplicates(subset=['Timestamp']).sort_values('Timestamp').reset_index(drop=True)
                # Tag sessions for session-aware analysis
                combined = SessionAnalysis.tag_sessions(combined)
                hist_df = combined

            historical_signals = {}
            if hist_df is not None:
                try:
                    # Focus historical pipeline on structure & multi-candle methods that require depth
                    historical_signals['market_structure'] = {
                        'higher_lower': MarketStructureAnalysis.higher_highs_lower_lows(hist_df),
                        'order_blocks': MarketStructureAnalysis.order_block_identification(hist_df),
                        'imbalance': MarketStructureAnalysis.imbalance_detection(hist_df),
                        'regime': MarketStructureAnalysis.market_regime(hist_df),
                    }
                    historical_signals['structure_patterns'] = self.structure_patterns.analyze(hist_df)
                    historical_signals['chart_patterns'] = self.chart_patterns.analyze(hist_df)
                    historical_signals['candlestick_patterns'] = self.candlestick_patterns.analyze(hist_df)
                    historical_signals['multi_candle_price_action'] = self.price_action.analyze(hist_df)
                    historical_signals['support_resistance'] = {
                        'support_strength': SupportResistanceAnalysis.support_strength(hist_df),
                        'resistance_strength': SupportResistanceAnalysis.resistance_strength(hist_df),
                    }
                    # Session context to help downgrade/upgrade confidence
                    historical_signals['session_context'] = SessionAnalysis.session_context(hist_df)
                except Exception:
                    self.logger.exception("Error running historical pipeline")

            # Combine signals for confluence scoring while preserving source labels
            merged_for_confluence = {}
            merged_for_confluence.update({f'current::{k}': v for k, v in current_signals.items()})
            # flatten historical_signals for scoring
            for hk, hv in (historical_signals.items()):
                if isinstance(hv, dict):
                    for subk, subv in hv.items():
                        merged_for_confluence[f'history::{hk}::{subk}'] = subv
                else:
                    merged_for_confluence[f'history::{hk}'] = hv

            confluence_score = ConfluenceAnalysis.calculate_confluence_score(merged_for_confluence)

            result = self.create_result(
                confluence_score=confluence_score,
                analysis={
                    'current_analysis': current_signals,
                    'historical_structure_analysis': historical_signals,
                },
                signal_count=len(merged_for_confluence),
                bullish_signals=ConfluenceAnalysis.bullish_confluence_count(merged_for_confluence),
                bearish_signals=ConfluenceAnalysis.bearish_confluence_count(merged_for_confluence),
                rating=ConfluenceAnalysis.confluence_strength_rating(confluence_score)
            )

            # Determine setup status heuristically to improve precision and provide clear labels
            try:
                struct_score = 0.0
                patt_score = 0.0
                if historical_signals.get('structure_patterns'):
                    struct_score = float(historical_signals['structure_patterns'].get('structure_score', 0.0)) if isinstance(historical_signals['structure_patterns'], dict) else 0.0
                if historical_signals.get('candlestick_patterns'):
                    patt_score = float(historical_signals['candlestick_patterns'].get('pattern_score', 0.0)) if isinstance(historical_signals['candlestick_patterns'], dict) else 0.0

                # Basic rules: require structure + confluence for valid; forming when near thresholds
                status = 'no_setup'
                reasoning = []
                direction = 'neutral'

                if confluence_score >= 65 and struct_score >= 55 and patt_score >= 50:
                    status = 'valid'
                    reasoning.append('High confluence with structural confirmation')
                elif confluence_score >= 50 or struct_score >= 50 or patt_score >= 45:
                    status = 'forming'
                    reasoning.append('Signals forming; watch closely')
                else:
                    status = 'no_setup'
                    reasoning.append('No clear confluence or structure')

                # Direction: simple bias from confluence average
                direction = 'bullish' if confluence_score > 52 else 'bearish' if confluence_score < 48 else 'neutral'

                result['setup_status'] = status
                result['direction'] = direction
                result['reasoning'] = {'confluence': confluence_score, 'structure_score': struct_score, 'pattern_score': patt_score, 'notes': reasoning}
            except Exception:
                self.logger.exception('Error computing setup_status')

            return result

        # Unsupported input
        return self.create_result(confluence_score=0.0, error='Unsupported data input to analyze()')
