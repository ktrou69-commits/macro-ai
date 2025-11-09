#!/usr/bin/env python3
"""
visualize_learning.py
Визуализация прогресса обучения
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Добавляем родительскую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from learning import LearningSystem


def plot_accuracy_over_time(learning: LearningSystem, template_id: str):
    """График точности во времени"""
    examples = learning.db.get_examples(template_id)
    
    if not examples:
        print(f"❌ Нет данных для {template_id}")
        return
    
    # Сортируем по времени
    examples = sorted(examples, key=lambda x: x['timestamp'])
    
    # Вычисляем скользящую точность (окно 20 примеров)
    window_size = 20
    timestamps = []
    accuracies = []
    
    for i in range(len(examples)):
        if i < window_size:
            continue
        
        window = examples[i-window_size:i]
        successes = sum(1 for e in window if e['success'])
        accuracy = successes / window_size
        
        timestamps.append(datetime.fromisoformat(examples[i]['timestamp']))
        accuracies.append(accuracy * 100)
    
    # Строим график
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, accuracies, linewidth=2, color='#2196F3')
    plt.fill_between(timestamps, accuracies, alpha=0.3, color='#2196F3')
    
    plt.title(f'Точность поиска: {template_id}', fontsize=14, fontweight='bold')
    plt.xlabel('Время', fontsize=12)
    plt.ylabel('Точность (%)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 105)
    
    # Форматирование дат
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gcf().autofmt_xdate()
    
    # Добавляем статистику
    stats = learning.db.get_statistics(template_id)
    stats_text = f"Всего: {stats['total_attempts']} | Точность: {stats['accuracy']*100:.1f}%"
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(f'learning/plots/{template_id}_accuracy.png', dpi=150)
    print(f"✅ График сохранен: learning/plots/{template_id}_accuracy.png")
    plt.show()


def plot_success_failure_distribution(learning: LearningSystem):
    """График распределения успехов/неудач по всем шаблонам"""
    all_templates = learning.db.get_all_templates()
    
    if not all_templates:
        print("❌ Нет данных")
        return
    
    # Собираем данные
    template_names = []
    successes = []
    failures = []
    
    for template_id in all_templates:
        stats = learning.db.get_statistics(template_id)
        template_names.append(template_id.split('/')[-1][:20])  # Короткое имя
        successes.append(stats['successful_attempts'])
        failures.append(stats['failed_attempts'])
    
    # Строим график
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = range(len(template_names))
    width = 0.35
    
    ax.bar([i - width/2 for i in x], successes, width, label='Успехи', color='#4CAF50')
    ax.bar([i + width/2 for i in x], failures, width, label='Неудачи', color='#F44336')
    
    ax.set_xlabel('Шаблоны', fontsize=12)
    ax.set_ylabel('Количество', fontsize=12)
    ax.set_title('Распределение успехов и неудач', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(template_names, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('learning/plots/success_failure_distribution.png', dpi=150)
    print("✅ График сохранен: learning/plots/success_failure_distribution.png")
    plt.show()


def main():
    """Главная функция"""
    # Создаем директорию для графиков
    Path('learning/plots').mkdir(parents=True, exist_ok=True)
    
    print("📊 Визуализация обучения")
    print("="*60)
    
    learning = LearningSystem(db_path="learning/memory.db")
    all_templates = learning.db.get_all_templates()
    
    if not all_templates:
        print("❌ Нет данных для визуализации")
        return
    
    print("\n💡 Доступные графики:")
    print("  1. Точность во времени (для конкретного шаблона)")
    print("  2. Распределение успехов/неудач (все шаблоны)")
    print("  3. Оба графика")
    
    choice = input("\nВыбери (1-3): ").strip()
    
    if choice == '1':
        print("\n📋 Доступные шаблоны:")
        for i, template_id in enumerate(all_templates, 1):
            print(f"  {i}. {template_id}")
        
        try:
            template_choice = int(input("\nВыбери шаблон (номер): ").strip())
            if 1 <= template_choice <= len(all_templates):
                template_id = all_templates[template_choice - 1]
                plot_accuracy_over_time(learning, template_id)
            else:
                print("⚠️  Неверный номер")
        except ValueError:
            print("⚠️  Введи число")
    
    elif choice == '2':
        plot_success_failure_distribution(learning)
    
    elif choice == '3':
        plot_success_failure_distribution(learning)
        
        print("\n📋 Выбери шаблон для графика точности:")
        for i, template_id in enumerate(all_templates, 1):
            print(f"  {i}. {template_id}")
        
        try:
            template_choice = int(input("\nВыбери шаблон (номер): ").strip())
            if 1 <= template_choice <= len(all_templates):
                template_id = all_templates[template_choice - 1]
                plot_accuracy_over_time(learning, template_id)
            else:
                print("⚠️  Неверный номер")
        except ValueError:
            print("⚠️  Введи число")
    
    else:
        print("⚠️  Неверный выбор")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 До свидания!")
