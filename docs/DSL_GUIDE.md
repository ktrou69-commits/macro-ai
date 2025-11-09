# 📝 DSL Guide - Руководство по Domain Specific Language

## 🎯 Что такое DSL?

**DSL (Domain Specific Language)** — упрощенный язык для создания последовательностей макросов.

Вместо сложного YAML:
```yaml
steps:
  - action: click
    template: templates/Chrome/ChromeBasicGuiButtons/ChromeApp-btn.png
    clicks: 1
```

Пишешь просто:
```
click ChromeApp
```

---

## 🚀 Быстрый старт

### 1. Создай файл `.atlas`

```bash
touch my_automation.atlas
```

### 2. Напиши последовательность

```
# Мой первый скрипт
open ChromeApp
wait 2s
click ChromeNewTab
type "Hello World"
press enter
```

### 3. Запусти

```bash
python3 macro_sequence.py --config my_automation.atlas --run my_automation
```

---

## 📚 Синтаксис DSL

### 🖱️ OPEN - Запуск приложения

```
open ChromeApp
open Safari
open Finder
```

**Что делает:** Кликает по иконке приложения и ждет его загрузки.

**YAML эквивалент:**
```yaml
- action: click
  template: templates/.../ChromeApp-btn.png
  clicks: 1
  wait_for_appear: true
  timeout: 3.0
```

---

### 🖱️ CLICK - Клик по кнопке

```
click ChromeNewTab
click TikTok-Like
click YouTube-Subscribe
```

**По координатам:**
```
click (500, 300)
```

**YAML эквивалент:**
```yaml
- action: click
  template: templates/.../ChromeNewTab-btn.png
  clicks: 1
```

---

### 🖱️ DOUBLE_CLICK - Двойной клик

```
double_click ChromeApp
dclick FileIcon
```

**YAML эквивалент:**
```yaml
- action: click
  template: templates/.../ChromeApp-btn.png
  clicks: 2
  interval: 0.3
```

---

### ⌨️ TYPE - Ввод текста

```
type "Hello World"
type 'Python automation'
type Привет мир
```

**YAML эквивалент:**
```yaml
- action: type
  text: "Hello World"
```

---

### 🔘 PRESS - Нажатие клавиши

```
press enter
press tab
press esc
press space
press backspace
```

**YAML эквивалент:**
```yaml
- action: key
  key: enter
```

---

### 🎹 HOTKEY - Комбинация клавиш

```
hotkey command+t
hotkey command+w
hotkey command+shift+n
hotkey ctrl+c
```

**YAML эквивалент:**
```yaml
- action: hotkey
  keys: [command, t]
```

---

### ⏸️ WAIT - Пауза

```
wait 2s
wait 1.5s
wait 500ms
wait 0.3s
```

**Форматы:**
- `2s` — 2 секунды
- `1.5s` — 1.5 секунды
- `500ms` — 500 миллисекунд

**YAML эквивалент:**
```yaml
- action: wait
  duration: 2.0
```

---

### 🖱️ SCROLL - Скролл

```
scroll down
scroll up
scroll down 10
scroll up 5
```

**YAML эквивалент:**
```yaml
- action: scroll
  direction: down
  amount: 5
  clicks: 1
```

---

### 🔄 REPEAT - Повторение

```
repeat 10:
  click TikTok-Like
  wait 1s
  scroll down
  wait 2s
```

**Важно:** Используй отступы (2 пробела или tab) для вложенных команд!

**YAML эквивалент:**
```yaml
- action: repeat
  times: 10
  steps:
    - action: click
      template: templates/.../TikTok-Like-btn.png
    - action: wait
      duration: 1.0
    - action: scroll
      direction: down
    - action: wait
      duration: 2.0
```

---

## 🎯 Примеры

### Пример 1: TikTok Auto Like

**Файл:** `tiktok_auto_like.atlas`

```
# TikTok Auto Like
# Автоматические лайки в TikTok

open ChromeApp
wait 2.5s

click ChromeNewTab
wait 0.5s

click ChromeSearchField
type "tiktok.com"
press enter
wait 4s

repeat 10:
  click TikTok-Like
  wait 1.5s
  scroll down
  wait 2s
```

**Запуск:**
```bash
python3 macro_sequence.py --config tiktok_auto_like.atlas --run tiktok_auto_like
```

---

### Пример 2: Chrome Quick Search

