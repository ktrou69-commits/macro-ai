#!/usr/bin/env python3
"""
ai_macro_generator.py
Оптимизированный AI генератор с контекстной фильтрацией
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional, Dict, List, Set
import subprocess

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import MACROS_DIR, TEMPLATES_DIR
from src.utils.api_config import api_config


class AIMacroGenerator:
    """Оптимизированный AI генератор макросов"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.templates_dir = project_root / "templates"
        self.macros_dir = MACROS_DIR
        self.dsl_ref_path = project_root / "dsl_references" / "DSL_REFERENCE.txt"
        self.user_variables_path = project_root / "dsl_references" / "USER_VARIABLES.txt"
        
        # API ключи из централизованной конфигурации
        self.openai_key = api_config.openai_key
        self.anthropic_key = api_config.anthropic_key
        self.gemini_key = api_config.gemini_key
        
        # Кэш для оптимизации
        self._templates_cache = {}
        self._dsl_commands_cache = None
        self._best_practices_cache = {}
        self._user_variables_cache = None
    
    def analyze_user_intent(self, user_input: str) -> Dict[str, any]:
        """
        Анализирует запрос пользователя и определяет контекст
        
        Returns:
            {
                'platforms': ['tiktok', 'youtube'],  # Какие платформы нужны
                'actions': ['like', 'comment'],       # Какие действия
                'needs_chrome': True,                 # Нужен ли Chrome
                'complexity': 'simple'                # simple/medium/complex
            }
        """
        user_lower = user_input.lower()
        
        # Определяем платформы
        platforms = set()
        if any(word in user_lower for word in ['tiktok', 'тикток', 'тик ток']):
            platforms.add('tiktok')
        if any(word in user_lower for word in ['youtube', 'ютуб', 'ютьюб']):
            platforms.add('youtube')
        if any(word in user_lower for word in ['instagram', 'инста', 'инстаграм']):
            platforms.add('instagram')
        
        # Определяем действия
        actions = set()
        if any(word in user_lower for word in ['лайк', 'like', 'поставить лайк']):
            actions.add('like')
        if any(word in user_lower for word in ['комментарий', 'comment', 'написать']):
            actions.add('comment')
        if any(word in user_lower for word in ['поиск', 'search', 'найти']):
            actions.add('search')
        if any(word in user_lower for word in ['скролл', 'scroll', 'пролистать']):
            actions.add('scroll')
        if any(word in user_lower for word in ['открыть', 'open', 'перейти']):
            actions.add('open')
        
        # Нужен ли Chrome
        needs_chrome = bool(platforms) or 'chrome' in user_lower or 'хром' in user_lower
        
        # Определяем сложность
        complexity = 'simple'
        if len(actions) > 2 or len(platforms) > 1:
            complexity = 'medium'
        if any(word in user_lower for word in ['цикл', 'repeat', 'несколько', 'много']):
            complexity = 'medium'
        if any(word in user_lower for word in ['если', 'try', 'catch', 'ошибка']):
            complexity = 'complex'
        
        return {
            'platforms': list(platforms),
            'actions': list(actions),
            'needs_chrome': needs_chrome,
            'complexity': complexity
        }
    
    def get_contextual_templates(self, platforms: List[str]) -> str:
        """
        Возвращает только релевантные шаблоны для указанных платформ
        
        ПОЧЕМУ ЛУЧШЕ:
        - Уменьшает размер промпта на 60-80%
        - AI видит только нужные шаблоны
        - Меньше путаницы, точнее результат
        """
        if not platforms:
            # Если платформа не определена, даём базовый набор
            platforms = ['chrome_basic']
        
        # Кэшируем результаты
        cache_key = ','.join(sorted(platforms))
        if cache_key in self._templates_cache:
            return self._templates_cache[cache_key]
        
        templates = []
        templates.append("📂 ДОСТУПНЫЕ ШАБЛОНЫ\n")
        
        # Всегда добавляем базовые Chrome шаблоны
        templates.append("Chrome - Базовые:")
        templates.append("  • ChromeApp           - Запуск Chrome")
        templates.append("  • ChromeNewTab        - Новая вкладка")
        templates.append("  • ChromeSearchField   - Адресная строка")
        templates.append("  • ChromeReload        - Обновить страницу")
        templates.append("")
        
        # Добавляем платформо-специфичные шаблоны
        if 'tiktok' in platforms:
            templates.append("TikTok:")
            templates.append("  • Chrome-TikTok-Like         - Лайк видео")
            templates.append("  • Chrome-TikTok-Comment      - Открыть комментарии")
            templates.append("  • Chrome-TikTok-CommentField - Поле комментария")
            templates.append("  • Chrome-TikTok-CommentSend  - Отправить комментарий")
            templates.append("  • Chrome-TikTok-Search       - Кнопка поиска")
            templates.append("  • Chrome-TikTok-SearchField  - Поле поиска")
            templates.append("  • Chrome-TikTok-ScrollDown   - Скролл вниз")
            templates.append("")
        
        if 'youtube' in platforms:
            templates.append("YouTube:")
            templates.append("  • Chrome-YouTube-SearchField - Поле поиска")
            templates.append("  • Chrome-YouTube-VideoFirst  - Первое видео")
            templates.append("  • Chrome-YouTube-Like        - Лайк видео")
            templates.append("  • Chrome-YouTube-Subscribe   - Подписка")
            templates.append("  • Chrome-YouTube-Comment     - Открыть комментарии")
            templates.append("  • Chrome-YouTube-CommentField - Поле комментария")
            templates.append("")
        
        result = "\n".join(templates)
        self._templates_cache[cache_key] = result
        return result
    
    def get_contextual_best_practices(self, actions: List[str], complexity: str) -> str:
        """
        Возвращает только релевантные best practices
        
        ПОЧЕМУ ЛУЧШЕ:
        - Фокус на конкретных действиях
        - Нет информационного шума
        - AI лучше следует правилам
        """
        cache_key = f"{','.join(sorted(actions))}_{complexity}"
        if cache_key in self._best_practices_cache:
            return self._best_practices_cache[cache_key]
        
        practices = []
        practices.append("⭐ КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА\n")
        
        # Базовые правила (всегда)
        practices.append("1. ОБЯЗАТЕЛЬНЫЕ ПАУЗЫ:")
        practices.append("   • После клика на поле ввода → wait 1s → type")
        practices.append("   • После type → wait 0.5s")
        practices.append("   • После press enter → wait 5s (загрузка)")
        practices.append("   • После click Like → wait 1.5s")
        practices.append("")
        
        practices.append("2. CHROME НАВИГАЦИЯ:")
        practices.append("   • ВСЕГДА: open ChromeApp → wait 2s → click ChromeNewTab")
        practices.append("   • НИКОГДА не пропускай ChromeNewTab!")
        practices.append("")
        
        # Специфичные для действий
        if 'like' in actions or 'scroll' in actions:
            practices.append("3. ЛАЙКИ И СКРОЛЛ:")
            practices.append("   repeat N:")
            practices.append("     click Like")
            practices.append("     wait 1.5s")
            practices.append("     scroll down")
            practices.append("     wait 2s")
            practices.append("")
        
        if 'comment' in actions:
            practices.append("4. КОММЕНТАРИИ:")
            practices.append("   click Comment → wait 2s")
            practices.append("   click CommentField → wait 1s")
            practices.append("   type 'text' → wait 1s")
            practices.append("   click Send → wait 2s")
            practices.append("")
        
        if 'search' in actions:
            practices.append("5. ПОИСК:")
            practices.append("   click SearchField → wait 1s")
            practices.append("   type 'query' → press enter → wait 3s")
            practices.append("")
        
        # Try/catch для сложных сценариев
        if complexity == 'complex':
            practices.append("6. ОБРАБОТКА ОШИБОК:")
            practices.append("   try:")
            practices.append("     <критичная операция>")
            practices.append("   catch:")
            practices.append("     log 'error'")
            practices.append("     <fallback>")
            practices.append("   end")
            practices.append("")
        
        result = "\n".join(practices)
        self._best_practices_cache[cache_key] = result
        return result
    
    def get_dsl_commands_compact(self) -> str:
        """
        Возвращает компактный список DSL команд
        
        ПОЧЕМУ ЛУЧШЕ:
        - Только синтаксис, без примеров
        - Примеры будут в best practices
        - Уменьшает дублирование
        """
        if self._dsl_commands_cache:
            return self._dsl_commands_cache
        
        commands = """📖 DSL КОМАНДЫ

Клики:
  open <template>           # Запуск приложения
  click <template>          # Клик по элементу
  click (<x>, <y>)          # Клик по координатам
  double_click <template>   # Двойной клик

Ввод:
  type "<text>"             # Ввод текста
  press <key>               # Нажатие клавиши (enter, tab, esc)
  hotkey <key>+<key>        # Комбинация (command+c)

Управление:
  wait <duration>           # Пауза (1s, 2.5s, 500ms)
  scroll <direction>        # Скролл (up, down, left, right)
  repeat <N>:               # Цикл
    <команды>

Обработка ошибок:
  try:                      # Начало try блока
    <команды>
  catch:                    # Обработка ошибки
    log "<message>"         # Логирование
    <fallback команды>
    abort                   # Прервать выполнение
  end                       # Конец блока

Параметры:
  threshold=0.7             # Порог совпадения (0.0-1.0)
  timeout=5.0               # Таймаут ожидания (секунды)
  index=0                   # Индекс элемента (если несколько)
"""
        self._dsl_commands_cache = commands
        return commands
    
    def load_user_variables(self) -> str:
        """
        Загружает пользовательские DSL переменные из USER_VARIABLES.txt
        
        Returns:
            Отформатированная строка с переменными для промпта
        """
        # Используем кэш если есть
        if self._user_variables_cache is not None:
            return self._user_variables_cache
        
        if not self.user_variables_path.exists():
            self._user_variables_cache = ""
            return ""
        
        try:
            with open(self.user_variables_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсим переменные из файла
            variables = []
            current_var = None
            current_desc = None
            current_code = []
            in_code = False
            
            for line in content.split('\n'):
                # Начало новой переменной
                if line.strip().startswith('${') and line.strip().endswith('}'):
                    # Сохраняем предыдущую
                    if current_var and current_code:
                        variables.append({
                            'name': current_var,
                            'description': current_desc or '',
                            'code': '\n'.join(current_code).strip()
                        })
                    
                    current_var = line.strip()[2:-1]  # Убираем ${ и }
                    current_desc = None
                    current_code = []
                    in_code = False
                
                # Описание (комментарий после разделителя)
                elif line.strip().startswith('# ') and not in_code and current_var:
                    if 'Создано:' not in line and 'Использований:' not in line:
                        current_desc = line.strip()[2:]
                
                # Разделитель - начало кода
                elif line.strip().startswith('-' * 10):
                    if not in_code:
                        in_code = True
                    else:
                        in_code = False
                
                # Секция ИСПОЛЬЗОВАНИЕ - конец кода
                elif line.strip().startswith('ИСПОЛЬЗОВАНИЕ:'):
                    in_code = False
                
                # Код переменной
                elif in_code and line.strip():
                    current_code.append(line)
            
            # Сохраняем последнюю переменную
            if current_var and current_code:
                variables.append({
                    'name': current_var,
                    'description': current_desc or '',
                    'code': '\n'.join(current_code).strip()
                })
            
            # Если нет переменных
            if not variables:
                self._user_variables_cache = ""
                return ""
            
            # Форматируем для промпта
            result = "\n📚 ПОЛЬЗОВАТЕЛЬСКИЕ DSL ПЕРЕМЕННЫЕ:\n\n"
            result += "Ты можешь использовать эти переменные, созданные пользователем:\n\n"
            
            for var in variables:
                result += f"${{{var['name']}}}\n"
                if var['description']:
                    result += f"  Описание: {var['description']}\n"
                result += f"  Код:\n"
                for line in var['code'].split('\n')[:5]:  # Первые 5 строк
                    result += f"    {line}\n"
                if len(var['code'].split('\n')) > 5:
                    result += f"    ... (еще {len(var['code'].split('\n')) - 5} строк)\n"
                result += "\n"
            
            result += "💡 ВАЖНО: Используй эти переменные когда подходит контекст!\n"
            result += "   Например, если пользователь просит 'открыть YouTube', используй ${YouTubeOpen} если она есть.\n"
            
            self._user_variables_cache = result
            return result
            
        except Exception as e:
            print(f"⚠️  Ошибка загрузки пользовательских переменных: {e}")
            self._user_variables_cache = ""
            return ""
    
    def build_optimized_prompt(self, user_input: str) -> str:
        """
        Строит оптимизированный промпт на основе анализа запроса
        
        ПОЧЕМУ ЛУЧШЕ:
        - Размер промпта уменьшается на 60-80%
        - Только релевантная информация
        - Лучше качество генерации
        - Дешевле (меньше токенов)
        - Быстрее (меньше обработки)
        """
        # Анализируем запрос
        context = self.analyze_user_intent(user_input)
        
        # Получаем контекстные данные
        templates = self.get_contextual_templates(context['platforms'])
        practices = self.get_contextual_best_practices(context['actions'], context['complexity'])
        commands = self.get_dsl_commands_compact()
        user_variables = self.load_user_variables()  # Загружаем пользовательские переменные
        
        # Строим промпт
        prompt = f"""Ты — AI-генератор DSL макросов для автоматизации Chrome.

Твоя задача: создать корректный DSL макрос по описанию пользователя.

{templates}

{commands}

{practices}

{user_variables}

🎯 ФОРМАТ ОТВЕТА:

1. Первая строка: 🎯 Макрос: "<короткое_название>"
2. Пустая строка
3. Чистый DSL код (без маркеров ```)

ПРАВИЛА ИМЕНОВАНИЯ:
✅ ПРАВИЛЬНО: youtube_search, tiktok_likes, chrome_open
❌ НЕПРАВИЛЬНО: найти_блогера_а4_на_youtube_через_chrome

Примеры хороших названий:
- "открыть YouTube и найти видео" → youtube_search
- "поставить 5 лайков в TikTok" → tiktok_likes
- "написать комментарий" → write_comment

⏩ INPUT: {user_input}
"""
        
        return prompt
    
    def generate_with_gemini(self, user_input: str) -> Optional[str]:
        """Генерация через Google Gemini API"""
        # Сбрасываем кэш пользовательских переменных для перечитывания файла
        self._user_variables_cache = None
        
        try:
            from google import genai
            
            if not self.gemini_key:
                print("❌ GEMINI_API_KEY не установлен")
                return None
            
            client = genai.Client(api_key=self.gemini_key)
            
            # Используем оптимизированный промпт
            prompt = self.build_optimized_prompt(user_input)
            
            print("🤖 Генерация через Google Gemini (оптимизированный промпт)...")
            print(f"📊 Размер промпта: ~{len(prompt)} символов")
            
            response = client.models.generate_content(
                model=api_config.gemini_model,
                contents=prompt
            )
            
            return response.text
            
        except ImportError:
            print("❌ Установите: pip install google-genai")
            return None
        except Exception as e:
            print(f"❌ Ошибка Gemini: {e}")
            return None
    
    def parse_ai_response(self, response: str) -> Dict[str, str]:
        """Парсит ответ AI и извлекает название и DSL код"""
        lines = response.strip().split('\n')
        
        # Ищем название макроса
        name = "ai_generated_macro"
        for line in lines:
            if line.startswith("🎯 Макрос:"):
                match = re.search(r'"([^"]+)"', line)
                if match:
                    name = match.group(1)
                    name = re.sub(r'[^\w\s-]', '', name)
                    name = re.sub(r'[-\s]+', '_', name)
                    name = name.lower()
                break
        
        # Извлекаем DSL код
        dsl_lines = []
        skip_first_lines = True
        
        for line in lines:
            if skip_first_lines:
                if line.startswith("🎯 Макрос:") or not line.strip():
                    continue
                else:
                    skip_first_lines = False
            
            if line.strip().startswith("```"):
                continue
            
            if line.strip():
                dsl_lines.append(line)
        
        dsl_code = '\n'.join(dsl_lines)
        
        return {
            'name': name,
            'dsl': dsl_code
        }
    
    def save_macro(self, name: str, dsl_code: str) -> Path:
        """Сохраняет макрос в файл"""
        self.macros_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{name}.atlas"
        filepath = self.macros_dir / filename
        
        counter = 1
        while filepath.exists():
            filename = f"{name}_{counter}.atlas"
            filepath = self.macros_dir / filename
            counter += 1
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(dsl_code)
        
        return filepath
    
    def generate_and_save(self, user_input: str) -> Optional[Path]:
        """Генерирует макрос и сохраняет в файл"""
        print()
        print("=" * 80)
        print("🤖 ОПТИМИЗИРОВАННЫЙ AI ГЕНЕРАТОР")
        print("=" * 80)
        print()
        print(f"📝 Ваш запрос: {user_input}")
        print()
        
        # Анализируем контекст
        context = self.analyze_user_intent(user_input)
        print(f"🔍 Обнаружено:")
        print(f"   Платформы: {', '.join(context['platforms']) or 'не определено'}")
        print(f"   Действия: {', '.join(context['actions']) or 'не определено'}")
        print(f"   Сложность: {context['complexity']}")
        print()
        
        # Генерируем
        response = self.generate_with_gemini(user_input)
        
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
        print("Использование: python3 ai_macro_generator.py '<описание>'")
        print()
        print("Пример:")
        print("  python3 ai_macro_generator.py 'поставить 5 лайков в TikTok'")
        sys.exit(1)
    
    user_input = sys.argv[1]
    project_root = Path(__file__).parent.parent.parent
    
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
