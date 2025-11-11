#!/usr/bin/env python3
"""
atlas_dsl_parser.py
Парсер DSL (Domain Specific Language) для Macro AI
Конвертирует .atlas файлы в YAML последовательности

Синтаксис DSL:
    open ChromeApp
    click ChromeNewTab
    type "text"
    press enter
    wait 3s
    scroll down
    repeat 10:
        click Button
        wait 1s
"""

import re
import yaml
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class AtlasDSLParser:
    """Парсер DSL для Macro AI"""
    
    def __init__(self, templates_base_path: str = "templates", dom_selectors_path: str = "dom_selectors"):
        self.templates_base_path = templates_base_path
        self.dom_selectors_path = dom_selectors_path
        self.template_map = self._build_template_map()
        self.dom_selectors = self._load_dom_selectors()
        self.current_indent = 0
        self.indent_stack = []
        
        # Загрузка DSL переменных
        self.variables = self._load_dsl_variables()
        if self.variables:
            print(f"✅ Загружено {len(self.variables)} DSL переменных")
        
        # НОВОЕ: Поддержка системных команд
        self.system_commands_whitelist = {
            'open_app', 'close_app', 'focus_window', 
            'take_screenshot', 'copy_to_clipboard', 'read_clipboard',
            'list_processes', 'switch_desktop', 'get_current_app'
        }
    
    def _build_template_map(self) -> Dict[str, str]:
        """
        Строит карту коротких имен → полные пути к шаблонам
        Читает structure.txt файлы из папок
        """
        template_map = {}
        
        # Сканируем templates/ рекурсивно
        templates_dir = Path(self.templates_base_path)
        if not templates_dir.exists():
            return template_map
        
        # Находим все .png файлы
        for png_file in templates_dir.rglob("*.png"):
            # Полный путь относительно templates/
            full_path = str(png_file)
            
            # Короткое имя (без расширения и путей)
            short_name = png_file.stem
            
            # Убираем префиксы типа "Chrome-TikTok-"
            clean_name = short_name
            for prefix in ["Chrome-TikTok-", "Chrome-YouTube-", "Chrome-", "Atlas-"]:
                if clean_name.startswith(prefix):
                    clean_name = clean_name[len(prefix):]
            
            # Убираем суффиксы типа "-btn"
            clean_name = clean_name.replace("-btn", "").replace("_btn", "")
            
            # Сохраняем оба варианта
            template_map[short_name] = full_path
            template_map[clean_name] = full_path
            
            # Также сохраняем с заменой дефисов на подчеркивания
            template_map[clean_name.replace("-", "_")] = full_path
            
        return template_map
    
    def _load_dom_selectors(self) -> Dict[str, Dict]:
        """
        Загружает DOM селекторы из dom_selectors/*/selectors.json
        
        Returns:
            Dict с именами селекторов и их данными
        """
        dom_map = {}
        
        dom_dir = Path(self.dom_selectors_path)
        if not dom_dir.exists():
            return dom_map
        
        # Находим все selectors.json файлы
        for json_file in dom_dir.rglob("selectors.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    selectors = json.load(f)
                
                # Добавляем все селекторы в карту
                for name, data in selectors.items():
                    dom_map[name] = data
                    
                    # Также добавляем короткие имена
                    if name.startswith('Chrome-'):
                        short_name = name[7:]  # Убираем "Chrome-"
                        dom_map[short_name] = data
                    
            except Exception as e:
                print(f"⚠️  Ошибка загрузки {json_file}: {e}")
        
        if dom_map:
            print(f"✅ Загружено {len(dom_map)} DOM селекторов")
        
        return dom_map
    
    def _load_dsl_variables(self) -> Dict[str, Dict[str, str]]:
        """
        Загружает DSL переменные из templates/DSL_VARIABLES.txt
        
        Returns:
            Dict с именами переменных и их кодом:
            {
                'ChromeOpen': {'code': 'open ChromeApp\nwait 2s\n...', 'params': []},
                'TikTokComment': {'code': 'click Comment\n...', 'params': ['comment_text']}
            }
        """
        variables = {}
        
        # Пути к файлам переменных
        var_files = [
            Path(self.templates_base_path) / 'DSL_VARIABLES.txt',
            Path('dsl_references') / 'USER_VARIABLES.txt'
        ]
        
        for var_file in var_files:
            if not var_file.exists():
                continue
            
            try:
                with open(var_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Парсинг переменных
                # Формат: ${VarName}
                #         ----...----
                #         код
                #         код
                
                current_var = None
                current_code = []
                in_code_section = False
                
                for line in content.split('\n'):
                    # Начало новой переменной: ${...}
                    if line.strip().startswith('${') and line.strip().endswith('}'):
                        # Сохраняем предыдущую переменную
                        if current_var and current_code:
                            code_text = '\n'.join(current_code).strip()
                            # Извлекаем параметры из кода (например {site_url})
                            params = re.findall(r'\{(\w+)\}', code_text)
                            variables[current_var] = {
                                'code': code_text,
                                'params': list(set(params))
                            }
                        
                        # Начинаем новую переменную
                        var_name = line.strip()[2:-1]  # Убираем ${ и }
                        current_var = var_name
                        current_code = []
                        in_code_section = False
                    
                    # Разделитель (----)
                    elif line.strip().startswith('---'):
                        in_code_section = True
                    
                    # Секция ИСПОЛЬЗОВАНИЕ или пустая строка после кода
                    elif line.strip().startswith('ИСПОЛЬЗОВАНИЕ:') or \
                         line.strip().startswith('================'):
                        in_code_section = False
                    
                    # Код переменной
                    elif in_code_section and current_var:
                        # Пропускаем комментарии и пустые строки в начале
                        if line.strip() and not line.strip().startswith('#'):
                            current_code.append(line)
                        elif current_code:  # Добавляем пустые строки только если уже есть код
                            current_code.append(line)
                
                # Сохраняем последнюю переменную
                if current_var and current_code:
                    code_text = '\n'.join(current_code).strip()
                    params = re.findall(r'\{(\w+)\}', code_text)
                    variables[current_var] = {
                        'code': code_text,
                        'params': list(set(params))
                    }
                
            except Exception as e:
                print(f"⚠️  Ошибка загрузки переменных из {var_file}: {e}")
        
        return variables
    
    def _expand_variable(self, var_name: str, params: Dict[str, str] = None) -> List[str]:
        """
        Разворачивает переменную в список строк DSL кода
        
        Args:
            var_name: Имя переменной (без ${})
            params: Словарь параметров для подстановки
        
        Returns:
            Список строк DSL кода
        """
        if var_name not in self.variables:
            print(f"⚠️  Переменная ${{{var_name}}} не найдена")
            return []
        
        var_data = self.variables[var_name]
        code = var_data['code']
        
        # Подстановка параметров
        if params:
            for param_name, param_value in params.items():
                code = code.replace(f'{{{param_name}}}', param_value)
        
        # Проверка на неподставленные параметры
        missing_params = re.findall(r'\{(\w+)\}', code)
        if missing_params:
            print(f"⚠️  Переменная ${{{var_name}}} требует параметры: {', '.join(missing_params)}")
        
        return code.split('\n')
    
    def _parse_variable_line(self, line: str) -> Optional[tuple]:
        """
        Парсит строку с переменной: ${VarName} или ${VarName:param1,param2}
        
        Returns:
            (var_name, params_dict) или None
        """
        line = line.strip()
        
        # Формат: ${VarName}
        simple_match = re.match(r'^\$\{(\w+)\}$', line)
        if simple_match:
            return (simple_match.group(1), {})
        
        # Формат: ${VarName:value}
        single_param_match = re.match(r'^\$\{(\w+):(.+)\}$', line)
        if single_param_match:
            var_name = single_param_match.group(1)
            param_value = single_param_match.group(2).strip()
            
            # Определяем имя параметра из определения переменной
            if var_name in self.variables:
                var_params = self.variables[var_name]['params']
                if var_params:
                    # Используем первый параметр
                    return (var_name, {var_params[0]: param_value})
            
            return (var_name, {'value': param_value})
        
        return None
    
    def _resolve_template(self, name: str) -> Optional[str]:
        """Находит полный путь к шаблону по короткому имени"""
        # Прямое совпадение
        if name in self.template_map:
            return self.template_map[name]
        
        # Поиск без учета регистра
        name_lower = name.lower()
        for key, value in self.template_map.items():
            if key.lower() == name_lower:
                return value
        
        # Если не найдено, возвращаем как есть (возможно это полный путь)
        return f"{self.templates_base_path}/{name}.png"
    
    def _parse_duration(self, duration_str: str) -> float:
        """Парсит длительность: '3s', '1.5s', '500ms'"""
        duration_str = duration_str.strip().lower()
        
        if duration_str.endswith('ms'):
            return float(duration_str[:-2]) / 1000
        elif duration_str.endswith('s'):
            return float(duration_str[:-1])
        else:
            return float(duration_str)
    
    def _parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Парсит одну строку DSL"""
        line = line.strip()
        
        # Пустая строка или комментарий
        if not line or line.startswith('#'):
            return None
        
        # ПЕРЕМЕННАЯ: ${VarName} или ${VarName:params}
        if line.startswith('${'):
            var_data = self._parse_variable_line(line)
            if var_data:
                var_name, params = var_data
                # Возвращаем специальный маркер для развертывания
                return {
                    'action': 'expand_variable',
                    'variable': var_name,
                    'params': params
                }
        
        # НОВОЕ: @SYSTEM команды
        if line.startswith('@system '):
            return self._parse_system_command(line)
        
        # OPEN - запуск приложения
        if line.startswith('open '):
            rest = line[5:].strip()
            # Парсим параметры (например: open ChromeApp threshold=0.7)
            parts = rest.split()
            template_name = parts[0]
            
            # Извлекаем параметры
            params = {}
            for part in parts[1:]:
                if '=' in part:
                    key, value = part.split('=', 1)
                    try:
                        params[key] = float(value)
                    except ValueError:
                        params[key] = value
            
            template_path = self._resolve_template(template_name)
            result = {
                'action': 'click',
                'template': template_path,
                'clicks': 1,
                'wait_for_appear': True,
                'timeout': 3.0,
                'description': f'Запуск {template_name}'
            }
            
            # Добавляем параметры если есть
            if 'threshold' in params:
                result['threshold'] = params['threshold']
            if 'timeout' in params:
                result['timeout'] = params['timeout']
            
            return result
        
        # CLICK - клик по кнопке
        if line.startswith('click '):
            rest = line[6:].strip()
            
            # Проверка на координаты: click (500, 300)
            coord_match = re.match(r'\((\d+),\s*(\d+)\)', rest)
            if coord_match:
                x, y = coord_match.groups()
                return {
                    'action': 'click',
                    'position': 'absolute',
                    'x': int(x),
                    'y': int(y),
                    'clicks': 1,
                    'description': f'Клик в ({x}, {y})'
                }
            
            # Парсим параметры (например: click Button threshold=0.8)
            parts = rest.split()
            template_name = parts[0]
            
            # Извлекаем параметры
            params = {}
            for part in parts[1:]:
                if '=' in part:
                    key, value = part.split('=', 1)
                    try:
                        params[key] = float(value)
                    except ValueError:
                        params[key] = value
            
            # Проверка на DOM селектор (case-insensitive)
            dom_key = None
            if template_name in self.dom_selectors:
                dom_key = template_name
            else:
                # Поиск без учета регистра
                template_lower = template_name.lower()
                for key in self.dom_selectors.keys():
                    if key.lower() == template_lower:
                        dom_key = key
                        break
            
            if dom_key:
                dom_data = self.dom_selectors[dom_key]
                return {
                    'action': 'selenium_click',
                    'selector': dom_data['selector'],
                    'index': 0,
                    'description': f'Клик по {template_name} (DOM: {dom_data["selector"]})'
                }
            
            # Fallback на Vision template
            template_path = self._resolve_template(template_name)
            result = {
                'action': 'click',
                'template': template_path,
                'clicks': 1,
                'description': f'Клик по {template_name}'
            }
            
            # Добавляем параметры если есть
            if 'threshold' in params:
                result['threshold'] = params['threshold']
            if 'timeout' in params:
                result['timeout'] = params['timeout']
            if 'index' in params:
                result['index'] = int(params['index'])
            
            return result
        
        # DOUBLE_CLICK - двойной клик
        if line.startswith('double_click ') or line.startswith('dclick '):
            prefix_len = 13 if line.startswith('double_click') else 7
            template_name = line[prefix_len:].strip()
            template_path = self._resolve_template(template_name)
            return {
                'action': 'click',
                'template': template_path,
                'clicks': 2,
                'interval': 0.3,
                'description': f'Двойной клик по {template_name}'
            }
        
        # TYPE - ввод текста
        if line.startswith('type '):
            text = line[5:].strip()
            # Убираем кавычки если есть
            if (text.startswith('"') and text.endswith('"')) or \
               (text.startswith("'") and text.endswith("'")):
                text = text[1:-1]
            return {
                'action': 'type',
                'text': text,
                'description': f'Ввод текста'
            }
        
        # PRESS - нажатие клавиши
        if line.startswith('press '):
            key = line[6:].strip().lower()
            return {
                'action': 'key',
                'key': key,
                'description': f'Нажатие {key}'
            }
        
        # HOTKEY - комбинация клавиш
        if line.startswith('hotkey '):
            keys_str = line[7:].strip()
            keys = [k.strip() for k in keys_str.split('+')]
            return {
                'action': 'hotkey',
                'keys': keys,
                'description': f'Комбинация {"+".join(keys)}'
            }
        
        # WAIT - пауза
        if line.startswith('wait '):
            duration_str = line[5:].strip()
            duration = self._parse_duration(duration_str)
            return {
                'action': 'wait',
                'duration': duration,
                'description': f'Пауза {duration}с'
            }
        
        # SCROLL - скролл
        if line.startswith('scroll '):
            direction = line[7:].strip().lower()
            
            # Парсим: scroll down 10
            parts = direction.split()
            direction = parts[0]
            amount = int(parts[1]) if len(parts) > 1 else 5
            
            return {
                'action': 'scroll',
                'direction': direction,
                'amount': amount,
                'clicks': 1,
                'description': f'Скролл {direction}'
            }
        
        # REPEAT - повторение (обрабатывается отдельно)
        if line.startswith('repeat '):
            match = re.match(r'repeat\s+(\d+):', line)
            if match:
                times = int(match.group(1))
                return {
                    'action': 'repeat',
                    'times': times,
                    'steps': [],
                    'description': f'Повторить {times} раз'
                }
        
        # END - конец блока repeat
        if line == 'end':
            return {
                'action': 'end',
                'description': 'Конец блока'
            }
        
        # SELENIUM_INIT - инициализация Selenium
        if line.startswith('selenium_init'):
            # Парсим: selenium_init url=https://example.com
            url = None
            if 'url=' in line:
                url = line.split('url=')[1].strip()
            return {
                'action': 'selenium_init',
                'url': url,
                'description': 'Selenium init'
            }
        
        # SELENIUM_CONNECT - подключение к существующему браузеру
        if line.startswith('selenium_connect'):
            return {
                'action': 'selenium_connect',
                'description': 'Selenium connect'
            }
        
        # SELENIUM_CLOSE - закрытие Selenium
        if line.startswith('selenium_close'):
            return {
                'action': 'selenium_close',
                'description': 'Selenium close'
            }
        
        # Неизвестная команда
        return None
    
    def parse(self, dsl_content: str) -> Dict[str, Any]:
        """
        Парсит DSL контент и возвращает YAML структуру
        
        Args:
            dsl_content: Содержимое .atlas файла
        
        Returns:
            Dict с последовательностью в формате YAML
        """
        lines = dsl_content.split('\n')
        steps = []
        block_stack = []  # Стек для вложенных блоков (repeat, try)
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            line = line.rstrip()
            
            # Пустая строка или комментарий
            if not line.strip() or line.strip().startswith('#'):
                continue
            
            # Определяем уровень отступа
            indent = len(line) - len(line.lstrip())
            
            # Если отступ уменьшился, выходим из блоков
            while block_stack and indent <= block_stack[-1]['indent']:
                block_stack.pop()
            
            # Парсим строку
            step = self._parse_line(line)
            
            if step:
                action = step['action']
                
                # РАЗВЕРТЫВАНИЕ ПЕРЕМЕННОЙ
                if action == 'expand_variable':
                    var_name = step['variable']
                    var_params = step['params']
                    
                    # Разворачиваем переменную в строки кода
                    expanded_lines = self._expand_variable(var_name, var_params)
                    
                    if expanded_lines:
                        print(f"🔄 Развертывание ${{{var_name}}} → {len(expanded_lines)} строк")
                        
                        # Рекурсивно парсим каждую строку развернутого кода
                        for exp_line in expanded_lines:
                            exp_step = self._parse_line(exp_line)
                            if exp_step:
                                # Добавляем развернутые шаги
                                if block_stack:
                                    self._add_to_current_block(block_stack[-1], exp_step)
                                else:
                                    steps.append(exp_step)
                    continue
                
                # TRY блок
                if action == 'try':
                    step['indent'] = indent
                    step['in_catch'] = False
                    
                    # Добавляем в текущий контекст
                    if block_stack:
                        self._add_to_current_block(block_stack[-1], step)
                    else:
                        steps.append(step)
                    
                    # Добавляем в стек
                    block_stack.append({
                        'indent': indent,
                        'step': step,
                        'type': 'try'
                    })
                
                # CATCH блок
                elif action == 'catch':
                    if block_stack and block_stack[-1]['type'] == 'try':
                        block_stack[-1]['step']['in_catch'] = True
                
                # END блок
                elif action == 'end':
                    if block_stack:
                        block_stack.pop()
                
                # REPEAT блок
                elif action == 'repeat':
                    step['indent'] = indent
                    
                    # Добавляем в текущий контекст
                    if block_stack:
                        self._add_to_current_block(block_stack[-1], step)
                    else:
                        steps.append(step)
                    
                    # Добавляем в стек
                    block_stack.append({
                        'indent': indent,
                        'step': step,
                        'type': 'repeat'
                    })
                
                # Обычный шаг
                else:
                    if block_stack:
                        self._add_to_current_block(block_stack[-1], step)
                    else:
                        steps.append(step)
        
        return {'steps': steps}
    
    def _add_to_current_block(self, block, step):
        """Добавляет шаг в текущий блок (try/catch или repeat)"""
        if block['type'] == 'try':
            if block['step']['in_catch']:
                block['step']['catch_steps'].append(step)
            else:
                block['step']['try_steps'].append(step)
        elif block['type'] == 'repeat':
            block['step']['steps'].append(step)
    
    def parse_file(self, filepath: str) -> Dict[str, Any]:
        """Парсит .atlas файл"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = self.parse(content)
        
        # Добавляем метаданные из имени файла
        filename = Path(filepath).stem
        result['name'] = filename.replace('_', ' ').title()
        
        return result
    
    def _parse_system_command(self, line: str) -> Dict[str, Any]:
        """Парсинг @system команд"""
        # Убираем префикс '@system '
        command_part = line[8:].strip()
        
        # Парсим команду и аргументы
        parts = command_part.split(' ', 1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        
        # Убираем кавычки из аргументов если есть
        if args.startswith('"') and args.endswith('"'):
            args = args[1:-1]
        
        # Проверяем whitelist
        if command not in self.system_commands_whitelist:
            raise ValueError(f"Системная команда '{command}' не разрешена")
        
        return {
            'action': 'system_command',
            'command': command,
            'args': args,
            'hidden': True,  # Не показывать в UI
            'description': f'Системная команда: {command} {args}'
        }
    
    def is_system_command(self, parsed_step: Dict[str, Any]) -> bool:
        """Проверка, является ли команда системной"""
        return parsed_step.get('action') == 'system_command'
    
    def convert_to_yaml(self, dsl_content: str) -> str:
        """Конвертирует DSL в YAML строку"""
        parsed = self.parse(dsl_content)
        return yaml.dump(parsed, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    def convert_file_to_yaml(self, dsl_filepath: str, yaml_filepath: str):
        """Конвертирует .atlas файл в .yaml"""
        parsed = self.parse_file(dsl_filepath)
        
        with open(yaml_filepath, 'w', encoding='utf-8') as f:
            yaml.dump({'sequences': {Path(dsl_filepath).stem: parsed}}, 
                     f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Конвертировано: {dsl_filepath} → {yaml_filepath}")


def main():
    """Тестирование парсера"""
    import sys
    
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python3 atlas_dsl_parser.py <file.atlas>")
        print("  python3 atlas_dsl_parser.py <file.atlas> <output.yaml>")
        return
    
    parser = AtlasDSLParser()
    
    dsl_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        # Конвертация в файл
        yaml_file = sys.argv[2]
        parser.convert_file_to_yaml(dsl_file, yaml_file)
    else:
        # Вывод в консоль
        parsed = parser.parse_file(dsl_file)
        print(yaml.dump({'sequences': {Path(dsl_file).stem: parsed}}, 
                       allow_unicode=True, default_flow_style=False, sort_keys=False))


if __name__ == "__main__":
    main()
