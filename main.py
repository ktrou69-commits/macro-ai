#!/usr/bin/env python3
"""
main.py
MACRO AI MASTER - Главное приложение для управления макросами

Интерактивное меню для:
- Запуска утилит
- Выполнения готовых макросов
- Быстрых веб-поисков
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from config import MACROS_DIR, EXAMPLES_DIR, TEMPLATES_DIR

# Загрузка переменных окружения из .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Импорт AI генератора
try:
    from utils.ai_macro_generator import AIMacroGenerator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class MacroAIMaster:
    """Главное приложение MACRO AI"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.utils_dir = self.project_root / "utils"
        self.examples_dir = EXAMPLES_DIR
        self.macros_dir = MACROS_DIR
        
    def clear_screen(self):
        """Очистка экрана"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        """Печать заголовка"""
        self.clear_screen()
        print("=" * 80)
        print("🚀 MACRO AI MASTER".center(80))
        print("=" * 80)
        print()
        print("Автоматизация действий на macOS через компьютерное зрение и DSL".center(80))
        print()
        print("=" * 80)
        print()
    
    def print_menu(self, title: str, options: List[str], back: bool = True):
        """Печать меню"""
        print(f"\n📋 {title}")
        print("-" * 80)
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        if back:
            print(f"  0. ← Назад")
        print()
    
    def get_choice(self, max_choice: int, allow_zero: bool = True) -> int:
        """Получение выбора пользователя"""
        while True:
            try:
                choice = input("Выберите действие: ").strip()
                if not choice:
                    continue
                choice = int(choice)
                if allow_zero and choice == 0:
                    return 0
                if 1 <= choice <= max_choice:
                    return choice
                print(f"⚠️  Введите число от {'0' if allow_zero else '1'} до {max_choice}")
            except ValueError:
                print("⚠️  Введите число")
            except KeyboardInterrupt:
                print("\n\n👋 До свидания!")
                sys.exit(0)
    
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None):
        """Запуск команды"""
        try:
            print(f"\n🔄 Запуск: {' '.join(cmd)}")
            print("-" * 80)
            subprocess.run(cmd, cwd=cwd or self.project_root, check=True)
            print("-" * 80)
            input("\n✅ Нажмите Enter для продолжения...")
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Ошибка выполнения: {e}")
            input("\nНажмите Enter для продолжения...")
        except KeyboardInterrupt:
            print("\n\n⏹️  Остановлено пользователем")
            input("\nНажмите Enter для продолжения...")
    
    # ========== РАЗДЕЛ 1: ИНСТРУМЕНТЫ ==========
    
    def menu_utils(self):
        """Меню инструментов"""
        while True:
            self.print_header()
            
            utils = [
                ("DSL Reference Generator", "dsl_reference_generator.py", 
                 "Генерация справочника DSL команд и шаблонов"),
                ("DOM Selector Tool", "dom_selector_tool.py",
                 "🔥 AI-powered извлечение DOM селекторов из HTML"),
                ("Path Watcher", "path_watcher.py",
                 "Автоматическое обновление путей при перемещении файлов"),
                ("Coordinate Finder", "simple_coordinate_finder.py",
                 "Поиск координат элементов на экране"),
                ("Smart Capture", "smart_capture.py",
                 "Умный захват скриншотов для шаблонов"),
            ]
            
            options = [f"{name} - {desc}" for name, _, desc in utils]
            self.print_menu("ИНСТРУМЕНТЫ", options)
            
            choice = self.get_choice(len(options))
            if choice == 0:
                return
            
            name, script, desc = utils[choice - 1]
            self.run_util(name, script, desc)
    
    def run_util(self, name: str, script: str, desc: str):
        """Запуск утилиты"""
        self.print_header()
        print(f"🔧 {name}")
        print("-" * 80)
        print(f"📝 {desc}")
        print("-" * 80)
        print()
        
        script_path = self.utils_dir / script
        
        if not script_path.exists():
            print(f"❌ Файл не найден: {script_path}")
            input("\nНажмите Enter для продолжения...")
            return
        
        # Специальные опции для каждой утилиты
        if script == "dsl_reference_generator.py":
            self.run_dsl_generator()
        elif script == "dom_selector_tool.py":
            self.run_command(["python3", str(script_path)])
        elif script == "path_watcher.py":
            self.run_command(["python3", str(script_path)])
        elif script == "simple_coordinate_finder.py":
            self.run_command(["python3", str(script_path)])
        elif script == "smart_capture.py":
            self.run_command(["python3", str(script_path)])
    
    def run_dsl_generator(self):
        """Запуск DSL Reference Generator с опциями"""
        print("📂 Выберите папку с шаблонами:")
        print("  1. Все шаблоны (templates/)")
        print("  2. Chrome (templates/Chrome)")
        print("  3. TikTok (templates/Chrome/TikTok)")
        print("  4. Atlas (templates/Atlas)")
        print("  5. Свой путь")
        print()
        
        choice = self.get_choice(5, allow_zero=False)
        
        paths = {
            1: "templates",
            2: "templates/Chrome",
            3: "templates/Chrome/TikTok",
            4: "templates/Atlas",
        }
        
        if choice == 5:
            path = input("Введите путь: ").strip()
        else:
            path = paths[choice]
        
        script_path = self.utils_dir / "dsl_reference_generator.py"
        self.run_command(["python3", str(script_path), "--templates-path", path])
    
    # ========== РАЗДЕЛ 2: DSL СБОРНИК ==========
    
    def menu_dsl_collection(self):
        """Меню DSL сборника"""
        while True:
            self.print_header()
            
            # Сканируем .atlas файлы
            atlas_files = list(self.macros_dir.glob("*.atlas"))
            
            if not atlas_files:
                print("⚠️  .atlas файлы не найдены в папке macros/production/")
                input("\nНажмите Enter для продолжения...")
                return
            
            # Сортируем по имени
            atlas_files.sort()
            
            options = []
            for atlas_file in atlas_files:
                # Читаем первую строку для описания
                try:
                    with open(atlas_file, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('#'):
                            desc = first_line[1:].strip()
                        else:
                            desc = "Макрос последовательность"
                except:
                    desc = "Макрос последовательность"
                
                options.append(f"{atlas_file.stem} - {desc}")
            
            self.print_menu("DSL СБОРНИК - Готовые макросы", options)
            
            choice = self.get_choice(len(options))
            if choice == 0:
                return
            
            atlas_file = atlas_files[choice - 1]
            self.run_atlas_macro(atlas_file)
    
    def run_atlas_macro(self, atlas_file: Path):
        """Запуск .atlas макроса"""
        self.print_header()
        print(f"🎬 {atlas_file.stem}")
        print("-" * 80)
        
        # Показываем содержимое
        try:
            with open(atlas_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print("📄 Содержимое:")
            print("-" * 80)
            print(content)
            print("-" * 80)
        except Exception as e:
            print(f"⚠️  Не удалось прочитать файл: {e}")
        
        print()
        print("Запустить этот макрос? (y/n): ", end='')
        confirm = input().strip().lower()
        
        if confirm == 'y':
            sequence_name = atlas_file.stem
            self.run_command([
                "python3", "macro_sequence.py",
                "--config", str(atlas_file),
                "--run", sequence_name
            ])
    
    # ========== РАЗДЕЛ 3: БЫСТРЫЕ ВЕБ-ПОИСКИ ==========
    
    def menu_quick_search(self):
        """Меню быстрых веб-поисков"""
        while True:
            self.print_header()
            
            browsers = ["Chrome", "Safari", "Firefox"]
            
            self.print_menu("БЫСТРЫЕ ВЕБ-ПОИСКИ - Выберите браузер", browsers)
            
            choice = self.get_choice(len(browsers))
            if choice == 0:
                return
            
            browser = browsers[choice - 1]
            self.menu_platform(browser)
    
    def menu_platform(self, browser: str):
        """Меню выбора платформы"""
        while True:
            self.print_header()
            print(f"🌐 Браузер: {browser}")
            print()
            
            platforms = ["YouTube", "TikTok", "Google", "Twitter"]
            
            self.print_menu("Выберите платформу", platforms)
            
            choice = self.get_choice(len(platforms))
            if choice == 0:
                return
            
            platform = platforms[choice - 1]
            self.quick_search(browser, platform)
    
    def quick_search(self, browser: str, platform: str):
        """Быстрый поиск"""
        self.print_header()
        print(f"🔍 {browser} → {platform}")
        print("-" * 80)
        print()
        
        search_query = input("Введите поисковый запрос: ").strip()
        
        if not search_query:
            print("⚠️  Запрос не может быть пустым")
            input("\nНажмите Enter для продолжения...")
            return
        
        print()
        print(f"🔄 Запуск поиска: '{search_query}' в {platform} через {browser}")
        print()
        
        # Создаем временный .atlas файл
        temp_atlas = self.create_quick_search_atlas(browser, platform, search_query)
        
        if temp_atlas:
            self.run_command([
                "python3", "macro_sequence.py",
                "--config", str(temp_atlas),
                "--run", temp_atlas.stem
            ])
            
            # Удаляем временный файл
            try:
                temp_atlas.unlink()
            except:
                pass
    
    def create_quick_search_atlas(self, browser: str, platform: str, query: str) -> Optional[Path]:
        """Создание временного .atlas файла для быстрого поиска"""
        
        # Определяем шаблоны для браузера
        browser_templates = {
            "Chrome": {
                "app": "ChromeApp",
                "new_tab": "ChromeNewTab",
                "search_field": "ChromeSearchField",
            },
            "Safari": {
                "app": "SafariApp",
                "new_tab": "SafariNewTab",
                "search_field": "SafariSearchField",
            },
            "Firefox": {
                "app": "FirefoxApp",
                "new_tab": "FirefoxNewTab",
                "search_field": "FirefoxSearchField",
            }
        }
        
        # URL платформ
        platform_urls = {
            "YouTube": "youtube.com",
            "TikTok": "tiktok.com",
            "Google": "google.com",
            "Twitter": "twitter.com",
        }
        
        if browser not in browser_templates or platform not in platform_urls:
            print(f"⚠️  Неподдерживаемая комбинация: {browser} + {platform}")
            return None
        
        templates = browser_templates[browser]
        url = platform_urls[platform]
        
        # Создаем DSL
        dsl_content = f"""# Quick Search - {browser} → {platform}
