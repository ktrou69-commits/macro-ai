"""
DSL Generator - Генератор DSL макросов через AI
Интеграция с существующим AI для генерации макросов и DSL переменных
"""

from pathlib import Path
from typing import Dict, Any, Optional
import sys

class DSLGenerator:
    """Генератор DSL макросов и переменных через AI"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
        # Добавляем путь к src для импорта
        sys.path.insert(0, str(project_root))
        
    def generate_macro_from_description(self, description: str) -> Dict[str, Any]:
        """
        Генерация макроса из текстового описания
        
        Args:
            description: Описание того, что должен делать макрос
            
        Returns:
            Dict с результатом генерации
        """
        try:
            # Используем настоящий AI генератор
            from src.ai.macro_generator import AIMacroGenerator
            
            generator = AIMacroGenerator(self.project_root)
            result = generator.generate_with_gemini(description)
            
            if result:
                # Извлекаем чистый код из ответа AI
                clean_code = self._extract_code_from_ai_response(result)
                platform = self._detect_platform(description)
                
                return {
                    'success': True,
                    'macro_code': clean_code,
                    'description': f"AI сгенерированный макрос: {description}",
                    'platform': platform
                }
            else:
                return {
                    'success': False,
                    'error': 'AI не смог сгенерировать макрос'
                }
                
        except ImportError:
            # Если AI генератор не найден, используем простую заглушку
            return self._generate_simple_macro(description)
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка генерации: {str(e)}'
            }
    
    def generate_dsl_variable_from_description(self, description: str) -> Dict[str, Any]:
        """
        Генерация DSL переменной из описания
        
        Args:
            description: Описание действия для переменной
            
        Returns:
            Dict с результатом генерации
        """
        try:
            # Генерируем макрос
            macro_result = self.generate_macro_from_description(description)
            
            if macro_result['success']:
                # Создаем имя переменной
                var_name = self._generate_variable_name(description)
                
                return {
                    'success': True,
                    'name': var_name,
                    'code': macro_result['macro_code'],
                    'description': description
                }
            else:
                return macro_result
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка создания переменной: {str(e)}'
            }
    
    def _generate_simple_macro(self, description: str) -> Dict[str, Any]:
        """Простая генерация макроса без AI (заглушка)"""
        
        platform = self._detect_platform(description)
        
        # Простые шаблоны для разных платформ
        if any(word in description.lower() for word in ['tiktok', 'тик ток', 'тикток']):
            macro_code = """open ChromeApp
wait 2s
click ChromeNewTab
wait 1s
click ChromeSearchField
type "tiktok.com"
press enter
wait 5s"""
            
        elif 'youtube' in description.lower():
            macro_code = """open ChromeApp
wait 2s
click ChromeNewTab
wait 1s
click ChromeSearchField
type "youtube.com"
press enter
wait 5s
click Chrome-YouTube-Like
wait 1s"""
            
        elif 'instagram' in description.lower():
            macro_code = """open ChromeApp
wait 2s
click ChromeNewTab
wait 1s
click ChromeSearchField
type "instagram.com"
press enter
wait 5s
click Chrome-Instagram-Like
wait 1s"""
            
        else:
            # Общий шаблон для других запросов
            if any(word in description.lower() for word in ['открой', 'открыть', 'зайди', 'перейди']):
                # Если просят что-то открыть, пытаемся определить что именно
                if any(word in description.lower() for word in ['сайт', 'страниц', 'веб']):
                    macro_code = f"""# Макрос для: {description}
open ChromeApp
wait 2s
click ChromeNewTab
wait 1s
click ChromeSearchField
type "google.com"
press enter
wait 3s
# Введите поисковый запрос или URL вручную"""
                else:
                    macro_code = f"""# Макрос для: {description}
open ChromeApp
wait 2s
click ChromeNewTab
wait 1s
click ChromeSearchField
# Введите URL или поисковый запрос
wait 2s"""
            else:
                macro_code = f"""# Макрос для: {description}
open ChromeApp
wait 2s
click ChromeNewTab
wait 1s
# Добавьте здесь специфичные действия для вашей задачи
"""
        
        return {
            'success': True,
            'macro_code': macro_code,
            'description': f"Автоматически сгенерированный макрос: {description}",
            'platform': platform
        }
    
    def _extract_code_from_ai_response(self, ai_response: str) -> str:
        """Извлечение DSL кода из ответа AI"""
        
        lines = ai_response.split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            # Начало блока кода
            if '```' in line and not in_code_block:
                in_code_block = True
                continue
            
            # Конец блока кода
            if '```' in line and in_code_block:
                break
            
            # Если мы внутри блока кода, добавляем строку
            if in_code_block:
                code_lines.append(line)
            
            # Если это DSL команда (начинается с известных команд)
            elif any(line.strip().startswith(cmd) for cmd in ['open', 'click', 'type', 'wait', 'press', 'repeat', 'scroll']):
                code_lines.append(line)
        
        # Если ничего не найдено, возвращаем весь ответ
        if not code_lines:
            return ai_response.strip()
        
        return '\n'.join(code_lines).strip()
    
    def _detect_platform(self, description: str) -> str:
        """Определение платформы из описания"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['tiktok', 'тик ток', 'тикток']):
            return 'TikTok'
        elif any(word in description_lower for word in ['youtube', 'ютуб', 'ютьюб']):
            return 'YouTube'
        elif any(word in description_lower for word in ['instagram', 'инстаграм', 'инста']):
            return 'Instagram'
        elif any(word in description_lower for word in ['twitter', 'твиттер']):
            return 'Twitter'
        elif any(word in description_lower for word in ['facebook', 'фейсбук']):
            return 'Facebook'
        elif any(word in description_lower for word in ['linkedin', 'линкедин']):
            return 'LinkedIn'
        else:
            return 'Unknown'
    
    def _generate_variable_name(self, description: str) -> str:
        """Генерация имени переменной из описания"""
        
        platform = self._detect_platform(description)
        description_lower = description.lower()
        
        # Определяем действие
        if 'лайк' in description_lower or 'like' in description_lower:
            action = 'Like'
        elif 'комментар' in description_lower or 'comment' in description_lower:
            action = 'Comment'
        elif 'подпис' in description_lower or 'subscribe' in description_lower:
            action = 'Subscribe'
        elif 'поиск' in description_lower or 'search' in description_lower:
            action = 'Search'
        elif 'откр' in description_lower or 'open' in description_lower:
            action = 'Open'
        else:
            action = 'Action'
        
        # Формируем имя переменной
        if platform != 'Unknown':
            return f"{platform}{action}"
        else:
            return f"Custom{action}"
    
    def get_available_templates(self) -> Dict[str, list]:
        """Получение списка доступных шаблонов"""
        try:
            templates = {}
            templates_dir = self.project_root / "templates"
            
            if templates_dir.exists():
                for item in templates_dir.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        png_files = list(item.rglob("*.png"))
                        if png_files:
                            templates[item.name] = [f.name for f in png_files]
            
            return templates
        except Exception as e:
            print(f"⚠️ Ошибка получения шаблонов: {e}")
            return {}
    
    def validate_macro_code(self, code: str) -> Dict[str, Any]:
        """Валидация кода макроса"""
        try:
            lines = code.strip().split('\n')
            errors = []
            warnings = []
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Проверка базовых команд
                if not any(line.startswith(cmd) for cmd in ['open', 'click', 'type', 'wait', 'press', 'repeat']):
                    warnings.append(f"Строка {i}: Неизвестная команда '{line.split()[0] if line.split() else line}'")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Ошибка валидации: {str(e)}"],
                'warnings': []
            }
