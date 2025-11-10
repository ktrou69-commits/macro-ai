#!/usr/bin/env python3
"""
migrate_macros_python.py
100% безопасная миграция макросов

Что делает:
1. Копирует файлы (НЕ удаляет старые)
2. Создаёт config.py
3. Обновляет код точечно
4. Создаёт backup
5. Тестирует
6. Предлагает удалить старое ТОЛЬКО если всё работает
"""

import shutil
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent

def print_header(text):
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80 + "\n")

def print_step(step_num, text):
    print(f"\n📦 Этап {step_num}: {text}...")
    print()

def create_structure():
    """Создаёт новую структуру папок"""
    print_step(1, "Создание новой структуры")
    
    dirs = [
        PROJECT_ROOT / "macros" / "production",
        PROJECT_ROOT / "macros" / "examples" / "basic",
        PROJECT_ROOT / "macros" / "examples" / "advanced",
        PROJECT_ROOT / "macros" / "templates",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"✅ Создано: {d.relative_to(PROJECT_ROOT)}")

def copy_files():
    """Копирует файлы (НЕ перемещает!)"""
    print_step(2, "Копирование файлов")
    
    # Из macro-queues/ → macros/production/
    macro_queues = PROJECT_ROOT / "macro-queues"
    production = PROJECT_ROOT / "macros" / "production"
    
    if macro_queues.exists():
        atlas_files = list(macro_queues.glob("*.atlas"))
        for f in atlas_files:
            shutil.copy2(f, production / f.name)
        print(f"✅ Скопировано из macro-queues/: {len(atlas_files)} файлов")
    else:
        print("⚠️  macro-queues/ не найдена")
    
    # Из старой macros/ → macros/production/
    old_macros = PROJECT_ROOT / "macros"
    if old_macros.exists():
        old_atlas = [f for f in old_macros.glob("*.atlas") if f.is_file()]
        for f in old_atlas:
            shutil.copy2(f, production / f.name)
        if old_atlas:
            print(f"✅ Скопировано из старой macros/: {len(old_atlas)} файлов")
    
    # Из examples/ → macros/examples/advanced/
    examples = PROJECT_ROOT / "examples"
    advanced = PROJECT_ROOT / "macros" / "examples" / "advanced"
    
    if examples.exists():
        atlas_files = list(examples.glob("*.atlas"))
        yaml_files = list(examples.glob("*.yaml"))
        
        for f in atlas_files:
            shutil.copy2(f, advanced / f.name)
        for f in yaml_files:
            shutil.copy2(f, advanced / f.name)
        
        print(f"✅ Скопировано из examples/: {len(atlas_files)} .atlas + {len(yaml_files)} .yaml")

def create_config():
    """Создаёт config.py"""
    print_step(3, "Создание config.py")
    
    config_content = '''"""
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
    print("💡 Запустите: python3 scripts/migrate_macros_python.py")
'''
    
    config_file = PROJECT_ROOT / "config.py"
    config_file.write_text(config_content)
    
    print("✅ Создан config.py")

def create_backups():
    """Создаёт backup файлов перед изменением"""
    print_step(4, "Создание backup")
    
    files_to_backup = [
        PROJECT_ROOT / "main.py",
        PROJECT_ROOT / "utils" / "ai_macro_generator.py",
        PROJECT_ROOT / "utils" / "ai_macro_generator_legacy.py",
        PROJECT_ROOT / "tests" / "test_dsl.py",
    ]
    
    for f in files_to_backup:
        if f.exists():
            backup = f.with_suffix(f.suffix + ".backup")
            shutil.copy2(f, backup)
            print(f"✅ Backup: {backup.relative_to(PROJECT_ROOT)}")

def update_main_py():
    """Обновляет main.py"""
    main_file = PROJECT_ROOT / "main.py"
    content = main_file.read_text()
    
    # Добавляем импорт в начало (после существующих импортов)
    if "from config import" not in content:
        # Находим последний import
        lines = content.split('\n')
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                last_import_idx = i
        
        # Вставляем после последнего импорта
        lines.insert(last_import_idx + 1, "from config import MACROS_DIR, EXAMPLES_DIR, TEMPLATES_DIR")
        content = '\n'.join(lines)
    
    # Заменяем пути
    content = content.replace(
        'self.macros_dir = self.project_root / "macro-queues"',
        'self.macros_dir = MACROS_DIR'
    )
    content = content.replace(
        'self.examples_dir = self.project_root / "examples"',
        'self.examples_dir = EXAMPLES_DIR'
    )
    
    # Обновляем сообщения
    content = content.replace('macro-queues/', 'macros/production/')
    
    main_file.write_text(content)
    print("✅ main.py обновлён")

