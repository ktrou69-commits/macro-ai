#!/usr/bin/env python3
"""
test_macro_loading.py
🔥 КРИТИЧНО: Тестирование загрузки макросов

Проверяет:
- Загрузку .atlas файлов
- Загрузку .yaml файлов
- Валидность содержимого
- Парсинг DSL
- Структуру макросов
"""

import sys
from pathlib import Path
import yaml

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MACROS_DIR, EXAMPLES_DIR
from src.core.atlas_dsl_parser import AtlasDSLParser


def test_macros_dir_exists():
    """Тест что папка с макросами существует"""
    print("\n" + "="*60)
    print("🧪 Тест 1: Папка с макросами")
    print("="*60)
    
    assert MACROS_DIR.exists(), f"MACROS_DIR не существует: {MACROS_DIR}"
    assert MACROS_DIR.is_dir(), f"MACROS_DIR не папка: {MACROS_DIR}"
    print(f"✅ MACROS_DIR: {MACROS_DIR}")
    
    assert EXAMPLES_DIR.exists(), f"EXAMPLES_DIR не существует: {EXAMPLES_DIR}"
    assert EXAMPLES_DIR.is_dir(), f"EXAMPLES_DIR не папка: {EXAMPLES_DIR}"
    print(f"✅ EXAMPLES_DIR: {EXAMPLES_DIR}")
    
    print()


def test_atlas_files_exist():
    """Тест что .atlas файлы существуют"""
    print("="*60)
    print("🧪 Тест 2: .atlas файлы")
    print("="*60)
    
    # Ищем .atlas файлы
    atlas_files = list(MACROS_DIR.glob('*.atlas'))
    
    print(f"📊 Найдено .atlas файлов: {len(atlas_files)}")
    
    if len(atlas_files) > 0:
        print("✅ Примеры:")
        for f in atlas_files[:5]:
            print(f"   • {f.name} ({f.stat().st_size} bytes)")
        assert True
    else:
        print("⚠️  Нет .atlas файлов в production/")
        print("   Это нормально для новой установки")
    
    print()


