"""
Connection repository for managing connection data.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from models.connection import Connection, ConnectionStatus
from .base import BaseRepository


class ConnectionRepository(BaseRepository[Connection]):
    """Repository for managing connections."""
    
    def get_active_connections(self) -> List[Connection]:
        """Get all active connections."""
        return [
            conn for conn in self._storage.values()
            if conn.is_active()
        ]
    
    def get_by_status(self, status: ConnectionStatus) -> List[Connection]:
        """Get connections by status."""
        return self.find_by(status=status)
    
    def get_by_tc375_device(self, device_id: str) -> Optional[Connection]:
        """Get connection by TC375 device ID."""
        results = self.find_by(tc375_device_id=device_id)
        return results[0] if results else None
    
    def get_by_pqc_session(self, session_id: str) -> Optional[Connection]:
        """Get connection by PQC session ID."""
        results = self.find_by(pqc_session_id=session_id)
        return results[0] if results else None
    
    def get_inactive_connections(self, timeout_seconds: int = 300) -> List[Connection]:
        """Get connections that have been inactive for too long."""
        cutoff_time = datetime.utcnow() - timedelta(seconds=timeout_seconds)
        return [
            conn for conn in self._storage.values()
            if conn.is_active() and conn.last_activity < cutoff_time
        ]
    
    def get_connections_by_address(self, address: str) -> List[Connection]:
        """Get connections from specific address."""
        return [
            conn for conn in self._storage.values()
            if conn.remote_address[0] == address
        ]
    
    def cleanup_disconnected(self, older_than_hours: int = 24) -> int:
        """Clean up old disconnected connections."""
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        to_delete = []
        
        for conn_id, conn in self._storage.items():
            if (conn.status == ConnectionStatus.DISCONNECTED and 
                conn.disconnected_at and 
                conn.disconnected_at < cutoff_time):
                to_delete.append(conn_id)
        
        for conn_id in to_delete:
            self.delete(conn_id)
        
        return len(to_delete)

