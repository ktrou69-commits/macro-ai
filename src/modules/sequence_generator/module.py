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

# Компоненты для улучшенного AI и валидации (Часть 2)
from .prompts.context_aware_prompts import ContextAwarePrompts, PromptContextBuilder
from .prompts.examples import AIExamples, ExampleSelector
from .validators.dsl_validator import DSLValidator, DSLFormatter
from .validators.semantic_validator import SemanticValidator

# Компоненты для многошаговых макросов (Часть 3)
from .dsl.conditions import Condition, ConditionalBlock, ConditionParser, ConditionEvaluator
from .dsl.loops import LoopBlock, RepeatLoop, WhileLoop, ForEachLoop, LoopParser, LoopExecutor
from .dsl.variables import VariableManager, VariableParser, VariableValidator
from .parsers.enhanced_dsl_parser import EnhancedDSLParser, ParsedDSL, DSLOptimizer
from .executors.enhanced_executor import EnhancedExecutor, ExecutionResult, ExecutionStatus
from .prompts.advanced_prompts import AdvancedPrompts, ComplexityAnalyzer


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
            
            # Инициализация компонентов Части 2: Улучшенный AI и валидация
            self._initialize_ai_enhancement_components()
            
            # Инициализация компонентов Части 3: Многошаговые макросы
            self._initialize_complex_macro_components()
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации расширенных компонентов: {e}")
            # Fallback к None для graceful degradation
            self.system_app_handler = None
            self.spotlight_integration = None
            self.web_selector_manager = None
    
    def _initialize_ai_enhancement_components(self):
        """Инициализация компонентов для улучшенного AI (Часть 2)"""
        try:
            # Инициализация контекстно-зависимых промптов
            self.context_prompts = ContextAwarePrompts()
            self.prompt_builder = PromptContextBuilder()
            self.logger.info(f"✅ ContextAwarePrompts: {len(self.context_prompts.get_available_prompt_types())} типов промптов")
            
            # Инициализация примеров для AI
            self.ai_examples = AIExamples()
            self.example_selector = ExampleSelector()
            examples_stats = self.ai_examples.get_statistics()
            self.logger.info(f"✅ AIExamples: {examples_stats.get('total_examples')} примеров для {len(examples_stats.get('available_intents', []))} типов")
            
            # Инициализация валидаторов DSL
            self.dsl_validator = DSLValidator()
            self.semantic_validator = SemanticValidator()
            self.dsl_formatter = DSLFormatter()
            self.logger.info("✅ DSL валидаторы инициализированы")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации AI компонентов: {e}")
            # Fallback к None для graceful degradation
            self.context_prompts = None
            self.prompt_builder = None
            self.ai_examples = None
            self.example_selector = None
            self.dsl_validator = None
            self.semantic_validator = None
            self.dsl_formatter = None
    
    def _initialize_complex_macro_components(self):
        """Инициализация компонентов для многошаговых макросов (Часть 3)"""
        try:
            # Инициализация расширенного DSL парсера
            self.enhanced_dsl_parser = EnhancedDSLParser()
            self.dsl_optimizer = DSLOptimizer()
            self.logger.info("✅ Enhanced DSL Parser инициализирован")
            
            # Инициализация расширенного исполнителя
            self.enhanced_executor = EnhancedExecutor()
            self.logger.info("✅ Enhanced Executor инициализирован")
            
            # Инициализация продвинутых промптов
            self.advanced_prompts = AdvancedPrompts()
            self.complexity_analyzer = ComplexityAnalyzer()
            self.logger.info("✅ Advanced Prompts инициализированы")
            
            # Инициализация компонентов DSL
            self.condition_parser = ConditionParser()
            self.loop_parser = LoopParser()
            self.variable_parser = VariableParser()
            self.logger.info("✅ DSL компоненты (условия, циклы, переменные) инициализированы")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка инициализации компонентов многошаговых макросов: {e}")
            # Fallback к None для graceful degradation
            self.enhanced_dsl_parser = None
            self.enhanced_executor = None
            self.advanced_prompts = None
            self.complexity_analyzer = None
            self.condition_parser = None
            self.loop_parser = None
            self.variable_parser = None
    
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
            # 1. Анализ намерений пользователя и сложности
            intent = self._analyze_user_intent(user_input)
            complexity_analysis = self._analyze_complexity(user_input)
            self.logger.info(f"Анализ намерений: {intent['type']} (confidence: {intent['confidence']})")
            self.logger.info(f"Анализ сложности: {complexity_analysis['complexity_level']} (требует расширенные возможности: {complexity_analysis['requires_advanced_features']})")
            
            # 2. Всегда используем AI генерацию с правильными промптами (отключаем старую расширенную генерацию)
            enhanced_dsl = None
            
            # 3. Используем AI генерацию с детальным анализом намерений (Части 2 и 3)
            if True:  # Всегда используем AI
                # Выбор типа промпта на основе сложности
                if complexity_analysis['requires_advanced_features']:
                    # Используем продвинутые промпты для сложных макросов (Часть 3)
                    full_prompt = self._build_complex_macro_prompt(user_input, intent, complexity_analysis, context)
                    self.logger.info("Используется продвинутый AI промпт для сложного макроса")
                else:
                    # Используем улучшенные промпты (Часть 2)
                    full_prompt = self._build_enhanced_prompt(user_input, intent, context)
                    self.logger.info("Используется улучшенный AI промпт")
                
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
            
            # 4. Валидация и улучшение DSL кода (Части 2 и 3)
            validated_dsl, validation_info = self._validate_and_improve_dsl(dsl_code, context, complexity_analysis)
            if validated_dsl != dsl_code:
                dsl_code = validated_dsl
                self.logger.info("DSL код улучшен после валидации")
            
            # 5. Сохранение макроса
            saved_file = self._save_generated_macro(name, dsl_code, description)
            
            # 6. Выполнение через executor (опционально)
            execution_result = None
            if self.config.executor_config.type != "none":
                execution_result = self.executor.execute(dsl_code)
                self.logger.info("Выполнение через executor завершено")
            
            # 7. Формирование результата
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
            
            # Добавляем дополнительную информацию для интеграции с main.py
            result_data.update({
                "success": True,
                "filepath": saved_file,
                "dsl_code": dsl_code,
                "complexity_analysis": complexity_analysis,
                "validation_info": validation_info
            })
            
            # Добавляем статистику DSL если доступен enhanced parser
            if hasattr(self, 'enhanced_dsl_parser') and self.enhanced_dsl_parser:
                try:
                    parsed_dsl = self.enhanced_dsl_parser.parse(dsl_code)
                    result_data["dsl_stats"] = parsed_dsl.metadata
                except:
                    pass
            
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
        """Детальный анализ намерений пользователя с использованием улучшенной системы"""
        try:
            # Используем детальный анализ намерений
            from src.ai.module_descriptions import analyze_request
            detailed_analysis = analyze_request(user_input)
            
            # Преобразуем результат в старый формат для совместимости
            subcategory = detailed_analysis.get('subcategory', 'system_automation')
            
            # Маппинг подкатегорий в старые типы
            type_mapping = {
                'web_automation': 'web',
                'system_automation': 'system_app', 
                'spotlight_automation': 'spotlight',
                'calculator_automation': 'system_app'
            }
            
            intent_type = type_mapping.get(subcategory, 'general')
            
            # Определяем целевое приложение/сайт
            target_app = None
            target_site = None
            
            if subcategory == 'web_automation':
                # Определяем веб-сайт из запроса
                user_lower = user_input.lower()
                web_sites = ['youtube', 'google', 'twitter', 'facebook', 'instagram', 
                           'linkedin', 'github', 'amazon', 'netflix']
                for site in web_sites:
                    if site in user_lower:
                        target_site = site
                        break
            
            elif subcategory in ['system_automation', 'calculator_automation']:
                # Определяем системное приложение
                user_lower = user_input.lower()
                if 'калькулятор' in user_lower or 'calculator' in user_lower:
                    target_app = 'Calculator'
                elif 'finder' in user_lower:
                    target_app = 'Finder'
                elif 'safari' in user_lower:
                    target_app = 'Safari'
            
            # Определение действия (совместимость)
            action = None
            user_lower = user_input.lower()
            if any(word in user_lower for word in ['открой', 'запусти', 'open']):
                action = 'open'
            elif any(word in user_lower for word in ['найди', 'поиск', 'search']):
                action = 'search'
            elif any(word in user_lower for word in ['кликни', 'нажми', 'click']):
                action = 'click'
            elif any(word in user_lower for word in ['введи', 'напиши', 'type']):
                action = 'type'
            
            intent = {
                "type": intent_type,
                "target_app": target_app,
                "target_site": target_site,
                "action": action,
                "confidence": detailed_analysis.get('confidence', 0.5),
                # Дополнительная информация из детального анализа
                "subcategory": subcategory,
                "matched_triggers": detailed_analysis.get('matched_triggers', []),
                "expected_commands": detailed_analysis.get('expected_commands', []),
                "analysis_method": detailed_analysis.get('analysis_method', 'detailed')
            }
            
            return intent
            
        except Exception as e:
            self.logger.error(f"Ошибка детального анализа намерений: {e}")
            # Fallback на простой анализ
            return {
                "type": "general",
                "target_app": None,
                "target_site": None,
                "action": None,
                "confidence": 0.3,
                "subcategory": "system_automation",
                "matched_triggers": [],
                "expected_commands": [],
                "analysis_method": "fallback"
            }
    
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
    
    def _build_enhanced_prompt(self, user_input: str, intent: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Построение улучшенного промпта с контекстно-зависимыми шаблонами (Часть 2)
        """
        try:
            if not self.context_prompts or not self.prompt_builder:
                # Fallback к базовому промпту
                return self.build_prompt(user_input, context)
            
            # Определяем тип промпта на основе намерения
            intent_type = intent.get('type', 'general')
            prompt_type = self._map_intent_to_prompt_type(intent_type, intent)
            
            # Строим контекст для промпта
            prompt_context = self._build_prompt_context(user_input, intent, context)
            
            # Добавляем примеры для Few-Shot Learning
            if self.example_selector:
                examples = self.example_selector.select_best_examples(user_input, intent_type, 2)
                prompt_context['examples'] = examples
            
            # Получаем контекстно-зависимый промпт
            enhanced_prompt = self.context_prompts.get_prompt_for_intent(prompt_type, prompt_context)
            
            self.logger.info(f"Построен улучшенный промпт типа: {prompt_type}")
            return enhanced_prompt
            
        except Exception as e:
            self.logger.error(f"Ошибка построения улучшенного промпта: {e}")
            return self.build_prompt(user_input, context)
    
    def _map_intent_to_prompt_type(self, intent_type: str, intent: Dict[str, Any]) -> str:
        """Маппинг типа намерения на тип промпта с использованием детального анализа"""
        
        # Используем подкатегорию из детального анализа если доступна
        subcategory = intent.get('subcategory')
        if subcategory:
            # Прямой маппинг подкатегорий на типы промптов
            subcategory_mapping = {
                'web_automation': 'web_automation',
                'system_automation': 'system_automation', 
                'spotlight_automation': 'spotlight_automation',
                'calculator_automation': 'calculator_automation'
            }
            
            mapped_type = subcategory_mapping.get(subcategory)
            if mapped_type:
                return mapped_type
        
        # Fallback на старый маппинг
        mapping = {
            'web': 'web_automation',
            'system_app': 'system_automation',
            'spotlight': 'spotlight_automation',
            'general': 'mixed_automation'
        }
        
        # Специальные случаи
        if intent_type == 'system_app' and intent.get('target_app') == 'Calculator':
            return 'calculator_automation'
        
        return mapping.get(intent_type, 'mixed_automation')
    
    def _build_prompt_context(self, user_input: str, intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Построение контекста для промпта"""
        try:
            builder = PromptContextBuilder()
            builder.add_user_request(user_input)
            
            # Добавляем контекст на основе типа намерения
            intent_type = intent.get('type')
            
            if intent_type == 'web' and intent.get('target_site'):
                site_name = intent['target_site']
                if self.web_selector_manager:
                    selectors = self.web_selector_manager.get_site_selectors(site_name)
                    builder.add_web_context(site_name, selectors)
            
            elif intent_type == 'system_app' and intent.get('target_app'):
                app_name = intent['target_app']
                if self.system_app_handler:
                    app_elements = self.system_app_handler.get_app_elements(app_name)
                    builder.add_system_context(app_name, app_elements)
                    
                    # Специальный случай для калькулятора
                    if app_name == 'Calculator':
                        # Извлекаем математическое выражение из запроса
                        import re
                        math_pattern = r'(\d+[\+\-\*\/\=\d\s\.]+)'
                        match = re.search(math_pattern, user_input)
                        if match:
                            builder.add_math_context(match.group(1).strip())
            
            elif intent_type == 'spotlight':
                if self.spotlight_integration:
                    searches = list(self.spotlight_integration.common_searches.keys())
                    builder.add_spotlight_context(searches)
            
            # Добавляем все доступные ресурсы
            resources = self.get_context_resources()
            builder.add_all_resources(resources)
            
            return builder.build()
            
        except Exception as e:
            self.logger.error(f"Ошибка построения контекста промпта: {e}")
            return {
                'user_request': user_input,
                'all_resources': 'Ресурсы недоступны'
            }
    
    def _validate_and_improve_dsl(self, dsl_code: str, context: Dict[str, Any]) -> tuple:
        """
        Валидация и улучшение DSL кода (Часть 2)
        
        Returns:
            tuple: (улучшенный_dsl_код, информация_о_валидации)
        """
        validation_info = {
            'syntax_validation': None,
            'semantic_validation': None,
            'improvements_applied': [],
            'warnings': [],
            'suggestions': []
        }
        
        improved_dsl = dsl_code
        
        try:
            # 1. Синтаксическая валидация и автоисправление
            if self.dsl_validator:
                syntax_result = self.dsl_validator.validate_dsl(improved_dsl, auto_fix=True)
                validation_info['syntax_validation'] = syntax_result
                
                if syntax_result.fixed_code:
                    improved_dsl = syntax_result.fixed_code
                    validation_info['improvements_applied'].extend(syntax_result.fixes_applied)
                    self.logger.info(f"Применено {len(syntax_result.fixes_applied)} синтаксических исправлений")
                
                validation_info['warnings'].extend(syntax_result.warnings)
                validation_info['suggestions'].extend(syntax_result.suggestions)
            
            # 2. Семантическая валидация
            if self.semantic_validator:
                semantic_result = self.semantic_validator.validate_semantics(improved_dsl, context)
                validation_info['semantic_validation'] = semantic_result
                
                validation_info['warnings'].extend(semantic_result.warnings)
                validation_info['suggestions'].extend(semantic_result.suggestions)
                
                if semantic_result.warnings:
                    self.logger.info(f"Семантическая валидация: {len(semantic_result.warnings)} предупреждений")
            
            # 3. Форматирование кода
            if self.dsl_formatter and improved_dsl != dsl_code:
                formatted_dsl = self.dsl_formatter.format_dsl(improved_dsl)
                if formatted_dsl != improved_dsl:
                    improved_dsl = formatted_dsl
                    validation_info['improvements_applied'].append("Код отформатирован для лучшей читаемости")
            
            # Логируем результаты валидации
            if validation_info['warnings']:
                for warning in validation_info['warnings'][:3]:  # Показываем первые 3 предупреждения
                    self.logger.warning(f"DSL валидация: {warning}")
            
            return improved_dsl, validation_info
            
        except Exception as e:
            self.logger.error(f"Ошибка валидации DSL: {e}")
            return dsl_code, validation_info
    
    def _analyze_complexity(self, user_input: str) -> Dict[str, Any]:
        """
        Анализ сложности пользовательского запроса (Часть 3)
        
        Args:
            user_input: Запрос пользователя
            
        Returns:
            Результат анализа сложности
        """
        try:
            if self.complexity_analyzer:
                return self.complexity_analyzer.analyze_request_complexity(user_input)
            else:
                # Fallback анализ
                return {
                    "complexity_level": "medium",
                    "requires_advanced_features": False,
                    "recommended_prompt": "basic_macro"
                }
        except Exception as e:
            self.logger.error(f"Ошибка анализа сложности: {e}")
            return {
                "complexity_level": "medium",
                "requires_advanced_features": False,
                "recommended_prompt": "basic_macro"
            }
    
    def _build_complex_macro_prompt(self, user_input: str, intent: Dict[str, Any], 
                                   complexity_analysis: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Построение продвинутого промпта для сложных макросов (Часть 3)
        
        Args:
            user_input: Запрос пользователя
            intent: Анализ намерений
            complexity_analysis: Анализ сложности
            context: Контекст выполнения
            
        Returns:
            Продвинутый промпт для AI
        """
        try:
            if not self.advanced_prompts:
                # Fallback к улучшенному промпту
                return self._build_enhanced_prompt(user_input, intent, context)
            
            # Определяем тип сложности
            complexity_level = complexity_analysis.get('recommended_prompt', 'complex_macro')
            
            # Строим контекст для продвинутого промпта
            advanced_context = {
                'user_request': user_input,
                'context': self._build_advanced_context(intent, context),
                'complexity_info': complexity_analysis
            }
            
            # Получаем продвинутый промпт
            advanced_prompt = self.advanced_prompts.get_advanced_prompt(complexity_level, advanced_context)
            
            # Добавляем примеры если доступны
            enhanced_prompt = self.advanced_prompts.enhance_prompt_with_examples(advanced_prompt, user_input)
            
            self.logger.info(f"Построен продвинутый промпт: {complexity_level}")
            return enhanced_prompt
            
        except Exception as e:
            self.logger.error(f"Ошибка построения продвинутого промпта: {e}")
            return self._build_enhanced_prompt(user_input, intent, context)
    
    def _build_advanced_context(self, intent: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Построение расширенного контекста для продвинутых промптов"""
        context_parts = []
        
        # Добавляем информацию о намерениях
        context_parts.append(f"Тип задачи: {intent.get('type', 'general')}")
        if intent.get('confidence'):
            context_parts.append(f"Уверенность: {intent['confidence']}")
        
        # Добавляем доступные ресурсы
        if self.system_app_handler:
            apps = list(self.system_app_handler.get_all_system_apps().keys())[:5]
            context_parts.append(f"Доступные приложения: {', '.join(apps)}")
        
        if self.web_selector_manager:
            sites = list(self.web_selector_manager.get_all_sites().keys())[:5]
            context_parts.append(f"Поддерживаемые сайты: {', '.join(sites)}")
        
        return "; ".join(context_parts)
    
    def _validate_and_improve_dsl(self, dsl_code: str, context: Dict[str, Any], 
                                 complexity_analysis: Dict[str, Any] = None) -> tuple:
        """
        Расширенная валидация DSL с поддержкой сложных конструкций (Части 2 и 3)
        
        Args:
            dsl_code: DSL код для валидации
            context: Контекст выполнения
            complexity_analysis: Анализ сложности (опционально)
            
        Returns:
            tuple: (улучшенный_dsl_код, информация_о_валидации)
        """
        validation_info = {
            'syntax_validation': None,
            'semantic_validation': None,
            'complex_validation': None,
            'improvements_applied': [],
            'warnings': [],
            'suggestions': []
        }
        
        improved_dsl = dsl_code
        
        try:
            # Проверяем, нужна ли расширенная валидация
            requires_advanced = complexity_analysis and complexity_analysis.get('requires_advanced_features', False)
            
            if requires_advanced and self.enhanced_dsl_parser:
                # Используем расширенную валидацию для сложных макросов
                parsed_dsl = self.enhanced_dsl_parser.parse(improved_dsl)
                validation_info['complex_validation'] = {
                    'errors': parsed_dsl.errors,
                    'warnings': parsed_dsl.warnings,
                    'metadata': parsed_dsl.metadata
                }
                
                if parsed_dsl.errors:
                    validation_info['warnings'].extend([f"Сложная валидация: {error}" for error in parsed_dsl.errors])
                else:
                    # Оптимизируем DSL если возможно
                    if self.dsl_optimizer:
                        optimized_dsl = self.dsl_optimizer.optimize(parsed_dsl)
                        # TODO: Преобразование обратно в строку
                        validation_info['improvements_applied'].append("Применена оптимизация сложных конструкций")
                
                self.logger.info("Применена расширенная валидация для сложного макроса")
            
            else:
                # Используем стандартную валидацию (Часть 2)
                if self.dsl_validator:
                    syntax_result = self.dsl_validator.validate_dsl(improved_dsl, auto_fix=True)
                    validation_info['syntax_validation'] = syntax_result
                    
                    if syntax_result.fixed_code:
                        improved_dsl = syntax_result.fixed_code
                        validation_info['improvements_applied'].extend(syntax_result.fixes_applied)
                    
                    validation_info['warnings'].extend(syntax_result.warnings)
                    validation_info['suggestions'].extend(syntax_result.suggestions)
                
                # Семантическая валидация
                if self.semantic_validator:
                    semantic_result = self.semantic_validator.validate_semantics(improved_dsl, context)
                    validation_info['semantic_validation'] = semantic_result
                    
                    validation_info['warnings'].extend(semantic_result.warnings)
                    validation_info['suggestions'].extend(semantic_result.suggestions)
            
            # Форматирование кода
            if self.dsl_formatter and improved_dsl != dsl_code:
                formatted_dsl = self.dsl_formatter.format_dsl(improved_dsl)
                if formatted_dsl != improved_dsl:
                    improved_dsl = formatted_dsl
                    validation_info['improvements_applied'].append("Код отформатирован для лучшей читаемости")
            
            return improved_dsl, validation_info
            
        except Exception as e:
            self.logger.error(f"Ошибка расширенной валидации DSL: {e}")
            # Fallback к базовой валидации
            return self._validate_and_improve_dsl_basic(dsl_code, context)
    
    def _validate_and_improve_dsl_basic(self, dsl_code: str, context: Dict[str, Any]) -> tuple:
        """Базовая валидация DSL (fallback)"""
        validation_info = {
            'improvements_applied': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Минимальная валидация
        if not dsl_code or not dsl_code.strip():
            validation_info['warnings'].append("DSL код пустой")
        
        return dsl_code, validation_info
    
    def generate_and_save(self, user_input: str) -> Dict[str, Any]:
        """
        Простой интерфейс для интеграции с main.py
        Возвращает результат в формате, ожидаемом основным приложением
        """
        try:
            # Выполняем через основной метод
            module_result = self.execute(user_input)
            
            if module_result.success:
                # Возвращаем данные в формате, ожидаемом main.py
                return module_result.data
            else:
                return {
                    "success": False,
                    "error": module_result.error or "Неизвестная ошибка генерации"
                }
                
        except Exception as e:
            self.logger.error(f"Ошибка в generate_and_save: {e}")
            return {
                "success": False,
                "error": str(e)
            }
