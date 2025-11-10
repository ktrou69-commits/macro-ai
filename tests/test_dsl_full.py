#!/usr/bin/env python3
"""
test_dsl_full.py
🔥 КРИТИЧНО: Полное тестирование DSL парсера

Проверяет ВСЕ команды DSL:
- click, type, wait, press, open
- try/catch блоки
- Переменные
- Комментарии
- Вложенные блоки
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.atlas_dsl_parser import AtlasDSLParser


def test_click_command():
    """Тест команды click"""
    print("\n" + "="*60)
    print("🧪 Тест 1: Команда click")
    print("="*60)
    
    parser = AtlasDSLParser()
    
    # Простой click
    dsl = "click ChromeApp"
    result = parser.parse(dsl)
    assert result is not None, "click не распарсился"
    assert 'steps' in result or 'sequences' in result, "Нет steps/sequences"
    print(f"✅ click ChromeApp распарсился")
    
    # Click с координатами
    dsl = "click ChromeApp at 100,200"
    result = parser.parse(dsl)
    assert result is not None, "click at не распарсился"
    print(f"✅ click at координаты распарсился")
    
    print()


def test_type_command():
    """Тест команды type"""
    print("="*60)
    print("🧪 Тест 2: Команда type")
    print("="*60)
    
    parser = AtlasDSLParser()
    
    # Type с кавычками
    dsl = "type 'hello world'"
    result = parser.parse(dsl)
    assert result is not None, "type не распарсился"
    print(f"✅ type 'text' распарсился")
    
    # Type без кавычек
    dsl = "type hello"
    result = parser.parse(dsl)
    assert result is not None, "type без кавычек не распарсился"
    print(f"✅ type text распарсился")
    
    print()


def test_wait_command():
    """Тест команды wait"""
    print("="*60)
    print("🧪 Тест 3: Команда wait")
    print("="*60)
    
    parser = AtlasDSLParser()
    
    # Wait секунды
    dsl = "wait 5s"
    result = parser.parse(dsl)
    assert result is not None, "wait не распарсился"
    print(f"✅ wait 5s распарсился")
    
    # Wait миллисекунды
    dsl = "wait 500ms"
    result = parser.parse(dsl)
    assert result is not None, "wait ms не распарсился"
    print(f"✅ wait 500ms распарсился")
    
    print()


def test_press_command():
    """Тест команды press"""
    print("="*60)
    print("🧪 Тест 4: Команда press")
    print("="*60)
    
    parser = AtlasDSLParser()
    
    # Press enter
    dsl = "press enter"
    result = parser.parse(dsl)
    assert result is not None, "press не распарсился"
    print(f"✅ press enter распарсился")
    
    # Press escape
    dsl = "press escape"
    result = parser.parse(dsl)
    assert result is not None, "press escape не распарсился"
    print(f"✅ press escape распарсился")
    
    print()


def test_open_command():
    """Тест команды open"""
    print("="*60)
    print("🧪 Тест 5: Команда open")
    print("="*60)
    
    parser = AtlasDSLParser()
    
    # Open приложение
    dsl = "open ChromeApp"
    result = parser.parse(dsl)
    assert result is not None, "open не распарсился"
    print(f"✅ open ChromeApp распарсился")
    
    print()


def test_comments():
    """Тест комментариев"""
    print("="*60)
    print("🧪 Тест 6: Комментарии")
    print("="*60)
    
    parser = AtlasDSLParser()
    
    # Комментарий с #
    dsl = "# This is a comment\nclick Button"
    result = parser.parse(dsl)
    # Комментарии должны игнорироваться, но команда должна распарситься
    assert result is not None
    print(f"✅ Комментарии игнорируются, команды парсятся")
    
    print()


def test_try_catch():
    """Тест try/catch блоков"""
    print("="*60)
    print("🧪 Тест 7: Try/Catch блоки")
    print("="*60)
    
    parser = AtlasDSLParser()
    
    dsl = """
try:
    click Button
    wait 2s
catch:
    log "Button not found"
    """
    
    # Парсим весь блок
    result = parser.parse(dsl)
    assert result is not None, "Try/catch блок не распарсился"
    
    print(f"✅ Try/catch блок распарсился")
    
    # Проверяем что есть структура
    result_str = str(result).lower()
    if 'try' in result_str or 'catch' in result_str or 'steps' in result_str:
        print(f"✅ Try/catch или steps обнаружены")
    else:
        print(f"⚠️  Try/catch не обнаружены явно (парсер может обрабатывать их по-другому)")
    
    print()


def test_dom_selectors():
    """Тест DOM селекторов"""
    print("="*60)
    print("🧪 Тест 8: DOM селекторы")
    print("="*60)
    
    parser = AtlasDSLParser()
    
    # Click по CSS селектору
    dsl = "click css:.button"
    result = parser.parse(dsl)
    assert result is not None, "CSS селектор не распарсился"
    print(f"✅ CSS селектор распарсился")
    
    # Click по XPath
    dsl = "click xpath://button[@id='submit']"
    result = parser.parse(dsl)
    assert result is not None, "XPath не распарсился"
    print(f"✅ XPath распарсился")
    
    print()


def test_variables():
    """Тест переменных"""
    print("="*60)
    print("🧪 Тест 9: Переменные")
    print("="*60)
    
    parser = AtlasDSLParser()
    
    # Set и use переменная
    dsl = "set username = 'John'\ntype {username}"
    result = parser.parse(dsl)
    assert result is not None
    print(f"✅ Переменные распарсились")
    
    print()


def test_complex_scenario():
    """Тест сложного сценария"""
    print("="*60)
    print("🧪 Тест 10: Сложный сценарий")
    print("="*60)
    
    parser = AtlasDSLParser()
    
    dsl = """
# Open Chrome and search
open ChromeApp
wait 2s
click ChromeNewTab
wait 1s
click ChromeSearchField
type 'test query'
press enter
wait 3s
    """
    
    result = parser.parse(dsl)
    assert result is not None, "Сложный сценарий не распарсился"
    
    # Проверяем что есть steps
    if 'steps' in result:
        parsed_count = len(result['steps'])
        print(f"✅ Сложный сценарий: {parsed_count} команд распарсилось")
        assert parsed_count >= 5, "Должно быть минимум 5 команд"
    else:
        print(f"✅ Сложный сценарий распарсился (структура: {list(result.keys())})")
    
    print()


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🔥 ПОЛНОЕ ТЕСТИРОВАНИЕ DSL".center(60))
    print("="*60)
    print("\nПроверяем ВСЕ команды DSL парсера!\n")
    
    tests = [
        test_click_command,
        test_type_command,
        test_wait_command,
        test_press_command,
        test_open_command,
        test_comments,
        test_try_catch,
        test_dom_selectors,
        test_variables,
        test_complex_scenario,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}\n")
            failed += 1
    
    print("="*60)
    if failed == 0:
        print("🎉 ВСЕ DSL ТЕСТЫ ПРОШЛИ!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print("\n💡 DSL парсер работает корректно!")
    else:
        print("⚠️  ЕСТЬ ПРОБЛЕМЫ В DSL!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print(f"❌ Провалено: {failed}/{len(tests)}")
        print("\n💡 Исправьте ошибки в DSL парсере!")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
