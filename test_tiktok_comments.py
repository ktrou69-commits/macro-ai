#!/usr/bin/env python3
"""
Тест чтения комментариев TikTok через Selenium
"""

import os
import platform
import requests
import zipfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

def get_chrome_version():
    """Получить версию Chrome"""
    try:
        import subprocess
        if platform.system() == "Darwin":
            paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome"
            ]
            
            for path in paths:
                if os.path.exists(path):
                    result = subprocess.run([path, "--version"], capture_output=True, text=True)
                    version = result.stdout.strip().split()[-1]
                    return version
        return None
    except:
        return None

def download_chromedriver(version):
    """Скачать ChromeDriver"""
    chromedriver_path = "/tmp/chromedriver_temp/chromedriver-mac-arm64/chromedriver"
    
    # Если уже скачан, используем его
    if os.path.exists(chromedriver_path):
        return chromedriver_path
    
    print(f"📥 Скачивание ChromeDriver для Chrome {version}...")
    
    major_version = version.split('.')[0]
    
    if platform.system() == "Darwin":
        if platform.machine() == "arm64":
            platform_name = "mac-arm64"
        else:
            platform_name = "mac-x64"
    
    download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/{platform_name}/chromedriver-{platform_name}.zip"
    
    try:
        response = requests.get(download_url)
        if response.status_code == 200:
            zip_path = "/tmp/chromedriver.zip"
            with open(zip_path, "wb") as f:
                f.write(response.content)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("/tmp/chromedriver_temp")
            
            if os.path.exists(chromedriver_path):
                os.chmod(chromedriver_path, 0o755)
                print(f"✅ ChromeDriver готов")
                return chromedriver_path
        
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def test_tiktok_comments():
    """Тест чтения комментариев TikTok"""
    
    print("="*60)
    print("🎯 ТЕСТ ЧТЕНИЯ КОММЕНТАРИЕВ TIKTOK")
    print("="*60)
    
    try:
        # 1. Подключение
        print("\n1️⃣ Подключение к Chrome...")
        chrome_version = get_chrome_version()
        chromedriver_path = download_chromedriver(chrome_version)
        
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
            print("💡 Открой видео TikTok в Chrome и запусти снова")
            return
        
        # 3. Поиск комментариев
        print("\n3️⃣ Поиск комментариев...")
        
        # Разные селекторы для комментариев
        selectors = [
            "[data-e2e='comment-text']",
            "[data-e2e='comment-level-1'] [data-e2e='comment-text']",
            ".comment-text",
            "[class*='comment']",
        ]
        
        found_comments = []
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"\n   ✅ Селектор '{selector}': найдено {len(elements)}")
                    
                    # Показать первые 5 комментариев
                    for i, elem in enumerate(elements[:5]):
                        try:
                            text = elem.text.strip()
                            if text and text not in found_comments:
                                found_comments.append(text)
                                print(f"      {i+1}. {text[:100]}...")
                        except:
                            pass
                    
                    if found_comments:
                        break
            except Exception as e:
                print(f"   ❌ Селектор '{selector}': {e}")
        
        # 4. Итог
        print("\n" + "="*60)
        if found_comments:
            print(f"✅ НАЙДЕНО КОММЕНТАРИЕВ: {len(found_comments)}")
            print("="*60)
            
            print("\n📝 Все найденные комментарии:")
            for i, comment in enumerate(found_comments, 1):
                print(f"\n{i}. {comment}")
            
            print("\n" + "="*60)
            print("🎉 ТЕСТ УСПЕШЕН! Selenium читает комментарии!")
            print("="*60)
        else:
            print("⚠️  КОММЕНТАРИИ НЕ НАЙДЕНЫ")
            print("="*60)
            print("\n💡 Возможные причины:")
            print("   1. Комментарии не загружены (прокрути вниз)")
            print("   2. Нужно открыть панель комментариев")
            print("   3. TikTok изменил структуру DOM")
            
            # Показать весь HTML для анализа
            print("\n📋 Структура страницы (первые 500 символов):")
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                html = body.get_attribute('innerHTML')
                print(html[:500])
            except:
                pass
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tiktok_comments()
