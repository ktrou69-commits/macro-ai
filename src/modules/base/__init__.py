"""
Базовые классы для модульной AI системы
"""

from .ai_module import AIModule
from .module_config import ModuleConfig
from .ai_agent import AIAgent
from .executor import Executor
from .module_result import ModuleResult

__all__ = [
    "AIModule",
    "ModuleConfig",
    "AIAgent", 
    "Executor",
    "ModuleResult"
]
