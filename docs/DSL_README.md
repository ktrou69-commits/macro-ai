# 🚀 DSL для Macro AI — Быстрый старт

## Что это?

**DSL (Domain Specific Language)** — простой язык для создания автоматизаций.

### Было (YAML):
```yaml
sequences:
  my_automation:
    steps:
    - action: click
      template: templates/Chrome/ChromeBasicGuiButtons/ChromeApp-btn.png
      clicks: 1
    - action: wait
      duration: 2.0
    - action: type
      text: "Hello"
```

### Стало (DSL):
```
open ChromeApp
wait 2s
type "Hello"
```

**В 5 раз короче! В 10 раз понятнее!**

---

## ⚡ Быстрый старт

### 1. Создай файл `.atlas`

```bash
nano my_first_automation.atlas
```

### 2. Напиши скрипт

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
python3 macro_sequence.py --config my_first_automation.atlas --run my_first_automation
```

**Готово!** 🎉

---

## 📚 Основные команды

| Команда | Описание | Пример |
|---------|----------|--------|
| `open` | Запустить приложение | `open ChromeApp` |
| `click` | Кликнуть по кнопке | `click TikTok-Like` |
| `type` | Ввести текст | `type "Hello"` |
| `press` | Нажать клавишу | `press enter` |
| `hotkey` | Комбинация клавиш | `hotkey command+t` |
| `wait` | Пауза | `wait 2s` |
| `scroll` | Скролл | `scroll down` |
| `repeat` | Повторить | `repeat 10:` |

---

## 🎯 Примеры

### TikTok Auto Like

**Файл:** `tiktok_like.atlas`

```
open ChromeApp
wait 2.5s
click ChromeNewTab
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
python3 macro_sequence.py --config tiktok_like.atlas --run tiktok_like
```

---

### Chrome Quick Search

**Файл:** `search.atlas`

```
open ChromeApp
wait 2s
click ChromeNewTab
click ChromeSearchField
type "Python tutorial"
press enter
```

**Запуск:**
```bash
python3 macro_sequence.py --config search.atlas --run search
```

---

## 🔄 Повторение (Loops)

```
repeat 5:
  click Button
  wait 1s
  scroll down
```

**Важно:** Используй отступы (2 пробела) для вложенных команд!

---

## 💡 Советы

### 1. Используй комментарии
```
# Это комментарий
open ChromeApp  # Запуск Chrome
```

### 2. Группируй логически
```
# Открытие Chrome
open ChromeApp
wait 2s

# Новая вкладка
click ChromeNewTab
wait 0.5s

# Поиск
click SearchField
type "query"
press enter
```

### 3. Добавляй паузы
```
click Button
wait 1s  # Ждем загрузки
```

---

## 🛠️ Конвертация в YAML

Если нужен YAML:

```bash
python3 atlas_dsl_parser.py my_script.atlas my_script.yaml
```

---

## 📁 Структура проекта

```
local-macros/
├── atlas_dsl_parser.py          # Парсер DSL
├── macro_sequence.py             # Запуск (поддерживает .atlas)
├── examples/
│   ├── tiktok_auto_like.atlas   # Пример 1
│   ├── chrome_search.atlas      # Пример 2
│   └── tiktok_comment.atlas     # Пример 3
└── docs/
    └── DSL_GUIDE.md             # Полное руководство
```

---

## 🎓 Обучение

### Шаг 1: Простой скрипт
```
open ChromeApp
wait 2s
```

### Шаг 2: Добавь действия
```
open ChromeApp
wait 2s
click ChromeNewTab
type "Hello"
press enter
```

### Шаг 3: Добавь цикл
```
open ChromeApp
wait 2s

repeat 5:
  click Button
  wait 1s
```

### Шаг 4: Создай сложный workflow
```
open ChromeApp
wait 2s

repeat 10:
  click TikTok-Like
  wait 1s
  scroll down
  wait 2s
```

---

## 🚀 Готовые примеры

В папке `examples/` есть готовые скрипты:

1. **tiktok_auto_like.atlas** — автолайки TikTok
2. **tiktok_comment.atlas** — автокомментарии TikTok
3. **chrome_quick_search.atlas** — быстрый поиск Chrome
4. **tiktok_research_workflow.atlas** — комплексный workflow

**Запуск:**
```bash
python3 macro_sequence.py --config examples/tiktok_auto_like.atlas --run tiktok_auto_like
```

---

## 📖 Полная документация

Смотри: `docs/DSL_GUIDE.md`

---

## ❓ FAQ

### Q: Какие имена кнопок использовать?

A: Смотри файлы `structure.txt` в папках `templates/`:
- `templates/Chrome/ChromeBasicGuiButtons/structure.txt`
- `templates/Chrome/TikTok/structure.txt`

### Q: Как узнать доступные команды?

A: Смотри `docs/DSL_GUIDE.md` — там все команды с примерами.

### Q: Можно ли использовать YAML и DSL вместе?

A: Да! Используй `.yaml` для сложных конфигов, `.atlas` для простых скриптов.

### Q: Как отладить скрипт?

A: Добавь больше `wait` команд и запускай пошагово.

---

## 🎉 Начни прямо сейчас!

```bash
# 1. Создай файл
nano my_automation.atlas

# 2. Напиши
open ChromeApp
wait 2s
type "Hello World"

# 3. Запусти
python3 macro_sequence.py --config my_automation.atlas --run my_automation
```

**Macro AI DSL — Автоматизация за 3 строки!** 🚀
