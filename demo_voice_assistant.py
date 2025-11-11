#!/usr/bin/env python3
"""
Демо-скрипт для тестирования базовой архитектуры голосового ассистента
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Тест 1: Проверка импортов"""
    print("🧪 Тест 1: Проверка импортов...")
    
    try:
        from src.memory.state_manager import StateManager, MacroState, state_manager
        print("   ✅ StateManager импортирован")
    except ImportError as e:
        print(f"   ❌ StateManager: {e}")
        return False
    
    try:
        from src.system.system_orchestrator import SystemOrchestrator, ExecutionStrategy, system_orchestrator
        print("   ✅ SystemOrchestrator импортирован")
    except ImportError as e:
        print(f"   ❌ SystemOrchestrator: {e}")
        return False
    
    try:
        from src.core.atlas_dsl_parser import AtlasDSLParser
        print("   ✅ AtlasDSLParser с @system поддержкой импортирован")
    except ImportError as e:
        print(f"   ❌ AtlasDSLParser: {e}")
        return False
    
    try:
        from src.core.macro_sequence import MacroRunner
        print("   ✅ MacroRunner с StateManager интеграцией импортирован")
    except ImportError as e:
        print(f"   ❌ MacroRunner: {e}")
        return False
    
    return True

def test_state_manager():
    """Тест 2: StateManager функциональность"""
    print("\n🧪 Тест 2: StateManager функциональность...")
    
    from src.memory.state_manager import StateManager
    import tempfile
    import shutil
    
    # Создаем временную папку для тестов
    temp_dir = tempfile.mkdtemp()
    manager = StateManager(storage_dir=temp_dir)
    
    try:
        # Создаем сессию
        session_id = manager.create_session(
            atlas_file="demo_test.atlas",
            voice_command="тестовая команда"
        )
        print(f"   ✅ Сессия создана: {session_id[:8]}...")
        
        # Сохраняем результат шага
        manager.save_step_result(session_id, 1, {
            'success': True,
            'variables': {'test_var': 'test_value'}
        })
        print("   ✅ Результат шага сохранен")
        
        # Получаем состояние
        state = manager.get_state(session_id)
        if state and state.current_step == 1:
            print("   ✅ Состояние загружено корректно")
        else:
            print("   ❌ Ошибка загрузки состояния")
            return False
        
        # Проверяем контекст для ИИ
        context = state.get_context_for_ai()
        if 'session_id' in context and 'variables' in context:
            print("   ✅ Контекст для ИИ сформирован")
        else:
            print("   ❌ Ошибка формирования контекста")
            return False
        
        return True
    
    finally:
        # Очищаем временную папку
        shutil.rmtree(temp_dir)

def test_system_orchestrator():
    """Тест 3: SystemOrchestrator логика"""
    print("\n🧪 Тест 3: SystemOrchestrator логика...")
    
    from src.system.system_orchestrator import SystemOrchestrator, ExecutionStrategy
    
    orchestrator = SystemOrchestrator()
    
    # Тест системной команды
    system_cmd = {'action': 'system_command', 'command': 'open_app'}
    strategy = orchestrator.choose_execution_strategy(system_cmd)
    if strategy == ExecutionStrategy.SYSTEM:
        print("   ✅ Системная команда определена корректно")
    else:
        print(f"   ❌ Неверная стратегия для системной команды: {strategy}")
        return False
    
    # Тест веб-контекста
    web_cmd = {'action': 'click', 'template': 'button.png'}
    web_context = {'current_app': 'Google Chrome'}
    strategy = orchestrator.choose_execution_strategy(web_cmd, web_context)
    if strategy == ExecutionStrategy.DOM:
        print("   ✅ Веб-контекст определен корректно")
    else:
        print(f"   ❌ Неверная стратегия для веб-контекста: {strategy}")
        return False
    
    # Тест fallback на CV
    desktop_cmd = {'action': 'click', 'template': 'button.png'}
    desktop_context = {'current_app': 'Finder'}
    strategy = orchestrator.choose_execution_strategy(desktop_cmd, desktop_context)
    if strategy == ExecutionStrategy.CV:
        print("   ✅ Fallback на CV работает корректно")
    else:
        print(f"   ❌ Неверная стратегия для fallback: {strategy}")
        return False
    
    return True

