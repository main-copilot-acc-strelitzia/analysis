"""General-purpose analyzer for indices, commodities, crypto, and uncategorized symbols."""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from analysis.base import BaseAnalyzer
from analysis.shared.indicators import TechnicalIndicators
from analysis.shared.statistics import StatisticalAnalysis
from analysis.shared.utils import AnalysisUtils
from analysis.shared.multi_candle_price_action import MultiCandlePriceAction
from analysis.shared.candlestick_patterns_advanced import CandlestickPatternAnalyzer
from analysis.shared.chart_patterns_advanced import ChartPatternAnalyzer
from analysis.shared.structure_price_action_patterns import StructurePriceActionAnalyzer
from analysis.forex.market_structure import MarketStructureAnalysis
from analysis.forex.trend import TrendAnalysis
from analysis.forex.momentum import MomentumAnalysis
from analysis.forex.volatility import VolatilityAnalysis
from analysis.forex.volume import VolumeAnalysis
from analysis.forex.support_resistance import SupportResistanceAnalysis
from analysis.forex.candlestick_patterns import CandlestickPatternAnalysis
from core.logger import get_logger
from config.settings import ANALYSIS_CONFIG


class GeneralAssetAnalyzer(BaseAnalyzer):
    """
    General-purpose analyzer for any asset type with configurable depth.
    
    Provides comprehensive analysis for:
    - Indices (stock indices, volatility indices)
    - Commodities (metals, energy, agriculture)
    - Cryptocurrencies
    - Any other uncategorized symbols
    
    Implements 300+ analysis methods:
    - 30 indicator-based signals (trend, momentum, volatility, volume, patterns, structure)
    - 1 multi-candle price action analysis
    - 80+ candlestick patterns (single, multi-candle, advanced, directional flow)
    - 100+ chart patterns (reversals, continuations, consolidations)
    - 200+ structure/price-action patterns (trends, S/R, formations, breakouts, market behavior)
    
    Analysis depth modes:
    - 'fast': Quick scan with 10 core signals (fast performance)
    - 'standard': Full analysis with 33+ signals (balanced)
    - 'deep': Comprehensive analysis with all signals + extra checks (thorough)
    """

    def __init__(self, symbol: str, timeframe: str, analysis_depth: Optional[str] = None):
        """
        Initialize general asset analyzer.
        
        Args:
            symbol: Asset symbol
            timeframe: Timeframe for analysis
            analysis_depth: 'fast', 'standard', or 'deep' (uses config if None)
        """
        super().__init__(symbol, timeframe)
        self.logger = get_logger()
        self.analysis_depth = analysis_depth or ANALYSIS_CONFIG.get('analysis_depth', 'standard')
        self.explanation_verbosity = ANALYSIS_CONFIG.get('explanation_verbosity', 'concise')
        self._signal_explanations = []
        self.price_action = MultiCandlePriceAction()
        self.candlestick_patterns = CandlestickPatternAnalyzer()
        self.chart_patterns = ChartPatternAnalyzer()
        self.structure_patterns = StructurePriceActionAnalyzer()

    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform analysis with configurable depth.
        
        Implements 300+ analysis methods:
        - 30 indicator-based signals (trend, momentum, volatility, volume, patterns, structure)
        - 1 multi-candle price action analysis (sequential candle behavior analysis)
        - 80+ candlestick patterns (single, multi-candle, advanced, directional flow)
        - 100+ chart patterns (reversals, continuations, consolidations)
        - 200+ structure/price-action patterns (trends, S/R, formations, breakouts, market behavior)
        
        Args:
            data: OHLCV DataFrame
            
        Returns:
            Dict with confluence score and analysis results.
        """
        if not self.validate_data(data):
            return self.create_result(
                confluence_score=0.0,
                error="Insufficient or invalid data",
                analysis_depth=self.analysis_depth
            )

        try:
            signals = {}
            self._signal_explanations = []
            
            # FAST MODE: 10 core signals only
            if self.analysis_depth == 'fast':
                signals['ma_trend'] = TrendAnalysis.moving_average_crossover(data)
                signals['rsi_momentum'] = MomentumAnalysis.rsi_momentum(data)
                signals['volume_trend'] = VolumeAnalysis.volume_trend(data)
                signals['volatility_level'] = VolatilityAnalysis.volatility_expansion(data)
                signals['support_resistance'] = SupportResistanceAnalysis.support_resistance_levels(data)
                signals['trend_strength'] = TrendAnalysis.trend_strength_confirmation(data)
                signals['macd_momentum'] = MomentumAnalysis.macd_signal(data)
                signals['breakout_detection'] = self._detect_breakout(data)
                signals['stochastic_momentum'] = MomentumAnalysis.stochastic_momentum(data)
                signals['pattern_confirmation'] = CandlestickPatternAnalysis.multi_pattern_confirmation(data)
            
            # STANDARD MODE: 33+ signals (balanced performance/comprehensiveness)
            elif self.analysis_depth == 'standard':
                # Price Action & Structure (6 methods)
                signals['higher_highs'] = MarketStructureAnalysis.higher_highs_lower_lows(data)
                signals['price_action'] = MarketStructureAnalysis.price_action_patterns(data)
                signals['market_regime'] = MarketStructureAnalysis.market_regime(data)
                signals['breakout_detection'] = self._detect_breakout(data)
                signals['pullback_detection'] = self._detect_pullback(data)
                signals['consolidation'] = self._detect_consolidation(data)

                # Trend Analysis (6 methods)
                signals['ma_trend'] = TrendAnalysis.moving_average_crossover(data)
                signals['trend_strength'] = TrendAnalysis.trend_strength_confirmation(data)
                signals['trend_direction'] = TrendAnalysis.trend_direction_detection(data)
                signals['adx_trend'] = MomentumAnalysis.adx_momentum(data)
                signals['rsi_trend'] = MomentumAnalysis.rsi_momentum(data)
                signals['macd_trend'] = MomentumAnalysis.macd_divergence_detection(data)

                # Momentum & Oscillators (6 methods)
                signals['rsi_momentum'] = MomentumAnalysis.rsi_momentum(data)
                signals['stochastic_momentum'] = MomentumAnalysis.stochastic_momentum(data)
                signals['cci_momentum'] = MomentumAnalysis.cci_momentum(data)
                signals['williams_momentum'] = MomentumAnalysis.williams_percent_range(data)
                signals['macd_momentum'] = MomentumAnalysis.macd_signal(data)
                signals['obv_momentum'] = self._on_balance_volume_analysis(data)

                # Volatility Analysis (6 methods)
                signals['volatility_level'] = VolatilityAnalysis.volatility_expansion(data)
                signals['bollinger_bands'] = VolatilityAnalysis.bollinger_bands_squeeze(data)
                signals['atr_volatility'] = VolatilityAnalysis.atr_expansion(data)
                signals['volatility_regime'] = VolatilityAnalysis.volatility_regime_detection(data)
                signals['range_expansion'] = self._range_expansion_analysis(data)
                signals['volatility_mean_reversion'] = self._volatility_mean_reversion(data)

                # Volume Analysis (6 methods)
                signals['volume_trend'] = VolumeAnalysis.volume_trend(data)
                signals['volume_confirmation'] = VolumeAnalysis.volume_confirmation_signal(data)
                signals['volume_divergence'] = VolumeAnalysis.volume_price_divergence(data)
                signals['volume_accumulation'] = VolumeAnalysis.accumulation_distribution_signal(data)
                signals['volume_spike'] = VolumeAnalysis.volume_spike_detection(data)
                signals['volume_profile'] = self._volume_profile_analysis(data)

                # Support & Resistance (3 methods)
                signals['support_resistance'] = SupportResistanceAnalysis.support_resistance_levels(data)
                signals['pivot_levels'] = SupportResistanceAnalysis.pivot_point_analysis(data)
                signals['level_confluence'] = SupportResistanceAnalysis.multiple_resistance_confluence(data)
            
            # DEEP MODE: All signals + extra validation
            elif self.analysis_depth == 'deep':
                # Same as standard mode but with additional analysis
                # Price Action & Structure (6 methods)
                signals['higher_highs'] = MarketStructureAnalysis.higher_highs_lower_lows(data)
                signals['price_action'] = MarketStructureAnalysis.price_action_patterns(data)
                signals['market_regime'] = MarketStructureAnalysis.market_regime(data)
                signals['breakout_detection'] = self._detect_breakout(data)
                signals['pullback_detection'] = self._detect_pullback(data)
                signals['consolidation'] = self._detect_consolidation(data)

                # Trend Analysis (6 methods)
                signals['ma_trend'] = TrendAnalysis.moving_average_crossover(data)
                signals['trend_strength'] = TrendAnalysis.trend_strength_confirmation(data)
                signals['trend_direction'] = TrendAnalysis.trend_direction_detection(data)
                signals['adx_trend'] = MomentumAnalysis.adx_momentum(data)
                signals['rsi_trend'] = MomentumAnalysis.rsi_momentum(data)
                signals['macd_trend'] = MomentumAnalysis.macd_divergence_detection(data)

                # Momentum & Oscillators (6 methods)
                signals['rsi_momentum'] = MomentumAnalysis.rsi_momentum(data)
                signals['stochastic_momentum'] = MomentumAnalysis.stochastic_momentum(data)
                signals['cci_momentum'] = MomentumAnalysis.cci_momentum(data)
                signals['williams_momentum'] = MomentumAnalysis.williams_percent_range(data)
                signals['macd_momentum'] = MomentumAnalysis.macd_signal(data)
                signals['obv_momentum'] = self._on_balance_volume_analysis(data)

                # Volatility Analysis (6 methods)
                signals['volatility_level'] = VolatilityAnalysis.volatility_expansion(data)
                signals['bollinger_bands'] = VolatilityAnalysis.bollinger_bands_squeeze(data)
                signals['atr_volatility'] = VolatilityAnalysis.atr_expansion(data)
                signals['volatility_regime'] = VolatilityAnalysis.volatility_regime_detection(data)
                signals['range_expansion'] = self._range_expansion_analysis(data)
                signals['volatility_mean_reversion'] = self._volatility_mean_reversion(data)

                # Volume Analysis (6 methods)
                signals['volume_trend'] = VolumeAnalysis.volume_trend(data)
                signals['volume_confirmation'] = VolumeAnalysis.volume_confirmation_signal(data)
                signals['volume_divergence'] = VolumeAnalysis.volume_price_divergence(data)
                signals['volume_accumulation'] = VolumeAnalysis.accumulation_distribution_signal(data)
                signals['volume_spike'] = VolumeAnalysis.volume_spike_detection(data)
                signals['volume_profile'] = self._volume_profile_analysis(data)

                # Support & Resistance (3 methods)
                signals['support_resistance'] = SupportResistanceAnalysis.support_resistance_levels(data)
                signals['pivot_levels'] = SupportResistanceAnalysis.pivot_point_analysis(data)
                signals['level_confluence'] = SupportResistanceAnalysis.multiple_resistance_confluence(data)
                
                # Additional deep analysis
                signals['correlation_analysis'] = StatisticalAnalysis.correlation_with_market(data)
                signals['distribution_analysis'] = StatisticalAnalysis.price_distribution_analysis(data)
                signals['anomaly_detection'] = StatisticalAnalysis.anomaly_detection(data)

            # Multi-Candle Price Action Analysis (1 method) - behavioral analysis of price flow sequences
            # Separate from candlestick patterns (individual shape analysis) and indicators (mathematical analysis)
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

            # Candlestick Patterns (3 methods) - all modes
            signals['pattern_doji'] = CandlestickPatternAnalysis.doji_pattern(data)
            signals['pattern_engulfing'] = CandlestickPatternAnalysis.engulfing_pattern(data)
            signals['pattern_hammer'] = CandlestickPatternAnalysis.hammer_pattern(data)

            # Calculate confluence score
            confluence_score = self._calculate_confluence(signals)
            
            # Build explanation if enabled
            explanation = ""
            if ANALYSIS_CONFIG.get('include_explanations', True):
                explanation = self._generate_explanation(signals, confluence_score)

            return self.create_result(
                confluence_score=confluence_score,
                analysis=signals,
                signal_count=len(signals),
                bullish_signals=sum(1 for v in signals.values() if isinstance(v, (int, float)) and v > 60),
                bearish_signals=sum(1 for v in signals.values() if isinstance(v, (int, float)) and v < 40),
                rating=self._get_rating(confluence_score),
                analysis_depth=self.analysis_depth,
                explanation=explanation,
                signal_sources=self._signal_explanations
            )

        except Exception as e:
            self.logger.error(f"Error in general asset analysis: {e}")
            return self.create_result(
                confluence_score=0.0,
                error=str(e)
            )

    def _detect_breakout(self, data: pd.DataFrame) -> float:
        """Detect price breakout above/below recent levels."""
        try:
            if len(data) < 20:
                return 50.0
            
            recent_high = data['High'].iloc[-20:-1].max()
            recent_low = data['Low'].iloc[-20:-1].min()
            current_close = data['Close'].iloc[-1]
            
            if current_close > recent_high:
                return 75.0  # Bullish breakout
            elif current_close < recent_low:
                return 25.0  # Bearish breakout
            else:
                return 50.0  # No breakout
        except Exception as e:
            self.logger.debug(f"Breakout detection error: {e}")
            return 50.0

    def _detect_pullback(self, data: pd.DataFrame) -> float:
        """Detect pullback to support/resistance during trend."""
        try:
            if len(data) < 30:
                return 50.0
            
            recent_high = data['High'].iloc[-30:].max()
            recent_low = data['Low'].iloc[-30:].min()
            mid_point = (recent_high + recent_low) / 2
            current_price = (data['Open'].iloc[-1] + data['Close'].iloc[-1]) / 2
            
            # Price pulled back to midpoint = potentially strong signal
            if abs(current_price - mid_point) < (recent_high - recent_low) * 0.1:
                return 70.0
            else:
                return 50.0
        except Exception as e:
            self.logger.debug(f"Pullback detection error: {e}")
            return 50.0

    def _detect_consolidation(self, data: pd.DataFrame) -> float:
        """Detect consolidation/accumulation phase."""
        try:
            if len(data) < 20:
                return 50.0
            
            recent_data = data.iloc[-20:]
            range_sizes = recent_data['High'] - recent_data['Low']
            avg_range = range_sizes.mean()
            current_range = range_sizes.iloc[-1]
            
            # Smaller range = consolidation
            if current_range < avg_range * 0.6:
                return 70.0  # Consolidation detected
            else:
                return 50.0
        except Exception as e:
            self.logger.debug(f"Consolidation detection error: {e}")
            return 50.0

    def _on_balance_volume_analysis(self, data: pd.DataFrame) -> float:
        """Analyze on-balance volume trend."""
        try:
            if len(data) < 10 or 'Volume' not in data.columns:
                return 50.0
            
            obv = self._calculate_obv(data)
            recent_obv = obv.iloc[-10:]
            
            # OBV trending up = bullish
            if recent_obv.iloc[-1] > recent_obv.iloc[0]:
                trend_strength = min(100.0, (recent_obv.iloc[-1] / recent_obv.iloc[0]) * 50)
                return 50.0 + trend_strength / 2
            else:
                trend_strength = min(100.0, (recent_obv.iloc[0] / recent_obv.iloc[-1]) * 50)
                return 50.0 - trend_strength / 2
        except Exception as e:
            self.logger.debug(f"OBV analysis error: {e}")
            return 50.0

    def _calculate_obv(self, data: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume."""
        obv = pd.Series(0.0, index=data.index)
        volume = data['Volume'].values
        closes = data['Close'].values
        
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume[i]
            elif closes[i] < closes[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv

    def _range_expansion_analysis(self, data: pd.DataFrame) -> float:
        """Analyze price range expansion."""
        try:
            if len(data) < 20:
                return 50.0
            
            recent_ranges = (data['High'] - data['Low']).iloc[-20:]
            avg_range = recent_ranges.mean()
            current_range = data['High'].iloc[-1] - data['Low'].iloc[-1]
            
            # Current range vs average
            if current_range > avg_range * 1.3:
                return 70.0  # Range expansion
            elif current_range < avg_range * 0.7:
                return 30.0  # Range contraction
            else:
                return 50.0
        except Exception as e:
            self.logger.debug(f"Range expansion error: {e}")
            return 50.0

    def _volatility_mean_reversion(self, data: pd.DataFrame) -> float:
        """Detect volatility mean reversion opportunities."""
        try:
            if len(data) < 30:
                return 50.0
            
            ranges = data['High'] - data['Low']
            recent_ranges = ranges.iloc[-10:].mean()
            historical_ranges = ranges.iloc[-30:-10].mean()
            
            # High volatility relative to recent average = reversion signal
            if recent_ranges > historical_ranges * 1.5:
                return 70.0  # Volatility spike (mean reversion likely)
            elif recent_ranges < historical_ranges * 0.7:
                return 30.0  # Low volatility expansion likely
            else:
                return 50.0
        except Exception as e:
            self.logger.debug(f"Volatility mean reversion error: {e}")
            return 50.0

    def _volume_profile_analysis(self, data: pd.DataFrame) -> float:
        """Analyze volume distribution profile."""
        try:
            if len(data) < 20 or 'Volume' not in data.columns:
                return 50.0
            
            # Volume trend (increasing/decreasing)
            recent_volume = data['Volume'].iloc[-10:].mean()
            historical_volume = data['Volume'].iloc[-30:-10].mean()
            
            if recent_volume > historical_volume * 1.2:
                return 70.0  # Increasing volume (bullish)
            elif recent_volume < historical_volume * 0.8:
                return 30.0  # Decreasing volume (bearish)
            else:
                return 50.0
        except Exception as e:
            self.logger.debug(f"Volume profile error: {e}")
            return 50.0

    def _calculate_confluence(self, signals: Dict[str, Any]) -> float:
        """Calculate confluence score from all signals."""
        try:
            numeric_signals = [v for v in signals.values() if isinstance(v, (int, float))]
            if not numeric_signals:
                return 50.0
            
            return float(np.mean(numeric_signals))
        except Exception as e:
            self.logger.debug(f"Confluence calculation error: {e}")
            return 50.0

    def _get_rating(self, confidence: float) -> str:
        """Get rating text for confidence score."""
        if confidence >= 80:
            return "Strong Bullish"
        elif confidence >= 65:
            return "Bullish"
        elif confidence >= 55:
            return "Moderate Bullish"
        elif confidence >= 45:
            return "Neutral"
        elif confidence >= 35:
            return "Moderate Bearish"
        elif confidence >= 20:
            return "Bearish"
        else:
            return "Strong Bearish"
    
    def _generate_explanation(self, signals: Dict[str, Any], confluence_score: float) -> str:
        """
        Generate human-readable explanation of why the bias was produced.
        Helps users understand which signals contributed to the score.
        
        Args:
            signals: Dictionary of all signals
            confluence_score: Final confluence score
            
        Returns:
            str: Human-readable explanation
        """
        try:
            verbosity = self.explanation_verbosity
            
            # Get top contributing signals
            numeric_signals = {}
            for name, value in signals.items():
                if isinstance(value, (int, float)):
                    numeric_signals[name] = value
            
            if not numeric_signals:
                return f"Analysis produced a {self._get_rating(confluence_score)} bias with score {confluence_score:.1f}. Insufficient data for detailed explanation."
            
            # Sort by deviation from neutral (50)
            sorted_signals = sorted(
                numeric_signals.items(),
                key=lambda x: abs(x[1] - 50),
                reverse=True
            )
            
            bullish = sum(1 for v in numeric_signals.values() if v > 60)
            bearish = sum(1 for v in numeric_signals.values() if v < 40)
            neutral = sum(1 for v in numeric_signals.values() if 40 <= v <= 60)
            
            if verbosity == 'minimal':
                return f"{self._get_rating(confluence_score)}: {confluence_score:.1f} ({bullish}↑ {bearish}↓ {neutral}→)"
            
            elif verbosity == 'concise':
                top_signals = sorted_signals[:3]
                signal_reasons = []
                for signal_name, value in top_signals:
                    direction = "Bullish" if value > 60 else "Bearish" if value < 40 else "Neutral"
                    signal_reasons.append(f"{signal_name} ({direction}: {value:.0f})")
                
                reason_text = ", ".join(signal_reasons)
                return (
                    f"{self._get_rating(confluence_score)} bias ({confluence_score:.1f}). "
                    f"Top factors: {reason_text}. "
                    f"Overall: {bullish} bullish, {bearish} bearish, {neutral} neutral signals."
                )
            
            else:  # detailed
                top_signals = sorted_signals[:5]
                signal_reasons = []
                for signal_name, value in top_signals:
                    direction = "BULLISH" if value > 60 else "BEARISH" if value < 40 else "NEUTRAL"
                    confidence_level = "Strong" if abs(value - 50) > 30 else "Moderate" if abs(value - 50) > 15 else "Weak"
                    signal_reasons.append(
                        f"  - {signal_name}: {direction} ({confidence_level}, score: {value:.1f})"
                    )
                
                reason_text = "\n".join(signal_reasons)
                return (
                    f"Analysis Result: {self._get_rating(confluence_score).upper()}\n"
                    f"Confluence Score: {confluence_score:.1f}\n"
                    f"\nTop Contributing Signals:\n{reason_text}\n"
                    f"\nSignal Summary: {bullish} Bullish, {bearish} Bearish, {neutral} Neutral\n"
                    f"Analysis Depth: {self.analysis_depth.upper()}\n"
                    f"Total Signals Evaluated: {len(numeric_signals)}"
                )
        
        except Exception as e:
            self.logger.debug(f"Error generating explanation: {e}")
            return f"Analysis produced {self._get_rating(confluence_score)} bias ({confluence_score:.1f})"

