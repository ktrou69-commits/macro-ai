#!/usr/bin/env python3
"""
example_advanced.py
Продвинутые примеры: ROI, мультишаблоны, условные клики
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import numpy as np
import pyautogui
import cv2
from typing import Optional, Tuple, List


class AdvancedMacro:
    """Продвинутый макрос с дополнительными возможностями"""
    
    def __init__(self, template_path: str):
        self.template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if self.template is None:
            raise ValueError(f"Не удалось загрузить шаблон: {template_path}")
        
        self.roi = None  # Region of Interest
        self.click_history = []
        
    def set_roi(self, x: int, y: int, width: int, height: int):
        """Установить область поиска (ускоряет работу)"""
        self.roi = (x, y, width, height)
        print(f"✅ ROI установлен: {self.roi}")
        
    def find_button(self, threshold: float = 0.86) -> Optional[Tuple[int, int]]:
        """Найти кнопку с учетом ROI"""
        
        # Скриншот
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Применить ROI если установлен
        if self.roi:
            x, y, w, h = self.roi
            search_area = frame_bgr[y:y+h, x:x+w]
            offset_x, offset_y = x, y
        else:
            search_area = frame_bgr
            offset_x, offset_y = 0, 0
        
        # Конвертация в grayscale
        search_gray = cv2.cvtColor(search_area, cv2.COLOR_BGR2GRAY)
        
        # Поиск
        result = cv2.matchTemplate(search_gray, self.template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            h, w = self.template.shape
            center_x = max_loc[0] + w // 2 + offset_x
            center_y = max_loc[1] + h // 2 + offset_y
            return (center_x, center_y), max_val
        
        return None, max_val
    
    def click_with_condition(self, condition_func=None) -> bool:
        """Кликнуть только если выполнено условие"""
        
        result = self.find_button()
        if result[0] is None:
            return False
        
        coords, score = result
        
        # Проверка условия
        if condition_func and not condition_func(coords, score):
            print(f"⏭️  Условие не выполнено, пропускаю клик")
            return False
        
        # Клик
        pyautogui.click(coords[0], coords[1])
        self.click_history.append({
            'coords': coords,
            'score': score,
            'time': time.time()
        })
        
        print(f"✅ Клик: {coords} (score: {score:.3f})")
        return True
    
    def wait_for_button(self, timeout: float = 10.0, check_interval: float = 0.5) -> bool:
        """Ждать появления кнопки"""
        
        print(f"⏳ Жду появления кнопки (таймаут: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self.find_button()
            if result[0] is not None:
                print(f"✅ Кнопка появилась!")
                return True
            time.sleep(check_interval)
        
        print(f"❌ Таймаут: кнопка не появилась за {timeout}s")
        return False
    
    def get_stats(self):
        """Статистика кликов"""
        if not self.click_history:
            return "Кликов не было"
        
        total = len(self.click_history)
        avg_score = sum(h['score'] for h in self.click_history) / total
        
        return f"Кликов: {total}, Средний score: {avg_score:.3f}"


def example_roi():
    """Пример использования ROI для ускорения"""
    
    print("🎯 Пример: Region of Interest (ROI)\n")
    
    macro = AdvancedMacro("models/button.png")
    
    # Установим ROI - ищем только в правой части экрана
    screen_width, screen_height = pyautogui.size()
    macro.set_roi(
        x=screen_width // 2,  # правая половина
        y=0,
        width=screen_width // 2,
        height=screen_height
    )
    
    print("🔍 Ищу кнопку только в правой половине экрана...\n")
    
    for i in range(5):
        result = macro.find_button()
        if result[0]:
            coords, score = result
            print(f"✅ Итерация {i+1}: Найдено {coords} (score: {score:.3f})")
            pyautogui.click(coords[0], coords[1])
            time.sleep(1)
        else:
            print(f"⏳ Итерация {i+1}: Не найдено")
            time.sleep(0.5)
    
    print(f"\n📊 {macro.get_stats()}")


def example_conditional_click():
    """Пример условного клика"""
    
    print("🎯 Пример: Условный клик\n")
    
    macro = AdvancedMacro("models/button.png")
    
    # Условие: кликать только если score > 0.9
    def high_confidence_only(coords, score):
        return score > 0.9
    
    print("🔍 Кликаю только если уверенность > 90%...\n")
    
    for i in range(5):
        print(f"Попытка {i+1}:")
        if macro.click_with_condition(high_confidence_only):
            time.sleep(1)
        else:
            time.sleep(0.5)
    
    print(f"\n📊 {macro.get_stats()}")


def example_wait_and_click():
    """Пример ожидания появления кнопки"""
    
    print("🎯 Пример: Ожидание появления кнопки\n")
    
    macro = AdvancedMacro("models/button.png")
    
    print("💡 Открой окно с кнопкой в течение 15 секунд...\n")
    
    if macro.wait_for_button(timeout=15.0):
        print("🎯 Кликаю!")
        result = macro.find_button()
        if result[0]:
            coords, score = result
            pyautogui.click(coords[0], coords[1])
            print(f"✅ Клик выполнен: {coords}")


def example_multi_click_sequence():
    """Пример последовательности кликов с задержками"""
    
    print("🎯 Пример: Последовательность кликов\n")
    
    macro = AdvancedMacro("models/button.png")
    
    sequence = [
        {'clicks': 2, 'delay': 0.5, 'wait': 1.0},  # 2 клика с задержкой 0.5с, потом ждать 1с
        {'clicks': 1, 'delay': 0, 'wait': 2.0},    # 1 клик, ждать 2с
        {'clicks': 3, 'delay': 0.3, 'wait': 0},    # 3 клика с задержкой 0.3с
    ]
    
    print("🔄 Выполняю последовательность кликов...\n")
    
    for i, step in enumerate(sequence):
        print(f"Шаг {i+1}: {step['clicks']} клик(ов)")
        
        for j in range(step['clicks']):
            result = macro.find_button()
            if result[0]:
                coords, score = result
                pyautogui.click(coords[0], coords[1])
                print(f"  ✅ Клик {j+1}/{step['clicks']}")
                
                if j < step['clicks'] - 1:  # не ждать после последнего клика в серии
                    time.sleep(step['delay'])
        
        if step['wait'] > 0:
            print(f"  ⏳ Жду {step['wait']}s...")
            time.sleep(step['wait'])
    
    print(f"\n📊 {macro.get_stats()}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Продвинутые примеры")
    print("="*60)
    print("\nВыбери пример:")
    print("  1. ROI (поиск в определенной области)")
    print("  2. Условный клик (только при высокой уверенности)")
    print("  3. Ожидание появления кнопки")
    print("  4. Последовательность кликов")
    print("="*60)
    
    choice = input("\nТвой выбор (1-4): ").strip()
    
    print("\n")
    
    try:
        if choice == "1":
            example_roi()
        elif choice == "2":
            example_conditional_click()
        elif choice == "3":
            example_wait_and_click()
        elif choice == "4":
            example_multi_click_sequence()
        else:
            print("❌ Неверный выбор")
    except KeyboardInterrupt:
        print("\n\n✋ Остановлено")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
