try:
    from blinker import Namespace

    _signals_available = True
except ImportError:
    _signals_available = False

    class Namespace:
        """Fallback Namespace class when blinker is not available."""

        def signal(self, name, doc=None):
            """Creates a fake signal."""
            return _FakeSignal(name, doc)

    class _FakeSignal:
        """
        Fake signal class that mimics blinker's Signal interface.

        Ignores send calls and raises an error for other operations.
        """

        def __init__(self, name, doc=None):
            self.name = name
            self.__doc__ = doc

        def send(self, *args, **kwargs):
            """Ignores send calls."""
            pass

        def _raise_blinker_unavailable(self, *args, **kwargs):
            """Raises an error indicating blinker is not installed."""
            raise RuntimeError(
                "Signalling support is unavailable because the blinker"
                " library is not installed."
            )

        connect = connect_via = connected_to = temporarily_connected_to = _raise_blinker_unavailable
        disconnect = _raise_blinker_unavailable
        has_receivers_for = receivers_for = _raise_blinker_unavailable

    del _FakeSignal._raise_blinker_unavailable


# The namespace for code signals. If you are not Flask code, do
# not put signals in here. Create your own namespace instead.
_core_signals = Namespace()


# Core signals. For usage examples grep the source code or consult
# the API documentation in docs/api.rst as well as docs/signals.rst
template_rendered = _core_signals.signal("template-rendered")
before_render_template = _core_signals.signal("before-render-template")
request_started = _core_signals.signal("request-started")
request_finished = _core_signals.signal("request-finished")
request_tearing_down = _core_signals.signal("request-tearing-down")
got_request_exception = _core_signals.signal("got-request-exception")
appcontext_tearing_down = _core_signals.signal("appcontext-tearing-down")
appcontext_pushed = _core_signals.signal("appcontext-pushed")
appcontext_popped = _core_signals.signal("appcontext-popped")
message_flashed = _core_signals.signal("message-flashed")