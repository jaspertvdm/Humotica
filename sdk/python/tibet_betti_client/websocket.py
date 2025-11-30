"""
WebSocket client for real-time TIBET/context updates
"""

import json
import logging
import threading
from typing import Optional, Callable, Dict, Any

try:
    import websocket
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False

logger = logging.getLogger(__name__)


class TibetWebSocket:
    """
    WebSocket client for real-time TIBET intent and context updates

    Example:
        >>> def handle_message(msg):
        ...     print(f"Received: {msg}")
        >>>
        >>> def handle_tibet(tibet_data):
        ...     print(f"TIBET intent: {tibet_data['intent']}")
        >>>
        >>> ws = TibetWebSocket(
        ...     url="ws://localhost:8000/ws/user_123",
        ...     on_message=handle_message,
        ...     on_tibet=handle_tibet
        ... )
        >>> ws.start()  # Runs in background thread
    """

    def __init__(
        self,
        url: str,
        on_message: Callable[[Dict[str, Any]], None],
        on_tibet: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_context_update: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_close: Optional[Callable[[], None]] = None
    ):
        """
        Initialize WebSocket client

        Args:
            url: WebSocket URL (ws://...)
            on_message: Callback for any message
            on_tibet: Optional callback for TIBET intents specifically
            on_context_update: Optional callback for context updates
            on_error: Optional error callback
            on_close: Optional close callback
        """
        if not HAS_WEBSOCKET:
            raise ImportError(
                "websocket-client not installed. "
                "Install with: pip install websocket-client"
            )

        self.url = url
        self.on_message = on_message
        self.on_tibet = on_tibet
        self.on_context_update = on_context_update
        self.on_error = on_error
        self.on_close = on_close

        self.ws: Optional[websocket.WebSocketApp] = None
        self.thread: Optional[threading.Thread] = None
        self.running = False

    def _handle_message(self, ws, message):
        """Internal message handler"""
        try:
            data = json.loads(message)

            # Call general message handler
            self.on_message(data)

            # Call specific handlers
            msg_type = data.get("type")

            if msg_type == "tibet" and self.on_tibet:
                self.on_tibet(data)

            elif msg_type == "context_update" and self.on_context_update:
                self.on_context_update(data)

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            if self.on_error:
                self.on_error(e)

    def _handle_error(self, ws, error):
        """Internal error handler"""
        logger.error(f"WebSocket error: {error}")
        if self.on_error:
            self.on_error(error)

    def _handle_close(self, ws, close_status_code, close_msg):
        """Internal close handler"""
        logger.info(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.running = False
        if self.on_close:
            self.on_close()

    def _handle_open(self, ws):
        """Internal open handler"""
        logger.info(f"WebSocket connected to {self.url}")
        self.running = True

    def start(self, block: bool = False):
        """
        Start WebSocket connection

        Args:
            block: If True, blocks current thread. If False, runs in background.

        Example:
            >>> ws.start(block=False)  # Background
            >>> # or
            >>> ws.start(block=True)   # Blocks until closed
        """
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self._handle_open,
            on_message=self._handle_message,
            on_error=self._handle_error,
            on_close=self._handle_close
        )

        if block:
            # Run in current thread (blocking)
            self.ws.run_forever()
        else:
            # Run in background thread
            self.thread = threading.Thread(
                target=self.ws.run_forever,
                daemon=True
            )
            self.thread.start()
            logger.info("WebSocket started in background")

    def send(self, data: Dict[str, Any]):
        """
        Send message through WebSocket

        Args:
            data: Data to send (will be JSON-encoded)

        Example:
            >>> ws.send({"type": "ping"})
        """
        if not self.ws or not self.running:
            raise RuntimeError("WebSocket not connected")

        message = json.dumps(data)
        self.ws.send(message)

    def close(self):
        """Close WebSocket connection"""
        if self.ws:
            self.ws.close()
            self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

        logger.info("WebSocket closed")

    def is_connected(self) -> bool:
        """Check if WebSocket is connected"""
        return self.running

    def __enter__(self):
        """Context manager entry"""
        self.start(block=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
