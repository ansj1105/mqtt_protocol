"""
TC375 device service for managing TC375 Litekit devices.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from models.tc375 import (
    TC375Device, TC375Command, TC375Response,
    TC375Protocol, TC375CommandType, TC375Status
)
from models.message import Message, MessageType
from repositories.tc375 import TC375DeviceRepository
from services.message_service import MessageService
from utils.logger import LoggerMixin
from utils.validators import validate_tc375_protocol
from config import Config


class TC375Service(LoggerMixin):
    """Service for managing TC375 devices."""
    
    def __init__(
        self,
        repository: TC375DeviceRepository,
        message_service: MessageService,
        config: Config
    ):
        self.repository = repository
        self.message_service = message_service
        self.config = config
    
    async def register_device(
        self,
        device_id: str,
        connection_id: str,
        protocol: str = "v2",
        firmware_version: Optional[str] = None,
        hardware_version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TC375Device:
        """
        Register a TC375 device.
        
        Args:
            device_id: Unique device ID
            connection_id: Associated connection ID
            protocol: Protocol version
            firmware_version: Firmware version
            hardware_version: Hardware version
            metadata: Additional metadata
        
        Returns:
            Registered device
        """
        # Validate protocol
        validate_tc375_protocol(protocol, self.config.tc375.supported_protocols)
        
        # Create device
        device = TC375Device(
            id=device_id,
            connection_id=connection_id,
            protocol=TC375Protocol(protocol),
            firmware_version=firmware_version,
            hardware_version=hardware_version,
            metadata=metadata or {}
        )
        
        # Save to repository
        self.repository.create(device_id, device)
        
        self.logger.info(
            f"TC375 device registered",
            extra={
                "device_id": device_id,
                "connection_id": connection_id,
                "protocol": protocol,
                "firmware_version": firmware_version
            }
        )
        
        return device
    
    async def unregister_device(self, device_id: str) -> bool:
        """Unregister a TC375 device."""
        device = self.repository.get(device_id)
        if not device:
            return False
        
        device.status = TC375Status.OFFLINE
        self.repository.update(device_id, device)
        
        self.logger.info(
            f"TC375 device unregistered",
            extra={"device_id": device_id}
        )
        
        return True
    
    async def update_heartbeat(self, device_id: str) -> bool:
        """Update device heartbeat."""
        success = self.repository.update_heartbeat(device_id)
        if success:
            self.logger.debug(f"Heartbeat updated for device: {device_id}")
        return success
    
    async def process_tc375_data(
        self,
        connection_id: str,
        payload: Dict[str, Any]
    ) -> TC375Response:
        """
        Process data from TC375 device.
        
        Args:
            connection_id: Source connection ID
            payload: Data payload
        
        Returns:
            Response to send back
        """
        device = self.repository.get_by_connection(connection_id)
        
        if not device:
            self.logger.warning(f"TC375 device not found for connection: {connection_id}")
            return TC375Response(
                command_type=TC375CommandType.QUERY,
                device_id="unknown",
                success=False,
                data={},
                error="Device not registered"
            )
        
        # Update heartbeat
        await self.update_heartbeat(device.id)
        
        # Process data (implement specific logic as needed)
        protocol_version = payload.get("protocol", device.protocol.value)
        data_size = len(str(payload.get("data", "")))
        
        self.logger.info(
            f"TC375 data processed",
            extra={
                "device_id": device.id,
                "protocol": protocol_version,
                "data_size": data_size
            }
        )
        
        response = TC375Response(
            command_type=TC375CommandType.QUERY,
            device_id=device.id,
            success=True,
            data={
                "status": "received",
                "protocol": protocol_version,
                "data_size": data_size,
                "processed_at": datetime.utcnow().isoformat()
            }
        )
        
        return response
    
    async def send_command(
        self,
        device_id: str,
        command: TC375Command
    ) -> bool:
        """
        Send command to TC375 device.
        
        Args:
            device_id: Target device ID
            command: Command to send
        
        Returns:
            True if sent successfully
        """
        device = self.repository.get(device_id)
        if not device:
            self.logger.warning(f"Device not found: {device_id}")
            return False
        
        # Mark device as busy
        device.status = TC375Status.BUSY
        self.repository.update(device_id, device)
        
        # Send command via message service
        message = Message(
            type=MessageType.TC375_COMMAND,
            payload=command.to_dict()
        )
        
        success = await self.message_service.send_message(device.connection_id, message)
        
        # Reset status
        device.status = TC375Status.ONLINE
        self.repository.update(device_id, device)
        
        if success:
            self.logger.info(
                f"Command sent to TC375 device",
                extra={
                    "device_id": device_id,
                    "command_type": command.command_type.value
                }
            )
        
        return success
    
    def get_device(self, device_id: str) -> Optional[TC375Device]:
        """Get device by ID."""
        return self.repository.get(device_id)
    
    def get_online_devices(self) -> List[TC375Device]:
        """Get all online devices."""
        return self.repository.get_online_devices()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get device statistics."""
        return self.repository.get_device_statistics()
    
    async def check_stale_devices(self) -> int:
        """Check and mark stale devices as offline."""
        timeout = self.config.tc375.client_timeout
        stale = self.repository.get_stale_devices(timeout)
        
        count = 0
        for device in stale:
            self.repository.mark_offline(device.id)
            count += 1
            self.logger.warning(
                f"Device marked as offline due to stale heartbeat",
                extra={"device_id": device.id}
            )
        
        return count

