#!/usr/bin/env python3
"""
test_config.py
Тестирование config.py (пути к макросам)
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MACROS_DIR, EXAMPLES_DIR, TEMPLATES_DIR, PROJECT_ROOT


def test_project_root():
    """Тест PROJECT_ROOT"""
    print("\n" + "="*60)
    print("🧪 Тест 1: PROJECT_ROOT")
    print("="*60)
    
    assert PROJECT_ROOT is not None, "PROJECT_ROOT должен быть установлен"
    print(f"✅ PROJECT_ROOT: {PROJECT_ROOT}")
    
    assert PROJECT_ROOT.exists(), "PROJECT_ROOT должен существовать"
    assert PROJECT_ROOT.is_dir(), "PROJECT_ROOT должен быть папкой"
    print("✅ PROJECT_ROOT существует и это папка")
    
    print()


def test_macros_dir():
    """Тест MACROS_DIR"""
    print("="*60)
    print("🧪 Тест 2: MACROS_DIR")
    print("="*60)
    
    assert MACROS_DIR is not None, "MACROS_DIR должен быть установлен"
    print(f"✅ MACROS_DIR: {MACROS_DIR}")
    
    assert MACROS_DIR.exists(), "MACROS_DIR должен существовать"
    assert MACROS_DIR.is_dir(), "MACROS_DIR должен быть папкой"
    print("✅ MACROS_DIR существует и это папка")
    
    # Проверяем что это macros/production/
    assert 'macros' in str(MACROS_DIR), "Путь должен содержать 'macros'"
    assert 'production' in str(MACROS_DIR), "Путь должен содержать 'production'"
    print("✅ Путь корректный (macros/production/)")
    
    print()


def test_examples_dir():
    """Тест EXAMPLES_DIR"""
    print("="*60)
    print("🧪 Тест 3: EXAMPLES_DIR")
    print("="*60)
    
    assert EXAMPLES_DIR is not None, "EXAMPLES_DIR должен быть установлен"
    print(f"✅ EXAMPLES_DIR: {EXAMPLES_DIR}")
    
    assert EXAMPLES_DIR.exists(), "EXAMPLES_DIR должен существовать"
    assert EXAMPLES_DIR.is_dir(), "EXAMPLES_DIR должен быть папкой"
    print("✅ EXAMPLES_DIR существует и это папка")
    
    # Проверяем что это macros/examples/
    assert 'macros' in str(EXAMPLES_DIR), "Путь должен содержать 'macros'"
    assert 'examples' in str(EXAMPLES_DIR), "Путь должен содержать 'examples'"
    print("✅ Путь корректный (macros/examples/)")
    
    print()


def test_templates_dir():
    """Тест TEMPLATES_DIR"""
    print("="*60)
    print("🧪 Тест 4: TEMPLATES_DIR")
    print("="*60)
    
    assert TEMPLATES_DIR is not None, "TEMPLATES_DIR должен быть установлен"
    print(f"✅ TEMPLATES_DIR: {TEMPLATES_DIR}")
    
    assert TEMPLATES_DIR.exists(), "TEMPLATES_DIR должен существовать"
    assert TEMPLATES_DIR.is_dir(), "TEMPLATES_DIR должен быть папкой"
    print("✅ TEMPLATES_DIR существует и это папка")
    
    # Проверяем что это templates/
    assert 'templates' in str(TEMPLATES_DIR), "Путь должен содержать 'templates'"
    print("✅ Путь корректный (templates/)")
    
    print()


def test_paths_relative_to_root():
    """Тест что все пути относительно PROJECT_ROOT"""
    print("="*60)
    print("🧪 Тест 5: Пути относительно PROJECT_ROOT")
    print("="*60)
    
    # Проверяем что все пути начинаются с PROJECT_ROOT
    assert str(MACROS_DIR).startswith(str(PROJECT_ROOT)), "MACROS_DIR должен быть внутри PROJECT_ROOT"
    assert str(EXAMPLES_DIR).startswith(str(PROJECT_ROOT)), "EXAMPLES_DIR должен быть внутри PROJECT_ROOT"
    assert str(TEMPLATES_DIR).startswith(str(PROJECT_ROOT)), "TEMPLATES_DIR должен быть внутри PROJECT_ROOT"
    print("✅ Все пути относительно PROJECT_ROOT")
    
    print()


def test_macros_files_exist():
    """Тест что в MACROS_DIR есть файлы"""
    print("="*60)
    print("🧪 Тест 6: Файлы в MACROS_DIR")
    print("="*60)
    
    # Ищем .atlas файлы
    atlas_files = list(MACROS_DIR.glob('*.atlas'))
    
    print(f"📊 Найдено .atlas файлов: {len(atlas_files)}")
    
    if atlas_files:
        print("✅ Примеры файлов:")
        for f in atlas_files[:5]:
            print(f"   • {f.name}")
    else:
        print("⚠️  Нет .atlas файлов (это нормально для новой установки)")
    
    print()


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ CONFIG".center(60))
    print("="*60)
    
    tests = [
        test_project_root,
        test_macros_dir,
        test_examples_dir,
        test_templates_dir,
        test_paths_relative_to_root,
        test_macros_files_exist,
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
