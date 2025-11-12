# 🔧 DSL Структура - Полный анализ парсера

## 📋 Содержание
1. [Обзор DSL системы](#обзор-dsl-системы)
2. [AtlasDSLParser - главный компонент](#atlasdsлparser---главный-компонент)
3. [Система шаблонов (Templates)](#система-шаблонов-templates)
4. [Система переменных (Variables)](#система-переменных-variables)
5. [DOM селекторы](#dom-селекторы)
6. [Парсинг DSL → YAML](#парсинг-dsl--yaml)

## 🎯 Обзор DSL системы

DSL (Domain Specific Language) в Macro AI - это специализированный язык для описания автоматизации браузера. Система состоит из нескольких взаимосвязанных компонентов:

```
┌─────────────────────────────────────────────────────────────────┐
│                        DSL СИСТЕМА                              │
├─────────────────────────────────────────────────────────────────┤
│  📄 .atlas ФАЙЛЫ                                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ DSL команды     │  │ Переменные      │  │ Комментарии     │  │
│  │ open ChromeApp  │  │ ${ChromeOpen}   │  │ # Описание      │  │
│  │ click Button    │  │ ${TikTokLike}   │  │ # Метаданные    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  🔧 ATLASDSЛPARSER                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Template Map    │  │ Variables Map   │  │ DOM Selectors   │  │
│  │ (изображения)   │→ │ (переменные)    │→ │ (веб-элементы)  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  📊 YAML ВЫХОД                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Структурирован. │  │ Выполнимые      │  │ MacroSequence   │  │
│  │ последователь-  │→ │ команды для     │→ │ исполняет       │  │
│  │ ность действий  │  │ автоматизации   │  │ на macOS        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🏗️ AtlasDSLParser - главный компонент

### **Инициализация и загрузка ресурсов**
```python
class AtlasDSLParser:
    def __init__(self, templates_base_path="templates", dom_selectors_path="dom_selectors"):
        # Пути к ресурсам
        self.templates_base_path = templates_base_path
        self.dom_selectors_path = dom_selectors_path
        
        # Загрузка всех компонентов
        self.template_map = self._build_template_map()        # Карта шаблонов
        self.dom_selectors = self._load_dom_selectors()      # DOM селекторы
        self.variables = self._load_dsl_variables()          # DSL переменные
        
        # Системные команды (whitelist)
        self.system_commands_whitelist = {
            'open_app', 'close_app', 'focus_window', 
            'take_screenshot', 'copy_to_clipboard', 'read_clipboard',
            'list_processes', 'switch_desktop', 'get_current_app'
        }
```

### **Основные методы парсера**
```python
# Главный метод парсинга
def parse(self, dsl_content: str) -> Dict[str, Any]

# Парсинг отдельной строки DSL
def _parse_line(self, line: str) -> Dict[str, Any]

# Развертывание переменных
def _expand_variable(self, var_name: str, params: Dict) -> List[str]

# Разрешение переменных в значениях
def _resolve_variable(self, value: Any) -> Any
```

## 🖼️ Система шаблонов (Templates)

### **Структура шаблонов**
```
templates/
├── Chrome-TikTok-like-btn.png      # Кнопка лайка в TikTok
├── Chrome-YouTube-search.png       # Поиск на YouTube  
├── Chrome-YouTube-video.png        # Видео на YouTube
├── Atlas-ChromeNewTab.png          # Новая вкладка Chrome
└── ...
```

### **Построение карты шаблонов**
```python
def _build_template_map(self) -> Dict[str, str]:
    """
    Строит карту: короткое_имя → полный_путь_к_файлу
    
    Примеры преобразований:
    Chrome-TikTok-like-btn.png → "like-btn" → templates/Chrome-TikTok-like-btn.png
    Atlas-ChromeNewTab.png → "ChromeNewTab" → templates/Atlas-ChromeNewTab.png
    """
    template_map = {}
    
    for png_file in templates_dir.rglob("*.png"):
        full_path = str(png_file)
        short_name = png_file.stem
        
        # Очистка имени от префиксов
        clean_name = short_name
        for prefix in ["Chrome-TikTok-", "Chrome-YouTube-", "Chrome-", "Atlas-"]:
            if clean_name.startswith(prefix):
                clean_name = clean_name[len(prefix):]
        
        # Убираем суффиксы
        clean_name = clean_name.replace("-btn", "").replace("_btn", "")
        
        # Сохраняем все варианты
        template_map[short_name] = full_path      # Полное имя
        template_map[clean_name] = full_path      # Очищенное имя
        template_map[clean_name.replace("-", "_")] = full_path  # С подчеркиваниями
```

### **Использование в DSL**
```atlas
# В .atlas файле можно использовать:
click like-btn                    # Короткое имя
click Chrome-TikTok-like-btn      # Полное имя
click ChromeNewTab               # Имя без префиксов
```

### **Парсинг в YAML**
```python
# DSL команда:
click like-btn

# Преобразуется в YAML:
- action: click_template
  template: "templates/Chrome-TikTok-like-btn.png"
  confidence: 0.8
  timeout: 10
```

## 💾 Система переменных (Variables)

### **Формат файлов переменных**
```
# templates/DSL_VARIABLES.txt или dsl_references/USER_VARIABLES.txt

${ChromeOpen}
--------------------
open ChromeApp
wait 2s
click ChromeNewTab
wait 1s

${TikTokLike}
--------------------
click TikTok-like-btn
wait 1s

${YouTubeSearch:query}
--------------------
click YouTube-search
wait 1s
type "{query}"
press enter
wait 3s

ИСПОЛЬЗОВАНИЕ:
${ChromeOpen} - Открыть Chrome и новую вкладку
${TikTokLike} - Поставить лайк на TikTok
${YouTubeSearch:query} - Найти видео на YouTube
```

### **Парсинг переменных**
```python
def _load_dsl_variables(self) -> Dict[str, Dict[str, str]]:
    """
    Загружает переменные в формат:
    {
        'ChromeOpen': {
            'code': 'open ChromeApp\nwait 2s\nclick ChromeNewTab\nwait 1s',
            'params': []
        },
        'YouTubeSearch': {
            'code': 'click YouTube-search\nwait 1s\ntype "{query}"\npress enter\nwait 3s',
            'params': ['query']
        }
    }
    """
```

### **Развертывание переменных в DSL**
```python
def _expand_variable(self, var_name: str, var_params: Dict) -> List[str]:
    """
    Разворачивает переменную в список DSL команд
    
    Пример:
    ${YouTubeSearch:query="Python tutorial"}
    
    Разворачивается в:
    [
        "click YouTube-search",
        "wait 1s", 
        "type \"Python tutorial\"",
        "press enter",
        "wait 3s"
    ]
    """
```

### **Использование переменных в DSL**
```atlas
# Простая переменная без параметров
${ChromeOpen}

# Переменная с параметрами  
${YouTubeSearch:query="Python tutorial"}

# Переменная с несколькими параметрами
${TikTokComment:text="Nice video!" user="@username"}
```

## 🌐 DOM селекторы

### **Структура DOM селекторов**
```
dom_selectors/
├── tiktok/
│   └── selectors.json
├── youtube/  
│   └── selectors.json
└── chrome/
    └── selectors.json
```

### **Формат selectors.json**
```json
{
    "Chrome-TikTok-like": {
        "selector": "[data-e2e='like-button']",
        "type": "css",
        "description": "Кнопка лайка в TikTok",
        "fallback_template": "templates/Chrome-TikTok-like-btn.png"
    },
    "Chrome-YouTube-search": {
        "selector": "input#search",
        "type": "css", 
        "description": "Поле поиска YouTube",
        "fallback_template": "templates/Chrome-YouTube-search.png"
    }
}
```

### **Загрузка DOM селекторов**
```python
def _load_dom_selectors(self) -> Dict[str, Dict]:
    """
    Загружает все DOM селекторы из dom_selectors/*/selectors.json
    
    Создает карту:
    {
        'Chrome-TikTok-like': {
            'selector': '[data-e2e="like-button"]',
            'type': 'css',
            'fallback_template': 'templates/Chrome-TikTok-like-btn.png'
        }
    }
    """
```

### **Использование DOM селекторов**
```atlas
# В DSL можно использовать DOM селекторы:
click Chrome-TikTok-like      # Использует CSS селектор
                              # Fallback к template при ошибке
```

## 🔄 Парсинг DSL → YAML

### **Основной процесс парсинга**
```python
def parse(self, dsl_content: str) -> Dict[str, Any]:
    """
    Полный процесс парсинга:
    1. Разбивка на строки
    2. Обработка отступов и блоков (repeat, try)
    3. Парсинг каждой строки
    4. Развертывание переменных
    5. Формирование YAML структуры
    """
    lines = dsl_content.split('\n')
    steps = []
    block_stack = []  # Стек для вложенных блоков
    
    for line_num, line in enumerate(lines, 1):
        # Пропуск комментариев и пустых строк
        if not line.strip() or line.strip().startswith('#'):
            continue
        
        # Определение уровня отступа для блоков
        indent = len(line) - len(line.lstrip())
        
        # Выход из блоков при уменьшении отступа
        while block_stack and indent <= block_stack[-1]['indent']:
            block_stack.pop()
        
        # Парсинг строки
        step = self._parse_line(line)
        
        if step:
            # Обработка переменных
            if step['action'] == 'expand_variable':
                expanded_lines = self._expand_variable(step['variable'], step['params'])
                # Рекурсивный парсинг развернутых строк
                
            # Добавление в соответствующий блок или основную последовательность
            if block_stack:
                self._add_step_to_block(block_stack[-1], step)
            else:
                steps.append(step)
```

### **Парсинг отдельной строки**
```python
def _parse_line(self, line: str) -> Dict[str, Any]:
    """
    Парсит одну строку DSL в YAML команду
    
    Поддерживаемые команды:
    - open AppName → open_app
    - click Template → click_template  
    - type "text" → type_text
    - wait 3s → wait
    - press enter → key_press
    - scroll down → scroll
    - repeat 5: → repeat блок
    - ${Variable} → expand_variable
    """
```

### **Примеры преобразований DSL → YAML**

#### **Простые команды:**
```atlas
# DSL:
open ChromeApp
wait 2s
click ChromeNewTab
type "youtube.com"
press enter

# YAML:
steps:
  - action: open_app
    app_name: "Google Chrome"
  - action: wait
    duration: 2.0
  - action: key_combination
    keys: ["cmd", "t"]
  - action: type_text
    text: "youtube.com"
  - action: key_press
    key: "return"
```

#### **Переменные:**
```atlas
# DSL:
${ChromeOpen}
${YouTubeSearch:query="Python"}

# YAML (после развертывания):
steps:
  - action: open_app
    app_name: "Google Chrome"
  - action: wait
    duration: 2.0
  - action: key_combination
    keys: ["cmd", "t"]
  - action: wait
    duration: 1.0
  - action: click_template
    template: "templates/Chrome-YouTube-search.png"
  - action: wait
    duration: 1.0
  - action: type_text
    text: "Python"
  - action: key_press
    key: "return"
  - action: wait
    duration: 3.0
```

#### **Блоки repeat:**
```atlas
# DSL:
repeat 3:
    click TikTok-like
    wait 2s
    scroll down

# YAML:
steps:
  - action: repeat
    count: 3
    steps:
      - action: click_template
        template: "templates/Chrome-TikTok-like-btn.png"
      - action: wait
        duration: 2.0
      - action: scroll
        direction: "down"
```

## 🎯 Ключевые особенности DSL системы

### **🔧 Модульность**
- **Шаблоны** - визуальные элементы интерфейса
- **Переменные** - переиспользуемые блоки кода
- **DOM селекторы** - веб-элементы с fallback к шаблонам
- **Системные команды** - безопасные macOS операции

### **⚡ Оптимизация**
- **Кэширование** шаблонов и переменных
- **Ленивая загрузка** ресурсов
- **Умное именование** с автоматическими сокращениями

### **🛡️ Надежность**
- **Fallback механизмы** (DOM → Template → System)
- **Валидация команд** через whitelist
- **Обработка ошибок** на всех уровнях

### **🔄 Расширяемость**
- **Простое добавление** новых шаблонов
- **Создание переменных** через AI
- **Поддержка вложенности** блоков

---

**Следующие разделы:**
- [02-template-system.md](02-template-system.md) - Детальная система шаблонов
- [03-variable-system.md](03-variable-system.md) - Система переменных и параметров
- [04-yaml-generation.md](04-yaml-generation.md) - Генерация выполнимого YAML
