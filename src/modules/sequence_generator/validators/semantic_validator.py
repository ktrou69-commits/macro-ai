"""
Семантический валидатор DSL для проверки логики и доступности ресурсов
"""

import re
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class SemanticValidationResult:
    """Результат семантической валидации"""
    warnings: List[str]
    suggestions: List[str]
    resource_issues: List[str]
    timing_issues: List[str]
    logic_issues: List[str]


class SemanticValidator:
    """Семантическая валидация DSL"""
    
    def __init__(self):
        self.validation_cache = {}
        self.app_cache = {}
        
    def validate_semantics(self, dsl_code: str, context: Optional[Dict[str, Any]] = None) -> SemanticValidationResult:
        """
        Полная семантическая валидация DSL кода
        
        Args:
            dsl_code: DSL код для валидации
            context: Контекст выполнения (доступные ресурсы)
            
        Returns:
            Результат семантической валидации
        """
        warnings = []
        suggestions = []
        resource_issues = []
        timing_issues = []
        logic_issues = []
        
        # Валидация доступности приложений
        app_warnings = self.validate_app_availability(dsl_code)
        resource_issues.extend(app_warnings)
        
        # Валидация таймингов
        timing_warnings, timing_suggestions = self.validate_timing(dsl_code)
        timing_issues.extend(timing_warnings)
        suggestions.extend(timing_suggestions)
        
        # Валидация логики последовательности
        logic_warnings = self.validate_command_sequence(dsl_code)
        logic_issues.extend(logic_warnings)
        
        # Валидация веб-ресурсов
        if context and 'web_selectors' in context:
            web_warnings = self.validate_web_resources(dsl_code, context['web_selectors'])
            resource_issues.extend(web_warnings)
        
        # Валидация системных ресурсов
        if context and 'system_apps' in context:
            system_warnings = self.validate_system_resources(dsl_code, context['system_apps'])
            resource_issues.extend(system_warnings)
        
        # Общие предложения по улучшению
        improvement_suggestions = self.suggest_improvements(dsl_code)
        suggestions.extend(improvement_suggestions)
        
        # Объединяем все предупреждения
        warnings.extend(resource_issues)
        warnings.extend(timing_issues)
        warnings.extend(logic_issues)
        
        return SemanticValidationResult(
            warnings=warnings,
            suggestions=suggestions,
            resource_issues=resource_issues,
            timing_issues=timing_issues,
            logic_issues=logic_issues
        )
    
    def validate_app_availability(self, dsl_code: str) -> List[str]:
        """Проверка доступности приложений"""
        warnings = []
        
        # Извлечение приложений из DSL
        apps = self._extract_apps(dsl_code)
        
        for app in apps:
            if app not in self.app_cache:
                self.app_cache[app] = self._is_app_installed(app)
            
            if not self.app_cache[app]:
                warnings.append(f"Приложение '{app}' не установлено или недоступно")
        
        return warnings
    
    def validate_timing(self, dsl_code: str) -> Tuple[List[str], List[str]]:
        """Проверка таймингов и временных интервалов"""
        warnings = []
        suggestions = []
        
        # Анализ wait команд
        waits = self._extract_waits(dsl_code)
        
        for wait_info in waits:
            wait_time = wait_info['time']
            line_number = wait_info['line']
            context_command = wait_info.get('context_command')
            
            if wait_time < 0.5:
                warnings.append(f"Строка {line_number}: Время ожидания {wait_time}s может быть слишком коротким для стабильной работы")
                suggestions.append(f"Рекомендуется минимум 0.5s для команды wait")
            
            elif wait_time > 10:
                warnings.append(f"Строка {line_number}: Время ожидания {wait_time}s может быть слишком долгим")
                suggestions.append(f"Рассмотрите уменьшение времени ожидания до 3-5 секунд")
            
            # Контекстные рекомендации
            if context_command:
                recommended_time = self._get_recommended_wait_time(context_command)
                if recommended_time and abs(wait_time - recommended_time) > 1:
                    suggestions.append(f"Для команды '{context_command}' рекомендуется ожидание {recommended_time}s")
        
        # Проверка отсутствующих wait команд
        missing_waits = self._find_missing_waits(dsl_code)
        for missing in missing_waits:
            suggestions.append(f"Строка {missing['line']}: Рекомендуется добавить 'wait' после команды '{missing['command']}'")
        
        return warnings, suggestions
    
    def validate_command_sequence(self, dsl_code: str) -> List[str]:
        """Валидация логики последовательности команд"""
        warnings = []
        
        lines = self._get_command_lines(dsl_code)
        
        for i, line_info in enumerate(lines):
            command = line_info['command']
            line_number = line_info['line']
            
            # Проверка логических противоречий
            if i > 0:
                prev_command = lines[i-1]['command']
                
                # Противоречивые команды
                if self._are_conflicting_commands(prev_command, command):
                    warnings.append(f"Строка {line_number}: Команда '{command}' может конфликтовать с предыдущей '{prev_command}'")
            
            # Проверка команд, требующих предварительных действий
            prerequisites = self._get_command_prerequisites(command)
            if prerequisites:
                if not self._check_prerequisites_met(lines[:i], prerequisites):
                    warnings.append(f"Строка {line_number}: Команда '{command}' требует предварительного выполнения: {', '.join(prerequisites)}")
        
        return warnings
    
    def validate_web_resources(self, dsl_code: str, web_selectors: Dict[str, Any]) -> List[str]:
        """Валидация веб-ресурсов и селекторов"""
        warnings = []
        
        # Извлечение веб-команд
        web_commands = self._extract_web_commands(dsl_code)
        
        for cmd_info in web_commands:
            command = cmd_info['command']
            args = cmd_info['args']
            line_number = cmd_info['line']
            
            if command == 'navigate':
                # Проверка URL
                if args and not self._is_valid_url(args[0]):
                    warnings.append(f"Строка {line_number}: URL '{args[0]}' может быть недействительным")
            
            elif command == 'click_element':
                # Проверка селектора
                if args:
                    selector = args[0].strip('"')
                    if not self._is_valid_xpath(selector):
                        warnings.append(f"Строка {line_number}: XPath селектор может быть некорректным: {selector}")
        
        return warnings
    
    def validate_system_resources(self, dsl_code: str, system_apps: Dict[str, Any]) -> List[str]:
        """Валидация системных ресурсов"""
        warnings = []
        
        # Извлечение системных команд
        system_commands = self._extract_system_commands(dsl_code)
        
        for cmd_info in system_commands:
            command = cmd_info['command']
            args = cmd_info['args']
            line_number = cmd_info['line']
            
            if command in ['open_app', 'system_command']:
                if args:
                    app_or_cmd = args[0].strip('"')
                    
                    # Проверка системных команд
                    if command == 'system_command':
                        if not self._is_safe_system_command(app_or_cmd):
                            warnings.append(f"Строка {line_number}: Системная команда может быть небезопасной: {app_or_cmd}")
        
        return warnings
    
    def suggest_improvements(self, dsl_code: str) -> List[str]:
        """Предложения по улучшению DSL кода"""
        suggestions = []
        
        # Анализ структуры кода
        lines = self._get_command_lines(dsl_code)
        
        # Предложения по оптимизации
        if len(lines) > 20:
            suggestions.append("Макрос содержит много команд. Рассмотрите разбиение на несколько более простых макросов")
        
        # Проверка на повторяющиеся паттерны
        patterns = self._find_repetitive_patterns(dsl_code)
        for pattern in patterns:
            suggestions.append(f"Обнаружен повторяющийся паттерн: {pattern}. Рассмотрите использование циклов")
        
        # Предложения по добавлению комментариев
        if not self._has_sufficient_comments(dsl_code):
            suggestions.append("Добавьте комментарии для лучшего понимания логики макроса")
        
        # Предложения по обработке ошибок
        if not self._has_error_handling(dsl_code):
            suggestions.append("Рассмотрите добавление проверок и обработки возможных ошибок")
        
        return suggestions
    
    def _extract_apps(self, dsl_code: str) -> List[str]:
        """Извлечение приложений из DSL кода"""
        apps = []
        
        # Паттерны для поиска приложений
        patterns = [
            r'open_app\s+"([^"]+)"',
            r'open\s+([A-Za-z][A-Za-z0-9_]*)',
            r'system_command\s+"open\s+-a\s+([^"]+)"'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, dsl_code, re.IGNORECASE)
            apps.extend(matches)
        
        return list(set(apps))  # Убираем дубликаты
    
    def _is_app_installed(self, app_name: str) -> bool:
        """Проверка установки приложения"""
        try:
            # Проверка через mdfind (Spotlight database)
            result = subprocess.run(
                ['mdfind', f'kMDItemDisplayName == "{app_name}" || kMDItemFSName == "{app_name}.app"'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return True
            
            # Альтернативная проверка через system_profiler
            result = subprocess.run(
                ['system_profiler', 'SPApplicationsDataType'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return app_name.lower() in result.stdout.lower()
            
        except Exception as e:
            logger.warning(f"Не удалось проверить установку приложения {app_name}: {e}")
            return True  # Предполагаем, что установлено, если не можем проверить
    
    def _extract_waits(self, dsl_code: str) -> List[Dict[str, Any]]:
        """Извлечение команд wait с контекстом"""
        waits = []
        lines = dsl_code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('#'):
                continue
            
            wait_match = re.search(r'wait\s+(\d+(?:\.\d+)?)s?', line_stripped, re.IGNORECASE)
            if wait_match:
                wait_time = float(wait_match.group(1))
                
                # Ищем предыдущую команду для контекста
                context_command = None
                for j in range(i-2, -1, -1):  # Ищем назад
                    prev_line = lines[j].strip()
                    if prev_line and not prev_line.startswith('#'):
                        context_command = prev_line.split()[0] if prev_line.split() else None
                        break
                
                waits.append({
                    'time': wait_time,
                    'line': i,
                    'context_command': context_command
                })
        
        return waits
    
    def _get_recommended_wait_time(self, command: str) -> Optional[float]:
        """Получение рекомендуемого времени ожидания для команды"""
        recommendations = {
            'open': 3.0,
            'open_app': 3.0,
            'navigate': 3.0,
            'click_element': 1.0,
            'system_command': 2.0,
            'spotlight_search': 1.0
        }
        return recommendations.get(command.lower())
    
    def _find_missing_waits(self, dsl_code: str) -> List[Dict[str, Any]]:
        """Поиск команд, после которых отсутствует wait"""
        missing = []
        lines = dsl_code.split('\n')
        
        commands_needing_wait = {'open', 'open_app', 'navigate', 'click_element', 'system_command'}
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('#'):
                continue
            
            command = line_stripped.split()[0].lower() if line_stripped.split() else ""
            
            if command in commands_needing_wait:
                # Проверяем следующую строку
                next_line_has_wait = False
                for j in range(i+1, min(i+3, len(lines))):  # Проверяем следующие 2 строки
                    next_line = lines[j].strip()
                    if next_line and not next_line.startswith('#'):
                        if next_line.lower().startswith('wait'):
                            next_line_has_wait = True
                        break
                
                if not next_line_has_wait:
                    missing.append({
                        'command': command,
                        'line': i + 1
                    })
        
        return missing
    
    def _get_command_lines(self, dsl_code: str) -> List[Dict[str, Any]]:
        """Получение информации о командах в коде"""
        command_lines = []
        lines = dsl_code.split('\n')
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith('#'):
                continue
            
            parts = line_stripped.split()
            if parts:
                command_lines.append({
                    'command': parts[0].lower(),
                    'args': parts[1:],
                    'line': i,
                    'full_line': line_stripped
                })
        
        return command_lines
    
    def _are_conflicting_commands(self, cmd1: str, cmd2: str) -> bool:
        """Проверка конфликтующих команд"""
        conflicts = {
            ('navigate', 'open_app'),  # Переход на сайт после открытия приложения
            ('close_tab', 'click_element'),  # Клик после закрытия вкладки
        }
        
        return (cmd1, cmd2) in conflicts or (cmd2, cmd1) in conflicts
    
    def _get_command_prerequisites(self, command: str) -> List[str]:
        """Получение предварительных требований для команды"""
        prerequisites = {
            'click_element': ['navigate', 'open_app'],
            'fill_field': ['navigate', 'open_app'],
            'close_tab': ['navigate']
        }
        return prerequisites.get(command, [])
    
    def _check_prerequisites_met(self, previous_commands: List[Dict[str, Any]], prerequisites: List[str]) -> bool:
        """Проверка выполнения предварительных требований"""
        executed_commands = {cmd['command'] for cmd in previous_commands}
        return any(prereq in executed_commands for prereq in prerequisites)
    
    def _extract_web_commands(self, dsl_code: str) -> List[Dict[str, Any]]:
        """Извлечение веб-команд"""
        web_commands = ['navigate', 'click_element', 'fill_field', 'wait_for_element', 'scroll_to', 'hover_element']
        commands = []
        
        for cmd_info in self._get_command_lines(dsl_code):
            if cmd_info['command'] in web_commands:
                commands.append(cmd_info)
        
        return commands
    
    def _extract_system_commands(self, dsl_code: str) -> List[Dict[str, Any]]:
        """Извлечение системных команд"""
        system_commands = ['open_app', 'system_command', 'spotlight_search']
        commands = []
        
        for cmd_info in self._get_command_lines(dsl_code):
            if cmd_info['command'] in system_commands:
                commands.append(cmd_info)
        
        return commands
    
    def _is_valid_url(self, url: str) -> bool:
        """Проверка валидности URL"""
        url = url.strip('"')
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None
    
    def _is_valid_xpath(self, xpath: str) -> bool:
        """Базовая проверка XPath селектора"""
        if not xpath.startswith('//'):
            return False
        
        # Проверка на базовые XPath паттерны
        invalid_patterns = ['///', '//..', '//[', '//]']
        return not any(pattern in xpath for pattern in invalid_patterns)
    
    def _is_safe_system_command(self, command: str) -> bool:
        """Проверка безопасности системной команды"""
        dangerous_commands = ['rm', 'del', 'format', 'sudo', 'chmod 777', 'dd if=']
        command_lower = command.lower()
        return not any(dangerous in command_lower for dangerous in dangerous_commands)
    
    def _find_repetitive_patterns(self, dsl_code: str) -> List[str]:
        """Поиск повторяющихся паттернов в коде"""
        patterns = []
        lines = [line.strip() for line in dsl_code.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        # Простой поиск повторяющихся последовательностей
        for i in range(len(lines) - 2):
            for j in range(i + 2, len(lines) - 1):
                if lines[i] == lines[j] and lines[i+1] == lines[j+1]:
                    pattern = f"{lines[i]} -> {lines[i+1]}"
                    if pattern not in patterns:
                        patterns.append(pattern)
        
        return patterns
    
    def _has_sufficient_comments(self, dsl_code: str) -> bool:
        """Проверка достаточности комментариев"""
        lines = dsl_code.split('\n')
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
        
        if code_lines == 0:
            return True
        
        comment_ratio = comment_lines / code_lines
        return comment_ratio >= 0.2  # Минимум 20% комментариев
    
    def _has_error_handling(self, dsl_code: str) -> bool:
        """Проверка наличия обработки ошибок"""
        error_handling_keywords = ['if', 'try', 'catch', 'error', 'fail', 'retry']
        dsl_lower = dsl_code.lower()
        return any(keyword in dsl_lower for keyword in error_handling_keywords)
