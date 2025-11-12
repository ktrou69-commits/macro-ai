#!/usr/bin/env python3
"""
Тестирование интеграции нового модуля с основным приложением
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_new_generator():
    """Тестирование нового генератора напрямую"""
    print("🧪 ТЕСТИРОВАНИЕ НОВОГО ГЕНЕРАТОРА")
    print("=" * 60)
    
    try:
        from src.modules.sequence_generator.module import SequenceGeneratorModule
        
        # Инициализация
        generator = SequenceGeneratorModule()
        print("✅ Модуль инициализирован")
        
        # Тестовые запросы
        test_cases = [
            "открой калькулятор",
            "найди на YouTube видео про Python",
            "создай макрос для покупки товаров с проверкой цен"
        ]
        
        for i, test_input in enumerate(test_cases, 1):
            print(f"\n🧪 ТЕСТ {i}: {test_input}")
            print("-" * 40)
            
            try:
                # Используем новый метод
                result = generator.generate_and_save(test_input)
                
                if result and result.get('success'):
                    print("✅ Генерация успешна")
                    
                    # Показываем анализ
                    if result.get('intent_analysis'):
                        intent = result['intent_analysis']
                        print(f"🧠 Намерение: {intent.get('type')} (уверенность: {intent.get('confidence')})")
                    
                    if result.get('complexity_analysis'):
                        complexity = result['complexity_analysis']
                        print(f"📊 Сложность: {complexity.get('complexity_level')}")
                        print(f"🔧 Расширенные возможности: {complexity.get('requires_advanced_features')}")
                    
                    if result.get('filepath'):
                        print(f"📁 Файл: {result['filepath']}")
                    
                    if result.get('dsl_stats'):
                        stats = result['dsl_stats']
                        print(f"📋 DSL статистика: блоков={stats.get('total_blocks', 0)}, условия={stats.get('has_conditionals', False)}")
                    
                else:
                    print("❌ Генерация не удалась")
                    if result and result.get('error'):
                        print(f"   Ошибка: {result['error']}")
                
            except Exception as e:
                print(f"❌ Ошибка в тесте: {e}")
        
        print(f"\n🎉 Тестирование завершено!")
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False

def show_integration_status():
    """Показать статус интеграции"""
    print(f"\n📊 СТАТУС ИНТЕГРАЦИИ")
    print("=" * 40)
    
    try:
        from src.modules.sequence_generator.module import SequenceGeneratorModule
        
        module = SequenceGeneratorModule()
        
        # Проверяем компоненты
        components = [
            ("SystemAppHandler", hasattr(module, 'system_app_handler') and module.system_app_handler),
            ("WebSelectorManager", hasattr(module, 'web_selector_manager') and module.web_selector_manager),
            ("ContextAwarePrompts", hasattr(module, 'context_prompts') and module.context_prompts),
            ("EnhancedDSLParser", hasattr(module, 'enhanced_dsl_parser') and module.enhanced_dsl_parser),
            ("AdvancedPrompts", hasattr(module, 'advanced_prompts') and module.advanced_prompts)
        ]
        
        available = sum(1 for _, status in components if status)
        total = len(components)
        
        print(f"🔧 Доступные компоненты: {available}/{total}")
        
        for name, status in components:
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {name}")
        
        print(f"📈 Готовность: {(available/total)*100:.1f}%")
        
        if available == total:
            print("🎉 ВСЕ КОМПОНЕНТЫ ДОСТУПНЫ!")
        else:
            print("⚠️ Некоторые компоненты недоступны")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки статуса: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ НОВОГО МОДУЛЯ")
    print("=" * 80)
    
    # Показываем статус
    show_integration_status()
    
    # Тестируем генератор
    test_new_generator()
    
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    print(f"   1. Запустите: python3 src/main.py")
    print(f"   2. Выберите опцию 6 (Генерация последовательности)")
    print(f"   3. Попробуйте простой запрос: 'открой калькулятор'")
    print(f"   4. Попробуйте сложный запрос: 'создай макрос с условиями'")
    print(f"   5. Наблюдайте за новыми возможностями!")
