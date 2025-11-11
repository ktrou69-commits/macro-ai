# 🔧 Этап 2: Системные команды (1 неделя)

**Время выполнения:** 1 неделя  
**Приоритет:** Высокий  
**Зависимости:** Этап 1 должен быть завершен

## 🎯 Цели этапа

1. Реализовать macOS Accessibility API команды
2. Создать полнофункциональный SystemOrchestrator
3. Интегрировать системные команды с DSL парсером
4. Протестировать все системные операции

## 📋 Системные команды для реализации

### Базовые команды приложений
- `@system open_app "AppName"` - Открыть приложение
- `@system close_app "AppName"` - Закрыть приложение
- `@system focus_window "WindowTitle"` - Фокус на окно
- `@system list_processes` - Список запущенных процессов

### Команды управления системой
- `@system take_screenshot [path]` - Сделать скриншот
- `@system copy_to_clipboard "text"` - Копировать в буфер
- `@system read_clipboard` - Прочитать из буфера
- `@system switch_desktop N` - Переключить рабочий стол

### Команды поиска и навигации
- `@system find_window "pattern"` - Найти окно по паттерну
- `@system get_window_info` - Информация о текущем окне
- `@system minimize_window` - Свернуть окно
- `@system maximize_window` - Развернуть окно

## 🛠️ Детальная реализация

### Шаг 2.1: Создать macos_commands.py

**Файл:** `src/system/macos_commands.py`

