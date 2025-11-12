#!/usr/bin/env python3
"""
Базовый тест модуля sequence_generator без AI API
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_module_structure():
    """Тест структуры модуля"""
    print("🧪 Тестирование структуры модуля...")
    
    expected_files = [
        "src/modules/sequence_generator/__init__.py",
        "src/modules/sequence_generator/module.py",
        "src/modules/sequence_generator/config.yaml",
        "src/modules/sequence_generator/prompts/base_prompt.txt",
        "src/modules/sequence_generator/prompts/context_template.txt"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in expected_files:
        full_path = project_root / file_path
        if full_path.exists():
            existing_files.append(file_path)
        else:
            missing_files.append(file_path)
    
    print(f"✅ Существующие файлы: {len(existing_files)}")
    for file_path in existing_files:
        print(f"   📄 {file_path}")
    
    if missing_files:
        print(f"❌ Отсутствующие файлы: {len(missing_files)}")
        for file_path in missing_files:
            print(f"   ❌ {file_path}")
        return False
    
    print("✅ Структура модуля корректна")
    return True

def test_config_loading():
    """Тест загрузки конфигурации"""
    print("\n🧪 Тестирование загрузки конфигурации...")
    
    try:
        import yaml
        
        config_path = project_root / "src/modules/sequence_generator/config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Проверяем ключевые поля
        required_fields = ["name", "description", "keywords", "priority"]
        for field in required_fields:
            assert field in config, f"Отсутствует поле {field}"
        
        print("✅ Конфигурация загружена корректно")
        print(f"   Имя: {config['name']}")
        print(f"   Приоритет: {config['priority']}")
        print(f"   Ключевых слов: {len(config['keywords'])}")
        
        return True, config
        
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False, None

def test_prompt_files():
    """Тест файлов промптов"""
    print("\n🧪 Тестирование файлов промптов...")
    
    try:
        prompts_dir = project_root / "src/modules/sequence_generator/prompts"
        
        # Проверяем базовый промпт
        base_prompt_path = prompts_dir / "base_prompt.txt"
        with open(base_prompt_path, 'r', encoding='utf-8') as f:
            base_prompt = f.read()
        
        # Проверяем что промпт содержит нужные элементы
        required_elements = [
            "{user_input}",
            "{available_templates}",
            "DSL КОМАНДЫ",
            "ФОРМАТ ОТВЕТА"
        ]
        
        for element in required_elements:
            assert element in base_prompt, f"Отсутствует элемент {element}"
        
        # Проверяем шаблон контекста
        context_template_path = prompts_dir / "context_template.txt"
        with open(context_template_path, 'r', encoding='utf-8') as f:
            context_template = f.read()
        
        print("✅ Файлы промптов корректны")
        print(f"   Базовый промпт: {len(base_prompt)} символов")
        print(f"   Шаблон контекста: {len(context_template)} символов")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки промптов: {e}")
        return False

def test_module_class_structure():
    """Тест структуры класса модуля"""
    print("\n🧪 Тестирование структуры класса...")
    
    try:
        from src.modules.sequence_generator.module import SequenceGeneratorModule
        
        # Проверяем что класс имеет нужные методы
        required_methods = [
            '__init__',
            'get_context_resources',
            'build_prompt',
            'parse_ai_result',
            '_save_generated_macro'
        ]
        
        for method in required_methods:
            assert hasattr(SequenceGeneratorModule, method), f"Отсутствует метод {method}"
        
        print("✅ Структура класса корректна")
        print(f"   Методов проверено: {len(required_methods)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки структуры класса: {e}")
        return False

def test_ai_result_parsing():
    """Тест парсинга AI результата (без инициализации модуля)"""
    print("\n🧪 Тестирование парсинга AI результата...")
    
    try:
        # Импортируем класс
        from src.modules.sequence_generator.module import SequenceGeneratorModule
        
        # Создаем временный экземпляр для тестирования метода
        # Мокаем AI агент чтобы избежать ошибки с API ключом
        import unittest.mock
        
        with unittest.mock.patch('src.modules.base.ai_agent.AIAgent'):
            module = SequenceGeneratorModule()
        
        # Тестовый AI ответ
        mock_ai_response = """
