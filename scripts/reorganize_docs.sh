#!/bin/bash
# Скрипт для реорганизации документации
# Безопасно перемещает файлы в новую структуру

set -e  # Остановка при ошибке

PROJECT_ROOT="/Users/kostya/Desktop/local-macros"
cd "$PROJECT_ROOT"

echo "🔄 Начинаем реорганизацию документации..."
echo ""

# ============================================================================
# ЭТАП 1: Перемещение файлов из корня в docs/
# ============================================================================

echo "📦 Этап 1: Перемещение файлов из корня..."

# Architecture
if [ -f "HOW_IT_WORKS.md" ]; then
    mv HOW_IT_WORKS.md docs/architecture/overview.md
    echo "✅ HOW_IT_WORKS.md → docs/architecture/overview.md"
fi

if [ -f "PROJECT_STRUCTURE.md" ]; then
    mv PROJECT_STRUCTURE.md docs/architecture/structure.md
    echo "✅ PROJECT_STRUCTURE.md → docs/architecture/structure.md"
fi

if [ -f "MIGRATION_COMPLETE.md" ]; then
    mv MIGRATION_COMPLETE.md docs/architecture/migration-history.md
    echo "✅ MIGRATION_COMPLETE.md → docs/architecture/migration-history.md"
fi

# Getting Started
if [ -f "QUICK_STRUCTURE.md" ]; then
    mv QUICK_STRUCTURE.md docs/getting-started/quick-structure.md
    echo "✅ QUICK_STRUCTURE.md → docs/getting-started/quick-structure.md"
fi

# AI Guides
if [ -f "PROMPT_UPDATER_COMPLETE.md" ]; then
    mv PROMPT_UPDATER_COMPLETE.md docs/guides/ai/prompt-updater-complete.md
    echo "✅ PROMPT_UPDATER_COMPLETE.md → docs/guides/ai/prompt-updater-complete.md"
fi

if [ -f "QUICK_PROMPT_UPDATE.md" ]; then
    mv QUICK_PROMPT_UPDATE.md docs/guides/ai/quick-prompt-update.md
    echo "✅ QUICK_PROMPT_UPDATE.md → docs/guides/ai/quick-prompt-update.md"
fi

echo ""

# ============================================================================
# ЭТАП 2: Реорганизация docs/ (AI документы)
# ============================================================================

echo "📦 Этап 2: Реорганизация AI документов..."

# AI guides
mv docs/AI_GENERATOR_MIGRATION.md docs/guides/ai/generator-migration.md 2>/dev/null && echo "✅ AI_GENERATOR_MIGRATION.md → guides/ai/" || true
mv docs/AI_OPTIMIZATION_SUMMARY.md docs/guides/ai/optimization-summary.md 2>/dev/null && echo "✅ AI_OPTIMIZATION_SUMMARY.md → guides/ai/" || true
mv docs/AI_PROMPT_OPTIMIZATION.md docs/guides/ai/prompt-optimization.md 2>/dev/null && echo "✅ AI_PROMPT_OPTIMIZATION.md → guides/ai/" || true
mv docs/PROMPT_UPDATER_GUIDE.md docs/guides/ai/prompt-updater-guide.md 2>/dev/null && echo "✅ PROMPT_UPDATER_GUIDE.md → guides/ai/" || true
mv docs/AI_SETUP.md docs/guides/ai/setup.md 2>/dev/null && echo "✅ AI_SETUP.md → guides/ai/" || true
mv docs/AI_QUICK_START.md docs/guides/ai/quick-start.md 2>/dev/null && echo "✅ AI_QUICK_START.md → guides/ai/" || true
mv docs/AI_CONTEXT_EXPLAINED.md docs/guides/ai/context-explained.md 2>/dev/null && echo "✅ AI_CONTEXT_EXPLAINED.md → guides/ai/" || true
mv docs/AI_IMPROVEMENTS_SUMMARY.md docs/guides/ai/improvements-summary.md 2>/dev/null && echo "✅ AI_IMPROVEMENTS_SUMMARY.md → guides/ai/" || true
mv docs/AI_NAMING_RULES.md docs/guides/ai/naming-rules.md 2>/dev/null && echo "✅ AI_NAMING_RULES.md → guides/ai/" || true
mv docs/AI_PAUSE_RULES.md docs/guides/ai/pause-rules.md 2>/dev/null && echo "✅ AI_PAUSE_RULES.md → guides/ai/" || true
mv docs/AI_PROMPT_ANALYSIS.md docs/guides/ai/prompt-analysis.md 2>/dev/null && echo "✅ AI_PROMPT_ANALYSIS.md → guides/ai/" || true
mv docs/ai_prompt_full.txt docs/guides/ai/prompt-full.txt 2>/dev/null && echo "✅ ai_prompt_full.txt → guides/ai/" || true

