#!/usr/bin/env python3
"""
monitor_learning.py
Мониторинг сбора данных в реальном времени
"""

import sys
from pathlib import Path
import time
from datetime import datetime

# Добавляем родительскую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from learning import LearningSystem


def monitor():
    """Мониторинг в реальном времени"""
    print("="*60)
    print("📡 МОНИТОРИНГ LEARNING SYSTEM")
    print("="*60)
    print("\n💡 Этот скрипт показывает данные в реальном времени")
    print("   Запусти макросы в другом терминале и наблюдай!")
    print("\n⏹️  Ctrl+C для остановки\n")
    
    learning = LearningSystem(db_path="learning/memory.db")
    
    # Получаем начальное состояние
    prev_stats = {}
    all_templates = learning.db.get_all_templates()
    
    for template_id in all_templates:
        prev_stats[template_id] = learning.db.get_statistics(template_id)
    
    print(f"🔍 Отслеживается шаблонов: {len(all_templates)}")
    print("-"*60)
    
    try:
        while True:
            time.sleep(2)  # Проверка каждые 2 секунды
            
            # Получаем текущее состояние
            all_templates = learning.db.get_all_templates()
            
            for template_id in all_templates:
                current_stats = learning.db.get_statistics(template_id)
                
                # Проверяем изменения
                if template_id not in prev_stats:
                    # Новый шаблон!
                    print(f"\n🆕 НОВЫЙ ШАБЛОН: {template_id}")
                    print(f"   Попыток: {current_stats['total_attempts']}")
                    prev_stats[template_id] = current_stats
                    continue
                
                prev = prev_stats[template_id]
                
                # Проверяем новые попытки
                if current_stats['total_attempts'] > prev['total_attempts']:
                    new_attempts = current_stats['total_attempts'] - prev['total_attempts']
                    new_successes = current_stats['successful_attempts'] - prev['successful_attempts']
                    new_failures = current_stats['failed_attempts'] - prev['failed_attempts']
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    print(f"\n[{timestamp}] 📊 {template_id}")
                    
                    if new_successes > 0:
                        print(f"   ✅ +{new_successes} успех(ов)")
                    if new_failures > 0:
                        print(f"   ❌ +{new_failures} неудач(и)")
                    
                    print(f"   📈 Всего: {current_stats['total_attempts']} | Точность: {current_stats['accuracy']*100:.1f}%")
                    
                    # Проверяем переобучение
                    if current_stats['last_retrain'] != prev['last_retrain']:
                        print(f"   🔄 ПЕРЕОБУЧЕНИЕ ВЫПОЛНЕНО!")
                    
                    prev_stats[template_id] = current_stats
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Мониторинг остановлен")
        print("\n📊 Финальная статистика:")
        learning.print_statistics()


if __name__ == '__main__':
    monitor()
