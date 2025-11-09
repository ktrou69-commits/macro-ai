#!/usr/bin/env python3
"""
Тест для поиска кнопки "Ответить" внутри контейнера комментария
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

def test_reply_button():
    """Проверка селекторов кнопки Ответить"""
    
    print("="*60)
    print("🔍 ТЕСТ КНОПКИ ОТВЕТИТЬ")
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
        
        # Найти контейнеры комментариев
        print("\n2️⃣ Поиск контейнеров комментариев...")
        containers = driver.find_elements(By.CSS_SELECTOR, "[data-e2e='comment-level-1']")
        print(f"✅ Найдено контейнеров: {len(containers)}")
        
        if not containers:
            print("❌ Контейнеры не найдены!")
            return
        
        # Взять первый контейнер
        container = containers[0]
        print(f"\n3️⃣ Анализ первого контейнера:")
        
        # Попробовать разные селекторы для кнопки
        selectors = [
            "span[data-e2e*='comment-reply']",
            "span[data-e2e='comment-reply-1']",
            "span[aria-label='Ответить']",
            "span[role='button']",
            "span.TUXText[aria-label='Ответить']",
            "*[aria-label='Ответить']",
        ]
        
        for i, selector in enumerate(selectors, 1):
            try:
                button = container.find_element(By.CSS_SELECTOR, selector)
                if button:
                    print(f"\n✅ {i}. Селектор работает: {selector}")
                    print(f"   Текст: {button.text}")
                    print(f"   data-e2e: {button.get_attribute('data-e2e')}")
                    print(f"   aria-label: {button.get_attribute('aria-label')}")
                    print(f"   role: {button.get_attribute('role')}")
            except:
                print(f"❌ {i}. Не работает: {selector}")
        
        # Показать все элементы с "Ответить"
        print(f"\n4️⃣ Все элементы содержащие 'Ответить':")
        all_elements = container.find_elements(By.XPATH, ".//*[contains(text(), 'Ответить')]")
        print(f"   Найдено внутри: {len(all_elements)}")
        
        # Искать рядом (следующий элемент)
        print(f"\n5️⃣ Поиск кнопки рядом с контейнером:")
        try:
            # Родитель контейнера
            parent = container.find_element(By.XPATH, "..")
            print(f"   ✅ Найден родитель")
            
            # Все кнопки "Ответить" в родителе
            buttons = parent.find_elements(By.XPATH, ".//*[contains(text(), 'Ответить')]")
            print(f"   Найдено кнопок в родителе: {len(buttons)}")
            
            for btn in buttons[:3]:
                print(f"   - {btn.tag_name}: {btn.text}")
                print(f"     data-e2e: {btn.get_attribute('data-e2e')}")
                print(f"     class: {btn.get_attribute('class')}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        # Показать HTML структуру
        print(f"\n6️⃣ HTML структура контейнера:")
        try:
            html = container.get_attribute('outerHTML')[:500]
            print(f"   {html}...")
        except:
            pass
        
        print("\n" + "="*60)
        print("✅ ТЕСТ ЗАВЕРШЕН")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reply_button()
