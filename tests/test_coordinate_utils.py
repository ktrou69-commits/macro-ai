#!/usr/bin/env python3
"""
test_coordinate_utils.py
Тестирование утилит для поиска координат
"""

import sys
import importlib.util


def test_import(module_path, module_name):
    """Тест импорта модуля"""
    print(f"\n{'='*60}")
    print(f"🧪 Тестирование: {module_name}")
    print('='*60)
    
    try:
        # Загружаем модуль
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        print(f"✅ Импорт успешен")
        
        # Проверяем наличие основного класса
        if hasattr(module, 'CoordinateFinder'):
            print(f"✅ Класс CoordinateFinder найден")
        elif hasattr(module, 'AdvancedCoordinateFinder'):
            print(f"✅ Класс AdvancedCoordinateFinder найден")
        else:
            print(f"⚠️  Основной класс не найден")
        
        # Проверяем методы
        if hasattr(module, 'CoordinateFinder'):
            cls = module.CoordinateFinder
        elif hasattr(module, 'AdvancedCoordinateFinder'):
            cls = module.AdvancedCoordinateFinder
        else:
            print(f"❌ Не удалось найти класс для проверки методов")
            return False
        
        # Проверяем наличие метода on_mouse_move
        if hasattr(cls, 'on_mouse_move'):
            print(f"✅ Метод on_mouse_move найден (исправление pynput)")
        else:
            print(f"❌ Метод on_mouse_move не найден")
            return False
        
        # Проверяем наличие метода on_press
        if hasattr(cls, 'on_press'):
            print(f"✅ Метод on_press найден")
        else:
            print(f"❌ Метод on_press не найден")
            return False
        
        # Проверяем наличие метода run
        if hasattr(cls, 'run'):
            print(f"✅ Метод run найден")
        else:
            print(f"❌ Метод run не найден")
            return False
        
        print(f"\n✅ Все проверки пройдены!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ COORDINATE UTILS")
    print("="*60)
    
    results = []
    
    # Тест 1: coordinate_finder.py
    result1 = test_import(
        'utils/coordinate_finder.py',
        'coordinate_finder'
    )
    results.append(('coordinate_finder.py', result1))
    
    # Тест 2: advanced_coordinate_finder.py
    result2 = test_import(
        'utils/advanced_coordinate_finder.py',
        'advanced_coordinate_finder'
    )
    results.append(('advanced_coordinate_finder.py', result2))
    
    # Итоги
    print("\n" + "="*60)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*60 + "\n")
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status}  {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