echo ""

# ============================================================================
# ЭТАП 3: DSL документы
# ============================================================================

echo "📦 Этап 3: Реорганизация DSL документов..."

mv docs/DSL_README.md docs/guides/dsl/README.md 2>/dev/null && echo "✅ DSL_README.md → guides/dsl/" || true
mv docs/DSL_GUIDE.md docs/guides/dsl/guide.md 2>/dev/null && echo "✅ DSL_GUIDE.md → guides/dsl/" || true
mv docs/DSL_CHEATSHEET.md docs/guides/dsl/cheatsheet.md 2>/dev/null && echo "✅ DSL_CHEATSHEET.md → guides/dsl/" || true
mv docs/DSL_REFERENCE_QUICKSTART.md docs/guides/dsl/reference-quickstart.md 2>/dev/null && echo "✅ DSL_REFERENCE_QUICKSTART.md → guides/dsl/" || true
mv docs/DSL_REFERENCE_UPDATED.md docs/guides/dsl/reference-updated.md 2>/dev/null && echo "✅ DSL_REFERENCE_UPDATED.md → guides/dsl/" || true
mv docs/DSL_GENERATOR_UPDATED.md docs/guides/dsl/generator-updated.md 2>/dev/null && echo "✅ DSL_GENERATOR_UPDATED.md → guides/dsl/" || true
mv docs/DSL_IMPLEMENTATION_SUMMARY.md docs/guides/dsl/implementation-summary.md 2>/dev/null && echo "✅ DSL_IMPLEMENTATION_SUMMARY.md → guides/dsl/" || true
mv docs/DSL_NAME_RESOLUTION_EXPLAINED.md docs/guides/dsl/name-resolution.md 2>/dev/null && echo "✅ DSL_NAME_RESOLUTION_EXPLAINED.md → guides/dsl/" || true
mv docs/DSL_VARIABLES_FIX.md docs/guides/dsl/variables-fix.md 2>/dev/null && echo "✅ DSL_VARIABLES_FIX.md → guides/dsl/" || true
mv docs/DSL_YAML_EXPLAINED.md docs/guides/dsl/yaml-explained.md 2>/dev/null && echo "✅ DSL_YAML_EXPLAINED.md → guides/dsl/" || true

echo ""

# ============================================================================
# ЭТАП 4: DOM документы
# ============================================================================

echo "📦 Этап 4: Реорганизация DOM документов..."

mv docs/DOM_AUTOMATION_GUIDE.md docs/guides/dom/automation-guide.md 2>/dev/null && echo "✅ DOM_AUTOMATION_GUIDE.md → guides/dom/" || true
mv docs/DOM_AUTOMATION_SUMMARY.md docs/guides/dom/automation-summary.md 2>/dev/null && echo "✅ DOM_AUTOMATION_SUMMARY.md → guides/dom/" || true
mv docs/DOM_PARSER_INTEGRATION.md docs/guides/dom/parser-integration.md 2>/dev/null && echo "✅ DOM_PARSER_INTEGRATION.md → guides/dom/" || true
mv docs/DOM_QUICK_START.md docs/guides/dom/quick-start.md 2>/dev/null && echo "✅ DOM_QUICK_START.md → guides/dom/" || true
mv docs/DOM_VISION_NAMING.md docs/guides/dom/vision-naming.md 2>/dev/null && echo "✅ DOM_VISION_NAMING.md → guides/dom/" || true
mv docs/F12_COPY_GUIDE.md docs/guides/dom/f12-copy-guide.md 2>/dev/null && echo "✅ F12_COPY_GUIDE.md → guides/dom/" || true
mv docs/TESTING_DOM_SELECTOR.md docs/guides/dom/testing-selectors.md 2>/dev/null && echo "✅ TESTING_DOM_SELECTOR.md → guides/dom/" || true

