#!/usr/bin/env python3
"""
ai_macro_generator.py
AI генератор макросов - создание .atlas файлов по описанию

Использует AI (OpenAI/Anthropic/Gemini) для генерации DSL макросов
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional, Dict, List
import subprocess

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import MACROS_DIR, TEMPLATES_DIR
from utils.api_config import api_config


class AIMacroGenerator:
    """AI генератор макросов"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.templates_dir = project_root / "templates"
        self.macros_dir = MACROS_DIR
        self.dsl_ref_path = project_root / "dsl_references" / "DSL_REFERENCE.txt"
        
        # API ключи из централизованной конфигурации
        self.openai_key = api_config.openai_key
        self.anthropic_key = api_config.anthropic_key
        self.gemini_key = api_config.gemini_key
    
    def get_templates_structure(self) -> str:
        """Получает структуру шаблонов с описаниями"""
        
        # Читаем централизованный файл структуры
        main_structure_file = self.templates_dir / "TEMPLATES_STRUCTURE.txt"
        
        if main_structure_file.exists():
            # Читаем централизованный файл с полным описанием
            with open(main_structure_file, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Fallback: Старый метод (если файла нет)
        structure = []
        structure.append("📂 СТРУКТУРА ШАБЛОНОВ:")
        structure.append("")
        
        # Читаем structure.txt файлы если есть
        for structure_file in self.templates_dir.rglob("structure.txt"):
            with open(structure_file, 'r', encoding='utf-8') as f:
                content = f.read()
                structure.append(content)
                structure.append("")
        
        # Сканируем все PNG файлы
        structure.append("📄 ДОСТУПНЫЕ ШАБЛОНЫ:")
        for png_file in sorted(self.templates_dir.rglob("*.png")):
            relative_path = png_file.relative_to(self.templates_dir)
            name = png_file.stem
            structure.append(f"  • {name} ({relative_path})")
        
        return "\n".join(structure)
    
    def get_best_practices(self) -> str:
        """Получает лучшие практики использования"""
        best_practices_file = self.templates_dir / "BEST_PRACTICES.txt"
        if best_practices_file.exists():
            with open(best_practices_file, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def get_dsl_reference(self) -> str:
        """Получает DSL справочник"""
        if self.dsl_ref_path.exists():
            with open(self.dsl_ref_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Генерируем справочник если его нет
            print("📚 Генерация DSL справочника...")
            subprocess.run([
                "python3",
                str(self.project_root / "utils" / "dsl_reference_generator.py")
            ], cwd=self.project_root, capture_output=True)
            
            if self.dsl_ref_path.exists():
                with open(self.dsl_ref_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return "DSL справочник недоступен"
    
    def build_system_prompt(self) -> str:
        """Строит системный промпт для AI"""
        
        templates_structure = self.get_templates_structure()
        dsl_reference = self.get_dsl_reference()
        best_practices = self.get_best_practices()
        
        prompt = f"""Ты — AI-интерпретатор DSL-сценариев автоматизации интерфейса Chrome.

У тебя есть доступ к структуре шаблонов, справочнику DSL и лучшим практикам.

Твоя задача — по входному описанию (INPUT) создавать корректный, логичный и эффективный DSL-макрос,
который можно выполнить в интерфейсе Chrome/TikTok/YouTube.

---
📘 СТРУКТУРА ШАБЛОНОВ

{templates_structure}

---
📚 DSL СПРАВОЧНИК

{dsl_reference}

---
⭐ ЛУЧШИЕ ПРАКТИКИ

{best_practices}

---
🎯 ПРАВИЛА ГЕНЕРАЦИИ

1. Ответ всегда начинается с заголовка:  
   **🎯 Макрос: "<краткое описание или имя задачи>"**

2. После заголовка — кодовый блок DSL (форматированный, чистый, без пояснений).

3. Макрос должен быть **логически завершённым сценарием** (если возможно).

4. Разрешено добавлять **комментарии** в код (`# ...`) для читаемости.

5. Если INPUT расплывчатый, ты можешь:
   - логически дополнить действия (например, открыть Chrome, перейти, кликнуть);
   - добавить "wait 2s" между шагами для реализма.

6. Если INPUT просит "вариации" — создай 2-3 разных подхода (в DSL), с пометкой "Вариант 1 / 2 / 3".

7. ВАЖНО: Используй только те шаблоны которые есть в структуре выше!

8. ЛУЧШИЕ ПРАКТИКИ - ОБЯЗАТЕЛЬНО СЛЕДУЙ:
   ✅ ВСЕГДА используй ChromeNewTab перед переходом на сайт
   ✅ ВСЕГДА добавляй ожидания между действиями (wait 1-2s)
   ✅ ВСЕГДА жди загрузки сайта (wait 5s после enter)
   ⭐ ВСЕГДА добавляй wait 1s после клика на поле ввода перед вводом текста!
   ⭐ ВСЕГДА добавляй wait 1s после клика на кнопку поиска!
   ❌ НИКОГДА не пропускай ChromeNewTab после открытия Chrome
   ❌ НИКОГДА не делай действия слишком быстро без ожиданий
   ❌ НИКОГДА не вводи текст сразу после клика на поле (добавь wait 1s!)
   
   Примеры ОБЯЗАТЕЛЬНЫХ пауз:
   • click SearchField → wait 1s → type "text"
   • click CommentField → wait 1s → type "comment"
   • click Search button → wait 1s → click SearchField
   • type "text" → wait 0.5s (после ввода)
   • press enter → wait 5s (загрузка страницы)

8.1. TRY/CATCH - ОБРАБОТКА ОШИБОК:
   ✅ Используй try/catch для критичных операций
   ✅ Добавляй fallback стратегии в catch блоке
   ✅ Используй log для отладки
   ✅ Используй abort для прерывания при критичных ошибках
   
   Синтаксис:
   try:
     <команды>
   catch:
     log "<сообщение>"
     <fallback команды>
     abort  # опционально
   end
   
   Примеры использования:
   • Открытие приложения с fallback
   • Клик с повторной попыткой
   • Поиск элемента с альтернативным путем

9. НАЗВАНИЕ ФАЙЛА: Используй КОРОТКИЕ названия (2-3 слова, snake_case):
    ✅ ПРАВИЛЬНО: youtube_search, tiktok_likes, chrome_open
    ❌ НЕПРАВИЛЬНО: найти_блогера_а4_на_youtube_через_chrome
    
    Примеры хороших названий:
    - "открыть YouTube и найти видео" → youtube_search
    - "поставить 5 лайков в TikTok" → tiktok_likes
    - "написать комментарий" → write_comment
    - "найти блогера А4" → find_a4

11. Формат ответа СТРОГО:
   - Первая строка: 🎯 Макрос: "<короткое_название>"
   - Пустая строка
   - DSL код (без ```atlas или других маркеров)
   - Только чистый DSL код!

---

⏩ Теперь жди INPUT в формате:

INPUT: <описание действия>
"""
        
        return prompt
    
    def generate_with_openai(self, user_input: str) -> Optional[str]:
        """Генерация через OpenAI API"""
        try:
            import openai
            
            if not self.openai_key:
                print("❌ OPENAI_API_KEY не установлен")
                return None
            
            openai.api_key = self.openai_key
            
            system_prompt = self.build_system_prompt()
            user_prompt = f"INPUT: {user_input}"
            
            print("🤖 Генерация через OpenAI...")
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except ImportError:
            print("❌ Установите: pip install openai")
            return None
        except Exception as e:
            print(f"❌ Ошибка OpenAI: {e}")
            return None
    
    def generate_with_anthropic(self, user_input: str) -> Optional[str]:
        """Генерация через Anthropic Claude API"""
        try:
            import anthropic
            
            if not self.anthropic_key:
                print("❌ ANTHROPIC_API_KEY не установлен")
                return None
            
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            
            system_prompt = self.build_system_prompt()
            user_prompt = f"INPUT: {user_input}"
            
            print("🤖 Генерация через Anthropic Claude...")
            
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            return message.content[0].text
            
        except ImportError:
            print("❌ Установите: pip install anthropic")
            return None
        except Exception as e:
            print(f"❌ Ошибка Anthropic: {e}")
            return None
    
    def generate_with_gemini(self, user_input: str) -> Optional[str]:
        """Генерация через Google Gemini API"""
        try:
            from google import genai
            
            if not self.gemini_key:
                print("❌ GEMINI_API_KEY не установлен")
                return None
            
            # Создаем клиент с API ключом
            client = genai.Client(api_key=self.gemini_key)
            
            system_prompt = self.build_system_prompt()
            full_prompt = f"{system_prompt}\n\nINPUT: {user_input}"
            
            print("🤖 Генерация через Google Gemini...")
            
            # Используем новую модель gemini-2.5-flash
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt
            )
            
            return response.text
            
        except ImportError:
            print("❌ Установите: pip install google-genai")
            return None
        except Exception as e:
            print(f"❌ Ошибка Gemini: {e}")
            return None
    
    def generate_macro(self, user_input: str, provider: str = "auto") -> Optional[str]:
        """
        Генерирует макрос используя AI
        
        Args:
            user_input: Описание желаемого макроса
            provider: AI провайдер (auto, openai, anthropic, gemini)
        
        Returns:
            Сгенерированный DSL код или None
        """
        
        if provider == "auto":
            # Пробуем по порядку
            if self.openai_key:
                result = self.generate_with_openai(user_input)
                if result:
                    return result
            
            if self.anthropic_key:
                result = self.generate_with_anthropic(user_input)
                if result:
                    return result
            
            if self.gemini_key:
                result = self.generate_with_gemini(user_input)
                if result:
                    return result
            
            print("❌ Ни один AI провайдер не доступен")
            print("💡 Установите API ключ:")
            print("   export OPENAI_API_KEY='your-key'")
            print("   export ANTHROPIC_API_KEY='your-key'")
            print("   export GEMINI_API_KEY='your-key'")
            return None
        
        elif provider == "openai":
            return self.generate_with_openai(user_input)
        elif provider == "anthropic":
            return self.generate_with_anthropic(user_input)
        elif provider == "gemini":
            return self.generate_with_gemini(user_input)
        else:
            print(f"❌ Неизвестный провайдер: {provider}")
            return None
    
    def parse_ai_response(self, response: str) -> Dict[str, str]:
        """
        Парсит ответ AI и извлекает название и DSL код
        
        Returns:
            {'name': 'название', 'dsl': 'dsl код'}
        """
        lines = response.strip().split('\n')
        
        # Ищем название макроса
        name = "ai_generated_macro"
        for line in lines:
            if line.startswith("🎯 Макрос:"):
                # Извлекаем название из кавычек
                match = re.search(r'"([^"]+)"', line)
                if match:
                    name = match.group(1)
                    # Преобразуем в имя файла
                    name = re.sub(r'[^\w\s-]', '', name)
                    name = re.sub(r'[-\s]+', '_', name)
                    name = name.lower()
                break
        
        # Извлекаем DSL код
        dsl_lines = []
        in_code_block = False
        skip_first_lines = True
        
        for line in lines:
            # Пропускаем заголовок и пустые строки в начале
            if skip_first_lines:
                if line.startswith("🎯 Макрос:") or not line.strip():
                    continue
                else:
                    skip_first_lines = False
            
            # Пропускаем маркеры кодовых блоков
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue
            
            # Собираем DSL код
            if line.strip():
                dsl_lines.append(line)
        
        dsl_code = '\n'.join(dsl_lines)
        
        return {
            'name': name,
            'dsl': dsl_code
        }
    
    def save_macro(self, name: str, dsl_code: str) -> Path:
        """
        Сохраняет макрос в файл
        
        Returns:
            Путь к созданному файлу
        """
        # Создаем папку если её нет
        self.macros_dir.mkdir(parents=True, exist_ok=True)
        
        # Формируем путь к файлу
        filename = f"{name}.atlas"
        filepath = self.macros_dir / filename
        
        # Проверяем существование и добавляем номер если нужно
        counter = 1
        while filepath.exists():
            filename = f"{name}_{counter}.atlas"
            filepath = self.macros_dir / filename
            counter += 1
        
        # Сохраняем
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(dsl_code)
        
        return filepath
    
    def generate_and_save(self, user_input: str, provider: str = "auto") -> Optional[Path]:
        """
        Генерирует макрос и сохраняет в файл
        
        Returns:
            Путь к созданному файлу или None
        """
        print()
        print("=" * 80)
        print("🤖 AI ГЕНЕРАТОР МАКРОСОВ")
        print("=" * 80)
        print()
        print(f"📝 Ваш запрос: {user_input}")
        print()
        
        # Генерируем
        response = self.generate_macro(user_input, provider)
        
        if not response:
            return None
        
        # Парсим ответ
        parsed = self.parse_ai_response(response)
        
        # Сохраняем
        filepath = self.save_macro(parsed['name'], parsed['dsl'])
        
        print()
        print("✅ Макрос сгенерирован!")
        print(f"📄 Название: {parsed['name']}")
        print(f"💾 Сохранено: {filepath}")
        print()
        
        return filepath


def main():
    """Тестовая функция"""
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python3 ai_macro_generator.py '<описание макроса>'")
        print()
        print("Пример:")
        print("  python3 ai_macro_generator.py 'открыть YouTube и поставить лайк'")
        sys.exit(1)
    
    user_input = sys.argv[1]
    project_root = Path(__file__).parent.parent
    
    generator = AIMacroGenerator(project_root)
    filepath = generator.generate_and_save(user_input)
    
    if filepath:
        print("=" * 80)
        print("✅ ГОТОВО!")
        print("=" * 80)
    else:
        print("=" * 80)
        print("❌ ОШИБКА")
        print("=" * 80)


if __name__ == "__main__":
    main()
