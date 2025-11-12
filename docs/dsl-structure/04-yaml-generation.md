# 📊 Генерация YAML из DSL - Детальный анализ

## 📋 Содержание
1. [Обзор процесса генерации](#обзор-процесса-генерации)
2. [Парсинг DSL команд](#парсинг-dsl-команд)
3. [Структура YAML выхода](#структура-yaml-выхода)
4. [Обработка блоков и отступов](#обработка-блоков-и-отступов)
5. [Интеграция с MacroSequence](#интеграция-с-macrosequence)

## 🎯 Обзор процесса генерации

Генерация YAML из DSL - это ключевой процесс, который преобразует человеко-читаемый DSL код в структурированный формат для выполнения:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DSL → YAML ГЕНЕРАЦИЯ                         │
├─────────────────────────────────────────────────────────────────┤
│  📄 DSL КОД (.atlas)                                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ open ChromeApp  │  │ ${ChromeOpen}   │  │ repeat 3:       │  │
│  │ click like-btn  │  │ click search    │  │   click btn     │  │
│  │ wait 2s         │  │ type "query"    │  │   wait 1s       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  🔧 ПАРСЕР (AtlasDSLParser)                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Лексический     │→ │ Развертывание   │→ │ Структурный     │  │
│  │ анализ строк    │  │ переменных      │  │ анализ блоков   │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  📊 YAML СТРУКТУРА                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ steps:          │  │ - action: ...   │  │ MacroSequence   │  │
│  │   - action: ... │→ │   params: ...   │→ │ выполняет       │  │
│  │   - action: ... │  │   timeout: ...  │  │ на macOS        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Парсинг DSL команд

### **Главный метод парсинга**
```python
def parse(self, dsl_content: str) -> Dict[str, Any]:
    """
    Парсит DSL контент и возвращает YAML структуру
    
    Процесс:
    1. Разбивка на строки
    2. Обработка каждой строки
    3. Управление блоками и отступами
    4. Развертывание переменных
    5. Формирование финальной структуры
    """
    lines = dsl_content.split('\n')
    steps = []
    block_stack = []  # Стек для вложенных блоков
    
    for line_num, line in enumerate(lines, 1):
        # Пропуск комментариев и пустых строк
        if not line.strip() or line.strip().startswith('#'):
            continue
        
        # Определение уровня отступа
        indent = len(line) - len(line.lstrip())
        
        # Управление стеком блоков
        while block_stack and indent <= block_stack[-1]['indent']:
            block_stack.pop()
        
        # Парсинг строки
        step = self._parse_line(line)
        
        if step:
            # Обработка специальных действий
            if step['action'] == 'expand_variable':
                self._handle_variable_expansion(step, steps, block_stack)
            elif step['action'] == 'repeat':
                self._handle_repeat_block(step, block_stack, indent)
            else:
                self._add_step_to_current_context(step, steps, block_stack)
    
    return {
        'steps': steps,
        'metadata': {
            'parsed_lines': len(lines),
            'generated_steps': len(steps),
            'variables_expanded': self._count_expanded_variables()
        }
    }
```

### **Парсинг отдельной строки DSL**
```python
def _parse_line(self, line: str) -> Dict[str, Any]:
    """
    Парсит одну строку DSL в YAML команду
    
    Поддерживаемые команды:
    - open AppName
    - click TemplateName
    - type "text"
    - wait Ns
    - press key
    - scroll direction
    - repeat N:
    - ${Variable}
    """
    line_stripped = line.strip()
    
    # Переменная
    if line_stripped.startswith('${') and '}' in line_stripped:
        return self._parse_variable_usage(line_stripped)
    
    # Команды с паттернами
    command_patterns = [
        (r'^open\s+(.+)', self._parse_open_command),
        (r'^click\s+(.+)', self._parse_click_command),
        (r'^type\s+"([^"]*)"', self._parse_type_command),
        (r'^wait\s+(\d+(?:\.\d+)?)s?', self._parse_wait_command),
        (r'^press\s+(.+)', self._parse_press_command),
        (r'^scroll\s+(.+)', self._parse_scroll_command),
        (r'^repeat\s+(\d+):', self._parse_repeat_command),
        (r'^key_combination\s+(.+)', self._parse_key_combination_command)
    ]
    
    for pattern, parser in command_patterns:
        match = re.match(pattern, line_stripped, re.IGNORECASE)
        if match:
            return parser(match)
    
    # Неизвестная команда
    return {
        'action': 'unknown',
        'original_line': line_stripped,
        'error': f'Unknown DSL command: {line_stripped}'
    }
```

### **Парсеры специфических команд**

#### **1. Команда `open`**
```python
def _parse_open_command(self, match) -> Dict[str, Any]:
    """
    Парсит команду открытия приложения
    
    DSL: open ChromeApp
    YAML: action: open_app, app_name: "Google Chrome"
    """
    app_name = match.group(1).strip()
    
    # Маппинг DSL имен в системные имена приложений
    app_mapping = {
        'ChromeApp': 'Google Chrome',
        'SafariApp': 'Safari',
        'CalculatorApp': 'Calculator',
        'TerminalApp': 'Terminal',
        'FinderApp': 'Finder'
    }
    
    system_app_name = app_mapping.get(app_name, app_name)
    
    return {
        'action': 'open_app',
        'app_name': system_app_name,
        'original_name': app_name,
        'timeout': 10
    }
```

#### **2. Команда `click`**
```python
def _parse_click_command(self, match) -> Dict[str, Any]:
    """
    Парсит команду клика
    
    DSL: click like-btn
    YAML: action: click_template, template: "path/to/template.png"
    """
    element_name = match.group(1).strip()
    
    # Проверяем, есть ли шаблон
    if element_name in self.template_map:
        return {
            'action': 'click_template',
            'template': self.template_map[element_name],
            'confidence': 0.8,
            'timeout': 10,
            'original_name': element_name
        }
    
    # Проверяем DOM селектор
    elif element_name in self.dom_selectors:
        selector_data = self.dom_selectors[element_name]
        return {
            'action': 'click_dom_element',
            'selector': selector_data['selector'],
            'selector_type': selector_data['type'],
            'fallback_template': selector_data.get('fallback_template'),
            'timeout': 10,
            'original_name': element_name
        }
    
    # Элемент не найден
    else:
        return {
            'action': 'error',
            'message': f'Template or selector "{element_name}" not found',
            'original_name': element_name,
            'suggestions': self._find_similar_names(element_name)
        }
```

#### **3. Команда `type`**
```python
def _parse_type_command(self, match) -> Dict[str, Any]:
    """
    Парсит команду ввода текста
    
    DSL: type "Hello World"
    YAML: action: type_text, text: "Hello World"
    """
    text = match.group(1)
    
    return {
        'action': 'type_text',
        'text': text,
        'typing_speed': 'normal',  # normal, fast, slow
        'clear_before': False
    }
```

#### **4. Команда `wait`**
```python
def _parse_wait_command(self, match) -> Dict[str, Any]:
    """
    Парсит команду ожидания
    
    DSL: wait 2s, wait 1.5s, wait 3
    YAML: action: wait, duration: 2.0
    """
    duration_str = match.group(1)
    duration = float(duration_str)
    
    return {
        'action': 'wait',
        'duration': duration,
        'reason': 'explicit_wait'
    }
```

#### **5. Команда `press`**
```python
def _parse_press_command(self, match) -> Dict[str, Any]:
    """
    Парсит команду нажатия клавиш
    
    DSL: press enter, press escape, press tab
    YAML: action: key_press, key: "return"
    """
    key = match.group(1).strip().lower()
    
    # Маппинг DSL клавиш в системные коды
    key_mapping = {
        'enter': 'return',
        'esc': 'escape',
        'escape': 'escape',
        'tab': 'tab',
        'space': 'space',
        'backspace': 'delete',
        'delete': 'forwarddelete'
    }
    
    system_key = key_mapping.get(key, key)
    
    return {
        'action': 'key_press',
        'key': system_key,
        'original_key': key
    }
```

#### **6. Команда `scroll`**
```python
def _parse_scroll_command(self, match) -> Dict[str, Any]:
    """
    Парсит команду прокрутки
    
    DSL: scroll down, scroll up, scroll left, scroll right
    YAML: action: scroll, direction: "down"
    """
    direction = match.group(1).strip().lower()
    
    valid_directions = ['up', 'down', 'left', 'right']
    if direction not in valid_directions:
        direction = 'down'  # По умолчанию
    
    return {
        'action': 'scroll',
        'direction': direction,
        'amount': 3,  # Количество "колесиков"
        'smooth': True
    }
```

#### **7. Команда `repeat`**
```python
def _parse_repeat_command(self, match) -> Dict[str, Any]:
    """
    Парсит команду повторения
    
    DSL: repeat 5:
    YAML: action: repeat, count: 5, steps: []
    """
    count = int(match.group(1))
    
    return {
        'action': 'repeat',
        'count': count,
        'steps': [],  # Будет заполнено вложенными командами
        'break_on_error': False
    }
```

## 📊 Структура YAML выхода

### **Базовая структура**
```yaml
# Генерируемая YAML структура
steps:
  - action: open_app
    app_name: "Google Chrome"
    timeout: 10
    
  - action: wait
    duration: 2.0
    reason: "explicit_wait"
    
  - action: click_template
    template: "templates/Atlas-ChromeNewTab.png"
    confidence: 0.8
    timeout: 10
    original_name: "ChromeNewTab"
    
  - action: type_text
    text: "youtube.com"
    typing_speed: "normal"
    clear_before: false
    
  - action: key_press
    key: "return"
    original_key: "enter"

metadata:
  parsed_lines: 15
  generated_steps: 5
  variables_expanded: 2
  parsing_time: 0.045
```

### **Структура для блоков repeat**
```yaml
steps:
  - action: repeat
    count: 3
    break_on_error: false
    steps:
      - action: click_template
        template: "templates/Chrome-TikTok-like-btn.png"
        confidence: 0.8
        timeout: 10
        
      - action: wait
        duration: 1.0
        reason: "explicit_wait"
        
      - action: scroll
        direction: "down"
        amount: 3
        smooth: true
```

### **Структура для ошибок**
```yaml
steps:
  - action: error
    message: "Template 'unknown-btn' not found"
    original_name: "unknown-btn"
    suggestions: ["like-btn", "comment-btn", "share-btn"]
    line_number: 5
    recoverable: false
```

## 🔄 Обработка блоков и отступов

### **Стек блоков**
```python
def _handle_repeat_block(self, step: Dict, block_stack: List, indent: int):
    """
    Обрабатывает блок repeat и добавляет его в стек
    
    Стек блоков позволяет обрабатывать вложенные структуры:
    repeat 3:
        click btn1
        repeat 2:
            click btn2
            wait 1s
        wait 2s
    """
    # Создаем новый блок
    block = {
        'type': 'repeat',
        'step': step,
        'indent': indent,
        'parent': block_stack[-1] if block_stack else None
    }
    
    # Добавляем в стек
    block_stack.append(block)
    
    # Инициализируем пустой список шагов
    step['steps'] = []
```

### **Добавление шагов в контекст**
```python
def _add_step_to_current_context(self, step: Dict, steps: List, block_stack: List):
    """
    Добавляет шаг в текущий контекст (основной список или блок)
    """
    if block_stack:
        # Добавляем в текущий блок
        current_block = block_stack[-1]
        current_block['step']['steps'].append(step)
    else:
        # Добавляем в основной список
        steps.append(step)
```

### **Обработка отступов**
```python
def _calculate_indent_level(self, line: str) -> int:
    """
    Вычисляет уровень отступа для определения вложенности
    
    Поддерживаются:
    - Пробелы (4 пробела = 1 уровень)
    - Табы (1 таб = 1 уровень)
    """
    indent = 0
    for char in line:
        if char == ' ':
            indent += 1
        elif char == '\t':
            indent += 4  # Таб = 4 пробела
        else:
            break
    
    return indent // 4  # Уровень отступа
```

## 🔗 Интеграция с MacroSequence

### **Выполнение сгенерированного YAML**
```python
# В MacroSequence.py
def execute_yaml_sequence(self, yaml_data: Dict[str, Any]):
    """
    Выполняет последовательность из YAML данных
    
    Процесс:
    1. Валидация структуры YAML
    2. Инициализация переменных и контекста
    3. Последовательное выполнение шагов
    4. Обработка ошибок и логирование
    """
    steps = yaml_data.get('steps', [])
    metadata = yaml_data.get('metadata', {})
    
    print(f"🚀 Выполнение последовательности: {len(steps)} шагов")
    
    for i, step in enumerate(steps, 1):
        try:
            print(f"📍 Шаг {i}/{len(steps)}: {step['action']}")
            
            # Разрешение переменных в параметрах
            resolved_step = self._resolve_step_variables(step)
            
            # Выполнение шага
            success = self._execute_step(resolved_step)
            
            if not success and step.get('break_on_error', True):
                print(f"❌ Остановка на шаге {i} из-за ошибки")
                break
                
        except Exception as e:
            print(f"❌ Ошибка на шаге {i}: {e}")
            if step.get('break_on_error', True):
                break
```

### **Разрешение переменных в runtime**
```python
def _resolve_step_variables(self, step: Dict[str, Any]) -> Dict[str, Any]:
    """
    Разрешает переменные в параметрах шага во время выполнения
    
    Поддерживает:
    - ${var_name} - простые переменные
    - {runtime_var} - runtime переменные из контекста
    """
    resolved_step = step.copy()
    
    for key, value in step.items():
        if isinstance(value, str):
            resolved_step[key] = self._resolve_variable(value)
        elif isinstance(value, list):
            resolved_step[key] = [self._resolve_variable(v) if isinstance(v, str) else v for v in value]
    
    return resolved_step

def _resolve_variable(self, value):
    """Разрешение переменных вида ${var_name} и {runtime_var}"""
    if isinstance(value, str):
        # DSL переменные ${var_name}
        if value.startswith('${') and value.endswith('}'):
            var_name = value[2:-1]
            return self.dsl_variables.get(var_name, value)
        
        # Runtime переменные {var_name}
        elif value.startswith('{') and value.endswith('}'):
            var_name = value[1:-1]
            return self.runtime_variables.get(var_name, value)
    
    return value
```

### **Выполнение различных типов действий**
```python
def _execute_step(self, step: Dict[str, Any]) -> bool:
    """
    Выполняет один шаг последовательности
    
    Поддерживаемые действия:
    - open_app: Открытие приложений
    - click_template: Клик по шаблону
    - click_dom_element: Клик по DOM элементу
    - type_text: Ввод текста
    - key_press: Нажатие клавиш
    - wait: Ожидание
    - scroll: Прокрутка
    - repeat: Повторение блока
    """
    action = step['action']
    
    if action == 'open_app':
        return self._execute_open_app(step)
    elif action == 'click_template':
        return self._execute_click_template(step)
    elif action == 'click_dom_element':
        return self._execute_click_dom_element(step)
    elif action == 'type_text':
        return self._execute_type_text(step)
    elif action == 'key_press':
        return self._execute_key_press(step)
    elif action == 'wait':
        return self._execute_wait(step)
    elif action == 'scroll':
        return self._execute_scroll(step)
    elif action == 'repeat':
        return self._execute_repeat(step)
    elif action == 'error':
        print(f"❌ Ошибка в DSL: {step['message']}")
        return False
    else:
        print(f"⚠️ Неизвестное действие: {action}")
        return False
```

## 📈 Оптимизация и статистика

### **Кэширование парсинга**
```python
class AtlasDSLParser:
    def __init__(self):
        self._parsing_cache = {}
    
    def parse_with_cache(self, dsl_content: str) -> Dict[str, Any]:
        """Парсинг с кэшированием для оптимизации"""
        content_hash = hashlib.md5(dsl_content.encode()).hexdigest()
        
        if content_hash in self._parsing_cache:
            print("📋 Использование кэшированного результата парсинга")
            return self._parsing_cache[content_hash]
        
        result = self.parse(dsl_content)
        self._parsing_cache[content_hash] = result
        
        return result
```

### **Статистика парсинга**
```python
def get_parsing_statistics(self) -> Dict[str, Any]:
    """Получение статистики парсинга"""
    return {
        'total_files_parsed': len(self._parsing_cache),
        'templates_loaded': len(self.template_map),
        'variables_loaded': len(self.variables),
        'dom_selectors_loaded': len(self.dom_selectors),
        'cache_hit_rate': self._calculate_cache_hit_rate(),
        'average_parsing_time': self._calculate_average_parsing_time()
    }
```

---

**Заключение:**
Система DSL → YAML генерации обеспечивает мощный и гибкий способ преобразования человеко-читаемых команд в выполнимые инструкции для автоматизации macOS. Поддержка переменных, блоков, шаблонов и DOM селекторов делает систему универсальной для различных сценариев автоматизации.
