"""Application lifecycle management."""

from typing import Optional, Callable
from enum import Enum
from core.logger import get_logger


class AppState(Enum):
    """Application state enumeration."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    SHUTTING_DOWN = "shutting_down"
    SHUTDOWN = "shutdown"
    ERROR = "error"


class LifecycleManager:
    """Manages application lifecycle and state transitions."""

    def __init__(self):
        """Initialize the lifecycle manager."""
        self.logger = get_logger()
        self._state = AppState.INITIALIZING
        self._on_state_change_callbacks = []

    @property
    def state(self) -> AppState:
        """Get current application state."""
        return self._state

    def register_state_change_callback(self, callback: Callable[[AppState, AppState], None]):
        """Register a callback for state changes."""
        self._on_state_change_callbacks.append(callback)

    def transition_to(self, new_state: AppState) -> bool:
        """Transition to a new state with validation."""
        old_state = self._state

        # Validate state transitions
        valid_transitions = {
            AppState.INITIALIZING: [AppState.RUNNING, AppState.ERROR, AppState.SHUTDOWN],
            AppState.RUNNING: [AppState.PAUSED, AppState.SHUTTING_DOWN, AppState.ERROR],
            AppState.PAUSED: [AppState.RUNNING, AppState.SHUTTING_DOWN, AppState.ERROR],
            AppState.SHUTTING_DOWN: [AppState.SHUTDOWN, AppState.ERROR],
            AppState.SHUTDOWN: [],
            AppState.ERROR: [AppState.SHUTDOWN, AppState.INITIALIZING],
        }

        if new_state not in valid_transitions.get(old_state, []):
            self.logger.warning(
                f"Invalid state transition: {old_state.value} -> {new_state.value}"
            )
            return False

        self._state = new_state
        self.logger.info(f"State transition: {old_state.value} -> {new_state.value}")

        # Trigger callbacks
        for callback in self._on_state_change_callbacks:
            try:
                callback(old_state, new_state)
            except Exception as e:
                self.logger.error(f"Error in state change callback: {e}")

        return True

    def is_running(self) -> bool:
        """Check if application is in running state."""
        return self._state == AppState.RUNNING

    def is_shutdown(self) -> bool:
        """Check if application is shutdown."""
        return self._state == AppState.SHUTDOWN
