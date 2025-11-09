#!/usr/bin/env python3
"""
cnn_detector.py
Детектор элементов на основе CNN
"""

import sys
from pathlib import Path
import numpy as np
import cv2
from typing import Optional, Tuple, List

# Добавляем родительскую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import tensorflow as tf
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️  TensorFlow не установлен. CNN детектор недоступен.")


class CNNDetector:
    """Детектор элементов на основе CNN"""
    
    def __init__(self, models_dir: str = "learning/models/cnn"):
        """
        Инициализация детектора
        
        Args:
            models_dir: Директория с обученными моделями
        """
        self.models_dir = Path(models_dir)
        self.models_cache = {}  # Кэш загруженных моделей
        self.img_size = (64, 64)
        
        if not TF_AVAILABLE:
            raise ImportError("TensorFlow не установлен")
    
    def load_model(self, template_id: str) -> Optional[keras.Model]:
        """
        Загружает обученную модель
        
        Args:
            template_id: ID шаблона
            
        Returns:
            Модель или None если не найдена
        """
        # Проверяем кэш
        if template_id in self.models_cache:
            return self.models_cache[template_id]
        
        # Путь к модели
        model_path = self.models_dir / f"{template_id.replace('/', '_')}_cnn.keras"
        
        if not model_path.exists():
            return None
        
        try:
            # Загружаем модель
            model = keras.models.load_model(model_path)
            
            # Кэшируем
            self.models_cache[template_id] = model
            
            return model
        except Exception as e:
            print(f"⚠️  Ошибка загрузки модели {template_id}: {e}")
            return None
    
    def preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """
        Предобработка изображения
        
        Args:
            img: Входное изображение
            
        Returns:
            Предобработанное изображение
        """
        # Конвертируем в grayscale если нужно
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Resize до нужного размера
        img = cv2.resize(img, self.img_size)
        
        # Нормализация [0, 1]
        img = img.astype(np.float32) / 255.0
        
        # Добавляем канал и batch dimension
        img = np.expand_dims(img, axis=-1)
        img = np.expand_dims(img, axis=0)
        
        return img
    
    def detect(
        self, 
        screenshot: np.ndarray, 
        template_id: str,
        threshold: float = 0.8,
        stride: int = 16
    ) -> Tuple[bool, Optional[Tuple[int, int]], float]:
        """
        Детектирует элемент на скриншоте
        
        Args:
            screenshot: Скриншот экрана
            template_id: ID шаблона
            threshold: Порог уверенности (0-1)
            stride: Шаг скользящего окна
            
        Returns:
            (найдено, координаты, уверенность)
        """
        # Загружаем модель
        model = self.load_model(template_id)
        
        if model is None:
            return False, None, 0.0
        
        # Конвертируем в grayscale
        if len(screenshot.shape) == 3:
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        else:
            gray = screenshot
        
        h, w = gray.shape
        window_h, window_w = self.img_size
        
        best_score = 0.0
        best_location = None
        
        # Скользящее окно
        for y in range(0, h - window_h, stride):
            for x in range(0, w - window_w, stride):
                # Вырезаем окно
                window = gray[y:y+window_h, x:x+window_w]
                
                # Предобработка
                processed = self.preprocess_image(window)
                
                # Предсказание
                prediction = model.predict(processed, verbose=0)[0][0]
                
                # Обновляем лучший результат
                if prediction > best_score:
                    best_score = prediction
                    best_location = (x + window_w // 2, y + window_h // 2)
        
        # Проверяем порог
        if best_score >= threshold:
            return True, best_location, float(best_score)
        else:
            return False, None, float(best_score)
    
    def detect_multi_scale(
        self,
        screenshot: np.ndarray,
        template_id: str,
        threshold: float = 0.8,
        scales: List[float] = [0.5, 0.75, 1.0, 1.25, 1.5]
    ) -> Tuple[bool, Optional[Tuple[int, int]], float]:
        """
        Детектирует элемент на разных масштабах
        
        Args:
            screenshot: Скриншот экрана
            template_id: ID шаблона
            threshold: Порог уверенности
            scales: Масштабы для проверки
            
        Returns:
            (найдено, координаты, уверенность)
        """
        best_score = 0.0
        best_location = None
        best_scale = 1.0
        
        for scale in scales:
            # Масштабируем изображение
            scaled_h = int(screenshot.shape[0] * scale)
            scaled_w = int(screenshot.shape[1] * scale)
            scaled = cv2.resize(screenshot, (scaled_w, scaled_h))
            
            # Детектируем
            found, location, score = self.detect(scaled, template_id, threshold=threshold)
            
            if found and score > best_score:
                best_score = score
                # Пересчитываем координаты для оригинального размера
                best_location = (int(location[0] / scale), int(location[1] / scale))
                best_scale = scale
        
        if best_location:
            return True, best_location, float(best_score)
        else:
            return False, None, float(best_score)
    
    def detect_fast(
        self,
        screenshot: np.ndarray,
        template_id: str,
        threshold: float = 0.8,
        grid_size: int = 8
    ) -> Tuple[bool, Optional[Tuple[int, int]], float]:
        """
        Быстрая детекция с использованием грубой сетки
        
        Args:
            screenshot: Скриншот экрана
            template_id: ID шаблона
            threshold: Порог уверенности
            grid_size: Размер сетки для грубого поиска
            
        Returns:
            (найдено, координаты, уверенность)
        """
        # Загружаем модель
        model = self.load_model(template_id)
        
        if model is None:
            return False, None, 0.0
        
        # Конвертируем в grayscale
        if len(screenshot.shape) == 3:
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        else:
            gray = screenshot
        
        h, w = gray.shape
        window_h, window_w = self.img_size
        
        # Грубый поиск
        stride_coarse = max(window_w // 2, 32)
        best_score = 0.0
        best_location = None
        
        candidates = []
        
        for y in range(0, h - window_h, stride_coarse):
            for x in range(0, w - window_w, stride_coarse):
                window = gray[y:y+window_h, x:x+window_w]
                processed = self.preprocess_image(window)
                prediction = model.predict(processed, verbose=0)[0][0]
                
                if prediction > threshold * 0.7:  # Более низкий порог для кандидатов
                    candidates.append((x, y, prediction))
        
        if not candidates:
            return False, None, 0.0
        
        # Точный поиск вокруг кандидатов
        stride_fine = 8
        
        for cx, cy, _ in candidates:
            # Область вокруг кандидата
            x_start = max(0, cx - stride_coarse)
            x_end = min(w - window_w, cx + stride_coarse)
            y_start = max(0, cy - stride_coarse)
            y_end = min(h - window_h, cy + stride_coarse)
            
            for y in range(y_start, y_end, stride_fine):
                for x in range(x_start, x_end, stride_fine):
                    window = gray[y:y+window_h, x:x+window_w]
                    processed = self.preprocess_image(window)
                    prediction = model.predict(processed, verbose=0)[0][0]
                    
                    if prediction > best_score:
                        best_score = prediction
                        best_location = (x + window_w // 2, y + window_h // 2)
        
        if best_score >= threshold:
            return True, best_location, float(best_score)
        else:
            return False, None, float(best_score)
    
    def is_model_available(self, template_id: str) -> bool:
        """
        Проверяет доступность модели
        
        Args:
            template_id: ID шаблона
            
        Returns:
            True если модель доступна
        """
        model_path = self.models_dir / f"{template_id.replace('/', '_')}_cnn.keras"
        return model_path.exists()
    
    def get_available_models(self) -> List[str]:
        """
        Возвращает список доступных моделей
        
        Returns:
            Список ID шаблонов
        """
        models = []
        
        if not self.models_dir.exists():
            return models
        
        for model_file in self.models_dir.glob("*_cnn.keras"):
            # Извлекаем template_id из имени файла
            template_id = model_file.stem.replace('_cnn', '').replace('_', '/')
            models.append(template_id)
        
        return models
    
    def clear_cache(self):
        """Очищает кэш моделей"""
        self.models_cache.clear()


def main():
    """Тестирование детектора"""
    import pyautogui
    
    print("🔍 Тест CNN детектора")
    print("="*60)
    
    detector = CNNDetector()
    
    # Получаем доступные модели
    models = detector.get_available_models()
    
    if not models:
        print("❌ Нет обученных моделей")
        print("💡 Сначала обучи модель: python3 learning/cnn_trainer.py")
        return
    
    print(f"\n📋 Доступные модели: {len(models)}")
    for i, model_id in enumerate(models, 1):
        print(f"  {i}. {model_id}")
    
    # Выбираем модель
    try:
        choice = int(input("\nВыбери модель (номер): ").strip())
        if 1 <= choice <= len(models):
            template_id = models[choice - 1]
        else:
            print("❌ Неверный номер")
            return
    except ValueError:
        print("❌ Введи число")
        return
    
    print(f"\n🔍 Детектирование: {template_id}")
    print("📸 Делаем скриншот...")
    
    # Делаем скриншот
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    
    # Детектируем
    print("🧠 Запуск CNN детектора...")
    found, location, confidence = detector.detect_fast(screenshot, template_id)
    
    if found:
        print(f"\n✅ НАЙДЕНО!")
        print(f"   Координаты: {location}")
        print(f"   Уверенность: {confidence*100:.1f}%")
    else:
        print(f"\n❌ НЕ НАЙДЕНО")
        print(f"   Максимальная уверенность: {confidence*100:.1f}%")


if __name__ == '__main__':
    main()
