# 🎯 Как работает вся система - Подробно

## ✅ Твое понимание ПРАВИЛЬНОЕ!

```
Физический файл → Короткий тег → Использование в DSL → Клик
```

**Именно так!** Давай разберем каждый шаг детально.

---

## 🔍 Полный цикл работы

### Шаг 1: Физические файлы

**У тебя есть файл:**
```
templates/Chrome/ChromeBasicGuiButtons/ChromeSearchField-btn.png
```

Это скриншот кнопки поиска в Chrome.

---

### Шаг 2: Создание карты имен (при запуске)

**Когда ты запускаешь:**
```bash
python3 macro_sequence.py --config examples/tiktok_auto_like.atlas --run tiktok_auto_like
```

**Что происходит:**

#### 2.1. Создается AtlasDSLParser

```python
# atlas_dsl_parser.py строка 28-30
def __init__(self, templates_base_path: str = "templates"):
    self.templates_base_path = templates_base_path
    self.template_map = self._build_template_map()  # ← ЗДЕСЬ!
```

#### 2.2. Сканируются все PNG файлы

```python
# atlas_dsl_parser.py строка 42-47
templates_dir = Path("templates")

# Находим ВСЕ .png файлы рекурсивно
for png_file in templates_dir.rglob("*.png"):
    # png_file = templates/Chrome/ChromeBasicGuiButtons/ChromeSearchField-btn.png
```

#### 2.3. Создаются короткие имена

```python
# atlas_dsl_parser.py строка 48-68

# Полный путь
full_path = "templates/Chrome/ChromeBasicGuiButtons/ChromeSearchField-btn.png"

# Короткое имя (без расширения)
short_name = png_file.stem  # "ChromeSearchField-btn"

# Убираем префиксы
clean_name = short_name
for prefix in ["Chrome-TikTok-", "Chrome-YouTube-", "Chrome-", "Atlas-"]:
    if clean_name.startswith(prefix):
        clean_name = clean_name[len(prefix):]

# clean_name = "SearchField-btn" (убрали "Chrome-")

# Убираем суффиксы
clean_name = clean_name.replace("-btn", "").replace("_btn", "")
# clean_name = "SearchField" (убрали "-btn")

# Сохраняем ВСЕ варианты
template_map["ChromeSearchField-btn"] = full_path  # Полное имя
template_map["ChromeSearchField"] = full_path      # Без -btn
template_map["SearchField"] = full_path            # Без Chrome- и -btn
```

**Результат - карта имен:**
```python
template_map = {
    "ChromeSearchField-btn": "templates/Chrome/ChromeBasicGuiButtons/ChromeSearchField-btn.png",
    "ChromeSearchField": "templates/Chrome/ChromeBasicGuiButtons/ChromeSearchField-btn.png",
    "SearchField": "templates/Chrome/ChromeBasicGuiButtons/ChromeSearchField-btn.png",
}
```

**Теперь можно использовать ЛЮБОЕ из этих имен в DSL!**

---

### Шаг 3: Парсинг DSL файла

**Ты пишешь в DSL:**
```atlas
click ChromeSearchField
```

**Что происходит:**

#### 3.1. Парсер читает строку

```python
# atlas_dsl_parser.py строка 120-121
if line.startswith('click '):
    template_name = line[6:].strip()
    # template_name = "ChromeSearchField"
```

#### 3.2. Парсер ищет файл по имени

```python
# atlas_dsl_parser.py строка 136
template_path = self._resolve_template(template_name)
# template_path = self._resolve_template("ChromeSearchField")
```

#### 3.3. _resolve_template находит путь

```python
# atlas_dsl_parser.py строка 72-85
def _resolve_template(self, name: str):
    # Ищет в карте
    if name in self.template_map:
        return self.template_map[name]
    
    # "ChromeSearchField" в template_map? ДА!
    # Возвращает: "templates/Chrome/ChromeBasicGuiButtons/ChromeSearchField-btn.png"
```

#### 3.4. Создается YAML шаг

```python
# atlas_dsl_parser.py строка 137-142
return {
    'action': 'click',
    'template': 'templates/Chrome/ChromeBasicGuiButtons/ChromeSearchField-btn.png',
    'clicks': 1,
    'description': 'Клик по ChromeSearchField'
}
```

---

### Шаг 4: Конвертация всего DSL в YAML

