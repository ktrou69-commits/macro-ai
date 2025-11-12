"""
Контекстно-зависимые промпты для улучшенной AI генерации
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ContextAwarePrompts:
    """Промпты, адаптирующиеся под тип задачи"""
    
    PROMPTS = {
        "web_automation": """
Ты эксперт по веб-автоматизации. Создай DSL макрос для веб-браузера.

ДОСТУПНЫЕ WEB КОМАНДЫ (через Selenium):
- selenium_init url=https://site.com - инициализация браузера и переход на URL
- selenium_find selector="#element_id" save_to=var_name - поиск элемента
- selenium_click selector="#element_id" - клик по элементу
- selenium_type selector="#input_field" text="текст" - заполнение поля
- selenium_scroll direction=down amount=3 - прокрутка страницы
- selenium_close - закрытие браузера
- wait 3s - ожидание загрузки

СПЕЦИАЛЬНЫЕ СЕЛЕКТОРЫ:
{web_selectors}

КОНТЕКСТ САЙТА: {site_context}

ЗАДАЧА: {user_request}

ФОРМАТ ОТВЕТА:
НАЗВАНИЕ: [Краткое название макроса]

DSL КОД:
```atlas
# Комментарий к макросу
[DSL команды]
```

ОПИСАНИЕ: [Подробное описание что делает макрос]
""",
        
        "system_automation": """
Ты эксперт по автоматизации macOS. Создай DSL макрос для системных приложений.

ДОСТУПНЫЕ SYSTEM КОМАНДЫ:
- @system open_app "app_name" - открытие приложения
- key cmd+space - системные горячие клавиши (Spotlight)
- type "query" - ввод текста для поиска
- press enter - нажатие клавиши
- click ElementName - клик по элементу приложения (шаблон)
- wait 3s - ожидание в секундах
- hotkey cmd+c - комбинация клавиш

ДОСТУПНЫЕ ПРИЛОЖЕНИЯ:
{system_apps}

СИСТЕМНЫЕ ГОРЯЧИЕ КЛАВИШИ:
{system_shortcuts}

КОНТЕКСТ ПРИЛОЖЕНИЯ: {app_context}

ЗАДАЧА: {user_request}

ФОРМАТ ОТВЕТА:
НАЗВАНИЕ: [Краткое название макроса]

DSL КОД:
```atlas
# Комментарий к макросу
[DSL команды]
```

ОПИСАНИЕ: [Подробное описание что делает макрос]
""",
        
        "spotlight_automation": """
Ты эксперт по Spotlight поиску macOS. Создай DSL макрос для поиска и запуска.

ДОСТУПНЫЕ SPOTLIGHT КОМАНДЫ:
- key "cmd+space" - открытие Spotlight
- type "search_query" - ввод поискового запроса
- press "enter" - подтверждение выбора
- key "down" - навигация по результатам
- key "up" - навигация вверх по результатам
- wait "time" - ожидание

ПОПУЛЯРНЫЕ ПОИСКИ:
{spotlight_searches}

ЗАДАЧА: {user_request}

ФОРМАТ ОТВЕТА:
НАЗВАНИЕ: [Краткое название макроса]

DSL КОД:
```atlas
# Комментарий к макросу
[DSL команды]
```

ОПИСАНИЕ: [Подробное описание что делает макрос]
""",
        
        "mixed_automation": """
Ты универсальный эксперт по автоматизации macOS. Создай комплексный DSL макрос.

ДОСТУПНЫЕ КОМАНДЫ:

ВЕБ-АВТОМАТИЗАЦИЯ (через Selenium):
- selenium_init url=https://site.com - инициализация браузера и переход на URL
- selenium_find selector="css_selector" save_to=var_name - поиск элемента
- selenium_click selector="css_selector" - клик по веб-элементу  
- selenium_type selector="css_selector" text="текст" - заполнение поля
- selenium_close - закрытие браузера

СИСТЕМНАЯ АВТОМАТИЗАЦИЯ:
- @system open_app "app_name" - открытие приложения
- open AppName - запуск приложения через шаблон
- key cmd+space - системные горячие клавиши
- type "текст для поиска" - ввод текста

БАЗОВЫЕ КОМАНДЫ:
- wait 3s - ожидание (3 секунды)
- type "text" - ввод текста
- click ElementName - клик по элементу (шаблон)
- press enter - нажатие клавиши
- hotkey cmd+c - комбинация клавиш

ДОСТУПНЫЕ РЕСУРСЫ:
{all_resources}

ЗАДАЧА: {user_request}

ФОРМАТ ОТВЕТА:
НАЗВАНИЕ: [Краткое название макроса]

DSL КОД:
```atlas
# Комментарий к макросу
[DSL команды с пояснениями]
```

ОПИСАНИЕ: [Подробное описание что делает макрос и как он работает]
""",
        
        "calculator_automation": """
Ты эксперт по автоматизации калькулятора macOS. Создай DSL макрос для математических вычислений.

ДОСТУПНЫЕ КОМАНДЫ КАЛЬКУЛЯТОРА:
- @system open_app "Calculator" - открытие калькулятора
- click button_0 до button_9 - цифры (без кавычек)
- click button_plus - сложение (+)
- click button_minus - вычитание (−)
- click button_multiply - умножение (×)
- click button_divide - деление (÷)
- click button_equals - равно (=)
- click button_clear - очистка (C)
- click button_decimal - десятичная точка (.)

ЭЛЕМЕНТЫ КАЛЬКУЛЯТОРА:
{calculator_elements}

МАТЕМАТИЧЕСКОЕ ВЫРАЖЕНИЕ: {math_expression}
ЗАДАЧА: {user_request}

ФОРМАТ ОТВЕТА:
НАЗВАНИЕ: Вычисление: {math_expression}

