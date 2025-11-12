"""
DSL валидатор для проверки синтаксиса и автоматического исправления
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Результат валидации DSL"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    fixed_code: Optional[str] = None
    fixes_applied: List[str] = None
    
    def __post_init__(self):
        if self.fixes_applied is None:
            self.fixes_applied = []


class DSLValidator:
    """Валидатор DSL синтаксиса"""
    
    # Допустимые команды DSL
    VALID_COMMANDS = {
        # Базовые команды
        'open', 'click', 'type', 'wait', 'press', 'key',
        
        # Системные команды
        'open_app', 'system_command', 'spotlight_search',
        
        # Веб команды
        'navigate', 'click_element', 'fill_field', 'wait_for_element',
        'scroll_to', 'hover_element', 'switch_tab', 'close_tab',
        
        # Дополнительные команды
        'screenshot', 'save_file', 'load_file'
    }
    
    # Типичные опечатки и их исправления
    COMMON_TYPOS = {
        'opne': 'open',
        'clik': 'click',
        'clck': 'click',
        'typ': 'type',
        'tipe': 'type',
        'wiat': 'wait',
        'weit': 'wait',
        'pres': 'press',
        'pess': 'press',
        'naviage': 'navigate',
        'navigat': 'navigate',
        'fil_field': 'fill_field',
        'fill_fild': 'fill_field',
        'sytem_command': 'system_command',
        'system_comand': 'system_command',
        'spotlight_serch': 'spotlight_search',
        'spotlight_searh': 'spotlight_search'
    }
    
    # Паттерны для валидации аргументов
    ARGUMENT_PATTERNS = {
        'wait': r'^\d+(\.\d+)?s?$',  # 2s, 1.5s, 3
        'type': r'^".*"$',           # "text in quotes"
        'navigate': r'^"https?://.*"$',  # "http://example.com"
        'key': r'^"[^"]*"$',         # "cmd+space"
        'press': r'^"?[a-zA-Z0-9_+]+"?$'  # enter, "cmd+c"
    }
    
    def __init__(self):
        self.validation_stats = {
            "total_validations": 0,
            "errors_found": 0,
            "fixes_applied": 0
        }
    
    def validate_dsl(self, dsl_code: str, auto_fix: bool = True) -> ValidationResult:
        """
        Валидация DSL кода
        
        Args:
            dsl_code: DSL код для валидации
            auto_fix: Автоматически исправлять ошибки
            
        Returns:
            Результат валидации
        """
        self.validation_stats["total_validations"] += 1
        
        errors = []
        warnings = []
        suggestions = []
        fixes_applied = []
        fixed_code = dsl_code
        
        if not dsl_code or not dsl_code.strip():
            return ValidationResult(
                is_valid=False,
                errors=["DSL код пустой"],
                warnings=[],
                suggestions=["Добавьте команды DSL"]
            )
        
        lines = dsl_code.strip().split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Пропускаем пустые строки и комментарии
            if not line_stripped or line_stripped.startswith('#'):
                continue
            
            # Валидация синтаксиса строки
            line_errors, line_warnings, line_suggestions = self._validate_line(line_stripped, i)
            errors.extend(line_errors)
            warnings.extend(line_warnings)
            suggestions.extend(line_suggestions)
            
            # Автоматическое исправление
            if auto_fix:
                fixed_line, line_fixes = self._fix_line(line_stripped)
                if line_fixes:
                    fixes_applied.extend([f"Строка {i}: {fix}" for fix in line_fixes])
                    # Заменяем строку в коде
                    lines[i-1] = line.replace(line_stripped, fixed_line)
        
        # Обновляем исправленный код
        if fixes_applied:
            fixed_code = '\n'.join(lines)
            self.validation_stats["fixes_applied"] += len(fixes_applied)
        
        # Семантическая валидация
        semantic_warnings = self._validate_semantics(fixed_code)
        warnings.extend(semantic_warnings)
        
        if errors:
            self.validation_stats["errors_found"] += len(errors)
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            fixed_code=fixed_code if fixes_applied else None,
            fixes_applied=fixes_applied
        )
    
    def _validate_line(self, line: str, line_number: int) -> Tuple[List[str], List[str], List[str]]:
        """Валидация отдельной строки"""
        errors = []
        warnings = []
        suggestions = []
        
        # Парсинг команды и аргументов
        parts = self._parse_command_line(line)
        if not parts:
            errors.append(f"Строка {line_number}: Невозможно распарсить команду")
            return errors, warnings, suggestions
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Проверка допустимости команды
        if command not in self.VALID_COMMANDS:
            errors.append(f"Строка {line_number}: Неизвестная команда '{command}'")
            
            # Предложение похожей команды
            suggestion = self._suggest_command(command)
            if suggestion:
                suggestions.append(f"Возможно, вы имели в виду '{suggestion}'?")
        
        # Валидация аргументов
        arg_errors, arg_warnings = self._validate_arguments(command, args, line_number)
        errors.extend(arg_errors)
        warnings.extend(arg_warnings)
        
        return errors, warnings, suggestions
    
    def _parse_command_line(self, line: str) -> List[str]:
        """Парсинг строки команды на части"""
        try:
            # Простой парсинг с учетом кавычек
            parts = []
            current_part = ""
            in_quotes = False
            
            for char in line:
                if char == '"':
                    in_quotes = not in_quotes
                    current_part += char
                elif char == ' ' and not in_quotes:
                    if current_part:
                        parts.append(current_part)
                        current_part = ""
                else:
                    current_part += char
            
            if current_part:
                parts.append(current_part)
            
            return parts
        except Exception:
            return []
    
    def _validate_arguments(self, command: str, args: List[str], line_number: int) -> Tuple[List[str], List[str]]:
        """Валидация аргументов команды"""
        errors = []
        warnings = []
        
        # Проверка количества аргументов
        expected_args = self._get_expected_args_count(command)
        if expected_args and len(args) != expected_args:
            errors.append(f"Строка {line_number}: Команда '{command}' ожидает {expected_args} аргументов, получено {len(args)}")
        
        # Проверка формата аргументов
        if command in self.ARGUMENT_PATTERNS and args:
            pattern = self.ARGUMENT_PATTERNS[command]
            for i, arg in enumerate(args):
                if not re.match(pattern, arg):
                    warnings.append(f"Строка {line_number}: Аргумент '{arg}' может иметь неправильный формат для команды '{command}'")
        
        # Специфичные проверки
        if command == 'wait':
            if args and not any(char.isdigit() for char in args[0]):
                errors.append(f"Строка {line_number}: Команда 'wait' требует числовое значение времени")
        
        elif command == 'navigate':
            if args and not (args[0].startswith('"http') or args[0].startswith('"https')):
                warnings.append(f"Строка {line_number}: URL должен начинаться с http:// или https://")
        
        return errors, warnings
    
    def _get_expected_args_count(self, command: str) -> Optional[int]:
        """Получение ожидаемого количества аргументов для команды"""
        args_count = {
            'open': 1,
            'open_app': 1,
            'click': 1,
            'type': 1,
            'wait': 1,
            'press': 1,
            'key': 1,
            'navigate': 1,
            'click_element': 1,
            'fill_field': 2,
            'system_command': 1,
            'spotlight_search': 1
        }
        return args_count.get(command)
    
    def _fix_line(self, line: str) -> Tuple[str, List[str]]:
        """Автоматическое исправление строки"""
        fixes = []
        fixed_line = line
        
        # Исправление опечаток в командах
        parts = fixed_line.split()
        if parts:
            command = parts[0].lower()
            if command in self.COMMON_TYPOS:
                correct_command = self.COMMON_TYPOS[command]
                fixed_line = fixed_line.replace(parts[0], correct_command, 1)
                fixes.append(f"Исправлена опечатка: '{command}' → '{correct_command}'")
        
        # Исправление кавычек
        if 'type ' in fixed_line and not ('"' in fixed_line):
            # Добавляем кавычки к аргументу type
            type_match = re.search(r'type\s+(.+)', fixed_line)
            if type_match:
                text = type_match.group(1).strip()
                if not text.startswith('"'):
                    fixed_line = fixed_line.replace(f'type {text}', f'type "{text}"')
                    fixes.append("Добавлены кавычки к тексту")
        
        # Исправление времени ожидания
        if 'wait ' in fixed_line:
            wait_match = re.search(r'wait\s+(\d+)(?!s)', fixed_line)
            if wait_match:
                time_value = wait_match.group(1)
                fixed_line = fixed_line.replace(f'wait {time_value}', f'wait {time_value}s')
                fixes.append("Добавлена единица времени 's'")
        
        return fixed_line, fixes
    
    def _suggest_command(self, wrong_command: str) -> Optional[str]:
        """Предложение правильной команды на основе схожести"""
        # Сначала проверяем прямые опечатки
        if wrong_command in self.COMMON_TYPOS:
            return self.COMMON_TYPOS[wrong_command]
        
        # Поиск по схожести (простой алгоритм)
        best_match = None
        best_score = 0
        
        for valid_command in self.VALID_COMMANDS:
            score = self._calculate_similarity(wrong_command, valid_command)
            if score > best_score and score > 0.6:  # Минимальный порог схожести
                best_score = score
                best_match = valid_command
        
        return best_match
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Простой расчет схожести строк"""
        if not str1 or not str2:
            return 0.0
        
        # Простая метрика на основе общих символов
        common_chars = set(str1.lower()) & set(str2.lower())
        total_chars = set(str1.lower()) | set(str2.lower())
        
        if not total_chars:
            return 0.0
        
        return len(common_chars) / len(total_chars)
    
    def _validate_semantics(self, dsl_code: str) -> List[str]:
        """Семантическая валидация DSL кода"""
        warnings = []
        
        # Проверка последовательности команд
        lines = [line.strip() for line in dsl_code.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        for i, line in enumerate(lines):
            command = line.split()[0].lower() if line.split() else ""
            
            # Проверка wait после команд, которые требуют времени
            if command in ['open', 'open_app', 'navigate', 'click_element'] and i < len(lines) - 1:
                next_line = lines[i + 1]
                next_command = next_line.split()[0].lower() if next_line.split() else ""
                
                if next_command != 'wait':
                    warnings.append(f"Рекомендуется добавить 'wait' после команды '{command}' для стабильности")
        
        # Проверка на слишком короткие ожидания
        wait_pattern = re.compile(r'wait\s+(\d+(?:\.\d+)?)s?')
        for match in wait_pattern.finditer(dsl_code):
            wait_time = float(match.group(1))
            if wait_time < 0.5:
                warnings.append(f"Время ожидания {wait_time}s может быть слишком коротким")
            elif wait_time > 10:
                warnings.append(f"Время ожидания {wait_time}s может быть слишком долгим")
        
        return warnings
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Получение статистики валидации"""
        return self.validation_stats.copy()
    
    def add_custom_command(self, command: str):
        """Добавление пользовательской команды"""
        self.VALID_COMMANDS.add(command.lower())
        logger.info(f"Добавлена пользовательская команда: {command}")
    
    def add_typo_fix(self, wrong: str, correct: str):
        """Добавление исправления опечатки"""
        self.COMMON_TYPOS[wrong.lower()] = correct.lower()
        logger.info(f"Добавлено исправление опечатки: {wrong} → {correct}")


class DSLFormatter:
    """Форматировщик DSL кода"""
    
    @staticmethod
    def format_dsl(dsl_code: str) -> str:
        """Форматирование DSL кода для лучшей читаемости"""
        lines = dsl_code.split('\n')
        formatted_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                formatted_lines.append("")
            elif stripped.startswith('#'):
                # Комментарии
                formatted_lines.append(stripped)
            else:
                # Команды с правильным отступом
                formatted_lines.append(stripped)
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def add_comments(dsl_code: str) -> str:
        """Добавление поясняющих комментариев к DSL коду"""
        lines = dsl_code.split('\n')
        commented_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped or stripped.startswith('#'):
                commented_lines.append(line)
                continue
            
            # Добавляем комментарии к командам
            parts = stripped.split()
            if parts:
                command = parts[0].lower()
                comment = DSLFormatter._get_command_comment(command, parts[1:])
                if comment:
                    commented_lines.append(f"{stripped}  # {comment}")
                else:
                    commented_lines.append(line)
            else:
                commented_lines.append(line)
        
        return '\n'.join(commented_lines)
    
    @staticmethod
    def _get_command_comment(command: str, args: List[str]) -> str:
        """Получение комментария для команды"""
        comments = {
            'open': "Открыть приложение",
            'open_app': "Запустить приложение",
            'wait': "Ожидание",
            'click': "Кликнуть по элементу",
            'type': "Ввести текст",
            'navigate': "Перейти на страницу",
            'press': "Нажать клавишу"
        }
        
        base_comment = comments.get(command, "")
        
        # Добавляем детали из аргументов
        if args and base_comment:
            if command == 'wait' and args:
                return f"{base_comment} {args[0]}"
            elif command in ['type', 'navigate'] and args:
                return f"{base_comment}: {args[0]}"
        
        return base_comment
