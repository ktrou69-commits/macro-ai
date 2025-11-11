#!/usr/bin/env python3
"""
system_orchestrator.py (обновленная версия)
Полнофункциональный оркестратор системных команд
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import re

from .macos_commands import macos_commands


class ExecutionStrategy(Enum):
    """Стратегии выполнения команд"""
    DOM = "dom"
    SYSTEM = "system"
    CV = "cv"


class SystemOrchestrator:
    """Полнофункциональный оркестратор системных команд"""
    
    def __init__(self):
        self.macos_commands = macos_commands
        
        # Маппинг команд на методы
        self.command_mapping = {
            'open_app': self.macos_commands.open_app,
            'close_app': self.macos_commands.close_app,
            'focus_window': self.macos_commands.focus_window,
            'list_processes': self.macos_commands.list_processes,
            'take_screenshot': self.macos_commands.take_screenshot,
            'copy_to_clipboard': self.macos_commands.copy_to_clipboard,
            'read_clipboard': self.macos_commands.read_clipboard,
            'switch_desktop': self.macos_commands.switch_desktop,
            'get_current_app': self.macos_commands.get_current_app
        }
        
        self.web_contexts = {
            'chrome', 'safari', 'firefox', 'browser', 'webkit'
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
        return cmd_name in self.command_mapping
    
    def is_web_context(self, context: Dict[str, Any]) -> bool:
        """Проверка веб-контекста"""
        app_name = context.get('current_app', '').lower()
        return any(web_app in app_name for web_app in self.web_contexts)
    
    def execute_system_command(self, command: str, args: str = "") -> Dict[str, Any]:
        """Выполнение системной команды"""
        try:
            # Проверяем, есть ли команда в маппинге
            if command not in self.command_mapping:
                return {
                    'success': False,
                    'error': f'Неизвестная системная команда: {command}',
                    'available_commands': list(self.command_mapping.keys())
                }
            
            # Парсим аргументы
            parsed_args = self._parse_command_args(args)
            
            # Выполняем команду
            method = self.command_mapping[command]
            
            # Вызываем метод с правильными аргументами
            if command in ['open_app', 'close_app', 'focus_window']:
                if not parsed_args:
                    return {
                        'success': False,
                        'error': f'Команда {command} требует аргумент (имя приложения/окна)'
                    }
                result = method(parsed_args[0])
                
            elif command == 'copy_to_clipboard':
                if not parsed_args:
                    return {
                        'success': False,
                        'error': 'Команда copy_to_clipboard требует текст для копирования'
                    }
                result = method(parsed_args[0])
                
            elif command == 'take_screenshot':
                path = parsed_args[0] if parsed_args else None
                result = method(path)
                
            elif command == 'switch_desktop':
                if not parsed_args:
                    return {
                        'success': False,
                        'error': 'Команда switch_desktop требует номер рабочего стола'
                    }
                try:
                    desktop_num = int(parsed_args[0])
                    result = method(desktop_num)
                except ValueError:
                    return {
                        'success': False,
                        'error': f'Неверный номер рабочего стола: {parsed_args[0]}'
                    }
                    
            else:
                # Команды без аргументов
                result = method()
            
            # Добавляем метаинформацию
            result['command'] = command
            result['args'] = args
            result['execution_time'] = self._get_current_timestamp()
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка выполнения команды {command}: {str(e)}',
                'command': command,
                'args': args
            }
    
    def _parse_command_args(self, args_string: str) -> List[str]:
        """Парсинг аргументов команды"""
        if not args_string.strip():
            return []
        
        # Простой парсер для строк в кавычках и без
        args = []
        current_arg = ""
        in_quotes = False
        
        for char in args_string:
            if char == '"' and not in_quotes:
                in_quotes = True
            elif char == '"' and in_quotes:
                in_quotes = False
                if current_arg:
                    args.append(current_arg)
                    current_arg = ""
            elif char == ' ' and not in_quotes:
                if current_arg:
                    args.append(current_arg)
                    current_arg = ""
            else:
                current_arg += char
        
        if current_arg:
            args.append(current_arg)
            
        return args
    
    def get_system_context(self) -> Dict[str, Any]:
        """Получить контекст системы"""
        try:
            current_app = self.macos_commands.get_current_app()
            processes = self.macos_commands.list_processes()
            
            return {
                'current_app': current_app.get('app_name', 'Unknown') if current_app.get('success') else 'Unknown',
                'process_count': processes.get('count', 0) if processes.get('success') else 0,
                'timestamp': self._get_current_timestamp(),
                'platform': 'macOS'
            }
        except Exception as e:
            return {
                'error': f'Ошибка получения контекста: {str(e)}',
                'platform': 'macOS'
            }
    
    def _get_current_timestamp(self) -> str:
        """Получить текущий timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_available_commands(self) -> List[str]:
        """Получить список доступных команд"""
        return list(self.command_mapping.keys())
    
    def get_available_strategies(self) -> List[str]:
        """Получить список доступных стратегий"""
        return [strategy.value for strategy in ExecutionStrategy]


# Глобальный экземпляр оркестратора
system_orchestrator = SystemOrchestrator()
