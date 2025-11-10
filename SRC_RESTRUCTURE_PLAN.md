# 📋 План реструктуризации: Создание src/

**Дата:** 10 ноября 2025  
**Цель:** Переместить весь основной код в `src/` без поломки зависимостей

---

## ✅ Подготовка (ВЫПОЛНЕНО)

- ✅ Создан Git коммит: `f37650b`
- ✅ Размер репозитория: 10 MB (без venv)
- ✅ Все изменения сохранены

**Откат в случае проблем:**
```bash
git reset --hard f37650b
```

---

## 🎯 Целевая структура

### До:
```
local-macros/
├── main.py                         # ❌ В корне
├── macro_sequence.py               # ❌ В корне
├── atlas_dsl_parser.py             # ❌ В корне
├── sequence_builder.py             # ❌ В корне
├── parallel_runner.py              # ❌ В корне
├── selenium_helper.py              # ❌ В корне
├── utils/                          # ❌ Смешано с кодом
├── tests/                          # ✅ OK
├── templates/                      # ✅ OK
├── macros/                         # ✅ OK
├── requirements.txt                # ✅ OK
└── .env                            # ✅ OK
```

### После:
```
local-macros/
├── src/                            # ✅ Весь основной код
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── macro_sequence.py
│   │   ├── atlas_dsl_parser.py
│   │   └── sequence_builder.py
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── parallel_runner.py
│   │   └── selenium_helper.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── macro_generator.py
│   │   ├── macro_generator_legacy.py
│   │   ├── prompt_updater.py
│   │   └── dom_analyzer.py
│   └── utils/
│       ├── __init__.py
│       ├── api_config.py
│       ├── smart_capture.py
│       ├── coordinate_finder.py
│       └── ... (все утилиты)
│
├── tests/                          # ✅ Тесты (не трогаем)
├── templates/                      # ✅ Шаблоны (не трогаем)
├── macros/                         # ✅ Макросы (не трогаем)
├── config.py                       # ✅ Конфиг (в корне)
├── requirements.txt                # ✅ Зависимости (в корне)
├── setup.py                        # ✅ Новый файл
├── .env                            # ✅ Env (в корне)
└── README.md                       # ✅ Документация (в корне)
```

---

## 📦 Этапы миграции

### Этап 1: Анализ зависимостей (КРИТИЧНО!)

**Нужно найти все импорты:**

1. **Импорты из корня:**
   ```python
   import main
   import macro_sequence
   import atlas_dsl_parser
   import sequence_builder
   import parallel_runner
   import selenium_helper
   ```

2. **Импорты из utils:**
   ```python
   from utils.api_config import api_config
   from utils.smart_capture import SmartCapture
   from utils.ai_macro_generator import AIMacroGenerator
   ```

3. **Относительные импорты:**
   ```python
   from . import something
   from .. import something
   ```

**Команды для поиска:**
```bash
# Найти все импорты из корня
grep -r "^import main" . --include="*.py"
grep -r "^import macro_sequence" . --include="*.py"
grep -r "^import atlas_dsl_parser" . --include="*.py"
grep -r "^import sequence_builder" . --include="*.py"
grep -r "^import parallel_runner" . --include="*.py"
grep -r "^import selenium_helper" . --include="*.py"

# Найти все from импорты
grep -r "^from main import" . --include="*.py"
grep -r "^from macro_sequence import" . --include="*.py"
grep -r "^from atlas_dsl_parser import" . --include="*.py"

# Найти все импорты utils
grep -r "from utils" . --include="*.py"
grep -r "import utils" . --include="*.py"
```

---

### Этап 2: Создание структуры src/

**Шаг 1: Создать папки**
```bash
mkdir -p src/core
mkdir -p src/engines
mkdir -p src/ai
mkdir -p src/utils
```

**Шаг 2: Создать __init__.py**
```bash
touch src/__init__.py
touch src/core/__init__.py
touch src/engines/__init__.py
touch src/ai/__init__.py
touch src/utils/__init__.py
```

---

### Этап 3: Перемещение файлов

