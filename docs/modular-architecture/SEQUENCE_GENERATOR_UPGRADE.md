# 🔧 План Улучшения sequence_generator Module

## 🎯 Цель Этапа
Превратить базовый sequence_generator в **мощный универсальный модуль автоматизации**, способный создавать сложные многошаговые макросы для любых приложений macOS.

---

## 📋 ЧАСТЬ 1: Расширение Типов Автоматизации (3-4 дня)

### 🎯 Цель
Добавить поддержку системных приложений macOS и расширить возможности автоматизации

### 📱 Новые Категории Приложений

#### 1.1 Системные Приложения macOS
```yaml
# Добавить в resources/system_apps.yaml
system_apps:
  Calculator:
    bundle_id: "com.apple.calculator"
    launch_command: "open -a Calculator"
    common_elements:
      - "button_1": "//XCUIElementTypeButton[@name='1']"
      - "button_plus": "//XCUIElementTypeButton[@name='+']"
      - "button_equals": "//XCUIElementTypeButton[@name='=']"
  
  Finder:
    bundle_id: "com.apple.finder"
    launch_command: "open -a Finder"
    common_elements:
      - "search_field": "//XCUIElementTypeSearchField"
      - "sidebar_applications": "//XCUIElementTypeOutlineRow[@name='Applications']"
  
  System_Preferences:
    bundle_id: "com.apple.systempreferences"
    launch_command: "open -a 'System Preferences'"
    common_elements:
      - "search_field": "//XCUIElementTypeSearchField"
```

#### 1.2 Spotlight Integration
```python
# Добавить в src/modules/sequence_generator/spotlight_integration.py
class SpotlightIntegration:
    """Интеграция со Spotlight поиском"""
    
    def generate_spotlight_macro(self, search_term: str, action: str = "open"):
        """Генерация макроса для Spotlight поиска"""
        return f"""
# Spotlight поиск: {search_term}
key cmd+space
wait 0.5s
type "{search_term}"
wait 1s
press enter
wait 2s
"""
```

#### 1.3 Расширенные Web Автоматизации
```yaml
# Расширить dom_selectors.yaml
advanced_web_selectors:
  youtube:
    video_player: "//div[@id='movie_player']"
    like_button: "//button[@aria-label='Like this video']"
    subscribe_button: "//button[contains(@aria-label, 'Subscribe')]"
    comment_box: "//div[@id='placeholder-area']"
  
  google:
    search_suggestions: "//ul[@role='listbox']//li"
    search_filters: "//div[@id='hdtb-msb']//a"
    images_tab: "//a[contains(@href, 'tbm=isch')]"
```

### 🛠️ Технические Задачи

#### День 1-2: Системные приложения
```bash
# 1. Создать system_apps.yaml с конфигурациями
touch src/modules/sequence_generator/resources/system_apps.yaml

# 2. Добавить SystemAppHandler
touch src/modules/sequence_generator/handlers/system_app_handler.py

# 3. Интегрировать в основной модуль
# Обновить module.py для поддержки системных приложений
```

#### День 3: Spotlight интеграция
```bash
# 1. Создать SpotlightIntegration класс
touch src/modules/sequence_generator/integrations/spotlight_integration.py

# 2. Добавить Spotlight команды в DSL
# Расширить AtlasDSL поддержкой: spotlight "search_term"
```

#### День 4: Расширенные web селекторы
```bash
# 1. Обновить dom_selectors.yaml
# Добавить селекторы для популярных сайтов

# 2. Создать WebSelectorManager
touch src/modules/sequence_generator/managers/web_selector_manager.py
```

### ✅ Критерии Успеха Части 1
- ✅ Поддержка 10+ системных приложений macOS
- ✅ Spotlight интеграция работает
- ✅ 50+ новых web селекторов добавлено
- ✅ Все новые возможности протестированы

---

## 📋 ЧАСТЬ 2: Улучшенный AI и Валидация (2-3 дня)

