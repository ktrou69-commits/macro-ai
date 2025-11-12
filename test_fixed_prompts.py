#!/usr/bin/env python3
"""
Тест исправленных промптов
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_fixed_prompts():
    """Тестирование исправленных промптов"""
    print("🧪 ТЕСТИРОВАНИЕ ИСПРАВЛЕННЫХ ПРОМПТОВ")
    print("=" * 60)
    
    try:
        from src.modules.sequence_generator.module import SequenceGeneratorModule
        
        # Инициализация
        generator = SequenceGeneratorModule()
        print("✅ Модуль инициализирован")
        
        # Тестируем веб-автоматизацию Amazon
        print(f"\n🌐 Тестируем веб-автоматизацию Amazon...")
        result = generator.generate_and_save("найди ноутбуки на Amazon")
        
        if result and result.get('success'):
            filepath = result.get('filepath')
            print(f"✅ Макрос сгенерирован: {Path(filepath).name}")
            
            # Читаем содержимое
            if filepath and os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"\n📄 Содержимое макроса:")
                print("-" * 40)
                print(content)
                print("-" * 40)
                
                # Проверяем правильные команды
                correct_commands = []
                wrong_commands = []
                
                if "selenium_init" in content:
                    correct_commands.append("selenium_init")
                if "selenium_click" in content:
                    correct_commands.append("selenium_click")
                if "selenium_type" in content:
                    correct_commands.append("selenium_type")
                
                # Проверяем неправильные команды
                if "navigate" in content:
                    wrong_commands.append("navigate")
                if "click_element" in content:
                    wrong_commands.append("click_element")
                if "fill_field" in content:
                    wrong_commands.append("fill_field")
                if "open_app" in content and "@system" not in content:
                    wrong_commands.append("open_app (без @system)")
                
                print(f"\n✅ Правильные команды: {correct_commands}")
                if wrong_commands:
                    print(f"❌ Неправильные команды: {wrong_commands}")
                    return False
                else:
                    print(f"✅ Неправильных команд не найдено!")
                
                return True
            else:
                print("❌ Файл макроса не найден")
                return False
        else:
            print("❌ Генерация не удалась")
            if result and result.get('error'):
                print(f"   Ошибка: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_prompts()
    
    print(f"\n{'='*60}")
    if success:
        print("🎉 ТЕСТ ПРОМПТОВ ПРОЙДЕН УСПЕШНО!")
        print("✅ AI теперь генерирует правильные команды DSL!")
    else:
        print("❌ ТЕСТ НЕ ПРОЙДЕН")
        print("🔧 Требуется дополнительная отладка промптов")
    print("="*60)
