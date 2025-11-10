# 🧪 Тест резолюции имен для YouTube

## 📁 Файл: `Chrome-YouTube-logo-btn.png`

### Как парсер обрабатывает:

```python
# Шаг 1: Извлечение имени без расширения
short_name = "Chrome-YouTube-logo-btn"

# Шаг 2: Сохранение полного имени
template_map["Chrome-YouTube-logo-btn"] = "templates/Chrome/YouTube/Chrome-YouTube-logo-btn.png"

# Шаг 3: Убираем префиксы
clean_name = "Chrome-YouTube-logo-btn"

# Проверяем префиксы:
prefixes = ["Chrome-TikTok-", "Chrome-YouTube-", "Chrome-", "Atlas-"]

# Совпадение: "Chrome-YouTube-"
clean_name = "logo-btn"  # Убрали "Chrome-YouTube-"

# Шаг 4: Убираем суффиксы
clean_name = clean_name.replace("-btn", "")
clean_name = "logo"

# Сохраняем
template_map["logo"] = "templates/Chrome/YouTube/Chrome-YouTube-logo-btn.png"

# Шаг 5: С подчеркиваниями
template_map["logo"] = "templates/Chrome/YouTube/Chrome-YouTube-logo-btn.png"
```

### Результат в template_map:

```python
template_map = {
    "Chrome-YouTube-logo-btn": "templates/Chrome/YouTube/Chrome-YouTube-logo-btn.png",
    "logo": "templates/Chrome/YouTube/Chrome-YouTube-logo-btn.png",
}
```

---

## ✅ Что работает в DSL:

```atlas
click Chrome-YouTube-logo-btn      ✅ Полное имя
click logo                         ✅ Короткое имя
click LOGO                         ✅ Без учета регистра
```

## ❌ Что НЕ работает:

```atlas
click Chrome-YouTube-logo          ❌ Нужно добавить -btn или убрать префикс
click YouTube-logo                 ❌ Нет в карте
```

---

## 🎯 Рекомендация для TEMPLATES_STRUCTURE.txt

### Текущая версия:
```
YouTube:
  • Chrome-YouTube-logo      - Логотип YouTube
```

### Проблема:
`Chrome-YouTube-logo` НЕ работает! Парсер создает только:
- `Chrome-YouTube-logo-btn` (полное)
- `logo` (короткое)

### Исправленная версия:
```
YouTube:
  • Chrome-YouTube-logo-btn  - Логотип YouTube (полное имя)
  • logo                     - Логотип YouTube (короткое имя)
```

**ИЛИ** (если хочешь использовать `YouTube-logo`):
```
YouTube:
  • logo                     - Логотип YouTube (рекомендуется)
  • Chrome-YouTube-logo-btn  - Логотип YouTube (полное имя)
```

---

## 💡 Решение проблемы

### Вариант 1: Использовать короткое имя `logo`

```atlas
click logo  ✅ Работает!
```

**Проблема:** Слишком общее имя. Если есть другие `logo` (TikTok, Instagram), будет конфликт!

---

### Вариант 2: Добавить префикс в парсер

Обнови `atlas_dsl_parser.py`:

```python
def _build_template_map(self) -> Dict[str, str]:
    # ...
    
    # Убираем префиксы типа "Chrome-TikTok-"
    clean_name = short_name
    for prefix in ["Chrome-TikTok-", "Chrome-YouTube-", "Chrome-", "Atlas-"]:
        if clean_name.startswith(prefix):
            clean_name = clean_name[len(prefix):]
    
    # Убираем суффиксы типа "-btn"
    clean_name = clean_name.replace("-btn", "").replace("_btn", "")
    
    # Сохраняем оба варианта
    template_map[short_name] = full_path
    template_map[clean_name] = full_path
    
    # ⭐ ДОБАВЬ ЭТО:
    # Сохраняем вариант с частичным префиксом (YouTube-logo, TikTok-Like)
    if "-" in short_name:
        parts = short_name.split("-")
        if len(parts) >= 3:  # Chrome-YouTube-logo-btn
            # Берем последние 2 части без суффикса
            partial_name = "-".join(parts[-2:]).replace("-btn", "")
            template_map[partial_name] = full_path
    
    # Также сохраняем с заменой дефисов на подчеркивания
    template_map[clean_name.replace("-", "_")] = full_path
```

### Теперь работает:

```python
template_map = {
    "Chrome-YouTube-logo-btn": путь,  # Полное
    "logo": путь,                     # Короткое
    "YouTube-logo": путь,             # ⭐ Частичное (новое!)
}
```

```atlas
click YouTube-logo  ✅ Работает!
```

---

## 🎨 Рекомендация для всех платформ

### В TEMPLATES_STRUCTURE.txt указывай ТРИ варианта:

```
YouTube:
  • YouTube-logo             - Логотип YouTube (рекомендуется для DSL)
  • logo                     - Логотип (короткое, может конфликтовать)
  • Chrome-YouTube-logo-btn  - Логотип (полное имя файла)

TikTok:
  • TikTok-Like              - Лайк видео (рекомендуется для DSL)
  • Like                     - Лайк (короткое)
  • Chrome-TikTok-Like-btn   - Лайк (полное имя файла)
```

### В DSL используй средний вариант:

```atlas
# YouTube
click YouTube-logo         ✅ Понятно и уникально
click YouTube-Subscribe    ✅ Понятно и уникально

# TikTok
click TikTok-Like          ✅ Понятно и уникально
click TikTok-Comment       ✅ Понятно и уникально
```

---

## 🔧 Нужно ли обновлять парсер?

### Текущее состояние:

Для `Chrome-YouTube-logo-btn.png` работают только:
- `Chrome-YouTube-logo-btn` ✅
- `logo` ✅

### Если хочешь чтобы работало `YouTube-logo`:

**ДА, нужно обновить парсер!**

Добавь код который я показал выше в `atlas_dsl_parser.py`.

---

## 🎯 Итоги

### Для файла `Chrome-YouTube-logo-btn.png`:

**Сейчас работают:**
- ✅ `Chrome-YouTube-logo-btn` (полное)
- ✅ `logo` (короткое)

**НЕ работают:**
- ❌ `Chrome-YouTube-logo` (нет -btn)
- ❌ `YouTube-logo` (нужно обновить парсер)

### Рекомендации:

**Вариант 1: Используй короткое имя**
```atlas
click logo  ✅
```

**Вариант 2: Обнови парсер для поддержки `YouTube-logo`**
```python
# Добавь код в atlas_dsl_parser.py
```

**Вариант 3: Используй полное имя**
```atlas
click Chrome-YouTube-logo-btn  ✅
```

---

**Хочешь чтобы я обновил парсер для поддержки `YouTube-logo`?** 🔧
