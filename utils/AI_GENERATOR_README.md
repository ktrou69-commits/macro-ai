# 🤖 AI Macro Generator - AI генератор макросов

## 🎯 Что это?

**AI Macro Generator** - автоматическое создание `.atlas` макросов по текстовому описанию с помощью AI.

**Просто опишите что нужно сделать** - AI создаст готовый макрос!

---

## 🚀 Быстрый старт

### Через main.py (рекомендуется):
```bash
python3 main.py
# → 4. Генерация последовательности (AI)
# → Введите описание
# → Макрос создан автоматически!
```

### Напрямую:
```bash
python3 utils/ai_macro_generator.py "открыть YouTube и поставить лайк"
```

---

## 📋 Требования

### 1. Установка библиотек:
```bash
# OpenAI (GPT-4)
pip install openai

# Anthropic (Claude)
pip install anthropic

# Google (Gemini)
pip install google-generativeai
```

### 2. API ключи:
```bash
# Установите хотя бы один ключ:

# OpenAI
export OPENAI_API_KEY='your-openai-key'

# Anthropic
export ANTHROPIC_API_KEY='your-anthropic-key'

# Google Gemini
export GEMINI_API_KEY='your-gemini-key'
```

**Получить ключи:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Google: https://makersuite.google.com/app/apikey

---

## 💡 Примеры использования

### Пример 1: TikTok лайки
```bash
python3 main.py
# → 4. Генерация последовательности (AI)
# → Ввод: "открыть TikTok и поставить 5 лайков"
```

**AI создаст:**
```atlas
# TikTok Auto Like

open ChromeApp
wait 2s

click ChromeNewTab
wait 1s

click ChromeSearchField
type "tiktok.com"
press enter
wait 5s

repeat 5:
  click Like
  wait 1.5s
  scroll down
  wait 2s
```

---

### Пример 2: YouTube поиск
```bash
# Ввод: "зайти на YouTube и найти Python tutorial"
```

**AI создаст:**
```atlas
# YouTube Search Python Tutorial

open ChromeApp
wait 2s

click ChromeSearchField
type "youtube.com"
press enter
wait 4s

click ChromeSearchField
type "Python tutorial"
press enter
wait 3s
```

---

### Пример 3: Мульти-вкладки
```bash
# Ввод: "открыть YouTube, потом TikTok, потом Google"
```

**AI создаст:**
```atlas
# Multi Tab Workflow

open ChromeApp
wait 2s

# YouTube
click ChromeNewTab
type "youtube.com"
press enter
wait 3s

# TikTok
click ChromeNewTab
type "tiktok.com"
press enter
wait 3s

# Google
click ChromeNewTab
type "google.com"
press enter
wait 2s
```

---

## 🔍 Как работает

### 1. Сбор контекста
```python
# Загружает:
- DSL справочник (команды)
- Структуру шаблонов (кнопки)
- Описания файлов
```

### 2. Формирование промпта
```python
system_prompt = """
Ты — AI-интерпретатор DSL-сценариев...

Структура шаблонов:
├── Chrome/
│   ├── ChromeApp-btn.png
│   ├── ChromeNewTab-btn.png
│   └── ...

DSL команды:
- open <template>
- click <template>
- type "<text>"
...

INPUT: <описание пользователя>
"""
```

### 3. Запрос к AI
```python
# Отправляет промпт + описание пользователя
response = ai_api.generate(system_prompt + user_input)
```

### 4. Парсинг ответа
```python
# Извлекает:
- Название макроса
- DSL код
```

### 5. Сохранение
```python
# Сохраняет в macro-queues/
filepath = "macro-queues/youtube_search.atlas"
```

---

## 🎨 Поддерживаемые AI провайдеры

### 1. OpenAI (GPT-4)
```bash
export OPENAI_API_KEY='your-key'
python3 utils/ai_macro_generator.py "ваш запрос"
```

**Модель:** `gpt-4`  
**Качество:** ⭐⭐⭐⭐⭐  
**Скорость:** ⭐⭐⭐⭐

---

### 2. Anthropic (Claude)
```bash
export ANTHROPIC_API_KEY='your-key'
python3 utils/ai_macro_generator.py "ваш запрос"
```

**Модель:** `claude-3-opus-20240229`  
**Качество:** ⭐⭐⭐⭐⭐  
**Скорость:** ⭐⭐⭐⭐

---

### 3. Google (Gemini)
```bash
export GEMINI_API_KEY='your-key'
python3 utils/ai_macro_generator.py "ваш запрос"
```

**Модель:** `gemini-pro`  
**Качество:** ⭐⭐⭐⭐  
**Скорость:** ⭐⭐⭐⭐⭐

---

## 🎯 Workflow

```
┌─────────────────────────────────────────┐
│  1. Пользователь вводит описание        │
│     "открыть TikTok и поставить лайк"   │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  2. Загрузка контекста                  │
│     - DSL справочник                    │
│     - Структура шаблонов                │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  3. Формирование промпта                │
│     System: "Ты AI-интерпретатор..."    │
│     User: "INPUT: открыть TikTok..."    │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  4. Запрос к AI API                     │
│     OpenAI / Anthropic / Gemini         │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  5. Парсинг ответа                      │
│     Название: "tiktok_auto_like"        │
│     DSL код: "open ChromeApp..."        │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  6. Сохранение в файл                   │
│     macro-queues/tiktok_auto_like.atlas │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  7. Предложение запустить               │
│     1. Запустить                        │
│     2. Посмотреть все                   │
└─────────────────────────────────────────┘
```

---

## 💡 Советы

### 1. Будьте конкретны
```
❌ "сделай что-то в TikTok"
✅ "открыть TikTok и поставить 5 лайков"
```

### 2. Указывайте последовательность
```
✅ "открыть Chrome, потом YouTube, потом найти Python"
```

### 3. Можно просить вариации
```
✅ "открыть TikTok и пролистать вниз, дай 2 варианта"
```

---

## 🐛 Решение проблем

### Ошибка: "AI генератор недоступен"
```bash
# Установите библиотеки
pip install openai anthropic google-generativeai
```

### Ошибка: "API ключ не установлен"
```bash
# Установите хотя бы один ключ
export OPENAI_API_KEY='your-key'
```

### Ошибка: "DSL справочник недоступен"
```bash
# Сгенерируйте справочник
python3 utils/dsl_reference_generator.py
```

---

## 📚 Документация

- **Главное приложение:** `docs/MACRO_AI_MASTER_README.md`
- **DSL:** `docs/DSL_YAML_EXPLAINED.md`
- **Макросы:** `macro-queues/README.md`

---

## 🎉 Преимущества

### Без AI генератора:
```
1. Открыть DSL справочник
2. Найти нужные команды
3. Найти нужные шаблоны
4. Написать .atlas файл вручную
5. Проверить синтаксис
6. Сохранить
7. Запустить
```

### С AI генератором:
```
1. Описать что нужно
2. Готово! ✅
```

**В 7 раз быстрее!** 🚀

---

**AI Macro Generator - создавай макросы мгновенно!** ⚡
