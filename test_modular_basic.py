#!/usr/bin/env python3
"""
Тестовый скрипт для проверки базовой структуры без AI API
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_structure():
    """Тест базовой структуры без AI"""
    print("🧪 Тестирование базовой структуры...")
    
    try:
        # Импорты
        from src.modules.base.module_config import ModuleConfig
        from src.modules.base.module_result import ModuleResult
        from src.modules.coordinator.intent_analyzer import IntentAnalyzer
        from src.modules.coordinator.module_selector import ModuleSelector
        
        # Тест конфигурации
        config = ModuleConfig(
            name="test_module",
            description="Тестовый модуль",
            when_to_use=["тест", "проверка"]
        )
        
        # Тест результата
        result = ModuleResult(success=True, data="test data")
        result.add_log("Тестовое сообщение")
        
        # Тест анализатора намерений
        analyzer = IntentAnalyzer()
        intent = analyzer.analyze("открой Chrome и зайди на YouTube")
        
        # Тест селектора модулей
        selector = ModuleSelector()
        selector.register_module("test_module", None, {
            "name": "test_module",
            "description": "Тестовый модуль",
            "keywords": ["автоматизация", "тест"],
            "priority": 1,
            "enabled": True
        })
        
        print("✅ Базовая структура работает корректно")
        print(f"   Конфигурация: {config.name}")
        print(f"   Результат: {result.success}")
        print(f"   Анализ намерений: {intent.type}")
        print(f"   Модулей в селекторе: {len(selector.get_all_modules())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка базовой структуры: {e}")
        return False


def test_mock_module():
    """Тест модуля-заглушки без AI"""
    print("\n🧪 Тестирование модуля-заглушки...")
    
    try:
        from src.modules.base.module_config import ModuleConfig
        from src.modules.base.module_result import ModuleResult
        
        class MockModule:
            """Простая заглушка модуля без AI"""
            
            def __init__(self):
                self.config = ModuleConfig(
                    name="mock_module",
                    description="Модуль-заглушка для тестирования"
                )
                self.name = self.config.name
            
            def execute(self, user_input: str, context=None) -> ModuleResult:
                """Простое выполнение без AI"""
                return ModuleResult(
                    success=True,
                    data=f"Mock обработка: {user_input}",
                    execution_time=0.1
                )
        
        # Создаем и тестируем модуль
        module = MockModule()
        result = module.execute("тестовый ввод")
        
        assert result.success
        assert "Mock обработка" in result.data
        
        print("✅ Модуль-заглушка работает корректно")
        print(f"   Результат: {result.data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка модуля-заглушки: {e}")
        return False


def test_coordinator_structure():
    """Тест структуры координатора без AI"""
    print("\n🧪 Тестирование структуры координатора...")
    
    try:
        from src.modules.coordinator.intent_analyzer import IntentAnalyzer
        from src.modules.coordinator.module_selector import ModuleSelector
        
        # Создаем компоненты
        analyzer = IntentAnalyzer()
        selector = ModuleSelector()
        
        # Тестируем анализ намерений
        intent = analyzer.analyze("создай автоматизацию для Chrome")
        
        # Регистрируем тестовый модуль
        selector.register_module("automation_module", None, {
            "name": "automation_module",
            "description": "Модуль автоматизации",
            "keywords": ["автоматизация", "chrome", "создай"],
            "priority": 1,
            "enabled": True
        })
        
        # Тестируем выбор модуля
        selection = selector.select_module(intent)
        
        print("✅ Структура координатора работает")
        print(f"   Анализ: {analyzer.get_intent_summary(intent)}")
        
        if selection:
            module_name, config = selection
            print(f"   Выбран модуль: {module_name}")
        else:
            print("   Модуль не выбран")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка структуры координатора: {e}")
        return False


def test_file_structure():
    """Тест структуры файлов"""
    print("\n🧪 Проверка структуры файлов...")
    
    expected_files = [
        "src/modules/__init__.py",
        "src/modules/base/__init__.py",
        "src/modules/base/ai_module.py",
        "src/modules/base/module_config.py",
        "src/modules/base/ai_agent.py",
        "src/modules/base/executor.py",
        "src/modules/base/module_result.py",
        "src/modules/coordinator/__init__.py",
        "src/modules/coordinator/ai_coordinator.py",
        "src/modules/coordinator/intent_analyzer.py",
        "src/modules/coordinator/module_selector.py",
        "src/modules/registry.py"
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
    
    print("✅ Все файлы на месте")
    return True


def main():
    """Главная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ БАЗОВОЙ СТРУКТУРЫ МОДУЛЬНОЙ СИСТЕМЫ")
    print("(без AI API для проверки архитектуры)")
    print("=" * 60)
    
    tests = [
        ("Структура файлов", test_file_structure),
        ("Базовая структура", test_basic_structure),
        ("Модуль-заглушка", test_mock_module),
        ("Структура координатора", test_coordinator_structure)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
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
        print("✅ Базовая архитектура модульной системы работает корректно")
        print("🔧 Структура готова для добавления AI функциональности")
        print("🚀 Можно переходить к созданию специализированных модулей")
    else:
        print(f"\n⚠️ Есть проблемы в {failed} тестах.")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
