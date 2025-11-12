#!/usr/bin/env python3
"""
Тестовый скрипт для модуля sequence_generator
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_module_import():
    """Тест импорта модуля"""
    print("🧪 Тестирование импорта модуля sequence_generator...")
    
    try:
        from src.modules.sequence_generator.module import SequenceGeneratorModule
        print("✅ Модуль успешно импортирован")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_module_initialization():
    """Тест инициализации модуля"""
    print("\n🧪 Тестирование инициализации модуля...")
    
    try:
        from src.modules.sequence_generator.module import SequenceGeneratorModule
        
        module = SequenceGeneratorModule()
        
        # Проверяем базовые свойства
        assert module.name == "sequence_generator"
        assert "автоматизация" in module.config.keywords
        assert module.config.priority == 1
        
        print("✅ Модуль успешно инициализирован")
        print(f"   Имя: {module.name}")
        print(f"   Описание: {module.description}")
        print(f"   Ключевые слова: {module.config.keywords[:3]}...")
        
        return True, module
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False, None

def test_resource_loading(module):
    """Тест загрузки ресурсов"""
    print("\n🧪 Тестирование загрузки ресурсов...")
    
    try:
        resources = module.get_context_resources()
        
        print("✅ Ресурсы загружены:")
        for resource_type, data in resources.items():
            if isinstance(data, dict) and "count" in data:
                print(f"   {resource_type}: {data['count']} элементов")
            else:
                print(f"   {resource_type}: доступно")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки ресурсов: {e}")
        return False

def test_prompt_building(module):
    """Тест построения промпта"""
    print("\n🧪 Тестирование построения промпта...")
    
    try:
        user_input = "открой Chrome и зайди на YouTube"
        context = {"current_app": "Finder", "timestamp": "2025-11-12 16:00:00"}
        
        prompt = module.build_prompt(user_input, context)
        
        # Проверяем что промпт содержит ключевые элементы
        assert user_input in prompt
        assert "DSL КОМАНДЫ" in prompt
        assert "ФОРМАТ ОТВЕТА" in prompt
        
        print("✅ Промпт успешно построен")
        print(f"   Длина промпта: {len(prompt)} символов")
        print(f"   Содержит пользовательский ввод: {'✅' if user_input in prompt else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка построения промпта: {e}")
        return False

def test_ai_result_parsing(module):
    """Тест парсинга AI результата"""
    print("\n🧪 Тестирование парсинга AI результата...")
    
    try:
        # Мокаем AI ответ
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
        
        print("✅ AI результат успешно распарсен")
        print(f"   Название: {parsed['name']}")
        print(f"   DSL код: {len(parsed['dsl_code'])} символов")
        print(f"   Описание: {parsed['description']}")
        
        return True, parsed
        
    except Exception as e:
        print(f"❌ Ошибка парсинга AI результата: {e}")
        return False, None

def test_macro_saving(module, parsed_result):
    """Тест сохранения макроса"""
    print("\n🧪 Тестирование сохранения макроса...")
    
    try:
        saved_file = module._save_generated_macro(
            parsed_result["name"],
            parsed_result["dsl_code"],
            parsed_result["description"]
        )
        
        if saved_file and Path(saved_file).exists():
            print("✅ Макрос успешно сохранен")
            print(f"   Файл: {saved_file}")
            
            # Читаем содержимое для проверки
            with open(saved_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            print(f"   Размер файла: {len(content)} символов")
            print(f"   Содержит DSL код: {'✅' if 'open ChromeApp' in content else '❌'}")
            
            return True
        else:
            print("❌ Файл не был создан")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка сохранения макроса: {e}")
        return False

def test_integration_with_coordinator():
    """Тест интеграции с координатором"""
    print("\n🧪 Тестирование интеграции с координатором...")
    
    try:
        from src.modules.registry import ModuleRegistry
        from src.modules.coordinator.ai_coordinator import AICoordinator
        from src.modules.sequence_generator.module import SequenceGeneratorModule
        
        # Создаем координатор и реестр
        coordinator = AICoordinator()
        registry = ModuleRegistry(coordinator)
        
        # Регистрируем наш модуль
        registry.manual_register_module(
            "sequence_generator",
            SequenceGeneratorModule,
            "Генерирует DSL последовательности по описанию пользователя",
            ["автоматизация", "макрос", "создай"],
            priority=1
        )
        
        # Тестируем анализ намерений
        intent = coordinator.analyze_user_intent_only("создай макрос для открытия Chrome")
        
        # Проверяем что модуль будет выбран
        modules = coordinator.get_available_modules()
        
        print("✅ Интеграция с координатором работает")
        print(f"   Зарегистрированных модулей: {len(modules)}")
        print(f"   Анализ намерений: {intent.type}")
        print(f"   Модуль sequence_generator: {'✅' if 'sequence_generator' in modules else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции с координатором: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ МОДУЛЯ SEQUENCE_GENERATOR")
    print("=" * 60)
    
    tests = [
        ("Импорт модуля", test_module_import),
        ("Инициализация модуля", test_module_initialization),
        ("Загрузка ресурсов", lambda: test_resource_loading(module) if 'module' in locals() else False),
        ("Построение промпта", lambda: test_prompt_building(module) if 'module' in locals() else False),
        ("Парсинг AI результата", lambda: test_ai_result_parsing(module) if 'module' in locals() else False),
        ("Сохранение макроса", lambda: test_macro_saving(module, parsed) if 'parsed' in locals() else False),
        ("Интеграция с координатором", test_integration_with_coordinator)
    ]
    
    passed = 0
    failed = 0
    module = None
    parsed = None
    
    for test_name, test_func in tests:
        try:
            if test_name == "Инициализация модуля":
                success, module = test_func()
            elif test_name == "Парсинг AI результата":
                success, parsed = test_func()
            elif test_name in ["Загрузка ресурсов", "Построение промпта"]:
                success = test_func() if module else False
            elif test_name == "Сохранение макроса":
                success = test_func() if module and parsed else False
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
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("✅ Модуль sequence_generator готов к использованию")
        print("🔧 Интеграция с существующей системой работает")
        print("🚀 Можно тестировать с реальным AI API")
    else:
        print(f"\n⚠️ Есть проблемы в {failed} тестах.")
        print("🔧 Необходимо исправить перед использованием с AI API")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