**Весь твой DSL файл:**
```atlas
# TikTok Auto Like
open ChromeApp
wait 2.5s
click ChromeNewTab
wait 0.5s
click ChromeSearchField
type "tiktok.com"
press enter
wait 4s
repeat 10:
  click Chrome-TikTok-Like
  wait 1.5s
  scroll down
  wait 2s
```

**Конвертируется в YAML структуру (в памяти!):**
```python
{
    'name': 'TikTok Auto Like',
    'steps': [
        {
            'action': 'click',
            'template': 'templates/Chrome/ChromeBasicGuiButtons/ChromeApp-btn.png',
            'clicks': 1,
            'description': 'Запуск ChromeApp'
        },
        {
            'action': 'wait',
            'duration': 2.5,
            'description': 'Ожидание 2.5s'
        },
        {
            'action': 'click',
            'template': 'templates/Chrome/ChromeBasicGuiButtons/ChromeNewTab-btn.png',
            'clicks': 1,
            'description': 'Клик по ChromeNewTab'
        },
        {
            'action': 'wait',
            'duration': 0.5,
            'description': 'Ожидание 0.5s'
        },
        {
            'action': 'click',
            'template': 'templates/Chrome/ChromeBasicGuiButtons/ChromeSearchField-btn.png',
            'clicks': 1,
            'description': 'Клик по ChromeSearchField'
        },
        {
            'action': 'type',
            'text': 'tiktok.com',
            'description': 'Ввод текста: tiktok.com'
        },
        {
            'action': 'press',
            'key': 'enter',
            'description': 'Нажатие клавиши: enter'
        },
        {
            'action': 'wait',
            'duration': 4.0,
            'description': 'Ожидание 4s'
        },
        {
            'action': 'repeat',
            'times': 10,
            'steps': [
                {
                    'action': 'click',
                    'template': 'templates/Chrome/Chrome-TikTok-Like.png',
                    'clicks': 1,
                    'description': 'Клик по Chrome-TikTok-Like'
                },
                {
                    'action': 'wait',
                    'duration': 1.5,
                    'description': 'Ожидание 1.5s'
                },
                {
                    'action': 'scroll',
                    'direction': 'down',
                    'description': 'Прокрутка вниз'
                },
                {
                    'action': 'wait',
                    'duration': 2.0,
                    'description': 'Ожидание 2s'
                }
            ],
            'description': 'Повторить 10 раз'
        }
    ]
}
```

**Это все происходит В ПАМЯТИ! Файл НЕ создается!** 🚀

---

### Шаг 5: Выполнение шагов

**macro_sequence.py выполняет каждый шаг:**

```python
# Для шага: click ChromeSearchField
step = {
    'action': 'click',
    'template': 'templates/Chrome/ChromeBasicGuiButtons/ChromeSearchField-btn.png',
    'clicks': 1
}

# 1. Загружает изображение шаблона
template_img = cv2.imread('templates/Chrome/ChromeBasicGuiButtons/ChromeSearchField-btn.png')

# 2. Делает скриншот экрана
screenshot = pyautogui.screenshot()

# 3. Ищет шаблон на экране
location = pyautogui.locateOnScreen(template_img)
# location = (x=500, y=100, width=200, height=30)

# 4. Кликает по центру найденного шаблона
center = pyautogui.center(location)
# center = (x=600, y=115)

pyautogui.click(center)
# ✅ КЛИК!
```

---

## 🎯 Ответы на твои вопросы

### 1. Правильно ли я понимаю?

**ДА! Абсолютно правильно!** ✅

```
1. Берется физический файл
   templates/Chrome/ChromeBasicGuiButtons/ChromeSearchField-btn.png

2. Создается короткий тег
   ChromeSearchField → templates/Chrome/ChromeBasicGuiButtons/ChromeSearchField-btn.png

3. В .atlas вводим
   click ChromeSearchField

4. Система кликает именно на него
   pyautogui.click(найденная_позиция)
```

---

### 2. Куда возвращается YAML?

**В ПАМЯТЬ! Файл НЕ создается!** 🎉

```python
# atlas_dsl_parser.py
def parse(self, dsl_content: str) -> Dict[str, Any]:
    """
    Парсит DSL контент и возвращает YAML структуру
    
    Returns:
        Dict с последовательностью в формате YAML
    """
    # Парсит DSL
    steps = []
    for line in dsl_content.split('\n'):
        step = self._parse_line(line)
        if step:
            steps.append(step)
    
    # Возвращает Python словарь (НЕ файл!)
    return {
        'name': 'Sequence Name',
        'steps': steps
    }
```

