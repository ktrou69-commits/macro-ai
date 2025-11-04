#!/usr/bin/env python3
"""
test_setup.py
Проверка установки и готовности системы к работе
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Проверка версии Python"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (требуется 3.10+)")
        return False

def check_dependencies():
    """Проверка установленных зависимостей"""
    required = {
        'numpy': 'numpy',
        'PIL': 'pillow',
        'cv2': 'opencv-python',
        'pyautogui': 'pyautogui',
    }
    
    optional = {
        'ultralytics': 'ultralytics (YOLO)',
        'torch': 'pytorch',
    }
    
    print("\n📦 Основные зависимости:")
    all_ok = True
    for module, name in required.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - установи: pip install {name}")
            all_ok = False
    
    print("\n📦 Опциональные зависимости:")
    for module, name in optional.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ⚠️  {name} - не установлен (опционально)")
    
    return all_ok

def check_file_structure():
    """Проверка структуры файлов"""
    required_files = [
        'macro_ai.py',
        'requirements.txt',
        'README.md',
        'data.yaml',
    ]
    
    required_dirs = [
        'models',
        'utils',
        'examples',
    ]
    
    print("\n📁 Структура проекта:")
    all_ok = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - отсутствует")
            all_ok = False
    
    for dir in required_dirs:
        if os.path.isdir(dir):
            print(f"  ✅ {dir}/")
        else:
            print(f"  ⚠️  {dir}/ - отсутствует")
    
    return all_ok

def check_template():
    """Проверка наличия шаблона"""
    template_path = "models/button.png"
    
    print("\n🖼️  Шаблон кнопки:")
    if os.path.exists(template_path):
        import cv2
        img = cv2.imread(template_path)
        if img is not None:
            print(f"  ✅ {template_path} ({img.shape[1]}x{img.shape[0]} px)")
            return True
        else:
            print(f"  ❌ {template_path} - поврежден")
            return False
    else:
        print(f"  ⚠️  {template_path} - не найден")
        print(f"     Создай шаблон: python utils/capture_button.py")
        return False

def check_permissions():
    """Проверка разрешений macOS"""
    print("\n🔐 Разрешения macOS:")
    print("  ℹ️  Проверь вручную в System Settings:")
    print("     • Privacy & Security → Screen Recording → Terminal")
    print("     • Privacy & Security → Accessibility → Terminal")
    print("  ⚠️  После добавления перезапусти Terminal!")
    return True

def test_screenshot():
    """Тест захвата экрана"""
    print("\n📸 Тест захвата экрана:")
    try:
        import pyautogui
        img = pyautogui.screenshot()
        print(f"  ✅ Скриншот работает ({img.size})")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        print(f"     Проверь разрешение Screen Recording")
        return False

def test_click():
    """Тест клика (безопасный)"""
    print("\n🖱️  Тест клика:")
    try:
        import pyautogui
        # Получаем текущую позицию (не кликаем)
        x, y = pyautogui.position()
        print(f"  ✅ PyAutoGUI работает (позиция мыши: {x}, {y})")
        print(f"     Для теста клика запусти: python macro_ai.py --template")
        return True
    except Exception as e:
        print(f"  ❌ Ошибка: {e}")
        print(f"     Проверь разрешение Accessibility")
        return False

def check_apple_silicon():
    """Проверка Apple Silicon и MPS"""
    print("\n🍎 Apple Silicon:")
    try:
        import platform
        if platform.processor() == 'arm':
            print(f"  ✅ Обнаружен Apple Silicon (M1/M2/M3)")
            
            # Проверка MPS
            try:
                import torch
                if torch.backends.mps.is_available():
                    print(f"  ✅ MPS доступен (GPU ускорение)")
                    print(f"     Используй: --device mps")
                else:
                    print(f"  ⚠️  MPS недоступен")
            except:
                print(f"  ⚠️  PyTorch не установлен (MPS недоступен)")
        else:
            print(f"  ℹ️  Intel процессор")
    except Exception as e:
        print(f"  ⚠️  Не удалось определить: {e}")
    
    return True

def main():
    print("\n" + "="*60)
    print("🔍 Проверка готовности системы")
    print("="*60)
    
    checks = [
        ("Python версия", check_python_version),
        ("Зависимости", check_dependencies),
        ("Структура файлов", check_file_structure),
        ("Шаблон", check_template),
        ("Разрешения", check_permissions),
        ("Захват экрана", test_screenshot),
        ("Клик мыши", test_click),
        ("Apple Silicon", check_apple_silicon),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Ошибка при проверке '{name}': {e}")
            results.append((name, False))
    
    # Итоги
    print("\n" + "="*60)
    print("📊 Итоги проверки:")
    print("="*60)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    # Рекомендации
    print("\n" + "="*60)
    print("💡 Следующие шаги:")
    print("="*60)
    
    if not os.path.exists("models/button.png"):
        print("  1. Создай шаблон: python utils/capture_button.py")
    else:
        print("  1. ✅ Шаблон готов")
    
    print("  2. Проверь разрешения в System Settings")
    print("  3. Запусти макрос: python macro_ai.py --template")
    print("="*60)

if __name__ == "__main__":
    main()
