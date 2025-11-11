"""
DSL Service - Сервис для работы с DSL переменными
Интеграция с существующим функционалом из src/ai/variable_generator.py
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

class DSLService:
    """Сервис для работы с DSL переменными"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
        # Добавляем путь к src для импорта
        sys.path.insert(0, str(project_root))
        
        # Импортируем необходимые классы
        try:
            from src.ai.variable_generator import AIVariableGenerator
            from src.ai.macro_generator import AIMacroGenerator
            self.variable_generator = AIVariableGenerator(project_root)
            self.macro_generator = AIMacroGenerator(project_root)
            self.ai_available = True
        except ImportError as e:
            print(f"⚠️ AI недоступен: {e}")
            self.ai_available = False
    
    def is_ai_available(self) -> bool:
        """Проверка доступности AI"""
        return self.ai_available
    
    def get_variables_list(self) -> List[Dict[str, Any]]:
        """
        Получение списка всех DSL переменных (пользовательские + системные)
        
        Returns:
            List с переменными
        """
        if not self.ai_available:
            return []
        
        try:
            variables = []
            
            # 1. ПОЛЬЗОВАТЕЛЬСКИЕ ПЕРЕМЕННЫЕ (из dsl_references/USER_VARIABLES.txt)
            user_var_names = self.variable_generator.list_variables()
            
            for var_name in user_var_names:
                var_info = self.variable_generator.get_variable_info(var_name)
                if var_info:
                    variables.append({
                        'name': var_info['name'],
                        'display_name': f"${{{var_info['name']}}}",
                        'description': var_info.get('description', 'Без описания'),
                        'code': var_info.get('code', ''),
                        'created': var_info.get('created', ''),
                        'usage_count': var_info.get('usage_count', 0),
                        'lines_count': len(var_info.get('code', '').split('\n')),
                        'type': 'user',
                        'source': 'dsl_references/USER_VARIABLES.txt'
                    })
            
            # 2. СИСТЕМНЫЕ ПЕРЕМЕННЫЕ (из templates/DSL_VARIABLES.txt)
            system_variables = self._load_system_variables()
            variables.extend(system_variables)
            
            return variables
            
        except Exception as e:
            print(f"Ошибка загрузки переменных: {e}")
            return []
    
    def _load_system_variables(self) -> List[Dict[str, Any]]:
        """Загрузка системных переменных из templates/DSL_VARIABLES.txt"""
        
        system_file = self.project_root / "templates" / "DSL_VARIABLES.txt"
        
        if not system_file.exists():
            return []
        
        try:
            with open(system_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
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
                            'display_name': f"${{{current_var}}}",
                            'description': current_desc or 'Системная переменная',
                            'code': '\n'.join(current_code).strip(),
                            'created': 'Системная',
                            'usage_count': 0,
                            'lines_count': len(current_code),
                            'type': 'system',
                            'source': 'templates/DSL_VARIABLES.txt'
                        })
                    
                    current_var = line.strip()[2:-1]  # Убираем ${ и }
                    current_desc = None
                    current_code = []
                    in_code = False
                
                # Описание (комментарий после разделителя)
                elif line.strip().startswith('# ') and not in_code and current_var:
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
                    'display_name': f"${{{current_var}}}",
                    'description': current_desc or 'Системная переменная',
                    'code': '\n'.join(current_code).strip(),
                    'created': 'Системная',
                    'usage_count': 0,
                    'lines_count': len(current_code),
                    'type': 'system',
                    'source': 'templates/DSL_VARIABLES.txt'
                })
            
            return variables
            
        except Exception as e:
            print(f"Ошибка загрузки системных переменных: {e}")
            return []
    
    def get_variable_details(self, var_name: str) -> Optional[Dict[str, Any]]:
        """
        Получение подробной информации о переменной
        
        Args:
            var_name: Название переменной
            
        Returns:
            Dict с подробной информацией
        """
        if not self.ai_available:
            return None
        
        try:
            return self.variable_generator.get_variable_info(var_name)
        except Exception as e:
            print(f"Ошибка получения информации о переменной: {e}")
            return None
    
    def generate_variable_async(self, description: str, callback=None) -> Dict[str, Any]:
        """
        Асинхронная генерация DSL переменной
        
        Args:
            description: Описание действия для переменной
            callback: Функция для обновления прогресса
            
        Returns:
            Dict с результатом операции
        """
        if not self.ai_available:
            return {
                'success': False,
                'error': 'AI недоступен',
                'message': 'Установите необходимые библиотеки: pip install openai anthropic google-genai'
            }
        
        try:
            if callback:
                callback("🔄 Генерация DSL кода через AI...")
            
            # Генерируем DSL код
            dsl_code = self.macro_generator.generate_with_gemini(description)
            
            if not dsl_code:
                return {
                    'success': False,
                    'error': 'Не удалось сгенерировать код',
                    'message': 'AI не смог создать DSL код для данного описания'
                }
            
            if callback:
                callback("🤖 Создание переменной...")
            
            # Создаем переменную
            variable = self.variable_generator.generate_variable(description, dsl_code)
            
            return {
                'success': True,
                'variable': variable,
                'dsl_code': dsl_code,
                'message': f'Переменная ${{{variable["name"]}}} успешно создана!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Ошибка генерации: {e}'
            }
    
    def save_variable(self, variable: Dict[str, Any]) -> Dict[str, Any]:
        """
        Сохранение переменной в файл
        
        Args:
            variable: Dict с данными переменной
            
        Returns:
            Dict с результатом операции
        """
        if not self.ai_available:
            return {
                'success': False,
                'error': 'AI недоступен'
            }
        
        try:
            success = self.variable_generator.save_variable(variable)
            
            if success:
                return {
                    'success': True,
                    'message': f'Переменная ${{{variable["name"]}}} сохранена!',
                    'file_path': str(self.variable_generator.variables_file)
                }
            else:
                return {
                    'success': False,
                    'error': 'Не удалось сохранить переменную'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_variable(self, var_name: str) -> Dict[str, Any]:
        """
        Удаление переменной (улучшенный алгоритм)
        
        Args:
            var_name: Название переменной
            
        Returns:
            Dict с результатом операции
        """
        if not self.ai_available:
            return {
                'success': False,
                'error': 'AI недоступен'
            }
        
        try:
            variables_file = self.variable_generator.variables_file
            
            # Проверяем существование файла
            if not variables_file.exists():
                return {
                    'success': False,
                    'error': 'Файл переменных не найден'
                }
            
            # Читаем файл
            with open(variables_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем существование переменной
            var_marker = f"${{{var_name}}}"
            if var_marker not in content:
                return {
                    'success': False,
                    'error': f'Переменная ${{{var_name}}} не найдена'
                }
            
            # УЛУЧШЕННЫЙ АЛГОРИТМ УДАЛЕНИЯ
            lines = content.split('\n')
            new_lines = []
            skip_block = False
            found_variable = False
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Начало блока переменной
                if line == var_marker:
                    found_variable = True
                    skip_block = True
                    # Пропускаем все строки до следующей переменной или конца файла
                    i += 1
                    continue
                
                # Начало другой переменной - прекращаем пропуск
                elif line.startswith('${') and line.endswith('}') and skip_block:
                    skip_block = False
                    new_lines.append(lines[i])
                    i += 1
                    continue
                
                # Обычная строка
                if not skip_block:
                    new_lines.append(lines[i])
                
                i += 1
            
            if not found_variable:
                return {
                    'success': False,
                    'error': f'Переменная ${{{var_name}}} не найдена в файле'
                }
            
            # Убираем лишние пустые строки в конце
            while new_lines and new_lines[-1].strip() == '':
                new_lines.pop()
            
            # Записываем обратно
            new_content = '\n'.join(new_lines)
            if new_content and not new_content.endswith('\n'):
                new_content += '\n'
            
            with open(variables_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return {
                'success': True,
                'message': f'Переменная ${{{var_name}}} полностью удалена!',
                'file_path': str(variables_file)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_variables_file_path(self) -> str:
        """Получение пути к файлу переменных"""
        if not self.ai_available:
            return ""
        
        return str(self.variable_generator.variables_file)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики по переменным
        
        Returns:
            Dict со статистикой
        """
        if not self.ai_available:
            return {
                'total_variables': 0,
                'total_lines': 0,
                'total_usage': 0
            }
        
        try:
            variables = self.get_variables_list()
            
            total_lines = sum(var['lines_count'] for var in variables)
            total_usage = sum(var['usage_count'] for var in variables)
            
            return {
                'total_variables': len(variables),
                'total_lines': total_lines,
                'total_usage': total_usage,
                'file_path': self.get_variables_file_path()
            }
            
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return {
                'total_variables': 0,
                'total_lines': 0,
                'total_usage': 0
            }
