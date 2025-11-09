# 🎯 Naming Convention: DOM vs Vision

## 📋 Проблема

**Было непонятно что используется:**
```atlas
click Chrome-TikTok-Like  # Это DOM или Vision? 🤔
```

## ✅ Решение: Разные имена

### Vision (Template Matching):
```atlas
click Chrome-TikTok-Like  # .png файл (Vision)
```

### DOM (CSS Selector):
```atlas
click Chrome-TikTok-Like-dom  # CSS селектор (DOM)
```

---

## 📊 Naming Convention

### Vision Templates:
```
Формат: Chrome-{Site}-{Element}
Пример: Chrome-TikTok-Like
Файл:   templates/Chrome/TikTok/Chrome-TikTok-Like-btn.png
```

### DOM Selectors:
```
Формат: Chrome-{site}-{element}-dom
Пример: Chrome-tiktok-like-dom
Файл:   dom_selectors/tiktok/selectors.json
```

**Ключевое отличие:** суффикс `-dom`

---

## 📁 Структура файлов

### templates/Chrome/TikTok/structure.txt

```
 ├── TikTok/
 │    │
 │    │    # ========================================
 │    │    # VISION TEMPLATES (Template Matching)
 │    │    # ========================================
 │    │    ├── Chrome-TikTok-Like-btn.png      # Vision
 │    │    ├── Chrome-TikTok-Comment-btn.png   # Vision
 │    │    ├── Chrome-TikTok-Search-btn.png    # Vision
 │    │
 │    │    # ========================================
 │    │    # DOM SELECTORS (CSS Selectors)
 │    │    # ========================================
 │    │    # Chrome-TikTok-Like-dom
 │    │    #   Selector: [data-e2e="like-icon"]
 │    │    #   Type: span
 │    │    #   Confidence: 95%
 │    │    #   Method: DOM (быстро, надежно)
 │    │    #   Fallback: Chrome-TikTok-Like-btn.png
```

### dom_selectors/tiktok/selectors.json

```json
{
  "Chrome-tiktok-like-dom": {
    "selector": "[data-e2e=\"like-icon\"]",
    "type": "span",
    "method": "DOM",
    "fallback": "Chrome-TikTok-Like-btn.png"
  }
}
```

---

## 🎯 Использование в макросах

### Вариант 1: Только DOM

```atlas
# Быстро, но может не работать на всех сайтах
click Chrome-tiktok-like-dom
```

### Вариант 2: Только Vision

```atlas
# Медленно, но работает везде
click Chrome-TikTok-Like
```

### Вариант 3: Hybrid (РЕКОМЕНДУЕТСЯ)

```atlas
# Лучшее из двух миров
try:
    click Chrome-tiktok-like-dom  # DOM (быстро)
catch:
    click Chrome-TikTok-Like      # Vision (надежно)
end
```

---

## 📊 Сравнение

| Аспект | Vision | DOM |
|--------|--------|-----|
| **Имя** | `Chrome-TikTok-Like` | `Chrome-tiktok-like-dom` |
| **Файл** | `.png` | `.json` |
| **Скорость** | 🐌 2000ms | ⚡ 50ms |
| **Надежность** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Зависимость от дизайна** | ❌ Да | ✅ Нет |

---

## 🔧 Автоматическое сохранение

### Инструмент автоматически:

1. **Добавляет суффикс `-dom`**
   ```
   Ввод: like
   Сохраняется: Chrome-tiktok-like-dom
   ```

2. **Сохраняет в JSON**
   ```
   dom_selectors/tiktok/selectors.json
   ```

3. **Обновляет structure.txt**
   ```
   templates/Chrome/TikTok/structure.txt
   ```

---

## 💡 Примеры

### Пример 1: TikTok Like

**Vision:**
```atlas
click Chrome-TikTok-Like  # templates/Chrome/TikTok/Chrome-TikTok-Like-btn.png
```

**DOM:**
```atlas
click Chrome-tiktok-like-dom  # dom_selectors/tiktok/selectors.json
```

**Hybrid:**
```atlas
try:
    click Chrome-tiktok-like-dom
catch:
    click Chrome-TikTok-Like
end
```

---

### Пример 2: YouTube Subscribe

**Vision:**
```atlas
click Chrome-YouTube-Subscribe  # .png
```

**DOM:**
```atlas
click Chrome-youtube-subscribe-dom  # .json
```

---

### Пример 3: Instagram Like

**Vision:**
```atlas
click Chrome-Instagram-Like  # .png
```

**DOM:**
```atlas
click Chrome-instagram-like-dom  # .json
```

---

## 📋 Workflow

### Создание DOM селектора:

```bash
# 1. Извлечь селектор
python3 utils/dom_selector_tool.py
→ 1. Извлечь селектор (AI)
→ Сайт: tiktok
→ Элемент: like

# 2. Автоматически сохраняется как:
Chrome-tiktok-like-dom

# 3. Обновляется:
✅ dom_selectors/tiktok/selectors.json
✅ templates/Chrome/TikTok/structure.txt

# 4. Использовать в макросе:
click Chrome-tiktok-like-dom
```

---

## 🎯 Best Practices

### 1. Используй Hybrid подход

```atlas
✅ try:
    click Chrome-tiktok-like-dom  # Быстро
catch:
    click Chrome-TikTok-Like      # Надежно
end
```

### 2. Документируй в structure.txt

```
# Chrome-TikTok-Like-dom
#   Selector: [data-e2e="like-icon"]
#   Fallback: Chrome-TikTok-Like-btn.png
```

### 3. Указывай метод в логах

```atlas
try:
    click Chrome-tiktok-like-dom
    log "✅ Like successful (DOM)"
catch:
    click Chrome-TikTok-Like
    log "✅ Like successful (Vision)"
end
```

---

## 📊 Таблица соответствий

| Vision Template | DOM Selector | Fallback |
|----------------|--------------|----------|
| `Chrome-TikTok-Like` | `Chrome-tiktok-like-dom` | ✅ |
| `Chrome-TikTok-Comment` | `Chrome-tiktok-comment-dom` | ✅ |
| `Chrome-YouTube-Subscribe` | `Chrome-youtube-subscribe-dom` | ✅ |
| `Chrome-Instagram-Like` | `Chrome-instagram-like-dom` | ✅ |

---

## 🎉 Итоги

### Naming Convention:
```
Vision:  Chrome-TikTok-Like           (.png)
DOM:     Chrome-tiktok-like-dom       (.json)
```

### Преимущества:
```
✅ Понятно что используется
✅ Легко различить в коде
✅ Автоматическое сохранение
✅ Документация в structure.txt
```

### Hybrid подход:
```atlas
try:
    click Chrome-tiktok-like-dom  # DOM
catch:
    click Chrome-TikTok-Like      # Vision
end
```

---

**Naming convention установлен! ✅**

**Теперь понятно что используется! 🎯**

**Hybrid = лучшее решение! 🚀**
