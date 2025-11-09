#!/usr/bin/env python3
"""
Тест для проверки правильных селекторов комментариев TikTok
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

def test_selectors():
    """Проверка разных селекторов"""
    
    print("="*60)
    print("🔍 ТЕСТ СЕЛЕКТОРОВ КОММЕНТАРИЕВ")
    print("="*60)
    
    try:
        # Подключение
        print("\n1️⃣ Подключение к Chrome...")
        chromedriver_path = "/tmp/chromedriver_temp/chromedriver-mac-arm64/chromedriver"
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Подключено!")
        print(f"   URL: {driver.current_url}")
        
        # Список селекторов для проверки
        selectors = [
            "[class*='comment-sidebar'] [data-e2e='comment-level-1']",
            "[class*='comment-sidebar'] span[class*='SpanText']",
            "[class*='comment-sidebar'] span[class*='Text']",
            "[class*='comment-sidebar'] [data-e2e='comment-text']",
            "[data-e2e='comment-level-1'] span",
            "[data-e2e='comment-text']",
        ]
        
        print("\n2️⃣ Проверка селекторов:\n")
        
        for i, selector in enumerate(selectors, 1):
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    print(f"✅ {i}. Селектор: {selector}")
                    print(f"   Найдено: {len(elements)} элементов")
                    
                    # Показать первые 3 с текстом
                    count = 0
                    for j, elem in enumerate(elements):
                        try:
                            text = elem.text.strip()
                            if text and len(text) > 5:
                                count += 1
                                if count <= 3:
                                    print(f"   [{j}] {text[:50]}...")
                        except:
                            pass
                    
                    print(f"   С текстом: {count}\n")
                else:
                    print(f"❌ {i}. Селектор: {selector}")
                    print(f"   Не найдено элементов\n")
                    
            except Exception as e:
                print(f"❌ {i}. Селектор: {selector}")
                print(f"   Ошибка: {e}\n")
        
        # Рекомендация
        print("="*60)
        print("💡 РЕКОМЕНДАЦИЯ:")
        print("="*60)
        print("\nИспользуй селектор который:")
        print("1. Нашел больше всего элементов")
        print("2. Показал комментарии с текстом")
        print("3. Не показал служебные тексты\n")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_selectors()
