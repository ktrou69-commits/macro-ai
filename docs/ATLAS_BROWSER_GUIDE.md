# 🌐 Atlas Browser + AI Guide

## 📋 Проблема

Atlas браузер не поддерживается напрямую через Selenium (ошибка: `cannot find Chrome binary`).

## ✅ Решение: Гибридный подход

Используй **Template matching + OCR + AI** вместо Selenium:

```
Atlas Browser
    ↓
Template Matching (клики по кнопкам)
    ↓
OCR (чтение текста комментариев)
    ↓
Gemini AI (генерация ответов)
    ↓
PyAutoGUI (ввод и отправка)
```

---

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Только AI и OCR (без Selenium)
pip install google-generativeai easyocr
```

### 2. Настройка API

```bash
export GEMINI_API_KEY="AIzaSyBGlFjt6bKJLJqcsavArM6wb7voH111gc8"
```

### 3. Запуск для Atlas

```bash
python3 macro_sequence.py \
  --config examples/tiktok_ai_atlas.yaml \
  --run tiktok_ai_atlas
```

---

## 📋 Доступные последовательности

### 1. `tiktok_ai_atlas` - Полная автоматизация
- Открывает Atlas
- Переходит на TikTok
- Читает комментарии (OCR)
- Генерирует ответы (AI)
- Отправляет

### 2. `tiktok_ai_simple` - Упрощенная версия
- Только для уже открытого TikTok
- OCR + AI + отправка
- Быстрее и проще

### 3. `test_ai_generation` - Тест AI
- Проверка работы Gemini API
- Без браузера

---

## 🎯 Пример использования

### Полная последовательность:

```yaml
sequences:
  my_atlas_replies:
    steps:
    # 1. Открыть Atlas (Template)
    - action: click
      template: templates/button.png
      clicks: 2
    
    # 2. Открыть TikTok (Template)
    - action: click
      template: templates/tiktok_openSite-btn.png
    
    # 3. Повторить для комментариев
    - action: repeat
      times: 5
      steps:
      
      # 3.1. Прочитать комментарий (OCR)
      - action: ai_extract_text
        method: ocr
        region: [100, 300, 600, 100]
        save_to: comment_text
      
      # 3.2. AI ответ (Gemini)
      - action: ai_generate
        prompt: "Ответь дружелюбно: {comment_text}"
        save_to: reply_text
      
      # 3.3. Ввести (PyAutoGUI)
      - action: type
        text: "{reply_text}"
      
      # 3.4. Отправить
      - action: key
        key: enter
      
      # 3.5. Скролл
      - action: scroll
        direction: down
        amount: 10
```

---

## 🔧 Настройка региона OCR

### Как найти координаты комментария:

1. **Открой TikTok в Atlas**
2. **Запусти скрипт поиска координат**:
   ```bash
   python3 utils/find_coordinates.py
   ```
3. **Наведи на комментарий** и запомни координаты
4. **Обнови region** в конфиге:
   ```yaml
   region: [x, y, width, height]
   # Например: [100, 300, 600, 100]
   ```

### Типичные координаты для Atlas:

```yaml
# Комментарий (верхний)
region: [200, 400, 500, 80]

# Комментарий (средний)
region: [200, 500, 500, 80]

# Поле ввода
x: 400
y: 650
```

---

## 💡 Best Practices для Atlas

### 1. Используй Template matching для кликов
```yaml
# ✅ Хорошо - надежно
- action: click
  template: templates/atlas-tiktok_reply_btn.png

# ❌ Плохо - координаты могут меняться
- action: click
  position: absolute
  x: 661
  y: 534
```

### 2. OCR для текста
```yaml
# ✅ Хорошо - динамический размер
- action: ai_extract_text
  method: ocr
  region: [100, 300, 600, 100]

# ❌ Selenium не работает с Atlas
- action: selenium_find
  selector: ".comment"  # НЕ РАБОТАЕТ
```

### 3. Добавляй паузы
```yaml
# Atlas может быть медленнее
- action: wait
  duration: 2.0  # между действиями

- action: wait
  duration: 3.0  # после загрузки страницы
```

### 4. Проверяй шаблоны
```bash
# Создай шаблоны для Atlas кнопок
python3 utils/smart_capture.py

# Сохрани как:
# - atlas-tiktok_reply_btn.png
# - atlas-tiktok_comment_input.png
# - atlas-tiktok_send_btn.png
```

---

## 🐛 Troubleshooting

### OCR медленно работает

```yaml
# Уменьши область сканирования
region: [200, 400, 400, 60]  # меньше = быстрее

# Или используй только английский
# В macro_sequence.py:
self.ocr_reader = easyocr.Reader(['en'], gpu=False)
```

### AI не генерирует ответы

```bash
# Проверь API ключ
echo $GEMINI_API_KEY

# Проверь интернет
ping google.com

# Проверь квоту
# https://makersuite.google.com/app/apikey
```

### Шаблоны не находятся

```yaml
# Добавь wait_for_appear
- action: click
  template: templates/button.png
  wait_for_appear: true
  timeout: 5.0

# Или уменьши threshold
# В macro_sequence.py:
DEFAULT_THRESHOLD = 0.75  # вместо 0.86
```

---

## 📊 Производительность

### MacBook Air M2 с Atlas:

| Действие | Скорость | Надежность |
|----------|----------|------------|
| Template matching | ⚡⚡⚡ 0.2-1с | ✅✅✅ Высокая |
| OCR (EasyOCR) | 🐌 2-5с | ✅✅ Средняя |
| AI (Gemini) | ⚡⚡ 1-2с | ✅✅✅ Высокая |
| PyAutoGUI (ввод) | ⚡⚡⚡ 0.1-0.5с | ✅✅✅ Высокая |

### Оптимизация:

```yaml
# 1. Уменьши область OCR
region: [200, 400, 400, 60]  # вместо [100, 300, 600, 100]

# 2. Используй кэш шаблонов (автоматически)

# 3. Ограничь длину AI ответов
max_tokens: 30  # вместо 50

# 4. Используй headless OCR
# (уже настроено: gpu=False)
```

---

## 🎯 Рекомендуемый workflow

### Для Atlas браузера:

```yaml
sequences:
  atlas_workflow:
    steps:
    # 1. Открыть Atlas (Template)
    - action: click
      template: templates/button.png
      clicks: 2
    
    # 2. Навигация (Template)
    - action: click
      template: templates/tiktok_openSite-btn.png
    
    # 3. AI обработка (OCR + Gemini)
    - action: repeat
      times: 5
      steps:
      - action: ai_extract_text
        method: ocr
        region: [200, 400, 500, 80]
        save_to: comment_text
      
      - action: ai_generate
        prompt: "Ответь: {comment_text}"
        save_to: reply_text
      
      # 4. Ввод (PyAutoGUI)
      - action: type
        text: "{reply_text}"
      
      - action: key
        key: enter
      
      # 5. Скролл (PyAutoGUI)
      - action: scroll
        direction: down
        amount: 10
```

---

## 📚 Дополнительные ресурсы

- [Template Matching Guide](TEMPLATE_MATCHING.md)
- [OCR Setup Guide](OCR_SETUP.md)
- [AI Comments Guide](AI_COMMENTS_GUIDE.md)

---

## 🚀 Что дальше?

1. **Создай шаблоны** для Atlas кнопок
2. **Найди координаты** комментариев
3. **Протестируй OCR** на своем экране
4. **Запусти** `tiktok_ai_atlas`

**Удачи с автоматизацией в Atlas!** 🎉
