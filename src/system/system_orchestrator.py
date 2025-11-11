#!/usr/bin/env python3
"""
system_orchestrator.py
Оркестратор выбора стратегии выполнения команд
"""

from typing import Dict, Any, Optional, List
from enum import Enum


class ExecutionStrategy(Enum):
    """Стратегии выполнения команд"""
    DOM = "dom"
    SYSTEM = "system"
    CV = "cv"


class SystemOrchestrator:
    """Оркестратор системных команд и выбора стратегии"""
    
    def __init__(self):
        self.system_commands = {
            'open_app', 'close_app', 'focus_window',
            'take_screenshot', 'copy_to_clipboard',
            'list_processes', 'switch_desktop'
        }
        
        self.web_contexts = {
            'chrome', 'safari', 'firefox', 'browser'
        }
    
    def choose_execution_strategy(self, command: Dict[str, Any], context: Dict[str, Any] = None) -> ExecutionStrategy:
        """
        Выбор стратегии выполнения команды
        
        Приоритет:
        1. DOM (если веб-контекст)
        2. System API (если системная команда)
        3. CV (универсальный fallback)
        """
        if context is None:
            context = {}
            
        # 1. Проверяем системные команды
        if self.is_system_command(command):
            return ExecutionStrategy.SYSTEM
            
        # 2. Проверяем веб-контекст
        if self.is_web_context(context):
            return ExecutionStrategy.DOM
            
        # 3. Fallback на CV
        return ExecutionStrategy.CV
    
    def is_system_command(self, command: Dict[str, Any]) -> bool:
        """Проверка, является ли команда системной"""
        if command.get('action') == 'system_command':
            return True
            
        # Проверяем по названию команды
        cmd_name = command.get('command', '')
        return cmd_name in self.system_commands
    
    def is_web_context(self, context: Dict[str, Any]) -> bool:
        """Проверка веб-контекста"""
        app_name = context.get('current_app', '').lower()
        return any(web_app in app_name for web_app in self.web_contexts)
    
    def execute_system_command(self, command: str, args: str = "") -> Dict[str, Any]:
        """
        Выполнение системной команды
        Пока заглушка - реализация в Этапе 2
        """
        print(f"🔧 Выполнение системной команды: {command} {args}")
        
        # Заглушка для тестирования
        return {
            'success': True,
            'command': command,
            'args': args,
            'result': f"Команда {command} выполнена успешно"
        }
    
    def get_available_strategies(self) -> List[str]:
        """Получить список доступных стратегий"""
        return [strategy.value for strategy in ExecutionStrategy]


# Глобальный экземпляр оркестратора
system_orchestrator = SystemOrchestrator()
