#!/usr/bin/env python3
"""
capture_button.py
Интерактивный помощник для захвата шаблона кнопки.
Позволяет выделить область на экране и сохранить как button.png
"""

import pyautogui
import cv2
import numpy as np
from PIL import Image
import os

def capture_template():
    """Захват шаблона кнопки с помощью выделения области"""
    
    print("\n" + "="*60)
    print("🎯 Помощник захвата шаблона кнопки")
    print("="*60)
    print("\nИнструкция:")
    print("1. Сейчас откроется полноэкранный скриншот")
    print("2. Выдели область с кнопкой мышью (нажми и тяни)")
    print("3. Нажми Enter для сохранения или Esc для отмены")
    print("4. Шаблон сохранится в models/button.png")
    print("\n💡 Совет: Захватывай только саму кнопку без лишнего фона")
    print("="*60)
    
    input("\nНажми Enter когда будешь готов...")
    
    # Делаем скриншот
    print("\n📸 Делаю скриншот...")
    screenshot = pyautogui.screenshot()
    img_array = np.array(screenshot)
    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    # Переменные для выделения
    selecting = False
    start_point = None
    end_point = None
    current_img = img_bgr.copy()
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal selecting, start_point, end_point, current_img
        
        if event == cv2.EVENT_LBUTTONDOWN:
            selecting = True
            start_point = (x, y)
            end_point = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if selecting:
                end_point = (x, y)
                current_img = img_bgr.copy()
                cv2.rectangle(current_img, start_point, end_point, (0, 255, 0), 2)
                
        elif event == cv2.EVENT_LBUTTONUP:
            selecting = False
            end_point = (x, y)
            current_img = img_bgr.copy()
            cv2.rectangle(current_img, start_point, end_point, (0, 255, 0), 2)
    
    # Создаем окно
    window_name = "Выдели кнопку | Enter - сохранить | Esc - отмена"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    print("\n✅ Выдели область с кнопкой...")
    
    while True:
        cv2.imshow(window_name, current_img)
        key = cv2.waitKey(1) & 0xFF
        
        # Enter - сохранить
        if key == 13:
            if start_point and end_point:
                break
            else:
                print("⚠️  Сначала выдели область!")
                
        # Esc - отмена
        elif key == 27:
            print("\n❌ Отменено")
            cv2.destroyAllWindows()
            return
    
    cv2.destroyAllWindows()
    
    # Извлекаем выделенную область
    x1, y1 = start_point
    x2, y2 = end_point
    
    # Нормализуем координаты
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)
    
    # Проверка размера
    if x2 - x1 < 10 or y2 - y1 < 10:
        print("\n❌ Область слишком маленькая! Попробуй еще раз.")
        return
    
    # Вырезаем область
    template = img_bgr[y1:y2, x1:x2]
    
    # Создаем папку models если нет
    os.makedirs("models", exist_ok=True)
    
    # Сохраняем
    output_path = "models/button.png"
    cv2.imwrite(output_path, template)
    
    print(f"\n✅ Шаблон сохранен: {output_path}")
    print(f"   Размер: {template.shape[1]}x{template.shape[0]} px")
    
    # Показываем превью
    print("\n👀 Показываю превью (нажми любую клавишу для закрытия)...")
    cv2.imshow("Сохраненный шаблон", template)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    print("\n🎉 Готово! Теперь можешь запустить:")
    print("   python macro_ai.py --template")


def capture_from_coordinates():
    """Захват шаблона по координатам (если знаешь точное расположение)"""
    
    print("\n" + "="*60)
    print("📐 Захват по координатам")
    print("="*60)
    
    try:
        print("\nВведи координаты области с кнопкой:")
        x1 = int(input("  X (левый край): "))
        y1 = int(input("  Y (верхний край): "))
        width = int(input("  Ширина: "))
        height = int(input("  Высота: "))
        
        # Делаем скриншот
        print("\n📸 Делаю скриншот...")
        screenshot = pyautogui.screenshot()
        img_array = np.array(screenshot)
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Вырезаем область
        template = img_bgr[y1:y1+height, x1:x1+width]
        
        # Создаем папку
        os.makedirs("models", exist_ok=True)
        
        # Сохраняем
        output_path = "models/button.png"
        cv2.imwrite(output_path, template)
        
        print(f"\n✅ Шаблон сохранен: {output_path}")
        print(f"   Размер: {template.shape[1]}x{template.shape[0]} px")
        
        # Превью
        print("\n👀 Показываю превью (нажми любую клавишу для закрытия)...")
        cv2.imshow("Сохраненный шаблон", template)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    except ValueError:
        print("\n❌ Ошибка: введи числовые значения")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


def main():
    """Главное меню"""
    
    print("\n" + "="*60)
    print("🎯 Помощник захвата шаблона кнопки")
    print("="*60)
    print("\nВыбери режим:")
    print("  1. Интерактивное выделение (рекомендуется)")
    print("  2. Ввод координат вручную")
    print("  3. Выход")
    print("="*60)
    
    choice = input("\nТвой выбор (1-3): ").strip()
    
    if choice == "1":
        capture_template()
    elif choice == "2":
        capture_from_coordinates()
    elif choice == "3":
        print("\n👋 До встречи!")
    else:
        print("\n❌ Неверный выбор")


if __name__ == "__main__":
    main()