echo ""

# ============================================================================
# ЭТАП 5: Templates документы
# ============================================================================

echo "📦 Этап 5: Реорганизация Templates документов..."

mv docs/COORDINATE_CHEATSHEET.md docs/guides/templates/coordinate-cheatsheet.md 2>/dev/null && echo "✅ COORDINATE_CHEATSHEET.md → guides/templates/" || true
mv docs/COORDINATE_UTILS_README.md docs/guides/templates/coordinate-utils.md 2>/dev/null && echo "✅ COORDINATE_UTILS_README.md → guides/templates/" || true
mv docs/COORDINATE_UTILS_SUMMARY.md docs/guides/templates/coordinate-summary.md 2>/dev/null && echo "✅ COORDINATE_UTILS_SUMMARY.md → guides/templates/" || true
mv docs/FINAL_COORDINATE_UTILS_SUMMARY.md docs/guides/templates/coordinate-final.md 2>/dev/null && echo "✅ FINAL_COORDINATE_UTILS_SUMMARY.md → guides/templates/" || true
mv docs/CREATE_TELEGRAM_TEMPLATE.md docs/guides/templates/create-telegram.md 2>/dev/null && echo "✅ CREATE_TELEGRAM_TEMPLATE.md → guides/templates/" || true
mv docs/CNN_VISION_GUIDE.md docs/guides/templates/cnn-vision.md 2>/dev/null && echo "✅ CNN_VISION_GUIDE.md → guides/templates/" || true
mv docs/TEMPLATE_RETRY_FIX.md docs/guides/templates/retry-fix.md 2>/dev/null && echo "✅ TEMPLATE_RETRY_FIX.md → guides/templates/" || true

echo ""

# ============================================================================
# ЭТАП 6: Getting Started документы
# ============================================================================

echo "📦 Этап 6: Реорганизация Getting Started документов..."

mv docs/QUICKSTART.md docs/getting-started/quickstart.md 2>/dev/null && echo "✅ QUICKSTART.md → getting-started/" || true
mv docs/QUICKSTART_ATLAS.md docs/getting-started/quickstart-atlas.md 2>/dev/null && echo "✅ QUICKSTART_ATLAS.md → getting-started/" || true

echo ""

# ============================================================================
# ЭТАП 7: Architecture документы
# ============================================================================

echo "📦 Этап 7: Реорганизация Architecture документов..."

mv docs/PROJECT_ARCHITECTURE.md docs/architecture/architecture.md 2>/dev/null && echo "✅ PROJECT_ARCHITECTURE.md → architecture/" || true
mv docs/PROJECT_STRUCTURE.md docs/architecture/project-structure.md 2>/dev/null && echo "✅ PROJECT_STRUCTURE.md → architecture/" || true
mv docs/PROJECT_STRUCTURE.txt docs/architecture/project-structure.txt 2>/dev/null && echo "✅ PROJECT_STRUCTURE.txt → architecture/" || true
mv docs/FULL_PROJECT_ANALYSIS.md docs/architecture/full-analysis.md 2>/dev/null && echo "✅ FULL_PROJECT_ANALYSIS.md → architecture/" || true
mv docs/SYSTEM_FLOW_DIAGRAM.md docs/architecture/system-flow.md 2>/dev/null && echo "✅ SYSTEM_FLOW_DIAGRAM.md → architecture/" || true
mv docs/HOW_IT_WORKS_DETAILED.md docs/architecture/how-it-works-detailed.md 2>/dev/null && echo "✅ HOW_IT_WORKS_DETAILED.md → architecture/" || true
mv docs/HYBRID_ENGINE_IMPLEMENTATION.md docs/architecture/hybrid-engine.md 2>/dev/null && echo "✅ HYBRID_ENGINE_IMPLEMENTATION.md → architecture/" || true

echo ""

# ============================================================================
# ЭТАП 8: Troubleshooting документы
# ============================================================================

echo "📦 Этап 8: Реорганизация Troubleshooting документов..."