### 🎯 Цель
Сделать AI генерацию более точной и добавить автоматическую валидацию DSL кода

### 🤖 Улучшения AI Промптов

#### 2.1 Контекстно-зависимые Промпты
```python
# src/modules/sequence_generator/prompts/context_aware_prompts.py
class ContextAwarePrompts:
    """Промпты, адаптирующиеся под тип задачи"""
    
    PROMPTS = {
        "web_automation": """
Ты эксперт по веб-автоматизации. Создай DSL макрос для веб-браузера.

ДОСТУПНЫЕ WEB КОМАНДЫ:
- navigate "url" - переход на страницу
- click_element "selector" - клик по элементу
- fill_field "selector" "text" - заполнение поля
- wait_for_element "selector" - ожидание элемента

КОНТЕКСТ: {web_selectors}
ЗАДАЧА: {user_request}
""",
        
        "system_automation": """
Ты эксперт по автоматизации macOS. Создай DSL макрос для системных приложений.

ДОСТУПНЫЕ SYSTEM КОМАНДЫ:
- open_app "app_name" - открытие приложения
- spotlight_search "query" - поиск через Spotlight
- system_key "key_combination" - системные горячие клавиши

КОНТЕКСТ: {system_apps}
ЗАДАЧА: {user_request}
""",
        
        "mixed_automation": """
Ты универсальный эксперт по автоматизации. Создай комплексный DSL макрос.

ДОСТУПНЫЕ КОМАНДЫ:
- Веб: navigate, click_element, fill_field
- Система: open_app, spotlight_search, system_key
- Базовые: wait, type, click, key

КОНТЕКСТ: {all_resources}
ЗАДАЧА: {user_request}
"""
    }
```

#### 2.2 Примеры для AI (Few-Shot Learning)
```python
# src/modules/sequence_generator/prompts/examples.py
AI_EXAMPLES = {
    "youtube_automation": {
        "request": "открой YouTube и найди видео про Python",
        "response": """
НАЗВАНИЕ: Поиск видео на YouTube

DSL КОД:
```atlas
# Открытие YouTube и поиск видео
open ChromeApp
wait 2s
navigate "https://youtube.com"
wait 3s
click_element "//input[@id='search']"
type "Python tutorial"
press enter
wait 2s
click_element "//div[@id='contents']//a[1]"
```

ОПИСАНИЕ: Автоматически открывает YouTube, выполняет поиск и кликает на первое видео
"""
    },
    
    "calculator_automation": {
        "request": "открой калькулятор и посчитай 25 + 17",
        "response": """
НАЗВАНИЕ: Вычисление в Калькуляторе

DSL КОД:
```atlas
# Открытие калькулятора и вычисление
open_app "Calculator"
wait 2s
click "button_2"
click "button_5"
click "button_plus"
click "button_1"
click "button_7"
click "button_equals"
wait 1s
```

ОПИСАНИЕ: Открывает калькулятор и выполняет вычисление 25 + 17
"""
    }
}
```

### 🔍 DSL Валидация и Исправление

#### 2.3 Syntax Validator
```python
# src/modules/sequence_generator/validators/dsl_validator.py
class DSLValidator:
    """Валидатор DSL синтаксиса"""
    
    VALID_COMMANDS = {
        'open', 'open_app', 'click', 'type', 'wait', 'press', 
        'navigate', 'click_element', 'fill_field', 'spotlight_search'
    }
    
    def validate_dsl(self, dsl_code: str) -> ValidationResult:
        """Валидация DSL кода"""
        errors = []
        warnings = []
        suggestions = []
        
        lines = dsl_code.strip().split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Проверка команд
            command = line.split()[0] if line.split() else ""
            if command not in self.VALID_COMMANDS:
                errors.append(f"Строка {i}: Неизвестная команда '{command}'")
                suggestion = self._suggest_command(command)
                if suggestion:
                    suggestions.append(f"Возможно, вы имели в виду '{suggestion}'?")
        
        return ValidationResult(errors, warnings, suggestions)
    
    def auto_fix_common_errors(self, dsl_code: str) -> str:
        """Автоматическое исправление частых ошибок"""
        # Исправление типичных опечаток
        fixes = {
            'opne': 'open',
            'clik': 'click', 
            'typ': 'type',
            'wiat': 'wait'
        }
        
        for wrong, correct in fixes.items():
            dsl_code = dsl_code.replace(wrong, correct)
        
        return dsl_code
```