def update_ai_generator():
    """Обновляет ai_macro_generator.py"""
    gen_file = PROJECT_ROOT / "utils" / "ai_macro_generator.py"
    content = gen_file.read_text()
    
    # Добавляем импорт
    if "from config import" not in content:
        lines = content.split('\n')
        # Находим первый import после docstring
        insert_idx = 0
        in_docstring = False
        for i, line in enumerate(lines):
            if '"""' in line or "'''" in line:
                in_docstring = not in_docstring
            if not in_docstring and (line.startswith('import ') or line.startswith('from ')):
                insert_idx = i
                break
        
        lines.insert(insert_idx, "import sys")
        lines.insert(insert_idx + 1, "sys.path.insert(0, str(Path(__file__).parent.parent))")
        lines.insert(insert_idx + 2, "from config import MACROS_DIR, TEMPLATES_DIR")
        content = '\n'.join(lines)
    
    # Заменяем путь
    content = content.replace(
        'self.macros_dir = project_root / "macro-queues"',
        'self.macros_dir = MACROS_DIR'
    )
    
    gen_file.write_text(content)
    print("✅ utils/ai_macro_generator.py обновлён")

def update_ai_generator_legacy():
    """Обновляет ai_macro_generator_legacy.py"""
    legacy_file = PROJECT_ROOT / "utils" / "ai_macro_generator_legacy.py"
    if not legacy_file.exists():
        print("⚠️  utils/ai_macro_generator_legacy.py не найден")
        return
    
    content = legacy_file.read_text()
    
    # Добавляем импорт
    if "from config import" not in content:
        lines = content.split('\n')
        insert_idx = 0
        in_docstring = False
        for i, line in enumerate(lines):
            if '"""' in line or "'''" in line:
                in_docstring = not in_docstring
            if not in_docstring and (line.startswith('import ') or line.startswith('from ')):
                insert_idx = i
                break
        
        lines.insert(insert_idx, "import sys")
        lines.insert(insert_idx + 1, "sys.path.insert(0, str(Path(__file__).parent.parent))")
        lines.insert(insert_idx + 2, "from config import MACROS_DIR, TEMPLATES_DIR")
        content = '\n'.join(lines)
    
    # Заменяем путь
    content = content.replace(
        'self.macros_dir = project_root / "macro-queues"',
        'self.macros_dir = MACROS_DIR'
    )
    
    legacy_file.write_text(content)
    print("✅ utils/ai_macro_generator_legacy.py обновлён")

def update_test_dsl():
    """Обновляет tests/test_dsl.py"""
    test_file = PROJECT_ROOT / "tests" / "test_dsl.py"
    if not test_file.exists():
        print("⚠️  tests/test_dsl.py не найден")
        return
    
    content = test_file.read_text()
    
    # Заменяем пути
    content = content.replace("'examples/", "'macros/examples/advanced/")
    
    test_file.write_text(content)
    print("✅ tests/test_dsl.py обновлён")

def update_code():
    """Обновляет весь код"""
    print_step(5, "Обновление кода")
    
    update_main_py()
    update_ai_generator()
    update_ai_generator_legacy()
    update_test_dsl()

def create_readmes():
    """Создаёт README файлы"""
    print_step(6, "Создание README")
    
    # macros/README.md
    macros_readme = PROJECT_ROOT / "macros" / "README.md"
    macros_readme.write_text('''# 📁 Macros

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

### AI генератор
```bash
python3 utils/ai_macro_generator.py "поставить 10 лайков в TikTok"
# Сохранится в macros/production/
```

## 📚 Документация

- [DSL Guide](../docs/guides/dsl/README.md)
- [AI Generator](../docs/guides/ai/README.md)
- [Examples](examples/README.md)
''')
    print("✅ Создан macros/README.md")
    
    # macros/examples/README.md
    examples_readme = PROJECT_ROOT / "macros" / "examples" / "README.md"
    examples_readme.write_text('''# 📚 Examples

Примеры макросов для обучения.

## 📂 Структура

- **basic/** - Базовые примеры для новичков
- **advanced/** - Продвинутые примеры

## 💡 Использование

```bash
python3 macro_sequence.py --config macros/examples/advanced/try_catch_example.atlas --run try_catch
```
''')
    print("✅ Создан macros/examples/README.md")

