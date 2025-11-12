"""
Обработчик системных приложений macOS
"""

import yaml
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class SystemAppHandler:
    """Обработчик системных приложений macOS"""
    
    def __init__(self):
        self.system_apps = {}
        self.spotlight_commands = {}
        self.system_shortcuts = {}
        self._load_system_apps_config()
    
    def _load_system_apps_config(self):
        """Загрузка конфигурации системных приложений"""
        try:
            config_path = Path(__file__).parent.parent / "resources" / "system_apps.yaml"
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    
                self.system_apps = config.get('system_apps', {})
                self.spotlight_commands = config.get('spotlight_commands', {})
                self.system_shortcuts = config.get('system_shortcuts', {})
                
                logger.info(f"✅ Загружено {len(self.system_apps)} системных приложений")
            else:
                logger.warning("⚠️ Конфигурация system_apps.yaml не найдена")
                
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки system_apps.yaml: {e}")
    
    def get_app_info(self, app_name: str) -> Optional[Dict[str, Any]]:
        """Получение информации о приложении"""
        # Поиск по точному имени
        if app_name in self.system_apps:
            return self.system_apps[app_name]
        
        # Поиск по ключевым словам
        for app_key, app_info in self.system_apps.items():
            keywords = app_info.get('keywords', [])
            if any(keyword.lower() in app_name.lower() for keyword in keywords):
                return app_info
        
        return None
    
    def is_system_app(self, app_name: str) -> bool:
        """Проверка, является ли приложение системным"""
        return self.get_app_info(app_name) is not None
    
    def get_launch_command(self, app_name: str) -> Optional[str]:
        """Получение команды запуска приложения"""
        app_info = self.get_app_info(app_name)
        if app_info:
            return app_info.get('launch_command')
        return None
    
    def get_app_elements(self, app_name: str) -> Dict[str, str]:
        """Получение элементов интерфейса приложения"""
        app_info = self.get_app_info(app_name)
        if app_info:
            return app_info.get('common_elements', {})
        return {}
    
    def is_app_installed(self, app_name: str) -> bool:
        """Проверка установки приложения"""
        app_info = self.get_app_info(app_name)
        if not app_info:
            return False
        
        bundle_id = app_info.get('bundle_id')
        if not bundle_id:
            return False
        
        try:
            # Проверка через mdfind (Spotlight database)
            result = subprocess.run(
                ['mdfind', f'kMDItemCFBundleIdentifier == "{bundle_id}"'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return bool(result.stdout.strip())
        except Exception as e:
            logger.warning(f"⚠️ Не удалось проверить установку {app_name}: {e}")
            return True  # Предполагаем, что установлено
    
    def generate_app_launch_dsl(self, app_name: str, method: str = "direct") -> str:
        """Генерация DSL для запуска приложения"""
        app_info = self.get_app_info(app_name)
        if not app_info:
            return f"# Приложение {app_name} не найдено в системных приложениях"
        
        app_display_name = app_info.get('app_name', app_name)
        description = app_info.get('description', 'Системное приложение macOS')
        
        if method == "spotlight":
            return self._generate_spotlight_launch_dsl(app_display_name, description)
        else:
            return self._generate_direct_launch_dsl(app_info, description)
    
    def _generate_direct_launch_dsl(self, app_info: Dict[str, Any], description: str) -> str:
        """Генерация DSL для прямого запуска"""
        launch_command = app_info.get('launch_command', '')
        app_name = app_info.get('app_name', 'Unknown')
        
        return f"""# Запуск {app_name}
# {description}
system_command "{launch_command}"
wait 2s"""
    
    def _generate_spotlight_launch_dsl(self, app_name: str, description: str) -> str:
        """Генерация DSL для запуска через Spotlight"""
        template = self.spotlight_commands.get('search_specific', {}).get('dsl_template', '')
        
        if template:
            return f"# {description}\n" + template.format(app_name=app_name)
        else:
            return f"""# Запуск {app_name} через Spotlight
# {description}
key cmd+space
wait 0.5s
type "{app_name}"
wait 1s
press enter
wait 2s"""
    
    def generate_calculator_macro(self, expression: str) -> str:
        """Генерация макроса для калькулятора"""
        if not self.is_system_app("Calculator"):
            return "# Калькулятор не найден"
        
        # Парсинг математического выражения
        dsl_commands = ["# Вычисление в калькуляторе: " + expression]
        dsl_commands.append("system_command \"open -a Calculator\"")
        dsl_commands.append("wait 2s")
        
        # Преобразование выражения в клики
        for char in expression.replace(" ", ""):
            if char.isdigit():
                dsl_commands.append(f"click \"button_{char}\"")
            elif char == '+':
                dsl_commands.append("click \"button_plus\"")
            elif char == '-':
                dsl_commands.append("click \"button_minus\"")
            elif char == '*':
                dsl_commands.append("click \"button_multiply\"")
            elif char == '/':
                dsl_commands.append("click \"button_divide\"")
            elif char == '.':
                dsl_commands.append("click \"button_decimal\"")
            elif char == '=':
                dsl_commands.append("click \"button_equals\"")
        
        # Добавляем = если его нет
        if not expression.endswith('='):
            dsl_commands.append("click \"button_equals\"")
        
        dsl_commands.append("wait 1s")
        
        return "\n".join(dsl_commands)
    
    def generate_finder_search_macro(self, search_term: str) -> str:
        """Генерация макроса для поиска в Finder"""
        return f"""# Поиск в Finder: {search_term}
system_command "open -a Finder"
wait 2s
click "search_field"
wait 0.5s
type "{search_term}"
press enter
wait 2s"""
    
    def generate_system_preferences_macro(self, preference_name: str) -> str:
        """Генерация макроса для открытия системных настроек"""
        # Поиск соответствующей настройки
        app_info = self.get_app_info("System_Preferences")
        if not app_info:
            return "# Системные настройки не найдены"
        
        elements = app_info.get('common_elements', {})
        
        # Поиск элемента по имени
        pref_element = None
        for element_name, selector in elements.items():
            if preference_name.lower() in element_name.lower():
                pref_element = element_name
                break
        
        if pref_element:
            return f"""# Открытие настроек: {preference_name}
system_command "open -a 'System Preferences'"
wait 3s
click "{pref_element}"
wait 2s"""
        else:
            return f"""# Поиск настроек: {preference_name}
system_command "open -a 'System Preferences'"
wait 3s
click "search_field"
wait 0.5s
type "{preference_name}"
wait 1s
press enter
wait 2s"""
    
    def get_system_shortcut(self, shortcut_name: str) -> Optional[str]:
        """Получение системного горячего клавиши"""
        return self.system_shortcuts.get(shortcut_name)
    
    def generate_screenshot_macro(self, screenshot_type: str = "selection") -> str:
        """Генерация макроса для скриншота"""
        shortcuts = {
            "selection": "cmd+shift+4",
            "window": "cmd+shift+4+space", 
            "full": "cmd+shift+3"
        }
        
        shortcut = shortcuts.get(screenshot_type, "cmd+shift+4")
        
        return f"""# Создание скриншота ({screenshot_type})
key {shortcut}
wait 1s"""
    
    def get_all_system_apps(self) -> List[str]:
        """Получение списка всех системных приложений"""
        return list(self.system_apps.keys())
    
    def get_app_keywords(self, app_name: str) -> List[str]:
        """Получение ключевых слов приложения"""
        app_info = self.get_app_info(app_name)
        if app_info:
            return app_info.get('keywords', [])
        return []
    
    def search_apps_by_keyword(self, keyword: str) -> List[str]:
        """Поиск приложений по ключевому слову"""
        matching_apps = []
        
        for app_name, app_info in self.system_apps.items():
            keywords = app_info.get('keywords', [])
            if any(keyword.lower() in kw.lower() for kw in keywords):
                matching_apps.append(app_name)
        
        return matching_apps
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики системных приложений"""
        return {
            "total_apps": len(self.system_apps),
            "spotlight_commands": len(self.spotlight_commands),
            "system_shortcuts": len(self.system_shortcuts),
            "apps_list": list(self.system_apps.keys())
        }
