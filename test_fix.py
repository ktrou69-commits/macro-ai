#!/usr/bin/env python3
"""
Быстрый тест исправления ошибки
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_filepath_fix():
    """Тестирование исправления filepath"""
    print("🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЯ FILEPATH")
    print("=" * 50)
    
    try:
        from src.modules.sequence_generator.module import SequenceGeneratorModule
        
        # Инициализация
        generator = SequenceGeneratorModule()
        print("✅ Модуль инициализирован")
        
        # Тестируем простой запрос
        result = generator.generate_and_save("открой калькулятор")
        
        if result and result.get('success'):
            filepath = result.get('filepath')
            print(f"✅ Генерация успешна")
            print(f"📁 Filepath тип: {type(filepath)}")
            print(f"📁 Filepath значение: {filepath}")
            
            # Тестируем преобразование
            if isinstance(filepath, str):
                path_obj = Path(filepath)
                print(f"✅ Преобразование в Path: {path_obj}")
                print(f"✅ Path.stem: {path_obj.stem}")
            else:
                print(f"✅ Уже Path объект: {filepath.stem}")
            
            return True
        else:
            print("❌ Генерация не удалась")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_filepath_fix()
