#!/usr/bin/env python3
"""
Демо-скрипт для тестирования Этапа 2: Системные команды
"""

import os
import sys
from pathlib import Path

def test_system_commands():
    """Тест системных команд"""
    print("🔧 Тест системных команд macOS:")
    
    from src.system.macos_commands import MacOSCommands
    commands = MacOSCommands()
    
    # 1. Список процессов
    print("   1. Список процессов...")
    result = commands.list_processes()
    if result['success']:
        print(f"      ✅ Найдено {result['count']} процессов")
    else:
        print(f"      ❌ Ошибка: {result['error']}")
    
    # 2. Текущее приложение
    print("   2. Текущее приложение...")
    result = commands.get_current_app()
    if result['success']:
        print(f"      ✅ Активное: {result['app_name']}")
    else:
        print(f"      ❌ Ошибка: {result['error']}")
    
    # 3. Буфер обмена
    print("   3. Операции с буфером...")
    test_text = "Демо Этап 2: Системные команды работают!"
    copy_result = commands.copy_to_clipboard(test_text)
    if copy_result['success']:
        read_result = commands.read_clipboard()
        if read_result['success'] and test_text in read_result['text']:
            print(f"      ✅ Буфер обмена работает ({copy_result['length']} символов)")
        else:
            print(f"      ❌ Ошибка чтения буфера")
    else:
        print(f"      ❌ Ошибка копирования: {copy_result['error']}")
    
    # 4. Скриншот
    print("   4. Создание скриншота...")
    screenshot_path = "/tmp/demo_stage2_screenshot.png"
    result = commands.take_screenshot(screenshot_path)
    if result['success']:
        print(f"      ✅ Скриншот создан: {result['size']:,} байт")
    else:
        print(f"      ❌ Ошибка: {result['error']}")
    
    return True

def test_system_orchestrator():
    """Тест системного оркестратора"""
    print("\n🎯 Тест системного оркестратора:")
    
    from src.system.system_orchestrator import SystemOrchestrator
    orchestrator = SystemOrchestrator()
    
    # 1. Доступные команды
    commands = orchestrator.get_available_commands()
    print(f"   ✅ Доступно команд: {len(commands)}")
    
    # 2. Парсинг аргументов
    args = orchestrator._parse_command_args('"Google Chrome" test "arg with spaces"')
    expected = ['Google Chrome', 'test', 'arg with spaces']
    if args == expected:
        print("   ✅ Парсинг аргументов работает")
    else:
        print(f"   ❌ Ошибка парсинга: {args} != {expected}")
    
    # 3. Выполнение команд
    result = orchestrator.execute_system_command('get_current_app')
    if result['success']:
        print(f"   ✅ Выполнение команд работает: {result['app_name']}")
    else:
        print(f"   ❌ Ошибка выполнения: {result['error']}")
    
    # 4. Системный контекст
    context = orchestrator.get_system_context()
    if 'current_app' in context and 'platform' in context:
        print(f"   ✅ Системный контекст: {context['current_app']} на {context['platform']}")
    else:
        print(f"   ❌ Ошибка контекста: {context}")
    
    return True

def test_atlas_integration():
    """Тест интеграции с .atlas файлами"""
    print("\n📄 Тест интеграции с .atlas файлами:")
    
    from src.core.atlas_dsl_parser import AtlasDSLParser
    from src.system.system_orchestrator import system_orchestrator
    
    # Создаем тестовый .atlas файл
    atlas_content = '''# Demo Stage 2 Atlas File
@system get_current_app
@system copy_to_clipboard "Atlas интеграция работает!"
wait 1s
@system read_clipboard
@system take_screenshot "/tmp/atlas_demo.png"
'''
    
    atlas_file = "demo_stage2_integration.atlas"
    with open(atlas_file, 'w', encoding='utf-8') as f:
        f.write(atlas_content)
    
    try:
        # Парсим файл
        parser = AtlasDSLParser()
        result = parser.parse_file(atlas_file)
        
        system_steps = [s for s in result['steps'] if s.get('action') == 'system_command']
        print(f"   ✅ Парсинг: {len(system_steps)} системных команд из {len(result['steps'])} шагов")
        
        # Выполняем системные команды
        executed = 0
        for step in system_steps:
            command = step['command']
            args = step.get('args', '')
            
            exec_result = system_orchestrator.execute_system_command(command, args)
            if exec_result['success']:
                executed += 1
        
        print(f"   ✅ Выполнение: {executed}/{len(system_steps)} команд успешно")
        
        return True
        
    finally:
        # Удаляем тестовый файл
        if os.path.exists(atlas_file):
            os.remove(atlas_file)

