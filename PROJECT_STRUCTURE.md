# 📁 Структура проекта local-macros

## 🎯 Главные файлы (корень проекта)

### Основные скрипты

| Файл | Назначение | Документация |
|------|-----------|--------------|
| `main.py` | 🎮 Главное меню приложения | `README.md` |
| `macro_sequence.py` | ▶️ Запуск последовательностей макросов | `docs/CONFIG_RUN_EXPLAINED.md`<br>`docs/CONFIG_RUN_QUICKREF.md` |
| `atlas_dsl_parser.py` | 📝 Парсер DSL языка (.atlas файлы) | `docs/DSL_GUIDE.md`<br>`docs/DSL_CHEATSHEET.md`<br>`docs/DSL_README.md` |
| `sequence_builder.py` | 🔨 Построитель последовательностей | - |
| `parallel_runner.py` | 🚀 Параллельное выполнение макросов | `docs/ADVANCED_PARALLEL_GUIDE.md`<br>`docs/PARALLEL_EXECUTION_GUIDE.md` |
| `selenium_helper.py` | 🌐 Помощник для Selenium/браузера | `docs/DOM_AUTOMATION_GUIDE.md`<br>`docs/SELENIUM_INTEGRATION.md` |
| `start_chrome_debug.sh` | 🔧 Запуск Chrome в debug режиме | `docs/DOM_QUICK_START.md` |

---

## 📂 Папки проекта

### 1. 📚 `templates/` - Шаблоны для поиска

**Назначение:** Скриншоты элементов UI для template matching

**Структура:**
```
templates/
├── Chrome/
│   ├── ChromeBasicGuiButtons/
│   ├── TikTok/
│   └── YouTube/
├── Atlas/
├── Safari/
└── Telegram/
```

**Документация:**
- `docs/CREATE_TEMPLATES.md` - Как создавать шаблоны
- `docs/CREATE_TELEGRAM_TEMPLATE.md` - Шаблоны для Telegram
- `docs/TEMPLATE_MATCHING_GUIDE.md` - Поиск по шаблонам
- `docs/ADAPTIVE_BUTTONS.md` - Адаптивные кнопки

**Использование:** Шаблоны используются в DSL командах `click <template>`

---

### 2. 🛠️ `utils/` - Утилиты и инструменты

**Назначение:** Вспомогательные инструменты для работы с проектом

| Файл | Назначение | Документация |
|------|-----------|--------------|
| `ai_macro_generator.py` | 🤖 AI генератор макросов | `docs/AI_QUICK_START.md`<br>`docs/AI_SETUP.md`<br>`docs/AI_INTEGRATION.md`<br>`utils/AI_GENERATOR_README.md` |
| `dsl_reference_generator.py` | 📖 Генератор DSL справки | `docs/DSL_REFERENCE_QUICKSTART.md`<br>`docs/DSL_REFERENCE_UPDATED.md`<br>`utils/DSL_REFERENCE_GENERATOR_README.md` |
| `dom_selector_extractor.py` | 🔍 Извлечение DOM селекторов | `docs/DOM_AUTOMATION_GUIDE.md`<br>`docs/DOM_PARSER_INTEGRATION.md` |
| `dom_selector_tool.py` | 🎯 Интерактивный инструмент DOM | `docs/F12_COPY_GUIDE.md`<br>`docs/DOM_QUICK_START.md` |
| `simple_coordinate_finder.py` | 📍 Поиск координат на экране | `docs/COORDINATE_UTILS_README.md`<br>`docs/COORDINATE_CHEATSHEET.md` |
| `smart_capture.py` | 📸 Умный захват элементов | `docs/SMART_CAPTURE_GUIDE.md` |
| `path_watcher.py` | 👁️ Наблюдатель за изменениями | `utils/PATH_WATCHER_README.md` |
| `learning_stats.py` | 📊 Статистика обучения | `docs/LEARNING_SYSTEM_GUIDE.md` |
| `ai_dom_analyzer.py` | 🧠 AI анализ DOM структуры | `docs/AI_CONTEXT_EXPLAINED.md` |

