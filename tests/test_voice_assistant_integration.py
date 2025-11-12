#!/usr/bin/env python3
"""
Интеграционные тесты голосового ассистента - Этап 5
"""

import pytest
import time
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from src.voice.speech_recognition import VoiceRecognizer, HotwordDetector
from src.voice.text_to_speech import TextToSpeech, VoiceAssistantResponses
from src.voice.voice_assistant import VoiceAssistant
from src.memory.state_manager import StateManager
from src.system.system_orchestrator import SystemOrchestrator
from src.core.atlas_dsl_parser import AtlasDSLParser


class TestVoiceAssistantIntegration:
    """Интеграционные тесты полного цикла"""
    
    def setup_method(self):
        """Настройка для каждого теста"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = StateManager(storage_dir=self.temp_dir)
        self.orchestrator = SystemOrchestrator()
        self.parser = AtlasDSLParser()
        
    def teardown_method(self):
        """Очистка после теста"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_full_voice_workflow(self):
        """Тест полного голосового workflow"""
        # Создаем сессию с голосовой командой
        session_id = self.state_manager.create_session(
            atlas_file="test_voice.atlas",
            voice_command="открой хром"
        )
        
        # Проверяем состояние
        state = self.state_manager.get_state(session_id)
        assert state is not None
        assert state.voice_command == "открой хром"
        assert state.current_step == 0
        
        # Симулируем выполнение системной команды
        result = self.orchestrator.execute_system_command(
            "open_app", '"Google Chrome"'
        )
        assert result['success'] == True
        assert 'app_name' in result or 'message' in result
        
        # Сохраняем результат выполнения
        self.state_manager.save_step_result(session_id, 1, result)
        
        # Проверяем обновленное состояние
        updated_state = self.state_manager.get_state(session_id)
        assert updated_state.current_step == 1
        assert 1 in updated_state.completed_steps
    
    def test_atlas_system_commands_parsing(self):
        """Тест парсинга @system команд в .atlas файлах"""
        atlas_content = '''# Тестовый .atlas файл с системными командами
@system open_app "Chrome"
wait 2s
@system take_screenshot "/tmp/test.png"
click Button
@system close_app "Chrome"
@system get_current_app
'''
        
        lines = [line.strip() for line in atlas_content.strip().split('\n') if line.strip()]
        parsed_commands = []
        
        for i, line in enumerate(lines, 1):
            if not line.startswith('#'):  # Пропускаем комментарии
                parsed = self.parser.parse(line)
                if parsed and 'steps' in parsed:
                    parsed_commands.extend(parsed['steps'])
        
        # Проверяем системные команды
        system_commands = [cmd for cmd in parsed_commands if cmd.get('action') == 'system_command']
        regular_commands = [cmd for cmd in parsed_commands if cmd.get('action') != 'system_command']
        
        assert len(system_commands) == 4  # 4 @system команды
        assert len(regular_commands) >= 2  # wait и click
        
        # Проверяем конкретные системные команды
        system_cmd_names = [cmd['command'] for cmd in system_commands]
        expected_commands = ['open_app', 'take_screenshot', 'close_app', 'get_current_app']
        
        for expected in expected_commands:
            assert expected in system_cmd_names
    
    def test_hotword_detection_and_command_extraction(self):
        """Тест обнаружения ключевых слов и извлечения команд"""
        detector = HotwordDetector()
        
        test_cases = [
            ("Окей ассистент, открой Safari", True, "открой Safari"),
            ("Привет ассистент, сделай скриншот", True, "сделай скриншот"),
            ("Эй макро, покажи процессы", True, "покажи процессы"),
            ("Просто обычная фраза", False, None),
            ("Ассистент, помоги с задачей", True, "помоги с задачей"),
            ("Слушай, что делать дальше", True, "что делать дальше")
        ]
        
        for phrase, should_detect, expected_command in test_cases:
            detected = detector.detect_hotword(phrase)
            assert detected == should_detect, f"Неверное обнаружение для '{phrase}'"
            
            if should_detect:
                extracted = detector.extract_command(phrase)
                assert extracted == expected_command, f"Неверная команда из '{phrase}': '{extracted}' != '{expected_command}'"
    
    def test_voice_assistant_command_processing(self):
        """Тест обработки команд голосовым ассистентом"""
        # Используем fallback режимы для тестирования
        assistant = VoiceAssistant(
            recognition_engine="fallback",
            tts_engine="fallback"
        )
        
        # Тестируем классификацию команд
        test_commands = [
            ("открой Safari", True, False),  # простая системная
            ("сделай скриншот", True, False),  # простая системная
            ("создай макрос для гугла", False, True),  # AI команда
            ("покажи активное приложение", False, False),  # общая команда
        ]
        
        for command, is_simple_system, is_ai in test_commands:
            simple_result = assistant._is_simple_system_command(command)
            ai_result = assistant._is_ai_command(command)
            
            assert simple_result == is_simple_system, f"Неверная классификация системной команды: '{command}'"
            assert ai_result == is_ai, f"Неверная классификация AI команды: '{command}'"
    
    def test_state_persistence_and_recovery(self):
        """Тест сохранения и восстановления состояний"""
        # Создаем сессию с несколькими шагами
        session_id = self.state_manager.create_session(
            atlas_file="complex_macro.atlas",
            voice_command="выполни сложный макрос"
        )
        
        # Симулируем выполнение нескольких шагов
        steps_data = [
            {"step": 1, "action": "open_app", "result": {"success": True, "app": "Chrome"}},
            {"step": 2, "action": "wait", "result": {"success": True, "duration": 2}},
            {"step": 3, "action": "take_screenshot", "result": {"success": True, "path": "/tmp/test.png"}},
        ]
        
        for step_data in steps_data:
            self.state_manager.save_step_result(
                session_id, 
                step_data["step"], 
                step_data["result"]
            )
        
        # Проверяем состояние
        state = self.state_manager.get_state(session_id)
        assert state.current_step == 3
        assert len(state.completed_steps) == 3
        
        # Проверяем возможность восстановления
        resumable_sessions = self.state_manager.get_resumable_sessions()
        session_ids = [s.session_id for s in resumable_sessions]
        assert session_id in session_ids
        
        # Тестируем восстановление конкретной сессии
        restored_state = self.state_manager.get_state(session_id)
        assert restored_state.session_id == session_id
        assert restored_state.voice_command == "выполни сложный макрос"
        assert restored_state.current_step == 3
    
    @pytest.mark.slow
    def test_tts_functionality(self):
        """Тест функциональности синтеза речи"""
        tts = TextToSpeech(engine="fallback")  # Используем fallback для тестов
        responses = VoiceAssistantResponses(tts)
        
        # Тест базового TTS
        result = tts.speak("Тестовое сообщение", priority="high")
        assert result == True
        
        # Тест быстрых ответов
        responses.acknowledge_command("открой Safari")
        responses.report_working()
        responses.report_completed("тестирование")
        responses.report_error("тестовая ошибка")
        
        # Ждем обработки очереди
        time.sleep(0.5)
        
        # Тест остановки речи
        tts.speak("Длинное тестовое сообщение для проверки остановки")
        tts.stop_speaking()
        assert tts.is_speaking == False
    
    def test_system_orchestrator_integration(self):
        """Тест интеграции системного оркестратора"""
        # Тест доступных команд
        available_commands = self.orchestrator.get_available_commands()
        expected_commands = [
            'open_app', 'close_app', 'focus_window', 'take_screenshot',
            'copy_to_clipboard', 'read_clipboard', 'list_processes', 'get_current_app'
        ]
        
        for cmd in expected_commands:
            assert cmd in available_commands, f"Команда '{cmd}' недоступна"
        
        # Тест выполнения безопасных команд
        safe_tests = [
            ("get_current_app", ""),
            ("list_processes", ""),
            ("copy_to_clipboard", '"тестовый текст"'),
            ("read_clipboard", ""),
        ]
        
        for command, args in safe_tests:
            result = self.orchestrator.execute_system_command(command, args)
            assert result['success'] == True, f"Команда '{command}' не выполнилась: {result.get('error', 'Unknown error')}"
            assert result['command'] == command
        
        # Тест неизвестной команды
        result = self.orchestrator.execute_system_command('invalid_command')
        assert result['success'] == False
        assert 'Неизвестная системная команда' in result['error']


