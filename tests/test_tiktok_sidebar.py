#!/usr/bin/env python3
"""
Тест чтения комментариев из sidebar TikTok
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

def test_tiktok_sidebar():
    """Чтение комментариев из sidebar"""
    
    print("="*60)
    print("🎯 ЧТЕНИЕ КОММЕНТАРИЕВ ИЗ SIDEBAR")
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
        
        # 2. URL
        print("\n2️⃣ Текущая страница:")
        print(f"   URL: {driver.current_url}")
        
        # 3. Найти sidebar
        print("\n3️⃣ Поиск sidebar комментариев...")
        
        sidebar_selectors = [
            "[class*='comment-sidebar']",
            "[class*='CommentSidebar']",
            "[class*='comment'][class*='sidebar']",
        ]
        
        sidebar = None
        for selector in sidebar_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    sidebar = elements[0]
                    print(f"   ✅ Найден sidebar: {selector}")
                    break
            except:
                pass
        
        if not sidebar:
            print("   ❌ Sidebar не найден")
            print("   💡 Открой комментарии вручную (кликни на иконку)")
            return
        
        # 4. Получить весь текст из sidebar
        print("\n4️⃣ Извлечение текста из sidebar...")
        try:
            sidebar_text = sidebar.text
            print(f"   ✅ Длина текста: {len(sidebar_text)} символов")
            print(f"\n   📝 Весь текст sidebar:\n")
            print("   " + "="*50)
            print(sidebar_text)
            print("   " + "="*50)
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # 5. Найти все span внутри sidebar
        print("\n5️⃣ Поиск span элементов в sidebar...")
        try:
            spans = sidebar.find_elements(By.TAG_NAME, "span")
            print(f"   ✅ Найдено span: {len(spans)}")
            
            comments = []
            for span in spans:
                try:
                    text = span.text.strip()
                    # Фильтруем: длина > 5 символов, не повторяется
                    if text and len(text) > 5 and text not in comments:
                        # Пропускаем служебные тексты
                        skip_words = ["Комментарии", "Ответить", "Нравится", "Добавить", "Показать"]
                        if not any(word in text for word in skip_words):
                            comments.append(text)
                except:
                    pass
            
            print(f"\n   ✅ Найдено комментариев: {len(comments)}")
            
            if comments:
                print("\n   📝 Комментарии:\n")
                for i, comment in enumerate(comments, 1):
                    print(f"   {i}. {comment}")
                    print(f"      (Длина: {len(comment)} символов)\n")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # 6. Альтернативный метод - все div внутри sidebar
        print("\n6️⃣ Альтернативный поиск (div элементы)...")
        try:
            divs = sidebar.find_elements(By.TAG_NAME, "div")
            print(f"   ✅ Найдено div: {len(divs)}")
            
            alt_comments = []
            for div in divs:
                try:
                    text = div.text.strip()
                    # Только текст длиной 10-500 символов
                    if text and 10 < len(text) < 500:
                        # Не должен содержать много переносов строк
                        if text.count('\n') < 3 and text not in alt_comments:
                            skip_words = ["Комментарии", "Ответить", "Нравится", "Добавить", "Показать"]
                            if not any(word in text for word in skip_words):
                                alt_comments.append(text)
                except:
                    pass
            
            print(f"\n   ✅ Найдено комментариев: {len(alt_comments)}")
            
            if alt_comments:
                print("\n   📝 Комментарии (альтернативный метод):\n")
                for i, comment in enumerate(alt_comments[:10], 1):
                    print(f"   {i}. {comment}")
                    print(f"      (Длина: {len(comment)} символов)\n")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print("\n" + "="*60)
        print("✅ ТЕСТ ЗАВЕРШЕН")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tiktok_sidebar()