---

### 3. 📝 `macros/` - Готовые макросы

**Назначение:** Готовые YAML последовательности

**Документация:**
- `docs/DSL_YAML_EXPLAINED.md` - Формат YAML
- `docs/YAML_STRUCTURE.md` - Структура файлов

**Примеры:**
```
macros/
├── tiktok_likes.yaml
├── youtube_search.yaml
└── telegram_send.yaml
```

---

### 4. 🎬 `macro-queues/` - Очередь макросов

**Назначение:** .atlas файлы (DSL формат) для выполнения

**Документация:**
- `docs/DSL_GUIDE.md` - DSL язык
- `docs/DSL_CHEATSHEET.md` - Шпаргалка

**Примеры:**
```
macro-queues/
├── ai_generated_macro_1.atlas
├── ai_generated_macro_2.atlas
└── custom_sequence.atlas
```

---

### 5. 🌐 `dom_selectors/` - DOM селекторы

**Назначение:** JSON файлы с CSS/XPath селекторами для веб-элементов

**Структура:**
```
dom_selectors/
├── tiktok_selectors.json
├── youtube_selectors.json
└── instagram_selectors.json
```

**Документация:**
- `docs/DOM_AUTOMATION_GUIDE.md` - Автоматизация через DOM
- `docs/DOM_QUICK_START.md` - Быстрый старт
- `docs/F12_COPY_GUIDE.md` - Копирование из DevTools
- `docs/DOM_VISION_NAMING.md` - Именование селекторов

**Использование:** Селекторы используются в DSL командах `selenium_click`, `selenium_type`

---

### 6. 📖 `dsl_references/` - DSL справочники

**Назначение:** Автоматически генерируемые справочники для AI

**Содержит:**
- Список доступных команд
- Список доступных шаблонов
- Примеры использования
- Лучшие практики

**Документация:**
- `docs/DSL_REFERENCE_QUICKSTART.md`
- `docs/DSL_REFERENCE_UPDATED.md`

**Генерация:**
```bash
python3 utils/dsl_reference_generator.py
```

---

### 7. 🎓 `learning/` - Система обучения

**Назначение:** CNN модели для распознавания элементов

**Структура:**
```
learning/
├── cnn_detector.py
├── training_data/
├── models/
└── datasets/
```

**Документация:**
- `docs/LEARNING_SYSTEM_GUIDE.md` - Система обучения
- `docs/CNN_VISION_GUIDE.md` - CNN детектор
- `docs/VISION_LEARNING_GUIDE.md` - Обучение моделей

**Использование:** Автоматическое улучшение поиска элементов

---

### 8. 🎮 `simulator/` - Симулятор макросов

**Назначение:** Dry-run выполнение без реальных действий

**Документация:**
- `docs/SIMULATOR_GUIDE.md` - Использование симулятора
- `docs/DRY_RUN_EXPLAINED.md` - Что такое dry-run

**Использование:** Тестирование макросов перед запуском

---

### 9. 📚 `examples/` - Примеры

**Назначение:** Примеры макросов и последовательностей

**Содержит:**
- Примеры YAML файлов
- Примеры .atlas файлов
- Примеры использования API

**Документация:**
- `docs/EXAMPLES_OVERVIEW.md`
- `docs/QUICK_START_EXAMPLES.md`

---

### 10. 🧪 `tests/` - Тесты

**Назначение:** Автоматические тесты проекта

**Документация:**
- `docs/TESTING_GUIDE.md`

---

### 11. 📱 `TelegramAI/` - Telegram интеграция

**Назначение:** Автоматизация Telegram через AI

**Документация:**
- `docs/TELEGRAM_GUIDE.md`
- `docs/CREATE_TELEGRAM_TEMPLATE.md`

---

### 12. 📄 `docs/` - Документация (89 файлов)

**Назначение:** Вся документация проекта

#### Категории документации:

**DSL и язык:**
- `DSL_GUIDE.md` - Основной гайд
- `DSL_CHEATSHEET.md` - Шпаргалка
- `DSL_README.md` - README
- `DSL_YAML_EXPLAINED.md` - YAML формат
- `DSL_VARIABLES_FIX.md` - Переменные