#### 2.4 Semantic Validator
```python
# src/modules/sequence_generator/validators/semantic_validator.py
class SemanticValidator:
    """Семантическая валидация DSL"""
    
    def validate_app_availability(self, dsl_code: str) -> List[str]:
        """Проверка доступности приложений"""
        warnings = []
        
        # Извлечение приложений из DSL
        apps = self._extract_apps(dsl_code)
        
        for app in apps:
            if not self._is_app_installed(app):
                warnings.append(f"Приложение '{app}' не установлено")
        
        return warnings
    
    def validate_timing(self, dsl_code: str) -> List[str]:
        """Проверка таймингов"""
        suggestions = []
        
        # Анализ wait команд
        waits = self._extract_waits(dsl_code)
        
        for wait_time in waits:
            if wait_time < 0.5:
                suggestions.append("Рекомендуется wait минимум 0.5s для стабильности")
            elif wait_time > 10:
                suggestions.append(f"Wait {wait_time}s может быть слишком долгим")
        
        return suggestions
```

### 🛠️ Технические Задачи

#### День 1: Улучшенные промпты
```bash
# 1. Создать context-aware промпты
touch src/modules/sequence_generator/prompts/context_aware_prompts.py

# 2. Добавить примеры для AI
touch src/modules/sequence_generator/prompts/examples.py

# 3. Интегрировать в module.py
# Обновить логику выбора промптов
```

#### День 2: DSL валидация
```bash
# 1. Создать валидаторы
mkdir src/modules/sequence_generator/validators
touch src/modules/sequence_generator/validators/{dsl_validator.py,semantic_validator.py}

# 2. Интегрировать валидацию в pipeline
# Добавить валидацию перед сохранением макроса
```

#### День 3: Автоматическое исправление
```bash
# 1. Реализовать auto-fix функции
# 2. Добавить user feedback для исправлений
# 3. Создать тесты для валидации
```

### ✅ Критерии Успеха Части 2
- ✅ AI генерирует более точные макросы (90%+ success rate)
- ✅ DSL валидация работает и находит ошибки
- ✅ Автоматическое исправление частых опечаток
- ✅ Контекстно-зависимые промпты улучшают качество

---

## 📋 ЧАСТЬ 3: Многошаговые Макросы и Условная Логика (2-3 дня)

### 🎯 Цель
Добавить поддержку сложных многошаговых макросов с условной логикой и циклами

### 🔄 Расширение DSL Синтаксиса

#### 3.1 Условная Логика
```atlas
# Новый синтаксис для условий
if element_exists "//button[@id='login']"
    click "//button[@id='login']"
    wait 2s
    type_in_field "//input[@name='username']" "user@example.com"
else
    click "//button[@id='signup']"
    wait 2s
endif

# Проверка текста на странице
if page_contains "Welcome back"
    click "//a[text()='Dashboard']"
else
    click "//a[text()='Get Started']"
endif
```

#### 3.2 Циклы и Повторения
```atlas
# Цикл с счетчиком
repeat 3 times
    click "//button[@class='next']"
    wait 2s
end_repeat

# Цикл до условия
while element_exists "//button[@class='load-more']"
    click "//button[@class='load-more']"
    wait 3s
    if page_contains "No more items"
        break
    endif
end_while

# Цикл по списку элементов
for_each "//div[@class='item']" as item
    click item
    wait 1s
    if element_exists "//button[@class='delete']"
        click "//button[@class='delete']"
        wait 1s
    endif
end_for
```

