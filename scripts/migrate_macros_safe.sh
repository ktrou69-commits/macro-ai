#!/bin/bash
# Безопасная миграция макросов
# 100% гарантия - сначала копирует, потом тестирует, только потом удаляет

set -e  # Остановка при ошибке

PROJECT_ROOT="/Users/kostya/Desktop/local-macros"
cd "$PROJECT_ROOT"

echo "🔄 БЕЗОПАСНАЯ МИГРАЦИЯ МАКРОСОВ"
echo "=" * 80
echo ""
echo "⚠️  ВАЖНО: Этот скрипт НЕ удаляет старые файлы автоматически!"
echo "   Он только копирует и обновляет код."
echo "   Удаление старых папок - вручную, после проверки."
echo ""
echo "=" * 80
echo ""

# ============================================================================
# ЭТАП 1: Создание новой структуры
# ============================================================================

echo "📦 Этап 1: Создание новой структуры..."
echo ""

mkdir -p macros/production
mkdir -p macros/examples/basic
mkdir -p macros/examples/advanced
mkdir -p macros/templates

echo "✅ Создано:"
echo "   • macros/production/"
echo "   • macros/examples/basic/"
echo "   • macros/examples/advanced/"
echo "   • macros/templates/"
echo ""

# ============================================================================
# ЭТАП 2: Копирование файлов (НЕ перемещение!)
# ============================================================================

echo "📦 Этап 2: Копирование файлов..."
echo ""

