#!/usr/bin/env python3
"""
Тесты для Этапа 2: Системные команды
"""

import pytest
import tempfile
import time
from pathlib import Path

from src.system.macos_commands import MacOSCommands
from src.system.system_orchestrator import SystemOrchestrator


class TestMacOSCommands:
    """Тесты системных команд macOS"""
    
    def setup_method(self):
        self.commands = MacOSCommands()
    
    def test_list_processes(self):
        """Тест получения списка процессов"""
        result = self.commands.list_processes()
        
        assert result['success'] == True
        assert 'processes' in result
        assert result['count'] > 0
        assert len(result['processes']) > 0
        
        # Проверяем структуру процесса
        process = result['processes'][0]
        assert 'pid' in process
        assert 'name' in process
        assert isinstance(process['pid'], int)
    
    def test_take_screenshot(self):
        """Тест создания скриншота"""
        with tempfile.TemporaryDirectory() as temp_dir:
            screenshot_path = Path(temp_dir) / "test_screenshot.png"
            
            result = self.commands.take_screenshot(str(screenshot_path))
            
            assert result['success'] == True
            assert result['path'] == str(screenshot_path)
            assert screenshot_path.exists()
            assert screenshot_path.stat().st_size > 0
    
    def test_clipboard_operations(self):
        """Тест операций с буфером обмена"""
        test_text = "Тестовый текст для буфера обмена"
        
        # Копируем в буфер
        copy_result = self.commands.copy_to_clipboard(test_text)
        assert copy_result['success'] == True
        assert copy_result['text'] == test_text
        
        # Читаем из буфера
        read_result = self.commands.read_clipboard()
        assert read_result['success'] == True
        assert test_text in read_result['text']
    
    def test_get_current_app(self):
        """Тест получения текущего приложения"""
        result = self.commands.get_current_app()
        
        assert result['success'] == True
        assert 'app_name' in result
        assert result['app_name'] != 'Unknown'
    
    @pytest.mark.slow
    def test_open_close_app(self):
        """Тест открытия и закрытия приложения (медленный тест)"""
        app_name = "Calculator"
        
        # Открываем приложение
        open_result = self.commands.open_app(app_name)
        assert open_result['success'] == True
        
        # Ждем запуска
        time.sleep(2)
        
        # Проверяем, что приложение запущено
        processes = self.commands.list_processes()
        calculator_running = any(
            app_name.lower() in proc['name'].lower() 
            for proc in processes['processes']
        )
        assert calculator_running == True
        
        # Закрываем приложение
        close_result = self.commands.close_app(app_name)
        assert close_result['success'] == True


class TestSystemOrchestrator:
    """Тесты системного оркестратора"""
    
    def setup_method(self):
        self.orchestrator = SystemOrchestrator()
    
    def test_command_parsing(self):
        """Тест парсинга аргументов команд"""
        # Простые аргументы
        args1 = self.orchestrator._parse_command_args('Calculator')
        assert args1 == ['Calculator']
        
        # Аргументы в кавычках
        args2 = self.orchestrator._parse_command_args('"Google Chrome"')
        assert args2 == ['Google Chrome']
        
        # Множественные аргументы
        args3 = self.orchestrator._parse_command_args('"App Name" arg2 "arg 3"')
        assert args3 == ['App Name', 'arg2', 'arg 3']
    
    def test_system_command_execution(self):
        """Тест выполнения системных команд"""
        # Тест команды без аргументов
        result1 = self.orchestrator.execute_system_command('list_processes')
        assert result1['success'] == True
        assert result1['command'] == 'list_processes'
        
        # Тест команды с аргументами
        result2 = self.orchestrator.execute_system_command(
            'copy_to_clipboard', 
            '"Тестовый текст"'
        )
        assert result2['success'] == True
        assert result2['command'] == 'copy_to_clipboard'
    
    def test_invalid_command(self):
        """Тест обработки неверных команд"""
        result = self.orchestrator.execute_system_command('invalid_command')
        
        assert result['success'] == False
        assert 'Неизвестная системная команда' in result['error']
        assert 'available_commands' in result
    
    def test_get_system_context(self):
        """Тест получения системного контекста"""
        context = self.orchestrator.get_system_context()
        
        assert 'current_app' in context
        assert 'platform' in context
        assert context['platform'] == 'macOS'
        assert 'timestamp' in context
    
    def test_available_commands(self):
        """Тест получения списка доступных команд"""
        commands = self.orchestrator.get_available_commands()
        
        assert isinstance(commands, list)
        assert len(commands) > 0
        assert 'open_app' in commands
        assert 'take_screenshot' in commands


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