#### 3.3 Переменные и Параметры
```atlas
# Объявление переменных
set search_term = "Python tutorial"
set max_results = 5

# Использование переменных
navigate "https://youtube.com"
wait 2s
type_in_field "//input[@id='search']" $search_term
press enter
wait 2s

# Параметры макроса (передаются при запуске)
param username = "default_user"
param password = "default_pass"

type_in_field "//input[@name='username']" $username
type_in_field "//input[@name='password']" $password
```

### 🏗️ Архитектурные Изменения

#### 3.4 Enhanced DSL Parser
```python
# src/modules/sequence_generator/parsers/enhanced_dsl_parser.py
class EnhancedDSLParser:
    """Расширенный парсер DSL с поддержкой условий и циклов"""
    
    def __init__(self):
        self.variables = {}
        self.parameters = {}
        
    def parse_conditional(self, lines: List[str], start_idx: int) -> Tuple[ConditionalBlock, int]:
        """Парсинг условных блоков"""
        condition = self._parse_condition(lines[start_idx])
        
        if_block = []
        else_block = []
        current_block = if_block
        
        i = start_idx + 1
        while i < len(lines):
            line = lines[i].strip()
            
            if line == "else":
                current_block = else_block
            elif line == "endif":
                break
            else:
                current_block.append(line)
            i += 1
        
        return ConditionalBlock(condition, if_block, else_block), i
    
    def parse_loop(self, lines: List[str], start_idx: int) -> Tuple[LoopBlock, int]:
        """Парсинг циклов"""
        loop_header = lines[start_idx].strip()
        
        if loop_header.startswith("repeat"):
            return self._parse_repeat_loop(lines, start_idx)
        elif loop_header.startswith("while"):
            return self._parse_while_loop(lines, start_idx)
        elif loop_header.startswith("for_each"):
            return self._parse_foreach_loop(lines, start_idx)
```

#### 3.5 Execution Engine
```python
# src/modules/sequence_generator/executors/enhanced_executor.py
class EnhancedExecutor:
    """Исполнитель расширенного DSL"""
    
    def execute_conditional(self, block: ConditionalBlock) -> bool:
        """Выполнение условного блока"""
        if self._evaluate_condition(block.condition):
            return self._execute_block(block.if_block)
        else:
            return self._execute_block(block.else_block)
    
    def execute_loop(self, block: LoopBlock) -> bool:
        """Выполнение цикла"""
        if isinstance(block, RepeatLoop):
            return self._execute_repeat_loop(block)
        elif isinstance(block, WhileLoop):
            return self._execute_while_loop(block)
        elif isinstance(block, ForEachLoop):
            return self._execute_foreach_loop(block)
    
    def _evaluate_condition(self, condition: Condition) -> bool:
        """Оценка условия"""
        if condition.type == "element_exists":
            return self._check_element_exists(condition.selector)
        elif condition.type == "page_contains":
            return self._check_page_contains(condition.text)
        elif condition.type == "variable_equals":
            return self.variables.get(condition.var_name) == condition.value
```

### 🤖 AI Генерация Сложных Макросов

#### 3.6 Advanced Prompt Templates
```python
# src/modules/sequence_generator/prompts/advanced_prompts.py
ADVANCED_MACRO_PROMPT = """
Ты эксперт по созданию сложных многошаговых макросов автоматизации.

ДОСТУПНЫЕ РАСШИРЕННЫЕ КОМАНДЫ:
- Условия: if element_exists/page_contains ... else ... endif
- Циклы: repeat N times, while condition, for_each selector
- Переменные: set var_name = "value", использование $var_name
- Параметры: param name = "default_value"

ПРИМЕРЫ СЛОЖНЫХ МАКРОСОВ:

1. Условная логика:
```atlas
if element_exists "//button[@id='login']"
    click "//button[@id='login']"
    type_in_field "//input[@name='email']" $email
