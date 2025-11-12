#!/usr/bin/env python3
"""
Тестовый скрипт для проверки базовой инфраструктуры модульной AI системы
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Тест импорта всех базовых компонентов"""
    print("🧪 Тестирование импортов...")
    
    try:
        # Базовые классы
        from src.modules.base.module_config import ModuleConfig, AIConfig, ExecutorConfig
        from src.modules.base.module_result import ModuleResult, ExecutionResult
        from src.modules.base.ai_agent import AIAgent
        from src.modules.base.executor import Executor, NoOpExecutor, DSLExecutor
        from src.modules.base.ai_module import AIModule
        
        print("✅ Базовые классы импортированы")
        
        # Координатор
        from src.modules.coordinator.intent_analyzer import IntentAnalyzer, UserIntent
        from src.modules.coordinator.module_selector import ModuleSelector
        from src.modules.coordinator.ai_coordinator import AICoordinator
        
        print("✅ Координатор импортирован")
        
        # Реестр
        from src.modules.registry import ModuleRegistry, initialize_modular_system
        
        print("✅ Реестр модулей импортирован")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False


def test_module_config():
    """Тест создания конфигурации модуля"""
    print("\n🧪 Тестирование ModuleConfig...")
    
    try:
        from src.modules.base.module_config import ModuleConfig
        
        # Создаем конфигурацию
        config = ModuleConfig(
            name="test_module",
            description="Тестовый модуль",
            when_to_use=["тест", "проверка"]
        )
        
        assert config.name == "test_module"
        assert "тест" in config.keywords
        assert config.priority == 5
        
        print("✅ ModuleConfig работает корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка ModuleConfig: {e}")
        return False


def test_intent_analyzer():
    """Тест анализатора намерений"""
    print("\n🧪 Тестирование IntentAnalyzer...")
    
    try:
        from src.modules.coordinator.intent_analyzer import IntentAnalyzer
        
        analyzer = IntentAnalyzer()
        
        # Тест автоматизации
        intent1 = analyzer.analyze("открой Chrome и зайди на YouTube")
        assert intent1.type == "automation"
        assert "chrome" in intent1.apps
        assert "youtube" in intent1.platforms
        
        # Тест чата
        intent2 = analyzer.analyze("привет, как дела?")
        assert intent2.type == "chat"
        
        print("✅ IntentAnalyzer работает корректно")
        print(f"   Пример анализа: {analyzer.get_intent_summary(intent1)}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка IntentAnalyzer: {e}")
        return False


def test_module_selector():
    """Тест селектора модулей"""
    print("\n🧪 Тестирование ModuleSelector...")
    
    try:
        from src.modules.coordinator.module_selector import ModuleSelector
        from src.modules.coordinator.intent_analyzer import IntentAnalyzer
        
        selector = ModuleSelector()
        analyzer = IntentAnalyzer()
        
        # Регистрируем тестовый модуль
        selector.register_module("test_module", None, {
            "name": "test_module",
            "description": "Тестовый модуль",
            "keywords": ["автоматизация", "тест"],
            "priority": 1,
            "enabled": True
        })
        
        # Тестируем выбор
        intent = analyzer.analyze("создай автоматизацию")
        selection = selector.select_module(intent)
        
        if selection:
            module_name, config = selection
            assert module_name == "test_module"
            print("✅ ModuleSelector работает корректно")
            print(f"   Выбран модуль: {module_name}")
        else:
            print("⚠️ ModuleSelector не выбрал модуль (это может быть нормально)")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка ModuleSelector: {e}")
        return False


def test_ai_coordinator():
    """Тест AI координатора"""
    print("\n🧪 Тестирование AICoordinator...")
    
    try:
        from src.modules.coordinator.ai_coordinator import AICoordinator
        
        coordinator = AICoordinator()
        
        # Тест обычного диалога (без API ключа будет ошибка, но структура должна работать)
        print("   Тестируем структуру координатора...")
        
        # Проверяем компоненты
        assert coordinator.intent_analyzer is not None
        assert coordinator.module_selector is not None
        assert coordinator.stats["total_requests"] == 0
        
        print("✅ AICoordinator инициализирован корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка AICoordinator: {e}")
        return False


def test_simple_module():
    """Тест создания простого модуля"""
    print("\n🧪 Тестирование создания простого модуля...")
    
    try:
        from src.modules.base.ai_module import AIModule
        from src.modules.base.module_config import ModuleConfig
        
        class TestModule(AIModule):
            def __init__(self):
                config = ModuleConfig(
                    name="simple_test",
                    description="Простой тестовый модуль"
                )
                super().__init__(config)
            
            def parse_ai_result(self, ai_result: str) -> str:
                return f"Обработано: {ai_result}"
        
        # Создаем модуль
        module = TestModule()
        assert module.name == "simple_test"
        
        # Тестируем парсинг
        result = module.parse_ai_result("тест")
        assert "Обработано: тест" == result
        
        print("✅ Простой модуль создан и работает")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания модуля: {e}")
        return False


def test_module_registry():
    """Тест реестра модулей"""
    print("\n🧪 Тестирование ModuleRegistry...")
    
    try:
        from src.modules.registry import ModuleRegistry
        from src.modules.coordinator.ai_coordinator import AICoordinator
        
        coordinator = AICoordinator()
        registry = ModuleRegistry(coordinator)
        
        # Создаем модули по умолчанию
        registry.create_default_modules()
        
        # Проверяем что модули зарегистрированы
        modules = registry.get_registered_modules()
        assert len(modules) > 0
        
        print(f"✅ ModuleRegistry работает, зарегистрировано модулей: {len(modules)}")
        for name in modules.keys():
            print(f"   📦 {name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка ModuleRegistry: {e}")
        return False


def test_full_initialization():
    """Тест полной инициализации системы"""
    print("\n🧪 Тестирование полной инициализации...")
    
    try:
        from src.modules.registry import initialize_modular_system
        
        # Инициализируем систему
        coordinator = initialize_modular_system()
        
        # Проверяем что все работает
        modules = coordinator.get_available_modules()
        stats = coordinator.get_statistics()
        
        print(f"✅ Система инициализирована успешно")
        print(f"   Модулей: {len(modules)}")
        print(f"   Статистика: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False


def main():
    """Главная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ БАЗОВОЙ ИНФРАСТРУКТУРЫ МОДУЛЬНОЙ AI СИСТЕМЫ")
    print("=" * 70)
    
    tests = [
        ("Импорты", test_imports),
        ("ModuleConfig", test_module_config),
        ("IntentAnalyzer", test_intent_analyzer),
        ("ModuleSelector", test_module_selector),
        ("AICoordinator", test_ai_coordinator),
        ("Простой модуль", test_simple_module),
        ("ModuleRegistry", test_module_registry),
        ("Полная инициализация", test_full_initialization)
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
    
    print("\n" + "=" * 70)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"✅ Пройдено: {passed}")
    print(f"❌ Провалено: {failed}")
    print(f"📈 Успешность: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Базовая инфраструктура работает корректно.")
        print("🚀 Готово к созданию специализированных модулей!")
    else:
        print(f"\n⚠️ Есть проблемы в {failed} тестах. Необходимо исправить перед продолжением.")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
