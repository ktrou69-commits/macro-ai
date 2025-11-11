#!/usr/bin/env python3
"""
variable_generator.py
AI генератор DSL переменных

Позволяет AI создавать переменные по запросу пользователя:
1. Генерирует DSL код через AIMacroGenerator
2. AI предлагает название переменной
3. AI создает описание
4. Сохраняет в USER_VARIABLES.txt
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.utils.api_config import api_config


class AIVariableGenerator:
    """AI генератор DSL переменных"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.variables_file = project_root / 'dsl_references' / 'USER_VARIABLES.txt'
        
        # API ключи
        self.gemini_key = api_config.gemini_key
        
        # Создаем папку если не существует
        self.variables_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Создаем файл если не существует
        if not self.variables_file.exists():
            self._create_empty_file()
    
    def _create_empty_file(self):
        """Создает пустой файл USER_VARIABLES.txt с заголовком"""
        with open(self.variables_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ПОЛЬЗОВАТЕЛЬСКИЕ DSL ПЕРЕМЕННЫЕ\n")
            f.write("=" * 80 + "\n")
            f.write("\n")
            f.write("📌 Этот файл содержит переменные, созданные пользователем через AI.\n")
            f.write("   Они автоматически загружаются парсером и доступны в AI промпте.\n")
            f.write("\n")
            f.write("=" * 80 + "\n")
            f.write("\n")
    
    def generate_variable(self, user_request: str, dsl_code: str) -> Dict:
        """
        Генерирует переменную по запросу пользователя
        
        Args:
            user_request: Описание действия от пользователя
            dsl_code: Сгенерированный DSL код
        
        Returns:
            Dict с данными переменной:
            {
                'name': 'YouTubeSearchTrending',
                'description': 'Открыть YouTube и найти trending videos',
                'code': 'open ChromeApp\nwait 2s\n...',
                'created': '2025-11-11T07:06:00',
                'usage_count': 0
            }
        """
        # Генерируем название переменной
        var_name = self.suggest_variable_name(user_request, dsl_code)
        
        # Генерируем описание
        description = self.generate_description(user_request, dsl_code)
        
        return {
            'name': var_name,
            'description': description,
            'code': dsl_code,
            'created': datetime.now().isoformat(),
            'usage_count': 0
        }
    
    def suggest_variable_name(self, request: str, code: str) -> str:
        """
        AI предлагает название для переменной
        
        Args:
            request: Запрос пользователя
            code: Сгенерированный DSL код
        
        Returns:
            Название переменной в CamelCase
        """
        try:
            from google import genai
            
            if not self.gemini_key:
                print("⚠️  GEMINI_API_KEY не установлен, использую автоматическое название")
                return self._auto_generate_name(request)
            
            client = genai.Client(api_key=self.gemini_key)
            
            prompt = f"""Предложи короткое название для DSL переменной.

Запрос пользователя: {request}

Сгенерированный код:
{code}

ПРАВИЛА:
1. Формат: CamelCase (например: YouTubeSearch, TikTokAutoLikes, ChromeOpen)
2. Начинается с заглавной буквы
3. Максимум 3-4 слова
4. Понятное и описательное
5. БЕЗ префикса "My" или "User"

Примеры хороших названий:
- "открыть YouTube и найти видео" → YouTubeSearch
- "поставить 5 лайков в TikTok" → TikTokAutoLikes
- "написать комментарий" → WriteComment
- "открыть Chrome" → ChromeOpen

Ответь ТОЛЬКО названием переменной, без объяснений и без символов ${{...}}.
"""
            
            response = client.models.generate_content(
                model=api_config.gemini_model,
                contents=prompt
            )
            
            # Очищаем ответ
            var_name = response.text.strip()
            var_name = var_name.replace('${', '').replace('}', '')
            var_name = re.sub(r'[^\w]', '', var_name)
            
            # Проверка формата
            if not var_name or not var_name[0].isupper():
                print(f"⚠️  AI предложил некорректное название: {var_name}")
                return self._auto_generate_name(request)
            
            return var_name
            
        except ImportError:
            print("⚠️  google-genai не установлен, использую автоматическое название")
            return self._auto_generate_name(request)
        except Exception as e:
            print(f"⚠️  Ошибка генерации названия: {e}")
            return self._auto_generate_name(request)
    
    def _auto_generate_name(self, request: str) -> str:
        """
        Автоматическая генерация названия без AI
        
        Args:
            request: Запрос пользователя
        
        Returns:
            Название переменной
        """
        # Извлекаем ключевые слова
        request_lower = request.lower()
        
        # Определяем платформу
        platform = None
        if 'youtube' in request_lower or 'ютуб' in request_lower:
            platform = 'YouTube'
        elif 'tiktok' in request_lower or 'тикток' in request_lower:
            platform = 'TikTok'
        elif 'chrome' in request_lower or 'хром' in request_lower:
            platform = 'Chrome'
        
        # Определяем действие
        action = None
        if 'search' in request_lower or 'найти' in request_lower or 'поиск' in request_lower:
            action = 'Search'
        elif 'like' in request_lower or 'лайк' in request_lower:
            action = 'Like'
        elif 'comment' in request_lower or 'комментарий' in request_lower:
            action = 'Comment'
        elif 'open' in request_lower or 'открыть' in request_lower:
            action = 'Open'
        elif 'scroll' in request_lower or 'скролл' in request_lower:
            action = 'Scroll'
        
        # Формируем название
        if platform and action:
            return f"{platform}{action}"
        elif platform:
            return f"{platform}Action"
        elif action:
            return f"Custom{action}"
        else:
            return "CustomVariable"
    
    def generate_description(self, request: str, code: str) -> str:
        """
        AI генерирует описание переменной
        
        Args:
            request: Запрос пользователя
            code: Сгенерированный DSL код
        
        Returns:
            Описание переменной
        """
        try:
            from google import genai
            
            if not self.gemini_key:
                print("⚠️  GEMINI_API_KEY не установлен, использую запрос пользователя")
                return request
            
            client = genai.Client(api_key=self.gemini_key)
            
            prompt = f"""Создай краткое описание для DSL переменной.

Запрос пользователя: {request}

Сгенерированный код:
{code}

ПРАВИЛА:
1. Одно предложение
2. Максимум 10-15 слов
3. Описывает ЧТО делает переменная
4. Начинается с глагола (Открыть, Найти, Поставить, Написать)
5. Без технических деталей

Примеры хороших описаний:
- "Открыть YouTube и найти видео по запросу"
- "Поставить лайк и пролистать к следующему видео"
- "Написать комментарий в TikTok"
- "Открыть Chrome и создать новую вкладку"

Ответь ТОЛЬКО описанием, без кавычек и дополнительных символов.
"""
            
            response = client.models.generate_content(
                model=api_config.gemini_model,
                contents=prompt
            )
            
            description = response.text.strip()
            description = description.replace('"', '').replace("'", '')
            
            return description
            
        except ImportError:
            return request
        except Exception as e:
            print(f"⚠️  Ошибка генерации описания: {e}")
            return request
    
    def save_variable(self, variable: Dict) -> bool:
        """
        Сохраняет переменную в USER_VARIABLES.txt
        
        Args:
            variable: Dict с данными переменной
        
        Returns:
            True если успешно сохранено
        """
        try:
            # Проверяем существование переменной
            if self._variable_exists(variable['name']):
                print(f"⚠️  Переменная ${{{variable['name']}}} уже существует!")
                overwrite = input("   Перезаписать? (y/n): ").strip().lower()
                if overwrite != 'y':
                    return False
                # Удаляем старую переменную
                self._remove_variable(variable['name'])
            
            # Добавляем новую переменную
            with open(self.variables_file, 'a', encoding='utf-8') as f:
                f.write(f"${{{variable['name']}}}\n")
                f.write("-" * 80 + "\n")
                f.write(f"# {variable['description']}\n")
                f.write(variable['code'])
                if not variable['code'].endswith('\n'):
                    f.write('\n')
                f.write("\n")
                f.write(f"ИСПОЛЬЗОВАНИЕ:\n")
                f.write(f"${{{variable['name']}}}\n")
                f.write("\n")
                f.write(f"# Создано: {variable['created']}\n")
                f.write(f"# Использований: {variable['usage_count']}\n")
                f.write("\n")
                f.write("-" * 80 + "\n")
                f.write("\n")
            
            print(f"✅ Переменная ${{{variable['name']}}} сохранена!")
            print(f"📁 Файл: {self.variables_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            return False
    
    def _variable_exists(self, var_name: str) -> bool:
        """Проверяет существование переменной"""
        if not self.variables_file.exists():
            return False
        
        with open(self.variables_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"${{{var_name}}}" in content
    
    def _remove_variable(self, var_name: str):
        """Удаляет переменную из файла"""
        if not self.variables_file.exists():
            return
        
        with open(self.variables_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Находим блок переменной
        var_marker = f"${{{var_name}}}"
        start = content.find(var_marker)
        
        if start == -1:
            return
        
        # Находим конец блока (следующая переменная или конец файла)
        next_var = content.find('\n${', start + len(var_marker))
        
        if next_var == -1:
            # Это последняя переменная
            new_content = content[:start]
        else:
            # Удаляем до следующей переменной
            new_content = content[:start] + content[next_var + 1:]
        
        # Записываем обратно
        with open(self.variables_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    def list_variables(self) -> list:
        """
        Возвращает список всех пользовательских переменных
        
        Returns:
            Список названий переменных
        """
        if not self.variables_file.exists():
            return []
        
        variables = []
        
        with open(self.variables_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('${') and line.strip().endswith('}'):
                    var_name = line.strip()[2:-1]
                    variables.append(var_name)
        
        return variables
    
    def get_variable_info(self, var_name: str) -> Optional[Dict]:
        """
        Получает информацию о переменной
        
        Args:
            var_name: Название переменной
        
        Returns:
            Dict с информацией или None
        """
        if not self.variables_file.exists():
            return None
        
        with open(self.variables_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ищем блок переменной
        var_marker = f"${{{var_name}}}"
        if var_marker not in content:
            return None
        
        # Извлекаем блок
        start = content.find(var_marker)
        
        # Находим конец блока (следующая переменная или конец файла)
        next_var = content.find('\n${', start + len(var_marker))
        
        if next_var == -1:
            block = content[start:]
        else:
            block = content[start:next_var]
        
        # Парсим блок
        lines = block.split('\n')
        
        description = None
        code_lines = []
        in_code = False
        created = None
        usage_count = 0
        
        for line in lines:
            if line.strip().startswith('# ') and 'Создано:' not in line and 'Использований:' not in line:
                if not description:
                    description = line.strip()[2:]
            elif line.strip().startswith('ИСПОЛЬЗОВАНИЕ:'):
                in_code = False
            elif line.strip().startswith('# Создано:'):
                created = line.split(':', 1)[1].strip()
            elif line.strip().startswith('# Использований:'):
                try:
                    usage_count = int(line.split(':', 1)[1].strip())
                except:
                    usage_count = 0
            elif in_code and line.strip() and not line.strip().startswith('ИСПОЛЬЗОВАНИЕ'):
                code_lines.append(line)
            elif line.strip() == '-' * 80:
                if not in_code:
                    in_code = True
                else:
                    in_code = False
        
        return {
            'name': var_name,
            'description': description,
            'code': '\n'.join(code_lines).strip(),
            'created': created,
            'usage_count': usage_count
        }


def main():
    """Тестирование генератора"""
    print("🧪 ТЕСТИРОВАНИЕ AI VARIABLE GENERATOR")
    print("=" * 80)
    
    project_root = Path(__file__).parent.parent.parent
    generator = AIVariableGenerator(project_root)
    
    # Тест 1: Создание переменной
    print("\nТЕСТ 1: Создание переменной")
    print("-" * 80)
    
    request = "Открыть YouTube и найти trending videos"
    code = """open ChromeApp
wait 2s
click ChromeNewTab
wait 1s
click ChromeSearchField
type "youtube.com"
press enter
wait 5s
click Chrome-YouTube-SearchField
type "trending videos"
press enter
wait 3s"""
    
    variable = generator.generate_variable(request, code)
    
    print(f"✅ Переменная создана:")
    print(f"   Название: ${{{variable['name']}}}")
    print(f"   Описание: {variable['description']}")
    print(f"   Строк кода: {len(variable['code'].split(chr(10)))}")
    
    # Тест 2: Сохранение
    print("\nТЕСТ 2: Сохранение переменной")
    print("-" * 80)
    
    if generator.save_variable(variable):
        print("✅ Переменная сохранена")
    
    # Тест 3: Список переменных
    print("\nТЕСТ 3: Список переменных")
    print("-" * 80)
    
    variables = generator.list_variables()
    print(f"✅ Найдено переменных: {len(variables)}")
    for var in variables:
        print(f"   - ${{{var}}}")
    
    # Тест 4: Информация о переменной
    print("\nТЕСТ 4: Информация о переменной")
    print("-" * 80)
    
    info = generator.get_variable_info(variable['name'])
    if info:
        print(f"✅ Переменная: ${{{info['name']}}}")
        print(f"   Описание: {info['description']}")
        print(f"   Создано: {info['created']}")
        print(f"   Использований: {info['usage_count']}")
    
    print("\n" + "=" * 80)
    print("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")


if __name__ == "__main__":
    main()
