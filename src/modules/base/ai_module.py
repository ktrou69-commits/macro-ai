"""
Базовый класс для всех AI модулей
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from .module_config import ModuleConfig
from .ai_agent import AIAgent
from .executor import create_executor
from .module_result import ModuleResult, ExecutionResult


class AIModule(ABC):
    """Базовый класс для всех AI модулей"""
    
    def __init__(self, config: ModuleConfig):
        self.config = config
        self.name = config.name
        self.description = config.description
        
        # Инициализация компонентов
        self.ai_agent = AIAgent(config.ai_config)
        self.executor = create_executor(config.executor_config)
        
        # Логирование
        self.logger = self._setup_logger()
        
        # Кэш ресурсов
        self._resources_cache = {}
        self._prompt_cache = {}
        
        self.logger.info(f"Модуль {self.name} инициализирован")
    
    def _setup_logger(self) -> logging.Logger:
        """Настройка логгера для модуля"""
        logger = logging.getLogger(f"module.{self.name}")
        logger.setLevel(logging.INFO)
        
        # Создаем handler если его нет
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[{self.name}] %(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def execute(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ModuleResult:
        """
        Главный метод выполнения модуля
        
        Args:
            user_input: Ввод пользователя
            context: Контекст выполнения
            
        Returns:
            Результат выполнения модуля
        """
        start_time = time.time()
        
        if context is None:
            context = {}
        
        self.logger.info(f"Начало выполнения: {user_input[:50]}...")
        
        try:
            # 1. Формирование промпта с контекстом
            full_prompt = self.build_prompt(user_input, context)
            
            # 2. AI генерация результата
            ai_result = self.ai_agent.generate(full_prompt, context)
            self.logger.info("AI генерация завершена")
            
            # 3. Парсинг AI результата
            parsed_result = self.parse_ai_result(ai_result)
            self.logger.info("Парсинг AI результата завершен")
            
            # 4. Выполнение через executor (если нужно)
            execution_result = None
            if self.config.executor_config.type != "none":
                execution_result = self.executor.execute(parsed_result)
                self.logger.info("Выполнение через executor завершено")
            
            # 5. Формирование результата
            execution_time = time.time() - start_time
            
            result = ModuleResult(
                success=True,
                data=execution_result.data if execution_result else parsed_result,
                execution_time=execution_time,
                metadata={
                    "ai_result": ai_result,
                    "parsed_result": parsed_result,
                    "execution_result": execution_result.to_dict() if execution_result else None
                }
            )
            
            result.add_log(f"Модуль {self.name} выполнен успешно за {execution_time:.2f}с")
            
            self.logger.info(f"Выполнение завершено успешно за {execution_time:.2f}с")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Ошибка в модуле {self.name}: {str(e)}"
            
            self.logger.error(error_msg)
            
            return ModuleResult(
                success=False,
                error=error_msg,
                execution_time=execution_time,
                metadata={"user_input": user_input, "context": context}
            )
    
    def build_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        """
        Построение промпта для AI
        
        Args:
            user_input: Ввод пользователя
            context: Контекст
            
        Returns:
            Полный промпт для AI
        """
        # Загружаем базовый промпт
        base_prompt = self.load_prompt("base_prompt.txt")
        
        # Загружаем ресурсы
        resources = self.get_context_resources()
        
        # Формируем полный промпт
        full_prompt = base_prompt.format(
            user_input=user_input,
            context=self._format_context(context),
            available_resources=self._format_resources(resources)
        )
        
        return full_prompt
    
    def load_prompt(self, prompt_name: str) -> str:
        """
        Загрузка промпта из файла
        
        Args:
            prompt_name: Имя файла промпта
            
        Returns:
            Содержимое промпта
        """
        if prompt_name in self._prompt_cache:
            return self._prompt_cache[prompt_name]
        
        # Путь к промпту
        prompt_path = Path(__file__).parent.parent / self.config.prompt_path / prompt_name
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_content = f.read()
            
            self._prompt_cache[prompt_name] = prompt_content
            return prompt_content
            
        except FileNotFoundError:
            # Fallback промпт
            fallback_prompt = f"""
            Ты - AI модуль "{self.name}".
            Твоя задача: {self.description}
            
            ЗАПРОС ПОЛЬЗОВАТЕЛЯ: {{user_input}}
            КОНТЕКСТ: {{context}}
            ДОСТУПНЫЕ РЕСУРСЫ: {{available_resources}}
            
            Выполни запрос пользователя согласно своему назначению.
            """
            
            self.logger.warning(f"Промпт {prompt_name} не найден, используется fallback")
            return fallback_prompt
    
    @abstractmethod
    def parse_ai_result(self, ai_result: str) -> Any:
        """
        Парсинг результата AI в нужный формат
        
        Args:
            ai_result: Результат от AI
            
        Returns:
            Распарсенный результат
        """
        pass
    
    def get_context_resources(self) -> Dict[str, Any]:
        """
        Получение ресурсов для контекста
        
        Returns:
            Словарь с ресурсами
        """
        resources = {}
        
        # Загружаем ресурсы согласно конфигурации
        if self.config.resources_config.templates:
            resources["templates"] = self.load_templates_structure()
        
        if self.config.resources_config.variables:
            resources["variables"] = self.load_dsl_variables()
        
        if self.config.resources_config.dom_selectors:
            resources["dom_selectors"] = self.load_dom_selectors()
        
        if self.config.resources_config.system_commands:
            resources["system_commands"] = self.load_system_commands()
        
        if self.config.resources_config.custom_data:
            resources["custom_data"] = self.load_custom_data()
        
        return resources
    
    def load_templates_structure(self) -> Dict[str, Any]:
        """Загрузка структуры шаблонов"""
        if "templates" in self._resources_cache:
            return self._resources_cache["templates"]
        
        # TODO: Интеграция с существующей системой шаблонов
        templates = {"placeholder": "templates structure"}
        self._resources_cache["templates"] = templates
        return templates
    
    def load_dsl_variables(self) -> Dict[str, Any]:
        """Загрузка DSL переменных"""
        if "variables" in self._resources_cache:
            return self._resources_cache["variables"]
        
        # TODO: Интеграция с существующей системой переменных
        variables = {"placeholder": "dsl variables"}
        self._resources_cache["variables"] = variables
        return variables
    
    def load_dom_selectors(self) -> Dict[str, Any]:
        """Загрузка DOM селекторов"""
        if "dom_selectors" in self._resources_cache:
            return self._resources_cache["dom_selectors"]
        
        # TODO: Интеграция с существующей системой DOM селекторов
        selectors = {"placeholder": "dom selectors"}
        self._resources_cache["dom_selectors"] = selectors
        return selectors
    
    def load_system_commands(self) -> Dict[str, Any]:
        """Загрузка системных команд"""
        if "system_commands" in self._resources_cache:
            return self._resources_cache["system_commands"]
        
        # TODO: Интеграция с существующими системными командами
        commands = {"placeholder": "system commands"}
        self._resources_cache["system_commands"] = commands
        return commands
    
    def load_custom_data(self) -> Dict[str, Any]:
        """Загрузка кастомных данных модуля"""
        return {}
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Форматирование контекста для промпта"""
        if not context:
            return "Контекст отсутствует"
        
        formatted = []
        for key, value in context.items():
            if value:
                formatted.append(f"- {key}: {value}")
        
        return "\n".join(formatted) if formatted else "Контекст отсутствует"
    
    def _format_resources(self, resources: Dict[str, Any]) -> str:
        """Форматирование ресурсов для промпта"""
        if not resources:
            return "Ресурсы не загружены"
        
        formatted = []
        for resource_type, data in resources.items():
            if data:
                formatted.append(f"- {resource_type}: доступно")
        
        return "\n".join(formatted) if formatted else "Ресурсы не загружены"
    
    def validate_input(self, user_input: str) -> bool:
        """
        Валидация пользовательского ввода
        
        Args:
            user_input: Ввод пользователя
            
        Returns:
            True если ввод валиден
        """
        return bool(user_input and user_input.strip())
    
    def get_module_info(self) -> Dict[str, Any]:
        """Получение информации о модуле"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.config.version,
            "author": self.config.author,
            "keywords": self.config.keywords,
            "priority": self.config.priority,
            "enabled": self.config.enabled,
            "resources": {
                "templates": self.config.resources_config.templates,
                "variables": self.config.resources_config.variables,
                "dom_selectors": self.config.resources_config.dom_selectors,
                "system_commands": self.config.resources_config.system_commands,
                "custom_data": self.config.resources_config.custom_data
            }
        }
