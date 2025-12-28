"""Configuration settings."""

# Analysis settings
ANALYSIS_CONFIG = {
    'default_timeframes': ['M15', 'H1', 'H4', 'D1'],
    'min_candles': 20,
    'max_candles': 500,
    'confluence_threshold': 60.0,
    'min_pattern_confidence': 40.0,  # Minimum confidence for candlestick patterns
    'pattern_weight': 0.6,  # Candlestick patterns weighted at 60% of normal signals
    'multi_timeframe_enabled': True,
    'account_monitor_interval': 5,  # Seconds between account change checks
    'analysis_depth': 'standard',  # 'fast' (quick scan), 'standard' (default), 'deep' (comprehensive)
    'include_explanations': True,  # Include human-readable signal explanations
    'explanation_verbosity': 'concise',  # 'minimal', 'concise', 'detailed'
}

# MT5 settings
MT5_CONFIG = {
    'connection_timeout': 10,
    'max_retries': 3,
    'retry_delay': 1.0,  # Initial delay between retries (seconds)
    'retry_backoff': 2.0,  # Backoff multiplier
    'symbol_refresh_interval': 300,  # Seconds between symbol list refreshes
}

# Symbol settings
SYMBOL_CONFIG = {
    'fetch_all_symbols': True,
    'enable_caching': True,
    'cache_duration_seconds': 3600,
    'auto_refresh_on_account_change': True,
    'invalid_until_reconnect_timeout': 30,  # Seconds to wait before retrying invalid symbols
}

# Logging settings
LOG_CONFIG = {
    'level': 'INFO',
    'file': 'strelitzia_trader.log',
    'max_file_size': 10485760,  # 10 MB
    'backup_count': 5,
    'verbosity': 'STANDARD',  # MINIMAL, STANDARD, VERBOSE, DEBUG
    'enable_debug_output': False,  # Extra verbose debug mode
}

# Timeframe weighting for multi-timeframe analysis
TIMEFRAME_WEIGHTS = {
    'M1': 0.6,
    'M5': 0.7,
    'M15': 0.8,
    'M30': 0.85,
    'H1': 0.9,
    'H4': 1.0,    # Reference timeframe
    'D1': 1.1,
    'W1': 1.2,
    'MN1': 1.3
}

# Pattern evaluation settings
PATTERN_EVAL_CONFIG = {
    'context_enabled': True,
    'trend_alignment_bonus': 1.15,  # 15% boost when aligned with trend
    'support_resistance_bonus': 1.20,  # 20% boost at key levels
    'high_volatility_penalty': 0.8,  # 20% penalty in high volatility
    'strong_candle_bonus': 1.10,  # 10% boost for strong candles
    'weak_candle_penalty': 0.7,  # 30% penalty for weak candles
    'min_reliability_threshold': 50.0,  # Minimum confidence for reliable patterns
}

# Performance settings
PERFORMANCE_CONFIG = {
    'enable_caching': True,
    'cache_staleness_factor': 1.5,  # Multiply timeframe minutes to determine staleness
    'parallel_timeframe_fetch': True,
    'batch_size_analysis': 5,  # Max symbols to analyze in parallel
    'ui_update_interval': 1.0,  # Seconds between UI updates
}

# UI Settings
UI_CONFIG = {
    'show_detailed_signals': True,
    'max_symbols_per_screen': 10,
    'show_timeframe_details': True,
    'show_confluence_details': True,
    'show_top_factors': True,
    'colorized_output': True,
}

# Robustness settings
ROBUSTNESS_CONFIG = {
    'max_consecutive_errors': 5,  # Errors before entering error state
    'graceful_degradation': True,
    'show_clear_error_messages': True,
    'auto_reconnect_enabled': True,
    'reconnect_delay': 2.0,  # Initial reconnect delay (seconds)
    'max_reconnect_attempts': 10,
    'session_change_detection_enabled': True,  # Auto-detect account/server changes
    'auto_reinitialize_on_session_change': True,  # Auto-reinit when account/server changes
    'data_availability_check': True,  # Check data sufficiency before analysis
    'fail_safe_mode': True,  # Prevent any trades/account modifications
}

# Safety guardrails
SAFETY_CONFIG = {
    'analysis_only_mode': True,  # NEVER place trades or modify account
    'prevent_order_functions': True,  # Block order-related MT5 functions
    'prevent_account_modifications': True,  # Block account-modifying operations
    'log_all_account_access': True,  # Log every account info access
}

