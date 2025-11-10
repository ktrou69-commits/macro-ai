# 🔬 MACRO AI - Техническое погружение

**Полное техническое описание всех компонентов**

---

## 📦 Зависимости (requirements.txt)

### Основные библиотеки:

```python
# Компьютерное зрение
opencv-python-headless>=4.8.0    # Обработка изображений
pillow>=10.0.0                   # Работа с изображениями
numpy>=1.24.0                    # Математика

# Автоматизация
pyautogui>=0.9.54                # Управление мышью/клавиатурой
pynput>=1.7.6                    # Мониторинг ввода

# AI
google-genai>=1.0.0              # Gemini API
ultralytics>=8.0.0               # YOLO (опционально)
torch>=2.0.0                     # PyTorch (для YOLO)

# Web автоматизация
selenium>=4.15.0                 # WebDriver
webdriver-manager>=4.0.0         # Управление драйверами
easyocr>=1.7.0                   # OCR (опционально)

# Утилиты
pyyaml>=6.0                      # YAML парсинг
python-dotenv>=1.0.0             # .env файлы
watchdog>=3.0.0                  # Мониторинг файлов
tqdm>=4.65.0                     # Прогресс бары
pyperclip>=1.8.2                 # Буфер обмена
```

---

## 🏗️ Архитектура системы

### Слои приложения:

```
┌─────────────────────────────────────────────┐
│         UI Layer (main.py)                  │
│    Интерактивное меню для пользователя     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Application Layer (src/core/)          │
│  macro_sequence.py - Оркестрация            │
│  atlas_dsl_parser.py - Парсинг              │
│  sequence_builder.py - Конструктор          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Service Layer (src/engines/)           │
│  selenium_helper.py - DOM                   │
│  parallel_runner.py - Параллелизм           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│       AI Layer (src/ai/)                    │
│  macro_generator.py - Генерация             │
│  prompt_updater.py - Обновление             │
│  dom_analyzer.py - Анализ                   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│      Data Layer (learning/, templates/)     │
│  memory.db - SQLite база                    │
│  *.png - Шаблоны кнопок                     │
│  *.json - DOM селекторы                     │
└─────────────────────────────────────────────┘
```

---

## 🔍 Детальный разбор модулей

### 1. macro_sequence.py - Сердце системы

#### Класс MacroSequence

**Инициализация:**
```python
def __init__(self, config_file, templates_dir=None, use_dom=False):
    self.config_file = Path(config_file)
    self.templates_dir = templates_dir or TEMPLATES_DIR
    self.use_dom = use_dom
    self.learning_system = LearningSystem()
    self.selenium_helper = None if not use_dom else SeleniumHelper()
```

**Загрузка конфигурации:**
```python
def load_config(self):
    # Поддержка .atlas и .yaml
    if self.config_file.suffix == '.atlas':
        parser = AtlasDSLParser(self.config_file)
        return parser.parse()
    else:
        with open(self.config_file) as f:
            return yaml.safe_load(f)
```

**Выполнение последовательности:**
```python
def execute_sequence(self, sequence_name):
    config = self.load_config()
    sequence = config['sequences'][sequence_name]
    
    for step in sequence['steps']:
        try:
            self.execute_step(step)
        except Exception as e:
            self.handle_error(step, e)
```

**Выполнение шага:**
```python
def execute_step(self, step):
    action = step['action']
    
    # Маппинг действий на методы
    actions_map = {
        'click': self.click_template,
        'wait': self.wait,
        'type': self.type_text,
        'press': self.press_key,
        'scroll': self.scroll,
        'selenium_click': self.selenium_click,
        'selenium_type': self.selenium_type,
        'selenium_read': self.selenium_read,
    }
    
    handler = actions_map.get(action)
    if handler:
        handler(step)
    else:
        raise ValueError(f"Unknown action: {action}")
```

**Template matching:**
```python
def click_template(self, step):
    template_path = self.templates_dir / step['template']
    
    # Загрузка шаблона
    template = cv2.imread(str(template_path))
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    
    # Поиск совпадения
    result = cv2.matchTemplate(screenshot_np, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # Клик если найдено
    if max_val >= step.get('threshold', 0.8):
        x, y = max_loc
        pyautogui.click(x, y)
        
        # Сохранение в learning
        self.learning_system.add_example(
            template_id=step['template'],
            screenshot=screenshot_np,
            success=True
        )
    else:
        raise TemplateNotFoundError(f"Template not found: {step['template']}")
```

---

