#!/usr/bin/env python3
"""
Интерактивное тестирование StateManager и системных команд
"""

from src.memory.state_manager import state_manager
from src.system.system_orchestrator import system_orchestrator, ExecutionStrategy
from src.core.macro_sequence import MacroRunner
from src.core.atlas_dsl_parser import AtlasDSLParser

def demo_state_management():
    """Демо управления состоянием"""
    print("🧠 Демо управления состоянием макросов:")
    
    runner = MacroRunner()
    
    # Создаем несколько сессий
    sessions = []
    for i in range(3):
        session_id = runner.start_session(
            f"test_macro_{i}.atlas", 
            f"Голосовая команда {i+1}"
        )
        sessions.append(session_id)
        print(f"   Сессия {i+1}: {session_id[:8]}...")
        
        # Симулируем выполнение шагов
        for step in range(1, 4):
            runner.save_step_result(step, {
                'success': True,
                'variables': {f'step_{step}_result': f'value_{step}'}
            })
    
    # Показываем состояния
    print(f"\n📊 Активных сессий: {len(state_manager.active_states)}")
    
    for session_id in sessions:
        state = state_manager.get_state(session_id)
        if state:
            context = state.get_context_for_ai()
            print(f"   {session_id[:8]}: {context['progress']} шагов, {len(context['variables'])} переменных")

def demo_strategy_selection():
    """Демо выбора стратегии выполнения"""
    print("\n🎯 Демо выбора стратегии выполнения:")
    
    test_commands = [
        ({'action': 'system_command', 'command': 'open_app'}, {}, "Системная команда"),
        ({'action': 'click', 'template': 'button.png'}, {'current_app': 'Chrome'}, "Веб-контекст"),
        ({'action': 'click', 'template': 'button.png'}, {'current_app': 'Finder'}, "Десктоп-контекст"),
        ({'action': 'type', 'text': 'hello'}, {}, "Обычная команда")
    ]
    
    for cmd, context, description in test_commands:
        strategy = system_orchestrator.choose_execution_strategy(cmd, context)
        print(f"   {description}: {strategy.value.upper()}")

def demo_atlas_parsing():
    """Демо парсинга .atlas файлов"""
    print("\n📄 Демо парсинга .atlas файлов:")
    
    parser = AtlasDSLParser()
    
    # Тестируем разные типы команд
    test_lines = [
        '@system open_app "Chrome"',
        '@system focus_window "Chrome"',
        'click Button',
        'wait 2s',
        'type "Hello World"',
        '@system take_screenshot'
    ]
    
    for line in test_lines:
        try:
            if line.startswith('@system'):
                result = parser._parse_system_command(line)
                print(f"   {line} → SYSTEM: {result['command']} {result['args']}")
            else:
                # Для обычных команд используем общий парсер
                result = parser._parse_line(line)
                if result:
                    print(f"   {line} → {result['action'].upper()}")
                else:
                    print(f"   {line} → SKIP")
        except Exception as e:
            print(f"   {line} → ERROR: {e}")

def show_file_structure():
    """Показать созданную структуру файлов"""
    print("\n📁 Созданная структура файлов:")
    
    import os
    from pathlib import Path
    
    def show_tree(path, prefix="", max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return
            
        path = Path(path)
        if not path.exists():
            return
            
        items = sorted([p for p in path.iterdir() if not p.name.startswith('.')])
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir() and current_depth < max_depth - 1:
                next_prefix = prefix + ("    " if is_last else "│   ")
                show_tree(item, next_prefix, max_depth, current_depth + 1)
    
    print("   src/")
    show_tree("src", "   ")

def main():
    """Главная функция интерактивного теста"""
    print("🎮 Интерактивное тестирование базовой архитектуры")
    print("=" * 60)
    
    show_file_structure()
    demo_state_management()
    demo_strategy_selection()
    demo_atlas_parsing()
    
    print("\n" + "=" * 60)
    print("🎉 Интерактивное тестирование завершено!")
    print("\n💡 Подсказки:")
    print("   • Все состояния сохраняются в папке macro_states/")
    print("   • Системные команды ограничены whitelist'ом")
    print("   • Стратегии выбираются автоматически: DOM → System → CV")
    print("   • Можно создавать свои .atlas файлы с @system командами")

if __name__ == "__main__":
    main()