**AI генерация:**
- `AI_QUICK_START.md` - Быстрый старт
- `AI_SETUP.md` - Настройка
- `AI_INTEGRATION.md` - Интеграция
- `AI_CONTEXT_EXPLAINED.md` - Контекст
- `AI_NAMING_RULES.md` - Правила именования
- `AI_PAUSE_RULES.md` - Правила пауз

**DOM автоматизация:**
- `DOM_AUTOMATION_GUIDE.md` - Основной гайд
- `DOM_QUICK_START.md` - Быстрый старт
- `DOM_PARSER_INTEGRATION.md` - Интеграция парсера
- `F12_COPY_GUIDE.md` - Копирование из F12

**Координаты:**
- `COORDINATE_UTILS_README.md` - Утилиты координат
- `COORDINATE_CHEATSHEET.md` - Шпаргалка
- `COORDINATE_UTILS_SUMMARY.md` - Сводка

**Шаблоны:**
- `CREATE_TEMPLATES.md` - Создание шаблонов
- `TEMPLATE_MATCHING_GUIDE.md` - Поиск по шаблонам
- `ADAPTIVE_BUTTONS.md` - Адаптивные кнопки

**Параллельное выполнение:**
- `PARALLEL_EXECUTION_GUIDE.md` - Гайд
- `ADVANCED_PARALLEL_GUIDE.md` - Продвинутый гайд

**Обучение:**
- `LEARNING_SYSTEM_GUIDE.md` - Система обучения
- `CNN_VISION_GUIDE.md` - CNN детектор
- `VISION_LEARNING_GUIDE.md` - Обучение моделей

**Selenium:**
- `SELENIUM_INTEGRATION.md` - Интеграция
- `SELENIUM_GUIDE.md` - Гайд

**Разное:**
- `HUMANLIKE_BEHAVIOR.md` - Человекоподобное поведение
- `SMART_CAPTURE_GUIDE.md` - Умный захват
- `SIMULATOR_GUIDE.md` - Симулятор

---

## 🗺️ Карта зависимостей

```
main.py
  ├─→ macro_sequence.py
  │     ├─→ atlas_dsl_parser.py
  │     ├─→ templates/
  │     ├─→ dom_selectors/
  │     ├─→ learning/
  │     └─→ selenium_helper.py
  │
  ├─→ sequence_builder.py
  │     └─→ templates/
  │
  ├─→ parallel_runner.py
  │     └─→ macro_sequence.py
  │
  └─→ utils/
        ├─→ ai_macro_generator.py
        │     ├─→ dsl_references/
        │     └─→ templates/
        │
        ├─→ dsl_reference_generator.py
        │     ├─→ templates/
        │     └─→ dsl_references/
        │
        └─→ dom_selector_tool.py
              └─→ dom_selectors/
```

---

## 📊 Статистика проекта

```
Папок: 12
Основных файлов: 7
Утилит: 15+
Документов: 89
Шаблонов: 100+
```

---

## 🚀 Быстрый старт

### 1. Запуск приложения
```bash
python3 main.py
```

### 2. Запуск макроса
```bash
python3 macro_sequence.py --config macros/example.yaml --run sequence_name
```

### 3. Генерация с AI
```bash
python3 utils/ai_macro_generator.py
```

### 4. Создание DSL справки
```bash
python3 utils/dsl_reference_generator.py
```

### 5. Извлечение DOM селектора
```bash
python3 utils/dom_selector_tool.py
```

---

## 📚 Основная документация

**Начни с:**
1. `README.md` - Главный README
2. `docs/DSL_GUIDE.md` - Язык DSL
3. `docs/AI_QUICK_START.md` - AI генерация
4. `docs/DOM_QUICK_START.md` - DOM автоматизация

**Полный список:** 89 документов в `docs/`

---

**Структура проекта документирована! 📁**

**Все папки описаны! 📂**

**Документация связана! 📚**

**Готово к использованию! ✅**
