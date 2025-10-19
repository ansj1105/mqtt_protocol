"""
Admin dashboard controller.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Any
from datetime import datetime

from services.connection_service import ConnectionService
from services.tc375_service import TC375Service
from services.pqc_service import PQCService
from utils.logger import get_logger


logger = get_logger(__name__)
templates = Jinja2Templates(directory="templates")


def create_admin_router(
    connection_service: ConnectionService,
    tc375_service: TC375Service,
    pqc_service: PQCService
) -> APIRouter:
    """Create admin dashboard router."""
    
    router = APIRouter()
    
    @router.get("/", response_class=HTMLResponse)
    async def admin_dashboard(request: Request):
        """Admin dashboard main page."""
        # Get statistics
        conn_stats = connection_service.get_statistics()
        tc375_stats = tc375_service.get_statistics()
        pqc_stats = pqc_service.get_statistics()
        
        # Get active connections
        active_connections = connection_service.get_active_connections()
        
        # Get TC375 devices
        tc375_devices = tc375_service.get_online_devices()
        
        context = {
            "request": request,
            "server_time": datetime.utcnow().isoformat(),
            "stats": {
                "connections": conn_stats,
                "tc375": tc375_stats,
                "pqc": pqc_stats
            },
            "active_connections": [conn.to_dict() for conn in active_connections[:10]],
            "tc375_devices": [dev.to_dict() for dev in tc375_devices[:10]],
            "total_connections": len(active_connections),
            "total_devices": len(tc375_devices)
        }
        
        return templates.TemplateResponse("dashboard.html", context)
    
    @router.get("/connections", response_class=HTMLResponse)
    async def connections_page(request: Request):
        """Connections management page."""
        connections = connection_service.get_active_connections()
        
        context = {
            "request": request,
            "connections": [conn.to_dict() for conn in connections],
            "total": len(connections)
        }
        
        return templates.TemplateResponse("connections.html", context)
    
    @router.get("/devices", response_class=HTMLResponse)
    async def devices_page(request: Request):
        """TC375 devices management page."""
        all_devices = tc375_service.repository.get_all()
        
        context = {
            "request": request,
            "devices": [dev.to_dict() for dev in all_devices],
            "stats": tc375_service.get_statistics()
        }
        
        return templates.TemplateResponse("devices.html", context)
    
    @router.get("/logs", response_class=HTMLResponse)
    async def logs_page(request: Request):
        """Logs viewer page."""
        context = {
            "request": request,
        }
        return templates.TemplateResponse("logs.html", context)
    
    @router.get("/api/dashboard-stats")
    async def get_dashboard_stats() -> Dict[str, Any]:
        """Get real-time dashboard statistics (for AJAX updates)."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "connections": connection_service.get_statistics(),
            "tc375": tc375_service.get_statistics(),
            "pqc": pqc_service.get_statistics(),
            "active_connections_count": len(connection_service.get_active_connections()),
            "online_devices_count": len(tc375_service.get_online_devices())
        }
    
    return router

