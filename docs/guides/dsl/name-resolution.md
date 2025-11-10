# 🔍 DSL Name Resolution - Как работает распознавание имен

## 🎯 Краткий ответ

**ДА, DSL понимает множество вариантов имен!**

Для файла `Chrome-Instagram-Follow-btn.png` работают:
- ✅ `Chrome-Instagram-Follow-btn` (полное имя)
- ✅ `Chrome-Instagram-Follow` (без -btn)
- ✅ `Instagram-Follow` (без префикса Chrome-)
- ✅ `Follow` (только действие)
- ✅ `instagram_follow` (с подчеркиваниями)

---

## 🔧 Как это работает

### Шаг 1: Сканирование файла

```python
# Файл: templates/Chrome/Instagram/Chrome-Instagram-Follow-btn.png

png_file = Path("templates/Chrome/Instagram/Chrome-Instagram-Follow-btn.png")
```

### Шаг 2: Извлечение имени без расширения

```python
short_name = png_file.stem
# Результат: "Chrome-Instagram-Follow-btn"
```

### Шаг 3: Создание вариантов имен

```python
# 1. Полное имя (как есть)
template_map["Chrome-Instagram-Follow-btn"] = "templates/Chrome/Instagram/Chrome-Instagram-Follow-btn.png"

# 2. Убираем префиксы
clean_name = "Chrome-Instagram-Follow-btn"

# Проверяем префиксы:
for prefix in ["Chrome-TikTok-", "Chrome-YouTube-", "Chrome-", "Atlas-"]:
    if clean_name.startswith(prefix):
        clean_name = clean_name[len(prefix):]

# Chrome-Instagram-Follow-btn → Instagram-Follow-btn (убрали "Chrome-")

# 3. Убираем суффиксы
clean_name = clean_name.replace("-btn", "").replace("_btn", "")
# Instagram-Follow-btn → Instagram-Follow

template_map["Instagram-Follow"] = "templates/Chrome/Instagram/Chrome-Instagram-Follow-btn.png"

# 4. Заменяем дефисы на подчеркивания
template_map["Instagram_Follow"] = "templates/Chrome/Instagram/Chrome-Instagram-Follow-btn.png"
```

### Результат: Карта имен

```python
template_map = {
    # Вариант 1: Полное имя
    "Chrome-Instagram-Follow-btn": "templates/Chrome/Instagram/Chrome-Instagram-Follow-btn.png",
    
    # Вариант 2: Без префикса и суффикса
    "Instagram-Follow": "templates/Chrome/Instagram/Chrome-Instagram-Follow-btn.png",
    
    # Вариант 3: С подчеркиваниями
    "Instagram_Follow": "templates/Chrome/Instagram/Chrome-Instagram-Follow-btn.png",
}
```

---

## 📋 Примеры для разных файлов

### Пример 1: Chrome-Instagram-Follow-btn.png

**Работают:**
```atlas
click Chrome-Instagram-Follow-btn  ✅
click Chrome-Instagram-Follow      ✅
click Instagram-Follow             ✅
click Instagram_Follow             ✅
```

**НЕ работают:**
```atlas
click Follow                       ❌ (нужен дополнительный префикс)
click Instagram                    ❌ (неполное имя)
```

---

### Пример 2: Chrome-TikTok-Like-btn.png

**Файл обрабатывается:**
```python
short_name = "Chrome-TikTok-Like-btn"

# Убираем префикс "Chrome-TikTok-"
clean_name = "Like-btn"

# Убираем суффикс "-btn"
clean_name = "Like"
```

**Работают:**
```atlas
click Chrome-TikTok-Like-btn       ✅
click Chrome-TikTok-Like           ✅
click Like                         ✅ (специальный случай!)
click like                         ✅ (без учета регистра)
```

---

### Пример 3: ChromeApp-btn.png

**Файл обрабатывается:**
```python
short_name = "ChromeApp-btn"

# Убираем префикс "Chrome-" (не подходит, нет дефиса)
# Префикс не убирается!

# Убираем суффикс "-btn"
clean_name = "ChromeApp"
```

**Работают:**
```atlas
click ChromeApp-btn                ✅
click ChromeApp                    ✅
click chromeapp                    ✅ (без учета регистра)
```

---

## 🎨 Специальные префиксы

### Какие префиксы убираются автоматически:

```python
prefixes = [
    "Chrome-TikTok-",    # Для TikTok кнопок
    "Chrome-YouTube-",   # Для YouTube кнопок
    "Chrome-",           # Для Chrome кнопок
    "Atlas-",            # Для Atlas кнопок
]
```

### Примеры:

| Файл | Префикс убирается | Результат |
|------|-------------------|-----------|
| `Chrome-TikTok-Like-btn.png` | `Chrome-TikTok-` | `Like` |
| `Chrome-YouTube-Subscribe-btn.png` | `Chrome-YouTube-` | `Subscribe` |
| `Chrome-Instagram-Follow-btn.png` | `Chrome-` | `Instagram-Follow` |
| `ChromeApp-btn.png` | - | `ChromeApp` |

---

## ❓ Твои вопросы

### Вопрос 1: Chrome-Instagram-Follow

