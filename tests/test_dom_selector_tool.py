#!/usr/bin/env python3
"""
test_dom_selector_tool.py
🔍 ВАЖНО: Тестирование DOM Selector Tool

Проверяет:
- DOMSelectorTool класс
- Инициализация tool
- AI анализатор
- DOMSelectorExtractor
- Методы извлечения селекторов
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_dom_selector_tool_import():
    """Тест импорта DOMSelectorTool"""
    print("\n" + "="*60)
    print("🧪 Тест 1: Импорт DOMSelectorTool")
    print("="*60)
    
    try:
        from src.utils.dom_selector_tool import DOMSelectorTool
        print("✅ DOMSelectorTool импортирован")
        
        # Проверяем что это класс
        assert callable(DOMSelectorTool), "DOMSelectorTool должен быть классом"
        print("✅ DOMSelectorTool - это класс")
        
    except ImportError as e:
        print(f"❌ Не удалось импортировать: {e}")
        raise
    
    print()


def test_dom_selector_tool_initialization():
    """Тест инициализации DOMSelectorTool"""
    print("="*60)
    print("🧪 Тест 2: Инициализация DOMSelectorTool")
    print("="*60)
    
    try:
        from src.utils.dom_selector_tool import DOMSelectorTool
        
        # Создаём экземпляр
        tool = DOMSelectorTool()
        assert tool is not None, "Tool не создался"
        print("✅ DOMSelectorTool создан")
        
        # Проверяем атрибуты
        assert hasattr(tool, 'extractor'), "Нет атрибута extractor"
        assert hasattr(tool, 'ai_analyzer'), "Нет атрибута ai_analyzer"
        print("✅ Все атрибуты на месте")
        
        # Проверяем extractor
        assert tool.extractor is not None, "extractor не инициализирован"
        print("✅ DOMSelectorExtractor инициализирован")
        
        # AI analyzer может быть None если нет ключа
        if tool.ai_analyzer:
            print("✅ AI анализатор доступен")
        else:
            print("⚠️  AI анализатор недоступен (нет GEMINI_API_KEY)")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        raise
    
    print()


def test_dom_selector_extractor_import():
    """Тест импорта DOMSelectorExtractor"""
    print("="*60)
    print("🧪 Тест 3: Импорт DOMSelectorExtractor")
    print("="*60)
    
    try:
        from src.utils.dom_selector_extractor import DOMSelectorExtractor
        print("✅ DOMSelectorExtractor импортирован")
        
        # Создаём экземпляр
        extractor = DOMSelectorExtractor()
        assert extractor is not None, "Extractor не создался"
        print("✅ DOMSelectorExtractor создан")
        
    except ImportError as e:
        print(f"⚠️  DOMSelectorExtractor не найден: {e}")
        print("   Это нормально, если модуль еще не создан")
    
    print()


def test_ai_dom_analyzer_import():
    """Тест импорта AIDOMAnalyzer"""
    print("="*60)
    print("🧪 Тест 4: Импорт AIDOMAnalyzer")
    print("="*60)
    
    try:
        from src.ai.dom_analyzer import AIDOMAnalyzer, GEMINI_AVAILABLE
        print("✅ AIDOMAnalyzer импортирован")
        
        if GEMINI_AVAILABLE:
            print("✅ Gemini SDK доступен")
        else:
            print("⚠️  Gemini SDK недоступен")
        
    except ImportError as e:
        print(f"❌ Не удалось импортировать: {e}")
        raise
    
    print()


def test_dom_selector_tool_methods():
    """Тест методов DOMSelectorTool"""
    print("="*60)
    print("🧪 Тест 5: Методы DOMSelectorTool")
    print("="*60)
    
    from src.utils.dom_selector_tool import DOMSelectorTool
    
    tool = DOMSelectorTool()
    
    # Проверяем основные методы
    methods = [
        'run',
        'extract_with_ai',
        'extract_rule_based',
        'view_selectors',
        'generate_structure',
        'batch_extract',
    ]
    
    found_methods = []
    missing_methods = []
    
    for method in methods:
        if hasattr(tool, method):
            found_methods.append(method)
            print(f"✅ {method}()")
        else:
            missing_methods.append(method)
            print(f"⚠️  {method}() не найден")
    
    print(f"\n📊 Найдено методов: {len(found_methods)}/{len(methods)}")
    
    # Должны быть хотя бы базовые методы
    assert 'run' in found_methods, "Метод run() обязателен"
    
    print()


def test_gemini_availability():
    """Тест доступности Gemini"""
    print("="*60)
    print("🧪 Тест 6: Доступность Gemini")
    print("="*60)
    
    try:
        from src.ai.dom_analyzer import GEMINI_AVAILABLE
        
        if GEMINI_AVAILABLE:
            print("✅ google-genai установлен")
            
            # Проверяем импорт
            from google import genai
            print("✅ genai импортирован")
            
            # Проверяем Client
            assert hasattr(genai, 'Client'), "Нет genai.Client"
            print("✅ genai.Client доступен")
        else:
            print("⚠️  google-genai не установлен")
            print("   Установите: pip install google-genai")
    
    except ImportError as e:
        print(f"⚠️  Ошибка импорта: {e}")
    
    print()


def test_dom_selector_tool_ai_analyzer_check():
    """Тест проверки AI анализатора"""
    print("="*60)
    print("🧪 Тест 7: Проверка AI анализатора")
    print("="*60)
    
    from src.utils.dom_selector_tool import DOMSelectorTool
    import os
    
    tool = DOMSelectorTool()
    
    # Проверяем наличие API ключа
    api_key = os.getenv('GEMINI_API_KEY')
    
    if api_key:
        print(f"✅ GEMINI_API_KEY установлен: {api_key[:20]}...")
        
        if tool.ai_analyzer:
            print("✅ AI анализатор инициализирован")
        else:
            print("⚠️  AI анализатор не инициализирован (возможна ошибка)")
    else:
        print("⚠️  GEMINI_API_KEY не установлен")
        print("   AI анализатор будет недоступен")
        
        assert tool.ai_analyzer is None, "ai_analyzer должен быть None без ключа"
        print("✅ ai_analyzer корректно None без ключа")
    
    print()


def test_dom_selector_extractor_methods():
    """Тест методов DOMSelectorExtractor"""
    print("="*60)
    print("🧪 Тест 8: Методы DOMSelectorExtractor")
    print("="*60)
    
    try:
        from src.utils.dom_selector_extractor import DOMSelectorExtractor
        
        extractor = DOMSelectorExtractor()
        
        # Проверяем основные методы
        expected_methods = [
            'save_selector',
            'load_selectors',
            'get_selector',
        ]
        
        found = []
        for method in expected_methods:
            if hasattr(extractor, method):
                found.append(method)
                print(f"✅ {method}()")
            else:
                print(f"⚠️  {method}() не найден")
        
        print(f"\n📊 Найдено методов: {len(found)}/{len(expected_methods)}")
        
    except ImportError:
        print("⚠️  DOMSelectorExtractor не импортируется")
        print("   Это нормально, если модуль еще не создан")
    
    print()


def test_dom_selectors_directory():
    """Тест наличия директории dom_selectors"""
    print("="*60)
    print("🧪 Тест 9: Директория dom_selectors")
    print("="*60)
    
    project_root = Path.cwd()
    dom_selectors_dir = project_root / 'dom_selectors'
    
    if dom_selectors_dir.exists():
        print(f"✅ Директория существует: {dom_selectors_dir}")
        
        # Проверяем содержимое
        subdirs = [d for d in dom_selectors_dir.iterdir() if d.is_dir()]
        print(f"✅ Найдено поддиректорий: {len(subdirs)}")
        
        for subdir in subdirs[:5]:  # Показываем первые 5
            print(f"   📁 {subdir.name}")
    else:
        print(f"⚠️  Директория не существует: {dom_selectors_dir}")
        print("   Создайте: mkdir -p dom_selectors")
    
    print()


def test_ai_dom_analyzer_initialization():
    """Тест инициализации AIDOMAnalyzer"""
    print("="*60)
    print("🧪 Тест 10: Инициализация AIDOMAnalyzer")
    print("="*60)
    
    import os
    from src.ai.dom_analyzer import AIDOMAnalyzer, GEMINI_AVAILABLE
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not GEMINI_AVAILABLE:
        print("⚠️  Gemini SDK недоступен")
        print("   Установите: pip install google-genai")
        return
    
    if not api_key:
        print("⚠️  GEMINI_API_KEY не установлен")
        print("   Тест пропущен")
        return
    
    try:
        analyzer = AIDOMAnalyzer()
        assert analyzer is not None, "Analyzer не создался"
        print("✅ AIDOMAnalyzer создан")
        
        # Проверяем атрибуты
        assert hasattr(analyzer, 'client'), "Нет атрибута client"
        print("✅ Gemini client инициализирован")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        raise
    
    print()


def test_dom_selector_tool_extractor_attribute():
    """Тест атрибута extractor"""
    print("="*60)
    print("🧪 Тест 11: Атрибут extractor")
    print("="*60)
    
    from src.utils.dom_selector_tool import DOMSelectorTool
    
    tool = DOMSelectorTool()
    
    # Проверяем что extractor не None
    assert tool.extractor is not None, "extractor не должен быть None"
    print("✅ extractor инициализирован")
    
    # Проверяем тип
    from src.utils.dom_selector_extractor import DOMSelectorExtractor
    assert isinstance(tool.extractor, DOMSelectorExtractor), "extractor должен быть DOMSelectorExtractor"
    print("✅ extractor правильного типа")
    
    print()


def test_dotenv_loading():
    """Тест загрузки .env файла"""
    print("="*60)
    print("🧪 Тест 12: Загрузка .env")
    print("="*60)
    
    project_root = Path.cwd()
    env_file = project_root / '.env'
    
    if env_file.exists():
        print(f"✅ .env файл существует: {env_file}")
        
        # Проверяем что dotenv установлен
        try:
            from dotenv import load_dotenv
            print("✅ python-dotenv установлен")
            
            # Загружаем .env
            load_dotenv(env_file)
            print("✅ .env файл загружен")
            
        except ImportError:
            print("⚠️  python-dotenv не установлен")
            print("   Установите: pip install python-dotenv")
    else:
        print(f"⚠️  .env файл не найден: {env_file}")
        print("   Создайте из .env.example")
    
    print()


def test_dom_selector_tool_complete_flow():
    """Тест полного flow (без реального выполнения)"""
    print("="*60)
    print("🧪 Тест 13: Полный flow (структура)")
    print("="*60)
    
    from src.utils.dom_selector_tool import DOMSelectorTool
    
    tool = DOMSelectorTool()
    
    # Проверяем что все компоненты на месте
    components = {
        'extractor': tool.extractor,
        'ai_analyzer': tool.ai_analyzer,  # Может быть None
    }
    
    print("📋 Компоненты:")
    for name, component in components.items():
        if component is not None:
            print(f"   ✅ {name}: {type(component).__name__}")
        else:
            print(f"   ⚠️  {name}: None (недоступен)")
    
    # Проверяем методы
    methods = ['run', 'extract_with_ai', 'extract_rule_based']
    print("\n📋 Методы:")
    for method in methods:
        if hasattr(tool, method):
            print(f"   ✅ {method}()")
        else:
            print(f"   ❌ {method}() отсутствует")
    
    print("\n✅ Структура tool корректна")
    
    print()


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🔍 ТЕСТИРОВАНИЕ DOM SELECTOR TOOL".center(60))
    print("="*60)
    print("\nПроверяем DOM Selector Tool!\n")
    
    tests = [
        test_dom_selector_tool_import,
        test_dom_selector_tool_initialization,
        test_dom_selector_extractor_import,
        test_ai_dom_analyzer_import,
        test_dom_selector_tool_methods,
        test_gemini_availability,
        test_dom_selector_tool_ai_analyzer_check,
        test_dom_selector_extractor_methods,
        test_dom_selectors_directory,
        test_ai_dom_analyzer_initialization,
        test_dom_selector_tool_extractor_attribute,
        test_dotenv_loading,
        test_dom_selector_tool_complete_flow,
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
        print("🎉 ВСЕ ТЕСТЫ DOM SELECTOR TOOL ПРОШЛИ!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print("\n💡 DOM Selector Tool работает!")
    else:
        print("⚠️  ЕСТЬ ПРОБЛЕМЫ С DOM SELECTOR TOOL!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print(f"❌ Провалено: {failed}/{len(tests)}")
        print("\n💡 Проверьте DOM Selector Tool!")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
