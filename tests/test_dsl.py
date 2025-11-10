#!/usr/bin/env python3
"""
test_dsl.py
Тестирование DSL парсера
"""

from atlas_dsl_parser import AtlasDSLParser
import yaml


def test_basic_commands():
    """Тест базовых команд"""
    print("\n" + "="*60)
    print("🧪 Тест 1: Базовые команды")
    print("="*60)
    
    dsl = """
# Базовые команды
open ChromeApp
click ChromeNewTab
type "Hello World"
press enter
wait 2s
scroll down
"""
    
    parser = AtlasDSLParser()
    result = parser.parse(dsl)
    
    print("\n📝 DSL:")
    print(dsl)
    
    print("\n📦 YAML:")
    print(yaml.dump(result, allow_unicode=True, default_flow_style=False))
    
    assert len(result['steps']) == 6
    assert result['steps'][0]['action'] == 'click'
    assert result['steps'][2]['action'] == 'type'
    assert result['steps'][4]['action'] == 'wait'
    
    print("✅ Тест пройден!")


def test_repeat():
    """Тест repeat"""
    print("\n" + "="*60)
    print("🧪 Тест 2: Repeat")
    print("="*60)
    
    dsl = """
repeat 5:
  click Button
  wait 1s
  scroll down
"""
    
    parser = AtlasDSLParser()
    result = parser.parse(dsl)
    
    print("\n📝 DSL:")
    print(dsl)
    
    print("\n📦 YAML:")
    print(yaml.dump(result, allow_unicode=True, default_flow_style=False))
    
    assert len(result['steps']) == 1
    assert result['steps'][0]['action'] == 'repeat'
    assert result['steps'][0]['times'] == 5
    assert len(result['steps'][0]['steps']) == 3
    
    print("✅ Тест пройден!")


def test_complex_workflow():
    """Тест сложного workflow"""
    print("\n" + "="*60)
    print("🧪 Тест 3: Сложный workflow")
    print("="*60)
    
    dsl = """
# TikTok Auto Like
open ChromeApp
wait 2.5s

click ChromeNewTab
wait 0.5s

click ChromeSearchField
type "tiktok.com"
press enter
wait 4s

repeat 10:
  click TikTok-Like
  wait 1.5s
  scroll down
  wait 2s
"""
    
    parser = AtlasDSLParser()
    result = parser.parse(dsl)
    
    print("\n📝 DSL:")
    print(dsl)
    
    print("\n📦 YAML:")
    yaml_str = yaml.dump(result, allow_unicode=True, default_flow_style=False)
    print(yaml_str)
    
    # Проверки
    assert len(result['steps']) > 0
    
    # Найти repeat
    repeat_step = None
    for step in result['steps']:
        if step['action'] == 'repeat':
            repeat_step = step
            break
    
    assert repeat_step is not None
    assert repeat_step['times'] == 10
    assert len(repeat_step['steps']) == 4
    
    print("✅ Тест пройден!")


def test_hotkeys():
    """Тест hotkeys"""
    print("\n" + "="*60)
    print("🧪 Тест 4: Hotkeys")
    print("="*60)
    
    dsl = """
hotkey command+t
hotkey command+w
hotkey command+shift+n
"""
    
    parser = AtlasDSLParser()
    result = parser.parse(dsl)
    
    print("\n📝 DSL:")
    print(dsl)
    
    print("\n📦 YAML:")
    print(yaml.dump(result, allow_unicode=True, default_flow_style=False))
    
    assert len(result['steps']) == 3
    assert result['steps'][0]['action'] == 'hotkey'
    assert result['steps'][0]['keys'] == ['command', 't']
    assert result['steps'][2]['keys'] == ['command', 'shift', 'n']
    
    print("✅ Тест пройден!")


def test_coordinates():
    """Тест координат"""
    print("\n" + "="*60)
    print("🧪 Тест 5: Координаты")
    print("="*60)
    
    dsl = """
click (500, 300)
click (100, 200)
"""
    
    parser = AtlasDSLParser()
    result = parser.parse(dsl)
    
    print("\n📝 DSL:")
    print(dsl)
    
    print("\n📦 YAML:")
    print(yaml.dump(result, allow_unicode=True, default_flow_style=False))
    
    assert len(result['steps']) == 2
    assert result['steps'][0]['action'] == 'click'
    assert result['steps'][0]['position'] == 'absolute'
    assert result['steps'][0]['x'] == 500
    assert result['steps'][0]['y'] == 300
    
    print("✅ Тест пройден!")


def test_file_parsing():
    """Тест парсинга файла"""
    print("\n" + "="*60)
    print("🧪 Тест 6: Парсинг файла")
    print("="*60)
    
    parser = AtlasDSLParser()
    
    # Проверяем существующие примеры
    example_files = [
        'macros/examples/advanced/tiktok_auto_like.atlas',
        'macros/examples/advanced/chrome_quick_search.atlas',
        'macros/examples/advanced/tiktok_comment.atlas'
    ]
    
    for filepath in example_files:
        try:
            print(f"\n📄 Парсинг: {filepath}")
            result = parser.parse_file(filepath)
            
            print(f"   ✅ Шагов: {len(result['steps'])}")
            print(f"   ✅ Имя: {result.get('name', 'N/A')}")
            
        except FileNotFoundError:
            print(f"   ⚠️  Файл не найден: {filepath}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
    
    print("\n✅ Тест пройден!")


def main():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ DSL ПАРСЕРА")
    print("="*60)
    
    try:
        test_basic_commands()
        test_repeat()
        test_complex_workflow()
        test_hotkeys()
        test_coordinates()
        test_file_parsing()
        
        print("\n" + "="*60)
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ Тест провален: {e}")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
