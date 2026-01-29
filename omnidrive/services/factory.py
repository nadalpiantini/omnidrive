"""
Service factory for creating cloud service instances.
Eliminates repetitive service instantiation logic in CLI.
"""
from typing import Optional, Dict, Type
from .base import CloudService, ServiceError
from .google_drive import GoogleDriveService
from .folderfort import FolderfortService


class ServiceFactory:
    """Factory for creating cloud service instances."""

    # Registry of available services
    _services: Dict[str, Type[CloudService]] = {
        'google': GoogleDriveService,
        'folderfort': FolderfortService,
        # 'onedrive': OneDriveService,  # TODO: Phase 2+
        # 'dropbox': DropboxService,     # TODO: Phase 2+
    }

    # Auth modules mapping
    _auth_modules = None

    @classmethod
    def register_service(cls, name: str, service_class: Type[CloudService]):
        """Register a new service."""
        cls._services[name] = service_class

    @classmethod
    def get_available_services(cls) -> list[str]:
        """Get list of available service names."""
        return list(cls._services.keys())

    @classmethod
    def is_service_available(cls, service_name: str) -> bool:
        """Check if a service is available."""
        return service_name in cls._services

    @classmethod
    def _set_auth_modules(cls, auth_modules):
        """Set auth modules (called from CLI)."""
        cls._auth_modules = auth_modules

    @classmethod
    def create_service(
        cls,
        service_name: str,
        auto_authenticate: bool = True
    ) -> CloudService:
        """
        Create a cloud service instance.

        Args:
            service_name: Name of the service (google, folderfort, etc.)
            auto_authenticate: If True, authenticate if not already authenticated

        Returns:
            CloudService instance

        Raises:
            ServiceError: If service not available or authentication fails
        """
        if not cls.is_service_available(service_name):
            available = ', '.join(cls.get_available_services())
            raise ServiceError(
                f"Service '{service_name}' not available. "
                f"Available: {available}",
                service_name=service_name
            )

        # Get service class
        service_class = cls._services[service_name]

        # Handle authentication
        access_token = None
        if auto_authenticate and cls._auth_modules:
            auth_module = cls._auth_modules.get(service_name)
            if auth_module:
                # Check if already authenticated
                is_auth_fn = getattr(auth_module, f'is_{service_name}_authenticated', None)
                if is_auth_fn and not is_auth_fn():
                    # Not authenticated, need to authenticate
                    get_token_fn = getattr(auth_module, f'get_{service_name}_token', None)
                    if get_token_fn:
                        access_token = get_token_fn()
                    else:
                        # Try authentication
                        auth_fn = getattr(auth_module, f'authenticate_{service_name}', None)
                        if auth_fn:
                            auth_fn()
                            # Get token after authentication
                            if get_token_fn:
                                access_token = get_token_fn()
                elif get_token_fn:
                    # Already authenticated, get token
                    access_token = get_token_fn()

        # Create service instance
        service = service_class(access_token=access_token)

        return service

    @classmethod
    def create_service_with_token(
        cls,
        service_name: str,
        access_token: str
    ) -> CloudService:
        """
        Create a cloud service instance with explicit token.

        Args:
            service_name: Name of the service
            access_token: Access token for the service

        Returns:
            CloudService instance
        """
        if not cls.is_service_available(service_name):
            available = ', '.join(cls.get_available_services())
            raise ServiceError(
                f"Service '{service_name}' not available. "
                f"Available: {available}",
                service_name=service_name
            )

        service_class = cls._services[service_name]
        return service_class(access_token=access_token)
