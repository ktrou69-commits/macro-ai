"""
Базовый исполнитель для модулей
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from .module_result import ExecutionResult
from .module_config import ExecutorConfig


class Executor(ABC):
    """Базовый класс исполнителя"""
    
    def __init__(self, config: ExecutorConfig):
        self.config = config
    
    @abstractmethod
    def execute(self, data: Any) -> ExecutionResult:
        """
        Выполнить данные
        
        Args:
            data: Данные для выполнения
            
        Returns:
            Результат выполнения
        """
        pass
    
    def validate_data(self, data: Any) -> bool:
        """
        Валидация входных данных
        
        Args:
            data: Данные для валидации
            
        Returns:
            True если данные валидны
        """
        return data is not None


class NoOpExecutor(Executor):
    """Исполнитель-заглушка (ничего не делает)"""
    
    def execute(self, data: Any) -> ExecutionResult:
        """Возвращает данные как есть"""
        return ExecutionResult(
            success=True,
            data=data,
            logs=["NoOpExecutor: данные переданы без изменений"]
        )


class DSLExecutor(Executor):
    """Исполнитель DSL кода"""
    
    def __init__(self, config: ExecutorConfig):
        super().__init__(config)
        self._initialize_dsl_components()
    
    def _initialize_dsl_components(self):
        """Инициализация компонентов DSL"""
        try:
            # Импортируем существующие компоненты
            import sys
            from pathlib import Path
            
            # Добавляем путь к src
            project_root = Path(__file__).parent.parent.parent.parent
            sys.path.insert(0, str(project_root))
            
            from src.core.atlas_dsl_parser import AtlasDSLParser
            from src.core.macro_sequence import MacroRunner
            
            self.dsl_parser = AtlasDSLParser()
            self.macro_sequence_class = MacroRunner
            
        except ImportError as e:
            print(f"⚠️ Не удалось импортировать DSL компоненты: {e}")
            self.dsl_parser = None
            self.macro_sequence_class = None
    
    def execute(self, dsl_code: str) -> ExecutionResult:
        """
        Выполнение DSL кода
        
        Args:
            dsl_code: DSL код для выполнения
            
        Returns:
            Результат выполнения
        """
        if not self.dsl_parser:
            return ExecutionResult(
                success=False,
                error="DSL компоненты не доступны"
            )
        
        try:
            # Парсинг DSL в YAML
            yaml_data = self.dsl_parser.parse(dsl_code)
            
            # Выполнение через MacroSequence
            sequence = self.macro_sequence_class(yaml_data)
            result = sequence.execute()
            
            return ExecutionResult(
                success=True,
                data=result,
                logs=[f"DSL выполнен успешно: {len(yaml_data.get('steps', []))} шагов"]
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Ошибка выполнения DSL: {str(e)}",
                logs=[f"DSL код: {dsl_code[:100]}..."]
            )


class CustomExecutor(Executor):
    """Кастомный исполнитель для специфичных задач"""
    
    def __init__(self, config: ExecutorConfig, execute_func=None):
        super().__init__(config)
        self.execute_func = execute_func
    
    def execute(self, data: Any) -> ExecutionResult:
        """Выполнение через кастомную функцию"""
        if not self.execute_func:
            return ExecutionResult(
                success=False,
                error="Кастомная функция выполнения не задана"
            )
        
        try:
            result = self.execute_func(data)
            return ExecutionResult(
                success=True,
                data=result,
                logs=["CustomExecutor: выполнено через кастомную функцию"]
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=f"Ошибка кастомного исполнителя: {str(e)}"
            )


def create_executor(config: ExecutorConfig, **kwargs) -> Executor:
    """
    Фабрика исполнителей
    
    Args:
        config: Конфигурация исполнителя
        **kwargs: Дополнительные параметры
        
    Returns:
        Экземпляр исполнителя
    """
    if config.type == "none":
        return NoOpExecutor(config)
    elif config.type == "dsl_executor":
        return DSLExecutor(config)
    elif config.type == "custom":
        return CustomExecutor(config, kwargs.get('execute_func'))
    else:
        raise ValueError(f"Неизвестный тип исполнителя: {config.type}")
