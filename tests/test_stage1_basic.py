#!/usr/bin/env python3
"""
Тесты для Этапа 1: Базовая архитектура
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.memory.state_manager import StateManager, MacroState
from src.system.system_orchestrator import SystemOrchestrator, ExecutionStrategy
from src.core.atlas_dsl_parser import AtlasDSLParser


class TestStateManager:
    """Тесты менеджера состояний"""
    
    def setup_method(self):
        """Настройка для каждого теста"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = StateManager(storage_dir=self.temp_dir)
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_session(self):
        """Тест создания сессии"""
        session_id = self.state_manager.create_session(
            atlas_file="test.atlas",
            voice_command="открой хром"
        )
        
        assert session_id is not None
        assert len(session_id) == 36  # UUID длина
        
        state = self.state_manager.get_state(session_id)
        assert state is not None
        assert state.atlas_file == "test.atlas"
        assert state.voice_command == "открой хром"
    
    def test_save_step_result(self):
        """Тест сохранения результата шага"""
        session_id = self.state_manager.create_session("test.atlas")
        
        result = {
            'success': True,
            'variables': {'screenshot_path': '/tmp/test.png'}
        }
        
        self.state_manager.save_step_result(session_id, 1, result)
        
        state = self.state_manager.get_state(session_id)
        assert state.current_step == 1
        assert 1 in state.completed_steps
        assert state.variables['screenshot_path'] == '/tmp/test.png'
    
    def test_resumable_sessions(self):
        """Тест получения возобновляемых сессий"""
        # Создаем сессию с pending шагами
        session_id = self.state_manager.create_session("test.atlas")
        self.state_manager.update_state(
            session_id, 
            pending_steps=[2, 3, 4],
            status="paused"
        )
        
        resumable = self.state_manager.get_resumable_sessions()
        assert len(resumable) == 1
        assert resumable[0].session_id == session_id


class TestSystemOrchestrator:
    """Тесты системного оркестратора"""
    
    def setup_method(self):
        self.orchestrator = SystemOrchestrator()
    
    def test_system_command_detection(self):
        """Тест определения системных команд"""
        system_cmd = {
            'action': 'system_command',
            'command': 'open_app'
        }
        
        regular_cmd = {
            'action': 'click',
            'template': 'button.png'
        }
        
        assert self.orchestrator.is_system_command(system_cmd) == True
        assert self.orchestrator.is_system_command(regular_cmd) == False
    
    def test_web_context_detection(self):
        """Тест определения веб-контекста"""
        web_context = {'current_app': 'Google Chrome'}
        desktop_context = {'current_app': 'Finder'}
        
        assert self.orchestrator.is_web_context(web_context) == True
        assert self.orchestrator.is_web_context(desktop_context) == False
    
    def test_strategy_selection(self):
        """Тест выбора стратегии выполнения"""
        # Системная команда
        system_cmd = {'action': 'system_command', 'command': 'open_app'}
        strategy = self.orchestrator.choose_execution_strategy(system_cmd)
        assert strategy == ExecutionStrategy.SYSTEM
        
        # Веб-контекст
        web_cmd = {'action': 'click', 'template': 'button.png'}
        web_context = {'current_app': 'Chrome'}
        strategy = self.orchestrator.choose_execution_strategy(web_cmd, web_context)
        assert strategy == ExecutionStrategy.DOM
        
        # Fallback на CV
        desktop_cmd = {'action': 'click', 'template': 'button.png'}
        desktop_context = {'current_app': 'Finder'}
        strategy = self.orchestrator.choose_execution_strategy(desktop_cmd, desktop_context)
        assert strategy == ExecutionStrategy.CV


class TestAtlasDSLParser:
    """Тесты парсера DSL с поддержкой @system команд"""
    
    def setup_method(self):
        self.parser = AtlasDSLParser()
    
    def test_system_command_parsing(self):
        """Тест парсинга @system команд"""
        line = '@system open_app "Chrome"'
        result = self.parser._parse_system_command(line)
        
        assert result['action'] == 'system_command'
        assert result['command'] == 'open_app'
        assert result['args'] == 'Chrome'
        assert result['hidden'] == True
    
    def test_system_command_whitelist(self):
        """Тест whitelist системных команд"""
        # Разрешенная команда
        allowed_line = '@system open_app "Chrome"'
        result = self.parser._parse_system_command(allowed_line)
        assert result is not None
        
        # Запрещенная команда
        forbidden_line = '@system rm -rf /'
        with pytest.raises(ValueError):
            self.parser._parse_system_command(forbidden_line)
    
    def test_system_command_integration(self):
        """Тест интеграции @system команд в общий парсинг"""
        dsl_content = """
# Тестовый макрос с системными командами
@system open_app "Chrome"
wait 2s
click ChromeNewTab
@system take_screenshot
"""
        
        result = self.parser.parse(dsl_content)
        steps = result['steps']
        
        # Проверяем, что системные команды парсятся
        system_steps = [step for step in steps if step.get('action') == 'system_command']
        assert len(system_steps) == 2
        
        # Проверяем первую системную команду
        first_system = system_steps[0]
        assert first_system['command'] == 'open_app'
        assert first_system['args'] == 'Chrome'
        assert first_system['hidden'] == True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