**Файл:** `chrome_search.atlas`

```
# Chrome Quick Search

open ChromeApp
wait 2.5s

click ChromeNewTab
wait 0.5s

click ChromeSearchField
type "Python automation tutorial"
press enter
wait 3s

scroll down 5
wait 1s
scroll down 5
```

---

### Пример 3: TikTok Comment Bot

**Файл:** `tiktok_comment.atlas`

```
# TikTok Comment Bot

# Запуск и переход на TikTok
open ChromeApp
wait 2.5s
click ChromeNewTab
wait 0.5s
click ChromeSearchField
type "tiktok.com"
press enter
wait 4s

# Поиск по хештегу
click TikTok-Search
wait 1s
click TikTok-SearchField
type "#python"
press enter
wait 3s

# Открыть первое видео
click TikTok-VideoFirst
wait 2s

# Цикл комментариев
repeat 5:
  click TikTok-Comment
  wait 1s
  
  click TikTok-CommentField
  type "Отличное видео! 🔥"
  wait 0.5s
  
  click TikTok-CommentSend
  wait 2s
  
  scroll down
  wait 3s
```

---

### Пример 4: Multi-Tab Research

**Файл:** `research.atlas`

```
# Multi-Tab Research

open ChromeApp
wait 2.5s

# GitHub
click ChromeNewTab
wait 0.5s
click ChromeSearchField
type "github.com"
press enter
wait 2s

# Stack Overflow
click ChromeNewTab
wait 0.5s
click ChromeSearchField
type "stackoverflow.com"
press enter
wait 2s

# YouTube
click ChromeNewTab
wait 0.5s
click ChromeSearchField
type "youtube.com"
press enter
```

---

## 🔧 Как работает парсер

### Разрешение имен шаблонов

Парсер автоматически находит шаблоны по коротким именам:

```
click TikTok-Like
```

Парсер ищет:
1. `Chrome-TikTok-Like-btn.png`
2. `Chrome-TikTok-Like.png`
3. `TikTok-Like-btn.png`
4. `TikTok-Like.png`

И находит полный путь: `templates/Chrome/TikTok/Chrome-TikTok-Like-btn.png`

---

## 📝 Комментарии

```
# Это комментарий
click Button  # Это тоже комментарий

# Можно писать многострочные комментарии:
# Строка 1
# Строка 2
# Строка 3
```

---

## 🎨 Стиль кода

### ✅ Хороший стиль

```
# Описание что делает скрипт
open ChromeApp
wait 2.5s

# Группируем логически связанные действия
click ChromeNewTab
wait 0.5s

# Используем понятные имена
click TikTok-Like
wait 1s

# Отступы для repeat
repeat 10:
  click Button
  wait 1s
```

### ❌ Плохой стиль

```
open ChromeApp
wait 2.5s
click ChromeNewTab
wait 0.5s
click TikTok-Like
wait 1s
repeat 10:
click Button
wait 1s
```

---

## 🛠️ Конвертация DSL → YAML

### Вручную

```bash
python3 atlas_dsl_parser.py my_script.atlas my_script.yaml
```

### Автоматически при запуске

```bash
python3 macro_sequence.py --config my_script.atlas --run my_script
```

Парсер автоматически конвертирует `.atlas` в YAML при загрузке!

---

## 🎯 Преимущества DSL

### 1. Простота
```
# DSL
click Button
wait 1s

# YAML
- action: click
  template: templates/Button.png
  clicks: 1
- action: wait
  duration: 1.0
```

### 2. Читаемость
DSL читается как обычный текст, а не как конфиг.

### 3. Скорость
Писать DSL в 3-5 раз быстрее чем YAML.

### 4. Меньше ошибок
Нет проблем с отступами YAML, кавычками, синтаксисом.

---

## 🔮 Будущие возможности

### Переменные
```
set search_query = "Python tutorial"
type {search_query}
```

### Условия
```
if found TikTok-Like:
  click TikTok-Like
else:
  scroll down 
```
 
### Функции
```
define search(query):
  click SearchField
  type {query}
  press enter

search("Python")
search("JavaScript")
```

---

## 📚 Ресурсы

- `atlas_dsl_parser.py` — парсер DSL
- `examples/*.atlas` — примеры скриптов
- `docs/DSL_GUIDE.md` — это руководство

---

**Macro AI DSL — Автоматизация простым языком!** 🚀
