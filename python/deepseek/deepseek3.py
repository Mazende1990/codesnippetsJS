"""
Signal handling implementation with fallback for when blinker is not available.
"""

class _FakeSignal:
    """
    Fake signal implementation when blinker is not available.
    
    Provides the same interface as blinker.Signal but raises exceptions for
    all operations except send() which becomes a no-op.
    """
    
    def __init__(self, name, doc=None):
        self.name = name
        self.__doc__ = doc or f"Fake signal for {name} (blinker not installed)"

    def send(self, *args, **kwargs):
        """No-op implementation when blinker is not available."""
        pass

    def _unsupported_operation(self, *args, **kwargs):
        raise RuntimeError(
            "Signaling support is unavailable because the blinker library is not installed. "
            "Install Flask with 'pip install flask[signals]' to enable."
        )

    # All other signal operations raise an exception
    connect = connect_via = connected_to = temporarily_connected_to = _unsupported_operation
    disconnect = _unsupported_operation
    has_receivers_for = receivers_for = _unsupported_operation


# Try to import blinker, fall back to fake implementation if not available
try:
    from blinker import Namespace
    signals_available = True
except ImportError:
    signals_available = False
    
    class Namespace:
        """Fake namespace implementation when blinker is not available."""
        
        def signal(self, name, doc=None):
            return _FakeSignal(name, doc)


# Flask's core signal namespace
_signals = Namespace()


# Core Flask signals with documentation
template_rendered = _signals.signal(
    "template-rendered",
    doc="Signal sent when a template was successfully rendered."
)

before_render_template = _signals.signal(
    "before-render-template", 
    doc="Signal sent before a template is rendered."
)

request_started = _signals.signal(
    "request-started",
    doc="Signal sent when a request context is set up."
)

request_finished = _signals.signal(
    "request-finished",
    doc="Signal sent when the response is sent and the request context is torn down."
)

request_tearing_down = _signals.signal(
    "request-tearing-down",
    doc="Signal sent when the request context is being torn down."
)

got_request_exception = _signals.signal(
    "got-request-exception",
    doc="Signal sent when an exception occurs during request handling."
)

appcontext_tearing_down = _signals.signal(
    "appcontext-tearing-down",
    doc="Signal sent when the application context is being torn down."
)

appcontext_pushed = _signals.signal(
    "appcontext-pushed",
    doc="Signal sent when an application context is pushed."
)

appcontext_popped = _signals.signal(
    "appcontext-popped",
    doc="Signal sent when an application context is popped."
)

message_flashed = _signals.signal(
    "message-flashed",
    doc="Signal sent when the flask.flash() function is called."
)