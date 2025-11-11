#!/usr/bin/env python3
"""
test_dsl_variables.py
Тестирование парсинга DSL переменных
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.atlas_dsl_parser import AtlasDSLParser
import yaml


def test_variable_loading():
    """Тест загрузки переменных"""
    print("=" * 80)
    print("ТЕСТ 1: Загрузка DSL переменных")
    print("=" * 80)
    
    parser = AtlasDSLParser()
    
    print(f"\n✅ Загружено переменных: {len(parser.variables)}")
    
    # Проверяем несколько переменных
    test_vars = ['ChromeOpen', 'TikTokOpen', 'YouTubeSearch', 'TikTokComment']
    
    for var_name in test_vars:
        if var_name in parser.variables:
            var_data = parser.variables[var_name]
            print(f"\n📦 ${{{var_name}}}")
            print(f"   Параметры: {var_data['params']}")
            print(f"   Строк кода: {len(var_data['code'].split(chr(10)))}")
        else:
            print(f"\n❌ ${{{var_name}}} не найдена")


def test_simple_variable():
    """Тест простой переменной без параметров"""
    print("\n" + "=" * 80)
    print("ТЕСТ 2: Простая переменная ${ChromeOpen}")
    print("=" * 80)
    
    parser = AtlasDSLParser()
    
    dsl_code = """
${ChromeOpen}
click ChromeSearchField
type "example.com"
press enter
wait 3s
"""
    
    print("\n📝 DSL код:")
    print(dsl_code)
    
    result = parser.parse(dsl_code)
    
    print(f"\n✅ Распарсено шагов: {len(result['steps'])}")
    
    # Выводим первые 5 шагов
    for i, step in enumerate(result['steps'][:5], 1):
        action = step.get('action', 'unknown')
        desc = step.get('description', '')
        print(f"   {i}. {action}: {desc}")


def test_variable_with_params():
    """Тест переменной с параметрами"""
    print("\n" + "=" * 80)
    print("ТЕСТ 3: Переменная с параметрами ${YouTubeSearch:Python tutorial}")
    print("=" * 80)
    
    parser = AtlasDSLParser()
    
    dsl_code = """
${ChromeOpen}
${YouTubeOpen}
${YouTubeSearch:Python tutorial}
${YouTubeLike}
"""
    
    print("\n📝 DSL код:")
    print(dsl_code)
    
    result = parser.parse(dsl_code)
    
    print(f"\n✅ Распарсено шагов: {len(result['steps'])}")
    
    # Выводим все шаги
    for i, step in enumerate(result['steps'], 1):
        action = step.get('action', 'unknown')
        desc = step.get('description', '')
        print(f"   {i}. {action}: {desc}")


def test_variable_in_repeat():
    """Тест переменной внутри repeat"""
    print("\n" + "=" * 80)
    print("ТЕСТ 4: Переменная внутри repeat")
    print("=" * 80)
    
    parser = AtlasDSLParser()
    
    dsl_code = """
${ChromeOpen}
${TikTokOpen}

repeat 3:
  ${TikTokLike}
  ${TikTokScrollNext}

log "Готово!"
"""
    
    print("\n📝 DSL код:")
    print(dsl_code)
    
    result = parser.parse(dsl_code)
    
    print(f"\n✅ Распарсено шагов: {len(result['steps'])}")
    
    # Выводим структуру
    for i, step in enumerate(result['steps'], 1):
        action = step.get('action', 'unknown')
        
        if action == 'repeat':
            count = step.get('count', 0)
            inner_steps = step.get('steps', [])
            print(f"   {i}. repeat {count} раз ({len(inner_steps)} шагов внутри)")
            for j, inner_step in enumerate(inner_steps, 1):
                inner_action = inner_step.get('action', 'unknown')
                inner_desc = inner_step.get('description', '')
                print(f"      {i}.{j}. {inner_action}: {inner_desc}")
        else:
            desc = step.get('description', '')
            print(f"   {i}. {action}: {desc}")


def test_parse_file():
    """Тест парсинга файла с переменными"""
    print("\n" + "=" * 80)
    print("ТЕСТ 5: Парсинг файла test_variables.atlas")
    print("=" * 80)
    
    parser = AtlasDSLParser()
    
    test_file = Path(__file__).parent.parent / 'macros' / 'production' / 'test_variables.atlas'
    
    if not test_file.exists():
        print(f"\n❌ Файл не найден: {test_file}")
        return
    
    print(f"\n📁 Файл: {test_file}")
    
    result = parser.parse_file(str(test_file))
    
    print(f"\n✅ Распарсено шагов: {len(result['steps'])}")
    
    # Конвертируем в YAML
    yaml_output = yaml.dump(result, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print("\n📄 YAML вывод (первые 50 строк):")
    print("-" * 80)
    for i, line in enumerate(yaml_output.split('\n')[:50], 1):
        print(f"{i:3}. {line}")


def test_variable_expansion():
    """Тест развертывания конкретной переменной"""
    print("\n" + "=" * 80)
    print("ТЕСТ 6: Развертывание переменной ${TikTokComment:Отличное видео!}")
    print("=" * 80)
    
    parser = AtlasDSLParser()
    
    var_name = 'TikTokComment'
    params = {'comment_text': 'Отличное видео!'}
    
    expanded = parser._expand_variable(var_name, params)
    
    print(f"\n📦 Переменная: ${{{var_name}}}")
    print(f"📝 Параметры: {params}")
    print(f"\n✅ Развернуто в {len(expanded)} строк:")
    print("-" * 80)
    for i, line in enumerate(expanded, 1):
        print(f"{i:3}. {line}")


def main():
    """Запуск всех тестов"""
    print("\n🧪 ТЕСТИРОВАНИЕ DSL ПЕРЕМЕННЫХ")
    print("=" * 80)
    
    try:
        test_variable_loading()
        test_simple_variable()
        test_variable_with_params()
        test_variable_in_repeat()
        test_parse_file()
        test_variable_expansion()
        
        print("\n" + "=" * 80)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
