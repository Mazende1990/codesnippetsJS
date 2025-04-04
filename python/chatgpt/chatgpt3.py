try:
    from blinker import Namespace
    signals_available = True

except ImportError:
    signals_available = False

    class _FakeSignal:
        """
        A fallback signal implementation if blinker is not installed.
        Supports `send`, but raises errors on all other signal-related operations.
        """

        def __init__(self, name, doc=None):
            self.name = name
            self.__doc__ = doc

        def send(self, *args, **kwargs):
            # Sending does nothing without blinker.
            pass

        def _fail(self, *args, **kwargs):
            raise RuntimeError(
                "Signalling support is unavailable because the 'blinker' "
                "library is not installed."
            )

        # Assign all unsupported signal methods to the failing handler.
        connect = connect_via = connected_to = temporarily_connected_to = _fail
        disconnect = has_receivers_for = receivers_for = _fail
        del _fail

    class Namespace:
        """
        A fake Namespace to mimic blinker when unavailable.
        Only `.signal()` is supported and returns a _FakeSignal.
        """
        def signal(self, name, doc=None):
            return _FakeSignal(name, doc)

# Define the global signal namespace.
# If you are not part of this core module, create a separate namespace.
_signals = Namespace()

# Core application signals
# These provide hooks into key events in the request/response lifecycle.
template_rendered = _signals.signal("template-rendered")
before_render_template = _signals.signal("before-render-template")

request_started = _signals.signal("request-started")
request_finished = _signals.signal("request-finished")
request_tearing_down = _signals.signal("request-tearing-down")
got_request_exception = _signals.signal("got-request-exception")

appcontext_tearing_down = _signals.signal("appcontext-tearing-down")
appcontext_pushed = _signals.signal("appcontext-pushed")
appcontext_popped = _signals.signal("appcontext-popped")

message_flashed = _signals.signal("message-flashed")
