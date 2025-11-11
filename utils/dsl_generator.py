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
            # Пытаемся использовать существующий AI генератор
            from src.ai.ai_generator import AIGenerator
            
            generator = AIGenerator(self.project_root)
            result = generator.generate_sequence_from_description(description)
            
            if result and 'sequence' in result:
                return {
                    'success': True,
                    'macro_code': result['sequence'],
                    'description': result.get('description', description),
                    'platform': result.get('platform', self._detect_platform(description))
                }
            else:
                return {
                    'success': False,
                    'error': 'Не удалось сгенерировать макрос'
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
        if 'tiktok' in description.lower():
            macro_code = """open ChromeApp
wait 2s
click ChromeNewTab
wait 1s
click ChromeSearchField
type "tiktok.com"
press enter
wait 5s
click Chrome-TikTok-Like
wait 1.5s"""
            
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
            # Общий шаблон
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
    
    def _detect_platform(self, description: str) -> str:
        """Определение платформы из описания"""
        description_lower = description.lower()
        
        if 'tiktok' in description_lower:
            return 'TikTok'
        elif 'youtube' in description_lower:
            return 'YouTube'
        elif 'instagram' in description_lower:
            return 'Instagram'
        elif 'twitter' in description_lower:
            return 'Twitter'
        elif 'facebook' in description_lower:
            return 'Facebook'
        elif 'linkedin' in description_lower:
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
