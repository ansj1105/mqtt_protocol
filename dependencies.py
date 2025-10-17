"""
Dependency injection container.
"""

from typing import Optional

from config import Config, init_config
from repositories.connection import ConnectionRepository
from repositories.tc375 import TC375DeviceRepository
from repositories.pqc import PQCSessionRepository
from services.connection_service import ConnectionService
from services.message_service import MessageService
from services.tc375_service import TC375Service
from services.pqc_service import PQCService
from controllers.websocket_controller import WebSocketController
from utils.logger import setup_logger, get_logger


class DependencyContainer:
    """
    Dependency injection container for managing service instances.
    Implements singleton pattern for service lifecycle management.
    """
    
    _instance: Optional['DependencyContainer'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._config: Optional[Config] = None
        self._logger = None
        
        # Repositories
        self._connection_repository: Optional[ConnectionRepository] = None
        self._tc375_repository: Optional[TC375DeviceRepository] = None
        self._pqc_repository: Optional[PQCSessionRepository] = None
        
        # Services
        self._connection_service: Optional[ConnectionService] = None
        self._message_service: Optional[MessageService] = None
        self._tc375_service: Optional[TC375Service] = None
        self._pqc_service: Optional[PQCService] = None
        
        # Controllers
        self._websocket_controller: Optional[WebSocketController] = None
    
    def initialize(self, config_path: str = "config.json"):
        """
        Initialize all dependencies.
        
        Args:
            config_path: Path to configuration file
        """
        # Initialize configuration
        self._config = init_config(config_path)
        
        # Setup logging
        self._logger = setup_logger(
            name="websocket_server",
            level=self._config.logging.level,
            log_format=self._config.logging.format,
            log_file=self._config.logging.file,
            console=self._config.logging.console
        )
        
        self._logger.info("Dependency container initialized")
        self._logger.info(f"Configuration loaded from: {config_path}")
        self._logger.info(f"TLS enabled: {self._config.tls.enabled}")
        self._logger.info(f"PQC enabled: {self._config.pqc.enabled}")
    
    @property
    def config(self) -> Config:
        """Get configuration."""
        if self._config is None:
            self.initialize()
        return self._config
    
    @property
    def logger(self):
        """Get logger."""
        if self._logger is None:
            self.initialize()
        return self._logger
    
    # Repository properties
    
    @property
    def connection_repository(self) -> ConnectionRepository:
        """Get connection repository."""
        if self._connection_repository is None:
            self._connection_repository = ConnectionRepository()
            self.logger.debug("Connection repository created")
        return self._connection_repository
    
    @property
    def tc375_repository(self) -> TC375DeviceRepository:
        """Get TC375 device repository."""
        if self._tc375_repository is None:
            self._tc375_repository = TC375DeviceRepository()
            self.logger.debug("TC375 repository created")
        return self._tc375_repository
    
    @property
    def pqc_repository(self) -> PQCSessionRepository:
        """Get PQC session repository."""
        if self._pqc_repository is None:
            self._pqc_repository = PQCSessionRepository()
            self.logger.debug("PQC repository created")
        return self._pqc_repository
    
    # Service properties
    
    @property
    def connection_service(self) -> ConnectionService:
        """Get connection service."""
        if self._connection_service is None:
            self._connection_service = ConnectionService(
                self.connection_repository,
                self.config
            )
            self.logger.debug("Connection service created")
        return self._connection_service
    
    @property
    def message_service(self) -> MessageService:
        """Get message service."""
        if self._message_service is None:
            self._message_service = MessageService(
                self.connection_service,
                self.config
            )
            self.logger.debug("Message service created")
        return self._message_service
    
    @property
    def tc375_service(self) -> TC375Service:
        """Get TC375 service."""
        if self._tc375_service is None:
            self._tc375_service = TC375Service(
                self.tc375_repository,
                self.message_service,
                self.config
            )
            self.logger.debug("TC375 service created")
        return self._tc375_service
    
    @property
    def pqc_service(self) -> PQCService:
        """Get PQC service."""
        if self._pqc_service is None:
            self._pqc_service = PQCService(
                self.pqc_repository,
                self.config
            )
            self.logger.debug("PQC service created")
        return self._pqc_service
    
    # Controller properties
    
    @property
    def websocket_controller(self) -> WebSocketController:
        """Get WebSocket controller."""
        if self._websocket_controller is None:
            self._websocket_controller = WebSocketController(
                self.connection_service,
                self.message_service,
                self.tc375_service,
                self.pqc_service
            )
            self.logger.debug("WebSocket controller created")
        return self._websocket_controller
    
    def reset(self):
        """Reset all dependencies (useful for testing)."""
        self._connection_repository = None
        self._tc375_repository = None
        self._pqc_repository = None
        self._connection_service = None
        self._message_service = None
        self._tc375_service = None
        self._pqc_service = None
        self._websocket_controller = None
        self.logger.info("Dependency container reset")


# Global container instance
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get the global dependency container."""
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


def init_container(config_path: str = "config.json") -> DependencyContainer:
    """
    Initialize the global dependency container.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        Initialized container
    """
    container = get_container()
    container.initialize(config_path)
    return container

