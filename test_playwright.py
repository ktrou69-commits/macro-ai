#!/usr/bin/env python3
"""
Тест Playwright - подключение к Chrome и чтение DOM
Playwright проще чем Selenium и не требует ChromeDriver!
"""

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("❌ Playwright не установлен")
    print("📦 Установи: pip install playwright")
    print("🔧 Затем: playwright install chromium")
    exit(1)

def test_playwright():
    """Тест подключения к Chrome через CDP"""
    
    print("="*60)
    print("🧪 ТЕСТ PLAYWRIGHT")
    print("="*60)
    
    try:
        with sync_playwright() as p:
            # 1. Подключение к Chrome через CDP
            print("\n1️⃣ Подключение к Chrome через CDP...")
            print("   Порт: 9222")
            
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            
            print("✅ Подключено!")
            
            # 2. Получить контекст и страницу
            print("\n2️⃣ Получение активной страницы...")
            contexts = browser.contexts
            if not contexts:
                print("❌ Нет открытых вкладок")
                return
            
            context = contexts[0]
            pages = context.pages
            
            if not pages:
                print("❌ Нет открытых страниц")
                return
            
            page = pages[0]
            print(f"✅ Найдено страниц: {len(pages)}")
            
            # 3. Получить URL
            print("\n3️⃣ Текущая страница:")
            url = page.url
            print(f"   URL: {url}")
            
            # 4. Получить title
            print("\n4️⃣ Заголовок:")
            title = page.title()
            print(f"   Title: {title}")
            
            # 5. Найти элементы
            print("\n5️⃣ Поиск элементов...")
            
            selectors = [
                ("body", "Тело страницы"),
                ("h1", "Заголовок H1"),
                ("a", "Ссылки"),
                ("button", "Кнопки"),
                ("input", "Поля ввода"),
            ]
            
            for selector, description in selectors:
                try:
                    elements = page.locator(selector).all()
                    count = len(elements)
                    
                    if count > 0:
                        print(f"   ✅ {description} ({selector}): найдено {count}")
                        
                        # Показать текст первого элемента
                        try:
                            text = elements[0].text_content()
                            if text:
                                text = text.strip()[:50]
                                print(f"      Текст: {text}...")
                        except:
                            pass
                    else:
                        print(f"   ⚠️  {description} ({selector}): не найдено")
                        
                except Exception as e:
                    print(f"   ❌ {description} ({selector}): {e}")
            
            # 6. Специфичные селекторы для TikTok
            if "tiktok.com" in url:
                print("\n6️⃣ Специфичные селекторы TikTok:")
                
                tiktok_selectors = [
                    ("[data-e2e='comment-text']", "Комментарии"),
                    ("[data-e2e='browse-video']", "Видео"),
                    ("[data-e2e='comment-level-1']", "Комментарии 1 уровня"),
                ]
                
                for selector, description in tiktok_selectors:
                    try:
                        elements = page.locator(selector).all()
                        count = len(elements)
                        
                        if count > 0:
                            print(f"   ✅ {description}: найдено {count}")
                            
                            # Показать текст первого комментария
                            try:
                                text = elements[0].text_content()
                                if text:
                                    text = text.strip()[:100]
                                    print(f"      Текст: {text}...")
                            except:
                                pass
                        else:
                            print(f"   ⚠️  {description}: не найдено")
                            
                    except Exception as e:
                        print(f"   ❌ {description}: {e}")
            
            # 7. Весь текст страницы
            print("\n7️⃣ Весь текст страницы:")
            try:
                body_text = page.locator("body").text_content()
                print(f"   Длина текста: {len(body_text)} символов")
                print(f"   Первые 200 символов:")
                print(f"   {body_text[:200]}...")
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
            
            print("\n" + "="*60)
            print("✅ ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
            print("="*60)
            
            # Не закрываем браузер
            
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        print("\n💡 Убедись что:")
        print("   1. Chrome запущен с --remote-debugging-port=9222")
        print("   2. Выполнил: ./start_chrome_debug.sh")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_playwright()