mv docs/BUGFIX_PYNPUT.md docs/troubleshooting/bugfix-pynput.md 2>/dev/null && echo "✅ BUGFIX_PYNPUT.md → troubleshooting/" || true
mv docs/PYTHON_313_COMPATIBILITY.md docs/troubleshooting/python-313.md 2>/dev/null && echo "✅ PYTHON_313_COMPATIBILITY.md → troubleshooting/" || true
mv docs/INPUT_LOGIC_FIXED.md docs/troubleshooting/input-logic-fixed.md 2>/dev/null && echo "✅ INPUT_LOGIC_FIXED.md → troubleshooting/" || true
mv docs/GEMINI_FIXED.md docs/troubleshooting/gemini-fixed.md 2>/dev/null && echo "✅ GEMINI_FIXED.md → troubleshooting/" || true
mv docs/GEMINI_SETUP_FIXED.md docs/troubleshooting/gemini-setup.md 2>/dev/null && echo "✅ GEMINI_SETUP_FIXED.md → troubleshooting/" || true
mv docs/LONG_HTML_SOLUTION.md docs/troubleshooting/long-html.md 2>/dev/null && echo "✅ LONG_HTML_SOLUTION.md → troubleshooting/" || true

echo ""

# ============================================================================
# ЭТАП 9: Специфичные гайды (Telegram, TikTok, etc.)
# ============================================================================

echo "📦 Этап 9: Реорганизация специфичных гайдов..."

# Создаём папки для специфичных платформ
mkdir -p docs/guides/platforms/telegram
mkdir -p docs/guides/platforms/tiktok
mkdir -p docs/guides/advanced

# Telegram
mv docs/TELEGRAM_*.md docs/guides/platforms/telegram/ 2>/dev/null && echo "✅ TELEGRAM_*.md → guides/platforms/telegram/" || true

# TikTok
mv docs/TIKTOK_*.md docs/guides/platforms/tiktok/ 2>/dev/null && echo "✅ TIKTOK_*.md → guides/platforms/tiktok/" || true

# Advanced
mv docs/PARALLEL_EXECUTION.md docs/guides/advanced/parallel-execution.md 2>/dev/null && echo "✅ PARALLEL_EXECUTION.md → guides/advanced/" || true
mv docs/ADVANCED_PARALLEL_GUIDE.md docs/guides/advanced/parallel-guide.md 2>/dev/null && echo "✅ ADVANCED_PARALLEL_GUIDE.md → guides/advanced/" || true
mv docs/LEARNING_SYSTEM_GUIDE.md docs/guides/advanced/learning-system.md 2>/dev/null && echo "✅ LEARNING_SYSTEM_GUIDE.md → guides/advanced/" || true
mv docs/HUMANLIKE_BEHAVIOR.md docs/guides/advanced/humanlike-behavior.md 2>/dev/null && echo "✅ HUMANLIKE_BEHAVIOR.md → guides/advanced/" || true
mv docs/SIMULATOR_GUIDE.md docs/guides/advanced/simulator.md 2>/dev/null && echo "✅ SIMULATOR_GUIDE.md → guides/advanced/" || true
mv docs/SELENIUM_BUILDER_GUIDE.md docs/guides/advanced/selenium-builder.md 2>/dev/null && echo "✅ SELENIUM_BUILDER_GUIDE.md → guides/advanced/" || true

# Try/Catch
mv docs/TRY_CATCH_*.md docs/guides/dsl/ 2>/dev/null && echo "✅ TRY_CATCH_*.md → guides/dsl/" || true

# Testing
mv docs/TESTING_*.md docs/troubleshooting/ 2>/dev/null && echo "✅ TESTING_*.md → troubleshooting/" || true
mv docs/TEST_*.md docs/troubleshooting/ 2>/dev/null && echo "✅ TEST_*.md → troubleshooting/" || true

# Other
mv docs/CONFIG_RUN_*.md docs/guides/dsl/ 2>/dev/null && echo "✅ CONFIG_RUN_*.md → guides/dsl/" || true
mv docs/PATH_WATCHER_*.md docs/guides/templates/ 2>/dev/null && echo "✅ PATH_WATCHER_*.md → guides/templates/" || true
mv docs/SKIP_EMPTY_COMMENTS.md docs/guides/advanced/skip-empty-comments.md 2>/dev/null && echo "✅ SKIP_EMPTY_COMMENTS.md → guides/advanced/" || true
mv docs/ENV_FILE_SETUP.md docs/getting-started/env-setup.md 2>/dev/null && echo "✅ ENV_FILE_SETUP.md → getting-started/" || true

