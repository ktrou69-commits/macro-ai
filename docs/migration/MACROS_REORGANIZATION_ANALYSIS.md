# 🔍 Анализ: Реорганизация макросов

**Дата:** 10 ноября 2025  
**Цель:** Объединить `macro-queues/`, `macros/`, `examples/` без нарушения кода

---

## 📊 Текущее использование папок

### 1. **macro-queues/** - Используется активно! ⚠️

#### Файлы, которые работают с `macro-queues/`:

**main.py** (6 мест):
```python
# Строка 40
self.macros_dir = self.project_root / "macro-queues"

# Строка 195 - Список макросов
atlas_files = list(self.macros_dir.glob("*.atlas"))
if not atlas_files:
    print("⚠️  .atlas файлы не найдены в папке macro-queues/")

# Строка 648 - AI генератор
macros = sorted(self.macros_dir.glob("*.atlas"))
if not macros:
    print("❌ Нет доступных макросов в macro-queues/")

# Строка 843 - Автоматизация
# Строка 876 - Параллельное выполнение
# Строка 951 - Быстрые поиски
# Строка 1157 - Показ макросов
```

**utils/ai_macro_generator.py** (2 места):
```python
# Строка 20 - Инициализация
self.macros_dir = project_root / "macro-queues"

# Метод generate_and_save() - Сохранение сгенерированных макросов
filepath = self.macros_dir / f"{safe_name}.atlas"
```

**utils/ai_macro_generator_legacy.py** (2 места):
```python
# Строка 22 - Инициализация
self.macros_dir = project_root / "macro-queues"

# Метод generate_and_save() - Сохранение
```

**Итого:** 3 файла активно используют `macro-queues/`

---

### 2. **macros/** - НЕ используется в коде! ✅

```bash
# Поиск показал: 0 результатов
grep -r "macros/" *.py utils/*.py
# Нет упоминаний!
```

**Вывод:** Папка `macros/` создана вручную, но код её не использует.

---

### 3. **examples/** - Используется минимально

#### Файлы, которые работают с `examples/`:

**main.py** (1 место):
```python
# Строка 39 - Инициализация (но не используется!)
self.examples_dir = self.project_root / "examples"
```

**tests/test_dsl.py** (1 место):
```python
# Строка 195 - Проверка примеров
example_files = [
    'examples/tiktok_auto_like.atlas',
    'examples/chrome_quick_search.atlas',
    'examples/tiktok_comment.atlas'
]
```

**Итого:** 2 файла, но `main.py` только инициализирует переменную, не использует.

---

### 4. **templates/** - Используется везде! ⚠️

#### Критически важные файлы:

1. **atlas_dsl_parser.py** - Сканирует `templates/` для резолва имён
2. **utils/smart_capture.py** - Сохраняет шаблоны в `templates/`
3. **utils/prompt_updater.py** - Сканирует `templates/` для AI
4. **utils/dsl_reference_generator.py** - Генерирует справочник из `templates/`
5. **utils/path_watcher.py** - Отслеживает изменения в `templates/`
6. **utils/dom_selector_tool.py** - Сохраняет в `templates/Chrome/{Website}/`
7. **main.py** - Показывает структуру `templates/`

**Вывод:** `templates/` трогать НЕЛЬЗЯ!

---

## 🎯 Безопасный план реорганизации

### Этап 1: Создать новую структуру

```bash
# Создаём новую структуру
mkdir -p macros/production
mkdir -p macros/examples/basic
mkdir -p macros/examples/advanced
mkdir -p macros/templates
```

### Этап 2: Переместить файлы

```bash
# Из macro-queues/ → macros/production/
mv macro-queues/*.atlas macros/production/

# Из macros/ → macros/production/ (если есть готовые)
mv macros/tiktok_automation_hybrid.atlas macros/production/
mv macros/tiktok_like_dom.atlas macros/production/

# Из examples/ → macros/examples/
# Базовые примеры
mv examples/simple_*.atlas macros/examples/basic/ 2>/dev/null || true
mv examples/hello_*.atlas macros/examples/basic/ 2>/dev/null || true

# Продвинутые примеры
mv examples/try_catch_example.atlas macros/examples/advanced/
mv examples/telegram_*.yaml macros/examples/advanced/
mv examples/*.atlas macros/examples/advanced/ 2>/dev/null || true
```

