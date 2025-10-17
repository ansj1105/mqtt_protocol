"""
TC375 device repository.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from models.tc375 import TC375Device, TC375Status, TC375Protocol
from .base import BaseRepository


class TC375DeviceRepository(BaseRepository[TC375Device]):
    """Repository for managing TC375 devices."""
    
    def get_online_devices(self) -> List[TC375Device]:
        """Get all online devices."""
        return self.find_by(status=TC375Status.ONLINE)
    
    def get_by_connection(self, connection_id: str) -> Optional[TC375Device]:
        """Get device by connection ID."""
        results = self.find_by(connection_id=connection_id)
        return results[0] if results else None
    
    def get_by_protocol(self, protocol: TC375Protocol) -> List[TC375Device]:
        """Get devices by protocol version."""
        return self.find_by(protocol=protocol)
    
    def get_stale_devices(self, timeout_seconds: int = 60) -> List[TC375Device]:
        """Get devices with stale heartbeat."""
        cutoff_time = datetime.utcnow() - timedelta(seconds=timeout_seconds)
        return [
            device for device in self._storage.values()
            if device.last_heartbeat < cutoff_time and device.status == TC375Status.ONLINE
        ]
    
    def mark_offline(self, device_id: str) -> bool:
        """Mark device as offline."""
        device = self.get(device_id)
        if device:
            device.status = TC375Status.OFFLINE
            self.update(device_id, device)
            return True
        return False
    
    def update_heartbeat(self, device_id: str) -> bool:
        """Update device heartbeat."""
        device = self.get(device_id)
        if device:
            device.update_heartbeat()
            self.update(device_id, device)
            return True
        return False
    
    def get_device_statistics(self) -> dict:
        """Get statistics about devices."""
        devices = self.get_all()
        return {
            "total": len(devices),
            "online": len([d for d in devices if d.status == TC375Status.ONLINE]),
            "offline": len([d for d in devices if d.status == TC375Status.OFFLINE]),
            "busy": len([d for d in devices if d.status == TC375Status.BUSY]),
            "error": len([d for d in devices if d.status == TC375Status.ERROR]),
            "by_protocol": {
                "v1": len([d for d in devices if d.protocol == TC375Protocol.V1]),
                "v2": len([d for d in devices if d.protocol == TC375Protocol.V2]),
            }
        }