### 2. atlas_dsl_parser.py - Парсер DSL

#### Класс AtlasDSLParser

**Структура парсера:**
```python
class AtlasDSLParser:
    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.lines = []
        self.current_line = 0
        self.sequences = {}
    
    def parse(self):
        """Главный метод парсинга"""
        self.lines = self.read_file()
        
        while self.current_line < len(self.lines):
            line = self.get_current_line()
            
            if self.is_comment(line) or self.is_empty(line):
                self.advance()
                continue
            
            if self.is_sequence_definition(line):
                self.parse_sequence()
            else:
                self.parse_command(line)
            
            self.advance()
        
        return self.build_config()
```

**Парсинг команд:**
```python
def parse_command(self, line):
    """Парсит одну команду"""
    parts = line.strip().split()
    command = parts[0].lower()
    args = parts[1:]
    
    # Маппинг команд
    command_map = {
        'click': self.parse_click,
        'wait': self.parse_wait,
        'type': self.parse_type,
        'press': self.parse_press,
        'scroll': self.parse_scroll,
        'open': self.parse_open,
        'selenium_click': self.parse_selenium_click,
        'selenium_type': self.parse_selenium_type,
        'selenium_read': self.parse_selenium_read,
        'log': self.parse_log,
        'repeat': self.parse_repeat,
    }
    
    parser = command_map.get(command)
    if parser:
        return parser(args)
    else:
        raise SyntaxError(f"Unknown command: {command}")
```

**Примеры парсинга:**
```python
def parse_click(self, args):
    """click Button"""
    return {
        'action': 'click',
        'template': args[0] + '.png',
        'threshold': 0.8
    }

def parse_wait(self, args):
    """wait 2s"""
    duration = args[0].replace('s', '')
    return {
        'action': 'wait',
        'duration': float(duration)
    }

def parse_type(self, args):
    """type "Hello World" """
    text = ' '.join(args).strip('"')
    return {
        'action': 'type',
        'text': text
    }

def parse_selenium_click(self, args):
    """selenium_click .button"""
    return {
        'action': 'selenium_click',
        'selector': args[0]
    }
```

**Обработка repeat:**
```python
def parse_repeat(self, args):
    """
    repeat 5:
        click Button
        wait 1s
    """
    count = int(args[0].replace(':', ''))
    body = []
    
    # Парсим тело цикла (с отступом)
    self.advance()
    while self.is_indented(self.get_current_line()):
        line = self.get_current_line().strip()
        body.append(self.parse_command(line))
        self.advance()
    
    return {
        'action': 'repeat',
        'count': count,
        'body': body
    }
```

---

### 3. macro_generator.py - AI генератор

#### Класс AIMacroGenerator

**Инициализация:**
```python
class AIMacroGenerator:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.macros_dir = project_root / 'macros' / 'production'
        
        # API конфигурация
        self.gemini_key = api_config.gemini_key
        self.gemini_model = api_config.gemini_model
        
        # Gemini client
        self.client = genai.Client(api_key=self.gemini_key)
        
        # Загрузка промптов
        self.templates_structure = self.load_templates_structure()
        self.best_practices = self.load_best_practices()
        self.dsl_reference = self.load_dsl_reference()
```

**Оптимизированный промпт:**
```python
def build_optimized_prompt(self, user_request):
    """Строит оптимизированный промпт (75% меньше)"""
    
    # 1. Анализ намерения
    intent = self.analyze_user_intent(user_request)
    
    # 2. Фильтрация шаблонов (только нужные)
    relevant_templates = self.filter_templates(intent)
    
    # 3. Компактная структура
    compact_structure = self.compress_structure(relevant_templates)
    
    # 4. Построение промпта
    prompt = f"""
Создай DSL макрос для: {user_request}

Доступные шаблоны:
{compact_structure}

DSL команды:
{self.dsl_reference}

Правила:
{self.best_practices}

Генерируй только DSL код, без объяснений.
"""
    
    return prompt
```

**Анализ намерения:**
```python
def analyze_user_intent(self, request):
    """Определяет что хочет пользователь"""
    request_lower = request.lower()
    
    intent = {
        'platform': None,
        'action': None,
        'elements': []
    }
    
    # Определение платформы
    platforms = {
        'youtube': ['youtube', 'ютуб'],
        'tiktok': ['tiktok', 'тикток'],
        'telegram': ['telegram', 'телеграм'],
    }
    
    for platform, keywords in platforms.items():
        if any(kw in request_lower for kw in keywords):
            intent['platform'] = platform
            break
    
    # Определение действия
    actions = {
        'like': ['лайк', 'like', 'поставь лайк'],
        'comment': ['комментарий', 'comment', 'напиши'],
        'search': ['найди', 'search', 'поиск'],
    }
    
    for action, keywords in actions.items():
        if any(kw in request_lower for kw in keywords):
            intent['action'] = action
            break
    
    return intent
```