class TestPerformanceOptimization:
    """Тесты производительности и оптимизации"""
    
    def test_state_manager_performance(self):
        """Тест производительности StateManager"""
        state_manager = StateManager()
        
        # Тест создания множественных сессий
        start_time = time.time()
        session_ids = []
        
        for i in range(50):  # Уменьшено для стабильности тестов
            session_id = state_manager.create_session(f"test_{i}.atlas")
            session_ids.append(session_id)
        
        creation_time = time.time() - start_time
        assert creation_time < 3.0, f"Создание сессий слишком медленное: {creation_time:.2f}s"
        
        # Тест загрузки состояний
        start_time = time.time()
        for session_id in session_ids[:10]:  # Проверяем первые 10
            state = state_manager.get_state(session_id)
            assert state is not None
        
        loading_time = time.time() - start_time
        assert loading_time < 1.0, f"Загрузка состояний слишком медленная: {loading_time:.2f}s"
        
        # Очистка тестовых данных
        state_manager.cleanup_old_states(max_age_hours=0)  # Очищаем все
    
    def test_dsl_parser_performance(self):
        """Тест производительности DSL парсера"""
        parser = AtlasDSLParser()
        
        # Создаем большой .atlas файл
        large_atlas = []
        for i in range(200):  # Уменьшено для стабильности
            large_atlas.append(f"@system open_app \"App_{i}\"")
            large_atlas.append(f"wait {i % 5 + 1}s")
            large_atlas.append(f"click Button_{i}")
        
        # Тест парсинга
        start_time = time.time()
        parsed_commands = []
        
        for line in large_atlas:
            parsed = parser.parse(line)
            if parsed and 'steps' in parsed:
                parsed_commands.extend(parsed['steps'])
        
        parsing_time = time.time() - start_time
        assert parsing_time < 2.0, f"Парсинг слишком медленный: {parsing_time:.2f}s"
        assert len(parsed_commands) > 0
        
        # Проверяем, что системные команды парсятся корректно
        system_commands = [cmd for cmd in parsed_commands if cmd.get('action') == 'system_command']
        assert len(system_commands) > 0
    
    def test_voice_assistant_initialization_time(self):
        """Тест времени инициализации голосового ассистента"""
        start_time = time.time()
        
        # Инициализация в fallback режиме
        assistant = VoiceAssistant(
            recognition_engine="fallback",
            tts_engine="fallback"
        )
        
        init_time = time.time() - start_time
        assert init_time < 2.0, f"Инициализация слишком медленная: {init_time:.2f}s"
        
        # Проверяем, что компоненты инициализированы
        assert assistant.voice_recognizer is not None
        assert assistant.tts is not None
        assert assistant.hotword_detector is not None