НАЗВАНИЕ: Открыть YouTube в Chrome

DSL КОД:
```atlas
# Открыть Chrome и перейти на YouTube
open ChromeApp
wait 2s
click ChromeNewTab
wait 1s
type "youtube.com"
press enter
wait 3s
```

ОПИСАНИЕ: Макрос для открытия YouTube в новой вкладке Chrome
"""
        
        parsed = module.parse_ai_result(mock_ai_response)
        
        # Проверяем парсинг
        assert "name" in parsed
        assert "dsl_code" in parsed
        assert "description" in parsed
        assert "open ChromeApp" in parsed["dsl_code"]
        assert "YouTube" in parsed["name"]
        
        print("✅ Парсинг AI результата работает")
        print(f"   Название: {parsed['name']}")
        print(f"   DSL код: {len(parsed['dsl_code'])} символов")
        print(f"   Описание: {parsed['description'][:50]}...")
        
        return True, parsed
        
    except Exception as e:
        print(f"❌ Ошибка парсинга AI результата: {e}")
        return False, None

def test_macro_saving_logic(parsed_result):
    """Тест логики сохранения макроса"""
    print("\n🧪 Тестирование логики сохранения макроса...")
    
    try:
        from src.modules.sequence_generator.module import SequenceGeneratorModule
        import unittest.mock
        
        with unittest.mock.patch('src.modules.base.ai_agent.AIAgent'):
            module = SequenceGeneratorModule()
        
        # Тестируем сохранение
        saved_file = module._save_generated_macro(
            parsed_result["name"],
            parsed_result["dsl_code"],
            parsed_result["description"]
        )
        
        if saved_file and Path(saved_file).exists():
            print("✅ Макрос успешно сохранен")
            print(f"   Файл: {Path(saved_file).name}")
            
            # Проверяем содержимое
            with open(saved_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert "# Macro Atlas File" in content
            assert "open ChromeApp" in content
            assert "Generated by Modular AI System" in content
            
            print(f"   Размер файла: {len(content)} символов")
            print("   Формат .atlas корректен")
            
            return True
        else:
            print("❌ Файл не был создан")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка сохранения макроса: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🚀 БАЗОВОЕ ТЕСТИРОВАНИЕ МОДУЛЯ SEQUENCE_GENERATOR")
    print("(без AI API для проверки структуры)")
    print("=" * 60)
    
    tests = [
        ("Структура модуля", test_module_structure),
        ("Загрузка конфигурации", test_config_loading),
        ("Файлы промптов", test_prompt_files),
        ("Структура класса", test_module_class_structure),
        ("Парсинг AI результата", test_ai_result_parsing),
        ("Логика сохранения", lambda: test_macro_saving_logic(parsed) if 'parsed' in locals() else False)
    ]
    
    passed = 0
    failed = 0
    config = None
    parsed = None
    
    for test_name, test_func in tests:
        try:
            if test_name == "Загрузка конфигурации":
                success, config = test_func()
            elif test_name == "Парсинг AI результата":
                success, parsed = test_func()
            elif test_name == "Логика сохранения":
                success = test_func() if parsed else False
            else:
                success = test_func()
            
            if success:
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"✅ Пройдено: {passed}")
    print(f"❌ Провалено: {failed}")
    print(f"📈 Успешность: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ВСЕ БАЗОВЫЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("✅ Структура модуля sequence_generator корректна")
        print("🔧 Логика парсинга и сохранения работает")
        print("🚀 Готов к тестированию с реальным AI API")
        print("\n💡 Для полного тестирования:")
        print("   1. Добавьте GEMINI_API_KEY в .env файл")
        print("   2. Запустите test_sequence_generator_module.py")
    else:
        print(f"\n⚠️ Есть проблемы в {failed} тестах.")
        print("🔧 Необходимо исправить перед продолжением")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