### Этап 3: Обновить код (КРИТИЧНО!)

#### 3.1. Обновить `main.py`:

```python
# БЫЛО:
self.macros_dir = self.project_root / "macro-queues"

# СТАЛО:
self.macros_dir = self.project_root / "macros" / "production"
```

**Места для изменения в main.py:**
- Строка 40: `self.macros_dir`
- Строка 198: Сообщение об ошибке
- Строка 651: Сообщение об ошибке
- Строка 846: Сообщение об ошибке
- Строка 879: Сообщение об ошибке
- Строка 954: Сообщение об ошибке
- Строка 1160: Сообщение об ошибке

#### 3.2. Обновить `utils/ai_macro_generator.py`:

```python
# БЫЛО:
self.macros_dir = project_root / "macro-queues"

# СТАЛО:
self.macros_dir = project_root / "macros" / "production"
```

**Места для изменения:**
- Строка 20: `self.macros_dir`

#### 3.3. Обновить `utils/ai_macro_generator_legacy.py`:

```python
# БЫЛО:
self.macros_dir = project_root / "macro-queues"

# СТАЛО:
self.macros_dir = project_root / "macros" / "production"
```

**Места для изменения:**
- Строка 22: `self.macros_dir`

#### 3.4. Обновить `tests/test_dsl.py`:

```python
# БЫЛО:
example_files = [
    'examples/tiktok_auto_like.atlas',
    'examples/chrome_quick_search.atlas',
    'examples/tiktok_comment.atlas'
]

# СТАЛО:
example_files = [
    'macros/examples/advanced/tiktok_auto_like.atlas',
    'macros/examples/advanced/chrome_quick_search.atlas',
    'macros/examples/advanced/tiktok_comment.atlas'
]
```

### Этап 4: Создать README для macros/

```bash
# Создать macros/README.md
# Создать macros/examples/README.md
# Создать macros/examples/basic/README.md
# Создать macros/examples/advanced/README.md
```

### Этап 5: Удалить старые папки

```bash
# ТОЛЬКО после проверки!
rmdir macro-queues
rmdir examples
rmdir macros  # старая папка
```

---

## ⚠️ КРИТИЧЕСКИЕ МОМЕНТЫ

### 1. **AI генератор сохраняет в macro-queues/**

**Файл:** `utils/ai_macro_generator.py`

```python
def generate_and_save(self, user_input: str) -> Path:
    # ...
    # ВАЖНО: Здесь происходит сохранение!
    filepath = self.macros_dir / f"{safe_name}.atlas"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(dsl_code)
```

**Решение:** Обновить `self.macros_dir` на `macros/production/`

---

### 2. **main.py сканирует macro-queues/**

**Файл:** `main.py`

```python
# Метод: show_macros_list()
atlas_files = list(self.macros_dir.glob("*.atlas"))
```

**Решение:** После изменения `self.macros_dir` всё заработает автоматически.

---

### 3. **examples/ используется в тестах**

**Файл:** `tests/test_dsl.py`

```python
example_files = [
    'examples/tiktok_auto_like.atlas',
    # ...
]
```

**Решение:** Обновить пути на `macros/examples/advanced/`

---

### 4. **templates/ НЕ ТРОГАТЬ!**

**Причина:** Используется в 7+ файлах для:
- Сканирования шаблонов
- Сохранения захваченных кнопок
- Генерации DSL справочника
- AI обновления промптов
- Path Watcher
- DOM селекторов

**Решение:** Оставить `templates/` как есть!

---

## 📋 Чек-лист изменений

### Файлы для обновления:

- [ ] `main.py` (строка 40 + 6 сообщений об ошибках)
- [ ] `utils/ai_macro_generator.py` (строка 20)
- [ ] `utils/ai_macro_generator_legacy.py` (строка 22)
- [ ] `tests/test_dsl.py` (строка 195-197)