# Автоматически сгенерированный макрос

# Запуск {browser}
open {templates['app']}
wait 3s

# Новая вкладка
click {templates['new_tab']}
wait 1s

# Переход на {platform}
click {templates['search_field']}
type "{url}"
press enter
wait 5s

# Поиск: {query}
click {templates['search_field']}
type "{query}"
press enter
wait 3s

# ✅ Готово
"""
        
        # Сохраняем во временный файл
        temp_file = self.project_root / f"_temp_quick_search_{browser}_{platform}.atlas"
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(dsl_content)
            return temp_file
        except Exception as e:
            print(f"❌ Ошибка создания временного файла: {e}")
            return None
    
    # ========== ГЛАВНОЕ МЕНЮ ==========
    
    # ========== РАЗДЕЛ 4: AI ГЕНЕРАТОР ==========
    
    def menu_ai_generator(self):
        """Меню AI генератора макросов"""
        if not AI_AVAILABLE:
            self.print_header()
            print("❌ AI генератор недоступен")
            print()
            print("Установите необходимые библиотеки:")
            print("  pip install openai anthropic google-genai")
            print()
            input("Нажмите Enter для продолжения...")
            return
        
        self.print_header()
        print("🤖 AI ГЕНЕРАТОР МАКРОСОВ")
        print("-" * 80)
        print()
        print("Опишите что должен делать макрос, и AI создаст его автоматически!")
        print()
        print("Примеры:")
        print("  • 'открыть YouTube и поставить лайк'")
        print("  • 'зайти на TikTok и пролистать 5 видео'")
        print("  • 'открыть Chrome, перейти на google.com и найти Python'")
        print()
        print("-" * 80)
        print()
        
        user_input = input("📝 Введите описание макроса (или 0 для отмены): ").strip()
        
        if not user_input or user_input == "0":
            return
        
        # Создаем генератор
        generator = AIMacroGenerator(self.project_root)
        
        # Генерируем и сохраняем
        filepath = generator.generate_and_save(user_input)
        
        if not filepath:
            input("\nНажмите Enter для продолжения...")
            return
        
        # Предлагаем запустить
        print()
        print("=" * 80)
        print(f"✅ Ваша новая последовательность создана: {filepath.stem}")
        print("=" * 80)
        print()
        print("Что дальше?")
        print("  1. Запустить эту последовательность")
        print("  2. Посмотреть все последовательности")
        print("  0. Вернуться в главное меню")
        print()
        
        choice = self.get_choice(2)
        
        if choice == 1:
            # Запускаем созданный макрос
            self.run_atlas_macro(filepath)
        elif choice == 2:
            # Показываем все макросы
            self.menu_dsl_collection()
    
    # ========== РАЗДЕЛ 5: АВТОМАТИЗАЦИЯ ПРОЦЕССОВ (AI) ==========
    
    def menu_automation(self):
        """Меню автоматизации процессов с AI"""
        while True:
            self.print_header()
            
            options = [
                "🏗️  Создание архитектуры шаблонов (AI)",
                "📝 Генерация DSL переменных (AI)",
                "🔮 Предложить оптимизацию (AI)",
            ]
            
            self.print_menu("АВТОМАТИЗАЦИЯ ПРОЦЕССОВ", options)
            
            choice = self.get_choice(len(options))
            
            if choice == 0:
                break
            elif choice == 1:
                self.automation_template_architecture()
            elif choice == 2:
                print("\n🚧 В разработке...")
                input("\nНажмите Enter для продолжения...")
            elif choice == 3:
                print("\n🚧 В разработке...")
                input("\nНажмите Enter для продолжения...")
    
    def automation_template_architecture(self):
        """AI-помощник для создания архитектуры шаблонов"""
        if not AI_AVAILABLE:
            self.print_header()
            print("❌ AI недоступен")
            print()
            print("Установите необходимые библиотеки:")
            print("  pip install openai anthropic google-genai")
            print()
            input("Нажмите Enter для продолжения...")
            return
        
        self.print_header()
        print("🏗️  СОЗДАНИЕ АРХИТЕКТУРЫ ШАБЛОНОВ")
        print("=" * 80)
        print()
        print("AI поможет создать структуру названий для фото-шаблонов интерфейса")
        print("на основе вашего описания действий.")
        print()
        print("Пример описания:")
        print("  'Я захожу в настройки, вижу кнопку Wi-Fi, затем нажимаю на сеть'")
        print("  'Открываю Instagram, кликаю на лайк, затем на комментарии'")
        print()
        print("=" * 80)
        print()
        
        user_input = input("📝 Опишите ваши действия (или 0 для отмены): ").strip()
        
        if not user_input or user_input == "0":
            return
        
        # Читаем текущую структуру
        structure_file = self.project_root / "templates" / "TEMPLATES_STRUCTURE.txt"
        current_structure = ""
        if structure_file.exists():
            with open(structure_file, 'r', encoding='utf-8') as f:
                current_structure = f.read()
        
        # Создаем промпт для AI
        from utils.ai_macro_generator import AIMacroGenerator
        generator = AIMacroGenerator(self.project_root)
        
        system_prompt = f"""Ты — эксперт по созданию архитектуры UI-шаблонов для автоматизации.

