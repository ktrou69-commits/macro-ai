#!/usr/bin/env python3
"""
example_basic.py
Базовый пример использования макроса программно (без CLI)
"""

import sys
import os

# Добавляем родительскую папку в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import numpy as np
import pyautogui
import cv2


def basic_template_matching():
    """Простейший пример template matching"""
    
    print("🎯 Базовый пример Template Matching\n")
    
    # Загрузка шаблона
    template_path = "models/button.png"
    if not os.path.exists(template_path):
        print(f"❌ Шаблон не найден: {template_path}")
        print("   Создай шаблон с помощью: python utils/capture_button.py")
        return
    
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    print(f"✅ Шаблон загружен: {template.shape}")
    
    # Параметры
    threshold = 0.86
    max_clicks = 5
    click_count = 0
    
    print(f"🔍 Ищу кнопку (макс. {max_clicks} кликов)...\n")
    
    try:
        while click_count < max_clicks:
            # Скриншот
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            
            # Поиск
            result = cv2.matchTemplate(frame_gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # Если найдено
            if max_val >= threshold:
                h, w = template.shape
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                
                print(f"✅ Найдено! Score: {max_val:.3f} → Клик ({center_x}, {center_y})")
                pyautogui.click(center_x, center_y)
                
                click_count += 1
                time.sleep(1)  # Пауза между кликами
            else:
                print(f"⏳ Поиск... (score: {max_val:.3f})")
                time.sleep(0.5)
                
    except KeyboardInterrupt:
        print("\n\n✋ Остановлено")
    
    print(f"\n📊 Выполнено кликов: {click_count}")


def find_button_once():
    """Найти кнопку один раз и вернуть координаты"""
    
    print("🔍 Поиск кнопки (один раз)...\n")
    
    template_path = "models/button.png"
    if not os.path.exists(template_path):
        print(f"❌ Шаблон не найден: {template_path}")
        return None
    
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    
    # Скриншот
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frame_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    
    # Поиск
    result = cv2.matchTemplate(frame_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= 0.86:
        h, w = template.shape
        center = (max_loc[0] + w // 2, max_loc[1] + h // 2)
        print(f"✅ Кнопка найдена: {center} (score: {max_val:.3f})")
        return center
    else:
        print(f"❌ Кнопка не найдена (score: {max_val:.3f})")
        return None


def click_button_if_found():
    """Найти и кликнуть один раз"""
    
    coords = find_button_once()
    if coords:
        print(f"🎯 Кликаю по {coords}...")
        pyautogui.click(coords[0], coords[1])
        print("✅ Клик выполнен!")
        return True
    return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("📚 Базовые примеры использования")
    print("="*60)
    print("\nВыбери пример:")
    print("  1. Непрерывный поиск и клики (5 раз)")
    print("  2. Найти кнопку один раз")
    print("  3. Найти и кликнуть один раз")
    print("="*60)
    
    choice = input("\nТвой выбор (1-3): ").strip()
    
    print("\n")
    
    if choice == "1":
        basic_template_matching()
    elif choice == "2":
        find_button_once()
    elif choice == "3":
        click_button_if_found()
    else:
        print("❌ Неверный выбор")