```python
#!/usr/bin/env python3
"""
macos_commands.py
Системные команды для macOS через Accessibility API
"""

import subprocess
import time
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

try:
    import Quartz
    import AppKit
    from AppKit import NSWorkspace, NSApplication
    from Cocoa import *
    MACOS_APIS_AVAILABLE = True
except ImportError:
    MACOS_APIS_AVAILABLE = False
    print("⚠️ macOS APIs недоступны. Используется fallback режим.")


class MacOSCommands:
    """Системные команды для macOS"""
    
    def __init__(self):
        self.workspace = NSWorkspace.sharedWorkspace() if MACOS_APIS_AVAILABLE else None
        
    def open_app(self, app_name: str) -> Dict[str, Any]:
        """Открыть приложение"""
        try:
            # Метод 1: Через NSWorkspace (предпочтительный)
            if self.workspace:
                success = self.workspace.launchApplication_(app_name)
                if success:
                    return {
                        'success': True,
                        'method': 'NSWorkspace',
                        'app_name': app_name,
                        'message': f'Приложение {app_name} запущено'
                    }
            
            # Метод 2: Через команду open (fallback)
            result = subprocess.run(['open', '-a', app_name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'method': 'open_command',
                    'app_name': app_name,
                    'message': f'Приложение {app_name} запущено через open'
                }
            else:
                return {
                    'success': False,
                    'error': f'Не удалось запустить {app_name}: {result.stderr}',
                    'app_name': app_name
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка запуска {app_name}: {str(e)}',
                'app_name': app_name
            }
    
    def close_app(self, app_name: str) -> Dict[str, Any]:
        """Закрыть приложение"""
        try:
            # Получаем список процессов
            processes = self.list_processes()
            target_pid = None
            
            for proc in processes['processes']:
                if app_name.lower() in proc['name'].lower():
                    target_pid = proc['pid']
                    break
            
            if not target_pid:
                return {
                    'success': False,
                    'error': f'Приложение {app_name} не найдено среди запущенных',
                    'app_name': app_name
                }
            
            # Мягкое завершение через SIGTERM
            result = subprocess.run(['kill', str(target_pid)], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'app_name': app_name,
                    'pid': target_pid,
                    'message': f'Приложение {app_name} (PID: {target_pid}) закрыто'
                }
            else:
                return {
                    'success': False,
                    'error': f'Не удалось закрыть {app_name}: {result.stderr}',
                    'app_name': app_name
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка закрытия {app_name}: {str(e)}',
                'app_name': app_name
            }
    
    def focus_window(self, window_title: str) -> Dict[str, Any]:
        """Фокус на окно по заголовку"""
        try:
            # AppleScript для фокуса на окно
            script = f'''
            tell application "System Events"
                set windowFound to false
                repeat with theApp in (every application process whose visible is true)
                    repeat with theWindow in (every window of theApp)
                        if name of theWindow contains "{window_title}" then
                            set frontmost of theApp to true
                            perform action "AXRaise" of theWindow
                            set windowFound to true
                            exit repeat
                        end if
                    end repeat
                    if windowFound then exit repeat
                end repeat
                return windowFound
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and 'true' in result.stdout:
                return {
                    'success': True,
                    'window_title': window_title,
                    'message': f'Фокус установлен на окно: {window_title}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Окно с заголовком "{window_title}" не найдено',
                    'window_title': window_title
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка фокуса на окно {window_title}: {str(e)}',
                'window_title': window_title
            }
    
    def list_processes(self) -> Dict[str, Any]:
        """Список запущенных процессов"""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'Ошибка получения списка процессов: {result.stderr}'
                }
            
            processes = []
            lines = result.stdout.strip().split('\n')[1:]  # Пропускаем заголовок
            
            for line in lines:
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    processes.append({
                        'user': parts[0],
                        'pid': int(parts[1]),
                        'cpu': float(parts[2]),
                        'memory': float(parts[3]),
                        'name': parts[10]
                    })
            
            return {
                'success': True,
                'processes': processes,
                'count': len(processes)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения процессов: {str(e)}'
            }
    
    def take_screenshot(self, path: str = None) -> Dict[str, Any]:
        """Сделать скриншот"""
        try:
            if not path:
                timestamp = int(time.time())
                path = f"/tmp/screenshot_{timestamp}.png"
            
            # Создаем директорию если не существует
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            result = subprocess.run(['screencapture', path], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and Path(path).exists():
                return {
                    'success': True,
                    'path': path,
                    'size': Path(path).stat().st_size,
                    'message': f'Скриншот сохранен: {path}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Не удалось создать скриншот: {result.stderr}',
                    'path': path
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка создания скриншота: {str(e)}',
                'path': path
            }
    
    def copy_to_clipboard(self, text: str) -> Dict[str, Any]:
        """Копировать текст в буфер обмена"""
        try:
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            
            if process.returncode == 0:
                return {
                    'success': True,
                    'text': text,
                    'length': len(text),
                    'message': f'Текст скопирован в буфер ({len(text)} символов)'
                }
            else:
                return {
                    'success': False,
                    'error': 'Не удалось скопировать в буфер',
                    'text': text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка копирования в буфер: {str(e)}',
                'text': text
            }
    
    def read_clipboard(self) -> Dict[str, Any]:
        """Прочитать текст из буфера обмена"""
        try:
            result = subprocess.run(['pbpaste'], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'text': result.stdout,
                    'length': len(result.stdout),
                    'message': f'Прочитано из буфера ({len(result.stdout)} символов)'
                }
            else:
                return {
                    'success': False,
                    'error': f'Не удалось прочитать буфер: {result.stderr}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка чтения буфера: {str(e)}'
            }
    
    def switch_desktop(self, desktop_num: int) -> Dict[str, Any]:
        """Переключить рабочий стол"""
        try:
            # AppleScript для переключения рабочего стола
            script = f'''
            tell application "System Events"
                key code {117 + desktop_num} using control down
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'desktop': desktop_num,
                    'message': f'Переключен на рабочий стол {desktop_num}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Не удалось переключить рабочий стол: {result.stderr}',
                    'desktop': desktop_num
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка переключения рабочего стола: {str(e)}',
                'desktop': desktop_num
            }
    
    def get_current_app(self) -> Dict[str, Any]:
        """Получить информацию о текущем активном приложении"""
        try:
            if self.workspace:
                active_app = self.workspace.activeApplication()
                return {
                    'success': True,
                    'app_name': active_app.get('NSApplicationName', 'Unknown'),
                    'bundle_id': active_app.get('NSApplicationBundleIdentifier', 'Unknown'),
                    'pid': active_app.get('NSApplicationProcessIdentifier', 0)
                }
            else:
                # Fallback через AppleScript
                script = '''
                tell application "System Events"
                    set frontApp to name of first application process whose frontmost is true
                    return frontApp
                end tell
                '''
                
                result = subprocess.run(['osascript', '-e', script], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    return {
                        'success': True,
                        'app_name': result.stdout.strip(),
                        'method': 'applescript'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Не удалось получить активное приложение: {result.stderr}'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения активного приложения: {str(e)}'
            }


# Глобальный экземпляр команд macOS
macos_commands = MacOSCommands()
```

