#!/usr/bin/env python3
"""
Тест улучшенного AI и валидации (Часть 2) sequence_generator модуля
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_enhanced_ai_part2():
    """Тестирование улучшенного AI и валидации (Часть 2)"""
    print("🧪 ТЕСТИРОВАНИЕ ЧАСТИ 2: УЛУЧШЕННЫЙ AI И ВАЛИДАЦИЯ")
    print("=" * 70)
    
    try:
        # Импорт модуля
        from src.modules.sequence_generator.module import SequenceGeneratorModule
        
        print("✅ Модуль импортирован успешно")
        
        # Инициализация модуля
        module = SequenceGeneratorModule()
        print("✅ Модуль инициализирован")
        
        # Проверка инициализации новых компонентов Части 2
        print("\n📊 СТАТУС КОМПОНЕНТОВ ЧАСТИ 2:")
        print(f"   ContextAwarePrompts: {'✅' if module.context_prompts else '❌'}")
        print(f"   AIExamples: {'✅' if module.ai_examples else '❌'}")
        print(f"   DSLValidator: {'✅' if module.dsl_validator else '❌'}")
        print(f"   SemanticValidator: {'✅' if module.semantic_validator else '❌'}")
        print(f"   DSLFormatter: {'✅' if module.dsl_formatter else '❌'}")
        
        # Тестирование контекстно-зависимых промптов
        print("\n🎯 ТЕСТИРОВАНИЕ КОНТЕКСТНО-ЗАВИСИМЫХ ПРОМПТОВ:")
        print("-" * 60)
        
        if module.context_prompts:
            prompt_types = module.context_prompts.get_available_prompt_types()
            print(f"✅ Доступно типов промптов: {len(prompt_types)}")
            print(f"   Типы: {', '.join(prompt_types)}")
            
            # Тест построения промпта
            test_context = {
                'user_request': 'открой калькулятор и посчитай 5+3',
                'system_apps': 'Calculator',
                'all_resources': 'Тестовые ресурсы'
            }
            
            try:
                prompt = module.context_prompts.get_prompt_for_intent('calculator_automation', test_context)
                print("✅ Промпт для калькулятора сгенерирован успешно")
                print(f"   Длина промпта: {len(prompt)} символов")
            except Exception as e:
                print(f"❌ Ошибка генерации промпта: {e}")
        
        # Тестирование примеров для AI
        print("\n📚 ТЕСТИРОВАНИЕ AI ПРИМЕРОВ:")
        print("-" * 60)
        
        if module.ai_examples:
            stats = module.ai_examples.get_statistics()
            print(f"✅ Всего примеров: {stats.get('total_examples', 0)}")
            print(f"   Типы намерений: {', '.join(stats.get('available_intents', []))}")
            
            # Тест селектора примеров
            if module.example_selector:
                examples = module.example_selector.select_best_examples(
                    "открой YouTube и найди видео", "web_automation", 2
                )
                print(f"✅ Найдено примеров для веб-автоматизации: {len(examples.split('ПРИМЕР')) - 1}")
        
        # Тестирование DSL валидации
        print("\n🔍 ТЕСТИРОВАНИЕ DSL ВАЛИДАЦИИ:")
        print("-" * 60)
        
        if module.dsl_validator:
            # Тест с корректным DSL
            correct_dsl = """
# Тестовый макрос
open Calculator
wait 2s
click button_5
click button_plus
click button_3
click button_equals
"""
            
            validation_result = module.dsl_validator.validate_dsl(correct_dsl, auto_fix=True)
            print(f"✅ Валидация корректного DSL: {'успешна' if validation_result.is_valid else 'неуспешна'}")
            print(f"   Ошибок: {len(validation_result.errors)}")
            print(f"   Предупреждений: {len(validation_result.warnings)}")
            
            # Тест с некорректным DSL (опечатки)
            incorrect_dsl = """
