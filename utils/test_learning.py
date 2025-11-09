#!/usr/bin/env python3
"""
test_learning.py
Тестирование Learning System
"""

import sys
from pathlib import Path
import numpy as np
import cv2

# Добавляем родительскую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from learning import LearningSystem


def create_fake_screenshot(color='red'):
    """Создает фейковый скриншот кнопки"""
    img = np.zeros((100, 100), dtype=np.uint8)
    
    if color == 'red':
        # Красная кнопка (в grayscale - светлая)
        cv2.circle(img, (50, 50), 30, 200, -1)
    elif color == 'blue':
        # Синяя кнопка (в grayscale - темная)
        cv2.circle(img, (50, 50), 30, 100, -1)
    
    return img


def test_basic_recording():
    """Тест 1: Базовая запись"""
    print("="*60)
    print("🧪 ТЕСТ 1: Базовая запись")
    print("="*60)
    
    learning = LearningSystem(db_path="learning/memory.db", retrain_threshold=10)
    
    # Записываем 5 успехов
    print("\n📝 Записываем 5 успехов...")
    for i in range(5):
        screenshot = create_fake_screenshot('red')
        learning.record_success(
            template_id="test-button",
            screenshot=screenshot,
            region=(100, 200, 100, 100),
            method="test"
        )
    
    # Записываем 3 неудачи
    print("\n📝 Записываем 3 неудачи...")
    for i in range(3):
        screenshot = create_fake_screenshot('blue')
        learning.record_failure(
            template_id="test-button",
            screenshot=screenshot,
            region=(100, 200, 100, 100),
            method="test",
            context="Test failure"
        )
    
    # Проверяем статистику
    print("\n📊 Проверка статистики...")
    stats = learning.db.get_statistics("test-button")
    
    print(f"\n✅ Результаты:")
    print(f"   Всего попыток: {stats['total_attempts']}")
    print(f"   Успешных: {stats['successful_attempts']}")
    print(f"   Неудачных: {stats['failed_attempts']}")
    print(f"   Точность: {stats['accuracy']*100:.1f}%")
    
    assert stats['total_attempts'] == 8, "Должно быть 8 попыток"
    assert stats['successful_attempts'] == 5, "Должно быть 5 успехов"
    assert stats['failed_attempts'] == 3, "Должно быть 3 неудачи"
    
    print("\n✅ ТЕСТ 1 ПРОЙДЕН!")


def test_auto_retrain():
    """Тест 2: Автоматическое переобучение"""
    print("\n" + "="*60)
    print("🧪 ТЕСТ 2: Автоматическое переобучение")
    print("="*60)
    
    learning = LearningSystem(db_path="learning/memory.db", retrain_threshold=10)
    
    # Записываем 7 успехов (красная кнопка)
    print("\n📝 Записываем 7 успехов (красная кнопка)...")
    for i in range(7):
        screenshot = create_fake_screenshot('red')
        learning.record_success(
            template_id="test-retrain",
            screenshot=screenshot,
            region=(100, 200, 100, 100)
        )
    
    # Записываем 3 неудачи (синяя кнопка - новый дизайн)
    print("\n📝 Записываем 3 неудачи (синяя кнопка)...")
    for i in range(3):
        screenshot = create_fake_screenshot('blue')
        learning.record_failure(
            template_id="test-retrain",
            screenshot=screenshot,
            region=(100, 200, 100, 100),
            context="Design changed"
        )
    
    print("\n⚡ Должно произойти автоматическое переобучение!")
    print("   (порог = 10 примеров)")
    
    # Проверяем что переобучение произошло
    stats = learning.db.get_statistics("test-retrain")
    
    print(f"\n📊 Статистика:")
    print(f"   Всего попыток: {stats['total_attempts']}")
    print(f"   Последнее переобучение: {stats['last_retrain']}")
    
    assert stats['total_attempts'] == 10, "Должно быть 10 попыток"
    assert stats['last_retrain'] is not None, "Должно быть переобучение"
    
    print("\n✅ ТЕСТ 2 ПРОЙДЕН!")