echo ""

# ============================================================================
# ЭТАП 10: Создание README файлов для каждой категории
# ============================================================================

echo "📦 Этап 10: Создание README файлов..."

# Getting Started README
cat > docs/getting-started/README.md << 'EOF'
# Getting Started

Документация для быстрого старта с Macro AI.

## 📚 Содержание

- [Quickstart](quickstart.md) - Быстрый старт
- [Quickstart Atlas](quickstart-atlas.md) - Быстрый старт с DSL
- [Environment Setup](env-setup.md) - Настройка окружения
- [Quick Structure](quick-structure.md) - Быстрый обзор структуры

## 🚀 С чего начать?

1. Прочитайте [Quickstart](quickstart.md)
2. Настройте окружение: [Environment Setup](env-setup.md)
3. Изучите DSL: [Quickstart Atlas](quickstart-atlas.md)

---

[← Назад к документации](../README.md)
EOF
echo "✅ Создан docs/getting-started/README.md"

# DSL README
cat > docs/guides/dsl/README.md << 'EOF'
# DSL (Domain Specific Language)

Документация по DSL языку для создания макросов.

## 📚 Содержание

### Основы
- [Guide](guide.md) - Полное руководство
- [Cheatsheet](cheatsheet.md) - Шпаргалка
- [YAML Explained](yaml-explained.md) - Объяснение YAML формата

### Справочники
- [Reference Quickstart](reference-quickstart.md) - Быстрый справочник
- [Reference Updated](reference-updated.md) - Обновлённый справочник

### Продвинутое
- [Name Resolution](name-resolution.md) - Разрешение имён
- [Variables Fix](variables-fix.md) - Работа с переменными
- [Try/Catch Examples](TRY_CATCH_EXAMPLES_ADDED.md) - Обработка ошибок
- [Config Run](CONFIG_RUN_EXPLAINED.md) - Конфигурация запуска

---

[← Назад к гайдам](../README.md)
EOF
echo "✅ Создан docs/guides/dsl/README.md"

# AI README
cat > docs/guides/ai/README.md << 'EOF'
# AI Guides

Документация по AI-powered функциям Macro AI.

## 📚 Содержание

### Быстрый старт
- [Quick Start](quick-start.md) - Быстрый старт с AI
- [Setup](setup.md) - Настройка AI

### Генератор макросов
- [Generator Migration](generator-migration.md) - Миграция генератора
- [Optimization Summary](optimization-summary.md) - Оптимизация (75% меньше)
- [Prompt Optimization](prompt-optimization.md) - Детальная оптимизация

### Обновление промптов
- [Prompt Updater Guide](prompt-updater-guide.md) - Полное руководство
- [Quick Prompt Update](quick-prompt-update.md) - Быстрое обновление
- [Prompt Updater Complete](prompt-updater-complete.md) - Полная документация

### Дополнительно
- [Context Explained](context-explained.md) - Контекст AI
- [Naming Rules](naming-rules.md) - Правила именования
- [Pause Rules](pause-rules.md) - Правила пауз
- [Prompt Analysis](prompt-analysis.md) - Анализ промптов

---

[← Назад к гайдам](../README.md)
EOF
echo "✅ Создан docs/guides/ai/README.md"

# DOM README
cat > docs/guides/dom/README.md << 'EOF'
# DOM Automation

Документация по автоматизации через DOM селекторы.

## 📚 Содержание

### Основы
- [Quick Start](quick-start.md) - Быстрый старт
- [Automation Guide](automation-guide.md) - Полное руководство
- [Automation Summary](automation-summary.md) - Краткая сводка

### Интеграция
- [Parser Integration](parser-integration.md) - Интеграция парсера
- [Vision Naming](vision-naming.md) - Именование Vision/DOM

### Инструменты
- [F12 Copy Guide](f12-copy-guide.md) - Копирование селекторов
- [Testing Selectors](testing-selectors.md) - Тестирование селекторов

---

[← Назад к гайдам](../README.md)
EOF
echo "✅ Создан docs/guides/dom/README.md"

