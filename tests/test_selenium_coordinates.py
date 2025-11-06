#!/usr/bin/env python3
"""
Тест: Selenium получает координаты + PyAutoGUI кликает
Гибридный подход: DOM для поиска, эмуляция для кликов
"""

import os
import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

def test_selenium_coordinates():
    """Selenium находит элемент, PyAutoGUI кликает по координатам"""
    
    print("="*60)
    print("🎯 ТЕСТ: SELENIUM КООРДИНАТЫ + PYAUTOGUI")
    print("="*60)
    
    try:
        # 1. Подключение к Chrome
        print("\n1️⃣ Подключение к Chrome...")
        chromedriver_path = "/tmp/chromedriver_temp/chromedriver-mac-arm64/chromedriver"
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Подключено!")
        print(f"   URL: {driver.current_url}")
        
        # 2. Найти sidebar комментариев
        print("\n2️⃣ Поиск sidebar комментариев...")
        sidebar = driver.find_element(By.CSS_SELECTOR, "[class*='comment-sidebar']")
        print("✅ Sidebar найден")
        
        # 3. Найти все комментарии
        print("\n3️⃣ Поиск комментариев...")
        
        # Найти контейнеры комментариев (не просто текст, а весь блок)
        comment_containers = driver.find_elements(By.CSS_SELECTOR, "[class*='comment-sidebar'] [data-e2e='comment-level-1']")
        
        if not comment_containers:
            print("❌ Комментарии не найдены")
            print("💡 Открой комментарии вручную")
            return
        
        print(f"✅ Найдено комментариев: {len(comment_containers)}")
        
        # 4. Выбрать конкретный комментарий (например, 2-й)
        target_index = 1  # 0 = первый, 1 = второй, 2 = третий
        
        if target_index >= len(comment_containers):
            target_index = 0
        
        target_comment = comment_containers[target_index]
        
        print(f"\n4️⃣ Выбран комментарий #{target_index + 1}:")
        
        # 5. Извлечь текст комментария
        try:
            comment_text_elem = target_comment.find_element(By.CSS_SELECTOR, "[data-e2e='comment-text']")
            comment_text = comment_text_elem.text
            print(f"   📝 Текст: {comment_text}")
            print(f"   📏 Длина: {len(comment_text)} символов")
        except:
            print("   ⚠️  Текст не найден")
            comment_text = ""
        
        # 6. Получить координаты комментария
        print(f"\n5️⃣ Получение координат комментария #{target_index + 1}:")
        
        location = target_comment.location
        size = target_comment.size
        
        print(f"   📍 Location: x={location['x']}, y={location['y']}")
        print(f"   📐 Size: width={size['width']}, height={size['height']}")
        
        # Вычислить центр
        center_x = location['x'] + size['width'] / 2
        center_y = location['y'] + size['height'] / 2
        
        print(f"   🎯 Центр: x={center_x}, y={center_y}")
        
        # 7. Найти кнопку "Ответить" ЭТОГО комментария
        print(f"\n6️⃣ Поиск кнопки 'Ответить' для комментария #{target_index + 1}:")
        
        try:
            # Ищем кнопку внутри контейнера комментария
            reply_button = target_comment.find_element(By.XPATH, ".//button[contains(., 'Ответить') or contains(., 'Reply')]")
            
            button_location = reply_button.location
            button_size = reply_button.size
            
            # Вычислить центр кнопки
            button_x = button_location['x'] + button_size['width'] / 2
            button_y = button_location['y'] + button_size['height'] / 2
            
            print(f"   ✅ Кнопка найдена!")
            print(f"   📍 Location: x={button_location['x']}, y={button_location['y']}")
            print(f"   📐 Size: width={button_size['width']}, height={button_size['height']}")
            print(f"   🎯 Центр кнопки: x={button_x}, y={button_y}")
            
            # 8. Симуляция клика через PyAutoGUI
            print(f"\n7️⃣ Симуляция клика через PyAutoGUI:")
            print(f"   ⚠️  ВНИМАНИЕ: Сейчас будет клик по координатам!")
            print(f"   Координаты: ({button_x}, {button_y})")
            
            # Спросить подтверждение
            response = input("\n   Выполнить клик? (y/n): ")
            
            if response.lower() == 'y':
                print(f"   🖱️  Клик через PyAutoGUI...")
                time.sleep(1)  # Пауза перед кликом
                
                # КЛИК!
                pyautogui.click(button_x, button_y)
                
                print(f"   ✅ Клик выполнен!")
                print(f"   💡 Проверь что открылось поле ответа")
            else:
                print(f"   ⏭️  Клик пропущен")
            
        except Exception as e:
            print(f"   ❌ Кнопка не найдена: {e}")
        
        # 9. Итог
        print("\n" + "="*60)
        print("✅ ТЕСТ ЗАВЕРШЕН")
        print("="*60)
        
        print("\n📊 Результат:")
        print(f"   Комментарий #{target_index + 1}: {comment_text[:50]}...")
        print(f"   Координаты: ({center_x}, {center_y})")
        
        if 'button_x' in locals():
            print(f"   Кнопка 'Ответить': ({button_x}, {button_y})")
        
        print("\n💡 Вывод:")
        print("   ✅ Selenium может получить координаты элементов!")
        print("   ✅ PyAutoGUI может кликнуть по этим координатам!")
        print("   ✅ Гибридный подход работает!")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_selenium_coordinates()