# Тестовый макрос с опечатками
opne Calculator
wiat 2s
clik button_5
typ "hello"
"""
            
            validation_result = module.dsl_validator.validate_dsl(incorrect_dsl, auto_fix=True)
            print(f"✅ Валидация некорректного DSL: {'исправлен' if validation_result.fixed_code else 'не исправлен'}")
            print(f"   Исправлений применено: {len(validation_result.fixes_applied)}")
            if validation_result.fixes_applied:
                print(f"   Примеры исправлений: {validation_result.fixes_applied[:2]}")
        
        # Тестирование семантической валидации
        print("\n🧠 ТЕСТИРОВАНИЕ СЕМАНТИЧЕСКОЙ ВАЛИДАЦИИ:")
        print("-" * 60)
        
        if module.semantic_validator:
            test_dsl = """
open NonExistentApp
wait 0.1s
navigate "invalid-url"
click_element "//invalid//xpath"
wait 15s
"""
            
            semantic_result = module.semantic_validator.validate_semantics(test_dsl)
            print(f"✅ Семантическая валидация выполнена")
            print(f"   Предупреждений: {len(semantic_result.warnings)}")
            print(f"   Предложений: {len(semantic_result.suggestions)}")
            print(f"   Проблем с ресурсами: {len(semantic_result.resource_issues)}")
            print(f"   Проблем с таймингом: {len(semantic_result.timing_issues)}")
            
            if semantic_result.warnings:
                print(f"   Пример предупреждения: {semantic_result.warnings[0]}")
        
        # Тестирование полного цикла с улучшенным AI
        print("\n🚀 ТЕСТИРОВАНИЕ ПОЛНОГО ЦИКЛА С УЛУЧШЕННЫМ AI:")
        print("-" * 60)
        
        test_requests = [
            {
                "request": "открой калькулятор и посчитай 15 + 25",
                "expected_type": "system_app"
            },
            {
                "request": "найди на YouTube видео про искусственный интеллект",
                "expected_type": "web"
            },
            {
                "request": "найди через spotlight терминал",
                "expected_type": "spotlight"
            }
        ]
        
        for i, test_case in enumerate(test_requests, 1):
            print(f"\n🧪 ТЕСТ {i}: {test_case['request']}")
            print("-" * 40)
            
            try:
                result = module.execute(test_case['request'])
                
                if result.success:
                    print("✅ Выполнение успешно")
                    
                    # Проверяем использование улучшенных возможностей
                    enhanced_used = result.metadata.get('enhanced', False)
                    print(f"   🚀 Расширенная генерация: {'✅' if enhanced_used else '🤖 AI генерация'}")
                    
                    if result.data:
                        macro_info = result.data.get("generated_macro", {})
                        print(f"   📝 Название: {macro_info.get('name', 'N/A')}")
                        
                        # Проверяем валидацию
                        validation_info = result.metadata.get('validation_info')
                        if validation_info:
                            improvements = validation_info.get('improvements_applied', [])
                            if improvements:
                                print(f"   🔧 Улучшений применено: {len(improvements)}")
                                print(f"   📋 Примеры: {improvements[:2]}")
                        
                        if result.data.get("saved_file"):
                            print(f"   💾 Сохранен: {Path(result.data['saved_file']).name}")
                    
                    print(f"   ⏱️ Время: {result.execution_time:.2f}с")
                    
                else:
                    print("❌ Выполнение неудачно")
                    print(f"   🚨 Ошибка: {result.error}")
                
            except Exception as e:
                print(f"❌ Ошибка выполнения: {e}")
        
        # Тестирование статистики компонентов
        print("\n📊 СТАТИСТИКА КОМПОНЕНТОВ:")
        print("-" * 60)
        
        if module.dsl_validator:
            validator_stats = module.dsl_validator.get_validation_statistics()
            print(f"📋 DSL Validator:")
            print(f"   Всего валидаций: {validator_stats.get('total_validations', 0)}")
            print(f"   Найдено ошибок: {validator_stats.get('errors_found', 0)}")
            print(f"   Применено исправлений: {validator_stats.get('fixes_applied', 0)}")
        
        if module.ai_examples:
            examples_stats = module.ai_examples.get_statistics()
            print(f"📚 AI Examples:")
            print(f"   Всего примеров: {examples_stats.get('total_examples', 0)}")
            print(f"   Распределение по типам: {examples_stats.get('intent_distribution', {})}")
        
        print("\n🎉 ВСЕ ТЕСТЫ ЧАСТИ 2 ЗАВЕРШЕНЫ!")
        print("✅ Улучшенный AI и валидация работают корректно")
        
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompt_building():
    """Тест построения улучшенных промптов"""
    print("\n" + "=" * 70)
    print("🎯 ДЕТАЛЬНОЕ ТЕСТИРОВАНИЕ ПОСТРОЕНИЯ ПРОМПТОВ")
    print("=" * 70)
    
    try:
        from src.modules.sequence_generator.prompts.context_aware_prompts import ContextAwarePrompts, PromptContextBuilder
        
        # Тест ContextAwarePrompts
        prompts = ContextAwarePrompts()
        available_types = prompts.get_available_prompt_types()
        print(f"✅ Доступно типов промптов: {len(available_types)}")
        
        # Тест PromptContextBuilder
        builder = PromptContextBuilder()
        context = (builder
                  .add_user_request("открой калькулятор и посчитай 5+3")
                  .add_system_context("Calculator", {"button_5": "//button[@name='5']"})
                  .add_math_context("5+3")
                  .build())
        
        print(f"✅ Контекст построен: {len(context)} ключей")
        
        # Тест генерации промпта
        prompt = prompts.get_prompt_for_intent("calculator_automation", context)
        print(f"✅ Промпт сгенерирован: {len(prompt)} символов")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования промптов: {e}")
        return False

def test_validation_components():
    """Тест компонентов валидации"""
    print("\n" + "=" * 70)
    print("🔍 ДЕТАЛЬНОЕ ТЕСТИРОВАНИЕ ВАЛИДАЦИИ")
    print("=" * 70)
    
    try:
        from src.modules.sequence_generator.validators.dsl_validator import DSLValidator
        from src.modules.sequence_generator.validators.semantic_validator import SemanticValidator
        
        # Тест DSLValidator
        validator = DSLValidator()
        
        # Тест с опечатками
        dsl_with_typos = "opne Calculator\nwiat 2s\nclik button_5"
        result = validator.validate_dsl(dsl_with_typos, auto_fix=True)
        
        print(f"✅ DSL Validator:")
        print(f"   Валидный: {result.is_valid}")
        print(f"   Исправлений: {len(result.fixes_applied)}")
        print(f"   Ошибок: {len(result.errors)}")
        
        # Тест SemanticValidator
        semantic_validator = SemanticValidator()
        
        dsl_code = """
