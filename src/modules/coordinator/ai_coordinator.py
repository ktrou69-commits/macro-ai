"""
Главный AI координатор - маршрутизатор запросов между модулями
"""

import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from .intent_analyzer import IntentAnalyzer, UserIntent
from .module_selector import ModuleSelector
from ..base.ai_module import AIModule
from ..base.module_result import ModuleResult
from ..base.ai_agent import AIAgent
from ..base.module_config import AIConfig


class AICoordinator:
    """Главный координатор модульной AI системы"""
    
    def __init__(self):
        # Компоненты координатора
        self.intent_analyzer = IntentAnalyzer()
        self.module_selector = ModuleSelector()
        
        # AI агент для обычных диалогов
        self.chat_ai = AIAgent(AIConfig(
            model="gemini-1.5-pro",
            max_tokens=2048,
            temperature=0.8
        ))
        
        # Кэш модулей
        self.module_instances = {}
        
        # Логирование
        self.logger = self._setup_logger()
        
        # Статистика
        self.stats = {
            "total_requests": 0,
            "chat_requests": 0,
            "module_requests": 0,
            "successful_executions": 0,
            "failed_executions": 0
        }
        
        self.logger.info("AI Coordinator инициализирован")
    
    def _setup_logger(self) -> logging.Logger:
        """Настройка логгера"""
        logger = logging.getLogger("ai_coordinator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '[COORDINATOR] %(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def process_user_input(self, user_input: str, input_type: str = "text", 
                          context: Optional[Dict[str, Any]] = None) -> ModuleResult:
        """
        Главный метод обработки пользовательского ввода
        
        Args:
            user_input: Ввод пользователя
            input_type: Тип ввода (text, voice)
            context: Контекст выполнения
            
        Returns:
            Результат обработки
        """
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        if context is None:
            context = {}
        
        self.logger.info(f"Обработка запроса ({input_type}): {user_input[:50]}...")
        
        try:
            # 1. Анализ намерений пользователя
            intent = self.intent_analyzer.analyze(user_input)
            self.logger.info(f"Намерения: {self.intent_analyzer.get_intent_summary(intent)}")
            
            # 2. Выбор стратегии обработки
            if intent.type == "chat" or intent.confidence < 0.4:
                # Обычный диалог
                return self._handle_chat_request(user_input, context, start_time)
            else:
                # Запуск модуля
                return self._handle_module_request(user_input, intent, context, start_time)
        
        except Exception as e:
            self.stats["failed_executions"] += 1
            error_msg = f"Ошибка координатора: {str(e)}"
            self.logger.error(error_msg)
            
            return ModuleResult(
                success=False,
                error=error_msg,
                execution_time=time.time() - start_time,
                metadata={"user_input": user_input, "context": context}
            )
    
    def _handle_chat_request(self, user_input: str, context: Dict[str, Any], 
                           start_time: float) -> ModuleResult:
        """Обработка обычного диалога"""
        self.stats["chat_requests"] += 1
        self.logger.info("Обработка как обычный диалог")
        
        try:
            # Формируем промпт для чата
            chat_prompt = self._build_chat_prompt(user_input, context)
            
            # Генерируем ответ
            response = self.chat_ai.generate(chat_prompt)
            
            execution_time = time.time() - start_time
            self.stats["successful_executions"] += 1
            
            result = ModuleResult(
                success=True,
                data={"response": response, "type": "chat"},
                execution_time=execution_time,
                metadata={"chat_response": True}
            )
            
            result.add_log("Обработано как обычный диалог")
            self.logger.info(f"Диалог завершен за {execution_time:.2f}с")
            
            return result
            
        except Exception as e:
            self.stats["failed_executions"] += 1
            error_msg = f"Ошибка обработки диалога: {str(e)}"
            self.logger.error(error_msg)
            
            return ModuleResult(
                success=False,
                error=error_msg,
                execution_time=time.time() - start_time
            )
    
    def _handle_module_request(self, user_input: str, intent: UserIntent, 
                             context: Dict[str, Any], start_time: float) -> ModuleResult:
        """Обработка запроса через модуль"""
        self.stats["module_requests"] += 1
        
        # Выбираем подходящий модуль
        module_selection = self.module_selector.select_module(intent)
        
        if not module_selection:
            self.logger.warning("Подходящий модуль не найден, переключаемся на диалог")
            return self._handle_chat_request(user_input, context, start_time)
        
        module_name, module_config = module_selection
        self.logger.info(f"Выбран модуль: {module_name}")
        
        try:
            # Получаем экземпляр модуля
            module = self._get_module_instance(module_name, module_config)
            
            # Добавляем информацию о намерениях в контекст
            enhanced_context = context.copy()
            enhanced_context.update({
                "intent": intent,
                "selected_module": module_name,
                "selection_reason": self.module_selector.get_selection_explanation(intent, module_name)
            })
            
            # Выполняем модуль
            result = module.execute(user_input, enhanced_context)
            
            # Обновляем статистику
            if result.success:
                self.stats["successful_executions"] += 1
            else:
                self.stats["failed_executions"] += 1
            
            # Добавляем метаданные координатора
            result.metadata.update({
                "coordinator_info": {
                    "selected_module": module_name,
                    "intent_analysis": intent,
                    "total_time": time.time() - start_time
                }
            })
            
            result.add_log(f"Выполнено через модуль: {module_name}")
            self.logger.info(f"Модуль {module_name} завершен, успех: {result.success}")
            
            return result
            
        except Exception as e:
            self.stats["failed_executions"] += 1
            error_msg = f"Ошибка выполнения модуля {module_name}: {str(e)}"
            self.logger.error(error_msg)
            
            return ModuleResult(
                success=False,
                error=error_msg,
                execution_time=time.time() - start_time,
                metadata={"failed_module": module_name, "intent": intent}
            )
    
    def _get_module_instance(self, module_name: str, module_config: Dict[str, Any]) -> AIModule:
        """Получение экземпляра модуля (с кэшированием)"""
        if module_name not in self.module_instances:
            # Создаем новый экземпляр модуля
            module_class = module_config["class"]
            module_instance = module_class()
            
            self.module_instances[module_name] = module_instance
            self.logger.info(f"Создан экземпляр модуля: {module_name}")
        
        return self.module_instances[module_name]
    
    def _build_chat_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        """Построение промпта для обычного диалога"""
        base_prompt = """
        Ты - AI ассистент Macro AI, специализирующийся на автоматизации macOS.
        
        Твои возможности:
        - Автоматизация браузера (Chrome, Safari)
        - Работа с приложениями macOS
        - Создание макросов и последовательностей действий
        - Голосовое управление
        - Помощь и консультации
        
        Отвечай дружелюбно и полезно. Если пользователь спрашивает о твоих возможностях,
        расскажи о модульной системе автоматизации.
        
        ЗАПРОС ПОЛЬЗОВАТЕЛЯ: {user_input}
        
        КОНТЕКСТ: {context}
        """
        
        context_str = ""
        if context:
            context_items = []
            for key, value in context.items():
                if value:
                    context_items.append(f"- {key}: {value}")
            context_str = "\n".join(context_items) if context_items else "Контекст отсутствует"
        
        return base_prompt.format(
            user_input=user_input,
            context=context_str
        )
    
    def register_module(self, module_name: str, module_class, config: Dict[str, Any]):
        """
        Регистрация нового модуля
        
        Args:
            module_name: Имя модуля
            module_class: Класс модуля
            config: Конфигурация модуля
        """
        self.module_selector.register_module(module_name, module_class, config)
        self.logger.info(f"Зарегистрирован модуль: {module_name}")
    
    def get_available_modules(self) -> Dict[str, Dict[str, Any]]:
        """Получение списка доступных модулей"""
        return self.module_selector.get_all_modules()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики работы координатора"""
        total = self.stats["total_requests"]
        success_rate = (self.stats["successful_executions"] / total * 100) if total > 0 else 0
        
        return {
            **self.stats,
            "success_rate": f"{success_rate:.1f}%",
            "chat_percentage": f"{(self.stats['chat_requests'] / total * 100):.1f}%" if total > 0 else "0%",
            "module_percentage": f"{(self.stats['module_requests'] / total * 100):.1f}%" if total > 0 else "0%"
        }
    
    def analyze_user_intent_only(self, user_input: str) -> UserIntent:
        """Только анализ намерений без выполнения"""
        return self.intent_analyzer.analyze(user_input)
    
    def explain_module_selection(self, user_input: str) -> str:
        """Объяснение выбора модуля для запроса"""
        intent = self.intent_analyzer.analyze(user_input)
        module_selection = self.module_selector.select_module(intent)
        
        explanation = f"Анализ запроса: '{user_input}'\n\n"
        explanation += f"Намерения: {self.intent_analyzer.get_intent_summary(intent)}\n\n"
        
        if module_selection:
            module_name, _ = module_selection
            explanation += self.module_selector.get_selection_explanation(intent, module_name)
        else:
            explanation += "Модуль не выбран - запрос будет обработан как обычный диалог"
        
        return explanation
