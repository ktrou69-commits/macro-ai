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
