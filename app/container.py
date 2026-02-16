"""
Service Container - DI Container dengan Singleton pattern
"""
from typing import Callable, Union, Type, Dict, Any
from threading import Lock


class ServiceContainer:
    _factories: Dict[str, Callable] = {}
    _instances: Dict[str, Any] = {}
    _lock = Lock()
    _booted = False

    @classmethod
    def register(cls, key: str, factory: Union[Callable, Type]):
        """Register service"""
        if isinstance(factory, type):
            cls._factories[key] = lambda: factory()
        else:
            cls._factories[key] = factory

    @classmethod
    def boot(cls):
        """Boot container"""
        cls._booted = True

    @classmethod
    def get(cls, key: str):
        """Get service instance (singleton)"""
        if not cls._booted:
            raise RuntimeError("Container not booted")
        
        if key not in cls._instances:
            with cls._lock:
                if key not in cls._instances:
                    cls._instances[key] = cls._factories[key]()
        
        return cls._instances[key]
    
    @classmethod
    def reset(cls):
        """Reset (untuk testing)"""
        cls._instances.clear()
        cls._booted = False