def test_atlas_parser():
    """Тест 4: Парсинг @system команд"""
    print("\n🧪 Тест 4: Парсинг @system команд...")
    
    from src.core.atlas_dsl_parser import AtlasDSLParser
    
    parser = AtlasDSLParser()
    
    # Тест парсинга системной команды
    try:
        result = parser._parse_system_command('@system open_app "Chrome"')
        if (result['action'] == 'system_command' and 
            result['command'] == 'open_app' and 
            result['args'] == 'Chrome'):
            print("   ✅ Парсинг @system команды работает")
        else:
            print(f"   ❌ Неверный результат парсинга: {result}")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка парсинга: {e}")
        return False
    
    # Тест whitelist
    try:
        parser._parse_system_command('@system forbidden_command')
        print("   ❌ Whitelist не работает - запрещенная команда прошла")
        return False
    except ValueError:
        print("   ✅ Whitelist работает корректно")
    
    return True

def test_atlas_file():
    """Тест 5: Парсинг тестового .atlas файла"""
    print("\n🧪 Тест 5: Парсинг тестового .atlas файла...")
    
    atlas_file = "test_voice_assistant.atlas"
    if not os.path.exists(atlas_file):
        print(f"   ❌ Файл {atlas_file} не найден")
        return False
    
    from src.core.atlas_dsl_parser import AtlasDSLParser
    
    try:
        parser = AtlasDSLParser()
        result = parser.parse_file(atlas_file)
        
        total_steps = len(result['steps'])
        system_steps = [s for s in result['steps'] if s.get('action') == 'system_command']
        
        print(f"   ✅ Файл распарсен: {total_steps} шагов")
        print(f"   ✅ Найдено системных команд: {len(system_steps)}")
        
        for i, step in enumerate(system_steps, 1):
            print(f"      {i}. {step['command']} {step['args']}")
        
        return True
    
    except Exception as e:
        print(f"   ❌ Ошибка парсинга файла: {e}")
        return False

def test_macro_runner_integration():
    """Тест 6: Интеграция с MacroRunner"""
    print("\n🧪 Тест 6: Интеграция с MacroRunner...")
    
    from src.core.macro_sequence import MacroRunner
    
    try:
        runner = MacroRunner()
        
        # Создаем сессию
        session_id = runner.start_session(
            atlas_file="test_voice_assistant.atlas",
            voice_command="Тест интеграции"
        )
        
        if session_id:
            print(f"   ✅ Сессия MacroRunner создана: {session_id[:8]}...")
        else:
            print("   ❌ Не удалось создать сессию")
            return False
        
        # Сохраняем результат
        runner.save_step_result(1, {
            'success': True,
            'variables': {'integration_test': 'passed'}
        })
        print("   ✅ Результат шага сохранен через MacroRunner")
        
        # Получаем контекст
        context = runner.get_ai_context()
        if context and 'session_id' in context:
            print("   ✅ Контекст для ИИ получен через MacroRunner")
            print(f"      Прогресс: {context.get('progress', 'N/A')}")
            print(f"      Переменные: {len(context.get('variables', {}))}")
        else:
            print("   ❌ Ошибка получения контекста")
            return False
        
        return True
    
    except Exception as e:
        print(f"   ❌ Ошибка интеграции: {e}")
        return False

def main():
    """Главная функция демо"""
    print("🎯 Демо тестирование базовой архитектуры голосового ассистента")
    print("=" * 70)
    
    tests = [
        test_imports,
        test_state_manager,
        test_system_orchestrator,
        test_atlas_parser,
        test_atlas_file,
        test_macro_runner_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print("   ❌ Тест провален")
        except Exception as e:
            print(f"   ❌ Критическая ошибка: {e}")
    
    print("\n" + "=" * 70)
    print(f"🏁 Результат: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("🎉 Все тесты прошли! Базовая архитектура работает корректно.")
        print("\n📋 Что можно делать дальше:")
        print("   1. Запустить полные тесты: python3 -m pytest tests/test_stage1_basic.py -v")
        print("   2. Перейти к Этапу 2: Системные команды")
        print("   3. Протестировать с реальными .atlas файлами")
    else:
        print("⚠️  Есть проблемы, которые нужно исправить.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
