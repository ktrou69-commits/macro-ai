"""
Модульная AI система для Macro AI

Этот пакет содержит модульную архитектуру для создания
специализированных AI агентов для автоматизации.
"""

__version__ = "1.0.0"
__author__ = "Macro AI Team"

from .base.ai_module import AIModule
from .base.module_config import ModuleConfig
from .coordinator.ai_coordinator import AICoordinator

__all__ = [
    "AIModule",
    "ModuleConfig", 
    "AICoordinator"
]
