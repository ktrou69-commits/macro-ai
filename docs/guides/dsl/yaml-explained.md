# 🎯 DSL + YAML - Как это работает

## 📖 Архитектура проекта

### 1. Три уровня работы с шаблонами

```
┌─────────────────────────────────────────────────────────────┐
│  1. ФИЗИЧЕСКИЕ ФАЙЛЫ (templates/)                          │
│     templates/Chrome/Chrome-TikTok-Like.png                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  2. КАРТА ИМЕН (atlas_dsl_parser.py)                        │
│     Chrome-TikTok-Like → templates/Chrome/Chrome-TikTok-Like.png │
│     TikTok-Like → templates/Chrome/Chrome-TikTok-Like.png   │
│     Like → templates/Chrome/Chrome-TikTok-Like.png          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  3. ИСПОЛЬЗОВАНИЕ В КОДЕ                                    │
│     DSL:  click Chrome-TikTok-Like                          │
│     YAML: template: templates/Chrome/Chrome-TikTok-Like.png │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Что обновляет Path Watcher

### ✅ Path Watcher ОБНОВЛЯЕТ:

**YAML файлы с прямыми путями:**
```yaml
# ДО перемещения
- action: click
  template: templates/Chrome/ChromeBasicGuiButtons/Chrome-TikTok-Like.png

# ПОСЛЕ перемещения (автоматически)
- action: click
  template: templates/Chrome/Chrome-TikTok-Like.png
```

**Python файлы:**
```python
# ДО
template_path = "templates/Chrome/ChromeBasicGuiButtons/Chrome-TikTok-Like.png"

# ПОСЛЕ (автоматически)
template_path = "templates/Chrome/Chrome-TikTok-Like.png"
```

---

### ❌ Path Watcher НЕ ОБНОВЛЯЕТ:

**DSL файлы (.atlas) с именами шаблонов:**
```atlas
# Это ИМЯ, а не путь
click Chrome-TikTok-Like  # ← НЕ изменится

# Потому что:
# - Chrome-TikTok-Like это КОРОТКОЕ ИМЯ
# - Путь к файлу разрешается динамически в atlas_dsl_parser.py
```

---

## 🎯 Как работает DSL

### Шаг 1: Ты пишешь DSL (.atlas файл)

```atlas
# examples/tiktok_auto_like.atlas
click Chrome-TikTok-Like
wait 1.5s
scroll down
```

### Шаг 2: DSL парсер строит карту имен

```python
# atlas_dsl_parser.py → _build_template_map()

template_map = {
    # Полное имя файла
    "Chrome-TikTok-Like": "templates/Chrome/Chrome-TikTok-Like.png",
    
    # Без префикса "Chrome-"
    "TikTok-Like": "templates/Chrome/Chrome-TikTok-Like.png",
    
    # Без префикса и суффикса "-btn"
    "Like": "templates/Chrome/Chrome-TikTok-Like.png",
}
```

**Как это работает:**
```python
def _build_template_map(self):
    # 1. Сканирует templates/ рекурсивно
    for png_file in templates_dir.rglob("*.png"):
        # 2. Создает короткие имена
        short_name = png_file.stem  # "Chrome-TikTok-Like"
        
        # 3. Убирает префиксы
        clean_name = short_name
        for prefix in ["Chrome-TikTok-", "Chrome-", "Atlas-"]:
            if clean_name.startswith(prefix):
                clean_name = clean_name[len(prefix):]
        
        # 4. Убирает суффиксы
        clean_name = clean_name.replace("-btn", "")
        
        # 5. Сохраняет все варианты
        template_map[short_name] = full_path  # Chrome-TikTok-Like
        template_map[clean_name] = full_path  # Like
```

### Шаг 3: DSL парсер разрешает имена

```python
# atlas_dsl_parser.py → _resolve_template()

def _resolve_template(self, name: str):
    # Ищет в карте
    if name in self.template_map:
        return self.template_map[name]
    
    # Если не найдено, добавляет templates/ и .png
    return f"templates/{name}.png"
```

**Пример:**
```python
_resolve_template("Chrome-TikTok-Like")
# → "templates/Chrome/Chrome-TikTok-Like.png"

_resolve_template("Like")
# → "templates/Chrome/Chrome-TikTok-Like.png"

_resolve_template("TikTok-Like")
# → "templates/Chrome/Chrome-TikTok-Like.png"
```

### Шаг 4: DSL парсер конвертирует в YAML

```python
# click Chrome-TikTok-Like
# ↓
{
    'action': 'click',
    'template': 'templates/Chrome/Chrome-TikTok-Like.png'
}
```

### Шаг 5: macro_sequence.py выполняет

```python
# Читает YAML
step = {'action': 'click', 'template': 'templates/Chrome/Chrome-TikTok-Like.png'}

# Находит шаблон на экране
location = pyautogui.locateOnScreen('templates/Chrome/Chrome-TikTok-Like.png')

