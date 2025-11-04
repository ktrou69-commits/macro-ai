#!/usr/bin/env python3
"""
macro_ai.py
Макрос для macOS: делает скриншот, ищет кнопку, кликает.
Режимы:
 - Template matching (OpenCV)  — быстрый, для статичных кнопок.
 - YOLO (ultralytics)         — более устойчивый, требует веса модели.
 - Hybrid                      — сначала OpenCV, fallback на YOLO.
"""

import time
import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image
import pyautogui
import cv2

# Попытка импортировать ultralytics (YOLO)
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except Exception as e:
    YOLO_AVAILABLE = False
    print(f"⚠️  YOLO недоступен: {e}")

# ---------- Настройки (можно менять) ----------
TEMPLATE_PATH = "models/button.png"     # путь к шаблону
YOLO_WEIGHTS = "models/best_yolo.pt"    # если обученная модель есть
TEMPLATE_THRESHOLD = 0.86               # порог совпадения шаблона (0..1)
DETECT_CONF = 0.5                       # порог для YOLO (0..1)
SLEEP_BETWEEN_FRAMES = 0.03             # пауза цикла (сек). 0.03 ≈ 33 FPS theoretical
MAX_SCREEN_WIDTH = None                 # можно ограничить для ускорения (px)
USE_GRAYSCALE_TEMPLATE = True
WARMUP = True                           # прогреть модель при старте
CLICK_COOLDOWN = 0.5                    # минимальная пауза между кликами (сек)
# ------------------------------------------------

# Безопасность PyAutoGUI
pyautogui.FAILSAFE = True  # двигай мышь в угол экрана для экстренной остановки
pyautogui.PAUSE = 0.05     # небольшая пауза между действиями PyAutoGUI