### Шаг 2.2: Обновить system_orchestrator.py

**Обновить файл:** `src/system/system_orchestrator.py`

```python
#!/usr/bin/env python3
"""
system_orchestrator.py (обновленная версия)
Полнофункциональный оркестратор системных команд
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import re

from .macos_commands import macos_commands


class ExecutionStrategy(Enum):
    """Стратегии выполнения команд"""
    DOM = "dom"
    SYSTEM = "system"
    CV = "cv"


class SystemOrchestrator:
    """Полнофункциональный оркестратор системных команд"""
    
    def __init__(self):
        self.macos_commands = macos_commands
        
        # Маппинг команд на методы
        self.command_mapping = {
            'open_app': self.macos_commands.open_app,
            'close_app': self.macos_commands.close_app,
            'focus_window': self.macos_commands.focus_window,
            'list_processes': self.macos_commands.list_processes,
            'take_screenshot': self.macos_commands.take_screenshot,
            'copy_to_clipboard': self.macos_commands.copy_to_clipboard,
            'read_clipboard': self.macos_commands.read_clipboard,
            'switch_desktop': self.macos_commands.switch_desktop,
            'get_current_app': self.macos_commands.get_current_app
        }
        
        self.web_contexts = {
            'chrome', 'safari', 'firefox', 'browser', 'webkit'
        }
    
    def execute_system_command(self, command: str, args: str = "") -> Dict[str, Any]:
        """Выполнение системной команды"""
        try:
            # Проверяем, есть ли команда в маппинге
            if command not in self.command_mapping:
                return {
                    'success': False,
                    'error': f'Неизвестная системная команда: {command}',
                    'available_commands': list(self.command_mapping.keys())
                }
            
            # Парсим аргументы
            parsed_args = self._parse_command_args(args)
            
            # Выполняем команду
            method = self.command_mapping[command]
            
            # Вызываем метод с правильными аргументами
            if command in ['open_app', 'close_app', 'focus_window']:
                if not parsed_args:
                    return {
                        'success': False,
                        'error': f'Команда {command} требует аргумент (имя приложения/окна)'
                    }
                result = method(parsed_args[0])
                
            elif command == 'copy_to_clipboard':
                if not parsed_args:
                    return {
                        'success': False,
                        'error': 'Команда copy_to_clipboard требует текст для копирования'
                    }
                result = method(parsed_args[0])
                
            elif command == 'take_screenshot':
                path = parsed_args[0] if parsed_args else None
                result = method(path)
                
            elif command == 'switch_desktop':
                if not parsed_args:
                    return {
                        'success': False,
                        'error': 'Команда switch_desktop требует номер рабочего стола'
                    }
                try:
                    desktop_num = int(parsed_args[0])
                    result = method(desktop_num)
                except ValueError:
                    return {
                        'success': False,
                        'error': f'Неверный номер рабочего стола: {parsed_args[0]}'
                    }
                    
            else:
                # Команды без аргументов
                result = method()
            
            # Добавляем метаинформацию
            result['command'] = command
            result['args'] = args
            result['execution_time'] = self._get_current_timestamp()
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка выполнения команды {command}: {str(e)}',
                'command': command,
                'args': args
            }
    
    def _parse_command_args(self, args_string: str) -> List[str]:
        """Парсинг аргументов команды"""
        if not args_string.strip():
            return []
        
        # Простой парсер для строк в кавычках и без
        args = []
        current_arg = ""
        in_quotes = False
        
        for char in args_string:
            if char == '"' and not in_quotes:
                in_quotes = True
            elif char == '"' and in_quotes:
                in_quotes = False
                if current_arg:
                    args.append(current_arg)
                    current_arg = ""
            elif char == ' ' and not in_quotes:
                if current_arg:
                    args.append(current_arg)
                    current_arg = ""
            else:
                current_arg += char
        
        if current_arg:
            args.append(current_arg)
            
        return args
    
    def choose_execution_strategy(self, command: Dict[str, Any], context: Dict[str, Any] = None) -> ExecutionStrategy:
        """Выбор стратегии выполнения команды"""
        if context is None:
            context = {}
            
        # 1. Системные команды
        if self.is_system_command(command):
            return ExecutionStrategy.SYSTEM
            
        # 2. Веб-контекст для DOM
        if self.is_web_context(context):
            return ExecutionStrategy.DOM
            
        # 3. Fallback на CV
        return ExecutionStrategy.CV
    
    def is_system_command(self, command: Dict[str, Any]) -> bool:
        """Проверка системной команды"""
        if command.get('action') == 'system_command':
            return True
            
        cmd_name = command.get('command', '')
        return cmd_name in self.command_mapping
    
    def is_web_context(self, context: Dict[str, Any]) -> bool:
        """Проверка веб-контекста"""
        app_name = context.get('current_app', '').lower()
        return any(web_app in app_name for web_app in self.web_contexts)
    
    def get_system_context(self) -> Dict[str, Any]:
        """Получить контекст системы"""
        try:
            current_app = self.macos_commands.get_current_app()
            processes = self.macos_commands.list_processes()
            
            return {
                'current_app': current_app.get('app_name', 'Unknown') if current_app.get('success') else 'Unknown',
                'process_count': processes.get('count', 0) if processes.get('success') else 0,
                'timestamp': self._get_current_timestamp(),
                'platform': 'macOS'
            }
        except Exception as e:
            return {
                'error': f'Ошибка получения контекста: {str(e)}',
                'platform': 'macOS'
            }
    
    def _get_current_timestamp(self) -> str:
        """Получить текущий timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_available_commands(self) -> List[str]:
        """Получить список доступных команд"""
        return list(self.command_mapping.keys())


# Глобальный экземпляр оркестратора
system_orchestrator = SystemOrchestrator()
```

