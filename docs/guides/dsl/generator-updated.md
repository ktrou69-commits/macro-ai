# ✅ DSL Reference Generator обновлен!

## 🎯 Что добавлено

### Теперь генератор извлекает:

1. **Vision Templates** (`.png` файлы)
2. **DOM Selectors** (из `structure.txt`) ← НОВОЕ!

---

## 📋 Формат в DSL_REFERENCE.txt

### Vision Templates:
```
🖼️  VISION TEMPLATES (Template Matching)
--------------------------------------------------------------------------------

📄 templates/Chrome/TikTok/Chrome-TikTok-Like-btn.png
   Доступные имена:
     • Chrome-TikTok-Like-btn
     • Chrome-TikTok-Like
     • Like
```

### DOM Selectors:
```
🔧 DOM SELECTORS (CSS Selectors)
--------------------------------------------------------------------------------

📄 TikTok/Chrome-TikTok-Like-dom
   Доступные имена:
     • Chrome-TikTok-Like-dom
     • TikTok-Like-dom
   Selector: [data-e2e="like-icon"]
   Type: span
   Confidence: 95%
   Method: DOM (быстро, надежно)
   Fallback: Chrome-TikTok-Like-btn.png (Vision)
```

---

## 🔧 Как работает парсинг

### 1. Сканирует `.png` файлы (Vision)
```python
png_files = list(self.templates_path.rglob("*.png"))
```

### 2. Парсит `structure.txt` (DOM)
```python
structure_files = list(self.templates_path.rglob("structure.txt"))

# Ищет строки вида:
# # Chrome-TikTok-Like-dom
# #   Selector: [data-e2e="like-icon"]
# #   Type: span
# #   Confidence: 95%
```

### 3. Извлекает метаданные
```python
metadata = {
    'selector': '[data-e2e="like-icon"]',
    'type': 'span',
    'confidence': '95%',
    'method': 'DOM (быстро, надежно)',
    'fallback': 'Chrome-TikTok-Like-btn.png'
}
```

---

## 🚀 Использование

### Генерация справочника:

```bash
# Для всех шаблонов
python3 utils/dsl_reference_generator.py

# Для конкретной папки
python3 utils/dsl_reference_generator.py --templates-path templates/Chrome/TikTok

# С кастомным выходным файлом
python3 utils/dsl_reference_generator.py --output my_reference.txt
```

### Вывод:
```
📂 Сканирование: templates/Chrome/TikTok
📄 Найдено PNG файлов (Vision): 4
📄 Найдено DOM селекторов: 1

✅ Справочник сохранен: dsl_references/DSL_REFERENCE.txt
📊 Всего строк: 130
🏷️  Уникальных имен: 8
📄 Файлов шаблонов: 5
```

---

## 📊 Формат structure.txt

### Правильный формат для парсинга:

```
 ├── TikTok/
 │    │
 │    │    # ========================================
 │    │    # VISION TEMPLATES (Template Matching)
 │    │    # ========================================
 │    │    ├── Chrome-TikTok-Like-btn.png      # Vision
 │    │
 │    │    # ========================================
 │    │    # DOM SELECTORS (CSS Selectors)
 │    │    # ========================================
 │    │    # Chrome-TikTok-Like-dom
 │    │    #   Selector: [data-e2e="like-icon"]
 │    │    #   Type: span
 │    │    #   Confidence: 95%
 │    │    #   Description: Иконка лайка в TikTok
 │    │    #   Method: DOM (быстро, надежно)
 │    │    #   Fallback: Chrome-TikTok-Like-btn.png (Vision)
```

### Ключевые моменты:

1. **Имя селектора:** `# Chrome-TikTok-Like-dom`
   - Должно заканчиваться на `-dom`
   - Должно содержать `# Chrome-`

2. **Метаданные:** `#   Selector:`, `#   Type:`, etc.
   - Начинаются с `#   ` (3 пробела после #)
   - Формат: `#   Ключ: Значение`

3. **Символы дерева:** ` │    │    #`
   - Парсер игнорирует их автоматически

---

## 💡 Примеры

### Пример 1: TikTok Like

**structure.txt:**
```
 │    │    # Chrome-TikTok-Like-dom
 │    │    #   Selector: [data-e2e="like-icon"]
 │    │    #   Type: span
 │    │    #   Confidence: 95%
 │    │    #   Fallback: Chrome-TikTok-Like-btn.png
```

**DSL_REFERENCE.txt:**
```
📄 TikTok/Chrome-TikTok-Like-dom
   Доступные имена:
     • Chrome-TikTok-Like-dom
     • TikTok-Like-dom
   Selector: [data-e2e="like-icon"]
   Type: span
   Confidence: 95%
   Fallback: Chrome-TikTok-Like-btn.png
```

**Использование в макросе:**
```atlas
click Chrome-TikTok-Like-dom  # DOM селектор
# или
click TikTok-Like-dom         # Короткое имя
```

---

### Пример 2: YouTube Subscribe

**structure.txt:**
```
 │    │    # Chrome-YouTube-Subscribe-dom
 │    │    #   Selector: button[aria-label="Subscribe"]
 │    │    #   Type: button
 │    │    #   Confidence: 90%
```

**DSL_REFERENCE.txt:**
```
📄 YouTube/Chrome-YouTube-Subscribe-dom
   Доступные имена:
     • Chrome-YouTube-Subscribe-dom
     • YouTube-Subscribe-dom
   Selector: button[aria-label="Subscribe"]
   Type: button
   Confidence: 90%
```

---

## 🔧 Обновленные файлы

```
✅ utils/dsl_reference_generator.py
   - Добавлен метод _scan_dom_selectors()
   - Обновлен метод scan_templates()
   - Обновлен метод generate_reference()
   - Парсинг метаданных из structure.txt

✅ dsl_references/DSL_REFERENCE.txt
   - Теперь включает DOM селекторы
   - Разделение Vision и DOM
   - Метаданные для каждого селектора

✅ docs/DSL_GENERATOR_UPDATED.md
   - Эта документация
```

---

## 🎉 Итоги

### Что работает:
```
✅ Парсинг Vision templates (.png)
✅ Парсинг DOM selectors (structure.txt)
✅ Извлечение метаданных
✅ Генерация справочника
✅ Все имена в алфавитном списке
```

### Формат:
```
Vision:  Chrome-TikTok-Like      (.png файл)
DOM:     Chrome-TikTok-Like-dom  (structure.txt)
```

### Использование:
```bash
python3 utils/dsl_reference_generator.py
# → Генерирует DSL_REFERENCE.txt
# → Включает Vision + DOM
# → Все метаданные
```

---

**DSL Generator обновлен! ✅**

**Теперь парсит DOM селекторы! 🔧**

**Один файл structure.txt для всего! 📝**

**Работает автоматически! 🚀**
