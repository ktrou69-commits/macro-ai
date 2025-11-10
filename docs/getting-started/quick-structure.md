# ⚡ Быстрая структура проекта

## 📁 Папки (что за что отвечает)

```
local-macros/
│
├── 📝 macros/              → Готовые YAML последовательности
├── 🎬 macro-queues/        → .atlas файлы (DSL формат)
├── 📚 templates/           → Скриншоты элементов UI
├── 🌐 dom_selectors/       → CSS/XPath селекторы
├── 📖 dsl_references/      → Справочники для AI
├── 🛠️  utils/              → Утилиты и инструменты
├── 🎓 learning/            → CNN модели обучения
├── 🎮 simulator/           → Симулятор (dry-run)
├── 📚 examples/            → Примеры использования
├── 🧪 tests/               → Тесты
├── 📱 TelegramAI/          → Telegram интеграция
└── 📄 docs/                → Документация (89 файлов)
```

---

## 🎯 Главные файлы

```
main.py                  → 🎮 Главное меню
macro_sequence.py        → ▶️  Запуск макросов
atlas_dsl_parser.py      → 📝 Парсер DSL
sequence_builder.py      → 🔨 Построитель
parallel_runner.py       → 🚀 Параллельное выполнение
selenium_helper.py       → 🌐 Selenium помощник
```

---

## 📚 Документация к папкам

### 📝 macros/ + macro-queues/
```
docs/DSL_GUIDE.md
docs/DSL_CHEATSHEET.md
docs/DSL_YAML_EXPLAINED.md
docs/CONFIG_RUN_EXPLAINED.md
```

### 📚 templates/
```
docs/CREATE_TEMPLATES.md
docs/TEMPLATE_MATCHING_GUIDE.md
docs/ADAPTIVE_BUTTONS.md
```

### 🌐 dom_selectors/
```
docs/DOM_AUTOMATION_GUIDE.md
docs/DOM_QUICK_START.md
docs/F12_COPY_GUIDE.md
docs/DOM_PARSER_INTEGRATION.md
```

### 🛠️ utils/
```
utils/AI_GENERATOR_README.md
utils/DSL_REFERENCE_GENERATOR_README.md
utils/PATH_WATCHER_README.md
docs/AI_QUICK_START.md
docs/COORDINATE_UTILS_README.md
```

### 🎓 learning/
```
docs/LEARNING_SYSTEM_GUIDE.md
docs/CNN_VISION_GUIDE.md
docs/VISION_LEARNING_GUIDE.md
```

### 🎮 simulator/
```
docs/SIMULATOR_GUIDE.md
docs/DRY_RUN_EXPLAINED.md
```

### 🚀 parallel_runner.py
```
docs/PARALLEL_EXECUTION_GUIDE.md
docs/ADVANCED_PARALLEL_GUIDE.md
```

---

## 🔄 Workflow

```
1. Создание макроса:
   utils/ai_macro_generator.py → macro-queues/*.atlas

2. Запуск макроса:
   main.py → macro_sequence.py → atlas_dsl_parser.py

3. Поиск элементов:
   templates/ (скриншоты)
   dom_selectors/ (CSS/XPath)
   learning/ (CNN модели)

4. Генерация справки:
   utils/dsl_reference_generator.py → dsl_references/
```

---

## 📊 Статистика

```
Папок:        12
Файлов:       7 основных
Утилит:       15+
Документов:   89
Шаблонов:     100+
```

---

**Полная документация:** `PROJECT_STRUCTURE.md`