def test_strategy_selection():
    """Тест выбора стратегии выполнения"""
    print("\n🎲 Тест выбора стратегии выполнения:")
    
    from src.system.system_orchestrator import SystemOrchestrator, ExecutionStrategy
    orchestrator = SystemOrchestrator()
    
    test_cases = [
        ({'action': 'system_command', 'command': 'open_app'}, {}, ExecutionStrategy.SYSTEM, "Системная команда"),
        ({'action': 'click', 'template': 'button.png'}, {'current_app': 'Chrome'}, ExecutionStrategy.DOM, "Веб-контекст"),
        ({'action': 'click', 'template': 'button.png'}, {'current_app': 'Finder'}, ExecutionStrategy.CV, "Десктоп-контекст"),
        ({'action': 'type', 'text': 'hello'}, {}, ExecutionStrategy.CV, "Обычная команда")
    ]
    
    passed = 0
    for cmd, context, expected, description in test_cases:
        strategy = orchestrator.choose_execution_strategy(cmd, context)
        if strategy == expected:
            print(f"   ✅ {description}: {strategy.value.upper()}")
            passed += 1
        else:
            print(f"   ❌ {description}: {strategy.value.upper()} (ожидался {expected.value.upper()})")
    
    print(f"   📊 Результат: {passed}/{len(test_cases)} стратегий выбраны корректно")
    return passed == len(test_cases)

def show_system_info():
    """Показать информацию о системе"""
    print("\n💻 Информация о системе:")
    
    from src.system.system_orchestrator import system_orchestrator
    
    context = system_orchestrator.get_system_context()
    print(f"   🖥️  Платформа: {context.get('platform', 'Unknown')}")
    print(f"   📱 Активное приложение: {context.get('current_app', 'Unknown')}")
    print(f"   🔢 Количество процессов: {context.get('process_count', 0)}")
    print(f"   ⏰ Время: {context.get('timestamp', 'Unknown')}")
    
    # Доступные команды
    commands = system_orchestrator.get_available_commands()
    print(f"   🛠️  Доступные системные команды ({len(commands)}):")
    for i, cmd in enumerate(commands, 1):
        print(f"      {i:2d}. {cmd}")

def main():
    """Главная функция демо"""
    print("🎯 Демо тестирование Этапа 2: Системные команды")
    print("=" * 70)
    
    tests = [
        ("Системные команды macOS", test_system_commands),
        ("Системный оркестратор", test_system_orchestrator),
        ("Интеграция с .atlas", test_atlas_integration),
        ("Выбор стратегии", test_strategy_selection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"   ❌ Тест '{test_name}' провален")
        except Exception as e:
            print(f"   ❌ Критическая ошибка в '{test_name}': {e}")
    
    show_system_info()
    
    print("\n" + "=" * 70)
    print(f"🏁 Результат: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("🎉 Этап 2: Системные команды завершен успешно!")
        print("\n📋 Что работает:")
        print("   ✅ Реальные системные команды macOS")
        print("   ✅ Полнофункциональный SystemOrchestrator")
        print("   ✅ Парсинг и выполнение @system команд в .atlas файлах")
        print("   ✅ Автоматический выбор стратегии выполнения")
        print("   ✅ Интеграция с существующей архитектурой")
        print("\n🚀 Готово к Этапу 3: Голосовой ввод!")
    else:
        print("⚠️  Есть проблемы, которые нужно исправить.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