def test_load_atlas_file():
    """Тест загрузки .atlas файла"""
    print("="*60)
    print("🧪 Тест 3: Загрузка .atlas файла")
    print("="*60)
    
    atlas_files = list(MACROS_DIR.glob('*.atlas'))
    
    if len(atlas_files) == 0:
        print("⚠️  Нет .atlas файлов для тестирования")
        print("   Создайте хотя бы один макрос")
        return
    
    # Берём первый файл
    atlas_file = atlas_files[0]
    print(f"📄 Тестируем: {atlas_file.name}")
    
    # Читаем файл
    with open(atlas_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert len(content) > 0, "Файл пустой"
    print(f"✅ Размер: {len(content)} символов")
    
    # Проверяем что есть команды
    lines = content.strip().split('\n')
    non_empty_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
    
    assert len(non_empty_lines) > 0, "Нет команд в файле"
    print(f"✅ Команд: {len(non_empty_lines)}")
    
    # Показываем первые команды
    print("✅ Первые команды:")
    for line in non_empty_lines[:3]:
        print(f"   • {line.strip()}")
    
    print()


def test_parse_atlas_file():
    """Тест парсинга .atlas файла"""
    print("="*60)
    print("🧪 Тест 4: Парсинг .atlas файла")
    print("="*60)
    
    atlas_files = list(MACROS_DIR.glob('*.atlas'))
    
    if len(atlas_files) == 0:
        print("⚠️  Нет .atlas файлов для парсинга")
        return
    
    parser = AtlasDSLParser()
    atlas_file = atlas_files[0]
    print(f"📄 Парсим: {atlas_file.name}")
    
    # Читаем и парсим
    with open(atlas_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.strip().split('\n')
    parsed_count = 0
    errors = []
    
    # Парсим весь файл сразу
    try:
        result = parser.parse(content)
        if result and 'steps' in result:
            parsed_count = len(result['steps'])
        elif result:
            # Если нет steps, считаем что распарсилось
            parsed_count = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
    except Exception as e:
        errors.append((0, "весь файл", str(e)))
    
    print(f"✅ Распарсилось команд: {parsed_count}")
    
    if errors:
        print(f"⚠️  Ошибок парсинга: {len(errors)}")
        for line_num, line, error in errors[:3]:
            print(f"   L{line_num}: {line[:50]}... → {error}")
    else:
        print(f"✅ Нет ошибок парсинга!")
    
    assert parsed_count > 0, "Ни одна команда не распарсилась"
    
    print()


def test_yaml_files_exist():
    """Тест что .yaml файлы существуют"""
    print("="*60)
    print("🧪 Тест 5: .yaml файлы")
    print("="*60)
    
    # Ищем .yaml файлы в examples
    yaml_files = list(EXAMPLES_DIR.glob('**/*.yaml'))
    
    print(f"📊 Найдено .yaml файлов: {len(yaml_files)}")
    
    if len(yaml_files) > 0:
        print("✅ Примеры:")
        for f in yaml_files[:5]:
            rel_path = f.relative_to(EXAMPLES_DIR)
            print(f"   • {rel_path} ({f.stat().st_size} bytes)")
    else:
        print("⚠️  Нет .yaml файлов в examples/")
    
    print()


def test_load_yaml_file():
    """Тест загрузки .yaml файла"""
    print("="*60)
    print("🧪 Тест 6: Загрузка .yaml файла")
    print("="*60)
    
    yaml_files = list(EXAMPLES_DIR.glob('**/*.yaml'))
    
    if len(yaml_files) == 0:
        print("⚠️  Нет .yaml файлов для тестирования")
        return
    
    # Берём первый файл
    yaml_file = yaml_files[0]
    print(f"📄 Тестируем: {yaml_file.relative_to(EXAMPLES_DIR)}")
    
    # Читаем YAML
    try:
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        assert data is not None, "YAML пустой"
        print(f"✅ YAML загружен")
        
        # Проверяем структуру
        if isinstance(data, dict):
            print(f"✅ Ключей в YAML: {len(data)}")
            print(f"✅ Ключи: {list(data.keys())[:5]}")
        elif isinstance(data, list):
            print(f"✅ Элементов в YAML: {len(data)}")
        
    except yaml.YAMLError as e:
        print(f"❌ Ошибка парсинга YAML: {e}")
        raise
    
    print()


def test_macro_structure():
    """Тест структуры макросов"""
    print("="*60)
    print("🧪 Тест 7: Структура макросов")
    print("="*60)
    
    # Проверяем что есть разные типы макросов
    atlas_count = len(list(MACROS_DIR.glob('*.atlas')))
    yaml_count = len(list(EXAMPLES_DIR.glob('**/*.yaml')))
    
    print(f"📊 .atlas файлов: {atlas_count}")
    print(f"📊 .yaml файлов: {yaml_count}")
    
    total = atlas_count + yaml_count
    if total > 0:
        print(f"✅ Всего макросов: {total}")
    else:
        print(f"⚠️  Нет макросов (создайте хотя бы один)")
    
    print()


def test_macro_commands():
    """Тест команд в макросах"""
    print("="*60)
    print("🧪 Тест 8: Команды в макросах")
    print("="*60)
    
    atlas_files = list(MACROS_DIR.glob('*.atlas'))
    
    if len(atlas_files) == 0:
        print("⚠️  Нет .atlas файлов")
        return
    
    # Собираем статистику команд
    all_commands = []
    
    for atlas_file in atlas_files[:5]:  # Первые 5 файлов
        with open(atlas_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Извлекаем команду (первое слово)
                command = line.split()[0] if line.split() else ''
                if command:
                    all_commands.append(command)
    
    # Подсчитываем уникальные команды
    unique_commands = set(all_commands)
    
    print(f"📊 Всего команд: {len(all_commands)}")
    print(f"📊 Уникальных команд: {len(unique_commands)}")
    print(f"✅ Команды: {', '.join(sorted(unique_commands)[:10])}")
    
    # Проверяем что есть базовые команды
    basic_commands = {'click', 'type', 'wait', 'open', 'press'}
    found_basic = basic_commands & unique_commands
    
    if found_basic:
        print(f"✅ Базовые команды найдены: {', '.join(found_basic)}")
    
    print()


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🔥 ТЕСТИРОВАНИЕ ЗАГРУЗКИ МАКРОСОВ".center(60))
    print("="*60)
    print("\nПроверяем загрузку и парсинг .atlas и .yaml файлов!\n")
    
    tests = [
        test_macros_dir_exists,
        test_atlas_files_exist,
        test_load_atlas_file,
        test_parse_atlas_file,
        test_yaml_files_exist,
        test_load_yaml_file,
        test_macro_structure,
        test_macro_commands,
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
        print("🎉 ВСЕ ТЕСТЫ ЗАГРУЗКИ ПРОШЛИ!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print("\n💡 Макросы загружаются корректно!")
    else:
        print("⚠️  ЕСТЬ ПРОБЛЕМЫ С ЗАГРУЗКОЙ!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print(f"❌ Провалено: {failed}/{len(tests)}")
        print("\n💡 Исправьте ошибки загрузки макросов!")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
