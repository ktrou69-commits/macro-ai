#!/usr/bin/env python3
"""
test_variable_generator.py
Тестирование AI генератора переменных
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai.variable_generator import AIVariableGenerator
from src.core.atlas_dsl_parser import AtlasDSLParser


def test_create_and_use_variable():
    """Тест создания переменной и её использования в парсере"""
    print("=" * 80)
    print("ТЕСТ: Создание переменной и использование в парсере")
    print("=" * 80)
    
    project_root = Path(__file__).parent.parent
    
    # 1. Создаем генератор
    generator = AIVariableGenerator(project_root)
    
    # 2. Создаем переменную
    request = "Открыть TikTok и поставить 3 лайка"
    code = """open ChromeApp
wait 2s
click ChromeNewTab
wait 1s
click ChromeSearchField
type "tiktok.com"
press enter
wait 5s
repeat 3:
  click Like
  wait 1.5s
  scroll down
  wait 2s"""
    
    print("\n📝 Создание переменной...")
    variable = generator.generate_variable(request, code)
    
    print(f"✅ Переменная создана: ${{{variable['name']}}}")
    print(f"   Описание: {variable['description']}")
    
    # 3. Сохраняем переменную
    print("\n💾 Сохранение переменной...")
    if generator.save_variable(variable):
        print("✅ Переменная сохранена")
    
    # 4. Создаем парсер (он должен загрузить нашу переменную)
    print("\n🔄 Создание парсера...")
    parser = AtlasDSLParser()
    
    if variable['name'] in parser.variables:
        print(f"✅ Переменная ${{{variable['name']}}} загружена в парсер!")
    else:
        print(f"❌ Переменная ${{{variable['name']}}} НЕ загружена в парсер")
        return False
    
    # 5. Используем переменную в DSL коде
    print("\n📄 Использование переменной в DSL коде...")
    dsl_code = f"""
${{{variable['name']}}}
log "Готово!"
"""
    
    result = parser.parse(dsl_code)
    
    print(f"✅ Распарсено шагов: {len(result['steps'])}")
    
    # Проверяем что переменная развернулась
    if len(result['steps']) > 1:
        print("✅ Переменная успешно развернулась в код!")
        return True
    else:
        print("❌ Переменная НЕ развернулась")
        return False


def test_variable_with_parameter():
    """Тест переменной с параметром"""
    print("\n" + "=" * 80)
    print("ТЕСТ: Переменная с параметром")
    print("=" * 80)
    
    project_root = Path(__file__).parent.parent
    generator = AIVariableGenerator(project_root)
    
    # Создаем переменную с параметром
    request = "Найти видео на YouTube"
    code = """click Chrome-YouTube-SearchField
wait 1s
type "{search_query}"
press enter
wait 3s
click Chrome-YouTube-VideoFirst
wait 5s"""
    
    print("\n📝 Создание переменной с параметром...")
    variable = generator.generate_variable(request, code)
    
    print(f"✅ Переменная создана: ${{{variable['name']}}}")
    
    # Сохраняем
    generator.save_variable(variable)
    
    # Используем с параметром
    parser = AtlasDSLParser()
    
    dsl_code = f"""
${{{variable['name']}:Python tutorial}}
"""
    
    result = parser.parse(dsl_code)
    
    print(f"✅ Распарсено шагов: {len(result['steps'])}")
    
    # Проверяем что параметр подставился
    for step in result['steps']:
        if step.get('action') == 'type':
            text = step.get('text', '')
            if 'Python tutorial' in text:
                print(f"✅ Параметр подставлен: type \"{text}\"")
                return True
    
    print("❌ Параметр НЕ подставлен")
    return False


def test_list_and_info():
    """Тест списка переменных и получения информации"""
    print("\n" + "=" * 80)
    print("ТЕСТ: Список переменных и информация")
    print("=" * 80)
    
    project_root = Path(__file__).parent.parent
    generator = AIVariableGenerator(project_root)
    
    # Список переменных
    print("\n📋 Список пользовательских переменных:")
    variables = generator.list_variables()
    
    for var in variables:
        print(f"   - ${{{var}}}")
        
        # Получаем информацию
        info = generator.get_variable_info(var)
        if info:
            print(f"     Описание: {info['description']}")
            print(f"     Строк кода: {len(info['code'].split(chr(10)))}")
    
    print(f"\n✅ Всего переменных: {len(variables)}")
    return True


def main():
    """Запуск всех тестов"""
    print("\n🧪 ТЕСТИРОВАНИЕ AI VARIABLE GENERATOR")
    print("=" * 80)
    
    try:
        test1 = test_create_and_use_variable()
        test2 = test_variable_with_parameter()
        test3 = test_list_and_info()
        
        print("\n" + "=" * 80)
        if test1 and test2 and test3:
            print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        else:
            print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