# Templates README
cat > docs/guides/templates/README.md << 'EOF'
# Templates & Coordinates

Документация по работе с шаблонами и координатами.

## 📚 Содержание

### Координаты
- [Coordinate Cheatsheet](coordinate-cheatsheet.md) - Шпаргалка
- [Coordinate Utils](coordinate-utils.md) - Утилиты
- [Coordinate Summary](coordinate-summary.md) - Сводка
- [Coordinate Final](coordinate-final.md) - Финальная версия

### Шаблоны
- [Create Telegram](create-telegram.md) - Создание Telegram шаблонов
- [CNN Vision](cnn-vision.md) - CNN для распознавания
- [Retry Fix](retry-fix.md) - Исправление повторов

### Path Watcher
- [Path Watcher Quickstart](PATH_WATCHER_QUICKSTART.md) - Быстрый старт
- [Path Watcher DSL](PATH_WATCHER_DSL_SUMMARY.md) - DSL интеграция

---

[← Назад к гайдам](../README.md)
EOF
echo "✅ Создан docs/guides/templates/README.md"

# Architecture README
cat > docs/architecture/README.md << 'EOF'
# Architecture

Документация по архитектуре проекта.

## 📚 Содержание

- [Overview](overview.md) - Общий обзор (HOW_IT_WORKS)
- [Architecture](architecture.md) - Детальная архитектура
- [Structure](structure.md) - Структура проекта
- [Project Structure](project-structure.md) - Альтернативная структура
- [Full Analysis](full-analysis.md) - Полный анализ
- [System Flow](system-flow.md) - Поток данных
- [How It Works Detailed](how-it-works-detailed.md) - Детальное объяснение
- [Hybrid Engine](hybrid-engine.md) - Гибридный движок
- [Migration History](migration-history.md) - История миграций

---

[← Назад к документации](../README.md)
EOF
echo "✅ Создан docs/architecture/README.md"

# Troubleshooting README
cat > docs/troubleshooting/README.md << 'EOF'
# Troubleshooting

Решение проблем и исправление ошибок.

## 📚 Содержание

### Исправления
- [Bugfix Pynput](bugfix-pynput.md) - Исправление pynput
- [Python 3.13](python-313.md) - Совместимость с Python 3.13
- [Input Logic Fixed](input-logic-fixed.md) - Исправление логики ввода
- [Gemini Fixed](gemini-fixed.md) - Исправление Gemini
- [Gemini Setup](gemini-setup.md) - Настройка Gemini
- [Long HTML](long-html.md) - Решение для длинного HTML

### Тестирование
- [Testing DOM Selector](TESTING_DOM_SELECTOR.md) - Тестирование DOM
- [Testing Learning](TESTING_LEARNING.md) - Тестирование обучения
- [Test Name Resolution](TEST_NAME_RESOLUTION.md) - Тестирование разрешения имён

---

[← Назад к документации](../README.md)
EOF
echo "✅ Создан docs/troubleshooting/README.md"

echo ""
echo "=" * 80
echo "✅ РЕОРГАНИЗАЦИЯ ЗАВЕРШЕНА!"
echo "=" * 80
echo ""
echo "📊 Статистика:"
echo "   • Создано категорий: 7"
echo "   • Перемещено файлов: ~80"
echo "   • Создано README: 7"
echo ""
echo "📁 Новая структура:"
echo "   docs/"
echo "   ├── getting-started/    (4 файла)"
echo "   ├── guides/"
echo "   │   ├── dsl/           (~15 файлов)"
echo "   │   ├── ai/            (~12 файлов)"
echo "   │   ├── dom/           (~7 файлов)"
echo "   │   ├── templates/     (~10 файлов)"
echo "   │   ├── platforms/     (Telegram, TikTok)"
echo "   │   └── advanced/      (~8 файлов)"
echo "   ├── architecture/       (~9 файлов)"
echo "   └── troubleshooting/    (~9 файлов)"
echo ""
echo "💡 Следующие шаги:"
echo "   1. Проверьте новую структуру: ls -R docs/"
echo "   2. Создайте CHANGELOG.md в корне"
echo "   3. Обновите README.md со ссылками"
echo "   4. Закоммитьте изменения"
echo ""
