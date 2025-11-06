#!/usr/bin/env python3
"""
Тест Selenium - подключение к Chrome и чтение DOM
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_selenium():
    """Тест подключения к Chrome"""
    
    print("="*60)
    print("🧪 ТЕСТ SELENIUM")
    print("="*60)
    
    try:
        # 1. Подключение к Chrome с debugging
        print("\n1️⃣ Подключение к Chrome...")
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Подключено!")
        
        # 2. Получить текущий URL
        print("\n2️⃣ Текущая страница:")
        current_url = driver.current_url
        print(f"   URL: {current_url}")
        
        # 3. Получить title
        print("\n3️⃣ Заголовок страницы:")
        title = driver.title
        print(f"   Title: {title}")
        
        # 4. Найти элементы
        print("\n4️⃣ Поиск элементов...")
        
        # Попробуем найти разные элементы
        selectors = [
            ("body", "Тело страницы"),
            ("h1", "Заголовок H1"),
            ("a", "Ссылки"),
            ("button", "Кнопки"),
            ("input", "Поля ввода"),
            ("div", "Блоки DIV"),
        ]
        
        for selector, description in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   ✅ {description} ({selector}): найдено {len(elements)}")
                    
                    # Показать текст первого элемента
                    if elements[0].text:
                        text = elements[0].text[:100]
                        print(f"      Текст: {text}...")
                else:
                    print(f"   ⚠️  {description} ({selector}): не найдено")
            except Exception as e:
                print(f"   ❌ {description} ({selector}): ошибка - {e}")
        
        # 5. Специфичные селекторы для TikTok (если на TikTok)
        if "tiktok.com" in current_url:
            print("\n5️⃣ Специфичные селекторы TikTok:")
            
            tiktok_selectors = [
                ("[data-e2e='comment-text']", "Комментарии"),
                ("[data-e2e='browse-video']", "Видео"),
                ("[data-e2e='comment-level-1']", "Комментарии 1 уровня"),
                (".tiktok-comment", "Комментарии (класс)"),
            ]
            
            for selector, description in tiktok_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"   ✅ {description}: найдено {len(elements)}")
                        
                        # Показать текст первого
                        if elements[0].text:
                            text = elements[0].text[:100]
                            print(f"      Текст: {text}...")
                    else:
                        print(f"   ⚠️  {description}: не найдено")
                except Exception as e:
                    print(f"   ❌ {description}: ошибка - {e}")
        
        # 6. Извлечь весь текст страницы
        print("\n6️⃣ Весь текст страницы:")
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            full_text = body.text
            print(f"   Длина текста: {len(full_text)} символов")
            print(f"   Первые 200 символов:")
            print(f"   {full_text[:200]}...")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
        
        print("\n" + "="*60)
        print("✅ ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
        print("="*60)
        
        # Не закрываем браузер
        # driver.quit()
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        print("\n💡 Убедись что:")
        print("   1. Chrome запущен с --remote-debugging-port=9222")
        print("   2. Выполнил: ./start_chrome_debug.sh")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_selenium()
