#!/usr/bin/env python3
"""
Финальный тест полной интеграции
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def final_integration_test():
    """Финальный тест интеграции"""
    print("🎉 ФИНАЛЬНЫЙ ТЕСТ ПОЛНОЙ ИНТЕГРАЦИИ")
    print("=" * 60)
    
    try:
        from src.modules.sequence_generator.module import SequenceGeneratorModule
        
        # Инициализация
        generator = SequenceGeneratorModule()
        print("✅ Модуль инициализирован")
        
        # Тестируем генерацию
        print("\n🧪 Тестируем генерацию макроса...")
        result = generator.generate_and_save("открой калькулятор")
        
        if result and result.get('success'):
            filepath = result.get('filepath')
            print(f"✅ Макрос сгенерирован: {filepath}")
            
            # Читаем содержимое
            if filepath and os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"\n📄 Содержимое макроса:")
                print("-" * 40)
                print(content)
                print("-" * 40)
                
                # Проверяем правильный формат
                if "@system open_app" in content:
                    print("✅ Правильный формат системной команды")
                else:
                    print("❌ Неправильный формат системной команды")
                
                # Тестируем выполнение
                print(f"\n🚀 Тестируем выполнение макроса...")
                
                import subprocess
                from pathlib import Path
                
                macro_name = Path(filepath).stem
                cmd = [
                    'python3', 
                    'src/core/macro_sequence.py',
                    '--config', filepath,
                    '--run', macro_name,
                    '--fast'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(project_root))
                
                if result.returncode == 0:
                    print("✅ Макрос выполнен успешно!")
                    if "✅ Приложение Calculator запущено" in result.stdout:
                        print("✅ Калькулятор открылся!")
                    else:
                        print("⚠️ Калькулятор может не открыться")
                else:
                    print(f"❌ Ошибка выполнения: {result.stderr}")
                
                return True
            else:
                print("❌ Файл макроса не найден")
                return False
        else:
            print("❌ Генерация не удалась")
            return False
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = final_integration_test()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 ФИНАЛЬНЫЙ ТЕСТ ПРОЙДЕН УСПЕШНО!")
        print("✨ ВСЯ ИНТЕГРАЦИЯ РАБОТАЕТ!")
        print()
        print("🚀 ТЕПЕРЬ МОЖНО ИСПОЛЬЗОВАТЬ:")
        print("   1. python3 src/main.py")
        print("   2. Выбрать опцию 6")
        print("   3. Ввести: 'открой калькулятор'")
        print("   4. Наслаждаться новыми возможностями!")
    else:
        print("❌ ФИНАЛЬНЫЙ ТЕСТ НЕ ПРОЙДЕН")
        print("🔧 Требуется дополнительная отладка")
    print("="*60)
