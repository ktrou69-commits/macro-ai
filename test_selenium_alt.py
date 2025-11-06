#!/usr/bin/env python3
"""
Альтернативный тест Selenium - без webdriver-manager
Скачивает ChromeDriver напрямую
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
        if platform.system() == "Darwin":  # macOS
            # Попробуем разные пути
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
    """Скачать ChromeDriver для конкретной версии"""
    print(f"📥 Скачивание ChromeDriver для Chrome {version}...")
    
    # Получить major version
    major_version = version.split('.')[0]
    
    # URL для скачивания (Chrome for Testing)
    base_url = "https://googlechromelabs.github.io/chrome-for-testing"
    
    # Определить платформу
    if platform.system() == "Darwin":
        if platform.machine() == "arm64":
            platform_name = "mac-arm64"
        else:
            platform_name = "mac-x64"
    
    # Скачать ChromeDriver
    download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/{platform_name}/chromedriver-{platform_name}.zip"
    
    print(f"   URL: {download_url}")
    
    try:
        response = requests.get(download_url)
        if response.status_code == 200:
            # Сохранить zip
            zip_path = "/tmp/chromedriver.zip"
            with open(zip_path, "wb") as f:
                f.write(response.content)
            
            # Распаковать
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall("/tmp/chromedriver_temp")
            
            # Найти chromedriver
            chromedriver_path = f"/tmp/chromedriver_temp/chromedriver-{platform_name}/chromedriver"
            
            if os.path.exists(chromedriver_path):
                # Сделать исполняемым
                os.chmod(chromedriver_path, 0o755)
                print(f"✅ ChromeDriver скачан: {chromedriver_path}")
                return chromedriver_path
        
        print(f"❌ Не удалось скачать (status: {response.status_code})")
        return None
        
    except Exception as e:
        print(f"❌ Ошибка скачивания: {e}")
        return None

def test_selenium():
    """Тест подключения к Chrome"""
    
    print("="*60)
    print("🧪 АЛЬТЕРНАТИВНЫЙ ТЕСТ SELENIUM")
    print("="*60)
    
    try:
        # 1. Получить версию Chrome
        print("\n1️⃣ Определение версии Chrome...")
        chrome_version = get_chrome_version()
        if chrome_version:
            print(f"   Chrome версия: {chrome_version}")
        else:
            print("   ⚠️  Не удалось определить версию Chrome")
            chrome_version = "142.0.7444.60"  # Твоя версия
            print(f"   Используем: {chrome_version}")
        
        # 2. Скачать ChromeDriver
        print("\n2️⃣ Скачивание ChromeDriver...")
        chromedriver_path = download_chromedriver(chrome_version)
        
        if not chromedriver_path:
            print("❌ Не удалось скачать ChromeDriver")
            return
        
        # 3. Подключение к Chrome
        print("\n3️⃣ Подключение к Chrome...")
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Подключено!")
        
        # 4. Получить текущий URL
        print("\n4️⃣ Текущая страница:")
        current_url = driver.current_url
        print(f"   URL: {current_url}")
        
        # 5. Получить title
        print("\n5️⃣ Заголовок страницы:")
        title = driver.title
        print(f"   Title: {title}")
        
        # 6. Найти элементы
        print("\n6️⃣ Поиск элементов...")
        
        selectors = [
            ("body", "Тело страницы"),
            ("h1", "Заголовок H1"),
            ("a", "Ссылки"),
            ("button", "Кнопки"),
        ]
        
        for selector, description in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   ✅ {description}: найдено {len(elements)}")
                    if elements[0].text:
                        text = elements[0].text[:50]
                        print(f"      Текст: {text}...")
            except Exception as e:
                print(f"   ❌ {description}: {e}")
        
        print("\n" + "="*60)
        print("✅ ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_selenium()
