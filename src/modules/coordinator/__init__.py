"""
Координатор модульной AI системы
"""

from .ai_coordinator import AICoordinator
from .intent_analyzer import IntentAnalyzer
from .module_selector import ModuleSelector

__all__ = [
    "AICoordinator",
    "IntentAnalyzer", 
    "ModuleSelector"
]
