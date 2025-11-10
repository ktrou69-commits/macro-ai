#!/usr/bin/env python3
"""
test_api_config.py
Тестирование централизованной конфигурации API
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.api_config import APIConfig, api_config


def test_api_config_initialization():
    """Тест инициализации APIConfig"""
    print("\n" + "="*60)
    print("🧪 Тест 1: Инициализация APIConfig")
    print("="*60)
    
    config = APIConfig()
    
    # Проверяем что конфиг создался
    assert config is not None, "APIConfig должен создаться"
    print("✅ APIConfig инициализирован")
    
    # Проверяем атрибуты
    assert hasattr(config, 'gemini_key'), "Должен быть gemini_key"
    assert hasattr(config, 'gemini_model'), "Должен быть gemini_model"
    assert hasattr(config, 'openai_key'), "Должен быть openai_key"
    assert hasattr(config, 'anthropic_key'), "Должен быть anthropic_key"
    print("✅ Все атрибуты на месте")
    
    print()


def test_gemini_key_loading():
    """Тест загрузки Gemini ключа"""
    print("="*60)
    print("🧪 Тест 2: Загрузка Gemini ключа")
    print("="*60)
    
    config = APIConfig()
    
    if config.gemini_key:
        print(f"✅ Gemini ключ загружен: {config.gemini_key[:20]}...")
        assert len(config.gemini_key) > 20, "Ключ должен быть длиннее 20 символов"
        assert config.has_gemini(), "has_gemini() должен вернуть True"
    else:
        print("⚠️  Gemini ключ не установлен (это нормально для тестов)")
        assert not config.has_gemini(), "has_gemini() должен вернуть False"
    
    print()


def test_gemini_model():
    """Тест модели Gemini"""
    print("="*60)
    print("🧪 Тест 3: Модель Gemini")
    print("="*60)
    
    config = APIConfig()
    
    assert config.gemini_model is not None, "Модель должна быть установлена"
    print(f"✅ Модель: {config.gemini_model}")
    
    # Проверяем что это валидная модель
    valid_models = [
        'gemini-1.5-flash',
        'gemini-2.0-flash',
        'gemini-2.5-flash',
        'gemini-2.5-flash-lite',
        'gemini-2.5-pro',
    ]
    
    assert config.gemini_model in valid_models, f"Модель должна быть одной из {valid_models}"
    print(f"✅ Модель валидна")
    
    print()


def test_global_instance():
    """Тест глобального экземпляра"""
    print("="*60)
    print("🧪 Тест 4: Глобальный экземпляр api_config")
    print("="*60)
    
    # Проверяем что глобальный экземпляр существует
    assert api_config is not None, "api_config должен существовать"
    print("✅ Глобальный api_config существует")
    
    # Проверяем что это APIConfig
    assert isinstance(api_config, APIConfig), "api_config должен быть экземпляром APIConfig"
    print("✅ api_config - экземпляр APIConfig")
    
    # Проверяем что у него те же данные
    config = APIConfig()
    assert api_config.gemini_key == config.gemini_key, "Ключи должны совпадать"
    assert api_config.gemini_model == config.gemini_model, "Модели должны совпадать"
    print("✅ Данные совпадают с новым экземпляром")
    
    print()


def test_helper_functions():
    """Тест функций-хелперов"""
    print("="*60)
    print("🧪 Тест 5: Функции-хелперы")
    print("="*60)
    
    from src.utils.api_config import get_gemini_key, get_openai_key, get_anthropic_key
    
    # Проверяем что функции существуют
    assert callable(get_gemini_key), "get_gemini_key должна быть функцией"
    assert callable(get_openai_key), "get_openai_key должна быть функцией"
    assert callable(get_anthropic_key), "get_anthropic_key должна быть функцией"
    print("✅ Все функции-хелперы существуют")
    
    # Проверяем что они возвращают правильные значения
    assert get_gemini_key() == api_config.gemini_key, "get_gemini_key() должна вернуть тот же ключ"
    assert get_openai_key() == api_config.openai_key, "get_openai_key() должна вернуть тот же ключ"
    assert get_anthropic_key() == api_config.anthropic_key, "get_anthropic_key() должна вернуть тот же ключ"
    print("✅ Функции возвращают правильные значения")
    
    print()


def test_print_status():
    """Тест вывода статуса"""
    print("="*60)
    print("🧪 Тест 6: Вывод статуса")
    print("="*60)
    
    config = APIConfig()
    
    # Проверяем что метод существует
    assert hasattr(config, 'print_status'), "Должен быть метод print_status"
    assert callable(config.print_status), "print_status должен быть методом"
    print("✅ Метод print_status существует")
    
    # Вызываем метод (он выведет статус)
    print("\n📊 Вызов print_status():")
    config.print_status()
    
    print()


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ API CONFIG".center(60))
    print("="*60)
    
    tests = [
        test_api_config_initialization,
        test_gemini_key_loading,
        test_gemini_model,
        test_global_instance,
        test_helper_functions,
        test_print_status,
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
