#!/usr/bin/env python3
"""
test_imports.py
Тестирование что все модули импортируются корректно после реструктуризации
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_core_imports():
    """Тест импортов из src/core/"""
    print("\n" + "="*60)
    print("🧪 Тест 1: Импорты src/core/")
    print("="*60)
    
    try:
        from src.core import atlas_dsl_parser
        print("✅ atlas_dsl_parser импортирован")
    except ImportError as e:
        print(f"❌ atlas_dsl_parser: {e}")
        raise
    
    try:
        from src.core.atlas_dsl_parser import AtlasDSLParser
        print("✅ AtlasDSLParser импортирован")
    except ImportError as e:
        print(f"❌ AtlasDSLParser: {e}")
        raise
    
    print()


def test_engines_imports():
    """Тест импортов из src/engines/"""
    print("="*60)
    print("🧪 Тест 2: Импорты src/engines/")
    print("="*60)
    
    try:
        from src.engines import selenium_helper
        print("✅ selenium_helper импортирован")
    except ImportError as e:
        print(f"❌ selenium_helper: {e}")
        raise
    
    try:
        from src.engines import parallel_runner
        print("✅ parallel_runner импортирован")
    except ImportError as e:
        print(f"❌ parallel_runner: {e}")
        raise
    
    print()


def test_ai_imports():
    """Тест импортов из src/ai/"""
    print("="*60)
    print("🧪 Тест 3: Импорты src/ai/")
    print("="*60)
    
    try:
        from src.ai.macro_generator import AIMacroGenerator
        print("✅ AIMacroGenerator импортирован")
    except ImportError as e:
        print(f"❌ AIMacroGenerator: {e}")
        raise
    
    try:
        from src.ai.macro_generator_legacy import AIMacroGenerator as LegacyGen
        print("✅ AIMacroGenerator (legacy) импортирован")
    except ImportError as e:
        print(f"❌ AIMacroGenerator (legacy): {e}")
        raise
    
    try:
        from src.ai.prompt_updater import PromptUpdater
        print("✅ PromptUpdater импортирован")
    except ImportError as e:
        print(f"❌ PromptUpdater: {e}")
        raise
    
    try:
        from src.ai.dom_analyzer import AIDOMAnalyzer
        print("✅ AIDOMAnalyzer импортирован")
    except ImportError as e:
        print(f"⚠️  AIDOMAnalyzer: {e} (может не быть google-genai)")
    
    print()


def test_utils_imports():
    """Тест импортов из src/utils/"""
    print("="*60)
    print("🧪 Тест 4: Импорты src/utils/")
    print("="*60)
    
    try:
        from src.utils.api_config import APIConfig, api_config
        print("✅ APIConfig импортирован")
    except ImportError as e:
        print(f"❌ APIConfig: {e}")
        raise
    
    try:
        from src.utils.smart_capture import SmartCapture
        print("✅ SmartCapture импортирован")
    except ImportError as e:
        print(f"❌ SmartCapture: {e}")
        raise
    
    try:
        from src.utils.coordinate_finder import CoordinateFinder
        print("✅ CoordinateFinder импортирован")
    except ImportError as e:
        print(f"⚠️  CoordinateFinder: {e} (может не быть класса)")
    
    print()


def test_config_import():
    """Тест импорта config.py"""
    print("="*60)
    print("🧪 Тест 5: Импорт config.py")
    print("="*60)
    
    try:
        from config import MACROS_DIR, EXAMPLES_DIR, TEMPLATES_DIR
        print("✅ config импортирован")
        print(f"   MACROS_DIR: {MACROS_DIR}")
        print(f"   EXAMPLES_DIR: {EXAMPLES_DIR}")
        print(f"   TEMPLATES_DIR: {TEMPLATES_DIR}")
    except ImportError as e:
        print(f"❌ config: {e}")
        raise
    
    print()


def test_cross_imports():
    """Тест кросс-импортов между модулями"""
    print("="*60)
    print("🧪 Тест 6: Кросс-импорты")
    print("="*60)
    
    # Проверяем что модули могут импортировать друг друга
    try:
        from src.ai.macro_generator import AIMacroGenerator
        gen = AIMacroGenerator(Path.cwd())
        print("✅ AIMacroGenerator создан (использует api_config)")
    except Exception as e:
        print(f"⚠️  AIMacroGenerator: {e}")
    
    try:
        from src.utils.api_config import api_config
        assert api_config is not None
        print("✅ api_config доступен глобально")
    except Exception as e:
        print(f"❌ api_config: {e}")
        raise
    
    print()


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ ИМПОРТОВ".center(60))
    print("="*60)
    
    tests = [
        test_core_imports,
        test_engines_imports,
        test_ai_imports,
        test_utils_imports,
        test_config_import,
        test_cross_imports,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print("="*60)
    print(f"✅ Пройдено: {passed}/{len(tests)}")
    if failed > 0:
        print(f"❌ Провалено: {failed}/{len(tests)}")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
