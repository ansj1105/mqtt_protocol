"""
REST API controller using FastAPI.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from schemas.api import (
    BroadcastRequestSchema,
    SendMessageRequestSchema,
    DisconnectRequestSchema,
    StatusResponseSchema,
    HealthResponseSchema,
    SuccessResponseSchema,
    ErrorResponseSchema
)
from schemas.connection import ConnectionListSchema, ConnectionSchema
from schemas.tc375 import TC375StatusSchema, TC375CommandSchema, TC375ResponseSchema
from schemas.pqc import PQCInfoSchema
from models.message import Message, MessageType
from models.tc375 import TC375Command, TC375CommandType
from services.connection_service import ConnectionService
from services.message_service import MessageService
from services.tc375_service import TC375Service
from services.pqc_service import PQCService
from utils.logger import get_logger


logger = get_logger(__name__)


def create_api_router(
    connection_service: ConnectionService,
    message_service: MessageService,
    tc375_service: TC375Service,
    pqc_service: PQCService
) -> APIRouter:
    """
    Create API router with all endpoints.
    
    Args:
        connection_service: Connection service instance
        message_service: Message service instance
        tc375_service: TC375 service instance
        pqc_service: PQC service instance
    
    Returns:
        Configured APIRouter
    """
    router = APIRouter()
    
    @router.get("/", response_model=Dict[str, Any])
    async def root():
        """API documentation."""
        return {
            "name": "WebSocket Server API",
            "version": "1.0.0",
            "description": "REST API for TC375 Litekit WebSocket Server",
            "architecture": "Layered Architecture (Controller -> Service -> Repository)",
            "endpoints": {
                "GET /": "API documentation",
                "GET /health": "Health check",
                "GET /status": "Server status",
                "GET /connections": "List active connections",
                "POST /broadcast": "Broadcast message to all clients",
                "POST /send": "Send message to specific client",
                "POST /disconnect": "Disconnect a client",
                "POST /tc375/command": "Send command to TC375 device",
                "GET /tc375/status": "Get TC375 device status",
                "GET /pqc/info": "Get PQC configuration info"
            }
        }
    
    @router.get("/health", response_model=HealthResponseSchema)
    async def health_check():
        """Health check endpoint."""
        return HealthResponseSchema(status="healthy")
    
    @router.get("/status", response_model=StatusResponseSchema)
    async def get_status():
        """Get server status."""
        stats = connection_service.get_statistics()
        
        return StatusResponseSchema(
            status="running",
            active_connections=stats["active_connections"],
            max_connections=connection_service.config.security.max_connections,
            uptime="N/A",  # Implement uptime tracking if needed
            tls_enabled=connection_service.config.tls.enabled,
            pqc_enabled=connection_service.config.pqc.enabled
        )
    
    @router.get("/connections", response_model=ConnectionListSchema)
    async def get_connections():
        """Get all active connections."""
        connections = connection_service.get_active_connections()
        
        return ConnectionListSchema(
            count=len(connections),
            connections=[
                ConnectionSchema(**conn.to_dict())
                for conn in connections
            ]
        )
    
    @router.post("/broadcast", response_model=SuccessResponseSchema)
    async def broadcast_message(request: BroadcastRequestSchema):
        """Broadcast message to all clients."""
        try:
            message = Message(
                type=MessageType.BROADCAST,
                payload=request.message
            )
            
            exclude = set(request.exclude) if request.exclude else None
            recipients = await message_service.broadcast_message(message, exclude)
            
            return SuccessResponseSchema(
                success=True,
                message=f"Message broadcast to {recipients} clients",
                data={"recipients": recipients}
            )
        
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/send", response_model=SuccessResponseSchema)
    async def send_message(request: SendMessageRequestSchema):
        """Send message to specific client."""
        try:
            message = Message(
                type=MessageType.MESSAGE,
                payload=request.message
            )
            
            success = await message_service.send_message(request.client_id, message)
            
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail=f"Client not found: {request.client_id}"
                )
            
            return SuccessResponseSchema(
                success=True,
                message=f"Message sent to {request.client_id}"
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/disconnect", response_model=SuccessResponseSchema)
    async def disconnect_client(request: DisconnectRequestSchema):
        """Disconnect a client."""
        try:
            # Get websocket
            websocket = connection_service.get_websocket(request.client_id)
            if not websocket:
                raise HTTPException(
                    status_code=404,
                    detail=f"Client not found: {request.client_id}"
                )
            
            # Close websocket
            reason = request.reason or "Disconnected by server"
            await websocket.close(code=1000, reason=reason)
            
            # Disconnect from service
            await connection_service.disconnect(request.client_id)
            
            return SuccessResponseSchema(
                success=True,
                message=f"Client {request.client_id} disconnected"
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error disconnecting client: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/tc375/command", response_model=SuccessResponseSchema)
    async def send_tc375_command(request: TC375CommandSchema):
        """Send command to TC375 device."""
        try:
            command = TC375Command(
                command_type=TC375CommandType(request.command_type),
                device_id=request.device_id,
                parameters=request.parameters,
                timeout=request.timeout,
                retries=request.retries
            )
            
            success = await tc375_service.send_command(request.device_id, command)
            
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail=f"Device not found: {request.device_id}"
                )
            
            return SuccessResponseSchema(
                success=True,
                message=f"Command sent to device {request.device_id}",
                data={"command_type": request.command_type}
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error sending TC375 command: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/tc375/status", response_model=Dict[str, Any])
    async def get_tc375_status():
        """Get TC375 device status."""
        try:
            stats = tc375_service.get_statistics()
            devices = tc375_service.get_online_devices()
            
            return {
                "statistics": stats,
                "online_devices": len(devices),
                "devices": [device.to_dict() for device in devices]
            }
        
        except Exception as e:
            logger.error(f"Error getting TC375 status: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/pqc/info", response_model=PQCInfoSchema)
    async def get_pqc_info():
        """Get PQC configuration information."""
        try:
            info = pqc_service.get_info()
            return PQCInfoSchema(**info)
        
        except Exception as e:
            logger.error(f"Error getting PQC info: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/statistics", response_model=Dict[str, Any])
    async def get_statistics():
        """Get comprehensive server statistics."""
        try:
            return {
                "connections": connection_service.get_statistics(),
                "pqc": pqc_service.get_statistics(),
                "tc375": tc375_service.get_statistics()
            }
        
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router