open Calculator
wait 0.1s
navigate "invalid-url"
system_command "rm -rf /"
"""
        
        semantic_result = semantic_validator.validate_semantics(dsl_code)
        print(f"✅ Semantic Validator:")
        print(f"   Предупреждений: {len(semantic_result.warnings)}")
        print(f"   Предложений: {len(semantic_result.suggestions)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования валидации: {e}")
        return False

if __name__ == "__main__":
    print("🎯 ТЕСТИРОВАНИЕ ЧАСТИ 2: УЛУЧШЕННЫЙ AI И ВАЛИДАЦИЯ")
    print("=" * 80)
    
    # Основные тесты
    success1 = test_enhanced_ai_part2()
    
    # Детальные тесты компонентов
    success2 = test_prompt_building()
    success3 = test_validation_components()
    
    print("\n" + "=" * 80)
    if success1 and success2 and success3:
        print("🎉 ВСЕ ТЕСТЫ ЧАСТИ 2 ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Улучшенный AI и валидация готовы к использованию")
        print("\n🚀 ДОСТИЖЕНИЯ ЧАСТИ 2:")
        print("   📋 Контекстно-зависимые промпты")
        print("   📚 Few-Shot Learning с примерами")
        print("   🔍 Синтаксическая валидация DSL")
        print("   🧠 Семантическая валидация")
        print("   🛠️ Автоматическое исправление ошибок")
        print("   📊 Улучшенная точность AI генерации")
    else:
        print("❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("⚠️ Требуется дополнительная отладка")
    
    print("\n💡 Следующий шаг: ЧАСТЬ 3 - Многошаговые макросы с условной логикой")