**Фильтрация шаблонов:**
```python
def filter_templates(self, intent):
    """Возвращает только нужные шаблоны"""
    all_templates = self.templates_structure
    
    if not intent['platform']:
        return all_templates
    
    # Фильтруем по платформе
    platform = intent['platform'].title()
    filtered = {}
    
    for path, templates in all_templates.items():
        if platform in path:
            filtered[path] = templates
    
    return filtered
```

**Генерация:**
```python
def generate_with_gemini(self, prompt):
    """Генерирует код через Gemini"""
    response = self.client.models.generate_content(
        model=self.gemini_model,
        contents=prompt,
        config={
            'temperature': 0.7,
            'max_output_tokens': 1024,
        }
    )
    
    # Извлечение кода
    code = response.text
    
    # Очистка (удаление markdown)
    code = code.replace('```atlas', '').replace('```', '').strip()
    
    return code
```

---

### 4. parallel_runner.py - Параллельное выполнение

#### Класс ParallelMacroRunner

**Создание Chrome экземпляра:**
```python
def create_chrome_instance(self, instance_id, debug_port=9222, profile_dir=None):
    """Создает отдельный Chrome"""
    options = webdriver.ChromeOptions()
    
    # Уникальный профиль
    if not profile_dir:
        profile_dir = f"/tmp/chrome-profile-{instance_id}"
    options.add_argument(f"--user-data-dir={profile_dir}")
    
    # Уникальный debug порт
    port = debug_port + instance_id
    options.add_argument(f"--remote-debugging-port={port}")
    
    # Позиционирование окон
    offset = instance_id * 50
    options.add_argument(f"--window-position={offset},{offset}")
    options.add_argument(f"--window-size=800,900")
    
    # Отключение автоматизации
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Создание драйвера
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Скрытие webdriver
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    
    return driver
```

**Параллельный запуск:**
```python
def run_parallel(self, macro_file=None, url="https://tiktok.com"):
    """Запускает макросы параллельно"""
    
    # 1. Создание экземпляров Chrome
    for i in range(self.num_instances):
        profile = self.custom_profiles[i] if i < len(self.custom_profiles) else None
        driver = self.create_chrome_instance(i, profile_dir=profile)
        
        if driver:
            self.drivers.append((i, driver))
        time.sleep(1)
    
    # 2. Запуск макросов в потоках
    for instance_id, driver in self.drivers:
        macro = self.custom_macros[instance_id] if instance_id < len(self.custom_macros) else macro_file
        url_current = self.custom_urls[instance_id] if instance_id < len(self.custom_urls) else url
        
        thread = threading.Thread(
            target=self.run_macro_in_instance,
            args=(driver, instance_id, macro, url_current)
        )
        thread.start()
        self.threads.append(thread)
    
    # 3. Ожидание завершения
    for thread in self.threads:
        thread.join()
    
    # 4. Вывод результатов
    self.print_results()
```

---

### 5. dsl_simulator.py - Симулятор

#### Класс DSLSimulator

**Симуляция шага:**
```python
def _simulate_step(self, step_number, step):
    """Симулирует один шаг"""
    action = step['action']
    template_id = step.get('template_id')
    
    # Получение статистики из Learning System
    if template_id:
        stats = self.learning_system.db.get_statistics(template_id)
        probability = stats['accuracy'] if stats['total_attempts'] > 0 else 0.5
    else:
        probability = 0.95  # Высокая для простых действий
    
    # Оценка времени
    estimated_time = self.base_times.get(action, 1.0)
    
    # Корректировка для специфичных действий
    if action == 'wait':
        estimated_time = step.get('duration', 1.0)
        probability = 1.0
    elif action == 'type':
        text = step.get('text', '')
        estimated_time = len(text) * self.base_times['type']
        probability = 0.98
    elif action == 'scroll':
        amount = step.get('amount', 1)
        estimated_time = self.base_times['scroll'] * amount
        probability = 0.99
    
    # Анализ рисков
    risks = self._analyze_risks(step, probability, stats if template_id else None)
    
    # Рекомендации
    recommendations = self._generate_recommendations(step, probability, risks)
    
    return SimulationStep(
        step_number=step_number,
        action=action,
        template_id=template_id,
        probability=probability,
        estimated_time=estimated_time,
        risks=risks,
        recommendations=recommendations
    )
```

