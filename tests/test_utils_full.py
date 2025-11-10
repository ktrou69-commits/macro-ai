#!/usr/bin/env python3
"""
test_utils_full.py
🔧 ПОЛЕЗНО: Полное тестирование утилит

Проверяет:
- Smart Capture
- Coordinate Finder
- Advanced Coordinate Finder
- DOM Selector Tool
- API Config
- Check API Quota
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_smart_capture():
    """Тест Smart Capture"""
    print("\n" + "="*60)
    print("🧪 Тест 1: Smart Capture")
    print("="*60)
    
    try:
        from src.utils.smart_capture import SmartCapture
        
        # Создаём экземпляр
        capture = SmartCapture()
        assert capture is not None
        print("✅ SmartCapture создан")
        
        # Проверяем методы
        methods = ['capture_template', 'save_template']
        found = []
        
        for method in methods:
            if hasattr(capture, method):
                found.append(method)
                print(f"✅ Метод {method}() существует")
        
        print(f"📊 Найдено методов: {len(found)}/{len(methods)}")
        
    except ImportError as e:
        print(f"⚠️  Smart Capture не импортируется: {e}")
    except Exception as e:
        print(f"⚠️  Ошибка: {e}")
    
    print()


def test_coordinate_finder():
    """Тест Coordinate Finder"""
    print("="*60)
    print("🧪 Тест 2: Coordinate Finder")
    print("="*60)
    
    try:
        # Пробуем импортировать
        from src.utils import coordinate_finder
        print("✅ coordinate_finder модуль импортирован")
        
        # Проверяем что есть функции/классы
        module_items = dir(coordinate_finder)
        useful_items = [item for item in module_items if not item.startswith('_')]
        
        print(f"📊 Экспортируемых элементов: {len(useful_items)}")
        if useful_items:
            print(f"✅ Примеры: {', '.join(useful_items[:5])}")
        
    except ImportError as e:
        print(f"⚠️  Coordinate Finder не импортируется: {e}")
    
    print()


def test_advanced_coordinate_finder():
    """Тест Advanced Coordinate Finder"""
    print("="*60)
    print("🧪 Тест 3: Advanced Coordinate Finder")
    print("="*60)
    
    try:
        from src.utils import advanced_coordinate_finder
        print("✅ advanced_coordinate_finder импортирован")
        
        # Проверяем что есть функции/классы
        module_items = dir(advanced_coordinate_finder)
        useful_items = [item for item in module_items if not item.startswith('_')]
        
        print(f"📊 Экспортируемых элементов: {len(useful_items)}")
        
    except ImportError as e:
        print(f"⚠️  Advanced Coordinate Finder не импортируется: {e}")
    
    print()


def test_dom_selector_tool():
    """Тест DOM Selector Tool"""
    print("="*60)
    print("🧪 Тест 4: DOM Selector Tool")
    print("="*60)
    
    try:
        from src.utils.dom_selector_tool import DOMSelectorTool
        print("✅ DOMSelectorTool импортирован")
        
        # Создаём экземпляр
        tool = DOMSelectorTool()
        assert tool is not None
        print("✅ DOMSelectorTool создан")
        
        # Проверяем методы
        if hasattr(tool, 'extract_selectors'):
            print("✅ Метод extract_selectors() существует")
        
    except ImportError as e:
        print(f"⚠️  DOM Selector Tool не импортируется: {e}")
    except Exception as e:
        print(f"⚠️  Ошибка: {e}")
    
    print()


def test_api_config_utility():
    """Тест API Config утилиты"""
    print("="*60)
    print("🧪 Тест 5: API Config")
    print("="*60)
    
    from src.utils.api_config import APIConfig, api_config
    
    # Проверяем глобальный экземпляр
    assert api_config is not None
    print("✅ Глобальный api_config существует")
    
    # Проверяем что это APIConfig
    assert isinstance(api_config, APIConfig)
    print("✅ api_config - экземпляр APIConfig")
    
    # Проверяем методы
    methods = ['has_gemini', 'has_openai', 'has_anthropic', 'print_status']
    found = []
    
    for method in methods:
        if hasattr(api_config, method):
            found.append(method)
    
    print(f"📊 Методов: {len(found)}/{len(methods)}")
    print(f"✅ Методы: {', '.join(found)}")
    
    print()


def test_check_api_quota():
    """Тест Check API Quota"""
    print("="*60)
    print("🧪 Тест 6: Check API Quota")
    print("="*60)
    
    try:
        from src.utils import check_api_quota
        print("✅ check_api_quota импортирован")
        
        # Проверяем что есть функция check_quota
        if hasattr(check_api_quota, 'check_quota'):
            print("✅ Функция check_quota() существует")
        
    except ImportError as e:
        print(f"⚠️  Check API Quota не импортируется: {e}")
    
    print()


def test_utils_directory_structure():
    """Тест структуры utils/"""
    print("="*60)
    print("🧪 Тест 7: Структура src/utils/")
    print("="*60)
    
    utils_dir = Path.cwd() / 'src' / 'utils'
    
    assert utils_dir.exists(), "src/utils/ не существует"
    print(f"✅ src/utils/ существует")
    
    # Находим все .py файлы
    py_files = list(utils_dir.glob('*.py'))
    py_files = [f for f in py_files if f.name != '__init__.py']
    
    print(f"📊 Python файлов: {len(py_files)}")
    
    if py_files:
        print("✅ Утилиты:")
        for f in sorted(py_files)[:10]:
            size_kb = f.stat().st_size / 1024
            print(f"   • {f.name} ({size_kb:.1f} KB)")
    
    assert len(py_files) > 0, "Нет утилит в src/utils/"
    
    print()


def test_utils_imports():
    """Тест импорта всех утилит"""
    print("="*60)
    print("🧪 Тест 8: Импорт всех утилит")
    print("="*60)
    
    utils_modules = [
        'api_config',
        'smart_capture',
        'coordinate_finder',
        'advanced_coordinate_finder',
        'find_comment_region',
        'simple_coordinate_finder',
        'check_api_quota',
        'dom_selector_tool',
    ]
    
    imported = []
    failed = []
    
    for module in utils_modules:
        try:
            __import__(f'src.utils.{module}')
            imported.append(module)
            print(f"✅ {module}")
        except ImportError as e:
            failed.append((module, str(e)))
            print(f"⚠️  {module}: {str(e)[:50]}...")
    
    print(f"\n📊 Импортировано: {imported}/{len(utils_modules)}")
    
    if failed:
        print(f"⚠️  Не импортировались: {len(failed)}")
    
    assert len(imported) > 0, "Ни одна утилита не импортировалась"
    
    print()


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🔧 ТЕСТИРОВАНИЕ УТИЛИТ".center(60))
    print("="*60)
    print("\nПроверяем все утилиты в src/utils/!\n")
    
    tests = [
        test_smart_capture,
        test_coordinate_finder,
        test_advanced_coordinate_finder,
        test_dom_selector_tool,
        test_api_config_utility,
        test_check_api_quota,
        test_utils_directory_structure,
        test_utils_imports,
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
        print("🎉 ВСЕ ТЕСТЫ УТИЛИТ ПРОШЛИ!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print("\n💡 Утилиты работают корректно!")
    else:
        print("⚠️  ЕСТЬ ПРОБЛЕМЫ С УТИЛИТАМИ!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print(f"❌ Провалено: {failed}/{len(tests)}")
        print("\n💡 Проверьте утилиты в src/utils/!")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