# Кликает
pyautogui.click(location)
```

---

## 🔄 Полный цикл

```
1. Ты пишешь DSL:
   click Chrome-TikTok-Like

2. atlas_dsl_parser.py сканирует templates/:
   Chrome-TikTok-Like → templates/Chrome/Chrome-TikTok-Like.png

3. atlas_dsl_parser.py конвертирует в YAML:
   action: click
   template: templates/Chrome/Chrome-TikTok-Like.png

4. macro_sequence.py выполняет:
   pyautogui.locateOnScreen('templates/Chrome/Chrome-TikTok-Like.png')
   pyautogui.click(location)
```

---

## 💡 Почему Path Watcher не обновляет .atlas файлы

### Причина 1: Имена, а не пути

```atlas
click Chrome-TikTok-Like  # ← Это ИМЯ шаблона
```

Path Watcher ищет **пути к файлам**, например:
```yaml
template: templates/Chrome/Chrome-TikTok-Like.png  # ← Это ПУТЬ
```

### Причина 2: Динамическое разрешение

DSL парсер **каждый раз** сканирует `templates/` и строит карту имен.

**Пример:**
```bash
# Переместил файл
mv templates/Chrome/ChromeBasicGuiButtons/Chrome-TikTok-Like.png \
   templates/Chrome/Chrome-TikTok-Like.png

# DSL парсер при следующем запуске:
# 1. Сканирует templates/
# 2. Находит templates/Chrome/Chrome-TikTok-Like.png
# 3. Создает: Chrome-TikTok-Like → templates/Chrome/Chrome-TikTok-Like.png
# 4. DSL файл работает БЕЗ изменений!
```

### Причина 3: Множественные имена

Один файл может иметь несколько имен:
```python
# templates/Chrome/Chrome-TikTok-Like.png доступен как:
click Chrome-TikTok-Like  # Полное имя
click TikTok-Like         # Без префикса
click Like                # Короткое имя
```

Path Watcher не знает какое имя используется в DSL.

---

## 🎯 Что нужно обновлять вручную

### Если переименовал файл:

**ДО:**
```
templates/Chrome/Chrome-TikTok-Like.png
```

**ПОСЛЕ:**
```
templates/Chrome/Chrome-TikTok-Heart.png
```

**DSL файл нужно обновить:**
```atlas
# ДО
click Chrome-TikTok-Like

# ПОСЛЕ (вручную)
click Chrome-TikTok-Heart
```

**YAML файл обновится автоматически:**
```yaml
# ДО
template: templates/Chrome/Chrome-TikTok-Like.png

# ПОСЛЕ (автоматически через Path Watcher)
template: templates/Chrome/Chrome-TikTok-Heart.png
```

---

## 📊 Сравнение DSL vs YAML

| Аспект | DSL (.atlas) | YAML (.yaml) |
|--------|--------------|--------------|
| **Синтаксис** | `click Chrome-TikTok-Like` | `template: templates/Chrome/Chrome-TikTok-Like.png` |
| **Использует** | Короткие имена | Полные пути |
| **Path Watcher** | ❌ Не обновляет | ✅ Обновляет |
| **Разрешение имен** | Динамическое (при запуске) | Статическое (в файле) |
| **Переименование файла** | ⚠️ Нужно обновить вручную | ✅ Обновится автоматически |
| **Перемещение файла** | ✅ Работает без изменений | ✅ Обновится автоматически |

---

## 🛠️ Улучшение Path Watcher для DSL

Чтобы Path Watcher обновлял и DSL файлы, нужно:

### Вариант 1: Отслеживать переименования

```python
# В path_watcher.py
def on_moved(self, event):
    old_name = Path(event.src_path).stem  # Chrome-TikTok-Like
    new_name = Path(event.dest_path).stem  # Chrome-TikTok-Heart
    
    if old_name != new_name:
        # Обновить DSL файлы
        update_dsl_files(old_name, new_name)
```

### Вариант 2: Использовать полные пути в DSL

```atlas
# Вместо
click Chrome-TikTok-Like

# Использовать
click (templates/Chrome/Chrome-TikTok-Like.png)
```

Тогда Path Watcher сможет обновлять.

---

## 🎉 Итоги

### DSL (.atlas):
- ✅ Использует короткие имена
- ✅ Автоматически находит файлы при запуске
- ✅ Перемещение файлов работает без изменений
- ⚠️ Переименование требует ручного обновления

### YAML (.yaml):
- ✅ Использует полные пути
- ✅ Path Watcher автоматически обновляет
- ✅ Перемещение и переименование работают автоматически

### Path Watcher:
- ✅ Обновляет YAML файлы
- ✅ Обновляет Python файлы
- ✅ Обновляет Markdown файлы
- ❌ Не обновляет DSL имена (они динамические)

---

**Рекомендация:**  
Для максимальной автоматизации используй YAML для прямых путей и DSL для коротких имен. Path Watcher будет обновлять YAML автоматически! 🚀
