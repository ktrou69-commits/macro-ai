#!/usr/bin/env python3
"""
cnn_trainer.py
Обучение CNN моделей для повышения точности распознавания
"""

import sys
import os
from pathlib import Path
import numpy as np
import cv2
import argparse
from datetime import datetime

# Добавляем родительскую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("❌ TensorFlow не установлен. Установи: pip3 install tensorflow")
    sys.exit(1)

from learning import LearningSystem


class CNNTrainer:
    """Тренер CNN моделей для распознавания элементов"""
    
    def __init__(self, learning_system: LearningSystem = None):
        """
        Инициализация тренера
        
        Args:
            learning_system: Система обучения для получения данных
        """
        self.learning_system = learning_system or LearningSystem(db_path="learning/memory.db")
        self.models_dir = Path("learning/models/cnn")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Параметры модели
        self.img_size = (64, 64)  # Размер входного изображения
        self.batch_size = 32
        self.epochs = 50
    
    def create_cnn_model(self, input_shape=(64, 64, 1)) -> keras.Model:
        """
        Создает архитектуру CNN модели
        
        Args:
            input_shape: Размер входного изображения
            
        Returns:
            Скомпилированная модель
        """
        model = keras.Sequential([
            # Входной слой
            layers.Input(shape=input_shape),
            
            # Блок 1: Базовые признаки
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Блок 2: Средние признаки
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Блок 3: Высокоуровневые признаки
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Классификация
            layers.Flatten(),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(1, activation='sigmoid')  # Бинарная классификация
        ])
        
        # Компиляция
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        return model
    
    def prepare_training_data(self, template_id: str, min_examples: int = 50):
        """
        Подготавливает данные для обучения
        
        Args:
            template_id: ID шаблона
            min_examples: Минимальное количество примеров
            
        Returns:
            X_train, X_val, y_train, y_val или None если недостаточно данных
        """
        print(f"\n📊 Подготовка данных для {template_id}...")
        
        # Загружаем примеры
        examples = self.learning_system.db.get_examples(template_id)
        
        if len(examples) < min_examples:
            print(f"❌ Недостаточно примеров: {len(examples)} < {min_examples}")
            print(f"💡 Запусти макрос несколько раз для накопления данных")
            return None
        
        # Разделяем на положительные и отрицательные
        positives = [e for e in examples if e['success'] and e['screenshot'] is not None]
        negatives = [e for e in examples if not e['success'] and e['screenshot'] is not None]
        
        print(f"   ✅ Положительных примеров: {len(positives)}")
        print(f"   ❌ Отрицательных примеров: {len(negatives)}")
        
        if len(positives) < 10 or len(negatives) < 10:
            print(f"⚠️  Слишком мало примеров одного из классов")
            return None
        
        # Балансируем классы
        min_count = min(len(positives), len(negatives))
        positives = positives[:min_count]
        negatives = negatives[:min_count]
        
        print(f"   ⚖️  Сбалансировано: {min_count} примеров каждого класса")
        
        # Подготавливаем изображения
        X = []
        y = []
        
        for example in positives:
            img = self._preprocess_image(example['screenshot'])
            if img is not None:
                X.append(img)
                y.append(1)  # Положительный класс
        
        for example in negatives:
            img = self._preprocess_image(example['screenshot'])
            if img is not None:
                X.append(img)
                y.append(0)  # Отрицательный класс
        
        X = np.array(X)
        y = np.array(y)
        
        # Перемешиваем
        indices = np.random.permutation(len(X))
        X = X[indices]
        y = y[indices]
        
        # Разделяем на train/val (80/20)
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        print(f"   📦 Train: {len(X_train)} примеров")
        print(f"   📦 Val: {len(X_val)} примеров")
        
        return X_train, X_val, y_train, y_val
    
    def _preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """
        Предобработка изображения
        
        Args:
            img: Входное изображение
            
        Returns:
            Предобработанное изображение
        """
        try:
            # Конвертируем в grayscale если нужно
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Resize до нужного размера
            img = cv2.resize(img, self.img_size)
            
            # Нормализация [0, 1]
            img = img.astype(np.float32) / 255.0
            
            # Добавляем канал
            img = np.expand_dims(img, axis=-1)
            
            return img
        except Exception as e:
            print(f"⚠️  Ошибка предобработки: {e}")
            return None
    
    def train(self, template_id: str, epochs: int = None, batch_size: int = None):
        """
        Обучает CNN модель для шаблона
        
        Args:
            template_id: ID шаблона
            epochs: Количество эпох (по умолчанию self.epochs)
            batch_size: Размер батча (по умолчанию self.batch_size)
            
        Returns:
            Обученная модель или None
        """
        print(f"\n{'='*60}")
        print(f"🧠 ОБУЧЕНИЕ CNN: {template_id}")
        print(f"{'='*60}")
        
        epochs = epochs or self.epochs
        batch_size = batch_size or self.batch_size
        
        # Подготовка данных
        data = self.prepare_training_data(template_id)
        if data is None:
            return None
        
        X_train, X_val, y_train, y_val = data
        
        # Создание модели
        print(f"\n🏗️  Создание модели...")
        model = self.create_cnn_model(input_shape=(*self.img_size, 1))
        
        print(f"\n📊 Архитектура модели:")
        model.summary()
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7
            )
        ]
        
        # Обучение
        print(f"\n🚀 Начало обучения...")
        print(f"   Эпох: {epochs}")
        print(f"   Batch size: {batch_size}")
        
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Оценка
        print(f"\n📈 Оценка модели...")
        train_loss, train_acc, train_prec, train_rec = model.evaluate(X_train, y_train, verbose=0)
        val_loss, val_acc, val_prec, val_rec = model.evaluate(X_val, y_val, verbose=0)
        
        print(f"\n📊 Результаты:")
        print(f"   Train - Loss: {train_loss:.4f}, Acc: {train_acc*100:.2f}%, Prec: {train_prec*100:.2f}%, Rec: {train_rec*100:.2f}%")
        print(f"   Val   - Loss: {val_loss:.4f}, Acc: {val_acc*100:.2f}%, Prec: {val_prec*100:.2f}%, Rec: {val_rec*100:.2f}%")
        
        # Сохранение
        model_path = self.models_dir / f"{template_id.replace('/', '_')}_cnn.keras"
        model.save(model_path)
        print(f"\n✅ Модель сохранена: {model_path}")
        
        # Сохраняем метаданные
        metadata = {
            'template_id': template_id,
            'train_acc': float(train_acc),
            'val_acc': float(val_acc),
            'train_examples': len(X_train),
            'val_examples': len(X_val),
            'epochs': epochs,
            'timestamp': datetime.now().isoformat()
        }
        
        metadata_path = self.models_dir / f"{template_id.replace('/', '_')}_metadata.txt"
        with open(metadata_path, 'w') as f:
            for key, value in metadata.items():
                f.write(f"{key}: {value}\n")
        
        print(f"✅ Метаданные сохранены: {metadata_path}")
        
        print(f"\n{'='*60}\n")
        
        return model
    
    def train_all(self, min_accuracy: float = 0.7):
        """
        Обучает модели для всех шаблонов с достаточным количеством данных
        
        Args:
            min_accuracy: Минимальная точность для сохранения модели
        """
        print(f"\n{'='*60}")
        print(f"🚀 МАССОВОЕ ОБУЧЕНИЕ CNN")
        print(f"{'='*60}")
        
        # Получаем все шаблоны
        all_templates = self.learning_system.db.get_all_templates()
        
        print(f"\n📋 Найдено шаблонов: {len(all_templates)}")
        
        trained_count = 0
        skipped_count = 0
        
        for template_id in all_templates:
            stats = self.learning_system.db.get_statistics(template_id)
            
            print(f"\n{'='*60}")
            print(f"🎯 {template_id}")
            print(f"   Попыток: {stats['total_attempts']}")
            print(f"   Текущая точность: {stats['accuracy']*100:.1f}%")
            
            if stats['total_attempts'] < 50:
                print(f"   ⏭️  Пропущено (мало данных)")
                skipped_count += 1
                continue
            
            # Обучаем
            model = self.train(template_id)
            
            if model:
                trained_count += 1
            else:
                skipped_count += 1
        
        print(f"\n{'='*60}")
        print(f"📊 ИТОГИ:")
        print(f"   ✅ Обучено: {trained_count}")
        print(f"   ⏭️  Пропущено: {skipped_count}")
        print(f"{'='*60}\n")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description='Обучение CNN моделей')
    parser.add_argument('--template', type=str, help='ID шаблона для обучения')
    parser.add_argument('--all', action='store_true', help='Обучить все шаблоны')
    parser.add_argument('--epochs', type=int, default=50, help='Количество эпох')
    parser.add_argument('--batch-size', type=int, default=32, help='Размер батча')
    
    args = parser.parse_args()
    
    # Создаем тренер
    trainer = CNNTrainer()
    
    if args.all:
        # Обучаем все
        trainer.train_all()
    elif args.template:
        # Обучаем один
        trainer.train(args.template, epochs=args.epochs, batch_size=args.batch_size)
    else:
        # Интерактивный режим
        print("\n📋 Доступные шаблоны:")
        all_templates = trainer.learning_system.db.get_all_templates()
        
        for i, template_id in enumerate(all_templates, 1):
            stats = trainer.learning_system.db.get_statistics(template_id)
            print(f"  {i}. {template_id} ({stats['total_attempts']} попыток, {stats['accuracy']*100:.1f}% точность)")
        
        if not all_templates:
            print("❌ Нет доступных шаблонов")
            print("💡 Запусти несколько макросов для накопления данных")
            return
        
        try:
            choice = int(input("\nВыбери шаблон (номер): ").strip())
            if 1 <= choice <= len(all_templates):
                template_id = all_templates[choice - 1]
                trainer.train(template_id, epochs=args.epochs, batch_size=args.batch_size)
            else:
                print("❌ Неверный номер")
        except ValueError:
            print("❌ Введи число")


if __name__ == '__main__':
    main()