У нас есть текущая структура шаблонов:

{current_structure}

Твоя задача — создать НОВУЮ ВЕТКУ в этой структуре на основе описания пользователя.

ПРАВИЛА:
1. Используй формат как в примере выше (с отступами и комментариями)
2. Названия файлов: AppName-ElementName-btn.png
3. Комментарии должны быть понятными и описывать назначение элемента
4. Если это новое приложение — создай новую папку
5. Если это вкладка внутри приложения (например Chrome) — добавь подпапку
6. Используй пробелы для отступов (не символы дерева)

ФОРМАТ ОТВЕТА:
Выведи ТОЛЬКО новую ветку структуры, без объяснений.

Пример:
  Settings/                            # Настройки системы
    Settings-WiFi-btn.png              # Кнопка Wi-Fi
    Settings-Network-btn.png           # Кнопка "Сеть"
    Settings-NetworkName-btn.png       # Название сети

INPUT: {user_input}
"""
        
        print("\n🤖 Генерация архитектуры...")
        print()
        
        # Генерируем через Gemini (быстрее и дешевле)
        try:
            from google import genai
            
            gemini_key = os.getenv("GEMINI_API_KEY")
            if not gemini_key:
                print("❌ GEMINI_API_KEY не установлен")
                input("\nНажмите Enter для продолжения...")
                return
            
            # Создаем клиент с API ключом
            client = genai.Client(api_key=gemini_key)
            
            # Генерируем контент
            from utils.api_config import api_config
            response = client.models.generate_content(
                model=api_config.gemini_model,
                contents=system_prompt
            )
            result = response.text
            
            print("=" * 80)
            print("✅ НОВАЯ АРХИТЕКТУРА:")
            print("=" * 80)
            print()
            print(result)
            print()
            print("=" * 80)
            print()
            
            # Предлагаем добавить в файл
            add_choice = input("Добавить эту структуру в TEMPLATES_STRUCTURE.txt? (y/n): ").strip().lower()
            
            if add_choice == 'y':
                with open(structure_file, 'a', encoding='utf-8') as f:
                    f.write("\n")
                    f.write(result)
                    f.write("\n")
                
                print("\n✅ Структура добавлена!")
                print(f"📁 Файл: {structure_file}")
            
        except Exception as e:
            print(f"❌ Ошибка генерации: {e}")
        
        print()
        input("Нажмите Enter для продолжения...")
    
    # ========== РАЗДЕЛ 6: СИМУЛЯТОР МАКРОСОВ ==========
    
    def menu_simulator(self):
        """Меню симулятора макросов"""
        while True:
            self.print_header()
            
            options = [
                "🎮 Симулировать макрос из файла",
                "📊 Сравнить несколько макросов",
                "📈 Показать статистику всех макросов",
            ]
            
            self.print_menu("СИМУЛЯТОР МАКРОСОВ", options)
            
            choice = self.get_choice(len(options))
            
            if choice == 0:
                break
            elif choice == 1:
                self.simulate_macro()
            elif choice == 2:
                self.compare_macros()
            elif choice == 3:
                self.show_all_macro_stats()
    
    def simulate_macro(self):
        """Симуляция одного макроса"""
        self.print_header()
        
        # Получаем список макросов
        macros = sorted(self.macros_dir.glob("*.atlas"))
        
        if not macros:
            print("❌ Нет доступных макросов в macros/production/")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("\n📋 Выберите макрос для симуляции:")
        print("-" * 80)
        for i, macro in enumerate(macros, 1):
            print(f"  {i}. {macro.stem}")
        print()
        
        choice = self.get_choice(len(macros), allow_zero=False)
        selected_macro = macros[choice - 1]
        
        print(f"\n🎮 Симуляция: {selected_macro.name}")
        print("-" * 80)
        
        # Запускаем симуляцию
        try:
            from simulator import simulate_from_file
            report = simulate_from_file(str(selected_macro))
            report.print_report()
        except Exception as e:
            print(f"❌ Ошибка симуляции: {e}")
            import traceback
            traceback.print_exc()
        
        input("\nНажмите Enter для продолжения...")
    
    def compare_macros(self):
        """Сравнение нескольких макросов"""
        self.print_header()
        
        macros = sorted(self.macros_dir.glob("*.atlas"))
        
        if len(macros) < 2:
            print("❌ Недостаточно макросов для сравнения (нужно минимум 2)")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("\n📊 Сравнение макросов")
        print("-" * 80)
        print("Выберите макросы для сравнения (по одному)")
        print()
        
        selected = []
        
        for i in range(2):
            print(f"\nМакрос #{i+1}:")
            for j, macro in enumerate(macros, 1):
                print(f"  {j}. {macro.stem}")
            
            choice = self.get_choice(len(macros), allow_zero=False)
            selected.append(macros[choice - 1])
        
        print(f"\n📊 Сравнение:")
        print("=" * 80)
        
        try:
            from simulator import simulate_from_file
            
            reports = []
            for macro in selected:
                print(f"\n🎮 {macro.name}")
                report = simulate_from_file(str(macro))
                reports.append((macro.name, report))
                
                print(f"   Шагов: {report.total_steps}")
                print(f"   Вероятность: {report.overall_probability*100:.1f}%")
                print(f"   Время: {report.estimated_total_time:.1f}s")
                print(f"   Рисков: {report.total_risks}")
            
            # Определяем лучший
            print("\n" + "=" * 80)
            best = max(reports, key=lambda x: x[1].overall_probability)
            print(f"🏆 Лучший макрос: {best[0]}")
            print(f"   Вероятность успеха: {best[1].overall_probability*100:.1f}%")
            
        except Exception as e:
            print(f"❌ Ошибка сравнения: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    def show_all_macro_stats(self):
        """Показать статистику всех макросов"""
        self.print_header()
        
        print("\n📈 СТАТИСТИКА ВСЕХ МАКРОСОВ")
        print("=" * 80)
        
        macros = sorted(self.macros_dir.glob("*.atlas"))
        
        if not macros:
            print("❌ Нет доступных макросов")
            input("\nНажмите Enter для продолжения...")
            return
        
        try:
            from simulator import simulate_from_file
            
            all_reports = []
            
            for macro in macros:
                try:
                    report = simulate_from_file(str(macro))
                    all_reports.append((macro.name, report))
                except Exception as e:
                    print(f"⚠️  Ошибка симуляции {macro.name}: {e}")
            
            # Сортируем по вероятности
            all_reports.sort(key=lambda x: x[1].overall_probability, reverse=True)
            
            print(f"\n📋 Всего макросов: {len(all_reports)}\n")
            
            for i, (name, report) in enumerate(all_reports, 1):
                # Иконка статуса
                if report.overall_probability >= 0.9:
                    status = "✅"
                elif report.overall_probability >= 0.7:
                    status = "⚠️ "
                else:
                    status = "❌"
                
                print(f"{status} {i}. {name}")
                print(f"   Вероятность: {report.overall_probability*100:.1f}%")
                print(f"   Время: {report.estimated_total_time:.1f}s")
                print(f"   Шагов: {report.total_steps}")
                print(f"   Рисков: {report.total_risks}")
                print()
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")
    
    # ========== РАЗДЕЛ 6: ПАРАЛЛЕЛЬНОЕ ВЫПОЛНЕНИЕ ==========
    
    def menu_parallel_execution(self):
        """Меню параллельного выполнения"""
        while True:
            self.print_header()
            
            options = [
                "🚀 Запустить Chrome с debug портом (1 окно)",
                "🚀🚀 Запустить несколько Chrome (3-10 окон)",
                "🔗 Подключиться к существующим Chrome",
                "⚡ Параллельный запуск (3 окна)",
                "⚡⚡ Параллельный запуск (5 окон)",
                "⚡⚡⚡ Параллельный запуск (10 окон)",
                "🎯 Кастомный запуск (выбрать макрос и количество)",
                "👥 Продвинутый режим (разные аккаунты/макросы/URL)",
                "📚 Список доступных макросов",
            ]
            
            self.print_menu("ПАРАЛЛЕЛЬНОЕ ВЫПОЛНЕНИЕ", options)
            
            choice = self.get_choice(len(options))
            
            if choice == 0:
                break
            elif choice == 1:
                # Запуск Chrome с debug портом (1 окно)
                self.run_command(["./utils/start_chrome_debug.sh"])
            elif choice == 2:
                # Запуск нескольких Chrome
                self.start_multiple_chrome()
            elif choice == 3:
                # Подключение к существующим Chrome
                self.connect_to_existing_chrome()
            elif choice == 4:
                # 3 окна
                self.run_parallel_macro(3)
            elif choice == 5:
                # 5 окон
                self.run_parallel_macro(5)
            elif choice == 6:
                # 10 окон
                self.run_parallel_macro(10)
            elif choice == 7:
                # Кастомный запуск
                self.run_parallel_custom()
            elif choice == 8:
                # Продвинутый режим
                self.run_advanced_parallel()
            elif choice == 9:
                # Список макросов
                self.show_available_macros()
    
    def run_parallel_macro(self, instances: int):
        """Запуск параллельного выполнения с выбором макроса"""
        self.print_header()
        
        # Получаем список макросов
        macros = sorted(self.macros_dir.glob("*.atlas"))
        
        if not macros:
            print("❌ Нет доступных макросов в macros/production/")
            input("\nНажмите Enter для продолжения...")
            return
        
        print(f"\n📋 Выберите макрос для запуска в {instances} окнах:")
        print("-" * 80)
        for i, macro in enumerate(macros, 1):
            print(f"  {i}. {macro.stem}")
        print()
        
        choice = self.get_choice(len(macros), allow_zero=False)
        selected_macro = macros[choice - 1]
        
        # Подтверждение
        print(f"\n⚠️  Будет запущено {instances} окон Chrome")
        print(f"📄 Макрос: {selected_macro.name}")
        confirm = input("\nПродолжить? (y/n): ").strip().lower()
        
        if confirm == 'y':
            self.run_command([
                "python3", "parallel_runner.py",
                "--instances", str(instances),
                "--macro", str(selected_macro)
            ])
    
    def run_parallel_custom(self):
        """Кастомный параллельный запуск"""
        self.print_header()
        
        # Получаем список макросов
        macros = sorted(self.macros_dir.glob("*.atlas"))
        
        if not macros:
            print("❌ Нет доступных макросов в macros/production/")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("\n📋 Выберите макрос:")
        print("-" * 80)
        for i, macro in enumerate(macros, 1):
            print(f"  {i}. {macro.stem}")
        print()
        
        macro_choice = self.get_choice(len(macros), allow_zero=False)
        selected_macro = macros[macro_choice - 1]
        
        # Количество экземпляров
        print(f"\n📊 Сколько окон запустить? (1-15)")
        print("💡 Рекомендуется:")
        print("   8GB RAM  → 3-4 окна")
        print("   16GB RAM → 5-8 окон")
        print("   32GB RAM → 10-15 окон")
        print()
        
        while True:
            try:
                instances = int(input("Количество окон: ").strip())
                if 1 <= instances <= 15:
                    break
                print("⚠️  Введите число от 1 до 15")
            except ValueError:
                print("⚠️  Введите число")
        
        # URL (опционально)
        print(f"\n🌐 URL для открытия (Enter для https://tiktok.com):")
        url = input("URL: ").strip() or "https://tiktok.com"
        
        # Подтверждение
        print(f"\n⚠️  Будет запущено {instances} окон Chrome")
        print(f"📄 Макрос: {selected_macro.name}")
        print(f"🌐 URL: {url}")
        confirm = input("\nПродолжить? (y/n): ").strip().lower()
        
        if confirm == 'y':
            self.run_command([
                "python3", "parallel_runner.py",
                "--instances", str(instances),
                "--macro", str(selected_macro),
                "--url", url
            ])
    
    def start_multiple_chrome(self):
        """Запуск нескольких Chrome окон"""
        self.print_header()
        
        print("\n📊 Сколько окон Chrome запустить? (2-10)")
        print("💡 Каждое окно = отдельный профиль для разных аккаунтов")
        print()
        
        while True:
            try:
                instances = int(input("Количество окон: ").strip())
                if 2 <= instances <= 10:
                    break
                print("⚠️  Введите число от 2 до 10")
            except ValueError:
                print("⚠️  Введите число")
        
        self.run_command(["./utils/start_multiple_chrome.sh", str(instances)])
    
    def connect_to_existing_chrome(self):
        """Подключение к существующим Chrome и запуск макросов"""
        self.print_header()
        
        # Получаем список макросов
        macros = sorted(self.macros_dir.glob("*.atlas"))
        
        if not macros:
            print("❌ Нет доступных макросов в macros/production/")
            input("\nНажмите Enter для продолжения...")
            return
        
        print("\n📋 Выберите макрос:")
        print("-" * 80)
        for i, macro in enumerate(macros, 1):
            print(f"  {i}. {macro.stem}")
        print()
        
        choice = self.get_choice(len(macros), allow_zero=False)
        selected_macro = macros[choice - 1]
        
        print(f"\n📊 Сколько окон Chrome уже запущено? (1-10)")
        while True:
            try:
                instances = int(input("Количество окон: ").strip())
                if 1 <= instances <= 10:
                    break
                print("⚠️  Введите число от 1 до 10")
            except ValueError:
                print("⚠️  Введите число")
        
        # Подтверждение
        print(f"\n⚠️  Подключение к {instances} существующим Chrome")
        print(f"📄 Макрос: {selected_macro.name}")
        print(f"💡 Убедись что Chrome запущены с портами 9222-{9222+instances-1}")
        confirm = input("\nПродолжить? (y/n): ").strip().lower()
        
        if confirm == 'y':
            self.run_command([
                "python3", "parallel_runner.py",
                "--use-existing",
                "--instances", str(instances),
                "--macro", str(selected_macro)
            ])
    
    def run_advanced_parallel(self):
        """Продвинутый режим: разные аккаунты/макросы/URL"""
        self.print_header()
        
        print("\n👥 ПРОДВИНУТЫЙ РЕЖИМ")
        print("-" * 80)
        print("Выберите сценарий:")
        print()
        print("  1. Разные аккаунты (разные профили Chrome)")
        print("  2. Разные макросы (каждое окно свой макрос)")
        print("  3. Разные URL (каждое окно свой URL)")
        print("  4. Комбинированный (всё вместе)")
        print()
        
        scenario = self.get_choice(4, allow_zero=False)
        
        if scenario == 1:
            self.run_different_accounts()
        elif scenario == 2:
            self.run_different_macros()
        elif scenario == 3:
            self.run_different_urls()
        elif scenario == 4:
            self.run_combined_scenario()
    
    def run_different_accounts(self):
        """Запуск с разными аккаунтами"""
        self.print_header()
        
        print("\n👤 РАЗНЫЕ АККАУНТЫ")
        print("-" * 80)
        print("Введите пути к профилям Chrome (по одному на строку)")
        print("Пример: /Users/kostya/chrome-account1")
        print("Пустая строка для завершения")
        print()
        
        profiles = []
        i = 1
        while True:
            profile = input(f"Профиль #{i}: ").strip()
            if not profile:
                break
            profiles.append(profile)
            i += 1
        
        if not profiles:
            print("❌ Не указано ни одного профиля")
            input("\nНажмите Enter для продолжения...")
            return
        
        # Выбор макроса
        macros = sorted(self.macros_dir.glob("*.atlas"))
        print(f"\n📋 Выберите макрос:")
        for i, macro in enumerate(macros, 1):
            print(f"  {i}. {macro.stem}")
        
        choice = self.get_choice(len(macros), allow_zero=False)
        selected_macro = macros[choice - 1]
        
        # Запуск
        cmd = [
            "python3", "parallel_runner.py",
            "--instances", str(len(profiles)),
            "--macro", str(selected_macro),
            "--profiles"
        ] + profiles
        
        self.run_command(cmd)
    
    def run_different_macros(self):
        """Запуск разных макросов в разных окнах"""
        self.print_header()
        
        macros = sorted(self.macros_dir.glob("*.atlas"))
        
        print("\n📄 РАЗНЫЕ МАКРОСЫ")
        print("-" * 80)
        print("Выберите макросы для каждого окна")
        print()
        
        selected_macros = []
        i = 1
        while True:
            print(f"\nМакрос для окна #{i}:")
            for j, macro in enumerate(macros, 1):
                print(f"  {j}. {macro.stem}")
            print(f"  0. Завершить выбор")
            
            choice = self.get_choice(len(macros))
            if choice == 0:
                break
            
            selected_macros.append(str(macros[choice - 1]))
            i += 1
        
        if not selected_macros:
            print("❌ Не выбрано ни одного макроса")
            input("\nНажмите Enter для продолжения...")
            return
        
        # Запуск
        cmd = [
            "python3", "parallel_runner.py",
            "--instances", str(len(selected_macros)),
            "--macros"
        ] + selected_macros
        
        self.run_command(cmd)
    
    def run_different_urls(self):
        """Запуск с разными URL"""
        self.print_header()
        
        print("\n🌐 РАЗНЫЕ URL")
        print("-" * 80)
        print("Введите URL для каждого окна (по одному на строку)")
        print("Пример: https://tiktok.com/@user1")
        print("Пустая строка для завершения")
        print()
        
        urls = []
        i = 1
        while True:
            url = input(f"URL #{i}: ").strip()
            if not url:
                break
            urls.append(url)
            i += 1
        
        if not urls:
            print("❌ Не указано ни одного URL")
            input("\nНажмите Enter для продолжения...")
            return
        
        # Выбор макроса
        macros = sorted(self.macros_dir.glob("*.atlas"))
        print(f"\n📋 Выберите макрос:")
        for i, macro in enumerate(macros, 1):
            print(f"  {i}. {macro.stem}")
        
        choice = self.get_choice(len(macros), allow_zero=False)
        selected_macro = macros[choice - 1]
        
        # Запуск
        cmd = [
            "python3", "parallel_runner.py",
            "--instances", str(len(urls)),
            "--macro", str(selected_macro),
            "--urls"
        ] + urls
        
        self.run_command(cmd)
    
    def run_combined_scenario(self):
        """Комбинированный сценарий"""
        print("\n🎯 КОМБИНИРОВАННЫЙ РЕЖИМ")
        print("Эта функция в разработке...")
        input("\nНажмите Enter для продолжения...")
    
    def show_available_macros(self):
        """Показать список доступных макросов"""
        self.print_header()
        
        macros = sorted(self.macros_dir.glob("*.atlas"))
        
        print("\n📚 Доступные макросы:")
        print("-" * 80)
        
        if not macros:
            print("❌ Нет макросов в macros/production/")
        else:
            for i, macro in enumerate(macros, 1):
                # Читаем первую строку для описания
                try:
                    with open(macro, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('#'):
                            description = first_line.lstrip('#').strip()
                        else:
                            description = "Нет описания"
                except:
                    description = "Нет описания"
                
                print(f"  {i}. {macro.stem}")
                print(f"     {description}")
                print()
        
        input("\nНажмите Enter для продолжения...")
    
    # ========== РАЗДЕЛ 8: ОБНОВЛЕНИЕ ПРОМПТОВ ==========
    
    def menu_prompt_updater(self):
        """Меню обновления промптов"""
        while True:
            self.print_header()
            
            options = [
                "🔄 Обновить все промпты (сканирует templates/)",
                "➕ Добавить новую платформу (AI создаст структуру)",
                "📊 Показать текущую структуру шаблонов",
                "📚 Открыть документацию",
            ]
            
            self.print_menu("ОБНОВЛЕНИЕ ПРОМПТОВ", options)
            
            choice = self.get_choice(len(options))
            if choice == 0:
                return
            
            if choice == 1:
                self.update_all_prompts()
            elif choice == 2:
                self.add_new_platform()
            elif choice == 3:
                self.show_templates_structure()
            elif choice == 4:
                self.open_prompt_docs()
    
    def update_all_prompts(self):
        """Обновить все промпты"""
        self.print_header()
        print("🔄 ОБНОВЛЕНИЕ ПРОМПТОВ")
        print("-" * 80)
        print()
        print("Эта функция:")
        print("  1. Сканирует templates/ и находит все PNG файлы")
        print("  2. AI обновляет TEMPLATES_STRUCTURE.txt")
        print("  3. AI обновляет BEST_PRACTICES.txt")
        print("  4. Регенерирует DSL_REFERENCE.txt")
        print()
        print("⚠️  Это займёт 10-20 секунд")
        print()
        
        confirm = input("Продолжить? (y/n): ").strip().lower()
        if confirm != 'y':
            return
        
        script_path = self.utils_dir / "prompt_updater.py"
        self.run_command(["python3", str(script_path), "--update"])
    
    def add_new_platform(self):
        """Добавить новую платформу"""
        self.print_header()
        print("➕ ДОБАВЛЕНИЕ НОВОЙ ПЛАТФОРМЫ")
        print("-" * 80)
        print()
        print("AI создаст структуру названий для фото-шаблонов")
        print("на основе вашего описания действий.")
        print()
        print("Примеры:")
        print("  • Instagram: 'открываю Instagram, кликаю лайк, пишу комментарий'")
        print("  • Twitter: 'открываю Twitter, пишу твит, ставлю лайк, делаю ретвит'")
        print("  • LinkedIn: 'открываю LinkedIn, ищу вакансии, откликаюсь'")
        print()
        print("-" * 80)
        print()
        
        platform = input("📝 Название платформы (например: Instagram): ").strip()
        if not platform:
            print("❌ Название не может быть пустым")
            input("\nНажмите Enter для продолжения...")
            return
        
        print()
        description = input("📝 Описание действий: ").strip()
        if not description:
            print("❌ Описание не может быть пустым")
            input("\nНажмите Enter для продолжения...")
            return
        
        script_path = self.utils_dir / "prompt_updater.py"
        self.run_command(["python3", str(script_path), "--add-platform", platform, description])
    
    def show_templates_structure(self):
        """Показать структуру шаблонов"""
        self.print_header()
        print("📊 СТРУКТУРА ШАБЛОНОВ")
        print("-" * 80)
        print()
        
        # Сканируем templates/
        templates_dir = self.project_root / "templates"
        structure = {}
        
        for png_file in sorted(templates_dir.rglob("*.png")):
            rel_path = png_file.relative_to(templates_dir)
            folder = str(rel_path.parent)
            
            if folder not in structure:
                structure[folder] = []
            
            structure[folder].append(png_file.name)
        
        total_files = sum(len(files) for files in structure.values())
        print(f"📂 Найдено: {len(structure)} папок, {total_files} файлов")
        print()
        
        for folder, files in sorted(structure.items()):
            print(f"📁 {folder}/ ({len(files)} файлов)")
            for filename in sorted(files):
                short_name = filename.replace('-btn.png', '').replace('.png', '')
                print(f"   • {short_name}")
            print()
        
        input("\nНажмите Enter для продолжения...")
    
    def open_prompt_docs(self):
        """Открыть документацию"""
        self.print_header()
        print("📚 ДОКУМЕНТАЦИЯ")
        print("-" * 80)
        print()
        print("Доступные документы:")
        print("  1. docs/PROMPT_UPDATER_GUIDE.md - Подробное руководство")
        print("  2. docs/AI_OPTIMIZATION_SUMMARY.md - Оптимизация AI")
        print("  3. docs/AI_PROMPT_OPTIMIZATION.md - Детальное объяснение")
        print()
        print("Открыть в браузере? (y/n): ", end='')
        
        confirm = input().strip().lower()
        if confirm == 'y':
            import webbrowser
            doc_path = self.project_root / "docs" / "PROMPT_UPDATER_GUIDE.md"
            webbrowser.open(f"file://{doc_path}")
            print("✅ Открыто в браузере")
        
        input("\nНажмите Enter для продолжения...")
    
    # ========== ГЛАВНОЕ МЕНЮ ==========
    
    def main_menu(self):
        """Главное меню"""
        while True:
            self.print_header()
            
            options = [
                "🔧 Инструменты (Utils)",
                "📚 DSL Сборник (Готовые макросы)",
                "🚀 Параллельное выполнение (Multi-Chrome)",
                "🎮 Симулятор макросов (Dry-run)",
                "🔍 Быстрые веб-поиски",
                "🤖 Генерация последовательности (AI)",
                "💡 Автоматизация процессов (AI)",
                "🔄 Обновление промптов (AI)",
                "❌ Выход",
            ]
            
            self.print_menu("ГЛАВНОЕ МЕНЮ", options, back=False)
            
            choice = self.get_choice(len(options), allow_zero=False)
            
            if choice == 1:
                self.menu_utils()
            elif choice == 2:
                self.menu_dsl_collection()
            elif choice == 3:
                self.menu_parallel_execution()
            elif choice == 4:
                self.menu_simulator()
            elif choice == 5:
                self.menu_quick_search()
            elif choice == 6:
                self.menu_ai_generator()
            elif choice == 7:
                self.menu_automation()
            elif choice == 8:
                self.menu_prompt_updater()
            elif choice == 9:
                self.print_header()
                print("👋 До свидания!".center(80))
                print()
                sys.exit(0)
    
    def run(self):
        """Запуск приложения"""
        try:
            self.main_menu()
        except KeyboardInterrupt:
            print("\n\n👋 До свидания!")
            sys.exit(0)


def main():
    """Точка входа"""
    app = MacroAIMaster()
    app.run()


if __name__ == "__main__":
    main()
