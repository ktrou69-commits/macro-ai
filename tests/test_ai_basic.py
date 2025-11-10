#!/usr/bin/env python3
"""
test_ai_basic.py
🤖 ВАЖНО: Базовое тестирование AI функций

Проверяет:
- AI Macro Generator
- Prompt Updater
- API конфигурацию для AI
- Gemini API доступность
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_ai_macro_generator_import():
    """Тест импорта AI Macro Generator"""
    print("\n" + "="*60)
    print("🧪 Тест 1: AI Macro Generator импорт")
    print("="*60)
    
    try:
        from src.ai.macro_generator import AIMacroGenerator
        print("✅ AIMacroGenerator импортирован")
        
        # Проверяем что это класс
        assert callable(AIMacroGenerator), "AIMacroGenerator должен быть классом"
        print("✅ AIMacroGenerator - это класс")
        
    except ImportError as e:
        print(f"❌ Не удалось импортировать: {e}")
        raise
    
    print()


def test_ai_macro_generator_initialization():
    """Тест инициализации AI Macro Generator"""
    print("="*60)
    print("🧪 Тест 2: AI Macro Generator инициализация")
    print("="*60)
    
    try:
        from src.ai.macro_generator import AIMacroGenerator
        
        # Создаём экземпляр
        generator = AIMacroGenerator(Path.cwd())
        assert generator is not None, "Генератор не создался"
        print("✅ AIMacroGenerator создан")
        
        # Проверяем атрибуты
        assert hasattr(generator, 'gemini_key'), "Нет атрибута gemini_key"
        assert hasattr(generator, 'project_root'), "Нет атрибута project_root"
        assert hasattr(generator, 'macros_dir'), "Нет атрибута macros_dir"
        print("✅ Все атрибуты на месте")
        
        # Проверяем что macros_dir существует
        assert generator.macros_dir.exists(), "macros_dir не существует"
        print(f"✅ macros_dir: {generator.macros_dir}")
        
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        raise
    
    print()


def test_prompt_updater_import():
    """Тест импорта Prompt Updater"""
    print("="*60)
    print("🧪 Тест 3: Prompt Updater импорт")
    print("="*60)
    
    try:
        from src.ai.prompt_updater import PromptUpdater
        print("✅ PromptUpdater импортирован")
        
        # Создаём экземпляр
        updater = PromptUpdater(Path.cwd())
        assert updater is not None
        print("✅ PromptUpdater создан")
        
        # Проверяем методы
        assert hasattr(updater, 'scan_templates'), "Нет метода scan_templates"
        assert hasattr(updater, 'update_structure'), "Нет метода update_structure"
        print("✅ Методы существуют")
        
    except ImportError as e:
        print(f"❌ Не удалось импортировать: {e}")
        raise
    
    print()


def test_ai_api_config():
    """Тест API конфигурации для AI"""
    print("="*60)
    print("🧪 Тест 4: API конфигурация для AI")
    print("="*60)
    
    from src.utils.api_config import api_config
    
    # Проверяем Gemini ключ
    if api_config.gemini_key:
        print(f"✅ Gemini ключ установлен: {api_config.gemini_key[:20]}...")
        assert len(api_config.gemini_key) > 20, "Ключ слишком короткий"
    else:
        print("⚠️  Gemini ключ не установлен")
        print("   Установите в .env: GEMINI_API_KEY=your-key")
    
    # Проверяем модель
    assert api_config.gemini_model is not None, "Модель не установлена"
    print(f"✅ Gemini модель: {api_config.gemini_model}")
    
    # Проверяем валидность модели
    valid_models = [
        'gemini-1.5-flash',
        'gemini-2.0-flash',
        'gemini-2.5-flash',
        'gemini-2.5-flash-lite',
        'gemini-2.5-pro',
    ]
    
    if api_config.gemini_model in valid_models:
        print(f"✅ Модель валидна")
    else:
        print(f"⚠️  Модель не в списке рекомендуемых: {valid_models}")
    
    print()


def test_gemini_sdk_available():
    """Тест доступности Gemini SDK"""
    print("="*60)
    print("🧪 Тест 5: Gemini SDK")
    print("="*60)
    
    try:
        from google import genai
        print("✅ google-genai установлен")
        
        # Проверяем что есть Client
        assert hasattr(genai, 'Client'), "Нет genai.Client"
        print("✅ genai.Client доступен")
        
        # Проверяем версию (если есть)
        if hasattr(genai, '__version__'):
            print(f"✅ Версия: {genai.__version__}")
        
    except ImportError:
        print("⚠️  google-genai не установлен")
        print("   pip install google-genai")
    
    print()


def test_ai_generator_methods():
    """Тест методов AI генератора"""
    print("="*60)
    print("🧪 Тест 6: Методы AI генератора")
    print("="*60)
    
    from src.ai.macro_generator import AIMacroGenerator
    
    generator = AIMacroGenerator(Path.cwd())
    
    # Проверяем основные методы
    methods = [
        'generate_macro',
        'build_optimized_prompt',
        'detect_platforms',
        'detect_actions',
    ]
    
    found_methods = []
    missing_methods = []
    
    for method in methods:
        if hasattr(generator, method):
            found_methods.append(method)
            print(f"✅ {method}()")
        else:
            missing_methods.append(method)
            print(f"⚠️  {method}() не найден")
    
    print(f"\n📊 Найдено методов: {len(found_methods)}/{len(methods)}")
    
    assert len(found_methods) > 0, "Ни один метод не найден"
    
    print()


def test_prompt_files_exist():
    """Тест наличия файлов промптов"""
    print("="*60)
    print("🧪 Тест 7: Файлы промптов")
    print("="*60)
    
    project_root = Path.cwd()
    
    # Проверяем файлы промптов
    prompt_files = {
        'TEMPLATES_STRUCTURE.txt': project_root / 'templates' / 'TEMPLATES_STRUCTURE.txt',
        'BEST_PRACTICES.txt': project_root / 'templates' / 'BEST_PRACTICES.txt',
    }
    
    found = []
    missing = []
    
    for name, path in prompt_files.items():
        if path.exists():
            found.append(name)
            size = path.stat().st_size
            print(f"✅ {name} ({size} bytes)")
        else:
            missing.append(name)
            print(f"⚠️  {name} не найден")
    
    if missing:
        print(f"\n⚠️  Отсутствуют файлы: {', '.join(missing)}")
        print("   Создайте через: python3 src/ai/prompt_updater.py --update")
    
    print()


def test_ai_legacy_generator():
    """Тест legacy AI генератора"""
    print("="*60)
    print("🧪 Тест 8: Legacy AI генератор")
    print("="*60)
    
    try:
        from src.ai.macro_generator_legacy import AIMacroGenerator as LegacyGen
        print("✅ Legacy AIMacroGenerator импортирован")
        
        # Создаём экземпляр
        generator = LegacyGen(Path.cwd())
        assert generator is not None
        print("✅ Legacy генератор создан")
        
        # Проверяем что это другой класс
        from src.ai.macro_generator import AIMacroGenerator
        assert LegacyGen != AIMacroGenerator, "Legacy и новый генератор - один класс"
        print("✅ Legacy и новый генератор - разные классы")
        
    except ImportError as e:
        print(f"⚠️  Legacy генератор не импортируется: {e}")
    
    print()


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🤖 ТЕСТИРОВАНИЕ AI".center(60))
    print("="*60)
    print("\nПроверяем AI генератор и Gemini API!\n")
    
    tests = [
        test_ai_macro_generator_import,
        test_ai_macro_generator_initialization,
        test_prompt_updater_import,
        test_ai_api_config,
        test_gemini_sdk_available,
        test_ai_generator_methods,
        test_prompt_files_exist,
        test_ai_legacy_generator,
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
        print("🎉 ВСЕ AI ТЕСТЫ ПРОШЛИ!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print("\n💡 AI генератор работает!")
    else:
        print("⚠️  ЕСТЬ ПРОБЛЕМЫ С AI!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print(f"❌ Провалено: {failed}/{len(tests)}")
        print("\n💡 Проверьте AI модули и API ключ!")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