**Анализ рисков:**
```python
def _analyze_risks(self, step, probability, stats):
    """Находит потенциальные проблемы"""
    risks = []
    
    # Низкая вероятность
    if probability < 0.7:
        risks.append(f"Низкая вероятность успеха ({probability*100:.1f}%)")
    
    # Нет истории
    if stats and stats['total_attempts'] == 0:
        risks.append("Нет исторических данных - первый запуск")
    
    # Больше неудач
    if stats and stats['failed_attempts'] > stats['successful_attempts']:
        risks.append(
            f"Больше неудач чем успехов ({stats['failed_attempts']} vs {stats['successful_attempts']})"
        )
    
    # Давно не было успехов
    if stats and stats['last_success']:
        last_success = datetime.fromisoformat(stats['last_success'])
        if datetime.now() - last_success > timedelta(days=7):
            risks.append("Последний успех был более 7 дней назад")
    
    return risks
```

---

## 🗄️ База данных (learning/memory.db)

### Схема таблиц:

```sql
-- Таблица шаблонов
CREATE TABLE templates (
    template_id TEXT PRIMARY KEY,
    total_attempts INTEGER DEFAULT 0,
    successful_attempts INTEGER DEFAULT 0,
    failed_attempts INTEGER DEFAULT 0,
    accuracy REAL DEFAULT 0.0,
    last_success TIMESTAMP,
    last_failure TIMESTAMP,
    last_retrain TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица примеров
CREATE TABLE examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id TEXT,
    screenshot BLOB,
    success BOOLEAN,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context TEXT,
    FOREIGN KEY (template_id) REFERENCES templates(template_id)
);

-- Индексы
CREATE INDEX idx_template_id ON examples(template_id);
CREATE INDEX idx_timestamp ON examples(timestamp);
CREATE INDEX idx_success ON examples(success);
```

### Класс LearningDatabase:

```python
class LearningDatabase:
    def __init__(self, db_path='learning/memory.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def get_statistics(self, template_id):
        """Получить статистику шаблона"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                total_attempts,
                successful_attempts,
                failed_attempts,
                accuracy,
                last_success,
                last_failure
            FROM templates
            WHERE template_id = ?
        """, (template_id,))
        
        row = cursor.fetchone()
        if not row:
            return self.create_template_entry(template_id)
        
        return {
            'total_attempts': row[0],
            'successful_attempts': row[1],
            'failed_attempts': row[2],
            'accuracy': row[3],
            'last_success': row[4],
            'last_failure': row[5]
        }
    
    def add_example(self, template_id, screenshot, success):
        """Добавить пример выполнения"""
        cursor = self.conn.cursor()
        
        # Сохранение примера
        cursor.execute("""
            INSERT INTO examples (template_id, screenshot, success)
            VALUES (?, ?, ?)
        """, (template_id, screenshot, success))
        
        # Обновление статистики
        cursor.execute("""
            UPDATE templates
            SET 
                total_attempts = total_attempts + 1,
                successful_attempts = successful_attempts + ?,
                failed_attempts = failed_attempts + ?,
                accuracy = CAST(successful_attempts AS REAL) / total_attempts,
                last_success = CASE WHEN ? THEN CURRENT_TIMESTAMP ELSE last_success END,
                last_failure = CASE WHEN NOT ? THEN CURRENT_TIMESTAMP ELSE last_failure END
            WHERE template_id = ?
        """, (
            1 if success else 0,
            0 if success else 1,
            success,
            success,
            template_id
        ))
        
        self.conn.commit()
```

---

## 🔐 Безопасность

### API ключи (.env):
```bash
# НЕ КОММИТИТЬ В GIT!
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.0-flash
```

### .gitignore:
```
.env
*.db
__pycache__/
venv/
*.pyc
.DS_Store
```

---

## 📊 Производительность

### Оптимизации:

1. **AI промпты:** ↓75% размер
2. **Кеширование:** Структура шаблонов
3. **Параллелизм:** N потоков
4. **Lazy loading:** Шаблоны по требованию

### Метрики:

- **Template matching:** ~50ms
- **Selenium click:** ~100ms
- **AI генерация:** ~2-5s
- **Симуляция:** ~10ms

---

**Конец технического описания** 🔬
