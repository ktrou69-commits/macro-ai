#!/usr/bin/env python3
"""
parallel_runner.py
Параллельный запуск макросов в нескольких окнах Chrome
"""

import time
import threading
import argparse
from pathlib import Path
import subprocess
import os

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("❌ Selenium не установлен")
    exit(1)


class ParallelMacroRunner:
    """Запуск макросов параллельно в разных окнах Chrome"""
    
    def __init__(self, num_instances=3, use_existing=False):
        self.num_instances = num_instances
        self.use_existing = use_existing  # Подключаться к существующим вкладкам
        self.drivers = []
        self.threads = []
        self.results = {}
        self.custom_profiles = []  # Кастомные профили
        self.custom_macros = []    # Разные макросы
        self.custom_urls = []      # Разные URL
    
    def connect_to_existing_chrome(self, instance_id, debug_port=9222):
        """
        Подключается к существующему Chrome через debug порт
        
        Args:
            instance_id: ID экземпляра (0, 1, 2, ...)
            debug_port: Debug порт (9222, 9223, ...)
        """
        print(f"🔗 Подключение к существующему Chrome #{instance_id}...")
        
        try:
            options = webdriver.ChromeOptions()
            
            # Подключение к существующему Chrome
            port = debug_port + instance_id
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
            
            # Создаем драйвер
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            print(f"✅ Подключено к Chrome #{instance_id} (порт {port})")
            return driver
            
        except Exception as e:
            print(f"❌ Ошибка подключения к Chrome #{instance_id}: {e}")
            return None
    
    def create_chrome_instance(self, instance_id, debug_port=9222, profile_dir=None):
        """
        Создает отдельный экземпляр Chrome с уникальным профилем
        
        Args:
            instance_id: ID экземпляра (0, 1, 2, ...)
            debug_port: Базовый порт для debug (9222, 9223, ...)
            profile_dir: Путь к профилю (опционально)
        """
        print(f"🚀 Запуск Chrome #{instance_id}...")
        
        try:
            options = webdriver.ChromeOptions()
            
            # Уникальный профиль для каждого экземпляра
            if profile_dir:
                # Используем кастомный профиль
                print(f"   📁 Профиль: {profile_dir}")
            else:
                # Временный профиль
                profile_dir = f"/tmp/chrome-profile-{instance_id}"
            
            options.add_argument(f"--user-data-dir={profile_dir}")
            
            # Уникальный debug порт
            port = debug_port + instance_id
            options.add_argument(f"--remote-debugging-port={port}")
            
            # Позиционирование окон (чтобы не перекрывались)
            window_offset = instance_id * 50
            options.add_argument(f"--window-position={window_offset},{window_offset}")
            options.add_argument(f"--window-size=800,900")
            
            # Отключаем некоторые проверки для скорости
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Путь к Chrome на macOS
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.exists(chrome_path):
                options.binary_location = chrome_path
            
            # Создаем драйвер
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Скрываем признаки автоматизации
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"✅ Chrome #{instance_id} запущен (порт {port})")
            return driver
            
        except Exception as e:
            print(f"❌ Ошибка запуска Chrome #{instance_id}: {e}")
            return None
    
    def run_macro_in_instance(self, driver, instance_id, macro_file, url="https://tiktok.com"):
        """
        Запускает макрос в конкретном экземпляре Chrome
        
        Args:
            driver: WebDriver экземпляр
            instance_id: ID экземпляра
            macro_file: Путь к .atlas файлу
            url: URL для открытия
        """
        print(f"📍 Instance #{instance_id}: Переход на {url}")
        
        try:
            # Открываем URL
            driver.get(url)
            time.sleep(3)
            
            # Запускаем макрос через macro_sequence.py
            cmd = [
                "python3", "macro_sequence.py",
                "--config", macro_file,
                "--run", Path(macro_file).stem,
                "--delay", "0"
            ]
            
            print(f"🎬 Instance #{instance_id}: Запуск макроса {Path(macro_file).name}")
            
            # Запуск в отдельном процессе
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            self.results[instance_id] = {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
            
            if result.returncode == 0:
                print(f"✅ Instance #{instance_id}: Макрос завершен успешно")
            else:
                print(f"❌ Instance #{instance_id}: Ошибка выполнения")
            
        except Exception as e:
            print(f"❌ Instance #{instance_id}: {e}")
            self.results[instance_id] = {'success': False, 'error': str(e)}
    
    def run_parallel(self, macro_file=None, url="https://tiktok.com"):
        """
        Запускает макрос параллельно в N экземплярах
        
        Args:
            macro_file: Путь к .atlas файлу (или None для разных макросов)
            url: URL для открытия (или None для разных URL)
        """
        print("="*60)
        print(f"🚀 ПАРАЛЛЕЛЬНЫЙ ЗАПУСК")
        print(f"📊 Экземпляров: {self.num_instances}")
        
        if self.custom_macros:
            print(f"📄 Макросы: Разные для каждого окна")
        else:
            print(f"📄 Макрос: {macro_file}")
        
        if self.custom_urls:
            print(f"🌐 URL: Разные для каждого окна")
        else:
            print(f"🌐 URL: {url}")
        
        if self.custom_profiles:
            print(f"👤 Профили: Разные аккаунты")
        
        print("="*60)
        
        # Создаем или подключаемся к экземплярам Chrome
        for i in range(self.num_instances):
            if self.use_existing:
                # Подключение к существующему Chrome
                driver = self.connect_to_existing_chrome(i)
            else:
                # Создание нового экземпляра
                profile = self.custom_profiles[i] if i < len(self.custom_profiles) else None
                driver = self.create_chrome_instance(i, profile_dir=profile)
            
            if driver:
                self.drivers.append((i, driver))
            time.sleep(1)  # Задержка между запусками
        
        print(f"\n✅ Запущено {len(self.drivers)} экземпляров Chrome\n")
        
        # Запускаем макросы в потоках
        for instance_id, driver in self.drivers:
            # Определяем макрос для этого экземпляра
            current_macro = self.custom_macros[instance_id] if instance_id < len(self.custom_macros) else macro_file
            
            # Определяем URL для этого экземпляра
            current_url = self.custom_urls[instance_id] if instance_id < len(self.custom_urls) else url
            
            thread = threading.Thread(
                target=self.run_macro_in_instance,
                args=(driver, instance_id, current_macro, current_url)
            )
            thread.start()
            self.threads.append(thread)
        
        # Ждем завершения всех потоков
        for thread in self.threads:
            thread.join()
        
        # Статистика
        self.print_results()
    
    def print_results(self):
        """Выводит результаты выполнения"""
        print("\n" + "="*60)
        print("📊 РЕЗУЛЬТАТЫ")
        print("="*60)
        
        success_count = sum(1 for r in self.results.values() if r.get('success'))
        
        for instance_id, result in self.results.items():
            status = "✅" if result.get('success') else "❌"
            print(f"{status} Instance #{instance_id}: {'Успешно' if result.get('success') else 'Ошибка'}")
        
        print("="*60)
        print(f"✅ Успешно: {success_count}/{len(self.results)}")
        print("="*60)
    
    def cleanup(self):
        """Закрывает все экземпляры Chrome"""
        print("\n🧹 Закрытие экземпляров...")
        for instance_id, driver in self.drivers:
            try:
                driver.quit()
                print(f"✅ Chrome #{instance_id} закрыт")
            except:
                pass


def main():
    parser = argparse.ArgumentParser(description='Параллельный запуск макросов')
    parser.add_argument('--instances', type=int, default=3, help='Количество параллельных экземпляров')
    parser.add_argument('--macro', type=str, help='Путь к .atlas файлу')
    parser.add_argument('--url', type=str, default='https://tiktok.com', help='URL для открытия')
    parser.add_argument('--use-existing', action='store_true', help='Подключиться к существующим Chrome (порты 9222+)')
    parser.add_argument('--profiles', type=str, nargs='+', help='Пути к профилям Chrome (разные аккаунты)')
    parser.add_argument('--macros', type=str, nargs='+', help='Разные макросы для каждого окна')
    parser.add_argument('--urls', type=str, nargs='+', help='Разные URL для каждого окна')
    
    args = parser.parse_args()
    
    runner = ParallelMacroRunner(num_instances=args.instances, use_existing=args.use_existing)
    
    # Кастомные профили
    if args.profiles:
        runner.custom_profiles = args.profiles
        print(f"👤 Используются кастомные профили: {len(args.profiles)}")
    
    # Разные макросы
    if args.macros:
        runner.custom_macros = args.macros
        print(f"📄 Используются разные макросы: {len(args.macros)}")
    
    # Разные URL
    if args.urls:
        runner.custom_urls = args.urls
        print(f"🌐 Используются разные URL: {len(args.urls)}")
    
    try:
        runner.run_parallel(args.macro, args.url)
    except KeyboardInterrupt:
        print("\n⏹️  Остановлено пользователем")
    finally:
        if not args.use_existing:
            # Не закрываем существующие Chrome
            runner.cleanup()


if __name__ == '__main__':
    main()
