#!/usr/bin/env python3
"""
Демо приложение для тестирования модуля sequence_generator
"""

import sys
import os
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Главная функция демо"""
    print("🚀 ДЕМО МОДУЛЯ SEQUENCE_GENERATOR")
    print("=" * 50)
    
    try:
        # Инициализируем модульную систему
        from src.modules.registry import initialize_modular_system
        
        print("🔧 Инициализация модульной системы...")
        coordinator = initialize_modular_system()
        
        print("\n📋 Доступные модули:")
        modules = coordinator.get_available_modules()
        for name, info in modules.items():
            status = "🟢" if info["enabled"] else "🔴"
            print(f"   {status} {name}: {info['description']}")
        
        print("\n" + "=" * 50)
        print("🎯 ТЕСТИРОВАНИЕ МОДУЛЯ SEQUENCE_GENERATOR")
        print("=" * 50)
        
        # Тестовые запросы
        test_requests = [
            "создай макрос для открытия YouTube в Chrome",
            "открой Chrome и зайди на TikTok",
            "автоматизируй открытие калькулятора",
            "сделай макрос для поиска в Google"
        ]
        
        for i, request in enumerate(test_requests, 1):
            print(f"\n🧪 ТЕСТ {i}: {request}")
            print("-" * 40)
            
            try:
                # Обрабатываем запрос через координатор
                result = coordinator.process_user_input(request, "text")
                
                if result.success:
                    print("✅ Запрос обработан успешно!")
                    
                    # Выводим информацию о результате
                    if result.data:
                        if isinstance(result.data, dict):
                            if "generated_macro" in result.data:
                                macro = result.data["generated_macro"]
                                print(f"   📝 Название: {macro.get('name', 'Неизвестно')}")
                                print(f"   📄 Описание: {macro.get('description', 'Нет описания')}")
                                
                                if "saved_file" in result.data:
                                    print(f"   💾 Сохранено: {Path(result.data['saved_file']).name}")
                            
                            elif "response" in result.data:
                                print(f"   💬 Ответ: {result.data['response'][:100]}...")
                        else:
                            print(f"   📊 Результат: {str(result.data)[:100]}...")
                    
                    # Выводим логи
                    if result.logs:
                        print("   📋 Логи:")
                        for log in result.logs[-3:]:  # Последние 3 лога
                            print(f"      {log}")
                    
                    print(f"   ⏱️ Время выполнения: {result.execution_time:.2f}с")
                    
                else:
                    print("❌ Ошибка обработки запроса")
                    if result.error:
                        print(f"   🚨 Ошибка: {result.error}")
                
            except Exception as e:
                print(f"❌ Критическая ошибка: {e}")
        
        # Статистика координатора
        print("\n" + "=" * 50)
        print("📊 СТАТИСТИКА КООРДИНАТОРА")
        print("=" * 50)
        
        stats = coordinator.get_statistics()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n🎉 Демо завершено!")
        print("💡 Проверьте папку macros/production/ для созданных макросов")
        
    except Exception as e:
        print(f"❌ Критическая ошибка демо: {e}")
        import traceback
        traceback.print_exc()

def interactive_mode():
    """Интерактивный режим"""
    print("🎮 ИНТЕРАКТИВНЫЙ РЕЖИМ")
    print("Введите 'exit' для выхода")
    print("=" * 50)
    
    try:
        from src.modules.registry import initialize_modular_system
        
        coordinator = initialize_modular_system()
        
        while True:
            try:
                user_input = input("\n💬 Ваш запрос: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'выход']:
                    print("👋 До свидания!")
                    break
                
                if not user_input:
                    continue
                
                print("🔄 Обработка...")
                result = coordinator.process_user_input(user_input, "text")
                
                if result.success:
                    print("✅ Готово!")
                    
                    if result.data and isinstance(result.data, dict):
                        if "generated_macro" in result.data:
                            macro = result.data["generated_macro"]
                            print(f"📝 Создан макрос: {macro.get('name', 'Неизвестно')}")
                            
                            if "saved_file" in result.data:
                                print(f"💾 Сохранен: {Path(result.data['saved_file']).name}")
                        
                        elif "response" in result.data:
                            print(f"💬 {result.data['response']}")
                else:
                    print(f"❌ Ошибка: {result.error}")
                
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
    
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()
