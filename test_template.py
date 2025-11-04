#!/usr/bin/env python3
"""
Тестовый скрипт для проверки template matching
Показывает где найден шаблон и рисует прямоугольник
"""

import cv2
import numpy as np
import pyautogui
from pathlib import Path

TEMPLATE_PATH = "models/button.png"
TEMPLATE_THRESHOLD = 0.86

def main():
    print("🔍 Тест Template Matching")
    print("="*60)
    
    # Проверка шаблона
    if not Path(TEMPLATE_PATH).exists():
        print(f"❌ Шаблон не найден: {TEMPLATE_PATH}")
        return
    
    # Загрузка шаблона
    template = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
    if template is None:
        print(f"❌ Не удалось загрузить шаблон")
        return
    
    print(f"✅ Шаблон загружен: {template.shape[1]}x{template.shape[0]}")
    
    # Захват экрана
    print("📸 Захват экрана...")
    img = pyautogui.screenshot()
    frame = np.array(img)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    screen_w, screen_h = frame.shape[1], frame.shape[0]
    print(f"📐 Размер экрана: {screen_w}x{screen_h}")
    
    # Template matching
    print("🔎 Поиск шаблона...")
    res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    print(f"\n📊 Результаты:")
    print(f"   Максимальное совпадение: {max_val:.4f}")
    print(f"   Порог: {TEMPLATE_THRESHOLD}")
    print(f"   Статус: {'✅ НАЙДЕНО' if max_val >= TEMPLATE_THRESHOLD else '❌ НЕ НАЙДЕНО'}")
    
    if max_val >= TEMPLATE_THRESHOLD:
        h, w = template.shape
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        center = (int(top_left[0] + w/2), int(top_left[1] + h/2))
        
        print(f"\n🎯 Координаты:")
        print(f"   Верхний левый угол: {top_left}")
        print(f"   Нижний правый угол: {bottom_right}")
        print(f"   Центр (для клика): {center}")
        
        # Рисуем прямоугольник
        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 3)
        cv2.circle(frame, center, 10, (0, 0, 255), -1)
        
        # Сохраняем результат
        output_path = "test_result.png"
        cv2.imwrite(output_path, frame)
        print(f"\n💾 Результат сохранен: {output_path}")
        print(f"   Откройте файл чтобы увидеть где найден шаблон")
        
    else:
        print(f"\n💡 Совет: Попробуйте:")
        print(f"   1. Понизить порог (сейчас {TEMPLATE_THRESHOLD})")
        print(f"   2. Пересоздать шаблон: python utils/capture_button.py")
        print(f"   3. Убедиться что кнопка видна на экране")
        
        # Показываем топ-5 совпадений
        print(f"\n🔝 Топ-5 мест с наибольшим совпадением:")
        threshold = 0.5
        loc = np.where(res >= threshold)
        matches = list(zip(*loc[::-1]))
        
        if matches:
            scores = [res[y, x] for x, y in matches]
            sorted_matches = sorted(zip(matches, scores), key=lambda x: x[1], reverse=True)[:5]
            
            for i, ((x, y), score) in enumerate(sorted_matches, 1):
                h, w = template.shape
                center = (int(x + w/2), int(y + h/2))
                print(f"   {i}. Score: {score:.4f} | Center: {center}")
                
                # Рисуем все найденные места
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, f"{score:.2f}", (x, y-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            output_path = "test_result_all.png"
            cv2.imwrite(output_path, frame)
            print(f"\n💾 Все совпадения сохранены: {output_path}")
        else:
            print(f"   Не найдено совпадений выше {threshold}")

if __name__ == "__main__":
    main()