**Что происходит:**

```python
# macro_sequence.py строка 105-107
parser = AtlasDSLParser()
parsed = parser.parse_file("examples/tiktok_auto_like.atlas")
# parsed = {'name': '...', 'steps': [...]}  ← Python словарь в памяти!

# Сохраняется в переменную
self.config = {
    'sequences': {
        'tiktok_auto_like': parsed  # ← В памяти!
    }
}
```

**Файл YAML НЕ создается!** Все происходит в памяти во время выполнения!

---

### 3. Когда это происходит?

**ДА! Прямо в момент запуска!** 🚀

```bash
python3 macro_sequence.py --config examples/tiktok_auto_like.atlas --run tiktok_auto_like
```

**Что происходит:**

```
1. Запуск скрипта
   ↓
2. Создание AtlasDSLParser
   ↓
3. Сканирование templates/ → Создание карты имен (в памяти)
   ↓
4. Чтение tiktok_auto_like.atlas
   ↓
5. Парсинг DSL → YAML структура (в памяти)
   ↓
6. Выполнение шагов один за другим
   ↓
7. Завершение
```

**Все происходит В ПАМЯТИ! Никакие файлы не создаются!** 🎉

---

## 📊 Визуальная схема

```
┌─────────────────────────────────────────────────────────────┐
│  ЗАПУСК                                                     │
│  python3 macro_sequence.py --config tiktok_auto_like.atlas  │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│  СКАНИРОВАНИЕ templates/                                    │
│  Находит все .png файлы                                     │
│  Создает карту имен В ПАМЯТИ:                               │
│  ChromeSearchField → templates/.../ChromeSearchField-btn.png│
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│  ЧТЕНИЕ DSL ФАЙЛА                                           │
│  click ChromeSearchField                                    │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│  ПАРСИНГ DSL → YAML (В ПАМЯТИ)                              │
│  {                                                          │
│    'action': 'click',                                       │
│    'template': 'templates/.../ChromeSearchField-btn.png'    │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────┐
│  ВЫПОЛНЕНИЕ                                                 │
│  1. Загружает шаблон ChromeSearchField-btn.png              │
│  2. Делает скриншот экрана                                  │
│  3. Ищет шаблон на экране                                   │
│  4. Кликает по найденной позиции                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 Ключевые моменты

### 1. Карта имен создается КАЖДЫЙ РАЗ при запуске

```python
# При каждом запуске:
parser = AtlasDSLParser()  # ← Сканирует templates/
```

**Поэтому:**
- ✅ Переместил файл → Работает автоматически
- ✅ Добавил новый файл → Сразу доступен
- ✅ Удалил файл → Сразу недоступен

### 2. YAML создается В ПАМЯТИ

```python
parsed = parser.parse_file("file.atlas")  # ← Python словарь
# НЕ создается файл .yaml!
```

**Поэтому:**
- ✅ Быстро (нет записи на диск)
- ✅ Чисто (нет временных файлов)
- ✅ Динамично (каждый раз заново)

### 3. Один файл может иметь много имен

```python
# Файл: ChromeSearchField-btn.png
template_map = {
    "ChromeSearchField-btn": "...",  # Полное имя
    "ChromeSearchField": "...",      # Без -btn
    "SearchField": "...",            # Короткое
}
```

**Можешь использовать любое:**
```atlas
click ChromeSearchField-btn  # ✅ Работает
click ChromeSearchField      # ✅ Работает
click SearchField            # ✅ Работает
```

---

## 🎉 Итоги

### Твое понимание ПРАВИЛЬНОЕ! ✅

```
Физический файл → Короткий тег → DSL → Клик
```

### YAML создается В ПАМЯТИ! 🚀

```python
parsed = parser.parse_file("file.atlas")  # ← Словарь в памяти
# Файл НЕ создается!
```

### Все происходит при запуске! ⚡

```bash
python3 macro_sequence.py --config file.atlas --run name
# ↓
# Сканирование → Парсинг → Выполнение
# Все в памяти!
```

---

**Да, это действительно круто!** 🎉

Вся система работает динамически в памяти, без создания временных файлов. Это делает ее быстрой, чистой и гибкой! 🚀