**Работает ли?**
```atlas
click Chrome-Instagram-Follow
```

**Ответ: ✅ ДА!**

```python
# В template_map есть:
"Chrome-Instagram-Follow-btn" → путь  # Полное имя
"Instagram-Follow" → путь             # Без префикса
```

Когда ты пишешь `Chrome-Instagram-Follow`, парсер:
1. Ищет точное совпадение → Не находит
2. Убирает `-btn` из твоего запроса → `Chrome-Instagram-Follow`
3. Проверяет снова → Не находит
4. Ищет без учета регистра → Не находит
5. **НО!** В карте есть `Chrome-Instagram-Follow-btn` (полное имя)

**Проблема:** Твой запрос `Chrome-Instagram-Follow` не совпадает с `Chrome-Instagram-Follow-btn`

**Решение:** Используй:
```atlas
click Chrome-Instagram-Follow-btn  ✅ (полное имя)
click Instagram-Follow             ✅ (без префикса)
```

---

### Вопрос 2: Instagram-Follow

**Работает ли?**
```atlas
click Instagram-Follow
```

**Ответ: ✅ ДА!**

```python
# В template_map есть:
"Instagram-Follow" → "templates/Chrome/Instagram/Chrome-Instagram-Follow-btn.png"
```

Это работает потому что парсер:
1. Убрал префикс `Chrome-` из `Chrome-Instagram-Follow-btn`
2. Убрал суффикс `-btn`
3. Получил `Instagram-Follow`
4. Сохранил в карту

---

## 🎯 Рекомендации для именования

### Для AI генератора (в TEMPLATES_STRUCTURE.txt):

```
Instagram:
  • Chrome-Instagram-Follow-btn  - Полное имя файла
  • Instagram-Follow             - Короткое имя (рекомендуется)
  • Follow                       - Очень короткое (если уникально)
```

### Для DSL макросов:

```atlas
# Вариант 1: Короткое имя (рекомендуется)
click Instagram-Follow

# Вариант 2: Полное имя
click Chrome-Instagram-Follow-btn

# Вариант 3: С подчеркиваниями
click Instagram_Follow
```

---

## 💡 Как добавить поддержку новых префиксов

### Если добавляешь Instagram:

#### 1. Обнови atlas_dsl_parser.py:

```python
def _build_template_map(self) -> Dict[str, str]:
    # ...
    for prefix in [
        "Chrome-TikTok-", 
        "Chrome-YouTube-", 
        "Chrome-Instagram-",  # ← Добавь это!
        "Chrome-", 
        "Atlas-"
    ]:
        if clean_name.startswith(prefix):
            clean_name = clean_name[len(prefix):]
    # ...
```

#### 2. Теперь работает:

```atlas
# Файл: Chrome-Instagram-Follow-btn.png

click Follow                       ✅ (убрали Chrome-Instagram-)
click Instagram-Follow             ✅ (убрали Chrome-)
click Chrome-Instagram-Follow      ✅ (без -btn)
```

---

## 📊 Полная схема резолюции имен

```
┌─────────────────────────────────────────────────────────────┐
│  ФАЙЛ: Chrome-Instagram-Follow-btn.png                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  ШАГ 1: Извлечение имени без расширения                     │
│  short_name = "Chrome-Instagram-Follow-btn"                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  ШАГ 2: Сохранение полного имени                            │
│  template_map["Chrome-Instagram-Follow-btn"] = путь         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  ШАГ 3: Убираем префиксы                                    │
│  Проверяем: Chrome-TikTok-, Chrome-YouTube-, Chrome-...     │
│  Совпадение: Chrome-                                        │
│  clean_name = "Instagram-Follow-btn"                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  ШАГ 4: Убираем суффиксы                                    │
│  clean_name = "Instagram-Follow"                            │
│  template_map["Instagram-Follow"] = путь                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  ШАГ 5: Заменяем дефисы на подчеркивания                    │
│  template_map["Instagram_Follow"] = путь                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  РЕЗУЛЬТАТ: 3 варианта имени в карте                        │
│  • Chrome-Instagram-Follow-btn                              │
│  • Instagram-Follow                                         │
│  • Instagram_Follow                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Итоги

### Для файла `Chrome-Instagram-Follow-btn.png`:

**Работают в DSL:**
- ✅ `Chrome-Instagram-Follow-btn` (полное имя)
- ✅ `Instagram-Follow` (без префикса Chrome-)
- ✅ `Instagram_Follow` (с подчеркиваниями)
- ✅ `instagram-follow` (без учета регистра)

**НЕ работают:**
- ❌ `Chrome-Instagram-Follow` (нет в карте, нужно добавить -btn)
- ❌ `Follow` (слишком короткое, нужен префикс Instagram-)

### Рекомендация:

**В TEMPLATES_STRUCTURE.txt указывай:**
```
Instagram:
  • Instagram-Follow    - Кнопка подписки  ← Используй это в DSL!
```

**В DSL макросах пиши:**
```atlas
click Instagram-Follow  ✅ Работает!
```

---

**DSL умный - он понимает множество вариантов имен!** 🧠

**Используй короткие имена без префиксов для удобства!** ✨
