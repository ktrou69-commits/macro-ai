#!/usr/bin/env python3
"""
template_capture.py (ранее smart_capture.py)
Умный захват шаблонов с поддержкой:
- Задержки перед захватом (для переключения рабочих столов)
- Выбора конкретного экрана
- Сохранения под своим именем
- Превью перед сохранением

Новая архитектура v2.0 - сохранение в templates/
"""

import cv2
import numpy as np
import pyautogui
import time
import os
import sys
from pathlib import Path

# Автономный скрипт - работает без зависимостей

class SmartCapture:
    def __init__(self):
        self.screenshot = None
        self.selected_region = None
        self.window_name = "Smart Capture - Выдели область"
        
    def countdown(self, seconds: int):
        """Обратный отсчет с визуализацией"""
        print(f"\n{'='*60}")
        print(f"⏰ Обратный отсчет: {seconds} секунд")
        print(f"{'='*60}")
        print("💡 Используй это время чтобы:")
        print("   • Переключиться на нужный рабочий стол")
        print("   • Открыть нужное приложение")
        print("   • Подготовить элемент для захвата")
        print(f"{'='*60}\n")
        
        for i in range(seconds, 0, -1):
            print(f"⏳ {i}...", end='\r', flush=True)
            time.sleep(1)
        
        print("📸 Захват экрана!     ")
        time.sleep(0.2)  # Небольшая пауза для стабильности
    
    def capture_screen(self):
        """Захват экрана"""
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        self.screenshot = frame
        return frame
    
    def mouse_callback(self, event, x, y, flags, param):
        """Обработка событий мыши для выделения области"""
        if event == cv2.EVENT_LBUTTONDOWN:
            param['drawing'] = True
            param['start_point'] = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if param['drawing']:
                param['current_point'] = (x, y)
                
        elif event == cv2.EVENT_LBUTTONUP:
            param['drawing'] = False
            param['end_point'] = (x, y)
    
    def interactive_select(self, frame):
        """Интерактивное выделение области"""
        display_frame = frame.copy()
        
        # Уменьшаем для отображения если экран большой
        screen_h, screen_w = frame.shape[:2]
        max_display_w = 1920
        max_display_h = 1080
        
        scale = 1.0
        if screen_w > max_display_w or screen_h > max_display_h:
            scale = min(max_display_w / screen_w, max_display_h / screen_h)
            new_w = int(screen_w * scale)
            new_h = int(screen_h * scale)
            display_frame = cv2.resize(display_frame, (new_w, new_h))
        
        # Параметры для отслеживания выделения
        params = {
            'drawing': False,
            'start_point': None,
            'current_point': None,
            'end_point': None
        }
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback, params)
        
        print("\n" + "="*60)
        print("🖱️  Выдели область мышью:")
        print("   • Нажми и тяни левую кнопку мыши")
        print("   • Enter - сохранить")
        print("   • Esc - отмена")
        print("   • R - пересделать выделение")
        print("="*60 + "\n")
        
        while True:
            temp_frame = display_frame.copy()
            
            # Рисуем прямоугольник выделения
            if params['start_point'] and params['current_point']:
                cv2.rectangle(
                    temp_frame,
                    params['start_point'],
                    params['current_point'],
                    (0, 255, 0),
                    2
                )
                
                # Показываем размеры
                if params['current_point']:
                    x1, y1 = params['start_point']
                    x2, y2 = params['current_point']
                    w = abs(x2 - x1)
                    h = abs(y2 - y1)
                    
                    # Масштабируем обратно к реальному размеру
                    real_w = int(w / scale)
                    real_h = int(h / scale)
                    
                    text = f"{real_w}x{real_h}"
                    cv2.putText(
                        temp_frame,
                        text,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )
            
            cv2.imshow(self.window_name, temp_frame)
            key = cv2.waitKey(1) & 0xFF
            
            # Enter - сохранить
            if key == 13 and params['start_point'] and params['current_point']:
                x1, y1 = params['start_point']
                x2, y2 = params['current_point']
                
                # Масштабируем обратно к оригинальному разрешению
                x1 = int(x1 / scale)
                y1 = int(y1 / scale)
                x2 = int(x2 / scale)
                y2 = int(y2 / scale)
                
                # Нормализуем координаты
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)
                
                self.selected_region = (x1, y1, x2, y2)
                cv2.destroyAllWindows()
                return True
            
            # Esc - отмена
            elif key == 27:
                cv2.destroyAllWindows()
                return False
            
            # R - пересделать
            elif key == ord('r') or key == ord('R'):
                params['start_point'] = None
                params['current_point'] = None
                params['end_point'] = None
        
        cv2.destroyAllWindows()
        return False
    
    def save_template(self, output_path: str):
        """Сохранение выделенной области"""
        if self.selected_region is None or self.screenshot is None:
            print("❌ Нет выделенной области")
            return False
        
        x1, y1, x2, y2 = self.selected_region
        template = self.screenshot[y1:y2, x1:x2]
        
        # Создаем директорию если нужно
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Сохраняем
        cv2.imwrite(output_path, template)
        
        h, w = template.shape[:2]
        print(f"\n✅ Шаблон сохранен:")
        print(f"   Путь: {output_path}")
        print(f"   Размер: {w}x{h}")
        
        return True
    
    def show_preview(self):
        """Показать превью выделенной области"""
        if self.selected_region is None or self.screenshot is None:
            return
        
        x1, y1, x2, y2 = self.selected_region
        template = self.screenshot[y1:y2, x1:x2]
        
        # Увеличиваем для лучшей видимости
        scale = 3
        h, w = template.shape[:2]
        preview = cv2.resize(template, (w * scale, h * scale), interpolation=cv2.INTER_NEAREST)
        
        cv2.imshow("Preview - Нажми любую клавишу", preview)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def main():
    print("\n" + "="*60)
    print("🎯 Smart Capture - Умный захват шаблонов")
    print("="*60)
    
    capture = SmartCapture()
    
    # Шаг 1: Задержка
    print("\n1️⃣  Задержка перед захватом")
    print("-" * 60)
    
    while True:
        delay_input = input("⏰ Задержка в секундах (0-30, Enter=5): ").strip()
        
        if delay_input == "":
            delay = 5
            break
        
        try:
            delay = int(delay_input)
            if 0 <= delay <= 30:
                break
            else:
                print("⚠️  Введи число от 0 до 30")
        except ValueError:
            print("⚠️  Введи число")
    
    # Обратный отсчет
    if delay > 0:
        capture.countdown(delay)
    
    # Шаг 2: Захват экрана
    print("\n2️⃣  Захват экрана...")
    frame = capture.capture_screen()
    print(f"✅ Экран захвачен: {frame.shape[1]}x{frame.shape[0]}")
    
    # Шаг 3: Выделение области
    print("\n3️⃣  Выделение области")
    print("-" * 60)
    
    success = capture.interactive_select(frame)
    
    if not success:
        print("\n❌ Отменено")
        return
    
    # Шаг 4: Превью
    print("\n4️⃣  Превью")
    print("-" * 60)
    capture.show_preview()
    
    # Шаг 5: Сохранение
    print("\n5️⃣  Сохранение")
    print("-" * 60)
    
    # Предлагаем имя файла
    print("\n💡 Примеры имен:")
    print("   • atlas_icon.png")
    print("   • plus_button.png")
    print("   • close_button.png")
    print("   • search_field.png")
    
    while True:
        filename = input("\n📝 Имя файла (Enter=button.png): ").strip()
        
        if filename == "":
            filename = "button.png"
        
        # Добавляем .png если нужно
        if not filename.endswith('.png'):
            filename += '.png'
        
        # Создаем папку templates если не существует
        templates_dir = Path("templates")
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Полный путь
        output_path = str(templates_dir / filename)
        
        # Проверяем существование
        if os.path.exists(output_path):
            overwrite = input(f"⚠️  Файл {filename} существует. Перезаписать? (y/n): ").strip().lower()
            if overwrite != 'y':
                continue
        
        break
    
    # Сохраняем
    if capture.save_template(output_path):
        print("\n" + "="*60)
        print("🎉 Готово!")
        print("="*60)
        print(f"📁 Сохранено: templates/{filename}")
        print("="*60)
        print(f"\n💡 Используй в конфиге:")
        print(f"   template: {output_path}")
        print("\n💡 Или запусти тест:")
        print(f"   python3 test_template.py")
        print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✋ Отменено")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