def test_last_success_retrieval():
    """Тест 3: Получение последнего успеха"""
    print("\n" + "="*60)
    print("🧪 ТЕСТ 3: Получение последнего успеха")
    print("="*60)
    
    learning = LearningSystem(db_path="learning/memory.db")
    
    # Записываем успех
    print("\n📝 Записываем успех...")
    screenshot = create_fake_screenshot('red')
    learning.record_success(
        template_id="test-last-success",
        screenshot=screenshot,
        region=(150, 250, 100, 100)
    )
    
    # Получаем последний успех
    print("\n🔍 Получаем последний успех...")
    last_success = learning.db.get_last_success("test-last-success")
    
    assert last_success is not None, "Должен быть последний успех"
    assert last_success['region'] == (150, 250, 100, 100), "Регион должен совпадать"
    assert last_success['screenshot'] is not None, "Должен быть скриншот"
    
    print(f"\n✅ Результаты:")
    print(f"   Регион: {last_success['region']}")
    print(f"   Timestamp: {last_success['timestamp']}")
    print(f"   Скриншот: {last_success['screenshot'].shape}")
    
    print("\n✅ ТЕСТ 3 ПРОЙДЕН!")


def test_continuous_recording():
    """Тест 4: Непрерывная запись (имитация реального использования)"""
    print("\n" + "="*60)
    print("🧪 ТЕСТ 4: Непрерывная запись")
    print("="*60)
    
    learning = LearningSystem(db_path="learning/memory.db", retrain_threshold=20)
    
    print("\n📝 Имитация 50 попыток поиска кнопки...")
    print("   (80% успехов, 20% неудач)")
    
    success_count = 0
    failure_count = 0
    
    for i in range(50):
        # 80% успехов
        if i % 5 != 0:
            screenshot = create_fake_screenshot('red')
            learning.record_success(
                template_id="test-continuous",
                screenshot=screenshot,
                region=(100 + i, 200, 100, 100)
            )
            success_count += 1
        else:
            screenshot = create_fake_screenshot('blue')
            learning.record_failure(
                template_id="test-continuous",
                screenshot=screenshot,
                region=(100 + i, 200, 100, 100)
            )
            failure_count += 1
        
        # Прогресс
        if (i + 1) % 10 == 0:
            print(f"   Прогресс: {i + 1}/50")
    
    # Проверяем статистику
    stats = learning.db.get_statistics("test-continuous")
    
    print(f"\n📊 Итоговая статистика:")
    print(f"   Всего попыток: {stats['total_attempts']}")
    print(f"   Успешных: {stats['successful_attempts']}")
    print(f"   Неудачных: {stats['failed_attempts']}")
    print(f"   Точность: {stats['accuracy']*100:.1f}%")
    print(f"   Переобучений: {'Да' if stats['last_retrain'] else 'Нет'}")
    
    assert stats['total_attempts'] == 50, "Должно быть 50 попыток"
    assert stats['successful_attempts'] == success_count
    assert stats['failed_attempts'] == failure_count
    
    print("\n✅ ТЕСТ 4 ПРОЙДЕН!")


def test_data_persistence():
    """Тест 5: Сохранение данных между сессиями"""
    print("\n" + "="*60)
    print("🧪 ТЕСТ 5: Сохранение данных")
    print("="*60)
    
    # Создаем первую сессию
    print("\n📝 Сессия 1: Записываем данные...")
    learning1 = LearningSystem(db_path="learning/memory.db")
    
    screenshot = create_fake_screenshot('red')
    learning1.record_success(
        template_id="test-persistence",
        screenshot=screenshot,
        region=(100, 200, 100, 100)
    )
    
    stats1 = learning1.db.get_statistics("test-persistence")
    print(f"   Попыток в сессии 1: {stats1['total_attempts']}")
    
    # Создаем вторую сессию (новый объект)
    print("\n📝 Сессия 2: Проверяем сохранение...")
    learning2 = LearningSystem(db_path="learning/memory.db")
    
    stats2 = learning2.db.get_statistics("test-persistence")
    print(f"   Попыток в сессии 2: {stats2['total_attempts']}")
    
    assert stats2['total_attempts'] >= stats1['total_attempts'], "Данные должны сохраниться"
    
    print("\n✅ ТЕСТ 5 ПРОЙДЕН!")


def main():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("🧪 ТЕСТИРОВАНИЕ LEARNING SYSTEM")
    print("="*60)
    
    try:
        test_basic_recording()
        test_auto_retrain()
        test_last_success_retrieval()
        test_continuous_recording()
        test_data_persistence()
        
        print("\n" + "="*60)
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("="*60)
        
        # Показываем общую статистику
        print("\n📊 ОБЩАЯ СТАТИСТИКА:")
        learning = LearningSystem(db_path="learning/memory.db")
        learning.print_statistics()
        
    except AssertionError as e:
        print(f"\n❌ ТЕСТ ПРОВАЛЕН: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