class MacroAI:
    """Основной класс для детекции и автоматизации кликов"""
    
    def __init__(self, args):
        self.args = args
        self.template = None
        self.yolo_model = None
        self.last_click_time = 0
        self.click_count = 0
        self.frame_count = 0
        self.start_time = time.time()
        self.scale_factor = 1.0  # коэффициент масштабирования экрана
        self.display_scale = 1.0  # Retina display scale factor
        
        # Определяем Retina scale factor
        self._detect_display_scale()
        
        # Инициализация
        self._init_template()
        self._init_yolo()
        
    def _detect_display_scale(self):
        """Определение scale factor для Retina дисплеев"""
        try:
            # Получаем физическое разрешение через screenshot
            img = pyautogui.screenshot()
            physical_w, physical_h = img.size
            
            # Получаем логическое разрешение
            logical_w, logical_h = pyautogui.size()
            
            # Вычисляем scale factor
            self.display_scale = physical_w / logical_w
            
            print(f"🖥️  Display info:")
            print(f"   Physical: {physical_w}x{physical_h}")
            print(f"   Logical:  {logical_w}x{logical_h}")
            print(f"   Scale:    {self.display_scale}x")
            
        except Exception as e:
            print(f"⚠️  Не удалось определить display scale: {e}")
            self.display_scale = 1.0
    
    def _init_template(self):
        """Загрузка шаблона для OpenCV"""
        if not self.args.template:
            return
            
        if not os.path.exists(TEMPLATE_PATH):
            print(f"⚠️  Шаблон не найден: {TEMPLATE_PATH}")
            return
            
        self.template = cv2.imread(
            TEMPLATE_PATH, 
            cv2.IMREAD_GRAYSCALE if USE_GRAYSCALE_TEMPLATE else cv2.IMREAD_COLOR
        )
        
        if self.template is None:
            raise RuntimeError(f"❌ Не удалось загрузить шаблон {TEMPLATE_PATH}")
            
        print(f"✅ Шаблон загружен: {TEMPLATE_PATH} ({self.template.shape})")
        
    def _init_yolo(self):
        """Инициализация YOLO модели"""
        if not self.args.yolo:
            return
            
        if not YOLO_AVAILABLE:
            print("❌ ultralytics не установлена! Установите: pip install ultralytics")
            return
            
        print("🔄 Инициализация YOLO...")
        
        # Выбор весов
        if os.path.exists(YOLO_WEIGHTS):
            weights = YOLO_WEIGHTS
            print(f"   Используем кастомную модель: {YOLO_WEIGHTS}")
        else:
            weights = "yolov8n.pt"  # nano модель - самая быстрая
            print(f"   Используем базовую модель: {weights}")
            
        try:
            self.yolo_model = YOLO(weights)
            
            # Устройство
            device = self.args.device or 'mps' if self._is_apple_silicon() else 'cpu'
            self.yolo_model.to(device)
            print(f"   Устройство: {device}")
            
            # Warmup
            if WARMUP:
                print("   Прогрев модели...")
                dummy = np.zeros((640, 640, 3), dtype=np.uint8)
                self.yolo_model.predict(dummy, verbose=False)
                
            print("✅ YOLO готов")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации YOLO: {e}")
            self.yolo_model = None
            
    @staticmethod
    def _is_apple_silicon():
        """Проверка на Apple Silicon"""
        try:
            import platform
            return platform.processor() == 'arm'
        except:
            return False
            
    def screenshot_to_cv2(self) -> np.ndarray:
        """Захват экрана и конвертация в OpenCV формат"""
        img = pyautogui.screenshot()
        frame = np.array(img)  # RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Опциональный ресайз для ускорения
        if MAX_SCREEN_WIDTH:
            h, w = frame.shape[:2]
            if w > MAX_SCREEN_WIDTH:
                self.scale_factor = float(w) / MAX_SCREEN_WIDTH
                new_w = int(w / self.scale_factor)
                new_h = int(h / self.scale_factor)
                frame = cv2.resize(frame, (new_w, new_h))
            else:
                self.scale_factor = 1.0
        else:
            self.scale_factor = 1.0
                
        return frame
        
    def template_search(self, frame_bgr: np.ndarray) -> Tuple[Optional[Tuple[int, int]], float]:
        """Поиск кнопки по шаблону OpenCV"""
        if self.template is None:
            return None, 0.0
            
        # Конвертация в grayscale
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        
        # Template matching
        res = cv2.matchTemplate(gray, self.template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        # Проверка порога
        if max_val >= TEMPLATE_THRESHOLD:
            h, w = self.template.shape
            top_left = max_loc
            # Центр на физическом разрешении
            center_physical = (int(top_left[0] + w/2), int(top_left[1] + h/2))
            
            # Применяем scale_factor если был ресайз
            center_physical = (
                int(center_physical[0] * self.scale_factor),
                int(center_physical[1] * self.scale_factor)
            )
            
            # Конвертируем в логическое разрешение для pyautogui
            center_logical = (
                int(center_physical[0] / self.display_scale),
                int(center_physical[1] / self.display_scale)
            )
            
            return center_logical, max_val
            
        return None, max_val
        
    def yolo_detect(self, frame_bgr: np.ndarray) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """Детекция кнопки через YOLO"""
        if self.yolo_model is None:
            return False, None
            
        try:
            results = self.yolo_model.predict(frame_bgr, conf=DETECT_CONF, verbose=False)
            
            if len(results) == 0:
                return False, None
                
            boxes = getattr(results[0], "boxes", None)
            if boxes is None or len(boxes) == 0:
                return False, None
                
            # Берем первый бокс (или можно выбрать по наибольшему conf)
            box = boxes.xyxy[0].cpu().numpy()  # [x1,y1,x2,y2]
            x1, y1, x2, y2 = map(int, box)
            cx_physical = (x1 + x2) // 2
            cy_physical = (y1 + y2) // 2
            
            # Применяем scale_factor если был ресайз
            cx_physical = int(cx_physical * self.scale_factor)
            cy_physical = int(cy_physical * self.scale_factor)
            
            # Конвертируем в логическое разрешение для pyautogui
            cx_logical = int(cx_physical / self.display_scale)
            cy_logical = int(cy_physical / self.display_scale)
            
            return True, (cx_logical, cy_logical)
            
        except Exception as e:
            print(f"⚠️  Ошибка YOLO детекции: {e}")
            return False, None
            
    def can_click(self) -> bool:
        """Проверка cooldown между кликами"""
        return (time.time() - self.last_click_time) >= CLICK_COOLDOWN
        
    def perform_click(self, x: int, y: int, method: str):
        """Выполнение клика с логированием"""
        if not self.can_click():
            return
            
        try:
            # Получаем текущий размер экрана для проверки
            screen_w, screen_h = pyautogui.size()
            
            # Проверяем, что координаты в пределах экрана
            if x < 0 or x >= screen_w or y < 0 or y >= screen_h:
                print(f"⚠️  Координаты вне экрана: ({x}, {y}), экран: {screen_w}x{screen_h}")
                return
            
            pyautogui.click(x, y)
            self.last_click_time = time.time()
            self.click_count += 1
            
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            
            print(f"🎯 [{method}] Клик #{self.click_count} → ({x}, {y}) | Display: {self.display_scale:.1f}x | FPS: {fps:.1f}")
            
        except Exception as e:
            print(f"❌ Ошибка клика: {e}")
            
    def run(self):
        """Основной цикл работы макроса"""
        screen_w, screen_h = pyautogui.size()
        
        print("\n" + "="*60)
        print("🚀 Макрос запущен!")
        print("="*60)
        print(f"📋 Режимы:")
        print(f"   Template: {'✅' if self.template is not None else '❌'}")
        print(f"   YOLO:     {'✅' if self.yolo_model is not None else '❌'}")
        
        if self.template is not None:
            print(f"\n📐 Информация:")
            print(f"   Размер экрана: {screen_w}x{screen_h}")
            print(f"   Размер шаблона: {self.template.shape[1]}x{self.template.shape[0]}")
            print(f"   Порог совпадения: {TEMPLATE_THRESHOLD}")
        
        print(f"\n💡 Нажми Ctrl+C для остановки")
        print(f"💡 Двигай мышь в угол экрана для экстренной остановки (FAILSAFE)")
        print("="*60 + "\n")
        
        try:
            while True:
                loop_start = time.time()
                self.frame_count += 1
                
                # Захват экрана
                frame = self.screenshot_to_cv2()
                clicked = False
                
                # 1) Попытка Template Matching (быстрый метод)
                if self.template is not None and not clicked:
                    center, score = self.template_search(frame)
                    if center:
                        self.perform_click(center[0], center[1], f"TEMPLATE score={score:.3f}")
                        clicked = True
                        
                # 2) Fallback на YOLO (если template не сработал)
                if not clicked and self.yolo_model is not None:
                    ok, coord = self.yolo_detect(frame)
                    if ok and coord:
                        self.perform_click(coord[0], coord[1], "YOLO")
                        clicked = True
                        
                # Контроль частоты кадров
                elapsed = time.time() - loop_start
                to_sleep = max(0, SLEEP_BETWEEN_FRAMES - elapsed)
                time.sleep(to_sleep)
                
        except KeyboardInterrupt:
            self._print_stats()
            print("\n✋ Остановлено пользователем.")
            sys.exit(0)
        except pyautogui.FailSafeException:
            self._print_stats()
            print("\n🛑 FAILSAFE активирован! Мышь в углу экрана.")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
    def _print_stats(self):
        """Вывод статистики работы"""
        elapsed = time.time() - self.start_time
        avg_fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        print("\n" + "="*60)
        print("📊 Статистика:")
        print(f"   Время работы: {elapsed:.1f} сек")
        print(f"   Кадров обработано: {self.frame_count}")
        print(f"   Средний FPS: {avg_fps:.1f}")
        print(f"   Кликов выполнено: {self.click_count}")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="🤖 Macro AI: screenshot → detect → click",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python macro_ai.py --template                    # OpenCV template matching
  python macro_ai.py --yolo                        # YOLO детекция
  python macro_ai.py --template --yolo             # Гибридный режим
  python macro_ai.py --yolo --device mps           # YOLO на Apple Silicon
  python macro_ai.py --template --yolo --device cpu # Гибрид на CPU
        """
    )
    
    parser.add_argument(
        "--template", 
        action="store_true", 
        help="Использовать шаблон OpenCV (models/button.png)"
    )
    parser.add_argument(
        "--yolo", 
        action="store_true", 
        help="Использовать YOLO (ultralytics)"
    )
    parser.add_argument(
        "--device", 
        type=str, 
        default=None, 
        choices=['cpu', 'mps', 'cuda'],
        help="Устройство для YOLO (cpu/mps/cuda). Auto: mps на Apple Silicon, иначе cpu"
    )
    
    args = parser.parse_args()
    
    # Валидация
    if not args.template and not args.yolo:
        print("❌ Ошибка: укажи хотя бы один режим (--template или --yolo)")
        parser.print_help()
        sys.exit(1)
        
    # Запуск
    macro = MacroAI(args)
    macro.run()


if __name__ == "__main__":
    main()
