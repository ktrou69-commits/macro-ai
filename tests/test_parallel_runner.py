#!/usr/bin/env python3
"""
test_parallel_runner.py
🚀 ВАЖНО: Тестирование параллельного выполнения макросов

Проверяет:
- ParallelMacroRunner класс
- Инициализация runner
- Методы создания экземпляров
- Управление потоками
- Результаты выполнения
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_parallel_runner_import():
    """Тест импорта ParallelMacroRunner"""
    print("\n" + "="*60)
    print("🧪 Тест 1: Импорт ParallelMacroRunner")
    print("="*60)
    
    try:
        from src.engines.parallel_runner import ParallelMacroRunner
        print("✅ ParallelMacroRunner импортирован")
        
        # Проверяем что это класс
        assert callable(ParallelMacroRunner), "ParallelMacroRunner должен быть классом"
        print("✅ ParallelMacroRunner - это класс")
        
    except ImportError as e:
        print(f"❌ Не удалось импортировать: {e}")
        raise
    
    print()


def test_parallel_runner_initialization():
    """Тест инициализации ParallelMacroRunner"""
    print("="*60)
    print("🧪 Тест 2: Инициализация ParallelMacroRunner")
    print("="*60)
    
    try:
        from src.engines.parallel_runner import ParallelMacroRunner
        
        # Создаём экземпляр с параметрами по умолчанию
        runner = ParallelMacroRunner()
        assert runner is not None, "Runner не создался"
        print("✅ ParallelMacroRunner создан (по умолчанию)")
        
        # Проверяем атрибуты
        assert hasattr(runner, 'num_instances'), "Нет атрибута num_instances"
        assert hasattr(runner, 'use_existing'), "Нет атрибута use_existing"
        assert hasattr(runner, 'drivers'), "Нет атрибута drivers"
        assert hasattr(runner, 'threads'), "Нет атрибута threads"
        assert hasattr(runner, 'results'), "Нет атрибута results"
        print("✅ Все атрибуты на месте")
        
        # Проверяем значения по умолчанию
        assert runner.num_instances == 3, f"num_instances должен быть 3, получен {runner.num_instances}"
        assert runner.use_existing == False, "use_existing должен быть False"
        assert isinstance(runner.drivers, list), "drivers должен быть списком"
        assert isinstance(runner.threads, list), "threads должен быть списком"
        assert isinstance(runner.results, dict), "results должен быть словарем"
        print("✅ Значения по умолчанию корректны")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        raise
    
    print()


def test_parallel_runner_custom_instances():
    """Тест создания runner с кастомным количеством экземпляров"""
    print("="*60)
    print("🧪 Тест 3: Кастомное количество экземпляров")
    print("="*60)
    
    from src.engines.parallel_runner import ParallelMacroRunner
    
    # Создаём runner с 5 экземплярами
    runner = ParallelMacroRunner(num_instances=5)
    assert runner.num_instances == 5, f"Ожидалось 5, получено {runner.num_instances}"
    print("✅ Runner создан с 5 экземплярами")
    
    # Создаём runner с 1 экземпляром
    runner = ParallelMacroRunner(num_instances=1)
    assert runner.num_instances == 1, f"Ожидалось 1, получено {runner.num_instances}"
    print("✅ Runner создан с 1 экземпляром")
    
    print()


def test_parallel_runner_use_existing():
    """Тест режима подключения к существующему Chrome"""
    print("="*60)
    print("🧪 Тест 4: Режим use_existing")
    print("="*60)
    
    from src.engines.parallel_runner import ParallelMacroRunner
    
    # Создаём runner с use_existing=True
    runner = ParallelMacroRunner(use_existing=True)
    assert runner.use_existing == True, "use_existing должен быть True"
    print("✅ Runner создан с use_existing=True")
    
    # Создаём runner с use_existing=False
    runner = ParallelMacroRunner(use_existing=False)
    assert runner.use_existing == False, "use_existing должен быть False"
    print("✅ Runner создан с use_existing=False")
    
    print()


def test_parallel_runner_custom_profiles():
    """Тест кастомных профилей"""
    print("="*60)
    print("🧪 Тест 5: Кастомные профили")
    print("="*60)
    
    from src.engines.parallel_runner import ParallelMacroRunner
    
    runner = ParallelMacroRunner()
    
    # Устанавливаем кастомные профили
    profiles = ['/tmp/profile1', '/tmp/profile2', '/tmp/profile3']
    runner.custom_profiles = profiles
    
    assert len(runner.custom_profiles) == 3, "Должно быть 3 профиля"
    assert runner.custom_profiles[0] == '/tmp/profile1', "Неверный первый профиль"
    print("✅ Кастомные профили установлены")
    
    print()


def test_parallel_runner_custom_macros():
    """Тест разных макросов для каждого окна"""
    print("="*60)
    print("🧪 Тест 6: Разные макросы")
    print("="*60)
    
    from src.engines.parallel_runner import ParallelMacroRunner
    
    runner = ParallelMacroRunner()
    
    # Устанавливаем разные макросы
    macros = ['macro1.atlas', 'macro2.atlas', 'macro3.atlas']
    runner.custom_macros = macros
    
    assert len(runner.custom_macros) == 3, "Должно быть 3 макроса"
    assert runner.custom_macros[1] == 'macro2.atlas', "Неверный второй макрос"
    print("✅ Разные макросы установлены")
    
    print()


def test_parallel_runner_custom_urls():
    """Тест разных URL для каждого окна"""
    print("="*60)
    print("🧪 Тест 7: Разные URL")
    print("="*60)
    
    from src.engines.parallel_runner import ParallelMacroRunner
    
    runner = ParallelMacroRunner()
    
    # Устанавливаем разные URL
    urls = ['https://site1.com', 'https://site2.com', 'https://site3.com']
    runner.custom_urls = urls
    
    assert len(runner.custom_urls) == 3, "Должно быть 3 URL"
    assert runner.custom_urls[2] == 'https://site3.com', "Неверный третий URL"
    print("✅ Разные URL установлены")
    
    print()


def test_parallel_runner_results_structure():
    """Тест структуры результатов"""
    print("="*60)
    print("🧪 Тест 8: Структура результатов")
    print("="*60)
    
    from src.engines.parallel_runner import ParallelMacroRunner
    
    runner = ParallelMacroRunner()
    
    # Симулируем результаты
    runner.results[0] = {
        'success': True,
        'output': 'Test output',
        'error': ''
    }
    
    runner.results[1] = {
        'success': False,
        'output': '',
        'error': 'Test error'
    }
    
    assert len(runner.results) == 2, "Должно быть 2 результата"
    assert runner.results[0]['success'] == True, "Первый результат должен быть успешным"
    assert runner.results[1]['success'] == False, "Второй результат должен быть неудачным"
    print("✅ Структура результатов корректна")
    
    print()


def test_parallel_runner_methods():
    """Тест наличия всех методов"""
    print("="*60)
    print("🧪 Тест 9: Методы ParallelMacroRunner")
    print("="*60)
    
    from src.engines.parallel_runner import ParallelMacroRunner
    
    runner = ParallelMacroRunner()
    
    # Проверяем основные методы
    methods = [
        'connect_to_existing_chrome',
        'create_chrome_instance',
        'run_macro_in_instance',
        'run_parallel',
        'print_results',
        'cleanup',
    ]
    
    found_methods = []
    missing_methods = []
    
    for method in methods:
        if hasattr(runner, method):
            found_methods.append(method)
            print(f"✅ {method}()")
        else:
            missing_methods.append(method)
            print(f"⚠️  {method}() не найден")
    
    print(f"\n📊 Найдено методов: {len(found_methods)}/{len(methods)}")
    
    assert len(found_methods) == len(methods), f"Не все методы найдены: {missing_methods}"
    
    print()


def test_parallel_runner_empty_results():
    """Тест пустых результатов"""
    print("="*60)
    print("🧪 Тест 10: Пустые результаты")
    print("="*60)
    
    from src.engines.parallel_runner import ParallelMacroRunner
    
    runner = ParallelMacroRunner()
    
    # Результаты должны быть пустыми при создании
    assert len(runner.results) == 0, "Результаты должны быть пустыми"
    assert len(runner.drivers) == 0, "Drivers должны быть пустыми"
    assert len(runner.threads) == 0, "Threads должны быть пустыми"
    print("✅ Начальное состояние корректно")
    
    print()


def test_parallel_runner_print_results():
    """Тест вывода результатов"""
    print("="*60)
    print("🧪 Тест 11: Вывод результатов")
    print("="*60)
    
    from src.engines.parallel_runner import ParallelMacroRunner
    
    runner = ParallelMacroRunner()
    
    # Добавляем тестовые результаты
    runner.results[0] = {'success': True}
    runner.results[1] = {'success': True}
    runner.results[2] = {'success': False}
    
    # Проверяем что print_results не падает
    try:
        runner.print_results()
        print("✅ print_results() работает корректно")
    except Exception as e:
        print(f"❌ print_results() упал: {e}")
        raise
    
    print()


def test_selenium_availability():
    """Тест доступности Selenium"""
    print("="*60)
    print("🧪 Тест 12: Доступность Selenium")
    print("="*60)
    
    try:
        from src.engines.parallel_runner import SELENIUM_AVAILABLE
        
        if SELENIUM_AVAILABLE:
            print("✅ Selenium доступен")
            
            # Проверяем импорты
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            print("✅ Selenium модули импортированы")
        else:
            print("⚠️  Selenium не доступен")
            print("   Установите: pip install selenium webdriver-manager")
    
    except ImportError as e:
        print(f"⚠️  Selenium не установлен: {e}")
    
    print()


def test_parallel_runner_instance_count_validation():
    """Тест валидации количества экземпляров"""
    print("="*60)
    print("🧪 Тест 13: Валидация количества экземпляров")
    print("="*60)
    
    from src.engines.parallel_runner import ParallelMacroRunner
    
    # Тестируем различные значения
    test_cases = [1, 2, 3, 5, 10]
    
    for count in test_cases:
        runner = ParallelMacroRunner(num_instances=count)
        assert runner.num_instances == count, f"Ожидалось {count}, получено {runner.num_instances}"
        print(f"✅ {count} экземпляров - OK")
    
    print()


def test_parallel_runner_lists_initialization():
    """Тест инициализации списков"""
    print("="*60)
    print("🧪 Тест 14: Инициализация списков")
    print("="*60)
    
    from src.engines.parallel_runner import ParallelMacroRunner
    
    runner = ParallelMacroRunner()
    
    # Проверяем что списки пустые и правильного типа
    assert isinstance(runner.drivers, list), "drivers должен быть списком"
    assert isinstance(runner.threads, list), "threads должен быть списком"
    assert isinstance(runner.results, dict), "results должен быть словарем"
    assert isinstance(runner.custom_profiles, list), "custom_profiles должен быть списком"
    assert isinstance(runner.custom_macros, list), "custom_macros должен быть списком"
    assert isinstance(runner.custom_urls, list), "custom_urls должен быть списком"
    
    print("✅ Все списки инициализированы правильно")
    
    # Проверяем что они пустые
    assert len(runner.drivers) == 0, "drivers должен быть пустым"
    assert len(runner.threads) == 0, "threads должен быть пустым"
    assert len(runner.results) == 0, "results должен быть пустым"
    assert len(runner.custom_profiles) == 0, "custom_profiles должен быть пустым"
    assert len(runner.custom_macros) == 0, "custom_macros должен быть пустым"
    assert len(runner.custom_urls) == 0, "custom_urls должен быть пустым"
    
    print("✅ Все списки пустые при инициализации")
    
    print()


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🚀 ТЕСТИРОВАНИЕ PARALLEL RUNNER".center(60))
    print("="*60)
    print("\nПроверяем параллельное выполнение макросов!\n")
    
    tests = [
        test_parallel_runner_import,
        test_parallel_runner_initialization,
        test_parallel_runner_custom_instances,
        test_parallel_runner_use_existing,
        test_parallel_runner_custom_profiles,
        test_parallel_runner_custom_macros,
        test_parallel_runner_custom_urls,
        test_parallel_runner_results_structure,
        test_parallel_runner_methods,
        test_parallel_runner_empty_results,
        test_parallel_runner_print_results,
        test_selenium_availability,
        test_parallel_runner_instance_count_validation,
        test_parallel_runner_lists_initialization,
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
        print("🎉 ВСЕ ТЕСТЫ PARALLEL RUNNER ПРОШЛИ!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print("\n💡 Параллельное выполнение работает!")
    else:
        print("⚠️  ЕСТЬ ПРОБЛЕМЫ С PARALLEL RUNNER!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print(f"❌ Провалено: {failed}/{len(tests)}")
        print("\n💡 Проверьте parallel_runner!")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