class TestSecurityAndValidation:
    """Тесты безопасности и валидации"""
    
    def test_system_commands_whitelist(self):
        """Тест whitelist'а системных команд"""
        orchestrator = SystemOrchestrator()
        
        # Разрешенные команды
        allowed_commands = [
            'open_app', 'close_app', 'focus_window', 'take_screenshot',
            'copy_to_clipboard', 'read_clipboard', 'list_processes', 'get_current_app'
        ]
        
        for command in allowed_commands:
            result = orchestrator.execute_system_command(command)
            # Команда должна быть распознана (может не выполниться из-за аргументов)
            assert 'Неизвестная системная команда' not in result.get('error', '')
        
        # Запрещенные команды
        forbidden_commands = [
            'rm_file', 'delete_file', 'execute_shell', 'sudo_command',
            'chmod_file', 'kill_process', 'system_shutdown'
        ]
        
        for command in forbidden_commands:
            result = orchestrator.execute_system_command(command)
            assert result['success'] == False
            assert 'Неизвестная системная команда' in result['error']
    
    def test_command_argument_validation(self):
        """Тест валидации аргументов команд"""
        orchestrator = SystemOrchestrator()
        
        # Тест парсинга аргументов
        test_cases = [
            ('Calculator', ['Calculator']),
            ('"Google Chrome"', ['Google Chrome']),
            ('"App Name" arg2 "arg 3"', ['App Name', 'arg2', 'arg 3']),
            ('', []),
        ]
        
        for input_args, expected in test_cases:
            parsed = orchestrator._parse_command_args(input_args)
            assert parsed == expected, f"Неверный парсинг '{input_args}': {parsed} != {expected}"
    
    def test_state_data_validation(self):
        """Тест валидации данных состояний"""
        state_manager = StateManager()
        
        # Тест создания сессии с валидными данными
        session_id = state_manager.create_session(
            atlas_file="valid_macro.atlas",
            voice_command="валидная команда"
        )
        assert session_id is not None
        
        state = state_manager.get_state(session_id)
        assert state.atlas_file == "valid_macro.atlas"
        assert state.voice_command == "валидная команда"
        
        # Очистка
        state_manager.cleanup_old_states(max_age_hours=0)
    
    def test_hotword_detection_security(self):
        """Тест безопасности обнаружения ключевых слов"""
        detector = HotwordDetector()
        
        # Тест на ложные срабатывания
        false_positives = [
            "Ассистенты бывают разные",
            "Макросы это полезно", 
            "Слушать музыку приятно",
            "Окей, давай поговорим",
            "Привет всем участникам"
        ]
        
        for phrase in false_positives:
            detected = detector.detect_hotword(phrase)
            assert detected == False, f"Ложное срабатывание на '{phrase}'"
        
        # Тест на корректные активации
        true_positives = [
            "Окей ассистент, помоги",
            "Привет ассистент, что делать",
            "Эй макро, начни работу",
            "Слушай, выполни команду",
            "Ассистент, открой приложение"
        ]
        
        for phrase in true_positives:
            detected = detector.detect_hotword(phrase)
            assert detected == True, f"Пропущена активация на '{phrase}'"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
