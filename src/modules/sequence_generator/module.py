"""
Модуль генерации DSL последовательностей
Адаптация существующей опции 6 под модульную архитектуру
"""

import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.modules.base.ai_module import AIModule
from src.modules.base.module_config import ModuleConfig, ResourcesConfig, ExecutorConfig
from src.modules.base.module_result import ModuleResult

# Новые компоненты для расширенной автоматизации
from .handlers.system_app_handler import SystemAppHandler
from .integrations.spotlight_integration import SpotlightIntegration
from .managers.web_selector_manager import WebSelectorManager


class SequenceGeneratorModule(AIModule):
    """Модуль генерации DSL последовательностей"""
    
    def __init__(self):
        config = ModuleConfig(
            name="sequence_generator",
            description="Генерирует DSL последовательности по описанию пользователя (адаптация опции 6)",
            prompt_path="sequence_generator/prompts/",
            when_to_use=[
                "автоматизация", "макрос", "последовательность",
                "создай макрос", "генерация", "открыть и сделать",
                "создай автоматизацию", "сделай макрос"
            ],
            resources_config=ResourcesConfig(
                templates=True,
                variables=True,
                dom_selectors=True,
                system_commands=True,
                custom_data=False
            ),
            executor_config=ExecutorConfig(
                type="dsl_executor",
                timeout=300,
                retry_attempts=3
            ),
            priority=1  # Высокий приоритет
        )
        super().__init__(config)
        
        # Интеграция с существующим AIMacroGenerator
        self._initialize_legacy_generator()
        
        # Инициализация новых компонентов
        self._initialize_enhanced_components()
    
    def _initialize_legacy_generator(self):
        """Инициализация существующего AIMacroGenerator"""
        try:
            from src.ai.macro_generator import AIMacroGenerator
            self.legacy_generator = AIMacroGenerator(project_root)
            self.logger.info("Интеграция с AIMacroGenerator успешна")
        except ImportError as e:
            self.logger.warning(f"Не удалось импортировать AIMacroGenerator: {e}")
            self.legacy_generator = None
    
    def _initialize_enhanced_components(self):
        """Инициализация новых компонентов для расширенной автоматизации"""
        try:
            # Инициализация обработчика системных приложений
            self.system_app_handler = SystemAppHandler()
            self.logger.info(f"✅ SystemAppHandler: {len(self.system_app_handler.get_all_system_apps())} приложений")
            
            # Инициализация Spotlight интеграции
            self.spotlight_integration = SpotlightIntegration()
            spotlight_stats = self.spotlight_integration.get_spotlight_statistics()
            self.logger.info(f"✅ SpotlightIntegration: {'доступен' if spotlight_stats.get('available') else 'недоступен'}")
            
            # Инициализация менеджера веб-селекторов
            self.web_selector_manager = WebSelectorManager()
            web_stats = self.web_selector_manager.get_site_statistics()
            self.logger.info(f"✅ WebSelectorManager: {web_stats.get('total_sites')} сайтов, {web_stats.get('total_selectors')} селекторов")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации расширенных компонентов: {e}")
            # Fallback к None для graceful degradation
            self.system_app_handler = None
            self.spotlight_integration = None
            self.web_selector_manager = None
    
    def get_context_resources(self) -> Dict[str, Any]:
        """Загружает ресурсы для контекста (интеграция с существующей системой)"""
        resources = {}
        
        try:
            # Используем существующий AIMacroGenerator для загрузки ресурсов
            if self.legacy_generator:
                # Загружаем шаблоны
                if self.config.resources_config.templates:
                    resources["templates"] = self._load_templates_via_legacy()
                
                # Загружаем переменные
                if self.config.resources_config.variables:
                    resources["variables"] = self._load_variables_via_legacy()
                
                # Загружаем DOM селекторы
                if self.config.resources_config.dom_selectors:
                    resources["dom_selectors"] = self._load_dom_selectors_via_legacy()
                
                # Загружаем системные команды
                if self.config.resources_config.system_commands:
                    resources["system_commands"] = self._load_system_commands_via_legacy()
            else:
                # Fallback к базовой реализации
                resources = super().get_context_resources()
            
            # Добавляем новые расширенные ресурсы
            resources.update(self._load_enhanced_resources())
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки ресурсов: {e}")
            resources = super().get_context_resources()
        
        return resources
    
    def execute(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ModuleResult:
        """
        Переопределенный метод выполнения с расширенными возможностями
        """
        start_time = time.time()
        
        if context is None:
            context = {}
        
        self.logger.info(f"Начало выполнения: {user_input[:50]}...")
        
        try:
            # 1. Анализ намерений пользователя
            intent = self._analyze_user_intent(user_input)
            self.logger.info(f"Анализ намерений: {intent['type']} (confidence: {intent['confidence']})")
            
            # 2. Попытка генерации через расширенные возможности
            enhanced_dsl = None
            if intent["confidence"] > 0.6:
                enhanced_dsl = self._generate_enhanced_dsl(user_input, intent)
                if enhanced_dsl:
                    self.logger.info(f"Использована расширенная генерация для {intent['type']}")
            
            # 3. Если расширенная генерация не сработала, используем AI
            if not enhanced_dsl:
                # Формирование промпта с контекстом
                full_prompt = self.build_prompt(user_input, context)
                
                # AI генерация результата
                ai_result = self.ai_agent.generate(full_prompt, context)
                self.logger.info("AI генерация завершена")
                
                # Парсинг AI результата
                parsed_result = self.parse_ai_result(ai_result)
                self.logger.info("Парсинг AI результата завершен")
                
                dsl_code = parsed_result["dsl_code"]
                name = parsed_result["name"]
                description = parsed_result["description"]
            else:
                # Используем результат расширенной генерации
                dsl_code = enhanced_dsl
                name = f"Enhanced {intent['type'].title()} Macro"
                description = f"Автоматически сгенерированный макрос для {intent['type']}"
                parsed_result = {
                    "name": name,
                    "dsl_code": dsl_code,
                    "description": description,
                    "enhanced": True,
                    "intent": intent
                }
            
            # 4. Сохранение макроса
            saved_file = self._save_generated_macro(name, dsl_code, description)
            
            # 5. Выполнение через executor (опционально)
            execution_result = None
            if self.config.executor_config.type != "none":
                execution_result = self.executor.execute(dsl_code)
                self.logger.info("Выполнение через executor завершено")
            
            # 6. Формирование результата
            execution_time = time.time() - start_time
            
            result_data = {
                "generated_macro": {
                    "name": name,
                    "description": description,
                    "dsl_code": dsl_code
                },
                "saved_file": saved_file,
                "intent_analysis": intent,
                "enhanced_generation": bool(enhanced_dsl)
            }
            
            if execution_result:
                result_data["execution_result"] = execution_result.to_dict()
            
            result = ModuleResult(
                success=True,
                data=result_data,
                execution_time=execution_time,
                metadata={
                    "parsed_result": parsed_result,
                    "intent": intent,
                    "enhanced": bool(enhanced_dsl)
                }
            )
            
            result.add_log(f"Макрос '{name}' успешно создан")
            if saved_file:
                result.add_log(f"Сохранен в: {Path(saved_file).name}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Ошибка в модуле {self.name}: {str(e)}"
            self.logger.error(error_msg)
            
            return ModuleResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
    
    def _load_templates_via_legacy(self) -> Dict[str, Any]:
        """Загрузка шаблонов через существующую систему"""
        try:
            # Используем существующую логику загрузки шаблонов
            templates_dir = project_root / "templates"
            if not templates_dir.exists():
                return {"count": 0, "available": []}
            
            template_files = list(templates_dir.rglob("*.png"))
            template_names = [f.stem for f in template_files]
            
            return {
                "count": len(template_files),
                "available": template_names[:20],  # Ограничиваем для промпта
                "total_files": len(template_files)
            }
        except Exception as e:
            self.logger.error(f"Ошибка загрузки шаблонов: {e}")
            return {"count": 0, "available": []}
    
    def _load_variables_via_legacy(self) -> Dict[str, Any]:
        """Загрузка DSL переменных через существующую систему"""
        try:
            # Загружаем переменные из существующих файлов
            variables_files = [
                project_root / "templates" / "DSL_VARIABLES.txt",
                project_root / "dsl_references" / "USER_VARIABLES.txt"
            ]
            
            variables = []
            for var_file in variables_files:
                if var_file.exists():
                    with open(var_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Простое извлечение переменных
                        var_matches = re.findall(r'\$\{([^}]+)\}', content)
                        variables.extend(var_matches)
            
            return {
                "count": len(variables),
                "available": list(set(variables))[:15]  # Уникальные, ограничиваем
            }
        except Exception as e:
            self.logger.error(f"Ошибка загрузки переменных: {e}")
            return {"count": 0, "available": []}
    
    def _load_dom_selectors_via_legacy(self) -> Dict[str, Any]:
        """Загрузка DOM селекторов через существующую систему"""
        try:
            # Загружаем DOM селекторы из существующей структуры
            dom_dir = project_root / "dom_selectors"
            if not dom_dir.exists():
                return {"count": 0, "available": []}
            
            selectors = []
            for json_file in dom_dir.rglob("selectors.json"):
                try:
                    import json
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        selectors.extend(data.keys())
                except:
                    continue
            
            return {
                "count": len(selectors),
                "available": selectors[:15]  # Ограничиваем
            }
        except Exception as e:
            self.logger.error(f"Ошибка загрузки DOM селекторов: {e}")
            return {"count": 0, "available": []}
    
    def _load_system_commands_via_legacy(self) -> Dict[str, Any]:
        """Загрузка системных команд"""
        system_commands = [
            "open_app", "close_app", "focus_window",
            "take_screenshot", "copy_to_clipboard", "read_clipboard",
            "list_processes", "switch_desktop", "get_current_app"
        ]
        
        return {
            "count": len(system_commands),
            "available": system_commands
        }
    
    def build_prompt(self, user_input: str, context: Dict[str, Any]) -> str:
        """Построение промпта с ресурсами"""
        # Загружаем базовый промпт
        base_prompt = self.load_prompt("base_prompt.txt")
        
        # Загружаем ресурсы
        resources = self.get_context_resources()
        
        # Форматируем ресурсы для промпта
        templates_str = self._format_templates_for_prompt(resources.get("templates", {}))
        variables_str = self._format_variables_for_prompt(resources.get("variables", {}))
        dom_selectors_str = self._format_dom_selectors_for_prompt(resources.get("dom_selectors", {}))
        system_commands_str = self._format_system_commands_for_prompt(resources.get("system_commands", {}))
        context_str = self._format_context_for_prompt(context)
        
        # Формируем полный промпт
        full_prompt = base_prompt.format(
            user_input=user_input,
            available_templates=templates_str,
            available_variables=variables_str,
            available_dom_selectors=dom_selectors_str,
            available_system_commands=system_commands_str,
            context=context_str
        )
        
        return full_prompt
    
    def _format_templates_for_prompt(self, templates: Dict[str, Any]) -> str:
        """Форматирование шаблонов для промпта"""
        if not templates or templates.get("count", 0) == 0:
            return "Шаблоны не загружены"
        
        available = templates.get("available", [])
        result = f"Доступно {templates['count']} шаблонов:\n"
        
        for template in available:
            result += f"- {template}\n"
        
        if len(available) < templates.get("total_files", 0):
            result += f"... и еще {templates['total_files'] - len(available)} шаблонов"
        
        return result
    
    def _format_variables_for_prompt(self, variables: Dict[str, Any]) -> str:
        """Форматирование переменных для промпта"""
        if not variables or variables.get("count", 0) == 0:
            return "DSL переменные не загружены"
        
        available = variables.get("available", [])
        result = f"Доступно {variables['count']} переменных:\n"
        
        for var in available:
            result += f"- ${{{var}}}\n"
        
        return result
    
    def _format_dom_selectors_for_prompt(self, selectors: Dict[str, Any]) -> str:
        """Форматирование DOM селекторов для промпта"""
        if not selectors or selectors.get("count", 0) == 0:
            return "DOM селекторы не загружены"
        
        available = selectors.get("available", [])
        result = f"Доступно {selectors['count']} DOM селекторов:\n"
        
        for selector in available:
            result += f"- {selector}\n"
        
        return result
    
    def _format_system_commands_for_prompt(self, commands: Dict[str, Any]) -> str:
        """Форматирование системных команд для промпта"""
        if not commands or commands.get("count", 0) == 0:
            return "Системные команды не загружены"
        
        available = commands.get("available", [])
        result = f"Доступно {commands['count']} системных команд:\n"
        
        for command in available:
            result += f"- {command}\n"
        
        return result
    
    def _format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """Форматирование контекста для промпта"""
        if not context:
            return "Контекст отсутствует"
        
        formatted = []
        for key, value in context.items():
            if value:
                formatted.append(f"- {key}: {value}")
        
        return "\n".join(formatted) if formatted else "Контекст отсутствует"
    
    def parse_ai_result(self, ai_result: str) -> Dict[str, Any]:
        """Парсинг результата AI в структурированный формат"""
        try:
            # Извлекаем название
            name_match = re.search(r'НАЗВАНИЕ:\s*(.+)', ai_result, re.IGNORECASE)
            name = name_match.group(1).strip() if name_match else "Generated Macro"
            
            # Извлекаем DSL код
            dsl_match = re.search(r'```atlas\n(.*?)\n```', ai_result, re.DOTALL | re.IGNORECASE)
            if not dsl_match:
                # Fallback: ищем любой код блок
                dsl_match = re.search(r'```\n(.*?)\n```', ai_result, re.DOTALL)
            
            if not dsl_match:
                # Если нет блоков кода, берем все после "DSL КОД:"
                dsl_match = re.search(r'DSL КОД:\s*\n(.*?)(?=\n\n|\nОПИСАНИЕ:|$)', ai_result, re.DOTALL | re.IGNORECASE)
            
            dsl_code = dsl_match.group(1).strip() if dsl_match else ai_result
            
            # Извлекаем описание
            desc_match = re.search(r'ОПИСАНИЕ:\s*(.+)', ai_result, re.IGNORECASE)
            description = desc_match.group(1).strip() if desc_match else "AI сгенерированный макрос"
            
            # Очищаем DSL код от лишнего
            dsl_code = self._clean_dsl_code(dsl_code)
            
            return {
                "name": name,
                "dsl_code": dsl_code,
                "description": description,
                "raw_ai_response": ai_result
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка парсинга AI результата: {e}")
            return {
                "name": "Generated Macro",
                "dsl_code": ai_result,
                "description": "AI сгенерированный макрос",
                "raw_ai_response": ai_result
            }
    
    def _clean_dsl_code(self, dsl_code: str) -> str:
        """Очистка DSL кода от лишних элементов"""
        lines = dsl_code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Пропускаем пустые строки и markdown артефакты
            if line and not line.startswith('```') and line != 'atlas':
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def execute_result(self, parsed_result: Dict[str, Any]) -> ModuleResult:
        """Выполнение сгенерированного DSL кода (опционально)"""
        try:
            dsl_code = parsed_result["dsl_code"]
            
            # Сохраняем сгенерированный макрос
            saved_file = self._save_generated_macro(
                parsed_result["name"],
                dsl_code,
                parsed_result["description"]
            )
            
            # Если нужно выполнить сразу - используем DSL executor
            if self.config.executor_config.type == "dsl_executor":
                execution_result = self.executor.execute(dsl_code)
                
                return ModuleResult(
                    success=execution_result.success,
                    data={
                        "generated_macro": parsed_result,
                        "saved_file": saved_file,
                        "execution_result": execution_result.data if execution_result.success else None
                    },
                    error=execution_result.error if not execution_result.success else None
                )
            else:
                # Только генерация без выполнения
                return ModuleResult(
                    success=True,
                    data={
                        "generated_macro": parsed_result,
                        "saved_file": saved_file
                    }
                )
                
        except Exception as e:
            return ModuleResult(
                success=False,
                error=f"Ошибка выполнения результата: {str(e)}",
                data={"parsed_result": parsed_result}
            )
    
    def _save_generated_macro(self, name: str, dsl_code: str, description: str) -> str:
        """Сохранение сгенерированного макроса в .atlas файл"""
        try:
            # Создаем имя файла
            safe_name = re.sub(r'[^\w\s-]', '', name).strip()
            safe_name = re.sub(r'[-\s]+', '_', safe_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{safe_name}_{timestamp}.atlas"
            
            # Путь к файлу
            macros_dir = project_root / "macros" / "production"
            macros_dir.mkdir(parents=True, exist_ok=True)
            filepath = macros_dir / filename
            
            # Формируем содержимое .atlas файла
            atlas_content = f"""# Macro Atlas File
# Generated by Modular AI System
# Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# Platform: macOS
# Description: {description}

# MACRO CODE
{dsl_code}

# METADATA
# Platform: macOS
# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
# Description: {description}
# Version: 1.0
# Module: sequence_generator
"""
            
            # Сохраняем файл
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(atlas_content)
            
            self.logger.info(f"Макрос сохранен: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения макроса: {e}")
            return ""
    
    def _load_enhanced_resources(self) -> Dict[str, Any]:
        """Загрузка расширенных ресурсов (системные приложения, веб-селекторы, Spotlight)"""
        enhanced_resources = {}
        
        try:
            # Системные приложения
            if self.system_app_handler:
                system_apps = self.system_app_handler.get_all_system_apps()
                enhanced_resources["system_apps"] = {
                    "count": len(system_apps),
                    "available": system_apps[:15],  # Ограничиваем для промпта
                    "examples": ["Calculator", "Finder", "System_Preferences", "TextEdit", "Terminal"]
                }
            
            # Веб-селекторы
            if self.web_selector_manager:
                web_stats = self.web_selector_manager.get_site_statistics()
                supported_sites = self.web_selector_manager.get_supported_sites()
                enhanced_resources["web_selectors"] = {
                    "total_sites": web_stats.get("total_sites", 0),
                    "total_selectors": web_stats.get("total_selectors", 0),
                    "popular_sites": [site["name"] for site in supported_sites[:10]],
                    "examples": ["youtube", "google", "github", "twitter", "linkedin"]
                }
            
            # Spotlight интеграция
            if self.spotlight_integration:
                spotlight_stats = self.spotlight_integration.get_spotlight_statistics()
                enhanced_resources["spotlight"] = {
                    "available": spotlight_stats.get("available", False),
                    "common_searches": list(self.spotlight_integration.common_searches.keys())[:10],
                    "examples": ["калькулятор", "finder", "настройки", "терминал"]
                }
            
            return enhanced_resources
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки расширенных ресурсов: {e}")
            return {}
    
    def _analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """Анализ намерений пользователя для выбора типа автоматизации"""
        intent = {
            "type": "general",  # general, system_app, web, spotlight
            "target_app": None,
            "target_site": None,
            "action": None,
            "confidence": 0.5
        }
        
        user_lower = user_input.lower()
        
        # Проверка на системные приложения
        if self.system_app_handler:
            for app_name in self.system_app_handler.get_all_system_apps():
                app_keywords = self.system_app_handler.get_app_keywords(app_name)
                if any(keyword.lower() in user_lower for keyword in app_keywords):
                    intent["type"] = "system_app"
                    intent["target_app"] = app_name
                    intent["confidence"] = 0.8
                    break
        
        # Проверка на веб-сайты
        if self.web_selector_manager and intent["type"] == "general":
            matching_sites = self.web_selector_manager.identify_site_from_keywords(user_input)
            if matching_sites:
                intent["type"] = "web"
                intent["target_site"] = matching_sites[0]
                intent["confidence"] = 0.7
        
        # Проверка на Spotlight поиск
        spotlight_keywords = ["найди", "поиск", "spotlight", "спотлайт", "найти"]
        if any(keyword in user_lower for keyword in spotlight_keywords):
            intent["type"] = "spotlight"
            intent["confidence"] = 0.6
        
        # Определение действия
        action_keywords = {
            "open": ["открой", "запусти", "открыть", "запустить", "open", "launch"],
            "search": ["найди", "поиск", "найти", "search", "find"],
            "click": ["кликни", "нажми", "click", "press"],
            "type": ["введи", "напиши", "type", "write"]
        }
        
        for action, keywords in action_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                intent["action"] = action
                break
        
        return intent
    
    def _generate_enhanced_dsl(self, user_input: str, intent: Dict[str, Any]) -> str:
        """Генерация DSL с использованием расширенных возможностей"""
        try:
            if intent["type"] == "system_app" and intent["target_app"]:
                return self._generate_system_app_dsl(user_input, intent["target_app"])
            
            elif intent["type"] == "web" and intent["target_site"]:
                return self._generate_web_automation_dsl(user_input, intent["target_site"])
            
            elif intent["type"] == "spotlight":
                return self._generate_spotlight_dsl(user_input)
            
            else:
                # Fallback к обычной генерации через AI
                return None
                
        except Exception as e:
            self.logger.error(f"Ошибка генерации расширенного DSL: {e}")
            return None
    
    def _generate_system_app_dsl(self, user_input: str, app_name: str) -> str:
        """Генерация DSL для системных приложений"""
        if not self.system_app_handler:
            return None
        
        # Специальные случаи для популярных приложений
        if "калькулятор" in user_input.lower() or "calculator" in user_input.lower():
            # Поиск математического выражения
            import re
            math_pattern = r'(\d+[\+\-\*\/\=\d\s\.]+)'
            match = re.search(math_pattern, user_input)
            if match:
                expression = match.group(1).strip()
                return self.system_app_handler.generate_calculator_macro(expression)
        
        if "finder" in user_input.lower() and ("найди" in user_input.lower() or "поиск" in user_input.lower()):
            # Извлечение поискового запроса
            search_terms = user_input.lower().replace("finder", "").replace("найди", "").replace("поиск", "").strip()
            if search_terms:
                return self.system_app_handler.generate_finder_search_macro(search_terms)
        
        # Обычный запуск приложения
        return self.system_app_handler.generate_app_launch_dsl(app_name)
    
    def _generate_web_automation_dsl(self, user_input: str, site_name: str) -> str:
        """Генерация DSL для веб-автоматизации"""
        if not self.web_selector_manager:
            return None
        
        user_lower = user_input.lower()
        
        # YouTube специальные случаи
        if site_name == "youtube":
            if "найди" in user_lower or "поиск" in user_lower:
                # Извлечение поискового запроса
                query = user_lower.replace("youtube", "").replace("найди", "").replace("поиск", "").strip()
                if query:
                    return self.web_selector_manager.generate_youtube_automation_dsl("search_and_play", query)
            elif "лайк" in user_lower:
                return self.web_selector_manager.generate_youtube_automation_dsl("like_video")
            elif "подпиш" in user_lower:
                return self.web_selector_manager.generate_youtube_automation_dsl("subscribe")
        
        # Google поиск
        elif site_name == "google":
            if "найди" in user_lower or "поиск" in user_lower:
                query = user_lower.replace("google", "").replace("гугл", "").replace("найди", "").replace("поиск", "").strip()
                search_type = "web"
                if "картинки" in user_lower or "изображения" in user_lower:
                    search_type = "images"
                elif "видео" in user_lower:
                    search_type = "videos"
                elif "новости" in user_lower:
                    search_type = "news"
                
                if query:
                    return self.web_selector_manager.generate_google_search_dsl(query, search_type)
        
        # Обычная навигация на сайт
        return self.web_selector_manager.generate_web_navigation_dsl(site_name)
    
    def _generate_spotlight_dsl(self, user_input: str) -> str:
        """Генерация DSL для Spotlight поиска"""
        if not self.spotlight_integration:
            return None
        
        # Извлечение поискового запроса
        user_lower = user_input.lower()
        query = user_lower
        
        # Убираем служебные слова
        remove_words = ["найди", "поиск", "spotlight", "спотлайт", "найти", "через", "в"]
        for word in remove_words:
            query = query.replace(word, "")
        
        query = query.strip()
        
        if query:
            return self.spotlight_integration.generate_spotlight_search_dsl(query, "open")
        
        return None
