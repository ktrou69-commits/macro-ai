"""
Результаты выполнения модулей
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class ExecutionError:
    """Ошибка выполнения"""
    type: str
    message: str
    context: Dict[str, Any]
    timestamp: datetime
    recoverable: bool = True


@dataclass
class ModuleResult:
    """Результат выполнения модуля"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    logs: List[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.logs is None:
            self.logs = []
        if self.metadata is None:
            self.metadata = {}
    
    def add_log(self, message: str):
        """Добавить лог сообщение"""
        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация результата"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "logs": self.logs,
            "execution_time": self.execution_time,
            "metadata": self.metadata
        }


@dataclass
class ExecutionResult:
    """Результат выполнения исполнителя"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    logs: List[str] = None
    
    def __post_init__(self):
        if self.logs is None:
            self.logs = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация результата"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "logs": self.logs
        }
