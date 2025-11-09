#!/usr/bin/env python3
"""
learning_stats.py
Утилита для просмотра статистики обучения
"""

import sys
from pathlib import Path

# Добавляем родительскую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from learning import LearningSystem


def main():
    """Главная функция"""
    print("="*60)
    print("📊 СТАТИСТИКА ОБУЧЕНИЯ")
    print("="*60)
    
    # Инициализация
    learning = LearningSystem(db_path="learning/memory.db")
    
    # Получаем все шаблоны
    all_templates = learning.db.get_all_templates()
    
    if not all_templates:
        print("\n❌ Нет данных для отображения")
        print("💡 Запусти несколько макросов чтобы накопить данные")
        return
    
    print(f"\n📋 Найдено шаблонов: {len(all_templates)}\n")
    
    # Выводим статистику по каждому
    for template_id in all_templates:
        stats = learning.db.get_statistics(template_id)
        
        print(f"🎯 {template_id}")
        print(f"   Всего попыток: {stats['total_attempts']}")
        print(f"   ✅ Успешных: {stats['successful_attempts']}")
        print(f"   ❌ Неудачных: {stats['failed_attempts']}")
        print(f"   📈 Точность: {stats['accuracy']*100:.1f}%")
        
        if stats['last_success']:
            print(f"   🕐 Последний успех: {stats['last_success']}")
        if stats['last_failure']:
            print(f"   🕐 Последняя неудача: {stats['last_failure']}")
        if stats['last_retrain']:
            print(f"   🔄 Последнее переобучение: {stats['last_retrain']}")
        
        print()
    
    print("="*60)
    
    # Интерактивное меню
    print("\n💡 Команды:")
    print("  1. Показать примеры для шаблона")
    print("  2. Переобучить шаблон вручную")
    print("  3. Выход")
    
    while True:
        choice = input("\nВыбери действие (1-3): ").strip()
        
        if choice == '1':
            show_examples(learning, all_templates)
        elif choice == '2':
            manual_retrain(learning, all_templates)
        elif choice == '3':
            print("\n👋 До свидания!")
            break
        else:
            print("⚠️  Неверный выбор")


def show_examples(learning: LearningSystem, all_templates: list):
    """Показать примеры для шаблона"""
    print("\n📋 Доступные шаблоны:")
    for i, template_id in enumerate(all_templates, 1):
        print(f"  {i}. {template_id}")
    
    try:
        choice = int(input("\nВыбери шаблон (номер): ").strip())
        if 1 <= choice <= len(all_templates):
            template_id = all_templates[choice - 1]
            
            examples = learning.db.get_examples(template_id, limit=10)
            
            print(f"\n📸 Последние 10 примеров для {template_id}:")
            for i, ex in enumerate(examples, 1):
                status = "✅" if ex['success'] else "❌"
                print(f"  {i}. {status} {ex['timestamp']} - {ex['method']}")
                if ex['context']:
                    print(f"     {ex['context']}")
        else:
            print("⚠️  Неверный номер")
    except ValueError:
        print("⚠️  Введи число")


def manual_retrain(learning: LearningSystem, all_templates: list):
    """Переобучить шаблон вручную"""
    print("\n📋 Доступные шаблоны:")
    for i, template_id in enumerate(all_templates, 1):
        stats = learning.db.get_statistics(template_id)
        print(f"  {i}. {template_id} (попыток: {stats['total_attempts']})")
    
    try:
        choice = int(input("\nВыбери шаблон для переобучения (номер): ").strip())
        if 1 <= choice <= len(all_templates):
            template_id = all_templates[choice - 1]
            
            confirm = input(f"\n⚠️  Переобучить {template_id}? (y/n): ").strip().lower()
            if confirm == 'y':
                print(f"\n🔄 Переобучение {template_id}...")
                learning.retrain(template_id)
                print("✅ Готово!")
        else:
            print("⚠️  Неверный номер")
    except ValueError:
        print("⚠️  Введи число")


if __name__ == '__main__':
    main()
