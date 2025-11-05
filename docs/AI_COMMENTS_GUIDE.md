# 🤖 AI Comments Guide - Умные комментарии с AI

## 📋 Обзор

Macro AI теперь поддерживает **автоматическую генерацию осмысленных ответов** на комментарии через:
- **Selenium/Playwright** - динамическая работа с DOM
- **EasyOCR** - извлечение текста из скриншотов (fallback)
- **Gemini API** - генерация умных ответов

---

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

Это установит:
- `selenium` - автоматизация браузера
- `webdriver-manager` - автоматическая установка драйверов
- `easyocr` - распознавание текста
- `google-generativeai` - Gemini API

### 2. Получение Gemini API Key

1. Перейди на https://makersuite.google.com/app/apikey
2. Создай API ключ
3. Скопируй `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```
4. Вставь свой ключ в `.env`:
   ```
   GEMINI_API_KEY=your_actual_key_here
   ```

### 3. Запуск примера

```bash
# Установи переменную окружения
export GEMINI_API_KEY="your_key"

# Запусти пример
python3 macro_sequence.py --config examples/tiktok_ai_comments.yaml --run tiktok_ai_replies_selenium
```

---

## 📚 Доступные действия

### 🌐 Selenium Actions

#### `selenium_init` - Инициализация браузера
```yaml
- action: selenium_init
  browser: chrome  # chrome, firefox, edge
  headless: false  # true для фонового режима
  url: "https://tiktok.com/@user/video/123"
```

#### `selenium_find` - Поиск элемента
```yaml
- action: selenium_find
  selector: ".comment-text"  # CSS селектор
  index: 0  # индекс элемента (если несколько)
  wait_for_element: true  # ждать появления
  timeout: 10.0  # максимальное время ожидания
  save_element: my_element  # сохранить в переменную
```

#### `selenium_click` - Клик по элементу
```yaml
- action: selenium_click
  selector: ".reply-button"  # CSS селектор
  # или
  element: my_element  # использовать сохраненный элемент
```

#### `selenium_type` - Ввод текста
```yaml
- action: selenium_type
  selector: ".comment-input"
  text: "{reply_text}"  # можно использовать переменные
```

#### `selenium_scroll` - Скролл страницы
```yaml
- action: selenium_scroll
  direction: down  # down или up
  amount: 300  # пикселей
```

#### `selenium_close` - Закрыть браузер
```yaml
- action: selenium_close
```

---

### 🤖 AI Actions

#### `ai_extract_text` - Извлечение текста
```yaml
- action: ai_extract_text
  method: selenium  # selenium (основной) или ocr (fallback)
  selector: ".comment-text"  # для selenium
  region: [100, 300, 600, 100]  # [x, y, width, height] для OCR
  fallback: ocr  # использовать OCR если selenium не сработал
  save_to: comment_text  # сохранить в переменную
```

**Методы:**
- `selenium` - извлечение через DOM (быстро, надежно)
- `ocr` - распознавание текста на скриншоте (медленно, fallback)

**Приоритет:**
1. Selenium (если доступен и указан)
2. OCR (если Selenium не сработал или указан напрямую)

#### `ai_generate` - Генерация ответа
```yaml
- action: ai_generate
  model: gemini  # gemini (пока только он)
  prompt: "Напиши дружелюбный ответ на: {comment_text}"
  max_tokens: 50  # максимум символов
  temperature: 0.7  # креативность (0.0-1.0)
  save_to: reply_text  # сохранить в переменную
```

**Параметры:**
- `prompt` - инструкция для AI (поддерживает переменные `{var}`)
- `max_tokens` - максимальная длина ответа
- `temperature` - креативность (0.0 = предсказуемо, 1.0 = креативно)
- `save_to` - имя переменной для сохранения

---

## 🎯 Примеры использования

### Пример 1: Простой ответ на комментарий

```yaml
sequences:
  simple_reply:
    steps:
    # 1. Открыть TikTok
    - action: selenium_init
      url: "https://tiktok.com/@user/video/123"
    
    # 2. Прочитать комментарий
    - action: ai_extract_text
      method: selenium
      selector: ".comment-text"
      save_to: comment_text
    
    # 3. Сгенерировать ответ
    - action: ai_generate
      prompt: "Ответь на: {comment_text}"
      save_to: reply_text
    
    # 4. Отправить
    - action: selenium_click
      selector: ".reply-button"
    
    - action: selenium_type
      selector: ".comment-input"
      text: "{reply_text}"
    
    - action: selenium_click
      selector: ".submit-button"
    
    # 5. Закрыть
    - action: selenium_close
```

