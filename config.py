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
    print("💡 Запустите: python3 scripts/migrate_macros_python.py")