### Папки для создания:

- [ ] `macros/production/`
- [ ] `macros/examples/basic/`
- [ ] `macros/examples/advanced/`
- [ ] `macros/templates/`

### Файлы для перемещения:

- [ ] `macro-queues/*.atlas` → `macros/production/`
- [ ] `macros/*.atlas` → `macros/production/`
- [ ] `examples/*.atlas` → `macros/examples/advanced/`
- [ ] `examples/*.yaml` → `macros/examples/advanced/`

### README для создания:

- [ ] `macros/README.md`
- [ ] `macros/examples/README.md`
- [ ] `macros/examples/basic/README.md`
- [ ] `macros/examples/advanced/README.md`

---

## 🧪 План тестирования

### После изменений проверить:

1. **AI генератор:**
   ```bash
   python3 utils/ai_macro_generator.py "поставить лайк в TikTok"
   # Проверить что файл создался в macros/production/
   ```

2. **Главное меню:**
   ```bash
   python3 main.py
   # → 6. Генерация последовательности (AI)
   # Проверить что макросы отображаются
   ```

3. **Список макросов:**
   ```bash
   python3 main.py
   # → 2. DSL Сборник
   # Проверить что макросы из macros/production/ видны
   ```

4. **Тесты:**
   ```bash
   python3 -m pytest tests/test_dsl.py
   # Проверить что примеры находятся
   ```

---

## 💡 Рекомендации

### Вариант 1: Постепенная миграция (БЕЗОПАСНО)

```bash
# Шаг 1: Создать новую структуру
mkdir -p macros/production

# Шаг 2: Скопировать (не перемещать!)
cp macro-queues/*.atlas macros/production/

# Шаг 3: Обновить код
# (изменить main.py, ai_macro_generator.py)

# Шаг 4: Протестировать
python3 main.py

# Шаг 5: Если всё работает - удалить старое
rm -rf macro-queues/
```

### Вариант 2: Симлинк (ВРЕМЕННОЕ РЕШЕНИЕ)

```bash
# Создать симлинк для обратной совместимости
ln -s macros/production macro-queues

# Код продолжит работать!
# Потом можно обновить код постепенно
```

### Вариант 3: Конфигурационный файл (ПРОФЕССИОНАЛЬНО)

```python
# config.py
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
MACROS_DIR = PROJECT_ROOT / "macros" / "production"
EXAMPLES_DIR = PROJECT_ROOT / "macros" / "examples"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# Использование:
from config import MACROS_DIR
self.macros_dir = MACROS_DIR
```

**Преимущества:**
- Одно место для изменения путей
- Легко переключаться между структурами
- Профессиональный подход

---

## ✅ Итоговая рекомендация

### Безопасный план (рекомендую):

1. **Создать скрипт миграции** (автоматизировать)
2. **Использовать конфигурационный файл** (config.py)
3. **Постепенная миграция** (сначала копировать, потом удалять)
4. **Тестирование после каждого шага**

### Файлы, которые точно нужно обновить:

```
main.py                           # 7 мест
utils/ai_macro_generator.py      # 1 место
utils/ai_macro_generator_legacy.py # 1 место
tests/test_dsl.py                 # 1 место
```

### Файлы, которые НЕ трогать:

```
atlas_dsl_parser.py              # Работает с templates/
utils/smart_capture.py           # Сохраняет в templates/
utils/prompt_updater.py          # Сканирует templates/
utils/dsl_reference_generator.py # Читает templates/
utils/path_watcher.py            # Отслеживает templates/
utils/dom_selector_tool.py       # Пишет в templates/
```

---

## 🚀 Следующий шаг

Хочешь чтобы я:
1. **Создал скрипт автоматической миграции?**
2. **Создал config.py для централизованных путей?**
3. **Обновил все 4 файла с новыми путями?**
4. **Создал README для новой структуры macros/?**

**Выбери вариант, и я сделаю это безопасно!** ✨
