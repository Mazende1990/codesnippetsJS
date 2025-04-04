"""
Flask signals module providing event notification capabilities.

This module defines core Flask signals and handles Blinker library availability
gracefully by providing a fallback implementation when Blinker is not installed.
"""

# Try to import Blinker, or create a fallback implementation
try:
    from blinker import Namespace
    signals_available = True
except ImportError:
    signals_available = False

    class Namespace:
        """Fallback Namespace implementation when Blinker is not available."""
        
        def signal(self, name, doc=None):
            """Create a new signal with the given name and documentation."""
            return _FakeSignal(name, doc)

    class _FakeSignal:
        """Fallback Signal implementation when Blinker is not available.
        
        This class mimics the Blinker Signal interface but only implements
        the 'send' method (as a no-op). All other methods raise a RuntimeError
        informing the user that Blinker is required for full signal functionality.
        """

        def __init__(self, name, doc=None):
            """Initialize a fake signal with a name and optional documentation."""
            self.name = name
            self.__doc__ = doc

        def send(self, *args, **kwargs):
            """Do nothing when sending signals in the fallback implementation."""
            pass

        def _fail(self, *args, **kwargs):
            """Helper method to raise an informative error about missing Blinker."""
            raise RuntimeError(
                "Signalling support is unavailable because the blinker"
                " library is not installed."
            )

        # Map all unimplemented methods to the _fail method
        connect = connect_via = connected_to = temporarily_connected_to = _fail
        disconnect = _fail
        has_receivers_for = receivers_for = _fail
        del _fail


# Create a namespace for Flask's internal signals
_signals = Namespace()


# Core Flask signals
#
# For usage examples:
# - Check the Flask source code
# - See API documentation in docs/api.rst 
# - See signals documentation in docs/signals.rst

# Template signals
template_rendered = _signals.signal("template-rendered")
before_render_template = _signals.signal("before-render-template")

# Request lifecycle signals
request_started = _signals.signal("request-started")
request_finished = _signals.signal("request-finished")
request_tearing_down = _signals.signal("request-tearing-down")
got_request_exception = _signals.signal("got-request-exception")

# Application context signals
appcontext_pushed = _signals.signal("appcontext-pushed")
appcontext_popped = _signals.signal("appcontext-popped")
appcontext_tearing_down = _signals.signal("appcontext-tearing-down")

# Flash messages signal
message_flashed = _signals.signal("message-flashed")