**Основные модули → src/core/**
```bash
git mv macro_sequence.py src/core/
git mv atlas_dsl_parser.py src/core/
git mv sequence_builder.py src/core/
```

**Движки → src/engines/**
```bash
git mv parallel_runner.py src/engines/
git mv selenium_helper.py src/engines/
```

**AI модули → src/ai/**
```bash
git mv utils/ai_macro_generator.py src/ai/macro_generator.py
git mv utils/ai_macro_generator_legacy.py src/ai/macro_generator_legacy.py
git mv utils/prompt_updater.py src/ai/prompt_updater.py
git mv utils/ai_dom_analyzer.py src/ai/dom_analyzer.py
```

**Утилиты → src/utils/**
```bash
git mv utils/api_config.py src/utils/
git mv utils/smart_capture.py src/utils/
git mv utils/coordinate_finder.py src/utils/
git mv utils/advanced_coordinate_finder.py src/utils/
git mv utils/find_comment_region.py src/utils/
git mv utils/simple_coordinate_finder.py src/utils/
git mv utils/check_api_quota.py src/utils/
git mv utils/dom_selector_tool.py src/utils/
```

**main.py → src/**
```bash
git mv main.py src/
```

---

### Этап 4: Обновление импортов

**Все файлы в src/ должны использовать:**

```python
# Было:
import macro_sequence
from utils.api_config import api_config

# Стало:
from src.core import macro_sequence
from src.utils.api_config import api_config
```

**Файлы для обновления:**
1. `src/main.py`
2. `src/core/macro_sequence.py`
3. `src/core/atlas_dsl_parser.py`
4. `src/core/sequence_builder.py`
5. `src/engines/parallel_runner.py`
6. `src/engines/selenium_helper.py`
7. `src/ai/macro_generator.py`
8. `src/ai/macro_generator_legacy.py`
9. `src/ai/prompt_updater.py`
10. `src/ai/dom_analyzer.py`
11. Все файлы в `src/utils/`
12. Все файлы в `tests/`

---

### Этап 5: Создание setup.py

```python
from setuptools import setup, find_packages

setup(
    name="macro-ai",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # Из requirements.txt
    ],
    entry_points={
        'console_scripts': [
            'macro-ai=src.main:main',
        ],
    },
)
```

---

### Этап 6: Обновление путей к файлам

**Файлы которые используют абсолютные пути:**

1. **config.py** - пути к macros/
2. **templates/** - пути к шаблонам
3. **tests/** - пути к тестовым данным

**Нужно обновить:**
```python
# Было:
Path(__file__).parent / "templates"

# Стало:
Path(__file__).parent.parent / "templates"
```

---

### Этап 7: Тестирование

**После каждого этапа:**

1. **Проверить импорты:**
   ```bash
   python3 -c "from src.core import macro_sequence"
   python3 -c "from src.utils.api_config import api_config"
   ```

2. **Запустить main.py:**
   ```bash
   python3 src/main.py
   ```

3. **Запустить тесты:**
   ```bash
   python3 tests/test_dsl.py
   python3 tests/test_gemini.py
   ```

4. **Проверить AI генератор:**
   ```bash
   python3 -m src.ai.macro_generator "тест"
   ```

---

## ⚠️ Критичные моменты

### 1. **Path(__file__) зависимости**

Файлы которые используют `Path(__file__)`:
- `config.py` → пути к macros/
- `src/utils/api_config.py` → путь к .env
- `src/ai/macro_generator.py` → пути к templates/
- `src/ai/prompt_updater.py` → пути к templates/

**Решение:** Использовать `Path(__file__).parent.parent` для выхода из src/

### 2. **sys.path.insert(0, ...)**

Файлы которые добавляют корень в sys.path:
- `src/utils/api_config.py`
- `src/ai/macro_generator.py`
- `src/ai/prompt_updater.py`

**Решение:** Обновить на `Path(__file__).parent.parent.parent`

### 3. **Импорты в tests/**

Тесты импортируют модули из корня:
```python
from macro_sequence import MacroSequence
from atlas_dsl_parser import AtlasDSLParser
```

**Решение:** Обновить на:
```python
from src.core.macro_sequence import MacroSequence
from src.core.atlas_dsl_parser import AtlasDSLParser
```

### 4. **config.py остаётся в корне**

`config.py` должен остаться в корне, так как он используется везде:
```python
from config import MACROS_DIR, TEMPLATES_DIR
```

---

## 🔄 План отката

### Если что-то пошло не так:

**Вариант 1: Откат через Git**
```bash
git reset --hard f37650b
git clean -fd
```

**Вариант 2: Откат конкретных файлов**
```bash
git checkout f37650b -- <file>
```

**Вариант 3: Создать ветку для эксперимента**
```bash
git checkout -b restructure-experiment
# Делаем изменения
# Если не получилось:
git checkout main
git branch -D restructure-experiment
```

---

## 📊 Чеклист выполнения

### Подготовка:
- [x] Создан Git коммит
- [x] Проверен размер репозитория
- [ ] Найдены все импорты
- [ ] Создан список файлов для обновления

### Миграция:
- [ ] Создана структура src/
- [ ] Перемещены файлы в src/core/
- [ ] Перемещены файлы в src/engines/
- [ ] Перемещены файлы в src/ai/
- [ ] Перемещены файлы в src/utils/
- [ ] Перемещён main.py в src/

### Обновление:
- [ ] Обновлены импорты в src/main.py
- [ ] Обновлены импорты в src/core/
- [ ] Обновлены импорты в src/engines/
- [ ] Обновлены импорты в src/ai/
- [ ] Обновлены импорты в src/utils/
- [ ] Обновлены импорты в tests/
- [ ] Обновлены пути Path(__file__)
- [ ] Обновлены sys.path.insert()

### Тестирование:
- [ ] Импорты работают
- [ ] main.py запускается
- [ ] Тесты проходят
- [ ] AI генератор работает
- [ ] Макросы выполняются

### Финализация:
- [ ] Создан setup.py
- [ ] Обновлён README.md
- [ ] Создан Git коммит
- [ ] Проверено всё работает

---

## 🎯 Следующий шаг

**Запустить анализ зависимостей:**
```bash
python3 scripts/analyze_imports.py
```

Это создаст полный список всех импортов и файлов которые нужно обновить.

---

**Готов начать? Сначала нужно проанализировать все импорты!**
