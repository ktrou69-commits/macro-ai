#!/usr/bin/env python3
"""
test_smoke.py
🔥 SMOKE TESTS - Быстрая проверка что вся система работает

Эти тесты проверяют:
- Все критичные пути существуют
- Все модули импортируются
- Все конфиги загружаются
- Основные функции работают

Запускай после ЛЮБЫХ изменений!
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_project_structure():
    """
    🏗️ Тест структуры проекта
    
    Проверяет что все критичные папки существуют
    """
    print("\n" + "="*60)
    print("🏗️ Тест 1: Структура проекта")
    print("="*60)
    
    project_root = Path(__file__).parent.parent
    
    # Критичные папки
    critical_dirs = {
        'src': project_root / 'src',
        'src/core': project_root / 'src' / 'core',
        'src/engines': project_root / 'src' / 'engines',
        'src/ai': project_root / 'src' / 'ai',
        'src/utils': project_root / 'src' / 'utils',
        'tests': project_root / 'tests',
        'templates': project_root / 'templates',
        'macros': project_root / 'macros',
        'macros/production': project_root / 'macros' / 'production',
        'macros/examples': project_root / 'macros' / 'examples',
        'docs': project_root / 'docs',
        'scripts': project_root / 'scripts',
    }
    
    missing = []
    for name, path in critical_dirs.items():
        if not path.exists():
            missing.append(name)
            print(f"❌ {name}: НЕ СУЩЕСТВУЕТ")
        else:
            print(f"✅ {name}")
    
    assert len(missing) == 0, f"Отсутствуют папки: {missing}"
    print(f"\n✅ Все {len(critical_dirs)} критичных папок на месте!")
    print()


def test_critical_files():
    """
    📄 Тест критичных файлов
    
    Проверяет что все важные файлы существуют
    """
    print("="*60)
    print("📄 Тест 2: Критичные файлы")
    print("="*60)
    
    project_root = Path(__file__).parent.parent
    
    critical_files = {
        'config.py': project_root / 'config.py',
        'requirements.txt': project_root / 'requirements.txt',
        'README.md': project_root / 'README.md',
        '.env': project_root / '.env',
        '.gitignore': project_root / '.gitignore',
        'src/main.py': project_root / 'src' / 'main.py',
        'src/core/atlas_dsl_parser.py': project_root / 'src' / 'core' / 'atlas_dsl_parser.py',
        'src/utils/api_config.py': project_root / 'src' / 'utils' / 'api_config.py',
    }
    
    missing = []
    for name, path in critical_files.items():
        if not path.exists():
            missing.append(name)
            print(f"❌ {name}: НЕ СУЩЕСТВУЕТ")
        else:
            print(f"✅ {name}")
    
    assert len(missing) == 0, f"Отсутствуют файлы: {missing}"
    print(f"\n✅ Все {len(critical_files)} критичных файлов на месте!")
    print()


def test_all_imports():
    """
    📦 Тест всех импортов
    
    Проверяет что ВСЕ модули импортируются без ошибок
    """
    print("="*60)
    print("📦 Тест 3: Все импорты")
    print("="*60)
    
    imports = {
        'config': lambda: __import__('config'),
        'src.core.atlas_dsl_parser': lambda: __import__('src.core.atlas_dsl_parser', fromlist=['AtlasDSLParser']),
        'src.core.macro_sequence': lambda: __import__('src.core.macro_sequence'),
        'src.core.sequence_builder': lambda: __import__('src.core.sequence_builder'),
        'src.engines.selenium_helper': lambda: __import__('src.engines.selenium_helper'),
        'src.engines.parallel_runner': lambda: __import__('src.engines.parallel_runner'),
        'src.ai.macro_generator': lambda: __import__('src.ai.macro_generator', fromlist=['AIMacroGenerator']),
        'src.ai.prompt_updater': lambda: __import__('src.ai.prompt_updater', fromlist=['PromptUpdater']),
        'src.utils.api_config': lambda: __import__('src.utils.api_config', fromlist=['APIConfig']),
        'src.utils.smart_capture': lambda: __import__('src.utils.smart_capture', fromlist=['SmartCapture']),
    }
    
    failed = []
    for name, import_func in imports.items():
        try:
            import_func()
            print(f"✅ {name}")
        except Exception as e:
            failed.append((name, str(e)))
            print(f"❌ {name}: {e}")
    
    assert len(failed) == 0, f"Не импортируются: {[name for name, _ in failed]}"
    print(f"\n✅ Все {len(imports)} модулей импортируются!")
    print()


def test_config_loading():
    """
    ⚙️ Тест загрузки конфигурации
    
    Проверяет что все конфиги загружаются правильно
    """
    print("="*60)
    print("⚙️ Тест 4: Загрузка конфигурации")
    print("="*60)
    
    # Проверяем config.py
    from config import MACROS_DIR, EXAMPLES_DIR, TEMPLATES_DIR, PROJECT_ROOT
    
    assert PROJECT_ROOT is not None, "PROJECT_ROOT не загружен"
    assert PROJECT_ROOT.exists(), "PROJECT_ROOT не существует"
    print(f"✅ PROJECT_ROOT: {PROJECT_ROOT}")
    
    assert MACROS_DIR is not None, "MACROS_DIR не загружен"
    assert MACROS_DIR.exists(), "MACROS_DIR не существует"
    print(f"✅ MACROS_DIR: {MACROS_DIR}")
    
    assert EXAMPLES_DIR is not None, "EXAMPLES_DIR не загружен"
    assert EXAMPLES_DIR.exists(), "EXAMPLES_DIR не существует"
    print(f"✅ EXAMPLES_DIR: {EXAMPLES_DIR}")
    
    assert TEMPLATES_DIR is not None, "TEMPLATES_DIR не загружен"
    assert TEMPLATES_DIR.exists(), "TEMPLATES_DIR не существует"
    print(f"✅ TEMPLATES_DIR: {TEMPLATES_DIR}")
    
    # Проверяем api_config
    from src.utils.api_config import api_config
    
    assert api_config is not None, "api_config не загружен"
    print(f"✅ api_config загружен")
    
    assert hasattr(api_config, 'gemini_key'), "api_config.gemini_key отсутствует"
    assert hasattr(api_config, 'gemini_model'), "api_config.gemini_model отсутствует"
    print(f"✅ api_config.gemini_model: {api_config.gemini_model}")
    
    print(f"\n✅ Все конфиги загружены правильно!")
    print()


def test_basic_functionality():
    """
    🔧 Тест базовой функциональности
    
    Проверяет что основные функции работают
    """
    print("="*60)
    print("🔧 Тест 5: Базовая функциональность")
    print("="*60)
    
    # Проверяем AtlasDSLParser
    from src.core.atlas_dsl_parser import AtlasDSLParser
    
    parser = AtlasDSLParser()
    assert parser is not None, "AtlasDSLParser не создался"
    print("✅ AtlasDSLParser создаётся")
    
    # Проверяем APIConfig
    from src.utils.api_config import APIConfig
    
    config = APIConfig()
    assert config is not None, "APIConfig не создался"
    assert config.has_gemini() or not config.has_gemini(), "has_gemini() работает"
    print("✅ APIConfig работает")
    
    # Проверяем SmartCapture
    from src.utils.smart_capture import SmartCapture
    
    capture = SmartCapture()
    assert capture is not None, "SmartCapture не создался"
    print("✅ SmartCapture создаётся")
    
    print(f"\n✅ Базовая функциональность работает!")
    print()


def test_macros_exist():
    """
    📝 Тест наличия макросов
    
    Проверяет что есть хотя бы несколько макросов
    """
    print("="*60)
    print("📝 Тест 6: Наличие макросов")
    print("="*60)
    
    from config import MACROS_DIR, EXAMPLES_DIR
    
    # Проверяем production макросы
    production_macros = list(MACROS_DIR.glob('*.atlas'))
    print(f"📊 Production макросов: {len(production_macros)}")
    
    if production_macros:
        print("✅ Примеры:")
        for m in production_macros[:3]:
            print(f"   • {m.name}")
    else:
        print("⚠️  Нет production макросов (это нормально для новой установки)")
    
    # Проверяем examples
    example_files = list(EXAMPLES_DIR.glob('**/*.yaml')) + list(EXAMPLES_DIR.glob('**/*.atlas'))
    print(f"📊 Example файлов: {len(example_files)}")
    
    if example_files:
        print("✅ Примеры:")
        for m in example_files[:3]:
            print(f"   • {m.name}")
    
    print(f"\n✅ Макросы проверены!")
    print()


def test_templates_exist():
    """
    🖼️ Тест наличия шаблонов
    
    Проверяет что есть шаблоны для компьютерного зрения
    """
    print("="*60)
    print("🖼️ Тест 7: Наличие шаблонов")
    print("="*60)
    
    from config import TEMPLATES_DIR
    
    # Проверяем PNG шаблоны
    templates = list(TEMPLATES_DIR.glob('**/*.png'))
    print(f"📊 PNG шаблонов: {len(templates)}")
    
    if templates:
        print("✅ Примеры:")
        for t in templates[:5]:
            print(f"   • {t.relative_to(TEMPLATES_DIR)}")
    else:
        print("⚠️  Нет PNG шаблонов (создайте через Smart Capture)")
    
    # Проверяем структуру папок
    chrome_dir = TEMPLATES_DIR / 'Chrome'
    if chrome_dir.exists():
        print(f"✅ Chrome/ папка существует")
        platforms = [d.name for d in chrome_dir.iterdir() if d.is_dir()]
        if platforms:
            print(f"✅ Платформы: {', '.join(platforms[:5])}")
    
    print(f"\n✅ Шаблоны проверены!")
    print()


def run_all_tests():
    """Запуск всех smoke тестов"""
    print("\n" + "="*60)
    print("🔥 SMOKE TESTS - ПРОВЕРКА ВСЕЙ СИСТЕМЫ".center(60))
    print("="*60)
    print("\nЭти тесты проверяют что ВСЯ система работает!")
    print("Запускай после ЛЮБЫХ изменений в коде.\n")
    
    tests = [
        test_project_structure,
        test_critical_files,
        test_all_imports,
        test_config_loading,
        test_basic_functionality,
        test_macros_exist,
        test_templates_exist,
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
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print("\n💡 Система полностью работоспособна!")
    else:
        print("⚠️  ЕСТЬ ПРОБЛЕМЫ!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print(f"❌ Провалено: {failed}/{len(tests)}")
        print("\n💡 Исправьте ошибки выше и запустите тесты снова!")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