### Пример 2: Массовая обработка с циклом

```yaml
sequences:
  mass_replies:
    steps:
    - action: selenium_init
      url: "https://tiktok.com/@user/video/123"
    
    - action: repeat
      times: 10
      steps:
      # Извлечь текст
      - action: ai_extract_text
        method: selenium
        selector: ".comment-text"
        fallback: ocr
        save_to: comment_text
      
      # AI ответ
      - action: ai_generate
        prompt: "Короткий дружелюбный ответ: {comment_text}"
        max_tokens: 50
        save_to: reply_text
      
      # Отправить
      - action: selenium_click
        selector: ".reply-button"
      
      - action: selenium_type
        selector: ".comment-input"
        text: "{reply_text}"
      
      - action: selenium_click
        selector: ".submit-button"
      
      # Пауза и скролл
      - action: wait
        duration: 2.0
      
      - action: selenium_scroll
        direction: down
        amount: 200
    
    - action: selenium_close
```

### Пример 3: Гибридный подход (Template + AI)

```yaml
sequences:
  hybrid_reply:
    steps:
    # Клик по кнопке (Template matching)
    - action: click
      template: templates/tiktok_comments_btn.png
    
    # Извлечь текст (OCR)
    - action: ai_extract_text
      method: ocr
      region: [100, 300, 600, 100]
      save_to: comment_text
    
    # AI генерация
    - action: ai_generate
      prompt: "Ответь: {comment_text}"
      save_to: reply_text
    
    # Ввод (pyautogui)
    - action: type
      text: "{reply_text}"
    
    - action: key
      key: enter
```

---

## 🎨 Продвинутые промпты

### Контекстные ответы
```yaml
- action: ai_generate
  prompt: |
    Ты - популярный блогер TikTok.
    Пользователь написал: {comment_text}
    
    Напиши короткий (до 50 символов) дружелюбный ответ с эмодзи.
    Будь позитивным и вовлекающим.
  save_to: reply_text
```

### Тональность
```yaml
- action: ai_generate
  prompt: "Напиши {tone} ответ на: {comment_text}"
  save_to: reply_text

# где tone может быть:
# - дружелюбный
# - профессиональный
# - смешной
# - мотивирующий
```

### С ограничениями
```yaml
- action: ai_generate
  prompt: |
    Ответь на комментарий: {comment_text}
    
    Требования:
    - Максимум 50 символов
    - Используй 1-2 эмодзи
    - Будь позитивным
    - Не используй вопросы
  max_tokens: 50
  temperature: 0.7
  save_to: reply_text
```

---

## 🔧 Поиск CSS селекторов

### Как найти селектор в TikTok:

1. **Открой DevTools** (F12 или Cmd+Opt+I)
2. **Кликни на инспектор** (стрелка в углу)
3. **Наведи на элемент** (комментарий, кнопка)
4. **Скопируй селектор**:
   - Правый клик на элементе в DevTools
   - Copy → Copy selector

### Примеры селекторов TikTok:

```yaml
# Комментарий
selector: "[data-e2e='comment-level-1'] span[data-e2e='comment-text']"

# Кнопка "Ответить"
selector: "[data-e2e='comment-reply-button']"

# Поле ввода комментария
selector: "[data-e2e='comment-input']"

# Кнопка "Отправить"
selector: "[data-e2e='comment-post']"

# Кнопка "Комментарии"
selector: "[data-e2e='browse-comment']"
```

**Совет:** Селекторы могут меняться! Проверяй их перед запуском.

---

## ⚙️ Настройка

### Переменные окружения

```bash
# .env файл
GEMINI_API_KEY=your_key_here
AI_MODEL=gemini-pro
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=100
```

### Глобальные переменные в YAML

```yaml
variables:
  tiktok_url: "https://tiktok.com/@user/video/123"
  reply_count: 5
  ai_model: gemini
  reply_tone: дружелюбный
  max_reply_length: 50
```