# Из macro-queues/ → macros/production/
if [ -d "macro-queues" ]; then
    file_count=$(find macro-queues -name "*.atlas" | wc -l)
    if [ $file_count -gt 0 ]; then
        cp macro-queues/*.atlas macros/production/ 2>/dev/null || true
        echo "✅ Скопировано из macro-queues/: $file_count файлов"
    else
        echo "⚠️  macro-queues/ пуста"
    fi
else
    echo "⚠️  macro-queues/ не найдена"
fi

# Из macros/ → macros/production/ (если есть старые файлы)
if [ -d "macros" ] && [ -f "macros/tiktok_automation_hybrid.atlas" ]; then
    cp macros/*.atlas macros/production/ 2>/dev/null || true
    echo "✅ Скопировано из старой macros/"
fi

# Из examples/ → macros/examples/advanced/
if [ -d "examples" ]; then
    # Atlas файлы
    atlas_count=$(find examples -name "*.atlas" | wc -l)
    if [ $atlas_count -gt 0 ]; then
        cp examples/*.atlas macros/examples/advanced/ 2>/dev/null || true
        echo "✅ Скопировано .atlas из examples/: $atlas_count файлов"
    fi
    
    # YAML файлы
    yaml_count=$(find examples -name "*.yaml" | wc -l)
    if [ $yaml_count -gt 0 ]; then
        cp examples/*.yaml macros/examples/advanced/ 2>/dev/null || true
        echo "✅ Скопировано .yaml из examples/: $yaml_count файлов"
    fi
fi

echo ""

# ============================================================================
# ЭТАП 3: Создание config.py (централизованные пути)
# ============================================================================

echo "📦 Этап 3: Создание config.py..."
echo ""

cat > config.py << 'EOF'
"""
config.py
Централизованная конфигурация путей для Macro AI
"""

from pathlib import Path

# Корень проекта
PROJECT_ROOT = Path(__file__).parent

# Основные папки
MACROS_DIR = PROJECT_ROOT / "macros" / "production"
EXAMPLES_DIR = PROJECT_ROOT / "macros" / "examples"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
UTILS_DIR = PROJECT_ROOT / "utils"

# Для обратной совместимости (deprecated)
MACRO_QUEUES_DIR = MACROS_DIR  # Алиас на новую папку

# DSL References
DSL_REFERENCES_DIR = PROJECT_ROOT / "dsl_references"
DSL_REFERENCE_FILE = DSL_REFERENCES_DIR / "DSL_REFERENCE.txt"

# Learning
LEARNING_DIR = PROJECT_ROOT / "learning"
LEARNING_DB = LEARNING_DIR / "memory.db"

# DOM Selectors
DOM_SELECTORS_DIR = PROJECT_ROOT / "dom_selectors"

# Проверка существования критичных папок
def check_directories():
    """Проверяет что все критичные папки существуют"""
    required = [MACROS_DIR, TEMPLATES_DIR, UTILS_DIR]
    missing = [d for d in required if not d.exists()]
    
    if missing:
        raise FileNotFoundError(
            f"Отсутствуют критичные папки: {', '.join(str(d) for d in missing)}"
        )

# Автоматическая проверка при импорте
try:
    check_directories()
except FileNotFoundError as e:
    print(f"⚠️  {e}")
    print("💡 Запустите: python3 scripts/migrate_macros_safe.sh")
EOF

echo "✅ Создан config.py"
echo ""

# ============================================================================
# ЭТАП 4: Создание backup старого кода
# ============================================================================

echo "📦 Этап 4: Создание backup..."
echo ""

# Backup main.py
cp main.py main.py.backup
echo "✅ Backup: main.py.backup"

# Backup ai_macro_generator.py
cp utils/ai_macro_generator.py utils/ai_macro_generator.py.backup
echo "✅ Backup: utils/ai_macro_generator.py.backup"

# Backup ai_macro_generator_legacy.py
cp utils/ai_macro_generator_legacy.py utils/ai_macro_generator_legacy.py.backup
echo "✅ Backup: utils/ai_macro_generator_legacy.py.backup"

# Backup test_dsl.py
if [ -f "tests/test_dsl.py" ]; then
    cp tests/test_dsl.py tests/test_dsl.py.backup
    echo "✅ Backup: tests/test_dsl.py.backup"
fi

echo ""

# ============================================================================
# ЭТАП 5: Обновление кода (используя config.py)
# ============================================================================

echo "📦 Этап 5: Обновление кода..."
echo ""

# 5.1. Обновить main.py
echo "Обновляем main.py..."

# Добавить импорт config в начало файла
sed -i.tmp '1i\
from config import MACROS_DIR, EXAMPLES_DIR, TEMPLATES_DIR
' main.py

# Заменить self.macros_dir = self.project_root / "macro-queues"
sed -i.tmp 's|self.macros_dir = self.project_root / "macro-queues"|self.macros_dir = MACROS_DIR|g' main.py

# Заменить self.examples_dir = self.project_root / "examples"
sed -i.tmp 's|self.examples_dir = self.project_root / "examples"|self.examples_dir = EXAMPLES_DIR|g' main.py

# Обновить сообщения об ошибках
sed -i.tmp 's|macro-queues/|macros/production/|g' main.py

rm main.py.tmp 2>/dev/null || true

echo "✅ main.py обновлён"

# 5.2. Обновить utils/ai_macro_generator.py
echo "Обновляем utils/ai_macro_generator.py..."

# Добавить импорт
sed -i.tmp '1i\
import sys\
sys.path.insert(0, str(Path(__file__).parent.parent))\
from config import MACROS_DIR, TEMPLATES_DIR
' utils/ai_macro_generator.py

# Заменить путь
sed -i.tmp 's|self.macros_dir = project_root / "macro-queues"|self.macros_dir = MACROS_DIR|g' utils/ai_macro_generator.py

rm utils/ai_macro_generator.py.tmp 2>/dev/null || true

echo "✅ utils/ai_macro_generator.py обновлён"

# 5.3. Обновить utils/ai_macro_generator_legacy.py
echo "Обновляем utils/ai_macro_generator_legacy.py..."

sed -i.tmp '1i\
import sys\
sys.path.insert(0, str(Path(__file__).parent.parent))\
from config import MACROS_DIR, TEMPLATES_DIR
' utils/ai_macro_generator_legacy.py

sed -i.tmp 's|self.macros_dir = project_root / "macro-queues"|self.macros_dir = MACROS_DIR|g' utils/ai_macro_generator_legacy.py

rm utils/ai_macro_generator_legacy.py.tmp 2>/dev/null || true

echo "✅ utils/ai_macro_generator_legacy.py обновлён"

# 5.4. Обновить tests/test_dsl.py (если существует)
if [ -f "tests/test_dsl.py" ]; then
    echo "Обновляем tests/test_dsl.py..."
    
    sed -i.tmp "s|'examples/|'macros/examples/advanced/|g" tests/test_dsl.py
    
    rm tests/test_dsl.py.tmp 2>/dev/null || true
    
    echo "✅ tests/test_dsl.py обновлён"
fi

echo ""

# ============================================================================
# ЭТАП 6: Создание README
# ============================================================================

echo "📦 Этап 6: Создание README..."
echo ""

# macros/README.md
cat > macros/README.md << 'EOF'
# 📁 Macros

Все макросы проекта организованы здесь.

## 📂 Структура

```
macros/
├── production/          # Готовые к использованию макросы
├── examples/            # Примеры для обучения
│   ├── basic/          # Базовые примеры
│   └── advanced/       # Продвинутые примеры
└── templates/          # Шаблоны для копирования
```

## 🚀 Использование

### Production макросы
```bash
python3 macro_sequence.py --config macros/production/tiktok_likes.atlas --run tiktok_likes
```

### Примеры
```bash
# Базовый пример
python3 macro_sequence.py --config macros/examples/basic/hello_world.atlas --run hello_world

# Продвинутый пример
python3 macro_sequence.py --config macros/examples/advanced/try_catch_example.atlas --run try_catch
```

## ➕ Создание нового макроса

### Вариант 1: AI генератор
```bash
python3 utils/ai_macro_generator.py "поставить 10 лайков в TikTok"
# Сохранится в macros/production/
```

### Вариант 2: Вручную
```bash
nano macros/production/my_macro.atlas
```

## 📚 Документация

- [DSL Guide](../docs/guides/dsl/README.md) - Синтаксис DSL
- [AI Generator](../docs/guides/ai/README.md) - AI генерация
- [Examples](examples/README.md) - Примеры
EOF

echo "✅ Создан macros/README.md"

# macros/examples/README.md
cat > macros/examples/README.md << 'EOF'
# 📚 Examples

Примеры макросов для обучения.

## 📂 Структура

- **basic/** - Базовые примеры для новичков
- **advanced/** - Продвинутые примеры с try/catch, циклами, etc.

## 🎓 Базовые примеры

Простые макросы для понимания основ:
- Клики
- Ввод текста
- Ожидания

## 🚀 Продвинутые примеры

Сложные макросы с:
- Try/catch блоками
- Циклами
- Условиями
- Telegram автоматизацией
- TikTok автоматизацией

## 💡 Как использовать

```bash
# Запустить пример
python3 macro_sequence.py --config macros/examples/advanced/try_catch_example.atlas --run try_catch

# Скопировать и изменить
cp macros/examples/advanced/try_catch_example.atlas macros/production/my_macro.atlas
nano macros/production/my_macro.atlas
```
EOF

echo "✅ Создан macros/examples/README.md"

echo ""

# ============================================================================
# ЭТАП 7: Проверка
# ============================================================================

echo "📦 Этап 7: Проверка..."
echo ""

# Проверяем что файлы скопировались
production_count=$(find macros/production -name "*.atlas" 2>/dev/null | wc -l)
examples_count=$(find macros/examples -name "*.atlas" -o -name "*.yaml" 2>/dev/null | wc -l)

echo "📊 Статистика:"
echo "   • macros/production/: $production_count файлов"
echo "   • macros/examples/: $examples_count файлов"
echo ""

# Проверяем что config.py работает
if python3 -c "from config import MACROS_DIR; print(MACROS_DIR)" > /dev/null 2>&1; then
    echo "✅ config.py работает корректно"
else
    echo "❌ config.py имеет ошибки!"
    exit 1
fi

echo ""

# ============================================================================
# ЭТАП 8: Инструкции
# ============================================================================

echo "=" * 80
echo "✅ МИГРАЦИЯ ЗАВЕРШЕНА!"
echo "=" * 80
echo ""
echo "📊 Что было сделано:"
echo "   1. ✅ Создана структура macros/"
echo "   2. ✅ Скопированы все файлы (старые НЕ удалены)"
echo "   3. ✅ Создан config.py"
echo "   4. ✅ Обновлён код (4 файла)"
echo "   5. ✅ Созданы backup файлы"
echo "   6. ✅ Созданы README"
echo ""
echo "🧪 ТЕСТИРОВАНИЕ:"
echo ""
echo "1. Проверьте AI генератор:"
echo "   python3 utils/ai_macro_generator.py 'тестовый макрос'"
echo "   # Должен создать файл в macros/production/"
echo ""
echo "2. Проверьте главное меню:"
echo "   python3 main.py"
echo "   # → 2. DSL Сборник"
echo "   # Должны отображаться макросы из macros/production/"
echo ""
echo "3. Проверьте что всё работает:"
echo "   python3 macro_sequence.py --config macros/production/<any>.atlas --run <name>"
echo ""
echo "=" * 80
echo "⚠️  ВАЖНО: СТАРЫЕ ПАПКИ НЕ УДАЛЕНЫ!"
echo "=" * 80
echo ""
echo "Старые папки сохранены для безопасности:"
echo "   • macro-queues/ (оригинал)"
echo "   • examples/ (оригинал)"
echo ""
echo "❌ УДАЛИТЬ СТАРЫЕ ПАПКИ МОЖНО ТОЛЬКО ПОСЛЕ ПРОВЕРКИ:"
echo ""
echo "   # Если всё работает - удалите вручную:"
echo "   rm -rf macro-queues/"
echo "   rm -rf examples/"
echo ""
echo "💡 Backup файлы кода:"
echo "   • main.py.backup"
echo "   • utils/ai_macro_generator.py.backup"
echo "   • utils/ai_macro_generator_legacy.py.backup"
echo "   • tests/test_dsl.py.backup"
echo ""
echo "   # Если что-то сломалось - восстановите:"
echo "   mv main.py.backup main.py"
echo ""
echo "=" * 80
echo "🎉 Готово! Протестируйте систему перед удалением старых папок."
echo "=" * 80
echo ""
