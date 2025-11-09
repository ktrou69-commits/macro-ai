#!/usr/bin/env python3
"""
prompt_updater.py
Автоматическое обновление структуры промптов для AI генератора

Использует AI для:
1. Сканирования новых шаблонов в templates/
2. Обновления TEMPLATES_STRUCTURE.txt
3. Регенерации DSL_REFERENCE.txt
4. Обновления BEST_PRACTICES.txt
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional
import subprocess


class PromptUpdater:
    """Автоматическое обновление промптов"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.templates_dir = project_root / "templates"
        self.dsl_ref_dir = project_root / "dsl_references"
        
        # Файлы для обновления
        self.structure_file = self.templates_dir / "TEMPLATES_STRUCTURE.txt"
        self.best_practices_file = self.templates_dir / "BEST_PRACTICES.txt"
        
        # Загружаем .env
        self._load_env()
        self.gemini_key = os.getenv("GEMINI_API_KEY")
    
    def _load_env(self):
        """Загружает переменные из .env файла"""
        env_file = self.project_root / ".env"
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        if key and value and not os.getenv(key):
                            os.environ[key] = value
    
    def scan_templates(self) -> Dict[str, List[str]]:
        """
        Сканирует папку templates/ и находит все PNG файлы
        
        Returns:
            {
                'Chrome/ChromeBasicGuiButtons': ['ChromeApp-btn.png', ...],
                'Chrome/TikTok': ['Chrome-TikTok-Like-btn.png', ...],
                ...
            }
        """
        structure = {}
        
        for png_file in sorted(self.templates_dir.rglob("*.png")):
            # Получаем относительный путь от templates/
            rel_path = png_file.relative_to(self.templates_dir)
            
            # Папка (например: Chrome/TikTok)
            folder = str(rel_path.parent)
            
            # Имя файла
            filename = png_file.name
            
            if folder not in structure:
                structure[folder] = []
            
            structure[folder].append(filename)
        
        return structure
    
    def generate_structure_description(self, structure: Dict[str, List[str]]) -> str:
        """
        Генерирует описание структуры для AI
        
        Args:
            structure: Результат scan_templates()
        
        Returns:
            Текстовое описание структуры
        """
        lines = []
        lines.append("📂 ТЕКУЩАЯ СТРУКТУРА ШАБЛОНОВ:")
        lines.append("")
        
        for folder, files in sorted(structure.items()):
            lines.append(f"📁 {folder}/ ({len(files)} файлов)")
            for filename in sorted(files):
                # Убираем -btn.png и показываем короткое имя
                short_name = filename.replace('-btn.png', '').replace('.png', '')
                lines.append(f"   • {short_name} ({filename})")
            lines.append("")
        
        return "\n".join(lines)
    
    def ask_ai_to_update_structure(self, current_structure: str) -> Optional[str]:
        """
        Просит AI обновить TEMPLATES_STRUCTURE.txt на основе текущих файлов
        
        Args:
            current_structure: Описание текущей структуры
        
        Returns:
            Новое содержимое для TEMPLATES_STRUCTURE.txt
        """
        try:
            from google import genai
            
            if not self.gemini_key:
                print("❌ GEMINI_API_KEY не установлен")
                return None
            
            client = genai.Client(api_key=self.gemini_key)
            
            prompt = f"""Ты — эксперт по документированию структуры шаблонов для автоматизации.

Твоя задача: создать красивый и понятный файл TEMPLATES_STRUCTURE.txt на основе текущих файлов.

{current_structure}

ТРЕБОВАНИЯ:

1. Формат файла:
================================================================================
ПОЛНАЯ СТРУКТУРА ШАБЛОНОВ - Описание всех кнопок и элементов
================================================================================

📂 templates/
│
├── Chrome/                              # Браузер Google Chrome
│   │
│   ├── ChromeBasicGuiButtons/           # Базовые кнопки Chrome
│   │   ├── ChromeApp-btn.png            # Иконка запуска Chrome
│   │   ├── ChromeNewTab-btn.png         # Кнопка "плюс" — открыть новую вкладку
│   │   └── ...
│   │
│   ├── TikTok/                          # Вкладка TikTok
│   │   ├── Chrome-TikTok-Like-btn.png   # Кнопка лайка видео
│   │   └── ...
│   │
│   └── YouTube/                         # Вкладка YouTube
│       └── ...

2. Краткие имена для DSL:
================================================================================
КРАТКИЕ ИМЕНА ШАБЛОНОВ (для использования в DSL)
================================================================================

Chrome - Базовые:
  • ChromeApp                - Запуск Chrome
  • ChromeNewTab             - Новая вкладка
  ...

3. Типичные сценарии:
================================================================================
ТИПИЧНЫЕ СЦЕНАРИИ ИСПОЛЬЗОВАНИЯ
================================================================================

1. Открыть Chrome и перейти на сайт:
   open ChromeApp
   wait 2s
   click ChromeSearchField
   ...

ВАЖНО:
- Добавь понятные комментарии для каждого файла
- Группируй по платформам (Chrome, TikTok, YouTube, ...)
- Используй эмодзи для красоты
- Добавь примеры использования

Верни ТОЛЬКО содержимое файла, без дополнительных объяснений!
"""
            
            print("🤖 AI обновляет структуру шаблонов...")
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            
            return response.text
            
        except ImportError:
            print("❌ Установите: pip install google-genai")
            return None
        except Exception as e:
            print(f"❌ Ошибка AI: {e}")
            return None
    
    def ask_ai_to_update_best_practices(self, structure: str) -> Optional[str]:
        """
        Просит AI обновить BEST_PRACTICES.txt
        
        Args:
            structure: Описание структуры шаблонов
        
        Returns:
            Новое содержимое для BEST_PRACTICES.txt
        """
        try:
            from google import genai
            
            if not self.gemini_key:
                return None
            
            client = genai.Client(api_key=self.gemini_key)
            
            # Читаем текущие best practices как референс
            current_practices = ""
            if self.best_practices_file.exists():
                with open(self.best_practices_file, 'r', encoding='utf-8') as f:
                    current_practices = f.read()
            
            prompt = f"""Ты — эксперт по созданию best practices для автоматизации.

Обнови файл BEST_PRACTICES.txt на основе новой структуры шаблонов.

ТЕКУЩАЯ СТРУКТУРА:
{structure}

ТЕКУЩИЕ BEST PRACTICES (для референса):
{current_practices[:2000]}  # Первые 2000 символов

ТРЕБОВАНИЯ:

1. Сохрани все важные правила из текущих practices
2. Добавь новые правила для новых платформ/кнопок
3. Формат:
   ✅ ПРАВИЛЬНО: <пример>
   ❌ НЕПРАВИЛЬНО: <пример>
   ПОЧЕМУ: <объяснение>

4. Обязательные секции:
   - CHROME - Базовые операции
   - TIKTOK - Работа с видео
   - YOUTUBE - Поиск и просмотр
   - ОБЩИЕ ПРАВИЛА - Ожидания
   - ОБРАБОТКА ОШИБОК - Try/Catch

5. Используй эмодзи и форматирование

Верни ТОЛЬКО содержимое файла!
"""
            
            print("🤖 AI обновляет best practices...")
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            
            return response.text
            
        except Exception as e:
            print(f"❌ Ошибка AI: {e}")
            return None
    
    def regenerate_dsl_reference(self) -> bool:
        """
        Регенерирует DSL_REFERENCE.txt используя существующий генератор
        
        Returns:
            True если успешно
        """
        try:
            print("🔄 Регенерация DSL справочника...")
            
            generator_path = self.project_root / "utils" / "dsl_reference_generator.py"
            
            if not generator_path.exists():
                print("⚠️  dsl_reference_generator.py не найден")
                return False
            
            result = subprocess.run(
                ["python3", str(generator_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ DSL справочник обновлён")
                return True
            else:
                print(f"❌ Ошибка: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка регенерации: {e}")
            return False
    
    def update_all(self, auto_confirm: bool = False) -> bool:
        """
        Обновляет все файлы промптов
        
        Args:
            auto_confirm: Автоматически подтверждать изменения
        
        Returns:
            True если успешно
        """
        print()
        print("=" * 80)
        print("🔄 АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ ПРОМПТОВ")
        print("=" * 80)
        print()
        
        # 1. Сканируем шаблоны
        print("📂 Сканирование templates/...")
        structure = self.scan_templates()
        
        total_files = sum(len(files) for files in structure.values())
        print(f"✅ Найдено: {len(structure)} папок, {total_files} файлов")
        print()
        
        # 2. Генерируем описание
        structure_desc = self.generate_structure_description(structure)
        print(structure_desc)
        print()
        
        # 3. Спрашиваем подтверждение
        if not auto_confirm:
            response = input("🤔 Обновить промпты на основе этой структуры? (y/n): ")
            if response.lower() != 'y':
                print("❌ Отменено")
                return False
        
        print()
        
        # 4. Обновляем TEMPLATES_STRUCTURE.txt
        print("📝 Обновление TEMPLATES_STRUCTURE.txt...")
        new_structure = self.ask_ai_to_update_structure(structure_desc)
        
        if new_structure:
            # Убираем маркеры кодовых блоков если есть
            new_structure = re.sub(r'^```.*\n', '', new_structure, flags=re.MULTILINE)
            new_structure = re.sub(r'\n```$', '', new_structure)
            
            with open(self.structure_file, 'w', encoding='utf-8') as f:
                f.write(new_structure)
            
            print(f"✅ Сохранено: {self.structure_file}")
        else:
            print("⚠️  Пропущено (ошибка AI)")
        
        print()
        
        # 5. Обновляем BEST_PRACTICES.txt
        print("📝 Обновление BEST_PRACTICES.txt...")
        new_practices = self.ask_ai_to_update_best_practices(structure_desc)
        
        if new_practices:
            new_practices = re.sub(r'^```.*\n', '', new_practices, flags=re.MULTILINE)
            new_practices = re.sub(r'\n```$', '', new_practices)
            
            with open(self.best_practices_file, 'w', encoding='utf-8') as f:
                f.write(new_practices)
            
            print(f"✅ Сохранено: {self.best_practices_file}")
        else:
            print("⚠️  Пропущено (ошибка AI)")
        
        print()
        
        # 6. Регенерируем DSL_REFERENCE.txt
        self.regenerate_dsl_reference()
        
        print()
        print("=" * 80)
        print("✅ ОБНОВЛЕНИЕ ЗАВЕРШЕНО!")
        print("=" * 80)
        print()
        print("📁 Обновлённые файлы:")
        print(f"   • {self.structure_file}")
        print(f"   • {self.best_practices_file}")
        print(f"   • {self.dsl_ref_dir}/DSL_REFERENCE.txt")
        print()
        print("💡 Теперь AI генератор будет использовать новую структуру!")
        print()
        
        return True
    
    def add_new_platform(self, platform_name: str, description: str) -> bool:
        """
        Добавляет новую платформу с помощью AI
        
        Args:
            platform_name: Название платформы (например: "Instagram")
            description: Описание действий (например: "открываю Instagram, кликаю лайк")
        
        Returns:
            True если успешно
        """
        try:
            from google import genai
            
            if not self.gemini_key:
                print("❌ GEMINI_API_KEY не установлен")
                return False
            
            client = genai.Client(api_key=self.gemini_key)
            
            prompt = f"""Ты — эксперт по созданию структуры шаблонов для автоматизации.

ЗАДАЧА: Создать структуру названий для фото-шаблонов платформы {platform_name}

ОПИСАНИЕ ДЕЙСТВИЙ:
{description}

ТРЕБОВАНИЯ:

1. Проанализируй описание и выдели все UI элементы (кнопки, поля, иконки)
2. Создай структуру названий файлов в формате:
   Chrome-{platform_name}-<Element>-btn.png

3. Формат ответа:

📂 СТРУКТУРА ДЛЯ {platform_name.upper()}
================================================================================

Папка: templates/Chrome/{platform_name}/

Файлы для создания:
  • Chrome-{platform_name}-<Element1>-btn.png - <Описание>
  • Chrome-{platform_name}-<Element2>-btn.png - <Описание>
  ...

Краткие имена для DSL:
  • Chrome-{platform_name}-<Element1> - <Описание>
  • <Element1> (короткое имя) - <Описание>
  ...

Типичный сценарий:
  open ChromeApp
  wait 2s
  click ChromeNewTab
  wait 1s
  click ChromeSearchField
  type "{platform_name.lower()}.com"
  press enter
  wait 5s
  click Chrome-{platform_name}-<Element1>
  ...

================================================================================

ПРИМЕР (для TikTok):
  • Chrome-TikTok-Like-btn.png - Кнопка лайка
  • Chrome-TikTok-Comment-btn.png - Кнопка комментариев
  • Chrome-TikTok-ScrollDown-btn.png - Скролл вниз

Верни ТОЛЬКО структуру, без дополнительных объяснений!
"""
            
            print(f"🤖 AI создаёт структуру для {platform_name}...")
            
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            
            # Сохраняем в отдельный файл
            output_file = self.templates_dir / f"{platform_name}_STRUCTURE.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print()
            print("✅ Структура создана!")
            print(f"📄 Сохранено: {output_file}")
            print()
            print("📋 СЛЕДУЮЩИЕ ШАГИ:")
            print()
            print(f"1. Создайте папку: templates/Chrome/{platform_name}/")
            print(f"2. Откройте файл: {output_file}")
            print("3. Используйте Smart Capture для создания шаблонов:")
            print("   python3 utils/smart_capture.py")
            print(f"4. Сохраняйте файлы с именами из {output_file}")
            print("5. Запустите обновление промптов:")
            print("   python3 utils/prompt_updater.py --update")
            print()
            
            return True
            
        except ImportError:
            print("❌ Установите: pip install google-genai")
            return False
        except Exception as e:
            print(f"❌ Ошибка AI: {e}")
            return False


def main():
    """Главная функция"""
    import sys
    
    project_root = Path(__file__).parent.parent
    updater = PromptUpdater(project_root)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--update":
            # Обновить все промпты
            updater.update_all(auto_confirm=False)
        
        elif command == "--auto":
            # Автоматическое обновление без подтверждения
            updater.update_all(auto_confirm=True)
        
        elif command == "--add-platform":
            # Добавить новую платформу
            if len(sys.argv) < 4:
                print("Использование: --add-platform <название> '<описание>'")
                print()
                print("Пример:")
                print("  --add-platform Instagram 'открываю Instagram, кликаю лайк, пишу комментарий'")
                sys.exit(1)
            
            platform = sys.argv[2]
            description = sys.argv[3]
            updater.add_new_platform(platform, description)
        
        else:
            print(f"❌ Неизвестная команда: {command}")
            sys.exit(1)
    
    else:
        # Интерактивный режим
        print()
        print("=" * 80)
        print("🔄 ОБНОВЛЕНИЕ ПРОМПТОВ")
        print("=" * 80)
        print()
        print("Выберите действие:")
        print()
        print("1. 🔄 Обновить все промпты (сканирует templates/)")
        print("2. ➕ Добавить новую платформу (AI создаст структуру)")
        print("3. 📊 Показать текущую структуру")
        print("4. ❌ Выход")
        print()
        
        choice = input("Ваш выбор (1-4): ")
        
        if choice == "1":
            updater.update_all(auto_confirm=False)
        
        elif choice == "2":
            platform = input("\n📝 Название платформы (например: Instagram): ")
            description = input("📝 Описание действий: ")
            updater.add_new_platform(platform, description)
        
        elif choice == "3":
            structure = updater.scan_templates()
            desc = updater.generate_structure_description(structure)
            print()
            print(desc)
        
        elif choice == "4":
            print("👋 До свидания!")
        
        else:
            print("❌ Неверный выбор")


if __name__ == "__main__":
    main()
