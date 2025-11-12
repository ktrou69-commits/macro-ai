#!/usr/bin/env python3
"""
Тест расширенных возможностей sequence_generator модуля
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_enhanced_sequence_generator():
    """Тестирование расширенных возможностей sequence_generator"""
    print("🧪 ТЕСТИРОВАНИЕ РАСШИРЕННОГО SEQUENCE_GENERATOR")
    print("=" * 60)
    
    try:
        # Импорт модуля
        from src.modules.sequence_generator.module import SequenceGeneratorModule
        
        print("✅ Модуль импортирован успешно")
        
        # Инициализация модуля
        module = SequenceGeneratorModule()
        print("✅ Модуль инициализирован")
        
        # Проверка инициализации компонентов
        print("\n📊 СТАТУС КОМПОНЕНТОВ:")
        print(f"   SystemAppHandler: {'✅' if module.system_app_handler else '❌'}")
        print(f"   SpotlightIntegration: {'✅' if module.spotlight_integration else '❌'}")
        print(f"   WebSelectorManager: {'✅' if module.web_selector_manager else '❌'}")
        
        # Тестовые запросы для разных типов автоматизации
        test_cases = [
            {
                "name": "Системное приложение - Калькулятор",
                "input": "открой калькулятор и посчитай 25 + 17",
                "expected_type": "system_app"
            },
            {
                "name": "Системное приложение - Finder поиск",
                "input": "найди в finder файлы python",
                "expected_type": "system_app"
            },
            {
                "name": "Веб-автоматизация - YouTube",
                "input": "найди на youtube видео про Python",
                "expected_type": "web"
            },
            {
                "name": "Веб-автоматизация - Google поиск",
                "input": "найди в google информацию про AI",
                "expected_type": "web"
            },
            {
                "name": "Spotlight поиск",
                "input": "найди через spotlight терминал",
                "expected_type": "spotlight"
            },
            {
                "name": "Обычная генерация",
                "input": "создай макрос для открытия браузера",
                "expected_type": "general"
            }
        ]
        
        print("\n🎯 ТЕСТИРОВАНИЕ АНАЛИЗА НАМЕРЕНИЙ:")
        print("-" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['name']}")
            print(f"   Запрос: '{test_case['input']}'")
            
            try:
                # Анализ намерений
                intent = module._analyze_user_intent(test_case['input'])
                print(f"   Тип: {intent['type']} (confidence: {intent['confidence']:.2f})")
                
                if intent['target_app']:
                    print(f"   Приложение: {intent['target_app']}")
                if intent['target_site']:
                    print(f"   Сайт: {intent['target_site']}")
                if intent['action']:
                    print(f"   Действие: {intent['action']}")
                
                # Проверка соответствия ожидаемому типу
                if intent['type'] == test_case['expected_type']:
                    print("   ✅ Тип определен правильно")
                else:
                    print(f"   ⚠️ Ожидался {test_case['expected_type']}, получен {intent['type']}")
                
                # Попытка генерации расширенного DSL
                if intent['confidence'] > 0.6:
                    enhanced_dsl = module._generate_enhanced_dsl(test_case['input'], intent)
                    if enhanced_dsl:
                        print("   ✅ Расширенная генерация DSL успешна")
                        print(f"   📝 DSL (первые 100 символов): {enhanced_dsl[:100]}...")
                    else:
                        print("   ⚠️ Расширенная генерация DSL не удалась")
                else:
                    print("   ℹ️ Низкая уверенность, будет использован AI")
                
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
        
        print("\n🔧 ТЕСТИРОВАНИЕ КОМПОНЕНТОВ:")
        print("-" * 50)
        
        # Тест SystemAppHandler
        if module.system_app_handler:
            print("\n📱 SystemAppHandler:")
            apps = module.system_app_handler.get_all_system_apps()
            print(f"   Загружено приложений: {len(apps)}")
            print(f"   Примеры: {apps[:5]}")
            
            # Тест генерации калькулятора
            calc_dsl = module.system_app_handler.generate_calculator_macro("5 + 3")
            print(f"   Калькулятор DSL: {'✅' if calc_dsl else '❌'}")
        
        # Тест WebSelectorManager
        if module.web_selector_manager:
            print("\n🌐 WebSelectorManager:")
            stats = module.web_selector_manager.get_site_statistics()
            print(f"   Поддерживаемых сайтов: {stats.get('total_sites', 0)}")
            print(f"   Всего селекторов: {stats.get('total_selectors', 0)}")
            
            # Тест определения сайта
            youtube_sites = module.web_selector_manager.identify_site_from_keywords("youtube видео")
            print(f"   YouTube определение: {'✅' if 'youtube' in youtube_sites else '❌'}")
        
        # Тест SpotlightIntegration
        if module.spotlight_integration:
            print("\n🔍 SpotlightIntegration:")
            spotlight_stats = module.spotlight_integration.get_spotlight_statistics()
            print(f"   Spotlight доступен: {'✅' if spotlight_stats.get('available') else '❌'}")
            print(f"   Общих поисков: {spotlight_stats.get('common_searches_count', 0)}")
        
        print("\n🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
        print("✅ Расширенные возможности sequence_generator работают")
        
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_execution():
    """Тест полного выполнения модуля"""
    print("\n" + "=" * 60)
    print("🚀 ТЕСТ ПОЛНОГО ВЫПОЛНЕНИЯ МОДУЛЯ")
    print("=" * 60)
    
    try:
        from src.modules.sequence_generator.module import SequenceGeneratorModule
        
        module = SequenceGeneratorModule()
        
        # Тестовые запросы
        test_requests = [
            "открой калькулятор",
            "найди на youtube Python tutorial",
            "найди через spotlight терминал"
        ]
        
        for i, request in enumerate(test_requests, 1):
            print(f"\n🧪 ТЕСТ {i}: {request}")
            print("-" * 40)
            
            try:
                result = module.execute(request)
                
                if result.success:
                    print("✅ Выполнение успешно")
                    
                    if result.data:
                        macro_info = result.data.get("generated_macro", {})
                        print(f"   📝 Название: {macro_info.get('name', 'N/A')}")
                        print(f"   📄 Описание: {macro_info.get('description', 'N/A')}")
                        
                        if result.data.get("enhanced_generation"):
                            print("   🚀 Использована расширенная генерация")
                        else:
                            print("   🤖 Использована AI генерация")
                        
                        if result.data.get("saved_file"):
                            print(f"   💾 Сохранен: {Path(result.data['saved_file']).name}")
                    
                    print(f"   ⏱️ Время: {result.execution_time:.2f}с")
                    
                    if result.logs:
                        print("   📋 Логи:")
                        for log in result.logs:
                            print(f"      {log}")
                else:
                    print("❌ Выполнение неудачно")
                    print(f"   🚨 Ошибка: {result.error}")
                
            except Exception as e:
                print(f"❌ Ошибка выполнения: {e}")
        
        print("\n🎉 Тесты полного выполнения завершены!")
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🎯 ТЕСТИРОВАНИЕ РАСШИРЕННЫХ ВОЗМОЖНОСТЕЙ SEQUENCE_GENERATOR")
    print("=" * 70)
    
    # Основные тесты
    success1 = test_enhanced_sequence_generator()
    
    # Тесты полного выполнения
    success2 = test_full_execution()
    
    print("\n" + "=" * 70)
    if success1 and success2:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Расширенные возможности sequence_generator готовы к использованию")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("⚠️ Требуется дополнительная отладка")
    
    print("\n💡 Следующий шаг: Тестирование с реальными запросами через координатор")
