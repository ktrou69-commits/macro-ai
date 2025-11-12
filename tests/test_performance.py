#!/usr/bin/env python3
"""
Тесты производительности голосового ассистента - Этап 5
"""

import pytest
import time
import psutil
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from src.voice.voice_assistant import VoiceAssistant
from src.memory.state_manager import StateManager
from src.system.system_orchestrator import SystemOrchestrator
from src.core.atlas_dsl_parser import AtlasDSLParser


class TestMemoryUsage:
    """Тесты использования памяти"""
    
    def get_memory_usage(self):
        """Получить текущее использование памяти в MB"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def test_voice_assistant_memory_footprint(self):
        """Тест потребления памяти голосовым ассистентом"""
        initial_memory = self.get_memory_usage()
        
        # Создаем голосового ассистента в fallback режиме
        assistant = VoiceAssistant(
            recognition_engine="fallback",
            tts_engine="fallback"
        )
        
        after_init_memory = self.get_memory_usage()
        init_overhead = after_init_memory - initial_memory
        
        # Инициализация не должна потреблять более 50MB
        assert init_overhead < 50, f"Слишком большое потребление памяти при инициализации: {init_overhead:.1f}MB"
        
        # Обрабатываем несколько команд
        test_commands = [
            "открой Safari",
            "сделай скриншот", 
            "покажи процессы",
            "закрой приложение"
        ]
        
        for command in test_commands:
            assistant.process_text_command(command)
            time.sleep(0.1)  # Небольшая пауза
        
        final_memory = self.get_memory_usage()
        total_overhead = final_memory - initial_memory
        
        # Общее потребление не должно превышать 100MB в fallback режиме
        assert total_overhead < 100, f"Слишком большое общее потребление памяти: {total_overhead:.1f}MB"
        
        print(f"💾 Потребление памяти: инициализация {init_overhead:.1f}MB, общее {total_overhead:.1f}MB")
    
    def test_state_manager_memory_scaling(self):
        """Тест масштабирования памяти StateManager"""
        initial_memory = self.get_memory_usage()
        
        state_manager = StateManager()
        session_ids = []
        
        # Создаем 100 сессий
        for i in range(100):
            session_id = state_manager.create_session(f"test_macro_{i}.atlas")
            session_ids.append(session_id)
            
            # Добавляем данные в каждую сессию
            for step in range(5):
                state_manager.save_step_result(session_id, step, {
                    'success': True,
                    'data': f'step_{step}_result_data',
                    'timestamp': time.time()
                })
        
        after_sessions_memory = self.get_memory_usage()
        memory_per_session = (after_sessions_memory - initial_memory) / 100
        
        # Каждая сессия не должна потреблять более 0.5MB
        assert memory_per_session < 0.5, f"Слишком большое потребление памяти на сессию: {memory_per_session:.2f}MB"
        
        # Очищаем сессии
        for session_id in session_ids:
            state_manager.cleanup_session(session_id)
        
        print(f"💾 Потребление памяти на сессию: {memory_per_session:.2f}MB")


class TestResponseTimes:
    """Тесты времени отклика"""
    
    def test_system_command_execution_time(self):
        """Тест времени выполнения системных команд"""
        orchestrator = SystemOrchestrator()
        
        # Быстрые команды
        fast_commands = [
            ("get_current_app", ""),
            ("copy_to_clipboard", '"test"'),
            ("read_clipboard", ""),
        ]
        
        for command, args in fast_commands:
            start_time = time.time()
            result = orchestrator.execute_system_command(command, args)
            execution_time = time.time() - start_time
            
            assert result['success'] == True
            assert execution_time < 0.5, f"Команда '{command}' выполняется слишком медленно: {execution_time:.3f}s"
            
            print(f"⚡ {command}: {execution_time:.3f}s")
    
    def test_dsl_parsing_speed(self):
        """Тест скорости парсинга DSL"""
        parser = AtlasDSLParser()
        
        # Создаем различные типы команд
        test_commands = [
            "@system open_app \"Chrome\"",
            "wait 2s",
            "click Button",
            "@system take_screenshot \"/tmp/test.png\"",
            "type \"Hello World\"",
            "@system close_app \"Chrome\""
        ]
        
        # Тест парсинга одиночных команд
        total_time = 0
        for i, command in enumerate(test_commands, 1):
            start_time = time.time()
            result = parser._parse_line(command, i)
            parse_time = time.time() - start_time
            total_time += parse_time
            
            assert result is not None
            assert parse_time < 0.01, f"Парсинг '{command}' слишком медленный: {parse_time:.4f}s"
        
        avg_time = total_time / len(test_commands)
        assert avg_time < 0.005, f"Средняя скорость парсинга слишком медленная: {avg_time:.4f}s"
        
        print(f"⚡ Средняя скорость парсинга: {avg_time:.4f}s")
    
    def test_voice_assistant_response_time(self):
        """Тест времени отклика голосового ассистента"""
        assistant = VoiceAssistant(
            recognition_engine="fallback",
            tts_engine="fallback"
        )
        
        test_commands = [
            "покажи активное приложение",
            "сделай скриншот",
            "открой Calculator"
        ]
        
        response_times = []
        
        for command in test_commands:
            start_time = time.time()
            assistant.process_text_command(command)
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            assert response_time < 1.0, f"Команда '{command}' обрабатывается слишком медленно: {response_time:.3f}s"
        
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 0.5, f"Средний отклик слишком медленный: {avg_response_time:.3f}s"
        
        print(f"⚡ Средний отклик: {avg_response_time:.3f}s")


class TestConcurrencyAndStability:
    """Тесты параллельности и стабильности"""
    
    def test_multiple_sessions_handling(self):
        """Тест обработки множественных сессий"""
        state_manager = StateManager()
        
        # Создаем множественные сессии параллельно
        import threading
        
        session_ids = []
        errors = []
        
        def create_session_worker(worker_id):
            try:
                for i in range(10):
                    session_id = state_manager.create_session(f"worker_{worker_id}_macro_{i}.atlas")
                    session_ids.append(session_id)
                    
                    # Добавляем некоторые данные
                    state_manager.save_step_result(session_id, 1, {
                        'worker_id': worker_id,
                        'iteration': i,
                        'success': True
                    })
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")
        
        # Запускаем 5 воркеров параллельно
        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=create_session_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        # Ждем завершения всех потоков
        for thread in threads:
            thread.join()
        
        # Проверяем результаты
        assert len(errors) == 0, f"Ошибки при параллельной работе: {errors}"
        assert len(session_ids) == 50, f"Неверное количество сессий: {len(session_ids)}"
        
        # Проверяем, что все сессии доступны
        for session_id in session_ids:
            state = state_manager.get_state(session_id)
            assert state is not None
        
        # Очистка
        for session_id in session_ids:
            state_manager.cleanup_session(session_id)
        
        print(f"🔄 Успешно обработано {len(session_ids)} параллельных сессий")
    
    def test_long_running_stability(self):
        """Тест стабильности при длительной работе"""
        assistant = VoiceAssistant(
            recognition_engine="fallback",
            tts_engine="fallback"
        )
        
        initial_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        
        # Симулируем длительную работу
        commands_processed = 0
        start_time = time.time()
        
        test_commands = [
            "покажи активное приложение",
            "сделай скриншот",
            "покажи процессы",
            "копируй текст в буфер"
        ]
        
        # Выполняем команды в течение 10 секунд
        while time.time() - start_time < 10:
            command = test_commands[commands_processed % len(test_commands)]
            assistant.process_text_command(command)
            commands_processed += 1
            time.sleep(0.1)  # Небольшая пауза между командами
        
        final_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        # Рост памяти не должен превышать 20MB за 10 секунд работы
        assert memory_growth < 20, f"Слишком большой рост памяти: {memory_growth:.1f}MB"
        
        # Должно быть обработано достаточно команд
        assert commands_processed > 50, f"Слишком мало команд обработано: {commands_processed}"
        
        print(f"🕐 Обработано {commands_processed} команд за 10 секунд, рост памяти: {memory_growth:.1f}MB")


class TestResourceOptimization:
    """Тесты оптимизации ресурсов"""
    
    def test_cpu_usage_during_processing(self):
        """Тест использования CPU во время обработки"""
        assistant = VoiceAssistant(
            recognition_engine="fallback",
            tts_engine="fallback"
        )
        
        # Мониторим CPU в течение обработки команд
        cpu_measurements = []
        
        def measure_cpu():
            for _ in range(20):  # 2 секунды измерений
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_measurements.append(cpu_percent)
        
        # Запускаем мониторинг CPU в отдельном потоке
        import threading
        cpu_thread = threading.Thread(target=measure_cpu)
        cpu_thread.start()
        
        # Обрабатываем команды
        for i in range(20):
            assistant.process_text_command(f"тестовая команда {i}")
            time.sleep(0.05)
        
        cpu_thread.join()
        
        if cpu_measurements:
            avg_cpu = sum(cpu_measurements) / len(cpu_measurements)
            max_cpu = max(cpu_measurements)
            
            # В fallback режиме CPU не должен превышать 30%
            assert avg_cpu < 30, f"Слишком высокое среднее использование CPU: {avg_cpu:.1f}%"
            assert max_cpu < 50, f"Слишком высокий пик использования CPU: {max_cpu:.1f}%"
            
            print(f"💻 CPU: среднее {avg_cpu:.1f}%, максимум {max_cpu:.1f}%")
    
    def test_file_handle_management(self):
        """Тест управления файловыми дескрипторами"""
        initial_fds = len(os.listdir('/proc/self/fd')) if os.path.exists('/proc/self/fd') else 0
        
        state_manager = StateManager()
        
        # Создаем и удаляем много сессий
        for i in range(50):
            session_id = state_manager.create_session(f"fd_test_{i}.atlas")
            state_manager.save_step_result(session_id, 1, {'test': True})
            state_manager.cleanup_session(session_id)
        
        final_fds = len(os.listdir('/proc/self/fd')) if os.path.exists('/proc/self/fd') else 0
        
        # Количество файловых дескрипторов не должно сильно вырасти
        if initial_fds > 0:  # Только если система поддерживает /proc/self/fd
            fd_growth = final_fds - initial_fds
            assert fd_growth < 10, f"Слишком много открытых файловых дескрипторов: +{fd_growth}"
            print(f"📁 Рост файловых дескрипторов: +{fd_growth}")


@pytest.mark.benchmark
class TestBenchmarks:
    """Бенчмарки производительности"""
    
    def test_benchmark_state_operations(self):
        """Бенчмарк операций с состояниями"""
        state_manager = StateManager()
        
        # Бенчмарк создания сессий
        start_time = time.time()
        session_ids = []
        for i in range(100):
            session_id = state_manager.create_session(f"benchmark_{i}.atlas")
            session_ids.append(session_id)
        creation_time = time.time() - start_time
        
        # Бенчмарк сохранения результатов
        start_time = time.time()
        for session_id in session_ids:
            for step in range(5):
                state_manager.save_step_result(session_id, step, {
                    'benchmark': True,
                    'step': step,
                    'data': 'x' * 100  # Небольшой объем данных
                })
        save_time = time.time() - start_time
        
        # Бенчмарк загрузки состояний
        start_time = time.time()
        for session_id in session_ids:
            state = state_manager.get_state(session_id)
            assert state is not None
        load_time = time.time() - start_time
        
        # Очистка
        for session_id in session_ids:
            state_manager.cleanup_session(session_id)
        
        print(f"\n📊 Бенчмарки StateManager:")
        print(f"   Создание 100 сессий: {creation_time:.3f}s ({creation_time/100*1000:.1f}ms/сессия)")
        print(f"   Сохранение 500 результатов: {save_time:.3f}s ({save_time/500*1000:.1f}ms/результат)")
        print(f"   Загрузка 100 состояний: {load_time:.3f}s ({load_time/100*1000:.1f}ms/состояние)")
        
        # Проверяем соответствие целевым показателям
        assert creation_time / 100 < 0.02, "Создание сессии слишком медленное"
        assert save_time / 500 < 0.01, "Сохранение результата слишком медленное"
        assert load_time / 100 < 0.01, "Загрузка состояния слишком медленная"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '-m', 'not benchmark'])
