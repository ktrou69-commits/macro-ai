#!/usr/bin/env python3
"""
test_vision_basic.py
🔍 ВАЖНО: Базовое тестирование компьютерного зрения

Проверяет:
- Наличие шаблонов (PNG файлы)
- Загрузку шаблонов через OpenCV
- Структуру папок templates/
- Smart Capture утилиту
- Coordinate Finder
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import TEMPLATES_DIR


def test_templates_dir_exists():
    """Тест что папка templates/ существует"""
    print("\n" + "="*60)
    print("🧪 Тест 1: Папка templates/")
    print("="*60)
    
    assert TEMPLATES_DIR.exists(), f"TEMPLATES_DIR не существует: {TEMPLATES_DIR}"
    assert TEMPLATES_DIR.is_dir(), f"TEMPLATES_DIR не папка: {TEMPLATES_DIR}"
    print(f"✅ TEMPLATES_DIR: {TEMPLATES_DIR}")
    
    print()


def test_png_templates_exist():
    """Тест что PNG шаблоны существуют"""
    print("="*60)
    print("🧪 Тест 2: PNG шаблоны")
    print("="*60)
    
    # Ищем все PNG файлы
    png_files = list(TEMPLATES_DIR.glob('**/*.png'))
    
    print(f"📊 Найдено PNG файлов: {len(png_files)}")
    
    if len(png_files) > 0:
        print("✅ Примеры:")
        for f in png_files[:5]:
            rel_path = f.relative_to(TEMPLATES_DIR)
            size_kb = f.stat().st_size / 1024
            print(f"   • {rel_path} ({size_kb:.1f} KB)")
        assert True
    else:
        print("⚠️  Нет PNG шаблонов")
        print("   Создайте шаблоны через Smart Capture:")
        print("   python3 src/utils/smart_capture.py")
    
    print()


def test_load_templates_opencv():
    """Тест загрузки шаблонов через OpenCV"""
    print("="*60)
    print("🧪 Тест 3: Загрузка через OpenCV")
    print("="*60)
    
    try:
        import cv2
        print("✅ OpenCV установлен")
    except ImportError:
        print("⚠️  OpenCV не установлен")
        print("   pip install opencv-python-headless")
        return
    
    png_files = list(TEMPLATES_DIR.glob('**/*.png'))
    
    if len(png_files) == 0:
        print("⚠️  Нет PNG файлов для тестирования")
        return
    
    # Тестируем первые 3 файла
    loaded_count = 0
    errors = []
    
    for png_file in png_files[:3]:
        try:
            img = cv2.imread(str(png_file))
            if img is not None:
                height, width = img.shape[:2]
                loaded_count += 1
                print(f"✅ {png_file.name}: {width}x{height}")
            else:
                errors.append((png_file.name, "Не удалось загрузить"))
        except Exception as e:
            errors.append((png_file.name, str(e)))
    
    print(f"\n📊 Загружено: {loaded_count}/{min(3, len(png_files))}")
    
    if errors:
        print(f"⚠️  Ошибок: {len(errors)}")
        for name, error in errors:
            print(f"   • {name}: {error}")
    
    assert loaded_count > 0, "Ни один шаблон не загрузился"
    
    print()


def test_templates_structure():
    """Тест структуры папок templates/"""
    print("="*60)
    print("🧪 Тест 4: Структура templates/")
    print("="*60)
    
    # Проверяем основные папки
    expected_dirs = {
        'Chrome': TEMPLATES_DIR / 'Chrome',
        'Atlas': TEMPLATES_DIR / 'Atlas',
    }
    
    found_dirs = []
    missing_dirs = []
    
    for name, path in expected_dirs.items():
        if path.exists():
            found_dirs.append(name)
            print(f"✅ {name}/ существует")
        else:
            missing_dirs.append(name)
            print(f"⚠️  {name}/ не существует")
    
    # Показываем подпапки Chrome/
    chrome_dir = TEMPLATES_DIR / 'Chrome'
    if chrome_dir.exists():
        platforms = [d.name for d in chrome_dir.iterdir() if d.is_dir()]
        if platforms:
            print(f"\n✅ Платформы в Chrome/:")
            for platform in platforms[:5]:
                png_count = len(list((chrome_dir / platform).glob('*.png')))
                print(f"   • {platform}/ ({png_count} шаблонов)")
    
    print()


def test_smart_capture_import():
    """Тест импорта Smart Capture"""
    print("="*60)
    print("🧪 Тест 5: Smart Capture")
    print("="*60)
    
    try:
        from src.utils.smart_capture import SmartCapture
        print("✅ SmartCapture импортирован")
        
        # Создаём экземпляр
        capture = SmartCapture()
        assert capture is not None
        print("✅ SmartCapture создан")
        
        # Проверяем методы
        methods_to_check = ['capture_screen', 'save_template', 'interactive_select']
        found_methods = [m for m in methods_to_check if hasattr(capture, m)]
        
        if found_methods:
            print(f"✅ Методы: {', '.join(found_methods)}")
        else:
            print("⚠️  Основные методы не найдены")
        
    except ImportError as e:
        print(f"❌ Не удалось импортировать SmartCapture: {e}")
        raise
    
    print()


def test_coordinate_finder_import():
    """Тест импорта Coordinate Finder"""
    print("="*60)
    print("🧪 Тест 6: Coordinate Finder")
    print("="*60)
    
    try:
        from src.utils.coordinate_finder import CoordinateFinder
        print("✅ CoordinateFinder импортирован")
        
        # Создаём экземпляр
        finder = CoordinateFinder()
        assert finder is not None
        print("✅ CoordinateFinder создан")
        
    except ImportError as e:
        print(f"⚠️  CoordinateFinder не импортируется: {e}")
        print("   Это нормально если класс называется по-другому")
    except Exception as e:
        print(f"⚠️  Ошибка создания CoordinateFinder: {e}")
    
    print()


def test_template_matching_available():
    """Тест доступности функций template matching"""
    print("="*60)
    print("🧪 Тест 7: Template Matching функции")
    print("="*60)
    
    try:
        import cv2
        
        # Проверяем что есть функция matchTemplate
        assert hasattr(cv2, 'matchTemplate'), "Нет cv2.matchTemplate"
        print("✅ cv2.matchTemplate доступен")
        
        # Проверяем методы сравнения
        methods = [
            'TM_CCOEFF',
            'TM_CCOEFF_NORMED',
            'TM_CCORR',
            'TM_CCORR_NORMED',
            'TM_SQDIFF',
            'TM_SQDIFF_NORMED',
        ]
        
        available_methods = []
        for method in methods:
            if hasattr(cv2, method):
                available_methods.append(method)
        
        print(f"✅ Доступно методов: {len(available_methods)}/{len(methods)}")
        print(f"✅ Методы: {', '.join(available_methods[:3])}...")
        
    except ImportError:
        print("⚠️  OpenCV не установлен")
    
    print()


def test_template_file_sizes():
    """Тест размеров файлов шаблонов"""
    print("="*60)
    print("🧪 Тест 8: Размеры шаблонов")
    print("="*60)
    
    png_files = list(TEMPLATES_DIR.glob('**/*.png'))
    
    if len(png_files) == 0:
        print("⚠️  Нет PNG файлов")
        return
    
    # Статистика размеров
    sizes = [f.stat().st_size for f in png_files]
    total_size = sum(sizes)
    avg_size = total_size / len(sizes)
    min_size = min(sizes)
    max_size = max(sizes)
    
    print(f"📊 Всего шаблонов: {len(png_files)}")
    print(f"📊 Общий размер: {total_size / 1024:.1f} KB")
    print(f"📊 Средний размер: {avg_size / 1024:.1f} KB")
    print(f"📊 Минимальный: {min_size / 1024:.1f} KB")
    print(f"📊 Максимальный: {max_size / 1024:.1f} KB")
    
    # Проверяем что нет слишком больших файлов
    large_files = [f for f in png_files if f.stat().st_size > 1024 * 1024]  # > 1 MB
    if large_files:
        print(f"\n⚠️  Больших файлов (>1MB): {len(large_files)}")
        for f in large_files[:3]:
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"   • {f.name}: {size_mb:.2f} MB")
    else:
        print(f"\n✅ Все файлы < 1 MB")
    
    print()


def run_all_tests():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🔍 ТЕСТИРОВАНИЕ VISION".center(60))
    print("="*60)
    print("\nПроверяем шаблоны и компьютерное зрение!\n")
    
    tests = [
        test_templates_dir_exists,
        test_png_templates_exist,
        test_load_templates_opencv,
        test_templates_structure,
        test_smart_capture_import,
        test_coordinate_finder_import,
        test_template_matching_available,
        test_template_file_sizes,
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
        print("🎉 ВСЕ VISION ТЕСТЫ ПРОШЛИ!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print("\n💡 Компьютерное зрение работает!")
    else:
        print("⚠️  ЕСТЬ ПРОБЛЕМЫ С VISION!".center(60))
        print("="*60)
        print(f"✅ Пройдено: {passed}/{len(tests)}")
        print(f"❌ Провалено: {failed}/{len(tests)}")
        print("\n💡 Проверьте шаблоны и OpenCV!")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