## 🧪 Тестирование системных команд

### Шаг 2.3: Создать тесты

**Создать файл:** `tests/test_stage2_system_commands.py`

```python
#!/usr/bin/env python3
"""
Тесты для Этапа 2: Системные команды
"""

import pytest
import tempfile
import time
from pathlib import Path

from src.system.macos_commands import MacOSCommands
from src.system.system_orchestrator import SystemOrchestrator


class TestMacOSCommands:
    """Тесты системных команд macOS"""
    
    def setup_method(self):
        self.commands = MacOSCommands()
    
    def test_list_processes(self):
        """Тест получения списка процессов"""
        result = self.commands.list_processes()
        
        assert result['success'] == True
        assert 'processes' in result
        assert result['count'] > 0
        assert len(result['processes']) > 0
        
        # Проверяем структуру процесса
        process = result['processes'][0]
        assert 'pid' in process
        assert 'name' in process
        assert isinstance(process['pid'], int)
    
    def test_take_screenshot(self):
        """Тест создания скриншота"""
        with tempfile.TemporaryDirectory() as temp_dir:
            screenshot_path = Path(temp_dir) / "test_screenshot.png"
            
            result = self.commands.take_screenshot(str(screenshot_path))
            
            assert result['success'] == True
            assert result['path'] == str(screenshot_path)
            assert screenshot_path.exists()
            assert screenshot_path.stat().st_size > 0
    
    def test_clipboard_operations(self):
        """Тест операций с буфером обмена"""
        test_text = "Тестовый текст для буфера обмена"
        
        # Копируем в буфер
        copy_result = self.commands.copy_to_clipboard(test_text)
        assert copy_result['success'] == True
        assert copy_result['text'] == test_text
        
        # Читаем из буфера
        read_result = self.commands.read_clipboard()
        assert read_result['success'] == True
        assert test_text in read_result['text']
    
    def test_get_current_app(self):
        """Тест получения текущего приложения"""
        result = self.commands.get_current_app()
        
        assert result['success'] == True
        assert 'app_name' in result
        assert result['app_name'] != 'Unknown'
    
    @pytest.mark.slow
    def test_open_close_app(self):
        """Тест открытия и закрытия приложения (медленный тест)"""
        app_name = "Calculator"
        
        # Открываем приложение
        open_result = self.commands.open_app(app_name)
        assert open_result['success'] == True
        
        # Ждем запуска
        time.sleep(2)
        
        # Проверяем, что приложение запущено
        processes = self.commands.list_processes()
        calculator_running = any(
            app_name.lower() in proc['name'].lower() 
            for proc in processes['processes']
        )
        assert calculator_running == True
        
        # Закрываем приложение
        close_result = self.commands.close_app(app_name)
        assert close_result['success'] == True


class TestSystemOrchestrator:
    """Тесты системного оркестратора"""
    
    def setup_method(self):
        self.orchestrator = SystemOrchestrator()
    
    def test_command_parsing(self):
        """Тест парсинга аргументов команд"""
        # Простые аргументы
        args1 = self.orchestrator._parse_command_args('Calculator')
        assert args1 == ['Calculator']
        
        # Аргументы в кавычках
        args2 = self.orchestrator._parse_command_args('"Google Chrome"')
        assert args2 == ['Google Chrome']
        
        # Множественные аргументы
        args3 = self.orchestrator._parse_command_args('"App Name" arg2 "arg 3"')
        assert args3 == ['App Name', 'arg2', 'arg 3']
    
    def test_system_command_execution(self):
        """Тест выполнения системных команд"""
        # Тест команды без аргументов
        result1 = self.orchestrator.execute_system_command('list_processes')
        assert result1['success'] == True
        assert result1['command'] == 'list_processes'
        
        # Тест команды с аргументами
        result2 = self.orchestrator.execute_system_command(
            'copy_to_clipboard', 
            '"Тестовый текст"'
        )
        assert result2['success'] == True
        assert result2['command'] == 'copy_to_clipboard'
    
    def test_invalid_command(self):
        """Тест обработки неверных команд"""
        result = self.orchestrator.execute_system_command('invalid_command')
        
        assert result['success'] == False
        assert 'Неизвестная системная команда' in result['error']
        assert 'available_commands' in result
    
    def test_get_system_context(self):
        """Тест получения системного контекста"""
        context = self.orchestrator.get_system_context()
        
        assert 'current_app' in context
        assert 'platform' in context
        assert context['platform'] == 'macOS'
        assert 'timestamp' in context
    
    def test_available_commands(self):
        """Тест получения списка доступных команд"""
        commands = self.orchestrator.get_available_commands()
        
        assert isinstance(commands, list)
        assert len(commands) > 0
        assert 'open_app' in commands
        assert 'take_screenshot' in commands


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

## 📋 Чек-лист выполнения Этапа 2

- [ ] Реализован MacOSCommands с полным набором команд
- [ ] Обновлен SystemOrchestrator с выполнением команд
- [ ] Добавлен парсинг аргументов команд
- [ ] Реализованы все базовые системные операции
- [ ] Написаны и пройдены все тесты
- [ ] Проверена интеграция с Этапом 1
- [ ] Документированы все команды и их параметры

## 🔗 Интеграция с DSL

После завершения этого этапа системные команды будут полностью интегрированы в DSL:

```atlas
# Пример использования системных команд в .atlas файле
@system open_app "Google Chrome"
wait 3s
@system focus_window "Chrome"
@system take_screenshot "/tmp/chrome_opened.png"

# Обычные команды CV/DOM
click NewTabButton
type "https://tiktok.com"
press enter
```

## ➡️ Следующий этап

После завершения системных команд переходим к [Этапу 3: Голосовой ввод](./stage-3-voice-input.md)