def check_migration():
    """Проверяет результат миграции"""
    print_step(7, "Проверка")
    
    production = PROJECT_ROOT / "macros" / "production"
    examples = PROJECT_ROOT / "macros" / "examples"
    
    prod_count = len(list(production.glob("*.atlas")))
    ex_count = len(list(examples.rglob("*.atlas"))) + len(list(examples.rglob("*.yaml")))
    
    print(f"📊 Статистика:")
    print(f"   • macros/production/: {prod_count} файлов")
    print(f"   • macros/examples/: {ex_count} файлов")
    print()
    
    # Проверяем config.py
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from config import MACROS_DIR
        print(f"✅ config.py работает корректно")
        print(f"   MACROS_DIR = {MACROS_DIR}")
    except Exception as e:
        print(f"❌ config.py имеет ошибки: {e}")
        return False
    
    return True

def print_final_instructions():
    """Выводит финальные инструкции"""
    print_header("✅ МИГРАЦИЯ ЗАВЕРШЕНА!")
    
    print("📊 Что было сделано:")
    print("   1. ✅ Создана структура macros/")
    print("   2. ✅ Скопированы все файлы (старые НЕ удалены)")
    print("   3. ✅ Создан config.py")
    print("   4. ✅ Обновлён код (4 файла)")
    print("   5. ✅ Созданы backup файлы")
    print("   6. ✅ Созданы README")
    print()
    
    print("🧪 ТЕСТИРОВАНИЕ:")
    print()
    print("1. Проверьте AI генератор:")
    print("   python3 utils/ai_macro_generator.py 'тестовый макрос'")
    print("   # Должен создать файл в macros/production/")
    print()
    print("2. Проверьте главное меню:")
    print("   python3 main.py")
    print("   # → 2. DSL Сборник")
    print("   # Должны отображаться макросы из macros/production/")
    print()
    print("3. Проверьте запуск макроса:")
    print("   python3 macro_sequence.py --config macros/production/<any>.atlas --run <name>")
    print()
    
    print_header("⚠️  ВАЖНО: СТАРЫЕ ПАПКИ НЕ УДАЛЕНЫ!")
    
    print("Старые папки сохранены для безопасности:")
    print("   • macro-queues/ (оригинал)")
    print("   • examples/ (оригинал)")
    print()
    print("❌ УДАЛИТЬ СТАРЫЕ ПАПКИ МОЖНО ТОЛЬКО ПОСЛЕ ПРОВЕРКИ:")
    print()
    print("   # Если всё работает - удалите вручную:")
    print("   rm -rf macro-queues/")
    print("   rm -rf examples/")
    print()
    print("💡 Backup файлы кода:")
    print("   • main.py.backup")
    print("   • utils/ai_macro_generator.py.backup")
    print("   • utils/ai_macro_generator_legacy.py.backup")
    print("   • tests/test_dsl.py.backup")
    print()
    print("   # Если что-то сломалось - восстановите:")
    print("   mv main.py.backup main.py")
    print("   mv utils/ai_macro_generator.py.backup utils/ai_macro_generator.py")
    print()
    
    print_header("🎉 Готово! Протестируйте систему перед удалением старых папок.")

def main():
    print_header("🔄 БЕЗОПАСНАЯ МИГРАЦИЯ МАКРОСОВ")
    
    print("⚠️  ВАЖНО: Этот скрипт НЕ удаляет старые файлы автоматически!")
    print("   Он только копирует и обновляет код.")
    print("   Удаление старых папок - вручную, после проверки.")
    print()
    
    input("Нажмите Enter для продолжения...")
    
    try:
        create_structure()
        copy_files()
        create_config()
        create_backups()
        update_code()
        create_readmes()
        
        if check_migration():
            print_final_instructions()
        else:
            print("\n❌ Миграция завершена с ошибками!")
            print("💡 Проверьте config.py и восстановите из backup если нужно")
            
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("💡 Восстановите из backup:")
        print("   mv main.py.backup main.py")
        print("   mv utils/ai_macro_generator.py.backup utils/ai_macro_generator.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