else
    click "//a[text()='Sign Up']"
endif
```

2. Циклы:
```atlas
repeat 5 times
    click "//button[@class='next']"
    wait 2s
    if page_contains "End of results"
        break
    endif
end_repeat
```

КОНТЕКСТ: {context}
ЗАДАЧА: {user_request}

Создай СЛОЖНЫЙ многошаговый макрос с использованием условий, циклов или переменных где это уместно.
"""
```

### 🛠️ Технические Задачи

#### День 1: Расширение DSL синтаксиса
```bash
# 1. Создать новые DSL конструкции
touch src/modules/sequence_generator/dsl/{conditions.py,loops.py,variables.py}

# 2. Обновить базовый парсер
# Добавить поддержку новых команд в AtlasDSLParser
```

#### День 2: Enhanced Parser и Executor
```bash
# 1. Создать расширенный парсер
mkdir src/modules/sequence_generator/parsers
touch src/modules/sequence_generator/parsers/enhanced_dsl_parser.py

# 2. Создать новый исполнитель
mkdir src/modules/sequence_generator/executors  
touch src/modules/sequence_generator/executors/enhanced_executor.py
```

#### День 3: AI интеграция и тестирование
```bash
# 1. Обновить AI промпты для сложных макросов
# 2. Интегрировать новые возможности в module.py
# 3. Создать comprehensive тесты
# 4. Обновить документацию
```

### ✅ Критерии Успеха Части 3
- ✅ Поддержка условной логики (if/else)
- ✅ Поддержка циклов (repeat, while, for_each)
- ✅ Система переменных и параметров
- ✅ AI генерирует сложные многошаговые макросы
- ✅ Backward compatibility с существующими макросами

---

## 📊 Общие Критерии Успеха Всего Этапа

### 🎯 Функциональные Требования
- ✅ **Поддержка 15+ типов приложений** (системные + web)
- ✅ **DSL валидация** с автоматическим исправлением
- ✅ **Условная логика** и циклы в макросах
- ✅ **95%+ success rate** для стандартных сценариев
- ✅ **Backward compatibility** со всеми существующими макросами

### ⚡ Производительность
- ✅ **Генерация макроса** < 5 секунд
- ✅ **Валидация DSL** < 1 секунды
- ✅ **Memory usage** < 150MB для модуля

### 🧪 Тестирование
- ✅ **Unit тесты** для всех новых компонентов
- ✅ **Integration тесты** для сложных сценариев
- ✅ **Performance тесты** для больших макросов
- ✅ **Regression тесты** для существующей функциональности

---

## 🚀 План Реализации (7 дней)

### 📅 Детальный Timeline

**День 1-2: Расширение автоматизации**
- Создать system_apps.yaml
- Реализовать SystemAppHandler
- Добавить Spotlight интеграцию
- Расширить web селекторы

**День 3-4: AI и валидация**
- Создать контекстно-зависимые промпты
- Реализовать DSL валидацию
- Добавить автоматическое исправление
- Интегрировать примеры для AI

**День 5-6: Сложные макросы**
- Расширить DSL синтаксис
- Создать enhanced parser
- Реализовать новый executor
- Обновить AI промпты

**День 7: Финализация**
- Comprehensive тестирование
- Обновление документации
- Performance оптимизация
- Подготовка к следующему этапу

---

## 🎉 Ожидаемый Результат

После завершения этого этапа **sequence_generator** станет **мощнейшим модулем автоматизации**, способным:

- 🤖 **Создавать сложные многошаговые макросы** с условиями и циклами
- 🖥️ **Автоматизировать любые приложения macOS** - от системных до веб
- 🔍 **Автоматически валидировать и исправлять** DSL код
- 🧠 **Генерировать более точные макросы** благодаря улучшенному AI
- 📝 **Поддерживать переменные и параметры** для гибкости

**Это будет фундамент для создания по-настоящему умного голосового помощника на следующем этапе!** 🚀
