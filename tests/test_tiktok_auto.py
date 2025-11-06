#!/usr/bin/env python3
"""
Автоматический тест - открывает комментарии и читает их
"""

import os
import platform
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_tiktok_auto():
    """Автоматический тест с открытием комментариев"""
    
    print("="*60)
    print("🤖 АВТОМАТИЧЕСКИЙ ТЕСТ TIKTOK")
    print("="*60)
    
    try:
        # 1. Подключение
        print("\n1️⃣ Подключение к Chrome...")
        chromedriver_path = "/tmp/chromedriver_temp/chromedriver-mac-arm64/chromedriver"
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Подключено!")
        
        # 2. Проверка URL
        print("\n2️⃣ Текущая страница:")
        current_url = driver.current_url
        print(f"   URL: {current_url}")
        
        if "tiktok.com" not in current_url:
            print("\n⚠️  Это не TikTok!")
            return
        
        # 3. Попытка открыть комментарии
        print("\n3️⃣ Открытие комментариев...")
        
        # Селекторы кнопки комментариев
        comment_button_selectors = [
            "[data-e2e='browse-comment']",
            "[data-e2e='comment-icon']",
            "button[aria-label*='comment']",
            "button[aria-label*='Comment']",
            ".comment-icon",
        ]
        
        clicked = False
        for selector in comment_button_selectors:
            try:
                button = driver.find_element(By.CSS_SELECTOR, selector)
                if button:
                    print(f"   ✅ Найдена кнопка: {selector}")
                    button.click()
                    print("   🖱️  Кликнул по кнопке комментариев")
                    clicked = True
                    time.sleep(2)  # Ждем загрузки
                    break
            except:
                pass
        
        if not clicked:
            print("   ⚠️  Кнопка комментариев не найдена")
            print("   💡 Попробуй кликнуть вручную и запусти снова")
        
        # 4. Скролл вниз для загрузки комментариев
        print("\n4️⃣ Скролл для загрузки комментариев...")
        try:
            driver.execute_script("window.scrollBy(0, 500)")
            time.sleep(1)
            print("   ✅ Скролл выполнен")
        except:
            pass
        
        # 5. Поиск комментариев
        print("\n5️⃣ Поиск комментариев...")
        
        # Ждем появления комментариев
        try:
            wait = WebDriverWait(driver, 5)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-e2e='comment-text']")))
            print("   ✅ Комментарии загружены")
        except:
            print("   ⚠️  Комментарии не загрузились за 5 секунд")
        
        # Ищем все комментарии (внутри sidebar)
        selectors = [
            "[class*='comment-sidebar'] [data-e2e='comment-text']",
            "[class*='CommentSidebar'] [data-e2e='comment-text']",
            "[data-e2e='comment-level-1'] [data-e2e='comment-text']",
            "[data-e2e='comment-text']",
            "[class*='comment'] span",
            ".comment-text-content",
        ]
        
        found_comments = []
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"\n   ✅ Селектор '{selector}': найдено {len(elements)}")
                    
                    for i, elem in enumerate(elements):
                        try:
                            text = elem.text.strip()
                            # Фильтруем placeholder
                            if text and text not in found_comments and "Добавить комментарий" not in text:
                                found_comments.append(text)
                                if i < 5:  # Показываем первые 5
                                    print(f"      {len(found_comments)}. {text[:100]}...")
                        except:
                            pass
                    
                    if found_comments:
                        break
            except Exception as e:
                print(f"   ❌ Селектор '{selector}': {e}")
        
        # 6. Итог
        print("\n" + "="*60)
        if found_comments:
            print(f"✅ НАЙДЕНО КОММЕНТАРИЕВ: {len(found_comments)}")
            print("="*60)
            
            print("\n📝 Все найденные комментарии:\n")
            for i, comment in enumerate(found_comments, 1):
                print(f"{i}. {comment}\n")
            
            print("="*60)
            print("🎉 УСПЕХ! Selenium читает комментарии любой длины!")
            print("="*60)
            
            # Показать длину комментариев
            print("\n📊 Статистика длины комментариев:")
            for i, comment in enumerate(found_comments[:5], 1):
                print(f"   {i}. Длина: {len(comment)} символов")
            
        else:
            print("⚠️  КОММЕНТАРИИ НЕ НАЙДЕНЫ")
            print("="*60)
            print("\n💡 Попробуй:")
            print("   1. Кликни на иконку комментариев вручную")
            print("   2. Прокрути вниз")
            print("   3. Запусти тест снова")
            
            # Показать структуру для отладки
            print("\n🔍 Отладка - поиск элементов с 'comment' в классе:")
            try:
                all_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='comment']")
                print(f"   Найдено элементов с 'comment': {len(all_elements)}")
                
                for elem in all_elements[:5]:
                    try:
                        tag = elem.tag_name
                        classes = elem.get_attribute('class')
                        text = elem.text[:50] if elem.text else ""
                        print(f"   - {tag}.{classes}: {text}...")
                    except:
                        pass
            except:
                pass
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tiktok_auto()
