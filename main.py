"""
Main application entry point.
WebSocket Server with TC375 Litekit support, TLS, and PQC hybrid cryptography.
"""

import asyncio
import ssl
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from dependencies import init_container, get_container
from controllers.api_controller import create_api_router
from controllers.admin_controller import create_admin_router
from fastapi.staticfiles import StaticFiles
from utils.logger import get_logger


# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger = get_logger(__name__)
    logger.info("=" * 80)
    logger.info("WebSocket Server starting...")
    logger.info("=" * 80)
    
    container = get_container()
    config = container.config
    
    logger.info(f"Server configuration:")
    logger.info(f"  - WebSocket port: {config.server.websocket_port}")
    logger.info(f"  - API port: {config.server.api_port}")
    logger.info(f"  - TLS enabled: {config.tls.enabled}")
    logger.info(f"  - PQC enabled: {config.pqc.enabled}")
    logger.info(f"  - Max connections: {config.security.max_connections}")
    
    # Start background tasks
    background_tasks = []
    
    # Cleanup task
    async def periodic_cleanup():
        while True:
            await asyncio.sleep(60)  # Every minute
            try:
                # Cleanup inactive connections
                inactive_count = await container.connection_service.cleanup_inactive()
                if inactive_count > 0:
                    logger.info(f"Cleaned up {inactive_count} inactive connections")
                
                # Cleanup expired PQC sessions
                expired_count = await container.pqc_service.cleanup_expired_sessions()
                if expired_count > 0:
                    logger.info(f"Cleaned up {expired_count} expired PQC sessions")
                
                # Check stale TC375 devices
                stale_count = await container.tc375_service.check_stale_devices()
                if stale_count > 0:
                    logger.info(f"Marked {stale_count} TC375 devices as offline")
            
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
    
    cleanup_task = asyncio.create_task(periodic_cleanup())
    background_tasks.append(cleanup_task)
    
    logger.info("WebSocket Server started successfully!")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("=" * 80)
    logger.info("WebSocket Server shutting down...")
    
    # Cancel background tasks
    for task in background_tasks:
        task.cancel()
    
    # Wait for tasks to complete
    await asyncio.gather(*background_tasks, return_exceptions=True)
    
    logger.info("WebSocket Server stopped")
    logger.info("=" * 80)


# Initialize application
def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    # Initialize dependency container
    container = init_container()
    config = container.config
    
    # Create FastAPI app
    app = FastAPI(
        title="TC375 Litekit WebSocket Server",
        description="WebSocket server with TLS and PQC hybrid cryptography support",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add API routes
    api_router = create_api_router(
        container.connection_service,
        container.message_service,
        container.tc375_service,
        container.pqc_service
    )
    app.include_router(api_router, prefix="/api", tags=["API"])
    
    # Add Admin routes
    admin_router = create_admin_router(
        container.connection_service,
        container.tc375_service,
        container.pqc_service
    )
    app.include_router(admin_router, prefix="/admin", tags=["Admin"])
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # WebSocket endpoint
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket connection endpoint."""
        await container.websocket_controller.handle_connection(websocket)
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "TC375 Litekit WebSocket Server",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "websocket": "/ws",
                "api": "/api",
                "docs": "/docs",
                "openapi": "/openapi.json"
            }
        }
    
    return app


def create_ssl_context(config) -> ssl.SSLContext:
    """
    Create SSL context for TLS support.
    
    Args:
        config: Server configuration
    
    Returns:
        Configured SSL context
    """
    logger = get_logger(__name__)
    
    if not config.tls.enabled:
        return None
    
    cert_path = Path(config.tls.cert_path)
    key_path = Path(config.tls.key_path)
    
    if not cert_path.exists() or not key_path.exists():
        logger.warning(f"TLS certificates not found!")
        logger.warning(f"  - Cert: {cert_path}")
        logger.warning(f"  - Key: {key_path}")
        logger.warning("TLS will be disabled. Run ./scripts/generate_certs.sh to generate certificates.")
        return None
    
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(
        certfile=str(cert_path),
        keyfile=str(key_path)
    )
    
    logger.info(f"TLS enabled with certificate: {cert_path}")
    return ssl_context


def main():
    """Main entry point."""
    # Create app
    app = create_app()
    container = get_container()
    config = container.config
    logger = get_logger(__name__)
    
    # Create SSL context
    ssl_context = create_ssl_context(config)
    
    # Uvicorn configuration
    uvicorn_config = {
        "app": app,
        "host": config.server.host,
        "port": config.server.websocket_port,
        "log_level": config.logging.level.lower(),
        "access_log": True,
    }
    
    if ssl_context:
        uvicorn_config["ssl_keyfile"] = config.tls.key_path
        uvicorn_config["ssl_certfile"] = config.tls.cert_path
        protocol = "wss" if ssl_context else "ws"
    else:
        protocol = "ws"
    
    logger.info(f"Starting server at {protocol}://{config.server.host}:{config.server.websocket_port}")
    logger.info(f"API available at http://{config.server.host}:{config.server.websocket_port}/api")
    logger.info(f"API docs at http://{config.server.host}:{config.server.websocket_port}/docs")
    
    # Run server
    uvicorn.run(**uvicorn_config)


if __name__ == "__main__":
    main()

