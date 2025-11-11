#!/usr/bin/env python3
"""
learning_system.py
Система обучения на успехах и неудачах
"""

import numpy as np
import cv2
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from datetime import datetime
import pickle

from learning.database import ExecutionDatabase


class LearningSystem:
    """Система обучения на основе результатов выполнения"""
    
    def __init__(self, db_path: str = "learning/memory.db", retrain_threshold: int = 100):
        """
        Инициализация системы обучения
        
        Args:
            db_path: Путь к базе данных
            retrain_threshold: Количество примеров для автоматического переобучения
        """
        self.db = ExecutionDatabase(db_path)
        self.retrain_threshold = retrain_threshold
        self.models_dir = Path("learning/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        print("🧠 Система обучения инициализирована")
        print(f"   📊 Порог переобучения: {retrain_threshold} примеров")
    
    def record_success(
        self,
        template_id: str,
        screenshot: np.ndarray,
        region: Tuple[int, int, int, int],
        method: str = "template_match"
    ) -> int:
        """
        Записывает успешное выполнение
        
        Args:
            template_id: ID шаблона
            screenshot: Скриншот найденной области
            region: Координаты (x, y, width, height)
            method: Метод поиска
            
        Returns:
            ID записи
        """
        execution_id = self.db.record_execution(
            template_id=template_id,
            success=True,
            screenshot=screenshot,
            region=region,
            method=method,
            context=f"Successfully found at {region}"
        )
        
        print(f"✅ Успех записан: {template_id} (ID: {execution_id})")
        
        # Проверяем нужно ли переобучение
        self._check_retrain(template_id)
        
        return execution_id
    
    def record_failure(
        self,
        template_id: str,
        screenshot: Optional[np.ndarray] = None,
        region: Optional[Tuple[int, int, int, int]] = None,
        method: str = "template_match",
        context: str = ""
    ) -> int:
        """
        Записывает неудачное выполнение
        
        Args:
            template_id: ID шаблона
            screenshot: Скриншот области где искали
            region: Координаты где искали
            method: Метод поиска
            context: Дополнительная информация
            
        Returns:
            ID записи
        """
        execution_id = self.db.record_execution(
            template_id=template_id,
            success=False,
            screenshot=screenshot,
            region=region,
            method=method,
            context=context or f"Failed to find with method: {method}"
        )
        
        print(f"❌ Неудача записана: {template_id} (ID: {execution_id})")
        
        # Проверяем нужно ли переобучение
        self._check_retrain(template_id)
        
        return execution_id
    
    def _check_retrain(self, template_id: str):
        """Проверяет нужно ли переобучение"""
        total_attempts = self.db.get_total_attempts(template_id)
        
        # Переобучаемся каждые N примеров
        if total_attempts > 0 and total_attempts % self.retrain_threshold == 0:
            print(f"\n⚡ ТРИГГЕР: Накоплено {total_attempts} примеров!")
            print(f"🔄 Запуск автоматического переобучения для {template_id}...")
            self.retrain(template_id)
    
    def retrain(self, template_id: str):
        """
        Переобучает модель на накопленных примерах
        
        Args:
            template_id: ID шаблона для переобучения
        """
        print(f"\n{'='*60}")
        print(f"🧠 ПЕРЕОБУЧЕНИЕ: {template_id}")
        print(f"{'='*60}")
        
        # 1. Загружаем примеры
        examples = self.db.get_examples(template_id, only_untrained=True)
        
        if not examples:
            print("⚠️  Нет новых примеров для обучения")
            return
        
        # 2. Разделяем на успешные и неудачные
        positives = [e for e in examples if e['success']]
        negatives = [e for e in examples if not e['success']]
        
        print(f"📊 Примеры:")
        print(f"   ✅ Успешных: {len(positives)}")
        print(f"   ❌ Неудачных: {len(negatives)}")
        
        if not positives and not negatives:
            print("⚠️  Недостаточно данных для обучения")
            return
        
        # 3. Анализируем неудачные примеры
        if negatives:
            print(f"\n🔍 Анализ неудачных примеров...")
            self._analyze_failures(template_id, negatives)
        
        # 4. Создаем/обновляем шаблон
        if positives:
            print(f"\n🎨 Создание улучшенного шаблона...")
            self._create_improved_template(template_id, positives, negatives)
        
        # 5. Помечаем примеры как использованные
        example_ids = [e['id'] for e in examples]
        self.db.mark_as_trained(example_ids)
        
        # 6. Обновляем timestamp переобучения
        self.db.update_retrain_timestamp(template_id)
        
        # 7. Статистика
        stats = self.db.get_statistics(template_id)
        print(f"\n📈 Статистика после переобучения:")
        print(f"   Всего попыток: {stats['total_attempts']}")
        print(f"   Точность: {stats['accuracy']*100:.1f}%")
        
        print(f"{'='*60}\n")
    
    def _analyze_failures(self, template_id: str, negatives: List[Dict]):
        """
        Анализирует неудачные примеры
        
        Ищет общие паттерны в неудачах:
        - Все в одной области? → Кнопка переместилась
        - Разные области? → Кнопка изменила внешний вид
        - Нет скриншотов? → Проблема с методом поиска
        """
        # Проверяем есть ли скриншоты
        with_screenshots = [n for n in negatives if n['screenshot'] is not None]
        
        if not with_screenshots:
            print("   ⚠️  Нет скриншотов для анализа")
            return
        
        # Анализируем регионы
        regions = [n['region'] for n in with_screenshots if n['region']]
        
        if regions:
            # Проверяем сконцентрированы ли неудачи в одной области
            x_coords = [r[0] for r in regions]
            y_coords = [r[1] for r in regions]
            
            x_std = np.std(x_coords) if len(x_coords) > 1 else 0
            y_std = np.std(y_coords) if len(y_coords) > 1 else 0
            
            if x_std < 50 and y_std < 50:
                print(f"   💡 Неудачи сконцентрированы в одной области")
                print(f"      Возможно, кнопка изменила внешний вид")
                avg_x = int(np.mean(x_coords))
                avg_y = int(np.mean(y_coords))
                print(f"      Центр: ({avg_x}, {avg_y})")
            else:
                print(f"   💡 Неудачи в разных областях")
                print(f"      Возможно, кнопка перемещается или метод поиска неточный")
        
        # Анализируем методы
        methods = [n['method'] for n in negatives]
        method_counts = {}
        for m in methods:
            method_counts[m] = method_counts.get(m, 0) + 1
        
        print(f"   📊 Методы поиска:")
        for method, count in method_counts.items():
            print(f"      {method}: {count} неудач")
    
    def _create_improved_template(
        self, 
        template_id: str, 
        positives: List[Dict],
        negatives: List[Dict]
    ):
        """
        Создает улучшенный шаблон на основе примеров
        
        Стратегия:
        1. Если есть свежие успешные примеры → используем их как новый шаблон
        2. Если есть только старые успехи + новые неудачи → 
           пытаемся найти общие черты в неудачах (это может быть новый дизайн)
        """
        # Берем последние успешные примеры
        recent_positives = sorted(positives, key=lambda x: x['timestamp'], reverse=True)[:10]
        
        # Извлекаем скриншоты
        positive_screenshots = [p['screenshot'] for p in recent_positives if p['screenshot'] is not None]
        
        if not positive_screenshots:
            print("   ⚠️  Нет скриншотов для создания шаблона")
            return
        
        # Создаем усредненный шаблон
        print(f"   📸 Создание шаблона из {len(positive_screenshots)} примеров...")
        
        # Приводим все к одному размеру
        target_size = (100, 100)  # Стандартный размер шаблона
        resized = []
        for img in positive_screenshots:
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_resized = cv2.resize(img, target_size)
            resized.append(img_resized)
        
        # Усредняем
        template = np.mean(resized, axis=0).astype(np.uint8)
        
        # Сохраняем
        template_path = self.models_dir / f"{template_id}_template.pkl"
        with open(template_path, 'wb') as f:
            pickle.dump(template, f)
        
        print(f"   ✅ Шаблон сохранен: {template_path}")
        
        # Также сохраняем как изображение для визуализации
        img_path = self.models_dir / f"{template_id}_template.png"
        cv2.imwrite(str(img_path), template)
        print(f"   🖼️  Визуализация: {img_path}")
    
    def get_template(self, template_id: str) -> Optional[np.ndarray]:
        """
        Загружает обученный шаблон
        
        Args:
            template_id: ID шаблона
            
        Returns:
            Шаблон или None если не найден
        """
        template_path = self.models_dir / f"{template_id}_template.pkl"
        
        if not template_path.exists():
            return None
        
        with open(template_path, 'rb') as f:
            return pickle.load(f)
    
    def get_statistics(self, template_id: Optional[str] = None) -> Dict:
        """
        Возвращает статистику
        
        Args:
            template_id: ID шаблона (None для всех)
            
        Returns:
            Статистика
        """
        if template_id:
            return self.db.get_statistics(template_id)
        else:
            # Статистика по всем шаблонам
            all_templates = self.db.get_all_templates()
            stats = {}
            for tid in all_templates:
                stats[tid] = self.db.get_statistics(tid)
            return stats
    
    def print_statistics(self, template_id: Optional[str] = None):
        """Выводит статистику в консоль"""
        print(f"\n{'='*60}")
        print("📊 СТАТИСТИКА ОБУЧЕНИЯ")
        print(f"{'='*60}")
        
        stats = self.get_statistics(template_id)
        
        if template_id:
            # Статистика одного шаблона
            self._print_template_stats(template_id, stats)
        else:
            # Статистика всех шаблонов
            for tid, st in stats.items():
                self._print_template_stats(tid, st)
                print("-" * 60)
        
        print(f"{'='*60}\n")
    
    def _print_template_stats(self, template_id: str, stats: Dict):
        """Выводит статистику одного шаблона"""
        print(f"\n🎯 {template_id}")
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
