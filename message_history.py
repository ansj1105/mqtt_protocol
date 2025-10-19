"""
Simple message history storage (in-memory).
"""

from collections import deque
from datetime import datetime
from typing import Dict, Any, List
import threading


class MessageHistory:
    """Thread-safe message history storage."""
    
    def __init__(self, max_size: int = 1000):
        self._messages = deque(maxlen=max_size)
        self._lock = threading.Lock()
    
    def add_received(self, connection_id: str, message_type: str, payload: Dict[str, Any]):
        """Add a received message."""
        with self._lock:
            self._messages.append({
                "direction": "received",
                "connection_id": connection_id,
                "type": message_type,
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def add_sent(self, connection_id: str, message_type: str, payload: Dict[str, Any]):
        """Add a sent message."""
        with self._lock:
            self._messages.append({
                "direction": "sent",
                "connection_id": connection_id,
                "type": message_type,
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent messages."""
        with self._lock:
            messages = list(self._messages)
            messages.reverse()  # Most recent first
            return messages[:limit]
    
    def get_by_connection(self, connection_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages for a specific connection."""
        with self._lock:
            messages = [m for m in self._messages if m["connection_id"] == connection_id]
            messages.reverse()
            return messages[:limit]
    
    def get_received_only(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get only received messages."""
        with self._lock:
            messages = [m for m in self._messages if m["direction"] == "received"]
            messages.reverse()
            return messages[:limit]
    
    def clear(self):
        """Clear all messages."""
        with self._lock:
            self._messages.clear()


# Global instance
_message_history = MessageHistory(max_size=1000)


def get_message_history() -> MessageHistory:
    """Get the global message history instance."""
    return _message_history