DSL КОД:
```atlas
# Вычисление математического выражения: {math_expression}
[DSL команды для последовательных кликов по кнопкам]
```

ОПИСАНИЕ: Автоматически выполняет вычисление {math_expression} в калькуляторе macOS
"""
    }
    
    @classmethod
    def get_prompt_for_intent(cls, intent_type: str, context: Dict[str, Any]) -> str:
        """
        Получение промпта для конкретного типа намерения
        
        Args:
            intent_type: Тип намерения (web_automation, system_automation, etc.)
            context: Контекст для подстановки в промпт
            
        Returns:
            Сформированный промпт
        """
        try:
            if intent_type not in cls.PROMPTS:
                logger.warning(f"Неизвестный тип намерения: {intent_type}, используем mixed_automation")
                intent_type = "mixed_automation"
            
            prompt_template = cls.PROMPTS[intent_type]
            
            # Подставляем контекст в промпт
            formatted_prompt = prompt_template.format(**context)
            
            logger.info(f"Сформирован промпт для типа: {intent_type}")
            return formatted_prompt
            
        except KeyError as e:
            logger.error(f"Отсутствует ключ в контексте: {e}")
            # Возвращаем базовый промпт
            return cls.PROMPTS["mixed_automation"].format(
                all_resources="Контекст недоступен",
                user_request=context.get("user_request", "Неизвестная задача")
            )
        except Exception as e:
            logger.error(f"Ошибка формирования промпта: {e}")
            return cls._get_fallback_prompt(context.get("user_request", ""))
    
    @classmethod
    def _get_fallback_prompt(cls, user_request: str) -> str:
        """Резервный промпт при ошибках"""
        return f"""
Создай DSL макрос для автоматизации.

ЗАДАЧА: {user_request}

ДОСТУПНЫЕ КОМАНДЫ:
- open - открыть приложение
- click - кликнуть по элементу
- type - ввести текст
- wait - подождать
- key - нажать клавишу

ФОРМАТ ОТВЕТА:
НАЗВАНИЕ: [Название макроса]

DSL КОД:
```atlas
# Комментарий
[DSL команды]
```

ОПИСАНИЕ: [Описание макроса]
"""
    
    @classmethod
    def get_available_prompt_types(cls) -> list:
        """Получение списка доступных типов промптов"""
        return list(cls.PROMPTS.keys())
    
    @classmethod
    def add_custom_prompt(cls, prompt_type: str, prompt_template: str):
        """Добавление пользовательского промпта"""
        cls.PROMPTS[prompt_type] = prompt_template
        logger.info(f"Добавлен пользовательский промпт: {prompt_type}")


class PromptContextBuilder:
    """Построитель контекста для промптов"""
    
    def __init__(self):
        self.context = {}
    
    def add_web_context(self, site_name: str, selectors: Dict[str, str]):
        """Добавление веб-контекста"""
        self.context["site_context"] = f"Сайт: {site_name}"
        self.context["web_selectors"] = self._format_selectors(selectors)
        return self
    
    def add_system_context(self, app_name: str, app_elements: Dict[str, str]):
        """Добавление системного контекста"""
        self.context["app_context"] = f"Приложение: {app_name}"
        self.context["system_apps"] = app_name
        self.context["calculator_elements"] = self._format_elements(app_elements)
        return self
    
    def add_spotlight_context(self, searches: list):
        """Добавление Spotlight контекста"""
        self.context["spotlight_searches"] = "\n".join([f"- {search}" for search in searches[:10]])
        return self
    
    def add_math_context(self, expression: str):
        """Добавление математического контекста"""
        self.context["math_expression"] = expression
        return self
    
    def add_user_request(self, request: str):
        """Добавление пользовательского запроса"""
        self.context["user_request"] = request
        return self
    
    def add_all_resources(self, resources: Dict[str, Any]):
        """Добавление всех доступных ресурсов"""
        formatted_resources = []
        
        for resource_type, resource_data in resources.items():
            if isinstance(resource_data, dict) and "available" in resource_data:
                items = resource_data["available"][:5]  # Ограничиваем количество
                formatted_resources.append(f"{resource_type.upper()}: {', '.join(map(str, items))}")
        
        self.context["all_resources"] = "\n".join(formatted_resources)
        return self
    
    def build(self) -> Dict[str, Any]:
        """Построение финального контекста"""
        # Добавляем значения по умолчанию для отсутствующих ключей
        defaults = {
            "web_selectors": "Веб-селекторы недоступны",
            "site_context": "Контекст сайта недоступен",
            "system_apps": "Системные приложения недоступны",
            "app_context": "Контекст приложения недоступен",
            "system_shortcuts": "Горячие клавиши недоступны",
            "spotlight_searches": "Поиски недоступны",
            "calculator_elements": "Элементы калькулятора недоступны",
            "math_expression": "Выражение не определено",
            "all_resources": "Ресурсы недоступны",
            "user_request": "Задача не определена"
        }
        
        for key, default_value in defaults.items():
            if key not in self.context:
                self.context[key] = default_value
        
        return self.context.copy()
    
    def _format_selectors(self, selectors: Dict[str, str]) -> str:
        """Форматирование селекторов для промпта"""
        if not selectors:
            return "Селекторы недоступны"
        
        formatted = []
        for name, selector in list(selectors.items())[:10]:  # Ограничиваем количество
            formatted.append(f"- {name}: {selector}")
        
        return "\n".join(formatted)
    
    def _format_elements(self, elements: Dict[str, str]) -> str:
        """Форматирование элементов для промпта"""
        if not elements:
            return "Элементы недоступны"
        
        formatted = []
        for name, element in elements.items():
            formatted.append(f"- {name}: {element}")
        
        return "\n".join(formatted)