Использование:
```yaml
- action: selenium_init
  url: "{tiktok_url}"

- action: repeat
  times: "{reply_count}"
  
- action: ai_generate
  prompt: "Напиши {reply_tone} ответ"
```

---

## 🐛 Troubleshooting

### Selenium не запускается

```bash
# Установи Chrome/Chromium
brew install --cask google-chrome

# Или используй Firefox
- action: selenium_init
  browser: firefox
```

### OCR медленно работает

```python
# В macro_sequence.py уже настроено:
self.ocr_reader = easyocr.Reader(['ru', 'en'], gpu=False)

# Если есть GPU (M2):
self.ocr_reader = easyocr.Reader(['ru', 'en'], gpu=True)
```

### Gemini API не работает

```bash
# Проверь ключ
echo $GEMINI_API_KEY

# Проверь квоту
# https://makersuite.google.com/app/apikey

# Проверь лимиты
# Бесплатный tier: 60 запросов/минуту
```

### Селекторы не находятся

```yaml
# Добавь ожидание
- action: selenium_find
  selector: ".comment-text"
  wait_for_element: true
  timeout: 10.0

# Или используй более общий селектор
selector: "span"  # найдет все span
index: 0  # возьмет первый
```

---

## 💡 Best Practices

### 1. Используй Selenium как основной метод
```yaml
# ✅ Хорошо
- action: ai_extract_text
  method: selenium
  fallback: ocr

# ❌ Плохо (медленно)
- action: ai_extract_text
  method: ocr
```

### 2. Добавляй паузы
```yaml
# Между действиями
- action: wait
  duration: 2.0

# Между итерациями
- action: repeat
  times: 10
  steps:
  - ... действия ...
  - action: wait
    duration: 3.0  # важно!
```

### 3. Используй fallback
```yaml
# На случай если Selenium не сработает
- action: ai_extract_text
  method: selenium
  selector: ".comment"
  fallback: ocr
  region: [100, 300, 600, 100]
```

### 4. Ограничивай длину ответов
```yaml
- action: ai_generate
  prompt: "Короткий ответ (до 50 символов): {comment_text}"
  max_tokens: 50  # важно для TikTok!
```

### 5. Закрывай браузер
```yaml
steps:
- action: selenium_init
  ...
- ... действия ...
- action: selenium_close  # всегда в конце!
```

---

## 📊 Производительность

### MacBook Air M2 (8GB RAM):

| Метод | Скорость | Память | Рекомендация |
|-------|----------|--------|--------------|
| **Selenium** | ⚡⚡⚡ Быстро (0.1-0.5с) | 200-300 MB | ✅ Основной |
| **OCR** | 🐌 Медленно (2-5с) | 500-800 MB | 🔄 Fallback |
| **Gemini API** | ⚡⚡ Средне (1-2с) | ~50 MB | ✅ Основной |

### Оптимизация:

```yaml
# Используй headless режим
- action: selenium_init
  headless: true  # экономит память

# Закрывай браузер после работы
- action: selenium_close

# Инициализируй OCR только если нужен
# (автоматически при первом использовании)
```

---

## 🎯 Примеры для разных платформ

### TikTok
```yaml
selector: "[data-e2e='comment-text']"
```

### Instagram
```yaml
selector: "span.x1lliihq"  # может меняться!
```

### YouTube
```yaml
selector: "#content-text"
```

### Twitter/X
```yaml
selector: "[data-testid='tweetText']"
```

**Важно:** Селекторы часто меняются! Проверяй перед использованием.

---

## 📚 Дополнительные ресурсы

- [Selenium документация](https://selenium-python.readthedocs.io/)
- [EasyOCR GitHub](https://github.com/JaidedAI/EasyOCR)
- [Gemini API docs](https://ai.google.dev/docs)
- [CSS Selectors Guide](https://www.w3schools.com/cssref/css_selectors.php)

---

## 🚀 Что дальше?

1. **Создай свои промпты** - экспериментируй с тональностью
2. **Найди селекторы** для своей платформы
3. **Автоматизируй рутину** - ответы, лайки, подписки
4. **Комбинируй методы** - Template + Selenium + AI

**Удачи с автоматизацией!** 🎉
