# 🧪 Тестирование DOM селектора

## 📋 Проблема

При запуске `tiktok_automation_hybrid.atlas`:
```
✅ Chrome opened successfully
❌ ERROR: Failed to open Chrome
🛑 ABORT: Прерывание выполнения
```

**Причина:** `try/catch` блок прерывает выполнение если **любой** шаг падает.

---

## ✅ Решение

### 1. Создан упрощенный тест: `tiktok_dom_test.atlas`

```atlas
# Простой тест без агрессивных try/catch
log "=== TikTok DOM Selector Test ==="

# 1. Открыть Chrome
open ChromeApp
wait 3s

# 2. Новая вкладка
click ChromeNewTab
wait 2s

# 3. Перейти на TikTok
click ChromeSearchField
type "tiktok.com"
press enter
wait 5s

# 4. Тест DOM селектора
try:
    click Chrome-tiktok-like-dom  # DOM
    log "✅ DOM selector worked!"
catch:
    click Chrome-TikTok-Like      # Vision fallback
    log "✅ Vision fallback worked!"
end
```

---

## 🚀 Как тестировать

### Вариант 1: Через меню

```bash
python3 main.py
→ 2. DSL Сборник
→ Найти: tiktok_dom_test
→ Запустить
```

### Вариант 2: Напрямую

```bash
# Конвертировать в YAML
python3 atlas_dsl_parser.py macro-queues/tiktok_dom_test.atlas /tmp/test.yaml

# Запустить
python3 macro_sequence.py --config /tmp/test.yaml --run tiktok_dom_test
```

---

## 📊 Что тестируется

### Шаги:
```
1. ✅ Открытие Chrome
2. ✅ Новая вкладка
3. ✅ Переход на TikTok
4. 🧪 Клик по Like (DOM селектор)
5. 🔄 Fallback на Vision если DOM не работает
```

### Ожидаемый результат:
```
✅ Chrome opened
✅ New tab opened
✅ TikTok loaded
✅ DOM selector worked!
   ИЛИ
✅ Vision fallback worked!
```

---

## 🔧 Исправления в основном макросе

### Было:
```atlas
try:
    open ChromeApp
    wait 2s
    click ChromeNewTab
    wait 1s
    log "Chrome opened successfully"
catch:
    log "ERROR: Failed to open Chrome"
    abort  # ❌ Прерывает даже если Chrome открылся
end
```

### Стало:
```atlas
# Без try/catch для критических шагов
open ChromeApp
wait 2s
log "Chrome opened"

click ChromeNewTab
wait 1s
log "New tab opened"
```

---

## 💡 Best Practices

### 1. Не используй `abort` в `catch` для некритических ошибок

```atlas
# ❌ Плохо
try:
    click Button
catch:
    abort  # Прерывает весь макрос
end

# ✅ Хорошо
try:
    click Button
catch:
    log "Button not found, continuing..."
end
```

### 2. Разделяй критические и некритические шаги

```atlas
# Критические (без try/catch)
open ChromeApp
wait 2s

# Некритические (с try/catch)
try:
    click OptionalButton
catch:
    log "Optional step skipped"
end
```

### 3. Используй `try/catch` только для DOM/Vision fallback

```atlas
# ✅ Правильное использование
try:
    click Chrome-tiktok-like-dom  # Пробуем DOM
catch:
    click Chrome-TikTok-Like      # Fallback на Vision
end
```

---

## 📁 Файлы

```
✅ macro-queues/tiktok_dom_test.atlas
   (упрощенный тест)

✅ macro-queues/tiktok_automation_hybrid.atlas
   (исправлен - убраны агрессивные abort)

✅ docs/TESTING_DOM_SELECTOR.md
   (эта документация)
```

---

## 🎯 Следующие шаги

1. **Запустить тест:**
   ```bash
   python3 main.py
   → 2. DSL Сборник
   → tiktok_dom_test
   ```

2. **Проверить логи:**
   ```
   ✅ Chrome opened
   ✅ New tab opened
   ✅ TikTok loaded
   ✅ DOM selector worked!
   ```

3. **Если DOM не работает:**
   - Проверить что TikTok загружен
   - Проверить селектор в браузере: `document.querySelector('[data-e2e="like-icon"]')`
   - Проверить что `dom_selectors/tiktok/selectors.json` существует

---

**Тестовый макрос готов! 🧪**

**Запусти tiktok_dom_test для проверки! 🚀**
